from influxdb import DataFrameClient
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json


def get_current_values_of_active_sensors():
    sensor_data = {
        "timestamp": None,
        "co2": 0,
        "humidity": 0,
        "light": 0,
        "motion": 0,
        "sound": 0,
        "temperature": 0,
    }
    url = "interactions.ics.unisg.ch"
    user = "admin"
    password = "inthrustwetrust"
    client = DataFrameClient(host=url, port=8086, username=user, password=password, database='sensor_net')
    result = client.query("SELECT * FROM room_402 ORDER BY ASC LIMIT 1")

    df = pd.DataFrame.from_dict(result['room_402'])
    if df.empty:
        print('Sorry ☹️, I can not read current sensor status of your room!')
        return 'Sorry ☹️, I can not read current sensor status of your room!'

    sensor_data['timestamp'] = np.datetime_as_string(df.index.values[0])

    for s in sensor_data:
        if not s == "timestamp":
            if s in df.columns:
                sensor_data[s] = df.iloc[0][s]

    return sensor_data


def get_current_values_of_active_sensors2(context_variables=['co2', 'humidity', 'temperature']):
    """
    Query the context and create a common data frame out of gathered data

    :param sensor_names: List of sensor names
    :return: object (collective data frame)
    """
    # todo: remove the table names from the sql queries. Create an api to serve these values and depending on the
    #  context variable names (sensor names) create the data frame with same column names.
    dfs = pd.DataFrame(data=None)
    try:
        for c in context_variables:
            result = requests.get("http://127.0.0.1:5000/context?sensorname=" + c)
            r = result.json()
            data = r['data']
            parsed = json.loads(data)
            df = pd.DataFrame(data=parsed)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            if dfs.empty:
                dfs = df
            else:
                dfs = pd.merge_asof(dfs, df, on='timestamp')
        print(dfs)
        return dfs
    except Exception as err:
        print(err)
        raise
