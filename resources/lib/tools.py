# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid

import xbmc
import json
import urlquick
import base64

from .vars import *
from Crypto.Cipher import AES
from codequick.utils import ensure_native_str
from codequick import Listitem
from codequick import Script



try:
    from urllib.parse import quote
    from urllib.parse import quote_plus
    from urllib.parse import unquote_plus
    from urllib.parse import urlencode
except ImportError:
    from urllib import quote
    from urllib import quote_plus
    from urllib import unquote_plus
    from urllib import urlencode



def formatimg(URL, TYPE):
    croppingPoint = 'mc'
    if TYPE == 'fanart':
        height = 1080
        width = 1920
    elif TYPE == 'poster':
        height = 450
        width = 300
    elif TYPE == 'thumbnail':
        height = 180
        width = 320
    elif TYPE == 'icon':
        height = 250
        width = 250
    elif TYPE == 'banner':
        height = ''
        width = ''
    URL = ensure_native_str(URL.format(height = height, width = width, croppingPoint = croppingPoint), 'utf-8')
    # in some case the api is returning a faulty url
    if not '/mediaObject' in URL:
        URL = URL.replace('mediaObject', '/mediaObject')
    return quote(URL, safe='&?=:/')

def encryptPASS():
    Script.log('encryptPASS: %s', lvl=Script.DEBUG)
    PASSWORD = Script.setting.get_string('password')
    password_store = Script.setting.get_string('encryptedpass')
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
        Script.setting.__setitem__(
                                    'encryptedpass',
                                    '%s|%s'%(ENCRYPTED_PASSWORD, PASSWORD)
                                  )
    return ENCRYPTED_PASSWORD


def getToken(USE_CASE):
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



def authenticate():
    TOKEN = getToken("LOGIN")
    #encrypt the password
    ENCRYPTED_PASSWORD = encryptPASS()
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
                                headers=LOGIN_HEADERS,
                                max_age=604800
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

def get_headers(profile_id=None, profile_type=None, is_master=False):
    TOKEN = getToken('PLAYOUT')
    headers = {
                'Shahid-Agent': SHAHID_AGENT,
                'User-Agent': SHAHID_AGENT,
                'UUID': 'ios',
                'language': language,
                'S-Session': TOKEN
              }
    EMAIL = Script.setting.get_string('username')
    PASSWORD = Script.setting.get_string('password')

    if is_master and profile_type != 'KID':
        master = 1
    else:
        master = 0

    if EMAIL and PASSWORD:
        Session = authenticate()['SESSION_ID']
        headers.update({'Token': Session})
    if not profile_id:
        pass
    if profile_type == 'KID':
        ageRestriction = True
        age = 12
    else:
        ageRestriction = False
        age = None

    HEAD = json.dumps({
                        "id": profile_id,
                        "master": master,
                        "age": age,
                        "ageRestriction": ageRestriction
                    }, separators=(',', ':'))
    headers.update({'profile': HEAD})
    return headers



def get_filter(requesttype, CATEGORY_MODE=None, **kwargs):
    filters = {}
    for ARG in kwargs:
        if kwargs[ARG]:
            if ARG == "genreId":
                if CATEGORY_MODE == "Dialect":
                    filters.update({"dialect": kwargs[ARG]})
                elif CATEGORY_MODE == "Genre":
                    filters.update({"genres": [kwargs[ARG]]})
            else:
                filters.update({ARG: kwargs[ARG]})
    result = urlencode({requesttype: json.dumps(filters, separators=(',', ':'))})
    return result


