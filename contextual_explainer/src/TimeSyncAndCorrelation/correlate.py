from DiscoverEnvironment import collectLogs
import numpy as np
import matplotlib.pyplot as plt
from tslearn.metrics import dtw_path


def check_for_correlation(ds):
    """
    show cross correlation percentages to determine if it is worth checking for counterfactuals or not

    :param dfs:
    """
    x = ds['sensor_13'].head(1000)
    y = ds['sensor_45'].head(1000)

    corr1 = np.corrcoef(x, y)
    print(f'Correlation before DTW: {corr1[0, 1]:.4f}')

    temp, _ = dtw_path(x, y)
    x_path, y_path = zip(*temp)
    x_path = np.asarray(x_path)
    y_path = np.asarray(y_path)
    x_warped = x[x_path]
    y_warped = y[y_path]

    corr2 = np.corrcoef(x_warped, y_warped)
    print(f'Correlation after DTW: {corr2[0, 1]:.4f}')

    return corr2

    # todo: check if the function works for more than two serieses.
