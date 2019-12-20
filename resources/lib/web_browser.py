import urllib, urllib2, xbmcgui, xbmc, datetime
from vars import *
from simplecache import SimpleCache
from tools import log
cache = SimpleCache()
def cacheURL(url, headers):
    log('cacheURL, url = ' + str(url))
    try:
        cacheResponse = cache.get(ADDON_NAME + '.openURL, url = %s,headers = %s'%(url,headers))
        if not cacheResponse:
            request = urllib2.Request(url, headers=headers)
            cacheResponse = urllib2.urlopen(request, timeout = TIMEOUT).read().decode('utf-8').strip()
            cache.set(ADDON_NAME + '.openURL, url = %s,headers = %s'%(url,headers), cacheResponse, expiration=datetime.timedelta(hours=1))
        return cacheResponse
    except Exception as e:log("openURL Failed! " + str(e), xbmc.LOGERROR)
    xbmcgui.Dialog().notification(ADDON_NAME, LANGUAGE(30001), ICON, 4000)
    return ''
