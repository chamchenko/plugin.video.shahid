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
def CATEGORIES(plugin, TYPE='SERIES', KIDS=False, **kwargs):
    plugin.log('CATEGORIES TYPE: %s' % TYPE, lvl=plugin.DEBUG)
    if TYPE == "SERIES":
        if CATEGORY_MODE == "Dialect":
            if KIDS:
                genre_list = DIALECTS_TVSHOWS_KIDS
            else:
                genre_list = DIALECTS_TVSHOWS
        elif CATEGORY_MODE == "Genre":
            if KIDS:
                genre_list = GENRES_TVSHOWS_KIDS
            else:
                genre_list = GENRES_TVSHOWS
    elif TYPE == 'PROGRAM':
        if CATEGORY_MODE == "Dialect":
            if KIDS:
                genre_list = DIALECTS_PROGRAMS_KIDS
            else:
                genre_list = DIALECTS_PROGRAMS
        elif CATEGORY_MODE == "Genre":
            if KIDS:
                genre_list = GENRES_PROGRAMS_KIDS
            else:
                genre_list = GENRES_PROGRAMS
    for genre in genre_list:
        title = genre['title']
        genreId = genre['id']
        url = '%s,%s' % (genreId, TYPE)
        item = Listitem()
        item.label = title
        item.info['mediatype'] = "episode"
        item.set_callback(BROWSE_TVSHOWS, genreId=genreId, productSubType=TYPE)
        plugin.log('Adding: %s' % title, lvl=plugin.DEBUG)
        yield item


@Route.register(autosort=False, content_type="tvshows")
def BROWSE_TVSHOWS(plugin, genreId, productSubType, **kwargs):
    plugin.log('BROWSE_TVSHOWS genreId: %s' % genreId, lvl=plugin.DEBUG)
    plugin.log('BROWSE_TVSHOWS productSubType: %s' % productSubType, lvl=plugin.DEBUG)
    productType = 'SHOW'
    page = 0
    hasMore = "True"
    added = 0
    while hasMore == "True":
        plugin.log('page: %s' % page, lvl=plugin.DEBUG)
        filters = {
                    "pageNumber": page,
                    "pageSize": 30,
                    "productType": productType,
                    "productSubType": productSubType,
                    "sorts": [{"order": "DESC", "type": "SORTDATE"}]
                  }
        if genreId:
            if CATEGORY_MODE == "Dialect":
                filters.update({"dialect": genreId})
            elif CATEGORY_MODE == "Genre":
                filters.update({"genres": [genreId]})
        if not productSubType:
            del filters['productSubType']
        filters = json.dumps(filters, separators=(',', ':'))
        params = urlencode({'filter': filters})
        headers = {'User-Agent': USER_AGENT}
        plugin.log('Fetching url: %s' % TVSOWS_API, lvl=plugin.DEBUG)
        plugin.log('Fetching params: %s' % params, lvl=plugin.DEBUG)
        Response = urlquick.get(TVSOWS_API, params=params, headers=headers).json()
        items = Response['productList']
        hasMore = str(items['hasMore'])
        for item in items['products']:
            title = item['title']
            plot = item['description']
            if item['pricingPlans'][0]['availability']:
                if item['pricingPlans'][0]['availability']['plus']:
                    if HIDE_PREMIUM:
                        continue
                    title += ' |Premium|'
                    plot = '[Premium]\n' + plot 
            showId = item['id']
            liz = Listitem()
            liz.label = ensure_native_str(title)
            liz.info['mediatype'] = "tvshow"
            liz.art["poster"] = formatimg(item['image']['posterImage'], 'poster')
            liz.art["fanart"] = formatimg(item['image']['thumbnailImage'], 'fanart')
            aired = str(item['createdDate'].split('T')[0])
            liz.info.date(aired, "%Y-%m-%d")
            liz.info['plot'] = ensure_native_str(plot)
            liz.set_callback(BROWSE_SEASONS, url=showId)
            plugin.log('Adding: %s' % title, lvl=plugin.DEBUG)
            added = added + 1
            yield liz
        page = page+1
    if added == 0:
        plugin.notify(
                        'Notice',
                        'This Section is empty or contain premium content only',
                        display_time=5000,
                        sound=True
                     )
        yield False


