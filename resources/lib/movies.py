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
from codequick import Route, Listitem, Resolver
from codequick.utils import ensure_native_str



@Route.register
def CATEGORIES_M(plugin, profile_id=None, profile_type=None, is_master=False, **kwargs):
    plugin.log('CATEGORIES Movies', lvl=plugin.DEBUG)
    if Movie_Category_Mode == "Dialect":
        genre_list = DIALECTS_MOVIES
    elif Movie_Category_Mode == "Genre":
        genre_list = GENRES_MOVIES

    t_key = 'title_%s' % language
    for genre in genre_list:
        title = genre[t_key]
        genreId = genre['id']
        item = Listitem()
        item.label = title
        item.info['mediatype'] = "episode"
        item.set_callback(
                            BROWSE_MOVIES,
                            genreId=genreId,
                            profile_id=profile_id,
                            profile_type=profile_type
                         )
        plugin.log('Adding: %s' % title, lvl=plugin.DEBUG)
        yield item


@Route.register(autosort=False, content_type="movies")
def BROWSE_MOVIES(plugin, genreId, page='0',  profile_id=None, profile_type=None, is_master=False, **kwargs):
    plugin.log('BROWSE_MOVIES genreId: %s' % genreId, lvl=plugin.DEBUG)
    EMAIL = plugin.setting.get_string('username')
    PASSWORD = plugin.setting.get_string('password')
    headers = get_headers(profile_id, profile_type, is_master)
    productType = 'MOVIE'
    hasMore = True
    liz = None
    while not liz and hasMore:
        plugin.log('page: %s' % page, lvl=plugin.DEBUG)
        params = get_filter(
                                requesttype='filter',
                                CATEGORY_MODE=Movie_Category_Mode,
                                pageNumber=page,
                                pageSize=30,
                                productType=productType,
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
            title = ensure_native_str(item['title'], 'utf-8')
            plot = ensure_native_str(item['description'], 'utf-8')
            cast = []
            for person in item['persons']:
                actor   = person['fullName']
                cast.append(actor)

            if item['pricingPlans'][0]['availability']:
                movieId = item['id']
                if item['pricingPlans'][0]['availability']['plus']:
                    if HIDE_PREMIUM:
                        continue
                    title += ' |%s|' % ensure_native_str(plugin.localize(30308), 'utf-8')
            # if not available assume it's comming soon and return the trailer
            elif item['trailerItem']:
                title += ' |%s|' % ensure_native_str(plugin.localize(30309), 'utf-8')
                movieId = item['trailerItem']['id']
            else:
                continue
            aired = str(item['createdDate'].split('T')[0])
            liz = Listitem()
            liz.label = title
            if item['trailerItem']:
                trailerId = item['trailerItem']['id']
                trailer = 'plugin://plugin.video.shahid/resources/lib/playback_resolver/play_video/?streamId=%s' % trailerId
                liz.info['trailer'] = trailer
            liz.info['mediatype'] = "movie"
            liz.info['cast'] = cast
            liz.art["poster"] = formatimg(item['image']['posterImage'], 'poster')
            liz.art["fanart"] = formatimg(item['image']['thumbnailImage'], 'fanart')
            if 'logoTitleImage' in item:
                liz.art["banner"] = formatimg(item['logoTitleImage'], 'banner')
            liz.info.date(aired, "%Y-%m-%d")
            liz.info['plot'] = plot
            liz.set_callback(play_video, streamId=movieId)
            plugin.log('Adding: %s' % title, lvl=plugin.DEBUG)
            if EMAIL and PASSWORD:
                CONTEXT_MENU(liz, movieId, profile_id, profile_type, is_master)
            CONTEXT_MENU2(liz, movieId, item['title'], "MOVIE")
            yield liz
        if not liz:
            page = int(page) + 1

    if hasMore:
        page = int(page)+1
        yield Listitem.next_page(
                                    genreId=genreId,
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
        
