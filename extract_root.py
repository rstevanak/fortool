from pprint import pprint

import click
import os
from extract_file import extract_from_file


@click.command()
@click.argument('root', type=click.Path(exists=True, file_okay=False,
                                        dir_okay=True, readable=True))
def extract_from_root(root):
    """Extracts forensic artifacts from filesystem, given its root"""
    artifacts = {}
    # TODO: go through homes from passwd
    for user in os.listdir(os.path.join(root, "home")):
        artifacts[user] = []
        home_dir = os.path.join(root, "home", user)
        firefox_home = os.path.join(home_dir, ".mozilla", "firefox")
        artifacts[user].append(extract_from_file(firefox_home, 'firefox'))
        chrome_home = os.path.join(home_dir, ".config", "chromium")
        artifacts[user].append(extract_from_file(chrome_home, 'chrome'))
        # artifacts |= extract_from_file(home_dir, 'file_metadata')

    logs_dir = os.path.join(root, 'var', 'log')
    # TODO: make this more universal(to include rhel)
    logs = ['syslog', 'dpkg.log', 'kern.log', 'auth.log']
    # TODO look through files in directory, log rotation
    # for i_log in logs:
    #     i_log_path = os.path.join(logs_dir, i_log)
    #     artifacts["LogArtifact"] = extract_from_file(i_log_path, 'logs')

    return artifacts


if __name__ == '__main__':
    artifacts = extract_from_root()
    pprint(artifacts)
