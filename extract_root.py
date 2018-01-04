import click
import os
from extract_file import extract_from_file


@click.command()
@click.argument('root', type=click.Path(exists=True, file_okay=False,
                                            dir_okay=True, readable=True))
def extract_from_root(root):
    """Extracts forensic artifacts from filesystem, given its root"""
    artifacts = set()
    #TODO: go through homes from passwd
    for user_home in os.listdir(os.path.join(root, "home")):
        home_dir = os.path.join(root, "home", user_home)
        firefox_home = os.path.join(home_dir, ".mozilla", "firefox")
        artifacts |= extract_from_file(firefox_home, 'firefox')
        chrome_home = os.path.join(home_dir, ".config", "chromium", "Default")
        artifacts |= extract_from_file(chrome_home, 'chrome')
        # artifacts |= extract_from_file(home_dir, 'file_metadata')

    logs_dir = os.path.join(root, 'var', 'log')
    # TODO: make this more universal(to include rhel)
    logs = ['syslog', 'dpkg.log', 'kern.log', 'auth.log']
    # TODO look through files in directory, log rotation
        # for i_log in logs:
        #     i_log_path = os.path.join(logs_dir, i_log)
        #     artifacts |= extract_from_file(i_log_path, 'logs')

    for row in sorted(artifacts, key=lambda tup: tup[0]):
        click.echo("{}\t{}\t{}".format(*row))


if __name__ == '__main__':
    extract_from_root()
