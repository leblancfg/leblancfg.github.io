#!/usr/bin/python
# -*- coding: utf-8 -*-P

AUTHOR = "François Leblanc"
SITEURL = "http://leblancfg.com"
SITENAME = "François Leblanc"
LOCALE = "en_US.utf8"
TIMEZONE = "America/Toronto"

DISPLAY_PAGES_ON_MENU = True
WITH_PAGINATION = True
DEFAULT_PAGINATION = 7
FEED_ALL_ATOM = "feeds/all.atom.xml"
CATEGORY_FEED_ATOM = "feeds/%s.atom.xml"
RELATIVE_URLS = False
DELETE_OUTPUT_DIRECTORY = True

TWITTER_USERNAME = "leblancfg1"
GITHUB_URL = "https://github.com/leblancfg"
DISQUS_SITENAME = "leblancfg"

SOCIAL = (
    ("linkedin", "https://www.linkedin.com/in/fran%C3%A7ois-leblanc-07294b106/"),
    ("github", "https://github.com/leblancfg"),
    ("mastodon", "https://fosstodon.org/@leblancfg"),
    ("rss", "https://leblancfg.com/feeds/all.atom.xml"),
)

STATIC_PATHS = ["images", "extra/CNAME"]
EXTRA_PATH_METADATA = {"extra/CNAME": {"path": "CNAME"}}

MARKUP = ("md", "ipynb")

PLUGIN_PATHS = ["./plugins"]
PLUGINS = ["ipynb.markup"]
