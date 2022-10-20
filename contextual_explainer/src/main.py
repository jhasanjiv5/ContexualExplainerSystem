from cmath import nan
from operator import countOf
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
import math


def find_keywords(query):
    message_keywords = ky.keyword_extract(query)
    message_keywords_lower = [x.lower() for x in message_keywords]
    return message_keywords_lower


def explain_graph(option):
    print(option)


def visualize_explanation(clf, cf, query_instance, feature_names, ontology_prefix, ontology_uri, subject=None, feature =None):
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
    diff = np.where(np.array(cf) != np.array(query_instance))[1]
    low_diff = np.where(np.array(cf) < np.array(query_instance))[1]
    high_diff = np.where(np.array(cf) > np.array(query_instance))[1]

    for i in diff:
        related_features.append(feature_names[i])

    explain_graph(related_features)

    for i in diff:
        if i in low_diff:
            predicate = 'negativeInfluence'
            object = feature_names[i]
        if i in high_diff:
            predicate = 'positiveInfluence'
            object = feature_names[i]
        print(object + ' has ' + predicate + ' on ' + feature + ' of '+ subject)
        
        rel_exist = discover.select_relationships(ontology_prefix, ontology_uri, subject, object)
        if len(rel_exist)>0:
            print('''Following are the preserved influences between {} and {}'''.format(subject, object))
            influence_type_array =[]
            for rel in rel_exist:
                influence_type_array.append(rel_exist[rel]['influence_type'])
                
                
            unique, counts = np.unique(influence_type_array, return_counts=True)
            print(np.column_stack((unique, counts)))
            
            
            rating_dict ={}
            for b in ['positiveInfluence', 'negativeInfluence']:
                sum = 0
                for a in rel_exist:

                    if rel_exist[a]['influence_type'] == b:
                        sum += int(rel_exist[a]['rating'])
                rating_dict.update({b:sum/len(rel_exist)})        
            print('Average ratings:{}'.format(rating_dict))

            feedback = input('Add your feedback: ')
            answer_given = input('Do you agree with found relationship? yes/no: ')
            rating = 0
            if answer_given.lower() == 'yes':
                rating = 1
            
            discover.insert_relationship(ontology_prefix, ontology_uri, subject, predicate, object,
                                                len(rel_exist),
                                                feedback, rating, feature)
        else:
            feedback = input('Add your feedback: ')
            answer_given = input('Do you agree with found relationship? yes/no: ')
            rating = 0
            if answer_given.lower() == 'yes':
                rating = 1
            discover.insert_relationship(ontology_prefix, ontology_uri, subject, predicate, object, 1,
                                            feedback, rating, feature)

    return related_features


def run_explanation_system():
    '''Thing Description found for CPS:'''

    print(
        '''
        Contextual Explanation System
        '''
    )
    print("---------Query-------------")
    query = input("Enter name of the entity: ") or "RB30_OG4_61-400_standing_lamp_1"
    class_name_input = input("Enter feature name for finding influence:")  or "lightPowerStatus"
    selected_datetime = input("Enter datetime of query instance: ") or "2022-01-01T00:00:00Z" 
    print("---------Context Discovery-")
    ontology_prefix = input("Enter the ontology prefix used: ") or "hsg"
    ontology_uri = input("Enter the ontology uri: ") or "<http://semantics.interactions.ics.unisg.ch/livingcampus#>"
    seed = input("Enter the relationship name to discover the Thing Descriprions: ") or "hasTD"
    #show existing relationships
    
    print('''Existing Contextual Influences for {}'''.format(query))
    effects_data = discover.show_effects(ontology_prefix, ontology_uri, query)
    df = pd.DataFrame(effects_data).T
    df.fillna(0, inplace=True)
    print(df)
    
    
    # start gathering thing descriptions 
    cps_td, contextual_variables = discover.discover_context(ontology_prefix, ontology_uri, seed, [query])
    print("Thing Description found for CPS:")
    print(cps_td)

    print("Found observable context features:")
    print(contextual_variables)
    
    # start collecting data
    links = collectLogs.get_links(cps_td, contextual_variables)
    dfs = collectLogs.get_logs(links)
    print(dfs.head())
    ## check if the colims have numeric values for correlation
    is_numeric_ds = dfs.apply(lambda s: pd.to_numeric(s, errors='coerce').notnull().all())
    corr = []
    for k, v in is_numeric_ds.items():
        if v:
            corr.append(k)
    corr_ds = dfs[corr]
    corr_dict = {}
    
    # NOTE: correlation is found in the demo because the pawerstatus is not binary but vriable as per the brightness of the light perhaps
    for i in range(corr_ds.shape[1]):
        variable_name = corr_ds.columns[i]
        variable_value = corr_ds.iloc[:,i]
        # TODO: only integer and float are supported for correlation, check for other datatypes
        if isinstance(variable_value[1], (int, float)):
            correlation_value =correlate.check_for_correlation(corr_ds[class_name_input], variable_value)
            if not math.isnan(correlation_value): #correlation value can be nan if there is not change in the variables subjected for correlation
                corr_dict[variable_name] = correlation_value
    for feature in corr_dict:
        print("Selected feature {} has CorrCoef {}.".format(feature, corr_dict[feature]))
    columns = [a for a in corr_dict.keys()]
    sensors = corr_ds[columns]
    print(sensors.head())
    class_names = class_name_input+'Class'
    sensors[class_names] = np.where(sensors[class_name_input]> 0, 'On', 'Off')
    # correlate.check_for_correlation(sensors)  # select features based of the correlation values
    X = sensors.loc[:, sensors.columns != class_names]
    y = sensors.loc[:, class_names]
    feature_names = list(X.columns)
    X_values = X.values  # only supports arrays atm
    y_values = y.values
    #y.name
    cat_feat = []
    lab = preprocessing.LabelEncoder()
    y_transformed = lab.fit_transform(y_values)
    
    num_feat = list(np.arange(len(feature_names)))
    X_train, X_test, y_train, y_test = train_test_split(X_values, y_transformed, test_size=0.2, random_state=20)
    #TODO: ask users to select continuous data columns for training purpose
    clf = cl.predict_ir(X_train, X_test, y_train, y_test, num_feat, cat_feat)
    # query_instance = X_test[0:1]
    timestamp = corr_ds.columns[corr_ds.columns.isin(['time','timestamp'])][0]

    query_instance = sensors.loc[corr_ds[timestamp] == selected_datetime, feature_names]
    query_instance = query_instance.iloc[:,:]
    print(query_instance)
    print('Model Prediction:')
    print(clf.predict(query_instance))

    print('Query Instance:')
    print(tabulate(query_instance, headers=feature_names, tablefmt='pretty', missingval='N/A'))

    
    #shap explainer
    
    #ex.shap_explain(sensors, clf.predict, X_test[0:1000, :], class_names, X_train, feature_names)
    
    #dice explainer
    cf = ex.dice_explain(clf, sensors.iloc[:,:], query_instance, feature_names, class_names)
    print(cf)
    
    #ask users to choose the countefactual
    if cf is not None:
        cf_select = int(input('Select an index from the presented counterfactual based on feasibility and actionability of it:'))
        visualize_explanation(clf, cf.loc[[cf_select], feature_names], query_instance, feature_names, ontology_prefix, ontology_uri, subject=query, feature = class_name_input)


if __name__ == '__main__':
    # cps_td, contextual_variables = discover.discover_context('hsg:RB30_OG4_61-400_standing_light_1')
    run_explanation_system()