@Route.register(autosort=False, content_type="seasons")
def BROWSE_SEASONS(plugin, url, **kwargs):
    plugin.log('BROWSE_TVSHOWS URL: %s' % url, lvl=plugin.DEBUG)
    headers = {'User-Agent': USER_AGENT}
    filters = json.dumps({"showId":url}, separators=(',', ':'))
    params = urlencode({'request': filters})
    plugin.log('Fetching url: %s' % PLAYABLE_API, lvl=plugin.DEBUG)
    plugin.log('Fetching params: %s' % params, lvl=plugin.DEBUG)
    json_parser = urlquick.get(PLAYABLE_API, params=params, headers=headers).json()
    TVShowTitle = json_parser['productModel']['show']['title']
    thumb = formatimg(
        json_parser['productModel']['show']['season']['image']['heroSliderImage'], 'thumbnail')
    if thumb == "":
        thumb = formatimg(
                    json_parser['productModel']['show']['season']['image']['thumbnailImage'], 'thumbnail')

    if thumb == "":
        thumb = formatimg(
                    json_parser['productModel']['show']['season']['image']['landscapeClean'], 'thumbnail')

    fanart = formatimg(
                    json_parser['productModel']['show']['season']['image']['landscapeClean'], 'thumbnail')
    items = json_parser['productModel']['show']['seasons']
    for item in items:
        seasonNumb = item['seasonNumber']
        title = plugin.localize(30105) + " %s" % seasonNumb
        seasonId = item['id']
        filters = json.dumps({"seasonId":seasonId}, separators=(',', ':'))
        params = urlencode({'request': filters})
        plugin.log('Fetching url: %s' % PLAYABLE_API, lvl=plugin.DEBUG)
        plugin.log('Fetching params: %s' % params, lvl=plugin.DEBUG)
        season_items = urlquick.get(PLAYABLE_API, params=params, headers=headers).json()
        thumb = formatimg(
                    season_items['productModel']['show']['season']['image']['heroSliderImage'], 'thumbnail')

        if thumb == "":
            thumb = formatimg(
                        season_items['productModel']['show']['season']['image']['thumbnailImage'], 'thumbnail')

        if thumb == "":
            thumb = formatimg(
                        season_items['productModel']['show']['season']['image']['landscapeClean'], 'thumbnail')
        fanart = formatimg(
                    season_items['productModel']['show']['season']['image']['landscapeClean'], 'thumbnail')
        playListId = season_items['productModel']['playlist']['id']
        aired = season_items['productModel']['createdDate'].split('T')[0]
        liz = Listitem()
        liz.label = ensure_native_str(title)
        liz.art["fanart"] = fanart
        liz.art["thumb"] = thumb
        liz.info.date(aired, "%Y-%m-%d")
        liz.info['mediatype'] = "tvshow"
        if json_parser['productModel']['show']['season']['pricingPlans'][0]['availability']['plus']:
            if HIDE_PREMIUM:
                continue
            title += ' [Premium]'
        liz.set_callback(BROWSE_EPISODES, url=playListId)
        plugin.log('Adding: %s' % title, lvl=plugin.DEBUG)
        yield liz
        if not Hide_Clips:
            for playlist in season_items['productModel']['show']['season']['playlists']:
                if (playlist['type'] == "CLIP" and playlist['count'] > 0):
                    playListId = playlist['id']
                    title = plugin.localize(30106)+" - "+ plugin.localize (30105)+" "+seasonNumb +' '+ playlist['title']
                    lizc = Listitem()
                    lizc.label = ensure_native_str(title)
                    lizc.info['mediatype'] = "tvshow"
                    lizc.TVShowTitle = TVShowTitle
                    lizc.season = seasonNumb
                    lizc.art["fanart"] = fanart
                    lizc.art["thumb"] = thumb
                    lizc.set_callback(BROWSE_EPISODES, url=playListId)
                    plugin.log('Adding: %s' % title, lvl=plugin.DEBUG)
                    yield lizc


