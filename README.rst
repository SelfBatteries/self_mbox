Self mbox
=========

This repository contains archive of the `Self mail conference`_ (http://selflanguage.org) from 26.7.1990 to 2.6.2016 in one `mbox file`_, with 4336 serialized email messages. This file may be imported into your favorite mail client (i used Thunderbird), so you may read the whole discussion from the beginning to the end.

Mbox file contains both `Old Self mail list`_ and new one hosted at Yahoo.

.. _Self mail conference: https://groups.yahoo.com/neo/groups/self-interest/info
.. _mbox file: https://en.wikipedia.org/wiki/Mbox
.. _Old Self mail list: http://merlintec.com/old-self-interest/threads.html

FAQ
===

Download?
---------

``self_full.mbox.lzma`` is what you are looking for.

Attachments?
------------
Sorry, no attachments from the year ~1998, when they began to use 3rd party services for the conference, which stripped the attachments and put them to some private group webspace, which is mostly lost today.

Why?
----
Self documentation sux, because it's incomplete. There is handbook and tutorial, which may show you the basics of the language, there are some papers, which may show you some interesting concepts, but I had trouble to understand some of the practical concepts and decisions. Self conference is excellent source of informations, but Yahoo interface is not usable at all (you don't really want to read 4000+ emails with that).

I found useful to import the files to email client and then delete all `processed` messages. This way, I could take my time, and read the conference as long as I needed without worry to keep track of what I did read and what not.

Thunderbird?
------------

Just download the file ``self_full.mbox.lzma``, unpack it and put it to ``~/.thunderbird/46dw0hkr.default/Mail/Local Folders`` (where ``46dw0hkr.default`` is name of your profile). It will show up as new folder in local account.

Scripts
=======

There is two python scripts, which may be used to download and then serialize the current yahoo mail list:

grab_self_mail_list.py
----------------------

This script will download all messages from Self mail conference and store them in Shelve (python serialization format) file named ``msg_db.shelve``. Script uses this file as a cache, so it doesn't have to download all messages next time you run it.

serializer.py
-------------

Serializer may be used to convert Shelve file to mbox format. There is junk in the emails, so it does some cleanup and also repairs ``Date`` headers.

raw files
=========

There are other useful files other than the main mbox archive;

msg_db.shelve.lzma
------------------

State of the Yahoo conference to this day (2.6.2016). You may want to unpack it, put it to main directory and run ``grab_self_mail_list.py`` to download only new files.

old_self.raw.tar.lzma
---------------------

HTML copy of Old Self maillist from 1990 to 1998 which may be found at http://merlintec.com/old-self-interest/threads.html.

old_self.tar.lzma
-----------------

Old Self maillist converted by mhn2mbox_ to mbox format.

.. _mhn2mbox: https://www.mhonarc.org/MHonArc/contrib/mhn2mbox.pl

self_alone.lzma
---------------

Mbox file with complete Yahoo archive, without Self mail list.

datasets
========

self-alts.mbox.lzma
-------------------

List of messages about alternative interpreters or languages inspired by Self.

self-interesting.mbox.lzma
--------------------------

List of messages I've found interesting.