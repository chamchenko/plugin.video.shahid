# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid


import json
import urlquick
import xbmcplugin

from codequick import Route
from codequick import Listitem
from codequick import Script
from codequick.utils import ensure_native_str
from .tools import *
from .vars import *
from .addon_utils import CONTEXT_MENU
from .addon_utils import CONTEXT_MENU2
from .tvshows import BROWSE_SEASONS
from .playback_resolver import play_video



def process_mixed_product(item):
    title = ensure_native_str(item['title'],'utf-8')
    if item['pricingPlans'][0]['availability']:
        if item['pricingPlans'][0]['availability']['plus']:
            if HIDE_PREMIUM:
                return False
            title += ' |%s|' % ensure_native_str(Script.localize(30308), 'utf-8')
    else:
        return False
    itemId = item['id']
    productType = item['productType']
    liz = Listitem()
    liz.label = title
    liz.art["poster"] = formatimg(item['image']['posterImage'], 'poster')
    liz.art["fanart"] = formatimg(item['image']['thumbnailImage'], 'fanart')
    if 'logoTitleImage' in item:
        liz.art["banner"] = formatimg(item['logoTitleImage'], 'banner')
    aired = str(item['createdDate'].split('T')[0])
    liz.info.date(aired, "%Y-%m-%d")
    liz.info['plot'] = ensure_native_str(item['description'], 'utf-8')
    if productType == 'MOVIE':
        liz.info['duration'] = item['duration']
        liz.info['mediatype'] = "movie"
        liz.set_callback(play_video, streamId=itemId)
    elif productType == 'SHOW':
        liz.info['mediatype'] = "show"
        liz.set_callback(BROWSE_SEASONS, showId=itemId)
    CONTEXT_MENU2(liz, itemId, title, productType)
    return liz



@Route.register(autosort=False, content_type="movies")
def SEARCH_CONTENT(plugin, search_query, profile_id=None, profile_type=None, is_master=False, page='0', **kwargs):
    plugin.add_sort_methods(xbmcplugin.SORT_METHOD_UNSORTED)
    plugin.log('SEARCH_CONTENT %s' % search_query, lvl=plugin.DEBUG)
    headers = get_headers(profile_id, profile_type, is_master)
    params = get_filter(
                            requesttype='request',
                            name=search_query,
                            pageNumber=page,
                            pageSize=30
                        )
    plugin.log('Fetching url: %s' % SEARCH_URL, lvl=plugin.DEBUG)
    plugin.log('Fetching params: %s' % params, lvl=plugin.DEBUG)
    Response = urlquick.get(
                                SEARCH_URL,
                                params=params,
                                headers=headers,
                                max_age=0
                           ).json()
    items = Response['productList']
    hasMore = items['hasMore']
    liz = None
    for item in items['products']:
        itemId = item['id']
        liz = process_mixed_product(item)   
        if liz:
            plugin.log('Adding: %s' % liz, lvl=plugin.DEBUG)
            if EMAIL and PASSWORD:
                CONTEXT_MENU(liz, itemId, profile_id, profile_type, is_master)
            yield liz
    if hasMore:
        page = int(page)+1
        yield Listitem.next_page(
                                    search_query=search_query,
                                    page=str(page),
                                    profile_id=profile_id,
                                    profile_type=profile_type
                                )
    if not liz and not hasMore:
        yield False
        plugin.notify(
                        plugin.localize(30208),
                        plugin.localize(30202),
                        display_time=5000,
                        sound=True
                     )

@Route.register(autosort=False, content_type="movies")
def MY_LIST(plugin, profile_id=None, profile_type=None, is_master=False, page='0', **kwargs):
    plugin.add_sort_methods(xbmcplugin.SORT_METHOD_UNSORTED)
    plugin.log('MY_LIST profile_id: %s' % profile_id, lvl=plugin.DEBUG)
    headers = get_headers(profile_id, profile_type, is_master)
    params = get_filter(
                            requesttype='request',
                            pageNumber=page,
                            pageSize=30,
                        )
    plugin.log('Fetching url: %s' % MY_LIST_URL, lvl=plugin.DEBUG)
    plugin.log('Fetching params: %s' % params, lvl=plugin.DEBUG)
    Response = urlquick.get(
                                MY_LIST_URL,
                                params=params,
                                headers=headers,
                                max_age=0
                           ).json()
    items = Response['productList']
    hasMore = items['hasMore']
    for item in items['products']:
        liz = process_mixed_product(item)   
        if liz:
            plugin.log('Adding: %s' % liz, lvl=plugin.DEBUG)
            yield liz

    if hasMore:
        page = int(page)+1
        yield Listitem.next_page(
                                    search_query=search_query,
                                    page=str(page),
                                    profile_id=profile_id,
                                    profile_type=profile_type
                                )
