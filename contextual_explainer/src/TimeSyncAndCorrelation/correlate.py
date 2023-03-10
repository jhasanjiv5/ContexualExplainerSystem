from ctypes import sizeof
from DiscoverEnvironment import collectLogs
import numpy as np
import matplotlib.pyplot as plt
from tslearn.metrics import dtw_path


def check_for_correlation(base, variable):
    """
    show cross correlation percentages to determine if it is worth checking for counterfactuals or not

    :param base:
    :param variable:
    """

    return np.corrcoef(base, variable)[0, 1]

    # todo: check if the function works for more than two serieses.
