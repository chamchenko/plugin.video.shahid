import json, xbmcplugin, sys, xbmc
from web_browser import cacheURL
from vars import *
from tools import log
from create_item import addLink
def getLive():
    log('browseCategory')
    xbmcplugin.setContent(int(sys.argv[1])    , 'videos')
    headers     = {'User-Agent': USER_AGENT}
    Response    = cacheURL(LIVES_API, headers)
    items       = json.loads(Response)['productList']['products']
    for  item in items:
        title       = item['title']
        uuu         = item['productUrl']['url']
        chid        = item['id']
        thumb       = item['thumbnailImage'].replace('{height}', '500').replace('{width}', '500').replace('{croppingPoint}', 'mc')
        urlp        = str(chid)
        infoLabels  = {"mediatype":"episodes","title":title,"TVShowTitle":title}
        infoArt     = {"thumb":thumb,"poster":thumb,"fanart":FANART,"icon":ICON,"logo":ICON}
        addLink(title, urlp, 9, infoLabels, infoArt, len(items))
