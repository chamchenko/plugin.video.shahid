# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid

from __future__ import unicode_literals

import json
import urlquick
import xbmcgui
import xbmcplugin
from .tools import urlencode
from .tools import formatimg
from .categories import *
from .vars import *
from .playback_resolver import play_video
from codequick import Route, Listitem, Resolver
from codequick.utils import ensure_native_str

Search = 30104

@Route.register
def CATEGORIES_M(plugin, TYPE='SERIES', **kwargs):
    plugin.log('CATEGORIES TYPE: %s' % TYPE, lvl=plugin.DEBUG)
    if CATEGORY_MODE == "Dialect":
        genre_list = DIALECTS_MOVIES
    elif CATEGORY_MODE == "Genre":
        genre_list = GENRES_MOVIES

    for genre in genre_list:
        title = genre['title']
        genreId = genre['id']
        item = Listitem()
        item.label = title
        item.info['mediatype'] = "episode"
        item.set_callback(BROWSE_MOVIES, genreId=genreId)
        plugin.log('Adding: %s' % title, lvl=plugin.DEBUG)
        yield item


@Route.register(autosort=False, content_type="movies")
def BROWSE_MOVIES(plugin, genreId, page=0, **kwargs):
    plugin.log('BROWSE_MOVIES genreId: %s' % genreId, lvl=plugin.DEBUG)
    productType = 'MOVIE'
    plugin.log('page: %s' % page, lvl=plugin.DEBUG)
    filters = {
                "pageNumber": page,
                "pageSize": 30,
                "productType": productType,
                "sorts": [{"order": "DESC", "type": "SORTDATE"}]
              }
    if genreId:
        if CATEGORY_MODE == "Dialect":
            filters.update({"dialect": genreId})
        elif CATEGORY_MODE == "Genre":
            filters.update({"genres": [genreId]})
    filters = json.dumps(filters, separators=(',', ':'))
    params = urlencode({'filter': filters})
    headers = {'User-Agent': USER_AGENT}
    plugin.log('Fetching url: %s' % TVSOWS_API, lvl=plugin.DEBUG)
    plugin.log('Fetching params: %s' % params, lvl=plugin.DEBUG)
    Response = urlquick.get(TVSOWS_API, params=params, headers=headers).json()
    items = Response['productList']
    hasMore = items['hasMore']
    for item in items['products']:
        title = item['title']
        plot = item['description']
        if item['pricingPlans'][0]['availability']:
            movieId = item['id']
            if item['pricingPlans'][0]['availability']['plus']:
                if HIDE_PREMIUM:
                    continue
                title += ' |Premium|'
                plot = '[Premium]\n' + plot
        # if not available assume it's comming soon and return the trailer
        else:
            title += ' |Trailer|'
            movieId = item['trailerItem']['id']
        liz = Listitem()
        aired = str(item['createdDate'].split('T')[0])
        liz.label = ensure_native_str(title)
        liz.info['mediatype'] = "movie"
        liz.art["poster"] = formatimg(item['image']['posterImage'], 'poster')
        liz.art["fanart"] = formatimg(item['image']['thumbnailImage'], 'fanart')
        liz.info.date(aired, "%Y-%m-%d")
        liz.info['plot'] = ensure_native_str(plot)
        liz.set_callback(play_video, url=movieId)
        plugin.log('Adding: %s' % title, lvl=plugin.DEBUG)
        yield liz

    if hasMore:
        page = int(page)+1
        yield Listitem.next_page(
                                    genreId=genreId,
                                    page=str(page)
                                )
        yield False
