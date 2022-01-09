import requests

ENDPOINT = ""
API_KEY = ""
headers_value = {"Authorization": "Bearer " + API_KEY}

params = {
}


def get_sensor_names():
    response_data = requests.get(ENDPOINT, params = params, headers = headers_value)

    return response_data.json()


def ask_questions():
    response_data = requests.post(ENDPOINT, params = params, headers = headers_value)

    return response_data.status_code