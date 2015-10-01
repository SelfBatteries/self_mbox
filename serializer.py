#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
import mailbox
from email.parser import Parser
from email.utils import formatdate
from dateutil.parser import parse as date_parse

# import html2text
from grab_self_mail_list import ShelveDB


# Variables ===================================================================
# Functions ===================================================================
def to_mbox(messages, filename="self_archive.mbox"):
    mbox = mailbox.mbox(filename)

    for msg in messages.values():
        mbox.add(msg.parsed)


# Classes =====================================================================
class Message(object):
    def __init__(self, uid, author_name, subject, raw_email, timestamp,
                 user_id):
        self.uid = uid
        self.timestamp = timestamp
        self.user_id = user_id

        # mail module in py2 requires utf-8
        self.author_name = author_name.encode("utf-8")
        self.subject = subject.encode("utf-8")
        self.raw_email = raw_email.encode("utf-8")

        # ugly, I know, but it only takes 1s for all the messages
        parsed = raw_email.replace("&lt;", "<")\
                          .replace("&lt=\n;", "<=\n")\
                          .replace("&l=\nt;", "<=\n")\
                          .replace("&=\nlt;", "<=\n")\
                          .replace("&#39;", "'")\
                          .replace("&gt;", ">")\
                          .replace("&gt=\n;", ">=\n")\
                          .replace("&g=\nt;", ">=\n")\
                          .replace("&=\ngt;", ">=\n")\
                          .replace("&quot;", '"')
        self.parsed = Parser().parsestr(parsed.encode("utf-8"))

        self._topic_id = None
        self._prev_in_topic = None
        self._next_in_topic = None

        self._postprocess()

    def _postprocess(self):
        self._self_parse_time()
        self._parse_subject()

        # mail objects look like dicts, but aren't - you cannot rewrite item,
        # you have to delete it first and then save it again
        del self.parsed["To"]
        del self.parsed["From"]
        del self.parsed["Date"]
        del self.parsed["Subject"]
        del self.parsed["Reply-To"]
        del self.parsed["Return-Path"]
        del self.parsed["X-Original-From"]

        self.parsed["From"] = "%s <%d>" % (self.author_name, self.user_id)
        self.parsed["Date"] = formatdate(self.timestamp)
        self.parsed["Subject"] = self.subject

    def _parse_subject(self):
        si_sign = "[self-interest]"
        if si_sign in self.subject:
            self.subject = self.subject.replace(si_sign, "")

        self.subject = " ".join(self.subject.split())  # remove multiple spaces

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
        yg_data = j_msg["ygData"]

        msg = Message(
            uid=yg_data["msgId"],
            author_name=yg_data["authorName"],
            subject=yg_data["subject"],
            raw_email=yg_data["rawEmail"],
            timestamp=int(yg_data.get("postDate", 0)),
            user_id=int(yg_data["userId"])
        )

        msg._topic_id = yg_data["topicId"]
        msg._prev_in_topic = yg_data["prevInTopic"]
        msg._next_in_topic = yg_data["nextInTopic"]

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

    to_mbox(messages, "self")

    # for uid, msg in db.msgs.iteritems():
    #     print msg["ygData"].get("profile", None)