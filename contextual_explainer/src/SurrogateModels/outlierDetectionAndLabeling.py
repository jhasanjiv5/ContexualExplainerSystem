import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def find_outlier_label(df):
    clf=IsolationForest(n_estimators=100, max_samples='auto', contamination=float(.12), max_features=1.0, bootstrap=False, n_jobs=-1, random_state=42, verbose=0)
    clf.fit(df)
    df['anomaly']=clf.predict(df)
    df['anomaly'].replace({-1:0}, inplace=True)
    # outliers=df.loc[df['anomaly']==-1]
    # outlier_index=list(outliers.index)
    #print(outlier_index)
    #Find the number of anomalies and normal points here points classified -1 are anomalous
    # print(outlier_index)
    return df
