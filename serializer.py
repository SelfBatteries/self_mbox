#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import time
import mailbox
import os.path
from email.parser import Parser
from email.utils import formatdate
from dateutil.parser import parse as date_parse

# import html2text
from grab_self_mail_list import ShelveDB


# Variables ===================================================================
# Classes =====================================================================
class Message(object):
    def __init__(self, uid, author_name, subject, raw_email, timestamp,
                 user_id):
        self.uid = uid
        self.user_id = user_id
        self.timestamp = timestamp

        # mail module in py2 requires utf-8
        self.subject = subject.encode("utf-8")
        self.raw_email = raw_email.encode("utf-8")
        self.author_name = author_name.encode("utf-8")

        # ugly, I know, but it only takes 1s for all the messages
        # http://bruno.im/2009/dec/18/decoding-emails-python/
        raw_email = raw_email.replace("&lt;", "<") \
                             .replace("&lt=\n;", "<=\n") \
                             .replace("&l=\nt;", "<=\n") \
                             .replace("&=\nlt;", "<=\n") \
                             .replace("&#39;", "'") \
                             .replace("&gt;", ">") \
                             .replace("&gt=\n;", ">=\n") \
                             .replace("&g=\nt;", ">=\n") \
                             .replace("&=\ngt;", ">=\n") \
                             .replace("&quot;", '"')
        self.email_msg = Parser().parsestr(raw_email.encode("utf-8"))

        self._topic_id = None
        self._prev_in_topic = None
        self._next_in_topic = None

        self._postprocess()

    def _parse_subject(self):
        si_sign = "[self-interest]"
        if si_sign in self.subject:
            self.subject = self.subject.replace(si_sign, "")

        self.subject = " ".join(self.subject.split())  # remove multiple spaces

    def _self_parse_time(self):
        def date_from_string(s):
            try:
                return date_parse(s)
            except ValueError:
                return None

        # try to parse dates in `Received` headers, which may look like this:
        # (qmail 43149 invoked from network); 5 Sep 2011 13:53:18 -0000 (...)
        received = (
            date_from_string(val.split(";")[-1].strip().split("(")[0])
            for key, val in self.email_msg.items()
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
        if "Date" in self.email_msg:
            date = date_from_string(self.email_msg["Date"])

            if date:
                timestamps.append(datetime_to_timestamp(date))

        if self.timestamp > 0:
            timestamps.append(self.timestamp)

        if not timestamps:
            raise ValueError("Couldn't find any reasonable timestamp!")

        timestamp = min(
            timestamp
            for timestamp in timestamps
            if timestamp and timestamp > 883612800  # skip < 1.1.1998 (first msg)
        )

        self.timestamp = int(timestamp)

    def _postprocess(self):
        self._self_parse_time()
        self._parse_subject()

        # mail objects look like dicts, but aren't - you cannot rewrite item,
        # you have to delete it first and then save it again
        del self.email_msg["To"]
        del self.email_msg["From"]
        del self.email_msg["Date"]
        del self.email_msg["Subject"]
        del self.email_msg["Reply-To"]
        del self.email_msg["Return-Path"]
        del self.email_msg["X-Original-From"]

        self.email_msg["From"] = "%s <%d>" % (self.author_name, self.user_id)
        self.email_msg["Date"] = formatdate(self.timestamp)
        self.email_msg["Subject"] = self.subject

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

    @staticmethod
    def to_mbox(messages, filename="self_archive.mbox"):
        # mailbox merges, we don't want that
        if os.path.exists(filename):
            os.unlink(filename)

        mbox = mailbox.mbox(filename)

        for msg in messages.values():
            mbox.add(msg.email_msg)

    def __repr__(self):
        return "Message(uid=%d, subject=%s)" % (self.uid, repr(self.subject))


# Main program ================================================================
if __name__ == '__main__':
    db = ShelveDB()

    messages = {
        uid: Message.from_json(msg)
        for uid, msg in db.msgs.iteritems()
    }

    Message.to_mbox(messages, "self")

    # for uid, msg in db.msgs.iteritems():
    #     print msg["ygData"].get("profile", None)