# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid


import json
import urlquick
import inputstreamhelper

from .vars import *
from .tools import get_headers
from .tools import get_filter
from codequick import Listitem
from codequick import Resolver
from codequick import Script
from xbmc import getInfoLabel



@Resolver.register
def play_video(plugin, streamId, **kwargs):
    plugin.log('play_video streamId: %s' % streamId, lvl=plugin.DEBUG)
    EMAIL = plugin.setting.get_string('username')
    PASSWORD = plugin.setting.get_string('password')
    playout_url = PLAYOUT_URL % streamId
    PLAYOUT_HEADERS = get_headers()
    plugin.log('Fetching url: %s' % playout_url, lvl=plugin.DEBUG)
    try:
        Response = urlquick.get(playout_url, headers=PLAYOUT_HEADERS)
    except urlquick.HTTPError as err:
        plugin.log('HTTPError: %s' % err, lvl=plugin.DEBUG)
        if '422 Client Error' in str(err) and EMAIL and PASSWORD:
            plugin.notify(
                            plugin.localize(30209),
                            plugin.localize(30206),
                            display_time=5000,
                            sound=True
                         )
        elif '422 Client Error' in str(err):
            plugin.notify(
                            plugin.localize(30209),
                            plugin.localize(30207),
                            display_time=5000,
                            sound=True
                         )
        else:
            plugin.notify(
                            plugin.localize(30209),
                            plugin.localize(30205),
                            display_time=5000,
                            sound=True
                         )
        return False
    jsonstr = Response.json()
    video_url = jsonstr['playout']['url']
    drm = jsonstr['playout']['drm']
    plugin.log('Playing: %s' % video_url, lvl=plugin.DEBUG)
    item = Listitem()
    item.label = getInfoLabel('ListItem.Label')
    item.path = video_url
    item.property[INPUTSTREAM_PROP] ='inputstream.adaptive'
    headers = {'User-Agent': USER_AGENT}
    if drm and 'm3u8' not in video_url:
        is_helper = inputstreamhelper.Helper('ism', drm='com.widevine.alpha')
        if is_helper.check_inputstream():
            params =  get_filter(requesttype='request', assetId=streamId)
            headers = {
                        'User-Agent': USER_AGENT,
                        'BROWSER_NAME': 'CHROME',
                        'SHAHID_OS': 'LINUX',
                        'BROWSER_VERSION': '79.0'
                      }
            Response = urlquick.get(requrl, params=params, headers=headers).json()
            licenceurl = Response['signature']
            authority = 'shahiddotnet.keydelivery.westeurope.media.azure.net'
            LICENSE_TEMP = '%s|authority=%s&origin=%s&User-Agent=%s&referer=%s|R{SSM}|'
            URL_LICENCE_KEY = LICENSE_TEMP % (
                                                licenceurl,
                                                authority,
                                                BASE_URL,
                                                USER_AGENT,
                                                BASE_URL
                                             )
            item.property['inputstream.adaptive.manifest_type'] = 'ism'
            item.property['inputstream.adaptive.license_type'] = 'com.widevine.alpha'
            item.property['inputstream.adaptive.license_key'] = URL_LICENCE_KEY
        else:
            return False
    else:
        item.property['inputstream'] = 'inputstream.adaptive'
        item.property['inputstream.adaptive.manifest_type'] = 'hls'
    return item
