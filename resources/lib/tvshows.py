import json, xbmcplugin, sys, xbmc
from web_browser import cacheURL
from vars import *
from tools import log, uni
from create_item import addDir, addLink

TVSOWS_API      = API_Base + 'product/filter?filter=%s'
PLAYLIST_API    = API_Base + 'product/playlist?request=%s'
PLAYABLE_API    = API_Base + 'playableAsset?request=%s'


def getCategories(url):
    log('getCategories')
    headers         = {'User-Agent': USER_AGENT}
    items           = json.loads(url)
    url             = items['url']
    productSubType  = items['productSubType']
    Response        = cacheURL(url, headers)
    items           = json.loads(Response)
    for item in items:
        title               = item['name'].replace('Series - ', '').replace('Programs - ', '')
        AR_title            = (item['displaytext'])
        try:
            categoryID      = item['genreId']
            categoryID      = json.dumps({'genreId':categoryID,'productSubType':productSubType, "page":0, "category":title})
        except:
            categoryID      = item['dialectId']
            categoryID      = json.dumps({'dialectId':categoryID,'productSubType':productSubType, "page":0, "category":title})
        infoLabels          = {"mediatype":"episode","title":AR_title,"TVShowTitle":AR_title}
        infoArt             = {"thumb":ICON,"poster":ICON,"fanart":ICON,"icon":ICON,"logo":ICON}
        addDir(AR_title, categoryID, 3, infoArt, infoLabels )

def getShowsFromPage(items,page):
    log('getShowsFromPage')
    try:
        categoryID      = items['genreId']
        productSubType  = items['productSubType']
        filterstring    = 'genres'
        category        = items['category']
        filters         = json.dumps({filterstring:[categoryID],"pageNumber":page,"pageSize":22,"productType":"SHOW","productSubType":productSubType,"sorts":[{"order":"DESC","type":"SORTDATE"}]})
        nexpage         = json.dumps({'genreId':categoryID,'productSubType':productSubType, "page":page+1, "category":category})
    except:
        categoryID      = items['dialectId']
        productSubType  = items['productSubType']
        filterstring    = 'dialect'
        category        = items['category']
        filters         = json.dumps({filterstring:categoryID,"pageNumber":page,"pageSize":22,"productType":"SHOW","productSubType":productSubType,"sorts":[{"order":"DESC","type":"SORTDATE"}]})
        nexpage         = json.dumps({'dialectId':categoryID,'productSubType':productSubType, "page":page+1})
    headers             = {'User-Agent': USER_AGENT}
    query               = urllib.quote(filters)
    Response            = cacheURL(TVSOWS_API%query, headers)
    items               = json.loads(Response)['productList']
    hasMore             = str(items['hasMore'])
    xbmcplugin.setContent(int(sys.argv[1])    , 'tvshows')
    for  item in items['products']:
        if str(item['pricingPlans'][0]['availability']['plus']) != "True":
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
    return hasMore

def getShows(categoryID):
    log('browseCategory')
    items   = json.loads(categoryID)
    page    = items['page']
    hasMore = "True"
    while hasMore == "True":
        hasMore = getShowsFromPage(items,page)
        page    = page+1


def getSeasons(showId):
    log('getSeasons')
    headers     = {'User-Agent': USER_AGENT}
    filters     = json.dumps({"showId":showId})
    query       = urllib.quote(filters)
    Response    = cacheURL(PLAYABLE_API%query, headers)
    items       = json.loads(Response)['productModel']['show']['seasons']
    xbmcplugin.setContent(int(sys.argv[1])    , 'episodes')
    for item in items:
        seasonNumb  = item['seasonNumber']
        title       = "Season %s"%seasonNumb
        seasonId    = item['id']
        filters     = json.dumps({"seasonId":seasonId})
        query       = urllib.quote(filters)
        Response    = cacheURL(PLAYABLE_API%query, headers)
        items       = json.loads(Response)['productModel']
        if str(items['show']['season']['pricingPlans'][0]['availability']['plus']) != "True":
            playListId  = items['playlist']['id']
            thumb       = items['show']['season']['image']['heroSliderImage'].replace('{height}', '180').replace('{width}', '320').replace('{croppingPoint}', 'mc')
            if thumb == "":
                thumb   = items['show']['season']['image']['thumbnailImage'].replace('{height}', '180').replace('{width}', '320').replace('{croppingPoint}', 'mc')
            if thumb == "":
                thumb   = items['show']['season']['image']['landscapeClean'].replace('{height}', '180').replace('{width}', '320').replace('{croppingPoint}', 'mc')
            fanart      = thumb.split('?')[0]
            aired       = items['createdDate'].split('T')[0]
            playListId  = json.dumps({'playListId':playListId, 'page':0})
            infoLabels  = {"mediatype":"episode","title":title, "TVShowTitle":title}
            infoArt     = {"thumb":thumb,"poster":thumb,"fanart":fanart,"icon":ICON,"logo":ICON}
            addDir(title, playListId, 5, infoArt, infoLabels )
    xbmc.executebuiltin('Container.SetSortMethod(23)')

def getEpisodesFromPage(playListId,page):
    log('getEpisodesFromPage')
    playoutURL  = 'https://api2.shahid.net/proxy/v2/playout/url/%s'
    headers     = {'User-Agent': USER_AGENT}
    filters     = json.dumps({"playListId":playListId,"pageNumber":page,"pageSize":30,"sorts":[{"order":"ASC","type":"SORTDATE"}]})
    query       = urllib.quote(filters)
    Response    = cacheURL(PLAYLIST_API%query, headers)
    items       = json.loads(Response)['productList']
    xbmcplugin.setContent(int(sys.argv[1])    , 'episodes')
    hasMore     = str(items['hasMore'])
    for item in items['products']:
        ide         = item['id']
        showTitle   = item['show']['title']
        title       = item['title']
        thumb       = item['image']['thumbnailImage'].replace('{height}', '180').replace('{width}', '320').replace('{croppingPoint}', 'mc')
        episodeNumb = item['number']
        seasonNumb  = item['show']['season']['seasonNumber']
        duration    = item['duration']
        aired       = str(item['createdDate'].split('T')[0])
        urlp        = str(ide)
        seinfo      = ('S' + ('0' if int(seasonNumb) < 10 else '') + str(seasonNumb) + 'E' + ('0' if int(episodeNumb) < 10 else '') + str(episodeNumb))
        infoLabels  = {"mediatype":"episode","title":showTitle.encode('utf-8','ignore'), "aired":aired, "duration":duration, "TVShowTitle":title, "season":seasonNumb, "episode":episodeNumb}
        infoArt     = {"thumb":thumb,"poster":thumb,"fanart":FANART,"icon":ICON,"logo":ICON}
        addLink(title, urlp, 9, infoLabels, infoArt, len(items))
    return hasMore


def getEpisodes(playListId):
    log('getEpisodes')
    items       = json.loads(playListId)
    playListId  = items['playListId']
    page        = items['page']
    hasMore     = "True"
    while hasMore == "True":
        hasMore = getEpisodesFromPage(playListId,page)
        page    = page+1
    xbmc.executebuiltin('Container.SetSortMethod(23)')
