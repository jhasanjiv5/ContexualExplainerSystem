from src.DiscoverEnvironment import collectLogs


def check_for_correlation(dfs):
    """
    show cross correlation percentages to determine if it is worth checking for counterfactuals or not

    :param dfs:
    """
    dfs = collectLogs.get_context_logs()
    print(dfs.corr())

    #todo: check if the function works for more than two serieses.