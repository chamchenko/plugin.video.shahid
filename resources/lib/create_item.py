import sys, xbmcgui, xbmcplugin, urllib
from vars import *
from tools import log
def addLink(name, u, mode, infoList=False, infoArt=False, total=0, infoCast=False):
    name = name.encode("utf-8")
    log('addLink, name = ' + name)
    liz=xbmcgui.ListItem(name)
    liz.setProperty('IsPlayable', 'true')
    if infoList == False: liz.setInfo(type="Video", infoLabels={"mediatype":"video","label":name,"title":name})
    else: liz.setInfo(type="Video", infoLabels=infoList)
    if infoArt == False: liz.setArt({'thumb':ICON,'fanart':FANART})
    else: liz.setArt(infoArt)
    if infoCast != False: liz.setCast(infoCast)
    u=sys.argv[0]+"?url="+urllib.quote_plus(u)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    #is_folder = False
    #return (u, liz, is_folder)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,totalItems=total)


def addDir(name, u, mode=None, infoArt=False, infoList=False, total=0, infoCast=False):
    name = name.encode("utf-8")
    log('addDir, name = ' + name)
    liz=xbmcgui.ListItem(name)
    liz.setProperty('IsPlayable', 'false')
    if infoList == False: liz.setInfo(type="Video", infoLabels={"mediatype":"video","label":name,"title":name})
    else: liz.setInfo(type="Video", infoLabels=infoList)
    if infoArt == False: liz.setArt({'thumb':ICON,'fanart':FANART})
    else: liz.setArt(infoArt)
    if infoCast != False: liz.setCast(infoCast)
    u=sys.argv[0]+"?url="+urllib.quote_plus(u)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True,totalItems=total)
