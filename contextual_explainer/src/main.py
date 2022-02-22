from DiscoverEnvironment import collectLogs, discover
from TimeSyncAndCorrelation import correlate
from SurrogateModels import classifier as cl
from sklearn import model_selection
from Explainers import explainer as ex
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
from tabulate import tabulate
from keywordExtraction import keywordExtract as ky


def find_keywords(query):
    message_keywords = ky.keyword_extract(query)
    message_keywords_lower = [x.lower() for x in message_keywords]
    return message_keywords_lower


def explain_graph(option):
    st.write(option)
    location, contextual_variables = discover.discover_context()
    '''Context discovered at:'''
    st.write(location)

    '''Found contextual factors:'''
    st.write(contextual_variables)


def visualize_explanation(clf, cf, query_instance, feature_names):
    """
    :param clf:
    :param cf:
    :param query_instance:
    """

    st.text('Counterfactual tagret class:')
    st.text(clf.predict(cf))

    st.text('Counterfactuals:')
    st.text(tabulate(cf, headers=feature_names, tablefmt='pretty', missingval='N/A'))

    st.text('List of causally relevant features:')
    related_features = []
    diff = np.where(cf != query_instance)[1]
    for i in diff:
        related_features.append(feature_names[i])
    # show explanation for top related feature instead of selection box for simplicity
    explain_graph(related_features[0])


if __name__ == '__main__':
    st.title(
        '''
        Contextual Explanation System
        '''
    )
    im2 = Image.open("contextual_explainer/src/Figures/banner.jpeg")
    st.sidebar.image([im2])
    # location, context_variables = discover.discover_context()
    # dfs = collectLogs.get_context_logs(context_variables)
    query = st.sidebar.text_input('Query:', 'please ask here...')
    time = st.sidebar.text_input('Time:', 'at what time...')
    st.sidebar.text('Found Keywords:')
    st.sidebar.text(find_keywords(query))

    if st.sidebar.button('Explain'):
        sensors = pd.read_csv(
            '/Users/sanjivjha/PycharmProjects/ContexualExplainerSystem/contextual_explainer/src/Logs/sensor.csv',
            index_col=0)
        sensors = sensors.fillna(0)
        sensors['timestamp'] = pd.to_datetime(sensors['timestamp'])
        sensors = sensors.drop(columns=['sensor_15'])
        sensors = sensors.replace('RECOVERING', 1)  # classes should be binary and 0 and 1 forms
        sensors = sensors.replace('BROKEN', 1)
        sensors = sensors.replace('NORMAL', 0)
        # correlate.check_for_correlation(sensors)  # select features based of the correlation values
        X = sensors.drop(columns=['timestamp', 'machine_status'])
        y = sensors.loc[:, 'machine_status']
        feature_names = list(X.columns)
        X = X.values  # only supports arrays atm
        y = y.values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=20)
        cat_feat = []
        num_feat = list(np.arange(len(feature_names)))
        instance_list = [0.109201, 46.441, 46.7014, 43.0121, 271.777, 0, 11.0677, 0, 11.1111, 16.0952, 1.23923, 0, 0, 0,
                         420.073,
                         463.138, 463.99, 2.53908, 665.888, 399.281, 879.61, 500.705, 997.563, 618.66, 724.126, 863.414,
                         546.332,
                         1136.95, 732.2, 632.87, 942.708, 817.858, 569.395, 178.586, 374.13, 301.229, 91.1615, 29.1667,
                         23.4375,
                         28.6458, 24.4792, 26.5625, 29.9479, 30.0926, 30.0926, 30.9606, 32.1181, 33.5648, 32.1181,
                         36.169,
                         36.169]
        query_instance = np.array(instance_list, dtype=np.float64).reshape(1, len(instance_list))
        clf = cl.predict_ir(X_train, X_test, y_train, y_test, num_feat, cat_feat)

        st.text('Model Decision:')
        st.text(clf.predict(query_instance))

        st.text('Query Instance:')
        st.text(tabulate(query_instance, headers=feature_names, tablefmt='pretty', missingval='N/A'))

        cf = ex.nice_explain(lambda x: clf.predict_proba(x), X_train, cat_feat, num_feat, y_train,
                             query_instance)
        visualize_explanation(clf, cf, query_instance, feature_names)  # show a list of names of changed feature

        # then check if it is a positive or negative influence i.e. higher for normal or lower for normal.
        # Can we perturb this value to find out the actual threshold on which the behavior changes? If yes then it can also
        # together with the feature (entity name) can be saved in the KG'''
