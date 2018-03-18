import subprocess
import re
from datetime import datetime


def parse(filename, command=''):
    return parse_wtmp(filename)


def parse_wtmp(filename):
    # TODO: parse from file, not through last
    # calling last with parameters to maximise extracted information
    raw_output = subprocess.check_output(['last', '--time-format', 'iso',
                                          '-xiw', '-f', filename])
    decoded = raw_output.decode("utf-8")
    artifacts = {'meta': {}, 'data': []}
    # constructing regex to match and group only lines in format:
    # (username) (tty\number) (ip_address) (all other characters till endline)
    iso_datetime_regex = r"(\d{4}-\d{2}-\d{2}T\d{2}\:\d{2}\:\d{2}[+-]\d{4})"
    ip_regex = r"((?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}" \
               r"(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))"
    user_login_regex = r"^(\w+) +(tty\d+) +" + ip_regex + r' +'
    user_login_regex += iso_datetime_regex + r"\W+(.+)$"
    # assigning returned groups from regex into their places
    for line in re.findall(user_login_regex, decoded, re.M):
        login_art = {'username': line[0], 'terminal': line[1],
                     'ip_address': line[2], 'added_info': line[4]}
        # parsing time from iso8601 standard into epoch time
        timestamp = line[3]
        iso8601_parsing = "%Y-%m-%dT%H:%M:%S%z"
        epoch = datetime.strptime(timestamp, iso8601_parsing).timestamp()
        login_art['time'] = epoch//2
        artifacts['data'].append(login_art)
    # TODO: parse restarts and runlevel changes
    # TODO: parse begin_date from file
    return artifacts
