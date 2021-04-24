# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid

from __future__ import unicode_literals

import json
import urlquick
import xbmcplugin

from codequick import Route, Resolver, Listitem, run
from codequick.utils import urljoin_partial, bold, ensure_native_str
from .tools import *
from .vars import *

from .movies import CATEGORIES_M
from .tvshows import CATEGORIES
from .tvshows import BROWSE_SEASONS
from .playback_resolver import play_video
from .live_tv import LIVE_TV





BASE_URL = "https://api2.shahid.net/proxy/v2/"
url_constructor = urljoin_partial(BASE_URL)

Live_TV = 30101
TV_Shows = 30102
TV_Programs = 30103
Kids = 30107


# noinspection PyUnusedLocal
@Route.register
def root(plugin):
    if MODE_KIDS:
        plugin.log('Creating Kids Menu', lvl=plugin.WARNING)
        yield Listitem.from_dict(
                                    LIVE_TV,
                                    bold(plugin.localize(Live_TV)),
                                    params={"KIDS": True}
                                )
        yield Listitem.from_dict(
                                    CATEGORIES,
                                    bold(plugin.localize(TV_Shows)),
                                    params={"TYPE": "SERIES", "KIDS": True}
                                )
        yield Listitem.from_dict(
                                    CATEGORIES,
                                    bold(plugin.localize(TV_Programs)),
                                    params={"TYPE": "PROGRAM", "KIDS": True}
                                )
    else:
        plugin.log('Creating Main Menu', lvl=plugin.WARNING)
        yield Listitem.from_dict(
                                    LIVE_TV,
                                    bold(plugin.localize(Live_TV))
                                )
        yield Listitem.from_dict(
                                    CATEGORIES,
                                    bold(plugin.localize(TV_Shows)),
                                    params={"TYPE": "SERIES"}
                                )
        yield Listitem.from_dict(
                                    CATEGORIES,
                                    bold(plugin.localize(TV_Programs)),
                                    params={"TYPE": "PROGRAM"}
                                )
        yield Listitem.from_dict(
                                    CATEGORIES_M,
                                    bold('Movies'),
                                    params={"TYPE": "PROGRAM"}
                                )
        yield Listitem.from_dict(
                                    KIDS_MENU,
                                    bold(plugin.localize(Kids))
                                )
        yield Listitem.search(SEARCH_CONTENT)

@Route.register
def KIDS_MENU(plugin):
    plugin.log('Creating Kids Menu', lvl=plugin.WARNING)
    yield Listitem.from_dict(
                                LIVE_TV,
                                bold(plugin.localize(Live_TV)),
                                params={"KIDS": True}
                            )
    yield Listitem.from_dict(
                                CATEGORIES,
                                bold(plugin.localize(TV_Shows)),
                                params={"TYPE": "SERIES", "KIDS": True}
                            )
    yield Listitem.from_dict(
                                CATEGORIES,
                                bold(plugin.localize(TV_Programs)),
                                params={"TYPE": "PROGRAM", "KIDS": True}
                            )


@Route.register(autosort=False, content_type="movies")
def SEARCH_CONTENT(plugin, search_query, page=0, **kwargs):
    plugin.add_sort_methods(xbmcplugin.SORT_METHOD_UNSORTED)
    plugin.log('SEARCH_CONTENT', lvl=plugin.DEBUG)
    headers = {'User-Agent': USER_AGENT}
    filters = json.dumps({
                            "name": search_query,
                            "pageNumber": page,
                            "pageSize": 30
                        }, separators=(',', ':'))
    params = urlencode({'request': filters})
    plugin.log('Fetching url: %s' % SEARCH_URL, lvl=plugin.DEBUG)
    plugin.log('Fetching params: %s' % params, lvl=plugin.DEBUG)
    Response = urlquick.get(SEARCH_URL, params=params, headers=headers).json()
    items = Response['productList']
    hasMore = items['hasMore']
    for item in items['products']:
        title = item['title']
        plot = item['description']
        if item['pricingPlans'][0]['availability']:
            if item['pricingPlans'][0]['availability']['plus']:
                if HIDE_PREMIUM:
                    continue
                title += ' |Premium|'
                plot = '[Premium]\n' + plot
        else:
            continue
        itemId = item['id']
        productType = item['productType']
        liz = Listitem()
        plugin.log('title: %s' % ensure_native_str(title))
        liz.label = ensure_native_str(title)
        liz.art["poster"] = formatimg(item['image']['posterImage'], 'poster')
        liz.art["fanart"] = formatimg(item['image']['thumbnailImage'], 'fanart')
        aired = str(item['createdDate'].split('T')[0])
        liz.info.date(aired, "%Y-%m-%d")
        if productType == 'MOVIE':
            liz.info['plot'] = '[MOVIE]: %s' % ensure_native_str(plot)
            liz.info['mediatype'] = "movie"
            liz.set_callback(play_video, url=itemId)
        elif productType == 'SHOW':
            liz.info['plot'] = '[TV SHOWS]: %s' % ensure_native_str(plot)
            liz.info['mediatype'] = "show"
            liz.set_callback(BROWSE_SEASONS, url=itemId)            
        plugin.log('Adding: %s' % title, lvl=plugin.DEBUG)
        yield liz

    if hasMore:
        page = int(page)+1
        yield Listitem.next_page(
                                    search_query=search_query,
                                    page=str(page)
                                )
        yield False
