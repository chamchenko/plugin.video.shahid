import urlparse, socket, json, HTMLParser, sys, traceback, re
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from vars import *

def log(msg, level=xbmc.LOGDEBUG):
    if DEBUG == False and level != xbmc.LOGERROR: return
    if level == xbmc.LOGERROR: msg += ' ,' + traceback.format_exc()
    xbmc.log(ADDON_ID + '-' + ADDON_VERSION + '-' + msg, level)

def uni(string, encoding = 'utf-8'):
    if isinstance(string, basestring):
        if not isinstance(string, unicode): string = unicode(string, encoding)
        elif isinstance(string, unicode): string = string.encode('ascii', 'replace')
    return string

def unescape(string):
    try:
        parser = HTMLParser.HTMLParser()
        return (parser.unescape(string))
    except: return string

def getParams():
    return dict(urlparse.parse_qsl(sys.argv[2][1:]))

def getPlaybackURL(HLSRAW,burl):
    playbackURL= ""
    for idx, line in enumerate(HLSRAW.split('\n')):
        if  'x'+QUALITY.replace('p', '') in HLSRAW.split('\n')[idx]:
            playbackURL = HLSRAW.split('\n')[idx+1].strip()
            break
        else: playbackURL =  None
    if not playbackURL:
        for quality in QUALITIES:
            for idx, line in enumerate(HLSRAW.split('\n')):
                if  'x'+quality in HLSRAW.split('\n')[idx]:
                    playbackURL = HLSRAW.split('\n')[idx+1].strip()
                    break
                else: playbackURL =  None
            if playbackURL: break
    playbackURL = burl+playbackURL.strip()
    return playbackURL
