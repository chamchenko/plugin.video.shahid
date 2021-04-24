# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid

from __future__ import unicode_literals

import json
import urlquick
import base64
import inputstreamhelper
from .vars import *
from codequick import Listitem,  Resolver, Script
from Crypto.Cipher import AES



@Resolver.register
def play_video(plugin, url, **kwargs):
    plugin.log('play_video streamId: %s' % url, lvl=plugin.DEBUG)
    playout_url = PLAYOUT_URL + str(url)
    TOKEN = getToken(plugin, 'PLAYOUT')
    plugin.log('TOKEN: %s' % TOKEN, lvl=plugin.DEBUG)

    PLAYOUT_HEADERS = {
                        'Shahid-Agent': SHAHID_AGENT,
                        'User-Agent': SHAHID_AGENT,
                        'UUID': 'ios',
                        'S-Session': TOKEN
                      }
    EMAIL = plugin.setting.get_string('username')
    PASSWORD = plugin.setting.get_string('password')
    if EMAIL and PASSWORD:
        Session = authenticate(plugin)['SESSION_ID']
        plugin.log('Session: %s' % Session, lvl=plugin.DEBUG)
        PLAYOUT_HEADERS.update({'Token': Session})
    plugin.log('Fetching url: %s' % playout_url, lvl=plugin.DEBUG)
    try:
        Response = urlquick.get(playout_url, headers=PLAYOUT_HEADERS)
    except urlquick.HTTPError as err:
        plugin.log('HTTPError: %s' % err, lvl=plugin.DEBUG)
        if '422 Client Error' in str(err) and EMAIL and PASSWORD:
            plugin.notify(
                            'Error',
                            'Login Failed',
                            display_time=5000,
                            sound=True
                         )
        elif '422 Client Error' in str(err):
            plugin.notify(
                            'Error',
                            'Premium Video',
                            display_time=5000,
                            sound=True
                         )
        else:
            plugin.notify(
                            'Error',
                            'Somthing Went Wrong, Please retry',
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
    headers = {'User-Agent': USER_AGENT}
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

@Script.register
def encryptPASS(plugin):
    plugin.log('encryptPASS: %s', lvl=plugin.DEBUG)
    PASSWORD = Script.setting.get_string('password')
    password_store = plugin.setting.get_string('encryptedpass')
    if password_store:
        ENCRYPTED_PASSWORD = password_store.split('|')[0]
        CLEAR_PASSWORD = password_store.split('|')[1]
    else:
        ENCRYPTED_PASSWORD = None
        CLEAR_PASSWORD = None
    if not ENCRYPTED_PASSWORD or CLEAR_PASSWORD != PASSWORD:
        secret_key = b'gx8KSZyPdfJhXes7'
        mode = AES.MODE_ECB
        bs = 16
        PADDING = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
        generator = AES.new(secret_key, mode)
        crypt = generator.encrypt(PADDING(PASSWORD).encode('utf-8'))
        ENCRYPTED_PASSWORD = base64.b64encode(crypt).decode('utf-8')
        plugin.setting.__setitem__(
                                    'encryptedpass',
                                    '%s|%s'%(ENCRYPTED_PASSWORD, PASSWORD)
                                  )
    return ENCRYPTED_PASSWORD

@Script.register
def getToken(plugin, USE_CASE):
    if USE_CASE == 'LOGIN':
        URL = LOGIN_TOKEN_URL
    else:
        URL = SESSION_TOKEN_URL
    HEADERS = {
                'User-Agent': USER_AGENT,
                'Shahid-Agent': SHAHID_AGENT
              }
    TOKEN = urlquick.post(
                            URL,
                            json = {},
                            headers = HEADERS,
                            max_age = -1
                         ).json()['jwt']
    return TOKEN

@Script.register
def authenticate(plugin, RENUE=False):
    TOKEN = getToken(plugin, "LOGIN")
    #encrypt the password
    ENCRYPTED_PASSWORD = encryptPASS(plugin)
    # build payload
    EMAIL = Script.setting.get_string('username')
    LOGIN_PAYLOAD = {
                        "email": EMAIL,
                        "password": ENCRYPTED_PASSWORD,
                        "deviceType": "Mobile",
                        "physicalDeviceType": "IOS",
                        "isNewUser": False,
                        "captchaToken": "c2hhaGlkLWF1dGgta2V5LXRva2Vu"
                    }
    LOGIN_HEADERS = {
                        'UUID': 'web',
                        'Content-Type': 'application/json',
                        'User-Agent': SHAHID_AGENT,
                        'S-Session': TOKEN
                    }
    LOGIN_DATA = urlquick.post(
                                LOGIN_URL,
                                json=LOGIN_PAYLOAD,
                                headers=LOGIN_HEADERS
                              ).json()
    LOGIN_INFO = {
                    'TOKEN': LOGIN_DATA['user']['token'],
                    'EXT_TOKEN': LOGIN_DATA['user']['externalToken'],
                    'SESSION_ID': LOGIN_DATA['user']['sessionId'],
                    'EXT_SESSION_ID': LOGIN_DATA['user']['externalSessionId'],
                    'EXT_USER_ID': LOGIN_DATA['user']['externalUserId'],
                    'HTTP_SESSION_ID': LOGIN_DATA['user']['httpSessionId']
                 }
    return LOGIN_INFO
