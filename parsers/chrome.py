import os
import sqlite3


def parse(filename):
    """Parses history of site visits, downloads and autofill from
    chrome/chromium folder. Returns set() of all artifacts found"""
    artifacts = set()
    chrome_home = os.path.abspath(filename)
    # Parsing history
    database = sqlite3.connect(os.path.join(chrome_home, "History"))
    query = 'SELECT visits.visit_time, urls.url, visits.visit_duration ' \
            'FROM urls, visits ' \
            'WHERE visits.url = urls.id'
    for row in database.execute(query):
        visit_time = row[0]//1000000 - 11644473600
        visit_desc = "User visited {} for {} seconds".format(*row[1:])
        artifacts.add((visit_time, "chrome history", visit_desc))
    # Parsing downloads
    query = 'SELECT start_time, target_path, received_bytes, total_bytes ' \
            'FROM downloads'
    for row in database.execute(query):
        art_time = row[0]//10000000
        art_desc = "Downloaded file {} ({}B/{}B)".format(*row[1:])
        artifacts.add((art_time, "chrome downloads", art_desc))
    # Parsing autofill
    database = sqlite3.connect(os.path.join(chrome_home, "Web Data"))
    query = 'SELECT date_last_used, name, value, date_created FROM autofill'
    for row in database.execute(query):
        art_time = row[0]
        art_desc = "User last input into field \"{}\" value \"{}\", " \
                   "first input on {}".format(*row[1:])
        artifacts.add((art_time, "chrome autofill", art_desc))
    # Parsing cookies
    database = sqlite3.connect(os.path.join(chrome_home, "Cookies"))
    query = 'SELECT creation_utc, host_key, encrypted_value FROM cookies'
    for row in database.execute(query):
        art_time = row[0]//10000000
        art_desc = "Created cookie from site {} with encrypted value {}" \
                   "".format(*row[1:])
        artifacts.add((art_time, "chrome cookie", art_desc))
        # TODO more details about cookies, decrypt values?
    # TODO: incomplete downloads
    # TODO: segments, segment_usage?
    # TODO: passwords, cookies, cache, certificates
    # TODO: parse all users

    return artifacts
