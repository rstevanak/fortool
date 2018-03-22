import json
import click
import parsers


def extract_from_file(filename, parser_type):
    """Extracts forensic artifacts from given file, with right type of parser
    specified"""
    parser = parsers
    for step in parser_type.split('.'):
        parser = getattr(parser, step)
    artifacts = parser.parse(filename)
    return artifacts


# This, so parsers can check if the given parser can be used
def unfold_all_packages(parent_module):
    """Returns all packages and subpackages of given module"""
    # this is so length of loop is modifiable, and all depths of importing
    # can be done
    packages = parent_module.__all__
    i = 0
    while i < len(packages):
        module_name = packages[i]
        module = parent_module
        for step in module_name.split('.'):
            module = getattr(module, step)
        # this means that packages[i] is subpackage and contains more modules
        if '__path__' in dir(module):
            packages.pop(i)
            for submodule in module.__all__:
                packages.append('.'.join([module_name, submodule]))
        else:
            # increasing only here, because otherwise element was popped, so
            # i already points to next element
            i += 1
    return packages


all_parsers = unfold_all_packages(parsers)


@click.command()
@click.argument('filename', type=click.Path(exists=True, file_okay=True,
                                            dir_okay=True, readable=True))
@click.option('--parser_type', '-p', type=click.Choice(all_parsers),
              help='Type of file to be parsed', required=True,
              prompt='These parsers are available:\n' +
                     ', '.join(all_parsers))
@click.option('--output', '-o', type=click.Path(file_okay=True, dir_okay=False,
                                                writable=True),
              help='File, with which resulting json merged, if not stated, '
                   'default is standard output')
def cli_extract_from_file(filename, parser_type, output):
    """Extracts forensic artifacts from given file, with right type of parser
        specified, with click user interface"""
    # click interface should ensure the parser is valid
    artifacts = extract_from_file(filename, parser_type)
    if output:
        with open(output, 'w') as outfile:
            json.dump(artifacts, outfile)
    else:
        print(json.dumps(artifacts))


if __name__ == '__main__':
    cli_extract_from_file()
