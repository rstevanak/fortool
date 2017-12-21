import click
import parsers


@click.command()
@click.argument('filename', type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True))
@click.option('--parser_type', '-p', type=click.Choice(parsers.__all__),
              default='text', help='Type of file to be parsed')
def extract_from_file(filename, parser_type):
    """Extracts forensic artifacts from given file, with right type of parser
    specified"""
    parser = getattr(parsers, parser_type)
    database = parser.parse(filename)
    for artifact in database:
        click.echo(artifact)


if __name__ == '__main__':
    extract_from_file()
