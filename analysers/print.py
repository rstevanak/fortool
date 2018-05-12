import json
from pprint import pformat, pprint
import click


def analyse(parsed):
    return pformat(parsed).split('\n')


@click.command()
@click.argument('filename', type=click.Path(exists=True, file_okay=True,
                                            dir_okay=False, readable=True))
def cli_analyse(filename):
    """Printer available from command line"""
    with open(filename, 'r') as file:
        parsed = json.load(file)
        pprint(parsed)


if __name__ == '__main__':
    cli_analyse()
