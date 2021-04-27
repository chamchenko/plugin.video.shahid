# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid


import json
import urlquick
import xbmcgui
import xbmcplugin

from .tools import urlencode
from .tools import formatimg
from .tools import get_headers
from .tools import get_filter
from .categories import *
from .vars import *
from .addon_utils import CONTEXT_MENU
from .addon_utils import CONTEXT_MENU2
from .playback_resolver import play_video
from codequick import Route
from codequick import Listitem
from codequick import Resolver
from codequick.utils import ensure_native_str



@Route.register
def CATEGORIES(plugin, productSubType='SERIES', profile_id=None, profile_type=None, is_master=False, **kwargs):
    plugin.log('CATEGORIES TYPE: %s' % productSubType, lvl=plugin.DEBUG)
    if productSubType == "SERIES":
        if Show_Category_Mode == "Dialect":
            genre_list = DIALECTS_TVSHOWS
        elif Show_Category_Mode == "Genre":
            genre_list = GENRES_TVSHOWS
    elif productSubType == 'PROGRAM':
        if Show_Category_Mode == "Dialect":
            genre_list = DIALECTS_PROGRAMS
        elif Show_Category_Mode == "Genre":
            genre_list = GENRES_PROGRAMS

    t_key = 'title_%s' % language
    for genre in genre_list:
        title = genre[t_key]
        genreId = genre['id']
        item = Listitem()
        item.label = title
        item.info['mediatype'] = "episode"
        item.set_callback(
                            BROWSE_TVSHOWS,
                            genreId=genreId,
                            productSubType=productSubType,
                            profile_id=profile_id,
                            profile_type=profile_type
                         )
        plugin.log('Adding: %s' % title, lvl=plugin.DEBUG)
        yield item


@Route.register(autosort=False, content_type="tvshows")
def BROWSE_TVSHOWS(plugin, genreId, productSubType, page='0', profile_id=None, profile_type=None, is_master=False, **kwargs):
    plugin.log('BROWSE_TVSHOWS genreId: %s' % genreId, lvl=plugin.DEBUG)
    plugin.log('BROWSE_TVSHOWS productSubType: %s' % productSubType, lvl=plugin.DEBUG)
    EMAIL = plugin.setting.get_string('username')
    PASSWORD = plugin.setting.get_string('password')
    headers = get_headers(profile_id, profile_type, is_master)
    productType = 'SHOW'
    hasMore = True
    liz = None
    while not liz and hasMore:
        plugin.log('page: %s' % page, lvl=plugin.DEBUG)
        params = get_filter(
                                requesttype='filter',
                                CATEGORY_MODE=Show_Category_Mode,
                                pageNumber=page,
                                pageSize=30,
                                productType=productType,
                                productSubType=productSubType,
                                sorts=[{"order": "DESC", "type": "SORTDATE"}],
                                genreId=genreId
                            )
        plugin.log('Fetching url: %s' % TVSOWS_API, lvl=plugin.DEBUG)
        plugin.log('Fetching params: %s' % params, lvl=plugin.DEBUG)
        Response = urlquick.get(
                                    TVSOWS_API,
                                    params=params,
                                    headers=headers,
                                    max_age=0
                               ).json()
        items = Response['productList']
        hasMore = items['hasMore']
        for item in items['products']:
            title = item['title']
            plot = item['description']
            if item['pricingPlans'][0]['availability']:
                if item['pricingPlans'][0]['availability']['plus']:
                    if HIDE_PREMIUM:
                        continue
                    title += ' |%s|' % plugin.localize(30308)
                showId = item['id']
            liz = Listitem()
            liz.label = ensure_native_str(title)
            liz.info['mediatype'] = "tvshow"
            liz.art["poster"] = formatimg(item['image']['posterImage'], 'poster')
            liz.art["fanart"] = formatimg(item['image']['thumbnailImage'], 'fanart')
            if 'logoTitleImage' in item:
                liz.art["banner"] = formatimg(item['logoTitleImage'], 'banner')
            aired = str(item['createdDate'].split('T')[0])
            liz.info.date(aired, "%Y-%m-%d")
            liz.info['plot'] = ensure_native_str(plot)
            liz.set_callback(
                                BROWSE_SEASONS,
                                showId=showId,
                                profile_id=profile_id,
                                profile_type=profile_type,
                                is_master=is_master
                            )
            plugin.log('Adding: %s' % title, lvl=plugin.DEBUG)
            if EMAIL and PASSWORD:
                CONTEXT_MENU(liz, showId, profile_id, profile_type, is_master)
            CONTEXT_MENU2(liz, showId, item['title'], "SHOW")
            yield liz
        if not liz:
            page = int(page) + 1

    if hasMore:
        page = int(page)+1
        yield Listitem.next_page(
                                    genreId=genreId,
                                    productSubType=productSubType,
                                    page=str(page),
                                    profile_id=profile_id,
                                    profile_type=profile_type,
                                    is_master=is_master
                                )
    if not liz and not hasMore:
        yield False
        plugin.notify(
                        plugin.localize(30208),
                        plugin.localize(30202),
                        display_time=5000,
                        sound=True
                     )
        


