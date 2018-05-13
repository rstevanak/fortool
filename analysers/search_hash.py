import json
import sys

import click


def search(parsed, hashes):
    """ Looks for all files and returns list of found file metadata"""
    # create dictionary for efficient looking through
    all_files = parsed.get('file_metadata')
    if not all_files:
        sys.stderr.write('No file metadata, exiting\n')
        sys.exit()
    all_hashes = {}
    for filename in all_files:
        file_hash = all_files[filename].get('md5')
        # directories and links do not have hashes
        if file_hash:
            all_hashes[file_hash] = (filename, all_files[filename])

    # now for each hash in hashes we check whether we have it
    found = []
    for search_hash in hashes:
        if search_hash in all_hashes:
            found.append(all_hashes[search_hash])
    return found


@click.command()
@click.argument('filename', type=click.Path(exists=True, file_okay=True,
                                            dir_okay=False, readable=True))
@click.option('--hashes', '-h', type=click.Path(exists=True, file_okay=True,
                                                dir_okay=False, readable=True),
              prompt="Please input path to hash file:",
              help='Path to file with hashes to search for')
def cli_analyse(filename, hashes):
    with open(filename, 'r') as file:
        parsed = json.load(file)
    with open(hashes) as hash_file:
        hashes_text = hash_file.readlines()
    # get rid of endlines
    hashes_text = [x.strip() for x in hashes_text]
    output = search(parsed, hashes_text)
    for i in output:
        print(i)


if __name__ == '__main__':
    cli_analyse()
