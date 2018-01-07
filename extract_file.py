from pprint import pprint

import click
import parsers


def extract_from_file(filename, parser_type):
    """Extracts forensic artifacts from given file, with right type of parser
    specified"""
    parser = getattr(parsers, parser_type)
    artifacts = parser.parse(filename)
    return artifacts


@click.command()
@click.argument('filename', type=click.Path(exists=True, file_okay=True,
                                            dir_okay=True, readable=True))
@click.option('--parser_type', '-p', type=click.Choice(parsers.__all__),
              help='Type of file to be parsed')
def cli_extract_from_file(filename, parser_type):
    """Extracts forensic artifacts from given file, with right type of parser
        specified, with click user interface"""
    artifacts = extract_from_file(filename, parser_type)
    pprint(artifacts)


if __name__ == '__main__':
    cli_extract_from_file()
