from DiscoverEnvironment import collectLogs, discover
from TimeSyncAndCorrelation import correlate
import pandas as pd

if __name__ == '__main__':
    #location, context_variables = discover.discover_context()
    #dfs = collectLogs.get_context_logs(context_variables)
    ds = pd.read_csv('contextual_explainer/src/Logs/sensor.csv', index_col=0)
    ds = ds.drop(columns='sensor_15')
    ds = ds.dropna()
    ds['timestamp'] = pd.to_datetime(ds['timestamp'])
    correlate.check_for_correlation(ds)
    clf = cl.predict_ir()
    X = ds.iloc[:, 45:-1].values
    y = ds['machine_status']
    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.3, random_state=1)
    num_feat = []
    cat_feat = []
    ex.nice_explain(clf, ds, X_test[0:1])
