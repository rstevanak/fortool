import json
from pprint import pprint


def analyse(filename):
    with open(filename, 'r') as file:
        json_data = json.load(file)

    pprint(json_data)
