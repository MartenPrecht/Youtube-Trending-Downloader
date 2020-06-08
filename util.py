import json
import os

with open('config.json') as file:
    config = json.load(file)

data_path = os.path.join(os.getcwd(), config['data_path']) if not config['data_path'].startswith('/') else config['data_path']
countries = config['countries']
