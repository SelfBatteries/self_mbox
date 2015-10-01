#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json
import shelve
from urllib2 import HTTPError

import httpkie

from shelvedb import ShelveDB

# Variables ===================================================================
DOWN = httpkie.Downloader()
URL = (
    "https://groups.yahoo.com/api/v1/groups/self-interest/messages/%d/"
    "raw?chrome=raw&tz=America%%2FLos_Angeles"
)


# Functions & classes =========================================================
def get_message(uid):
    try:
        data = DOWN.download(URL % uid)
    except HTTPError as e:
        return None

    return json.loads(data)


def all_messages(db):
    for i in xrange(1000000):
        uid = i + 1
        if uid not in db:
            yield uid, get_message(uid)


# Main program ================================================================
if __name__ == '__main__':
    db = ShelveDB()

    missing_cnt = 0
    last_missing_uid = 0
    for uid, message in all_messages(db):
        # 5 missing messages in a row means end
        if missing_cnt >= 5:
            break
        if uid - last_missing_uid > 5:  # make sure that they are in row
            missing_cnt = 0

        if not message:
            missing_cnt += 1
            last_missing_uid = uid
            continue

        missing_cnt = 0  # row of missing messages broken
        uid = message["ygData"]["msgId"]
        db[uid] = message

        print uid, message["ygData"]["subject"]

        if uid % 10:
            db.save()

    db.save()
