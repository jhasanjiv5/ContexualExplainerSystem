from DiscoverEnvironment import collectLogs, discover
from TimeSyncAndCorrelation import correlate
from SurrogateModels import classifier as cl
from sklearn import model_selection
from Explainers import explainer as ex
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
# import streamlit as st
from PIL import Image
from tabulate import tabulate
from keywordExtraction import keywordExtract as ky
from datetime import *
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn import utils


def find_keywords(query):
    message_keywords = ky.keyword_extract(query)
    message_keywords_lower = [x.lower() for x in message_keywords]
    return message_keywords_lower


def explain_graph(option):
    print(option)


def visualize_explanation(clf, cf, query_instance, feature_names, ontology_prefix, ontology_uri, subject=None):
    """
    :param clf:
    :param cf:
    :param query_instance:
    """
    predicate = None
    object = None

    print('Counterfactual predicted class from using base model:')
    print(clf.predict(cf))

    print('Counterfactuals:')
    print(tabulate(cf, headers=feature_names, tablefmt='pretty', missingval='N/A'))
    print('List of causally relevant features:')
    related_features = []
    diff = np.where(cf != query_instance)[1]
    low_diff = np.where(cf < query_instance)[1]
    high_diff = np.where(cf > query_instance)[1]

    for i in diff:
        related_features.append(feature_names[i])

    explain_graph(related_features)

    for i in diff:
        if i in low_diff:
            predicate = 'negativeEffect'
            object = feature_names[i]
        if i in high_diff:
            predicate = 'positiveEffect'
            object = feature_names[i]
        print(object + ' has ' + predicate + ' on ' + subject)
        print('''Following are the existing Relationships between {} and {}'''.format(subject, object))
        rel_exist = discover.select_relationships(ontology_prefix, ontology_uri, subject, object)
        unique, counts = np.unique(rel_exist, return_counts=True)
        print(np.column_stack((unique, counts)))

        feedback = input('Add your feedback')
        answer_given = input('Do you agree with found relationship? yes/no')
        rating = False
        if answer_given.lower() == 'yes':
            rating = True

        if len(rel_exist) > 0:
            discover.insert_relationship(ontology_prefix, ontology_uri, subject, predicate, object,
                                         len(rel_exist),
                                         feedback, rating)
        else:
            discover.insert_relationship(ontology_prefix, ontology_uri, subject, predicate, object, 1,
                                         feedback, rating)

    # show explanation for top related feature instead of selection box for simplicity

    print('''Existing Relationships for {}'''.format(subject))
    effects_data = discover.show_effects(ontology_prefix, ontology_uri, subject)
    df = pd.DataFrame(effects_data).T
    df.fillna(0, inplace=True)
    print(df)
    plt.figure(figsize=(16, 8), dpi=150)

    return related_features


def run_explanation_system():
    '''Thing Description found for CPS:'''

    print(
        '''
        Contextual Explanation System
        '''
    )
    print("---------Query-------------")
    query = input("Enter name of the entity: ")
    class_name_input = input("Enter feature name for finding influence:")
    print("---------Context Discovery-")
    ontology_prefix = input("Enter the ontology prefix used: ")
    ontology_uri = input("Enter the ontology uri: ")
    seed = input("Enter the relationship name to discover the Thing Descriprions: ")
    # start gathering thing descriptions 
    cps_td, contextual_variables = discover.discover_context(ontology_prefix, ontology_uri, seed, [query])
    print("Thing Description found for CPS:")
    print(cps_td)

    print("Found observable context features:")
    print(contextual_variables)
    
    # start collecting data
    links = collectLogs.get_links(cps_td, contextual_variables)
    dfs = collectLogs.get_logs(links)
    dfs.fillna(0)
    
    ## check if the colims have numeric values for correlation
    is_numeric_ds = dfs.apply(lambda s: pd.to_numeric(s, errors='coerce').notnull().all())
    corr = []
    for k, v in is_numeric_ds.items():
        if v:
            corr.append(k)
    corr_ds = dfs[corr]
    print(corr_ds)
    corr_dict = {}
    
    # NOTE: correlation is found in the demo because the pawerstatus is not binary but vriable as per the brightness of the light perhaps
    for i in range(corr_ds.shape[1]):
        variable_name = corr_ds.columns[i]
        variable_value = corr_ds.iloc[:,i]
        # TODO: only integer and float are supported for correlation, check for other datatypes
        if isinstance(variable_value[1], (int, float)):
            corr_dict[variable_name] = correlate.check_for_correlation(corr_ds[class_name_input], variable_value)
    for feature in corr_dict:
        print("Selected feature {} has CorrCoef {}.".format(feature, corr_dict[feature]))
    
    sensors = corr_ds[corr_dict.keys()]
    ##### for demo data only
    sensors.loc[sensors.lightPowerStatus > 0, 'lightPowerStatus'] = 1
    selected_datetime = input("Enter datetime of query instance: ")
    # correlate.check_for_correlation(sensors)  # select features based of the correlation values
    X = sensors.loc[:, sensors.columns != class_name_input]
    y = sensors.loc[:, class_name_input]
    feature_names = list(X.columns)
    X_values = X.values  # only supports arrays atm
    y_values = y.values
    print(np.unique(y_values))
    class_names = class_name_input #y.name
    cat_feat = []
    lab = preprocessing.LabelEncoder()
    y_transformed = lab.fit_transform(y_values)
    num_feat = list(np.arange(len(feature_names)))
    X_train, X_test, y_train, y_test = train_test_split(X_values, y_transformed, test_size=0.2, random_state=20)
    #TODO: ask users to select continuous data columns for training purpose
    clf = cl.predict_ir(X_train, X_test, y_train, y_test, num_feat, cat_feat)
    # query_instance = X_test[0:1]
    timestamp = corr_ds.columns[corr_ds.columns.isin(['time','timestamp'])][0]
    query_instance = sensors.loc[corr_ds[timestamp] == selected_datetime, feature_names].values
    
    print('Model Decision:')
    print(clf.predict(query_instance))

    print('Query Instance:')
    print(tabulate(query_instance, headers=feature_names, tablefmt='pretty', missingval='N/A'))

    # cf = ex.nice_explain(lambda x: clf.predict_proba(x), X_train, cat_feat, num_feat, y_train,
    #                     query_instance)
    
    #dice explainer
    cf = ex.dice_explain(clf, sensors, pd.DataFrame(query_instance, columns=feature_names), feature_names, class_names)
    
    #ask users to choose the countefactual
    if cf is not None:
        cf_select = input('Select an index from the presented counterfactual based on feasibility and actionability of it:')
        visualize_explanation(clf, cf[cf_select], query_instance, feature_names, ontology_prefix, ontology_uri, subject=query)


if __name__ == '__main__':
    # cps_td, contextual_variables = discover.discover_context('hsg:RB30_OG4_61-400_standing_light_1')
    run_explanation_system()
