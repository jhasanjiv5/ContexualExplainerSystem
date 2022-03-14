import pandas as pd
import requests
import json


def get_links(cps_td, context_variables):
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
    Query the context and create a common data frame out of gathered data

    :param links: list of links to logs
    :return: object (collective data frame)
    """
    dfs = pd.DataFrame(data=None)
    try:
        for k, c in links.items():
            if '&duration=1' in c:
                result = requests.get(c + '100')
            else:
                result = requests.get(c + '&duration=1100')
            # 'SELECT mean("humidity"), mean("temperature"), mean("light"), mean("uvi"), mean("pressure") FROM "thunderboard_086bd7fe10cb" WHERE time >= now() - 30d and time <= now() GROUP BY time(1h) fill(linear);')
            r = result.json()

            df = pd.DataFrame(data=r)
            df = df.rename(columns={'value': k})
            df['time'] = pd.to_datetime(df['time'])
            if dfs.empty:
                dfs = df
            else:
                dfs = pd.merge_asof(dfs, df, on='time')


    except Exception as err:
        print(err)
        raise
    print(dfs)
    return dfs
