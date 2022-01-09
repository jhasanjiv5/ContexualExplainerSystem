import pandas as pd
from sklearn import model_selection
from sklearn.tree import DecisionTreeClassifier

ds = pd.read_csv('Logs/sensor.csv', index_col=0)
ds = ds.drop(columns='sensor_15')
ds = ds.dropna()
ds['timestamp'] = pd.to_datetime(ds['timestamp'])
X = ds.iloc[:, 45:-1].values
y = ds['machine_status']
X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.3, random_state=1)


def train_model():
    """

    :return:
    """
    clf = DecisionTreeClassifier()
    clf = clf.fit(X_train, y_train)
    return clf


def predict_ir():
    """

    :return:
    """
    clf = train_model()
    y_pred = clf.predict(X_test)
    from sklearn.metrics import accuracy_score
    acc = accuracy_score(y_test, y_pred)
    print(acc)
    return clf
