from pprint import pprint

import click
import analysers


def analyse_from_file(filename, analyser_type):
    """Analyses artifacts collected by parsers in file on filename address"""
    analyser = getattr(analysers, analyser_type)
    artifacts = analyser.analyse(filename)
    return artifacts


@click.command()
@click.argument('filename', type=click.Path(exists=True, file_okay=True,
                                            dir_okay=True, readable=True))
@click.option('--analyser_type', '-a', type=click.Choice(analysers.__all__),
              help='Type of analyser you want to use', required=True,
              prompt='These analysers are available:\n' +
                     ', '.join(analysers.__all__))
def cli_analyse_from_file(filename, analyser_type):
    """Just passes arguments to function 'analyse_from_file' from command
    line """
    analyse_from_file(filename, analyser_type)


if __name__ == '__main__':
    cli_analyse_from_file()
