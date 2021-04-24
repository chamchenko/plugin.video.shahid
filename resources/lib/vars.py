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
USER_AGENT = 'Shahid/3660 CFNetwork/1220.1 Darwin/20.3.0'
SHAHID_AGENT = 'Shahid/6.8.3.3660 CFNetwork/1220.1 Darwin/20.3.0 (iPhone/6s iOS/14.4) Safari/604.1'

PROXY_BASE_URL = "https://api2.shahid.net/proxy"
BASE_URL_V2 = PROXY_BASE_URL + "/v2/"
BASE_URL_V2_1 = PROXY_BASE_URL + "/v2.1/"
URL_CONSTRUCTOR = urljoin_partial(BASE_URL_V2)
URL_CONSTRUCTOR_V2_1 = urljoin_partial(BASE_URL_V2_1)
URL_LIVE = URL_CONSTRUCTOR('product/filter')

TVSOWS_API = URL_CONSTRUCTOR('product/filter')
MOVIE_API = URL_CONSTRUCTOR('product/id')
PLAYABLE_API = URL_CONSTRUCTOR('playableAsset')
PLAYLIST_API = URL_CONSTRUCTOR('product/playlist')
SEARCH_URL = URL_CONSTRUCTOR('search/grid')
DRM_URL = URL_CONSTRUCTOR('playout/new/drm')
LOGIN_TOKEN_URL = URL_CONSTRUCTOR('session/web')
SESSION_TOKEN_URL = URL_CONSTRUCTOR('session/ios')


LOGIN_URL = URL_CONSTRUCTOR_V2_1('usersservice/validateLogin')
PLAYOUT_URL = URL_CONSTRUCTOR_V2_1('playout/new/url/')

SHOWS_PARAMS = {"page": 0,  "productType":"SHOW"}

