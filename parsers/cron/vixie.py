from os.path import join, isdir, basename
from os import listdir
import re


def parse(filename, filesystem_root):
    """Parses all crontabs for all users provided /var/spool/cron/crontab"""
    artifacts = {}
    # if not given directory, parse only that file
    if not isdir(filename):
        artifacts[basename(filename)] = parse_vixie_crontab(filename)

    for user_crontab in listdir(filename):
        crontab_path = join(filename, user_crontab)
        artifacts[user_crontab] = parse_vixie_crontab(crontab_path)
    return artifacts


def parse_vixie_crontab(filename):
    artifacts = []
    with open(filename, 'r') as f:
        for line in f:
            # TODO: maybe rewrite regex to use groups and be more readable
            if not re.match(r'(([0-9]{1,2}|\*|\*/[0-9]+)\s){5}.+', line):
                continue
            words = line.split()
            art = {
                "cron_time": " ".join(words[:5]),
                "job": " ".join(words[5:]),
            }
            artifacts.append(art)
    return artifacts
