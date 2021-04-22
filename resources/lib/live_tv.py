# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid

from __future__ import unicode_literals

import json
import urlquick
from .tools import urlencode
from .tools import formatimg
from .vars import *
from .playback_resolver import play_video
from codequick import Route, Listitem, Resolver

@Route.register(content_type="files")
def LIVE_TV(plugin, KIDS=False):
    plugin.log('LIVE_TV', lvl=plugin.DEBUG)
    headers = {'User-Agent': USER_AGENT}
    filters = {
                "pageNumber": 0,
                "pageSize": 50,
                "productType": "LIVESTREAM",
                "productSubType": "LIVE_CHANNEL"
              }
    filters = json.dumps(filters, separators=(',', ':'))
    LIVE_PARAMS = urlencode({'filter': filters})
    plugin.log('Fetching url: %s' % URL_LIVE, lvl=plugin.DEBUG)
    plugin.log('Fetching params: %s' % LIVE_PARAMS, lvl=plugin.DEBUG)
    Response = urlquick.get(URL_LIVE, params=LIVE_PARAMS, headers=headers).json()
    elems = Response['productList']['products']
    for elem in elems:
        if KIDS == True:
            kidsAllowed = elem['pricingPlans'][0]['kidsAllowed']
            if not kidsAllowed:
                continue
        title = elem['title']
        chid = elem['id']
        thumb = formatimg(elem['thumbnailImage'], 'icon')
        url = chid
        item = Listitem()
        item.art["thumb"] = thumb
        item.art["fanart"] = thumb
        item.label = title
        item.set_callback(play_video, url=url)
        plugin.log('Adding: %s' % title, lvl=plugin.DEBUG)
        yield item


