# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid

from __future__ import unicode_literals
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
        height = 1920
        width = 1080
    if TYPE == 'poster':
        height = 450
        width = 300
    if TYPE == 'thumbnail':
        height = 180
        width = 320
    if TYPE == 'icon':
        height = 250
        width = 250
    URL = URL.format(height = height, width = width, croppingPoint = croppingPoint)
    # in some case the api is returning a faulty url
    if not '/mediaObject' in URL:
        URL = URL.replace('mediaObject', '/mediaObject')
    return quote(URL, safe='&?=:/')


def getBitrate(HLSRAW, drm, QUALITY):
    if not 'x%s'%QUALITY in HLSRAW:
        pattern = ',RESOLUTION\=.*x([0-9]+)'
        availables = re.findall(pattern, HLSRAW)
        QUALITY = 0
        for quality in availables:
            if quality > QUALITY:
                QUALITY = quality
    try:
        pattern = '(Bitrate\=\")([0-9]+)\".*(MaxHeight\=\"%s)'%QUALITY
        bitrate = int(re.findall(pattern, HLSRAW)[0][1])
    except:
        try:
            pattern = 'BANDWIDTH\=([0-9]+)(.*\,RESOLUTION\=.*x%s)'%QUALITY
            bitrate = int(re.findall(pattern, HLSRAW)[0][0])
        except:
            bitrate = None
    return bitrate
