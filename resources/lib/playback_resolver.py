# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid

from __future__ import unicode_literals

import json
import urlquick
from .vars import *
from codequick import Listitem,  Resolver
import inputstreamhelper

@Resolver.register
def play_video(plugin, url, **kwargs):
    plugin.log('play_video streamId: %s' % url, lvl=plugin.DEBUG)
    headers = {'User-Agent': USER_AGENT}
    playout_url = PLAYOUT_URL + str(url)
    plugin.log('Fetching url: %s' % playout_url, lvl=plugin.DEBUG)
    try:
        Response = urlquick.get(playout_url, headers=headers)
    except urlquick.HTTPError as err:
        plugin.log('HTTPError: %s' % err, lvl=plugin.DEBUG)
        if '422 Client Error' in str(err):
            plugin.notify(
                            'Playback error',
                            'Premium Video',
                            display_time=5000,
                            sound=True
                         )
        return False
    jsonstr = Response.json()
    video_url = jsonstr['playout']['url']
    drm = jsonstr['playout']['drm']
    plugin.log('Playing: %s' % video_url, lvl=plugin.DEBUG)
    item = Listitem()
    item.path = video_url
    item.property[INPUTSTREAM_PROP] ='inputstream.adaptive'
    if drm and 'm3u8' not in video_url:
        is_helper = inputstreamhelper.Helper('ism', drm='com.widevine.alpha')
        if is_helper.check_inputstream():
            filters = json.dumps({"assetId":streamId}, separators=(',', ':'))
            params = urlencode({'request': filters})
            headers = {
                        'User-Agent': USER_AGENT,
                        'BROWSER_NAME': 'CHROME',
                        'SHAHID_OS': 'LINUX',
                        'BROWSER_VERSION': '79.0'
                      }
            Response = urlquick.get(requrl, params=params, headers=headers).json()
            licenceurl = Response['signature']
            authority = 'shahiddotnet.keydelivery.westeurope.media.azure.net'
            URL_LICENCE_KEY = '%s|authority=%s&origin=%s&User-Agent=%s&referer=%s|R{SSM}|'%(licenceurl,authority,BASE_URL,USER_AGENT,BASE_URL)
            item.property['inputstream.adaptive.manifest_type'] = 'ism'
            item.property['inputstream.adaptive.license_type'] = 'com.widevine.alpha'
            item.property['inputstream.adaptive.license_key'] = URL_LICENCE_KEY
        else:
            return False
    else:
        item.property['inputstream'] = 'inputstream.adaptive'
        item.property['inputstream.adaptive.manifest_type'] = 'hls'
    return item
