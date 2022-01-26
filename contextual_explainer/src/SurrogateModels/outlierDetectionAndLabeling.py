import pandas as pd
import numpy as np


def find_outlier_label(df):
    upper_threshold = 1
    lower_threshold = -1

    # Calculate rolling median
    df['rolling_temp'] = df['Temperatura'].rolling(window=3).median()

    # Calculate difference
    df['diff'] = df['Temperatura'] - df['rolling_temp']

    # Flag rows to be dropped as `1`
    df['drop_flag'] = np.where((df['diff'] > upper_threshold) | (df['diff'] < lower_threshold), 1, 0)

    # Drop flagged rows
    df = df[df['drop_flag'] != 1]
    df = df.drop(['rolling_temp', 'rolling_temp', 'diff', 'drop_flag'], axis=1)
