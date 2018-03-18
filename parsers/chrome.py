import base64
import os
import sqlite3


def parse_profile(filename):
    """Parses history of site visits, downloads and autofill from
    chrome/chromium profile folder"""
    profile_arts = {}
    profile_home = os.path.abspath(filename)
    # Parsing history
    profile_arts["history"] = []
    database = sqlite3.connect(os.path.join(profile_home, "History"))
    query = 'SELECT visits.visit_time, urls.url, visits.visit_duration ' \
            'FROM urls, visits ' \
            'WHERE visits.url = urls.id'
    for row in database.execute(query):
        art = {}
        art["time"] = row[0] // 1000000 - 11644473600
        art["site"], art["duration"] = row[1:3]
        profile_arts["history"].append(art)
    # Parsing downloads
    profile_arts["downloads"] = []
    query = 'SELECT start_time, target_path, received_bytes, total_bytes ' \
            'FROM downloads'
    for row in database.execute(query):
        art = {}
        art["time"] = row[0] // 10000000
        art["filename"], art["down_size"], art["size"] = row[1:]
        profile_arts["downloads"].append(art)
    # Parsing autofill
    profile_arts["forms"] = []
    database = sqlite3.connect(os.path.join(profile_home, "Web Data"))
    query = 'SELECT date_last_used, name, value, date_created FROM autofill'
    for row in database.execute(query):
        art = {}
        art["time_last"], art["field"], art["value"], art["time_created"] = row
        profile_arts["forms"].append(art)
    # Parsing cookies
    profile_arts["cookies"] = []
    database = sqlite3.connect(os.path.join(profile_home, "Cookies"))
    query = 'SELECT creation_utc, host_key, encrypted_value FROM cookies'
    for row in database.execute(query):
        art = {}
        art["time_created"] = row[0] // 10000000
        # This is done in order to be accepted by json
        # json doesn't like bytes
        b64encoded_cookie = base64.b64encode(row[2])
        art["encrypted_value"] = b64encoded_cookie.decode('UTF-8')
        art["site"] = row[1]
        profile_arts["cookies"].append(art)
        # TODO more details about cookies, decrypt values?
        # TODO what does secure in cookies mean
    # TODO: incomplete downloads
    # TODO: segments, segment_usage?
    # TODO: cache, certificates
    return profile_arts


def parse(filename):
    # TODO: parse configuration
    artifacts = {}
    artifacts["profiles"] = {}
    default_profile_path = os.path.join(os.path.abspath(filename), "Default")
    artifacts["profiles"]["Default"] = parse_profile(default_profile_path)
    return artifacts
