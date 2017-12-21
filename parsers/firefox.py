import json
import os
import sqlite3


def parse(filename):
    moz_home = os.path.abspath(filename)
    artifacts = set()

    database = sqlite3.connect(os.path.join(moz_home, "places.sqlite"))
    c = database.cursor()
    #Parsing browser history
    history = c.execute("SELECT moz_historyvisits.visit_date, moz_places.url FROM moz_places, moz_historyvisits"
                        " WHERE moz_places.id = moz_historyvisits.place_id;")
    for row in history:
        artifacts.add((row[0]/1000000, "mozilla history", "User visited " + str(row[1])))
    #Parsing browser download history
    downloads = c.execute("SELECT tabname.content, tabmeta.content FROM moz_annos AS tabname, moz_annos AS tabmeta, "
                          "moz_anno_attributes AS typemeta, moz_anno_attributes AS typename "
                          "WHERE typemeta.name = 'downloads/metaData' "
                          "AND typename.name = 'downloads/destinationFileURI'"
                          "AND tabname.anno_attribute_id = typename.id "
                          "AND tabmeta.anno_attribute_id = typemeta.id "
                          "AND tabname.place_id = tabmeta.place_id;")
    for row in downloads:
        down_filename = row[0]
        down_meta = json.loads(row[1])
        art_desc = "Downloaded file " + down_filename + " of size " + str(down_meta["fileSize"]) + "B"
        artifacts.add((down_meta["endTime"]/1000, "mozilla downloads", art_desc))
    #TODO: Favicons, from where user came to site, bookmarks
    #Parsing formhistory
    database = sqlite3.connect(os.path.join(moz_home, "formhistory.sqlite"))
    c = database.cursor()
    formhistory = c.execute("SELECT fieldname, value, timesused, firstUsed, lastUsed FROM moz_formhistory")
    for row in formhistory:

        artifacts.add((row[4]/1000000, "mozilla formhistory", "User input into field " + row[0] + " value " + row[1] +
                       " from " + str(row[3]) + " to " + str(row[4]) + " " + str(row[2]) + " times "))
    #TODO: Deleted formhistory
    #TODO: Sessionstore? necessary?
    #TODO: format of cookies
    #TODO: favicons
    passwords = json.load(open(os.path.join(moz_home, "logins.json")))
    for row in passwords['logins']:
        art_desc = "User last used password on " + str(row['hostname']) + " created on " + str(row['timeCreated']) \
                   + " last changed on " + str(row['timeLastUsed'])
        artifacts.add((row['timeLastUsed']/100, "mozilla password", art_desc))
    #TODO: decrypt passwords
    return artifacts
