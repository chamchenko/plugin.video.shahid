# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid


import xbmc

from codequick.utils import urljoin_partial
from codequick import Script



XBMC_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split('-')[0].split('.')[0])
INPUTSTREAM_PROP = 'inputstream' if XBMC_VERSION >= 19 else 'inputstreamaddon'

#Add-on related
ADDON_ID = 'plugin.video.shahid'
ADDON_NAME =Script.get_info('name')
SETTINGS_LOC = Script.get_info('profile')
ADDON_PATH = Script.get_info('path')
ADDON_VERSION = Script.get_info('version')
ICON = Script.get_info('icon')
FANART = Script.get_info('fanart')
Hide_Clips = Script.setting.get_boolean('Hide_Clips')
HIDE_PREMIUM = Script.setting.get_boolean('Hide_Premium')
MODE_KIDS = Script.setting.get_boolean('Mode_Kids')
QUALITY = Script.setting.get_string('Quality').replace('p','')
EMAIL = Script.setting.get_string('username')
PASSWORD = Script.setting.get_string('password')
Movie_Category_Mode = Script.setting.get_string('Movie_Category_Mode')
Show_Category_Mode = Script.setting.get_string('Show_Category_Mode')
language = xbmc.getLanguage(xbmc.ISO_639_1)
if language != 'ar' and language != 'en':
    language = 'en'

#Web related
USER_AGENT = 'Shahid/3660 CFNetwork/1220.1 Darwin/20.3.0'
SHAHID_AGENT = 'Shahid/6.8.3.3660 CFNetwork/1220.1 Darwin/20.3.0 (iPhone/6s iOS/14.4) Safari/604.1'


PROXY_BASE_URL = "https://api2.shahid.net/proxy"
URL_CONSTRUCTOR = urljoin_partial(PROXY_BASE_URL + "/v2/")
AVATAR_URL = URL_CONSTRUCTOR('userprofile/profiles/avatar/')
MOVIE_API = URL_CONSTRUCTOR('product/id')
DRM_URL = URL_CONSTRUCTOR('playout/new/drm')
LOGIN_TOKEN_URL = URL_CONSTRUCTOR('session/web')
SESSION_TOKEN_URL = URL_CONSTRUCTOR('session/ios')

URL_CONSTRUCTOR_V2_1 = urljoin_partial(PROXY_BASE_URL + "/v2.1/")
LOGIN_URL = URL_CONSTRUCTOR_V2_1('usersservice/validateLogin')
PLAYOUT_URL = URL_CONSTRUCTOR_V2_1('playout/new/url/%s')
PROFILES_URL = URL_CONSTRUCTOR_V2_1('userprofile/profiles/me')
SEARCH_URL = URL_CONSTRUCTOR_V2_1('search/grid')
ADD_TO_LIST_URL = URL_CONSTRUCTOR_V2_1('personalization/add/')
MY_LIST_URL = URL_CONSTRUCTOR_V2_1('personalization/grid')
TVSOWS_API = URL_CONSTRUCTOR_V2_1('product/filter')
PLAYABLE_API = URL_CONSTRUCTOR_V2_1('playableAsset')
PLAYLIST_API = URL_CONSTRUCTOR_V2_1('product/playlist')
URL_LIVE = URL_CONSTRUCTOR_V2_1('product/filter')
