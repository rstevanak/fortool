import json
import os
import sqlite3
import configparser
import sys


def parse_profile(filename):
    """Parses history, downloads, autofilling forms, and
    passwords (not decrypted) if given firefox profile home directory"""
    moz_home = os.path.abspath(filename)
    artifacts = set()

    database = sqlite3.connect(os.path.join(moz_home, "places.sqlite"))

    # Parsing browser history
    query = "SELECT moz_historyvisits.visit_date, moz_places.url " \
            "FROM moz_places, moz_historyvisits " \
            "WHERE moz_places.id = moz_historyvisits.place_id;"
    history = database.execute(query)
    for row in history:
        art_time = row[0] // 1000000
        art_desc = "User visited {}".format(row[1])
        artifacts.add((art_time, "firefox history", art_desc))

    # Parsing browser download history
    query = "SELECT tabmeta.content, tabname.content " \
            "FROM moz_annos AS tabname, moz_annos AS tabmeta, " \
            "moz_anno_attributes AS typemeta, " \
            "moz_anno_attributes AS typename " \
            "WHERE typemeta.name = 'downloads/metaData' " \
            "AND typename.name = 'downloads/destinationFileURI'" \
            "AND tabname.anno_attribute_id = typename.id " \
            "AND tabmeta.anno_attribute_id = typemeta.id " \
            "AND tabname.place_id = tabmeta.place_id;"
    downloads = database.execute(query)
    for row in downloads:
        # metadata of download in firefox file is in json format
        down_meta = json.loads(row[0])
        art_time = down_meta["endTime"] // 1000
        art_desc = "Downloaded file {} of size {} B" \
                   "".format(row[1], down_meta["fileSize"])
        artifacts.add((art_time, "firefox downloads", art_desc))
    # TODO: from where user came to site, bookmarks

    database = sqlite3.connect(os.path.join(moz_home, "formhistory.sqlite"))

    # Parsing formhistory
    query = "SELECT lastUsed, fieldname, value, firstUsed, timesused " \
            "FROM moz_formhistory"
    form_history = database.execute(query)
    for row in form_history:
        art_time = row[0] // 1000000
        art_desc = "User last input into field \"{}\" value \"{}\" " \
                   "created on {}, since used {} times".format(*row[1:])
        artifacts.add((art_time, "firefox formhistory", art_desc))
    # TODO: Deleted formhistory
    # TODO: Sessionstore? necessary?

    # Parsing passwords
    passwords = json.load(open(os.path.join(moz_home, "logins.json")))
    for row in passwords['logins']:
        art_time = row['timeLastUsed'] // 1000

        art_desc = "User last used password on {} created on {}, last " \
                   "changed on {}, encrypted username:\"{}\" encrypted " \
                   "password: \"{}\"" \
                   "".format(row['hostname'], row['timeCreated'],
                             row['timePasswordChanged'],
                             row['encryptedUsername'],
                             row['encryptedPassword'])
        artifacts.add((art_time, "firefox password", art_desc))
        # TODO: decrypt passwords
    # TODO: make compatible with old versions of firefox

    database = sqlite3.connect(os.path.join(moz_home, "cookies.sqlite"))
    query = 'SELECT creationTime, baseDomain, value FROM moz_cookies'
    for row in database.execute(query):
        art_time = row[0] // 1000000
        art_desc = "Created cookie from site {} with value {}" \
                   "".format(*row[1:])
        artifacts.add((art_time, "firefox cookie", art_desc))
        # TODO more details about cookies - name
    return artifacts


def parse(filename):
    """Parses all profiles, given firefox home folder"""
    artifacts = set()
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
    for p_name, p_path in profiles:
        artifacts |= parse_profile(p_path)
        # TODO: Differentiate users in artifact type
    return artifacts
