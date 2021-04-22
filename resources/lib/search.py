# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid

from __future__ import unicode_literals

import json
import urlquick
import xbmcgui
from .tools import urlencode
from .tools import formatimg
from .vars import *
from .playback_resolver import play_video
from codequick import Route, Listitem, Resolver

@Route.register(content_type="tvshows")
def SEARCH_CONTENT(plugin):
    plugin.log('SEARCH_CONTENT', lvl=plugin.DEBUG)
    headers = {'User-Agent': USER_AGENT}
    search_string = xbmcgui.Dialog().input('Search', type=xbmcgui.INPUT_ALPHANUM)
    page = 0
    hasMore = "True"
    while hasMore == "True":
        filters = json.dumps({
                            "name": search_string,
                            "pageNumber": page,
                            "pageSize": 30
                        }, separators=(',', ':'))
        params = urlencode({'request': filters})
        plugin.log('Fetching url: %s' % SEARCH_URL, lvl=plugin.DEBUG)
        plugin.log('Fetching params: %s' % params, lvl=plugin.DEBUG)
        Response = urlquick.get(SEARCH_URL, params=params, headers=headers).text
        items = json.loads(Response)['productList']
        for  item in items['products']:
                title = item['title']
                showId = item['id']
                plot = item['description']
                aired = str(item['createdDate'].split('T')[0])
                poster = formatimg(item['image']['posterImage'], 'thumbnail')
                fanart = formatimg(item['image']['thumbnailImage'], 'fanart')
                liz = Listitem()
                liz.label = title
                liz.art["poster"] = poster
                liz.art["fanart"] = fanart
                liz.info['mediatype'] = "tvshow"
                liz.info['TVShowTitle'] = "title"
                liz.info['plot'] = plot
                liz.info.date(aired, "%Y-%m-%d")
                liz.set_callback(BROWSE_SEASONS, url=showId)
                plugin.log('Adding: %s' % title, lvl=plugin.DEBUG)
                yield liz
        hasMore = str(items['hasMore'])
        page = page+1
