import requests
import json
import os

DC_API_URL = os.environ.get('DC_API_URL')


def get_cycle_info():
    info_url = DC_API_URL + "/public"
    response = requests.get(info_url)
    data = response.json()

    return data
