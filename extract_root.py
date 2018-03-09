from pprint import pprint

import click
import os

import sys

from extract_file import extract_from_file


@click.command()
@click.argument('root', type=click.Path(exists=True, file_okay=False,
                                        dir_okay=True, readable=True))
@click.option('--configuration', '-c',
              type=click.Path(exists=True, file_okay=True, dir_okay=False,
                              readable=True),
              help="filename of configuration to be used")
def extract_from_root(root, configuration):
    """Extracts forensic artifacts from filesystem, given its root and
    configuration file"""
    artifacts = {}
    if not configuration:
        configuration = 'default_extraction.conf'
    conf = open(configuration, 'r')
    # variable to count lines for better error connection in conf
    line_num = -1

    for line in conf:
        line_num += 1

        # ignoring comments
        if line.strip().startswith('#'):
            continue

        # executing one line
        command = line.split()
        # all to which command is applied
        paths = []
        # if path starts with ~ we want to run it through all home folders
        if command[1].startswith('~/'):
            # check if user_data was already loaded
            if not artifacts.get('user_data'):
                sys.stderr.write('user_data not yet loaded\n')
                continue

            for user in artifacts['user_data'].values():
                print(user)
                home_dir = user['home'].strip('/')
                # TODO more robust home_dir sanitation for os.path.join
                # path join works if one address does not begin with /
                p = os.path.join(root, home_dir, command[1][2:])
                paths.append(p)
        # if filename starts with anything else(presumed /)
        else:
            paths = [os.path.join(root, command[1])]

        for filename in paths:
            # If there is no file at given location, it should be skipped
            # this is desirable with for example browsers, because not every
            # user has all browsers installed, but it should be tried
            if not os.path.exists(filename):
                sys.stderr.write("No file at {}, skipping\n".format(filename))
                continue

            # If there is AttributeError, most probably it was bad name of
            # parser in configuration, and execution should be run again with
            #  correct one
            try:
                art = extract_from_file(filename, command[0])
            except AttributeError:
                sys.stderr.write("Error parsing configuration at line "
                                 "{}\n".format(line_num))
                raise
            art_path = command[2].split('.')
            # constructiong path for artifact in final tree if it does not exist
            current_dict = artifacts
            for i in art_path[:-1]:
                if not current_dict.get(i):
                    current_dict[i] = {}
                current_dict = current_dict[i]
            # assigning artifact on its place
            # If there is nothing, just add itself
            if not current_dict.get(art_path[-1]):
                current_dict[art_path[-1]] = art
            # If there is array, append itself
            elif type(current_dict.get(art_path[-1])) == list:
                current_dict[art_path[-1]].append(art)
            # If there already is artifact at the same path, construct array,
            #  where they will be both contained
            else:
                old_art = current_dict[art_path[-1]]
                current_dict[art_path[-1]] = list([old_art])
                current_dict[art_path[-1]].append(art)
    return artifacts


if __name__ == '__main__':
    artifacts = extract_from_root()
    pprint(artifacts)
