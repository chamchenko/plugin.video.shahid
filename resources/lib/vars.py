# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid

from __future__ import unicode_literals

import xbmcaddon
from codequick.utils import urljoin_partial
from codequick.script import Settings
from xbmc import getInfoLabel


#Add-on related
ADDON_ID = 'plugin.video.shahid'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME = REAL_SETTINGS.getAddonInfo('name')
SETTINGS_LOC = REAL_SETTINGS.getAddonInfo('profile')
ADDON_PATH = REAL_SETTINGS.getAddonInfo('path')
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
ICON = REAL_SETTINGS.getAddonInfo('icon')
FANART = REAL_SETTINGS.getAddonInfo('fanart')
XBMC_VERSION = int(getInfoLabel("System.BuildVersion").split('-')[0].split('.')[0])
INPUTSTREAM_PROP = 'inputstream' if XBMC_VERSION >= 19 else 'inputstreamaddon'
DEBUG = Settings.get_string('Debugging') == 'true'
Hide_Clips = Settings.get_string('Hide_Clips') == 'true'
HIDE_PREMIUM = Settings.get_string('Hide_Premium') == 'true'
MODE_KIDS = Settings.get_string('Mode_Kids') == 'true'
QUALITY = Settings.get_string('Quality').replace('p','')
CATEGORY_MODE = Settings.get_string('Category_Mode')




#Web related
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
BASE_URL = "https://api2.shahid.net/proxy/v2/"
URL_CONSTRUCTOR = urljoin_partial(BASE_URL)
URL_LIVE = URL_CONSTRUCTOR('product/filter')
PLAYOUT_URL = URL_CONSTRUCTOR('playout/new/url/')
TVSOWS_API = URL_CONSTRUCTOR('product/filter')
MOVIE_API = URL_CONSTRUCTOR('product/id')
PLAYABLE_API = URL_CONSTRUCTOR('playableAsset')
PLAYLIST_API = URL_CONSTRUCTOR('product/playlist')
SEARCH_URL = URL_CONSTRUCTOR('search/grid')
DRM_URL = URL_CONSTRUCTOR('playout/new/drm')

SHOWS_PARAMS = {"page": 0,  "productType":"SHOW"}
