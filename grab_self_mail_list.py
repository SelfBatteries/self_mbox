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
        if e.code == 404:
            return None

        raise StopIteration()

    return json.loads(data)


def all_messages(db):
    for i in xrange(100000000):
        if i + 1 not in db:
            yield get_message(i + 1)


class ShelveDB(object):
    def __init__(self, fn="msg_db.shelve"):
        self.fn = fn
        self.key = "msgs"

        with shelver("msg_db.shelve") as db:
            self.msgs = db.get(self.key, {})

    def __setitem__(self, key, item): 
        self.msgs[key] = item

    def __delitem__(self, key): 
        del self.msgs[key]

    def __getitem__(self, key): 
        return self.msgs[key]

    def has_key(self, k):
        return self.msgs.has_key(k)

    def __contains__(self, item):
        return item in self.msgs

    def save(self):
        with shelver("msg_db.shelve") as db:
            db[self.key] = self.msgs


# Main program ================================================================
if __name__ == '__main__':
    db = ShelveDB()

    for message in all_messages(db):
        if not message:
            continue

        uid = message["ygData"]["msgId"]
        db[uid] = message

        print uid, message["ygData"]["subject"]

        if uid % 10:
            db.save()

    db.save()
