from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
from influxdb import DataFrameClient
import config

app = Flask(__name__)
api = Api(app)

client = DataFrameClient(host=config.url, port=config.port, username=config.user, password=config.password,
                         database=config.database_name)


class ExplainInfluence(Resource):
    def get(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('sensorname', required=True)  # add args
        args = parser.parse_args()  # parse arguments to dictionary
        # query based on time SELECT * FROM "absolutismus" WHERE time = '2016-07-31T20:07:00Z' OR time = '2016-07-31T23:07:17Z'
        if args['sensorname'] == 'Sensor0618-humidity':
            result = client.query(
                'SELECT mean("humidity") FROM "thunderboard_14b4576da75c" WHERE time >= now() - 30d and time <= now() GROUP BY time(1h) fill(null);')
            df = pd.DataFrame(data=result['thunderboard_14b4576da75c'])
            df = df.rename_axis('timestamp').reset_index()
            df = df.rename(columns={'mean': 'Humidity'})
        elif args['sensorname'] == 'Sensor0617-temperature':
            result = client.query(
                'SELECT mean("temperature") FROM "thunderboard_14b4576da75c" WHERE time >= now() - 30d and time <= now() GROUP BY time(1h) fill(null);')
            df = pd.DataFrame(data=result['thunderboard_14b4576da75c'])
            df = df.rename_axis('timestamp').reset_index()
            df = df.rename(columns={'mean': 'Temperature'})
        elif args['sensorname'] == 'co2':
            result = client.query(
                'SELECT mean("co2") FROM "ganesh_sensorbrd_2" WHERE time >= now() - 30d and time <= now() GROUP BY time(1h) fill(null);')
            df = pd.DataFrame(data=result['ganesh_sensorbrd_2'])
            df = df.rename_axis('timestamp').reset_index()
            df = df.rename(columns={'mean': 'Co2'})
        else:
            return {
                       'message': f"'{args['sensorname']}' not found!"
                   }, 400

        return {'data': df.to_json(orient='records', date_format='iso')}, 200  # return data with 200 OK


api.add_resource(ExplainInfluence, '/influence')  # add endpoints

if __name__ == '__main__':
    app.run()  # run our Flask app
