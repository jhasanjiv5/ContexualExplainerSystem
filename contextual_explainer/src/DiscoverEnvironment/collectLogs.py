import pandas as pd
import requests
import json


def get_context_logs(context_variables):
    """
    Query the context and create a common data frame out of gathered data

    :param context_variables: List of sensor names
    :return: object (collective data frame)
    """
    dfs = pd.DataFrame(data=None)
    try:
        for c in context_variables:
            result = requests.get(c['link']) #todo: switch request methods based on methods afforded by the contextual variables
            r = result.json()
            data = r['data']
            parsed = json.loads(data)
            df = pd.DataFrame(data=parsed)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            if dfs.empty:
                dfs = df
            else:
                dfs = pd.merge_asof(dfs, df, on='timestamp')

    except Exception as err:
        print(err)
        raise

    return dfs


def get_cps_logs():  # todo: get the logs from CPS
    """

    :return:
    """
    return "empty function"
