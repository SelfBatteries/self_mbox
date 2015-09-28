#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json
import shelve
from urllib2 import HTTPError
from contextlib import contextmanager

import httpkie


# Variables ===================================================================
DOWN = httpkie.Downloader()
URL = (
    "https://groups.yahoo.com/api/v1/groups/self-interest/messages/%d/"
    "raw?chrome=raw&tz=America%%2FLos_Angeles"
)


# Functions & classes =========================================================
@contextmanager
def shelver(fn):
    """
    In python 2.7, there is no context manager for shelve. So this is it.
    """
    db = shelve.open(fn)
    yield db
    db.close()


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


class ShelveDB(object):
    def __init__(self, fn="msg_db.shelve"):
        self.fn = fn
        self.key = "msgs"
        self.missing_key = "missing"

        with shelver("msg_db.shelve") as db:
            self.msgs = db.get(self.key, {})
            self.missing = db.get(self.missing_key, set())

    def __setitem__(self, key, item): 
        self.msgs[key] = item

    def __delitem__(self, key): 
        del self.msgs[key]

    def __getitem__(self, key): 
        return self.msgs[key]

    def __contains__(self, item):
        return (item in self.msgs) or (item in self.missing)

    def has_key(self, k):
        return self.msgs.has_key(k)

    def add_missing(self, uid):
        self.missing.update([uid])

    def save(self):
        with shelver("msg_db.shelve") as db:
            db[self.key] = self.msgs
            db[self.missing_key] = self.missing


# Main program ================================================================
if __name__ == '__main__':
    db = ShelveDB()

    missing_cnt = 0
    for uid, message in all_messages(db):
        if missing_cnt >= 5:  # 5 missing messages in a row means end
            break

        if not message:
            missing_cnt += 1
            # db.add_missing(uid)  # this will ban last messages once they appear
            continue

        missing_cnt = 0  # row of missing messages broken
        uid = message["ygData"]["msgId"]
        db[uid] = message

        print uid, message["ygData"]["subject"]

        if uid % 10:
            db.save()

    db.save()
