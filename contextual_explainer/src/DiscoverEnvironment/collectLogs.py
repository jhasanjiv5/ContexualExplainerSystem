import pandas as pd
import requests
import time


def get_links(cps_td, context_variables):
    """
    Query the context and coolect URIs

    :param cps_td 
    :param context_variables
    :return: object (collectionod links)
    """
    links = dict()
    results = requests.get(cps_td)
    r = results.json()
    for i in r['properties']:
        links.update({
            i: r['properties'][i]['forms'][0]['href']})

    for l in context_variables:
        results = requests.get(l)
        r = results.json()
        for i in r['properties']:
            links.update({
                i: r['properties'][i]['forms'][0]['href']})

    return links


def get_logs(links):
    """
    Query the context and create a common data frame from gathered data

    :param links: list of links to logs
    :return: object (collective data frame)
    """
    dfs = pd.DataFrame(data=None)
    try:
        for k, c in links.items():
            # for using the demo living-campus TDs with 10.2.2.33 address
            c = c.replace('10.2.2.33', '127.0.0.1')
            if '&duration=1' in c:
                result = requests.get(c)
            else:
  
                result = requests.get(c + '&duration=1100')
            if result.status_code == 200:
                r = result.json()
                if len(r) == 0:
                    t_end = time.time() + 10 #ask for next 1000(seconds) entries one at a time, it can be modified based on the data frequeny of the sensor
                    data_dict = dict()
                    while time.time() < t_end:
                        data_dict.update((requests.get(c)).json())                   
                        
                    df = pd.DataFrame(data=data_dict)
                    if not df.empty:
                        df = df.rename(columns={'value': k})
                        df['time'] = pd.to_datetime(df['time'])
                        if dfs.empty:
                            dfs = df
                        else:
                            dfs = pd.merge_asof(dfs, df, on='time')
                else:
                    df = pd.DataFrame(data=r)
                    if not df.empty:
                        df = df.rename(columns={'value': k})
                        df['time'] = pd.to_datetime(df['time'])
                        if dfs.empty:
                            dfs = df
                        else:
                            dfs = pd.merge_asof(dfs, df, on='time')
    except Exception as err:
        print(err)
        raise
    dfs.fillna(0, inplace=True)
    dfs.to_csv('data.csv', sep=',')
    # dfs = pd.read_csv('data.csv', sep=',')
    return dfs