@Route.register(autosort=False, content_type="seasons")
def BROWSE_SEASONS(plugin, showId, profile_id=None, profile_type=None, is_master=False, **kwargs):
    plugin.log('BROWSE_TVSHOWS showId: %s' % showId, lvl=plugin.DEBUG)
    headers = get_headers(profile_id, profile_type, is_master)
    params = get_filter(requesttype='request', showId=showId)
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
                    json_parser['productModel']['show']['season']['image']['landscapeClean'], 'fanart')
    items = json_parser['productModel']['show']['seasons']
    liz = None
    lizc = None
    for item in items:
        seasonNumb = item['seasonNumber']
        title = plugin.localize(30106) + " %s" % seasonNumb
        seasonId = item['id']
        params =  get_filter(requesttype='request', seasonId=seasonId)
        plugin.log('Fetching url: %s' % PLAYABLE_API, lvl=plugin.DEBUG)
        plugin.log('Fetching params: %s' % params, lvl=plugin.DEBUG)
        season_items = urlquick.get(PLAYABLE_API, params=params, headers=headers).json()
        count = season_items['productModel']['playlist']['count']
        if count == 0:
            continue
        thumb = formatimg(
                    season_items['productModel']['show']['season']['image']['heroSliderImage'], 'thumbnail')

        if thumb == "":
            thumb = formatimg(
                        season_items['productModel']['show']['season']['image']['thumbnailImage'], 'thumbnail')

        if thumb == "":
            thumb = formatimg(
                        season_items['productModel']['show']['season']['image']['landscapeClean'], 'thumbnail')
        fanart = formatimg(
                    season_items['productModel']['show']['season']['image']['landscapeClean'], 'fanart')
        playListId = season_items['productModel']['playlist']['id']
        aired = season_items['productModel']['createdDate'].split('T')[0]
        if json_parser['productModel']['show']['season']['pricingPlans'][0]['availability']:
            if json_parser['productModel']['show']['season']['pricingPlans'][0]['availability']['plus']:
                if HIDE_PREMIUM:
                    continue
                title += ' [%s]' % plugin.localize(30308)
        else:
            continue
        liz = Listitem()
        liz.label = title
        liz.art["fanart"] = fanart
        liz.art["thumb"] = thumb
        liz.info.date(aired, "%Y-%m-%d")
        liz.info['mediatype'] = "tvshow"
        liz.set_callback(
                            BROWSE_EPISODES,
                            playListId=playListId,
                            profile_id=profile_id,
                            profile_type=profile_type,
                            is_master=is_master
                        )
        plugin.log('Adding: %s' % title, lvl=plugin.DEBUG)
        yield liz
        if not Hide_Clips:
            for playlist in season_items['productModel']['show']['season']['playlists']:
                if (playlist['type'] == "CLIP" and playlist['count'] > 0):
                    playListId = playlist['id']
                    title = "%s - %s %s %s" % (
                                                plugin.localize(30106),
                                                plugin.localize (30107),
                                                seasonNumb,
                                                playlist['title']
                                              )
                    lizc = Listitem()
                    lizc.label = title
                    lizc.info['mediatype'] = "tvshow"
                    lizc.TVShowTitle = TVShowTitle
                    lizc.season = seasonNumb
                    lizc.art["fanart"] = fanart
                    lizc.art["thumb"] = thumb
                    lizc.set_callback(BROWSE_EPISODES, playListId=playListId)
                    plugin.log('Adding: %s' % title, lvl=plugin.DEBUG)
                    yield lizc
    if not liz and not lizc:
        yield False
        plugin.notify(
                        plugin.localize(30208),
                        plugin.localize(30202),
                        display_time=5000,
                        sound=True
                     )
        

@Route.register(autosort=False, content_type="episodes")
def BROWSE_EPISODES(plugin, playListId, profile_id=None, profile_type=None, is_master=False, **kwargs):
    plugin.add_sort_methods(xbmcplugin.SORT_METHOD_EPISODE)
    plugin.log('BROWSE_EPISODES playListId: %s' % playListId, lvl=plugin.DEBUG)
    headers = get_headers(profile_id, profile_type, is_master)
    page = 0
    hasMore = True
    while hasMore:
        params = get_filter(
                                requesttype='request',
                                playListId=playListId,
                                pageNumber=page,
                                pageSize=30
                           )
        plugin.log('Fetching url: %s' % PLAYLIST_API, lvl=plugin.DEBUG)
        plugin.log('Fetching params: %s' % params, lvl=plugin.DEBUG)
        Response = urlquick.get(PLAYLIST_API, params=params, headers=headers).json()
        items = Response['productList']
        hasMore = items['hasMore']
        showTitle = items['products'][0]['show']['title']
        plugin.log('showTitle: %s' % showTitle, lvl=plugin.DEBUG)
        for item in items['products']:
            streamId = item['id']
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
                liz.label = ensure_native_str(showTitle, 'utf-8')
                liz.TVShowTitle = showTitle
            else:
                liz.label = ensure_native_str(title, 'utf-8') \
                    or ensure_native_str(item['bcmMediaID'], 'utf-8')
                liz.info['mediatype'] = "video"
            liz.info['plot'] = ensure_native_str(plot, 'utf-8')
            liz.art["thumb"] = thumb
            liz.info.date(aired, "%Y-%m-%d")
            liz.info.duration = duration
            liz.set_callback(play_video, streamId=streamId)
            plugin.log('Adding: %s S%sxE%s' % (showTitle,seasonNumb, episodeNumb), lvl=plugin.DEBUG)
            yield liz
        page = page+1