@Route.register(autosort=False, content_type="episodes")
def BROWSE_EPISODES(plugin, url, **kwargs):
    plugin.add_sort_methods(xbmcplugin.SORT_METHOD_EPISODE)
    plugin.log('BROWSE_EPISODES playListId: %s' % url, lvl=plugin.DEBUG)
    headers = {'User-Agent': USER_AGENT}
    page = 0
    hasMore = "True"
    while hasMore == "True":
        filters = json.dumps({
                            "playListId": url,
                            "pageNumber": page,
                            "pageSize": 30,
                            "sorts": [{"order":"ASC","type":"SORTDATE"}]
                        }, separators=(',', ':'))
        params = urlencode({'request': filters})
        plugin.log('Fetching url: %s' % PLAYLIST_API, lvl=plugin.DEBUG)
        plugin.log('Fetching params: %s' % params, lvl=plugin.DEBUG)
        Response = urlquick.get(PLAYLIST_API, params=params, headers=headers).json()
        items = Response['productList']
        hasMore = str(items['hasMore'])
        showTitle = items['products'][0]['show']['title']
        plugin.log('showTitle: %s' % showTitle, lvl=plugin.DEBUG)
        for item in items['products']:
            streamId = str(item['id'])
            title = item['title']
            plot = title
            thumb = formatimg(item['image']['thumbnailImage'], 'thumbnail')
            episodeNumb = item['number']
            seasonNumb = item['show']['season']['seasonNumber']
            duration = item['duration']
            aired = str(item['createdDate'].split('T')[0])
            vtype = item['assetType']
            liz = Listitem()
            # if duration is superior to 15 minutes assume it's an episode not a clip
            if vtype == "EPISODE" or ( vtype != "EPISODE" and duration > 900):
                if vtype != "EPISODE":
                    showTitle += ' %s' % item['playlist']['title']
                liz.info['episode'] = episodeNumb
                liz.info['season'] = seasonNumb
                liz.info['mediatype'] = "episode"
                liz.label = ensure_native_str(showTitle)
                liz.TVShowTitle = showTitle
            else:
                liz.label = ensure_native_str(title) or ensure_native_str(item['bcmMediaID'])
                liz.info['mediatype'] = "video"
            liz.info['plot'] = ensure_native_str(plot)
            liz.art["thumb"] = thumb
            liz.info.date(aired, "%Y-%m-%d")
            liz.info.duration = duration
            liz.set_callback(play_video, url=streamId)
            plugin.log('Adding: %s S%sxE%s' % (showTitle,seasonNumb, episodeNumb), lvl=plugin.DEBUG)
            yield liz
        page = page+1


@Route.register(autosort=False, content_type="tvshows")
def SEARCH_CONTENT(plugin, search_query, TYPE='SERIES', **kwargs):
    plugin.add_sort_methods(xbmcplugin.SORT_METHOD_UNSORTED)
    plugin.log('SEARCH_CONTENT', lvl=plugin.DEBUG)
    headers = {'User-Agent': USER_AGENT}
    page = 0
    hasMore = "True"
    productSubType = TYPE
    productType = "SHOW"
    filters = json.dumps({
                            "name": search_query,
                            "productType": productType,
                            "productSubType": productSubType,
                            "pageNumber": page,
                            "pageSize": 30
                        }, separators=(',', ':'))
    params = urlencode({'request': filters})
    plugin.log('Fetching url: %s' % SEARCH_URL, lvl=plugin.DEBUG)
    plugin.log('Fetching params: %s' % params, lvl=plugin.DEBUG)
    Response = urlquick.get(SEARCH_URL, params=params, headers=headers).json()
    items = Response['productList']
    for  item in items['products']:
        title = item['title']
        showId = item['id']
        plot = item['description']
        aired = str(item['createdDate'].split('T')[0])
        poster = formatimg(item['image']['posterImage'], 'poster')
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
