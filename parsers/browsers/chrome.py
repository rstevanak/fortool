import base64
import os
import sqlite3

# Chrome uses this time offset in seconds against epoch in some cases
# This should be the difference between 1.1.1601 and 1.1.1970
OFFSET = 11644473600


def parse_profile(filename):
    """Parses history of site visits, downloads and autofill from
    chrome/chromium profile folder"""
    profile_arts = {}
    profile_home = os.path.abspath(filename)

    # Parsing history
    database = sqlite3.connect(os.path.join(profile_home, "History"))
    query = """
    SELECT visits.visit_time, urls.url, visits.visit_duration 
    FROM urls, visits
    WHERE visits.url = urls.id
    """
    profile_arts["history"] = [
        {
            "time": row[0] // 1000000 - OFFSET,
            "time_orig": row[0],
            "site": row[1:3][0],
            "duration": row[1:3][1],
        }
        for row in database.execute(query)
    ]

    # Parsing downloads
    query = """
    SELECT start_time, target_path, received_bytes, total_bytes 
    FROM downloads
    """
    profile_arts["downloads"] = [
        {
            "time": row[0] // 10000000 - OFFSET,
            "time_orig": row[0],
            "filename": row[1],
            "down_size": row[2],
            "size": row[3],
        }
        for row in database.execute(query)
    ]

    # Parsing autofill
    database = sqlite3.connect(os.path.join(profile_home, "Web Data"))
    query = """
    SELECT date_last_used, name, value, date_created 
    FROM autofill
    """
    profile_arts["forms"] = [
        {
            "time_last": row[0],
            "time_last_orig": row[0],
            "field": row[1],
            "value": row[2],
            "time_created": row[3],
            "time_created_orig": row[3],
        }
        for row in database.execute(query)
    ]
    # Parsing cookies

    database = sqlite3.connect(os.path.join(profile_home, "Cookies"))
    query = """
    SELECT creation_utc, host_key, encrypted_value 
    FROM cookies
    """
    profile_arts["cookies"] = [
        {
            "time_created": row[0] // 10000000 - OFFSET,
            "time_created_orig": row[0],
            "value": base64.b64encode(row[2]).decode('UTF-8'),
            "site": row[1],
        }
        for row in database.execute(query)
    ]
    database = sqlite3.connect(os.path.join(profile_home, 'Login Data'))
    query = """
    SELECT date_created, origin_url, username_value, password_value
    FROM logins;
    """
    profile_arts["passwords"] = [
        {
            "time_created": row[0] // 10000000 - OFFSET,
            "time_created_orig": row[0],
            "site": row[1],
            "username": row[2],
            "password": row[3],
        }
        for row in database.execute(query)
    ]
    # TODO: incomplete downloads
    # TODO: segments, segment_usage?
    # TODO: cache, certificates
    return profile_arts


def parse(filename, filesystem_root):
    # TODO: parse configuration
    artifacts = {
        "profiles": {},
        'browser_meta': {
            'browser_type': 'Chrome/Chromium'
        }
    }
    default_profile_path = os.path.join(os.path.abspath(filename), "Default")
    artifacts["profiles"]["default"] = parse_profile(default_profile_path)
    return artifacts
