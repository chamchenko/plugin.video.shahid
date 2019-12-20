#   Copyright (C) 2019 CHAMCHENKO
#
#
# This file is part of SHAHID.
#
# SHAHID is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SHAHID is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SHAHID.  If not, see <http://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-

import sys, time, datetime, re, traceback, ast, re
import urlparse, urllib, urllib2, socket, json, HTMLParser
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from tools import *
from live import getLive
from tvshows import getShows, getSeasons, getEpisodes, getCategories
from create_item import addDir
from vars import *
from web_browser import *


socket.setdefaulttimeout(TIMEOUT)
class SHAHID(object):
    def __init__(self):
        log('__init__')

    def buildMenu(self, items):
        for item in items: addDir(*item)
    def browseLive(self):
        getLive()
    def browseCategorieShows(self,url):
        getCategories(url)
    def browseShows(self,categoryID):
        getShows(categoryID)
    def browseSeasons(self,showId):
        getSeasons(showId)
    def browseEpisodes(self,playListId):
        getEpisodes(playListId)


    def playVideo(self, name, streamId, liz=None):
        log('playVideo')
        playoutURL  = PLAYOUT_URL%streamId
        headers     = {'User-Agent': USER_AGENT}
        jsonstr     = json.loads(cacheURL(playoutURL, headers))
        drm         = jsonstr['playout']['drm']
        if drm:
            playbackURL     = jsonstr['playout']['url']
            requrl          = DRM_URL%(urllib.quote('{"assetId":%s}'%streamId))
            headers         = {'User-Agent': USER_AGENT, 'BROWSER_NAME': 'CHROME', 'SHAHID_OS': 'LINUX', 'BROWSER_VERSION': '79.0'}
            request         = urllib2.Request(requrl, headers=headers)
            Response        = urllib2.urlopen(request, timeout = TIMEOUT).read().decode('utf-8').strip()
            licenceurl      = json.loads(Response)['signature']
            URL_LICENCE_KEY = '%s|authority=shahiddotnet.keydelivery.westeurope.media.azure.net&origin=https://shahid.mbc.net&User-Agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36&referer=https://shahid.mbc.net|R{SSM}|'%licenceurl
            liz             = xbmcgui.ListItem(name, path=playbackURL)
            liz.setProperty('inputstreamaddon','inputstream.adaptive')
            liz.setProperty('inputstream.adaptive.manifest_type', 'ism')
            liz.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
            liz.setProperty('inputstream.adaptive.license_key', URL_LICENCE_KEY)
        else:
            playbackURL = jsonstr['playout']['url'].replace('filter=NO_HD,','')
            liz         = xbmcgui.ListItem(name, path=playbackURL)
            liz.setProperty('inputstreamaddon','inputstream.adaptive')
            liz.setProperty('inputstream.adaptive.manifest_type',  'hls')
        bitrate     = getBitrate(cacheURL(playbackURL,headers),drm)
        if bitrate:
            xbmcaddon.Addon(id='inputstream.adaptive').setSetting(id='MINBANDWIDTH', value=bitrate)
            xbmcaddon.Addon(id='inputstream.adaptive').setSetting(id='MAXBANDWIDTH', value=str(int(bitrate)+100000))
            xbmcaddon.Addon(id='inputstream.adaptive').setSetting(id='STREAMSELECTION', value="0")
        else: xbmcaddon.Addon(id='inputstream.adaptive').setSetting(id='STREAMSELECTION', value="1")
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=liz)
        xbmcaddon.Addon(id='inputstream.adaptive').setSetting(id='MINBANDWIDTH', value="0")
        xbmcaddon.Addon(id='inputstream.adaptive').setSetting(id='MAXBANDWIDTH', value="0")

params=getParams()
try: url=urllib.unquote_plus(params["url"])
except: url=None
try: name=urllib.unquote_plus(params["name"])
except: name=None
try: mode=int(params["mode"])
except: mode=None
log("Mode: "+str(mode))
log("URL : "+str(url))
log("Name: "+str(name))


if  mode==None: SHAHID().buildMenu(MAIN_MENU)
elif mode == 1: SHAHID().browseLive()
elif mode == 2: SHAHID().browseCategorieShows(url)
elif mode == 3: SHAHID().browseShows(url)
elif mode == 4: SHAHID().browseSeasons(url)
elif mode == 5: SHAHID().browseEpisodes(url)
elif mode == 9: SHAHID().playVideo(name, url)


xbmcplugin.addSortMethod(int(sys.argv[1]) , xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(int(sys.argv[1]) , xbmcplugin.SORT_METHOD_EPISODE)
xbmcplugin.addSortMethod(int(sys.argv[1]) , xbmcplugin.SORT_METHOD_DATE)
xbmcplugin.addSortMethod(int(sys.argv[1]) , xbmcplugin.SORT_METHOD_NONE)
xbmcplugin.addSortMethod(int(sys.argv[1]) , xbmcplugin.SORT_METHOD_LABEL)
xbmcplugin.addSortMethod(int(sys.argv[1]) , xbmcplugin.SORT_METHOD_TITLE)
xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
