import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline

'''ds = pd.read_csv('Logs/sensor.csv', index_col=0)
ds = ds.drop(columns='sensor_15')
ds = ds.dropna()
ds['timestamp'] = pd.to_datetime(ds['timestamp'])
X = ds.iloc[:, 45:-1].values
y = ds['machine_status']
X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.3, random_state=1)
'''


def train_model(X_train, X_test, y_train, y_test, num_feat, cat_feat):
    """

    :return:
    """
    clf = Pipeline([
        ('PP', ColumnTransformer([
            ('num', StandardScaler(), num_feat),
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_feat)])),
        ('RF', RandomForestClassifier(max_depth=5, n_estimators=15, min_samples_split=3, max_leaf_nodes=5,
                                      random_state=20))])
    clf.fit(X_train, y_train)
    return clf


def predict_ir(X_train, X_test, y_train, y_test, num_feat, cat_feat):
    """

    :return:
    """
    clf = train_model(X_train, X_test, y_train, y_test, num_feat, cat_feat)
    y_pred = clf.predict(X_test)
    from sklearn.metrics import accuracy_score
    from sklearn.metrics import precision_score
    acc = accuracy_score(y_test, y_pred)
    print("Accuraccy:{} ".format(acc))
    return clf
