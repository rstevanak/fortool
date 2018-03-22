import json
import os
import sqlite3
import configparser
import sys


def parse_profile(filename):
    """Parses history, downloads, autofilling forms, and
    passwords (not decrypted) if given firefox profile home directory
    exports json of browser format described in artifact_types"""
    moz_home = os.path.abspath(filename)
    profile_arts = {}

    # Parsing browser history
    database = sqlite3.connect(os.path.join(moz_home, "places.sqlite"))
    query = """
    SELECT moz_historyvisits.visit_date, moz_places.url, moz_places.title  
    FROM moz_places, moz_historyvisits 
    WHERE moz_places.id = moz_historyvisits.place_id;
    """
    profile_arts["history"] = [
        {
            "time": row[0] // 1000000,
            "site": row[1],
            "title": row[2]
        }
        for row in database.execute(query)
    ]

    # Parsing browser download history
    query = """
    SELECT tabmeta.content, tabname.content 
    FROM moz_annos AS tabname, moz_annos AS tabmeta, 
    moz_anno_attributes AS typemeta, moz_anno_attributes AS typename  
    WHERE typemeta.name = 'downloads/metaData' 
    AND typename.name = 'downloads/destinationFileURI' 
    AND tabname.anno_attribute_id = typename.id 
    AND tabmeta.anno_attribute_id = typemeta.id 
    AND tabname.place_id = tabmeta.place_id;
    """
    profile_arts["downloads"] = []
    for row in database.execute(query):
        # metadata of download in firefox file is in json format
        down_meta = json.loads(row[0])
        art = {"time_end": down_meta["endTime"] // 1000,
               "filename": row[1],
               "size": down_meta["fileSize"],
               }
        profile_arts["downloads"].append(art)
    # TODO: from where user came to site(referer), bookmarks

    database = sqlite3.connect(os.path.join(moz_home, "formhistory.sqlite"))
    # Parsing formhistory
    query = """
    SELECT lastUsed, fieldname, value, firstUsed, timesused 
    FROM moz_formhistory;
    """
    profile_arts["forms"] = [
        {
            "time_last": row[0] // 1000000,
            "field": row[1],
            "value": row[2],
            "time_created": row[3],
            "number_used": row[4],
        }
        for row in database.execute(query)
    ]
    # TODO: Deleted formhistory
    # TODO: Sessionstore? necessary?

    # Parsing passwords

    passwords_path = os.path.join(moz_home, "logins.json")
    # TODO: make more compatible with historical versions
    if os.path.exists(passwords_path):
        passwords = json.load(open(passwords_path, 'r'))
        profile_arts["passwords"] = [
            {
                "time_last": row['timeLastUsed'] // 1000,
                "site": row['hostname'],
                "time_created": row['timeCreated'],
                "time_changed": row['timePasswordChanged'],
                "encrypted_username": row['encryptedUsername'],
                "encrypted_password": row['encryptedPassword']
            }
            for row in passwords['logins']
        ]
    # TODO: decrypt passwords

    database = sqlite3.connect(os.path.join(moz_home, "cookies.sqlite"))
    query = 'SELECT creationTime, baseDomain, value, name FROM moz_cookies;'
    profile_arts["cookies"] = [
        {
            "time_created": row[0] // 1000000,
            "site": row[1],
            "value": row[2],
            "name": row[3]
        }
        for row in database.execute(query)
    ]
    return profile_arts


def parse(filename):
    """Parses all profiles, given firefox home folder"""
    artifacts = {}

    # Parsing profiles.ini
    config = configparser.ConfigParser()
    try:
        config.read(os.path.join(filename, "profiles.ini"))
    except IOError:
        sys.stderr.write("Couldn't open profiles.ini")
    # In profiles.ini there are sections 'General' and 'Profilex' where x is
    # a number for each profile, so we only want latter.
    conf_profiles = [x for x in config.sections() if x.startswith('Profile')]
    # tuples of (name, path), where are name and path of/to profile
    profiles = []
    for prof in conf_profiles:
        p_name = config[prof]['Name']
        if bool(config[prof]['IsRelative']):
            p_path = os.path.join(filename, config[prof]['Path'])
        else:
            p_path = config[prof]['Path']
        p_tuple = (p_name, p_path)
        profiles.append(p_tuple)
    # TODO: parse firefox version etc.

    # Parsing specific profiles
    artifacts["profiles"] = {}
    for p_name, p_path in profiles:
        artifacts["profiles"][p_name] = parse_profile(p_path)
    return artifacts
