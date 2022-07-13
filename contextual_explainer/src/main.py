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
from TimeSyncAndCorrelation import eventCorrelation

'''
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

'''


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

    print('Counterfactual tagret class:')
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
        answer_given = input('Do you agree with found relationship?')
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


'''@app.route('/run/')'''


def run_explanation_system():
    '''Thing Description found for CPS:'''

    print(
        '''
        Contextual Explanation System
        '''
    )
    # im2 = Image.open("contextual_explainer/src/Figures/banner.jpeg")
    # st.sidebar.image([im2])
    query = input("Enter name of the entity: ")
    ontology_prefix = input("Enter the ontology prefix used: ")
    ontology_uri = input("Enter the ontology uri: ")
    # date = st.sidebar.date_input('date')
    # st.sidebar.text(date)
    # time = st.sidebar.time_input('time')
    # selected_datetime = datetime.combine(date, time).isoformat() + "Z"
    # st.sidebar.text(selected_datetime)
    # st.sidebar.text('Found Keywords:')
    # words = find_keywords(query)
    # st.sidebar.text(words)
    cps_td, contextual_variables = discover.discover_context(ontology_prefix, ontology_uri, [query])
    '''Thing Description found for CPS:'''
    print(cps_td)

    '''Found observable context features:'''
    print(contextual_variables)
    links = collectLogs.get_links(cps_td, contextual_variables)
    dfs = collectLogs.get_logs(links)
    sensors = dfs
    sensors = sensors.fillna(0)
    # sensors['time'] = pd.to_datetime(sensors['time'])
    # selected_datetime = st.sidebar.selectbox(label="Select time...", options=sensors)
    selected_datetime = input("Enter datetime of query instance: ")
    # correlate.check_for_correlation(sensors)  # select features based of the correlation values
    X = sensors.drop(columns=['time', 'r400', 'r410', 'r402'])
    y = sensors.loc[:, 'r400']
    feature_names = list(X.columns)
    class_names = y.name
    X = X.values  # only supports arrays atm
    y = y.values
    cat_feat = []
    num_feat = list(np.arange(len(feature_names)))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=20)
    clf = cl.predict_ir(X_train, X_test, y_train, y_test, num_feat, cat_feat)
    # query_instance = X_test[0:1]
    query_select = sensors.loc[sensors['time'] == selected_datetime].values
    query_instance = query_select[:, 4:11]
    print('Model Decision:')
    print(clf.predict(query_instance))

    print('Query Instance:')
    print(tabulate(query_instance, headers=feature_names, tablefmt='pretty', missingval='N/A'))

    # cf = ex.nice_explain(lambda x: clf.predict_proba(x), X_train, cat_feat, num_feat, y_train,
    #                     query_instance)
    cf = ex.dice_explain(clf, sensors.drop(columns=['time', 'r410', 'r402']),
                         pd.DataFrame(query_instance, columns=feature_names))
    related_features = visualize_explanation(clf, cf, query_instance, feature_names, ontology_prefix, ontology_uri,
                                             subject=query)

    # using plot method to plot open prices.
    # in plot method we set the label and color of the curve.
    df[related_features].plot(label=related_features)
    df[class_names].plot(label=query, color='orange')

    # adding title to the plot
    plt.title('Open Price Plot')

    # adding Label to the x-axis
    plt.xlabel('Years')

    # adding legend to the curve
    plt.legend()
    # eventCorrelation.plot_event_timeframe(related_features, query)

    # show a list of names of changed feature # it should take name of the class it is predicting the values for

    # then check if it is a positive or negative influence i.e. higher for normal or lower for normal.
    # Can we perturb this value to find out the actual threshold on which the behavior changes? If yes then it can also
    # together with the feature (entity name) can be saved in the KG'''


if __name__ == '__main__':
    # cps_td, contextual_variables = discover.discover_context('hsg:RB30_OG4_61-400_standing_light_1')
    run_explanation_system()
