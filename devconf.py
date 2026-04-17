#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from pathlib import Path

exec((Path(__file__).with_name("pelicanconf.py")).read_text(), globals())

SITEURL = ""
RELATIVE_URLS = True

# Avoid generating feed links that assume a fixed site URL during local dev.
FEED_ALL_ATOM = None
FEED_ALL_RSS = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
