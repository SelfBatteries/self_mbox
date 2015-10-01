#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
import mailbox
from email.parser import Parser
from dateutil.parser import parse as date_parse

# import html2text
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
        self.parsed = Parser().parsestr(raw_email.encode("utf-8"))

        self._topic_id = None
        self._prev_in_topic = None
        self._next_in_topic = None

        self._postprocess()

    def _postprocess(self):
        self._self_parse_time()

    def _self_parse_time(self):
        def parse_date(s):
            try:
                return date_parse(s)
            except ValueError:
                return None

        # try to parse dates in `Received` headers, which may look like this:
        # (qmail 43149 invoked from network); 5 Sep 2011 13:53:18 -0000 (...)
        received = (
            parse_date(val.split(";")[-1].strip().split("(")[0])
            for key, val in self.parsed.items()
            if key == "Received"
        )

        def datetime_to_timestamp(dt):
            """
            Sometimes the year is out of range, so thats why the try..
            """
            try:
                return time.mktime(dt.timetuple())
            except ValueError:
                return None

        received_timestamps = [
            datetime_to_timestamp(dt)
            for dt in received
            if dt  # to filter None from previous expression
        ]

        timestamps = received_timestamps
        if "Date" in self.parsed:
            date = parse_date(self.parsed["Date"])

            if date:
                timestamps.append(datetime_to_timestamp(date))

        if self.timestamp > 0:
            timestamps.append(self.timestamp)

        if not timestamps:
            raise ValueError("Couldn't find any reasonable timestamp!")

        timestamp = min(
            timestamp
            for timestamp in timestamps
            if timestamp and timestamp > 883612800  # skip < 1.1.1998
        )

        self.timestamp = int(timestamp)

    @staticmethod
    def from_json(j_msg):
        uid = j_msg["ygData"]["msgId"]

        msg = Message(
            uid=uid,
            author_name=j_msg["ygData"]["authorName"],
            subject=j_msg["ygData"]["subject"],
            raw_email=j_msg["ygData"]["rawEmail"],
            timestamp=int(j_msg["ygData"].get("postDate", 0)),
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

    last = messages[max(messages.keys())]
    print last
    print last.timestamp

    # to_mbox(messages, "self")
    print last.parsed["Date"]