from pprint import pprint


def analyse(filename):
    with open(filename, 'r') as file:
        pprint(file)
