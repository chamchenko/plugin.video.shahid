import json, xbmcplugin, sys, xbmc, xbmcgui
from web_browser import cacheURL
from vars import *
from tools import log, uni
from create_item import addDir, addLink


def searchContent():
    search_string   = xbmcgui.Dialog().input('Search', type=xbmcgui.INPUT_ALPHANUM)
    page            = 0
    hasMore         = "True"
    xbmcplugin.setContent(int(sys.argv[1])    , 'tvshows')
    while hasMore == "True":
        query           = urllib.quote('{"name":"%s","pageNumber":%s,"pageSize":22}'%(search_string,page))
        url             = SEARCH_URL%query
        print url
        headers         = {'User-Agent': USER_AGENT}
        Response        = cacheURL(url, headers)
        items           = json.loads(Response)['productList']
        hasMore         = str(items['hasMore'])
        for  item in items['products']:
            if str(item['pricingPlans'][0]['availability']['plus']) != "True" and str(item['productType']) == "SHOW" :
                title       = item['title']
                uuu         = item['productUrl']['url']
                showId      = item['id']
                plot        = item['description']
                aired       = str(item['createdDate'].split('T')[0])
                posterr     = item['image']['posterImage'].replace('{height}', '450').replace('{width}', '300').replace('{croppingPoint}', 'mc')
                fanartt     = item['image']['thumbnailImage'].split('?')[0]
                infoLabels  = {"mediatype":"episode","title":title, "aired":aired, "plot":plot, "TVShowTitle":title}
                infoArt     = {"thumb":posterr,"poster":posterr,"fanart":fanartt,"icon":ICON,"logo":ICON}
                addDir(title, str(showId), 4, infoArt, infoLabels )
        hasMore = str(items['hasMore'])
        page    = page+1
#https://api2.shahid.net/proxy/v2/search/grid?request=%7B%22name%22%3A%22the%20voice%22%2C%22pageNumber%22%3A0%2C%22pageSize%22%3A24%7D
