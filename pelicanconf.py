#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = 'François Leblanc'
SITEURL = 'http://localhost:8000'
SITENAME = "leblancfg.com"
SITETITLE = AUTHOR
SITESUBTITLE = 'Data Science, Geospatial Python, Space Stuff'
SITEDESCRIPTION = '%s\'s Thoughts and Writings' % AUTHOR
SITELOGO = 'https://avatars0.githubusercontent.com/u/15659410?s=400&u=e3bc92486becb34e77028eef0f4dfc302540fcb3&v=4'
FAVICON = '/img/icons/favicon.ico'
BROWSER_COLOR = '#330033'
# PYGMENTS_STYLE = 'monokai'

ROBOTS = 'index, follow'

THEME = 'Flex'
PATH = 'content'
TIMEZONE = 'America/Montreal'

I18N_TEMPLATES_LANG = 'en'
DEFAULT_LANG = 'en'
OG_LOCALE = 'en_US'
LOCALE = 'en_US'

DATE_FORMATS = {
    'en': '%B %d, %Y',
}

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

USE_FOLDER_AS_CATEGORY = False
MAIN_MENU = True
HOME_HIDE_TAGS = True

LINKS = (('Kaggle', 'https://kaggle.com/leblancfg'),
        ('Résumé', 'https://leblancfg.com/pdf/leblancfg_CV.pdf'),)

SOCIAL = (('linkedin', 'https://www.linkedin.com/in/fran%C3%A7ois-leblanc-07294b106/'),
          ('github', 'https://github.com/leblancfg'),
          ('twitter', 'https://twitter.com/leblancfg1'),
          ('rss', 'https://leblancfg.com/feeds/all.atom.xml'))

MENUITEMS = (('Archives', '/archives.html'),
             ('Categories', '/categories.html'),
             ('Tags', '/tags.html'),)

CC_LICENSE = {
    'name': 'Creative Commons Attribution-ShareAlike',
    'version': '4.0',
    'slug': 'by-sa'
}

COPYRIGHT_YEAR = 2018

DEFAULT_PAGINATION = 10

MARKUP = ('md', 'ipynb')

PLUGIN_PATHS = ['./plugins']
PLUGINS = ['ipynb.markup']

# Define Links
STATIC_PATHS = ['img', 'extra/CNAME']
EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'}, }

# Analytics
GOOGLE_ANALYTICS = 'UA-120300361-1'

# Adsense
# AD_CODE = '3662443451'
# GOOGLE_ADSENSE = {
#     'ca_id': 'ca-pub-9414058741554736',    # Your AdSense ID
#     'page_level_ads': True,          # Allow Page Level Ads (mobile)
#     'ads': {
#         'aside': AD_CODE,          # Side bar banner (all pages)
#         'main_menu': AD_CODE,      # Banner before main menu (all pages)
#         'index_top': AD_CODE,      # Banner after main menu (index only)
#         'index_bottom': AD_CODE,   # Banner before footer (index only)
#         'article_top': AD_CODE,    # Banner after article title (article only)
#         'article_bottom': AD_CODE, # Banner after article content (article only)
#     }
# }
