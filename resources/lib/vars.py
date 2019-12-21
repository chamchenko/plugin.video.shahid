# -*- coding: utf-8 -*- 
from __future__ import unicode_literals
import xbmcaddon, urllib, json
ADDON_ID        = 'plugin.video.shahid'
REAL_SETTINGS   = xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME      = REAL_SETTINGS.getAddonInfo('name')
SETTINGS_LOC    = REAL_SETTINGS.getAddonInfo('profile')
ADDON_PATH      = REAL_SETTINGS.getAddonInfo('path').decode('utf-8')
ADDON_VERSION   = REAL_SETTINGS.getAddonInfo('version')
ICON            = REAL_SETTINGS.getAddonInfo('icon')
FANART          = REAL_SETTINGS.getAddonInfo('fanart')
LANGUAGE        = REAL_SETTINGS.getLocalizedString
TIMEOUT         = 15
USER_AGENT      = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
DEBUG           = REAL_SETTINGS.getSetting('Enable_Debugging') == 'true'
Hide_Clips      = REAL_SETTINGS.getSetting('Hide_Clips') == 'true'
QUALITY         = REAL_SETTINGS.getSetting('Quality').replace('p','')
MAXBANDWIDTH    = xbmcaddon.Addon(id='inputstream.adaptive').getSetting('MAXBANDWIDTH')
MINBANDWIDTH    = xbmcaddon.Addon(id='inputstream.adaptive').getSetting('MINBANDWIDTH')
STREAMSELECTION = xbmcaddon.Addon(id='inputstream.adaptive').getSetting('STREAMSELECTION')
BASE_URL        = 'https://shahid.mbc.net'
API_Base        = 'https://api2.shahid.net/proxy/v2/'
LIVE_API        = API_Base + 'playout/new/url/%s'
LIVES_API       = API_Base + 'product/filter?filter=' + urllib.quote('{"pageNumber":0,"pageSize":25,"productType":"LIVESTREAM","productSubType":"LIVE_CHANNEL"}')
TVSOWS_API      = API_Base + 'product/filter?filter=%s'
PLAYLIST_API    = API_Base + 'product/playlist?request=%s'
PLAYABLE_API    = API_Base + 'playableAsset?request=%s'
PLAYOUT_URL     = API_Base + 'playout/new/url/%s'
SEARCH_URL      = API_Base + 'search/grid?request=%s'
DRM_URL         = API_Base + 'playout/new/drm?request=%s'
CAT_API_BURL    = 'https://shahid.mbc.net/vikimap/entries/'
CAT_TVSHOWS_P   = '58a43d63bad68a020f203da7,58a43e26bad68a020f203de4,58a43e4abad68a020f203e0d,59216106a0e84500062126a1,5921613da0e84500062126b5,59216174a0e84500062126c8,592161a1a0e84500062126db,59216207a0e84500062126f6,5bf17b5c1de1c4001a2a24e2,5d0f7d96a0e845001da34ee6,59216295a0e8450006212734,5a0958a5a0e845000cef0fde,592162d7a0e8450006212747,59ddd51623eec6000d7daf8e,59dcb141a0e845000cb0036e'
CAT_PROGRAMS_P  = '58a43e59bad68a020f203e21,58a43e35bad68a020f203df8,59215e4ca0e845000621261d,59215e00a0e8450006212609,58a43e17bad68a020f203dd3,59215e81a0e8450006212630,59215ec4a0e8450006212643,59215f51a0e845000621267c,59215f29a0e8450006212669'
CAT_MOVIES_P    = '8a43b4cbad68a020f203d52,58a43cf6bad68a020f203d7b,58a43d46bad68a020f203d91,59215821a0e845000621258d,59215780a0e8450006212575,59215874a0e845000621259e,592158c9a0e84500062125af,59215919a0e84500062125c2,59215983a0e84500062125d3,592159b9a0e84500062125e4,598829c7a0e845000d86b9c2,59882a45a0e845000d86b9cf,59882a8aa0e845000d86b9e0,5bb4ba6a23eec6001b4d438b,5dd678471de1c4001cfa989b'
VALUES          = "{'page':'%s'}"
MAIN_MENU       = [(LANGUAGE(40001), json.dumps({"url": "",                         "productType":"LIVESTREAM",  "productSubType": "LIVE_CHANNEL"   }), 1),
                   (LANGUAGE(40002), json.dumps({"url":CAT_API_BURL+CAT_TVSHOWS_P,  "productType":"SHOW",        "productSubType": "SERIES"         }), 2),
                   (LANGUAGE(40003), json.dumps({"url":CAT_API_BURL+CAT_PROGRAMS_P, "productType":"SHOW",        "productSubType": "PROGRAM"        }), 2),
                   (LANGUAGE(40007), json.dumps({"url":"", "productType":"SHOW",        "productSubType": ""        }), 2),
                   (LANGUAGE(40004) , "", 6)]

Kidslist = [
  {
    "genreId": 9649,
    "displaytext": "رسوم متحركة",
    "name":"Cartoon"
  },
  {
    "genreId": 9859,
    "displaytext": "أطفال",
    "name":"Kids"
  }
]



