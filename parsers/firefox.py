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
    profile_arts["history"] = []
    database = sqlite3.connect(os.path.join(moz_home, "places.sqlite"))
    query = "SELECT moz_historyvisits.visit_date, moz_places.url, " \
            "moz_places.title " \
            "FROM moz_places, moz_historyvisits " \
            "WHERE moz_places.id = moz_historyvisits.place_id;"
    for row in database.execute(query):
        art = {"time": row[0] // 1000000, "site": row[1], "title": row[2]}
        profile_arts["history"].append(art)

    # Parsing browser download history
    profile_arts["downloads"] = []
    query = "SELECT tabmeta.content, tabname.content " \
            "FROM moz_annos AS tabname, moz_annos AS tabmeta, " \
            "moz_anno_attributes AS typemeta, " \
            "moz_anno_attributes AS typename " \
            "WHERE typemeta.name = 'downloads/metaData' " \
            "AND typename.name = 'downloads/destinationFileURI'" \
            "AND tabname.anno_attribute_id = typename.id " \
            "AND tabmeta.anno_attribute_id = typemeta.id " \
            "AND tabname.place_id = tabmeta.place_id;"
    for row in database.execute(query):
        # metadata of download in firefox file is in json format
        down_meta = json.loads(row[0])
        art = {}
        art["time_end"] = down_meta["endTime"] // 1000
        art["filename"] = row[1]
        art["size"] = down_meta["fileSize"]
        profile_arts["downloads"].append(art)
    # TODO: from where user came to site, bookmarks

    database = sqlite3.connect(os.path.join(moz_home, "formhistory.sqlite"))

    # Parsing formhistory
    profile_arts["forms"] = []
    query = "SELECT lastUsed, fieldname, value, firstUsed, timesused " \
            "FROM moz_formhistory;"
    for row in database.execute(query):
        art = {}
        art["time_last"] = row[0] // 1000000
        art["field"], art["value"], art["time_created"] = row[1:4]
        art["number_used"] = row[4]
        profile_arts["forms"].append(art)
    # TODO: Deleted formhistory
    # TODO: Sessionstore? necessary?

    # Parsing passwords
    profile_arts["passwords"] = []
    passwords = json.load(open(os.path.join(moz_home, "logins.json")))
    for row in passwords['logins']:
        art = {}
        art["time_last"] = row['timeLastUsed'] // 1000
        art["site"] = row['hostname']
        art["time_created"] = row['timeCreated']
        art["time_changed"] = row['timePasswordChanged']
        art["encrypted_username"] = row['encryptedUsername']
        art["encrypted_password"] = row['encryptedPassword']
        profile_arts["passwords"].append(art)
        # TODO: decrypt passwords

    database = sqlite3.connect(os.path.join(moz_home, "cookies.sqlite"))
    query = 'SELECT creationTime, baseDomain, value, name FROM moz_cookies;'
    profile_arts["cookies"] = []
    for row in database.execute(query):
        art = {}
        art["time_created"] = row[0] // 1000000
        art["site"], art["value"], art["name"] = row[1:4]
        profile_arts["cookies"].append(art)
    return profile_arts
    # TODO: make compatible with old versions of firefox


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
