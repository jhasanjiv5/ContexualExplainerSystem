from src.DiscoverEnvironment import collectLogs, discover

if __name__ == '__main__':
    #location, context_variables = discover.discover_context()
    #collectLogs.get_context_logs(context_variables)
    '''clf = cl.predict_ir()
    ds = pd.read_csv('Logs/sensor.csv', index_col=0)
    ds = ds.drop(columns='sensor_15')
    ds = ds.dropna()
    ds['timestamp'] = pd.to_datetime(ds['timestamp'])
    X = ds.iloc[:, 45:-1].values
    y = ds['machine_status']
    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.3, random_state=1)
    num_feat = []
    cat_feat = []
    ex.nice_explain(clf, ds, X_test[0:1])'''
