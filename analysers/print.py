import json
from pprint import pformat, pprint

import click


def analyse(parsed):
    return pformat(parsed).split('\n')


@click.command()
@click.argument('filename', type=click.Path(exists=True, file_okay=True,
                                            dir_okay=False, readable=True))
@click.option('--threshold', '-r', type=int,
               help='Number of bad logins as a trigger')
def cli_analyse(filename, threshold=5):
    """Printer available from command line"""
    print(threshold)
    with open(filename, 'r') as file:
        parsed = json.load(file)
        pprint(parsed)


if __name__ == '__main__':
    cli_analyse()
