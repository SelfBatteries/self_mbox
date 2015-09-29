#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
# import html2text
import mailbox
from email.parser import Parser

from grab_self_mail_list import ShelveDB


# Variables ===================================================================
# Functions ===================================================================
def to_mbox(messages, filename="self_archive.mbox"):
    mbox = mailbox.mbox(filename)

    parser = Parser()
    for msg in messages.values():
        parsed = parser.parsestr(msg.raw_email.encode("utf-8"))
        mbox.add(parsed)


# Classes =====================================================================
class Message(object):
    def __init__(self, uid, author_name, subject, raw_email, timestamp):
        self.uid = uid
        self.author_name = author_name
        self.timestamp = timestamp
        self.subject = subject
        self.raw_email = raw_email

        self._topic_id = None
        self._prev_in_topic = None
        self._next_in_topic = None

    @staticmethod
    def from_json(j_msg):
        uid = j_msg["ygData"]["msgId"]

        msg = Message(
            uid=uid,
            author_name=j_msg["ygData"]["authorName"],
            subject=j_msg["ygData"]["subject"],
            raw_email=j_msg["ygData"]["rawEmail"],
            timestamp=int(j_msg["ygData"].get("postDate", uid)),
        )

        msg._topic_id = j_msg["ygData"]["topicId"]
        msg._prev_in_topic = j_msg["ygData"]["prevInTopic"]
        msg._next_in_topic = j_msg["ygData"]["nextInTopic"]

        if msg._topic_id == 0:
            msg._topic_id = None
        if msg._prev_in_topic == 0:
            msg._prev_in_topic = None
        if msg._next_in_topic == 0:
            msg._next_in_topic = None

        return msg

    def __repr__(self):
        return "Message(uid=%d, subject=%s)" % (self.uid, repr(self.subject))


def Topic(self):
    def __init__(self, title, post, replies):
        self.title = title
        self.post = post
        self.replies = replies


# Main program ================================================================
if __name__ == '__main__':
    db = ShelveDB()

    messages = {
        uid: Message.from_json(msg)
        for uid, msg in db.msgs.iteritems()
    }

    print messages[max(messages.keys())]#, messages[-1].timestamp
