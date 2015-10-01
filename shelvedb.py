#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import shelve
from contextlib import contextmanager


# Functions & classes =========================================================
@contextmanager
def shelver(fn):
    """
    In python 2.7, there is no context manager for shelve. So this is it.
    """
    db = shelve.open(fn)
    yield db
    db.close()


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
        return (item in self.msgs)# or (item in self.missing)

    def has_key(self, k):
        return self.msgs.has_key(k)

    def add_missing(self, uid):
        self.missing.update([uid])

    def save(self):
        with shelver("msg_db.shelve") as db:
            db[self.key] = self.msgs
            db[self.missing_key] = set()  #self.missing
