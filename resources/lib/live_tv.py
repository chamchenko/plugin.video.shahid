# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid


import json
import urlquick

from .tools import urlencode
from .tools import formatimg
from .vars import *
from .tools import get_headers
from .tools import get_filter
from .playback_resolver import play_video
from codequick import Route
from codequick import Listitem
from codequick import Resolver



@Route.register(content_type="files")
def LIVE_TV(plugin, profile_id=None, profile_type=None, is_master=False, page='0'):
    plugin.log('LIVE_TV', lvl=plugin.DEBUG)
    headers = get_headers(profile_id, profile_type, is_master)
    params = get_filter(
                            requesttype='filter',
                            pageNumber=page,
                            pageSize=50,
                            productType="LIVESTREAM",
                            productSubType="LIVE_CHANNEL",
                            sorts=[{"order": "DESC", "type": "SORTDATE"}]
                        )
    plugin.log('Fetching url: %s' % URL_LIVE, lvl=plugin.DEBUG)
    plugin.log('Fetching params: %s' % params, lvl=plugin.DEBUG)
    Response = urlquick.get(URL_LIVE, params=params, headers=headers).json()
    items = Response['productList']['products']
    for item in items:
        if profile_type == "KID":
            kidsAllowed = item['pricingPlans'][0]['kidsAllowed']
            if not kidsAllowed:
                continue
        title = item['title']
        chId = item['id']
        thumb = formatimg(item['thumbnailImage'], 'icon')
        liz = Listitem()
        liz.art["thumb"] = thumb
        liz.art["fanart"] = thumb
        liz.label = title
        liz.set_callback(play_video, streamId=chId)
        plugin.log('Adding: %s' % title, lvl=plugin.DEBUG)
        yield liz


