#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from pathlib import Path

from pelican_jupyter import markup as nb_markup

AUTHOR = "François Leblanc"
SITEURL = "http://localhost:8000"
SITENAME = "leblancfg.com"
SITETITLE = AUTHOR
SITESUBTITLE = "Data Science, Geospatial Python, Space Stuff"
SITEDESCRIPTION = "%s's Thoughts and Writings" % AUTHOR
SITELOGO = "https://avatars0.githubusercontent.com/u/15659410?s=400&u=e3bc92486becb34e77028eef0f4dfc302540fcb3&v=4"
FAVICON = "/img/icons/favicon.ico"
BROWSER_COLOR = "#330033"
PYGMENTS_STYLE = "monokai"

ROBOTS = "index, follow"

HOME = str(Path.home())
THEME = f"pelican-themes/Flex"
PATH = "content"
TIMEZONE = "America/Montreal"

I18N_TEMPLATES_LANG = "en"
DEFAULT_LANG = "en"
OG_LOCALE = "en_US"
LOCALE = "en_US"

DATE_FORMATS = {"en": "%B %d, %Y"}

FEED_ALL_ATOM = "feeds/all.atom.xml"
CATEGORY_FEED_ATOM = "feeds/{slug}.atom.xml"
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

USE_FOLDER_AS_CATEGORY = False
MAIN_MENU = True
HOME_HIDE_TAGS = True

LINKS = (("Résumé", "https://leblancfg.resumeed.com/"),)

SOCIAL = (
    ("linkedin", "https://www.linkedin.com/in/fran%C3%A7ois-leblanc-07294b106/"),
    ("github", "https://github.com/leblancfg"),
    ("mastodon", "https://fosstodon.org/@leblancfg"),
    ("rss", "https://leblancfg.com/feeds/all.atom.xml"),
)

MENUITEMS = (
    ("Archives", "/archives.html"),
    ("Categories", "/categories.html"),
    ("Tags", "/tags.html"),
)

CC_LICENSE = {
    "name": "Creative Commons Attribution-ShareAlike",
    "version": "4.0",
    "slug": "by-sa",
}

COPYRIGHT_YEAR = 2019

DEFAULT_PAGINATION = 10

MARKUP = ("md", "ipynb")

PLUGINS = [nb_markup]

IGNORE_FILES = [".ipynb_checkpoints"]

# Define Links
STATIC_PATHS = ["img", "extra/CNAME", "pages/leblancfg_CV.pdf"]
EXTRA_PATH_METADATA = {
    "extra/CNAME": {"path": "CNAME"},
    "pages/leblancfgCV.pdf": {"path": "pages/leblancfg_CV.pdf"},
}

# Analytics
GOOGLE_ANALYTICS = "UA-120300361-1"
