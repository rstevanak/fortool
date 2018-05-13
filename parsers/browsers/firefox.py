import json
import os
import sqlite3
import configparser
import sys
from base64 import b64decode

from pyasn1.codec.der import decoder
from hashlib import sha1
from Crypto.Cipher import DES3
import hmac


def decrypt3DES(globalSalt, masterPassword, entrySalt, encryptedData):
    """ Decryption of 3DES mozilla way, from https://github.com/lclevy/firepwd
    """
    hp = sha1(globalSalt + masterPassword).digest()
    pes = entrySalt + b'\x00' * (20 - len(entrySalt))
    chp = sha1(hp + entrySalt).digest()
    k1 = hmac.new(chp, pes + entrySalt, sha1).digest()
    tk = hmac.new(chp, pes, sha1).digest()
    k2 = hmac.new(chp, tk + entrySalt, sha1).digest()
    k = k1 + k2
    iv = k[-8:]
    key = k[:24]
    return DES3.new(key, DES3.MODE_CBC, iv).decrypt(encryptedData)


def parse_profile(filename):
    """Parses history, downloads, autofilling forms, and
    passwords if given firefox profile home directory
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
            "time_orig": row[0],
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
        art = {"time": down_meta["endTime"] // 1000,
               "time_orig": down_meta["endTime"],
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
            "time_last_orig": row[0],
            "field": row[1],
            "value": row[2],
            "time_created": row[3],
            "time_created_orig": row[3],
            "number_used": row[4],
        }
        for row in database.execute(query)
    ]
    # TODO: Deleted formhistory
    # TODO: Sessionstore? necessary?

    # Parsing passwords
    # TODO: support signons.sqlite and key3.db
    passwords_path = os.path.join(moz_home, "logins.json")

    if os.path.exists(passwords_path):
        passwords = json.load(open(passwords_path, 'r'))
        profile_arts["passwords"] = [
            {
                "time_last": row['timeLastUsed'] // 1000,
                "time_last_orig": row['timeLastUsed'],
                "site": row['hostname'],
                "time_created": row['timeCreated'],
                "time_created_orig": row['timeCreated'],
                "time_changed": row['timePasswordChanged'],
                "time_changed_orig": row['timePasswordChanged'],
                "encrypted_username": row['encryptedUsername'],
                "encrypted_password": row['encryptedPassword']
            }
            for row in passwords['logins']
        ]
    else:
        passwords_path = os.path.join(moz_home, "signons.sqlite")
        if os.path.exists(passwords_path):
            raise NotImplementedError

    # Password decryption, inspired by https://github.com/lclevy/firepwd
    key_file = os.path.join(moz_home, "key4.db")
    if profile_arts["passwords"] and os.path.exists(key_file):
        db = sqlite3.connect(key_file)
        query = "SELECT item1,item2 FROM metadata WHERE id = 'password';"
        global_salt, pass_check_asn1 = db.execute(query).fetchone()
        pass_check = decoder.decode(pass_check_asn1)
        entrySalt = pass_check[0][0][1][0].asOctets()
        cipher_test = pass_check[0][1].asOctets()
        master_password = b''
        clear_test = decrypt3DES(global_salt, master_password,
                                 entrySalt, cipher_test)
        # successful unciphering of key
        if clear_test == b'password-check\x02\x02':
            a11_asn1 = db.execute("SELECT a11 FROM nssPrivate;").fetchone()
            a11 = decoder.decode(a11_asn1[0])
            entrySalt = a11[0][0][1][0].asOctets()
            cipherKey = a11[0][1].asOctets()
            key = decrypt3DES(global_salt, master_password, entrySalt,
                              cipherKey)[:24]
            # decrypting entries in database
            for entry in profile_arts["passwords"]:
                for field in ['encrypted_username', 'encrypted_password']:
                    # each entry is base64 encoded and serialized in asn1
                    asn1data = decoder.decode(b64decode(entry[field]))
                    iv = asn1data[0][1][1].asOctets()
                    cipher = asn1data[0][2].asOctets()
                    val = DES3.new(key, DES3.MODE_CBC, iv).decrypt(cipher)
                    # Remove PKCS7 paddnig-last byte contains length of padding
                    val = val[:-val[-1]]
                    # Field without 'encrypted_'
                    entry[field[10:]] = val
        else:
            # TODO: passwords input/breaking
            sys.stderr.write("Mozilla user in {} probably uses password\n"
                             "".format(moz_home))
    # Parsing cookies
    database = sqlite3.connect(os.path.join(moz_home, "cookies.sqlite"))
    query = 'SELECT creationTime, baseDomain, value, name FROM moz_cookies;'
    profile_arts["cookies"] = [
        {
            "time_created": row[0] // 1000000,
            "time_created_orig": row[0],
            "site": row[1],
            "value": row[2],
            "name": row[3]
        }
        for row in database.execute(query)
    ]
    return profile_arts


def parse(filename, filesystem_root):
    """Parses all profiles, given firefox home folder"""
    artifacts = {'browser_meta': {'browser_type': 'Mozilla Firefox'}}

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
            without_slash_path = config[prof]['Path'].lstrip('/')
            p_path = os.path.join(filesystem_root, without_slash_path)
        p_tuple = (p_name, p_path)
        profiles.append(p_tuple)
    # TODO: parse firefox version etc.

    # Parsing specific profiles
    artifacts["profiles"] = {}
    for p_name, p_path in profiles:
        artifacts["profiles"][p_name] = parse_profile(p_path)
    return artifacts
