# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid


import urlquick
import json
import xbmcvfs
import os

from codequick import Script
from codequick.utils import keyboard
from codequick.utils import ensure_native_str
from .vars import *
from .tools import get_headers
from .tools import get_filter

try:
    from xbmcvfs import translatePath
except ImportError:
    from xbmc import translatePath as translatepath
    def translatePath(path):
        return translatepath(path).decode('utf-8')


@Script.register
def clear_cache(plugin):
    # Clear urlquick cache
    urlquick.cache_cleanup(-1)
    Script.notify(
                    plugin.localize(30208),
                    plugin.localize(30203),
                    display_time=5000,
                    sound=True
                 )


@Script.register
def add_to_my_list(plugin, itemID, profile_id, profile_type, is_master):
    plugin.log('add_to_my_list', lvl=plugin.DEBUG)
    headers = get_headers(profile_id, profile_type, is_master)
    add_url = ADD_TO_LIST_URL + str(itemID)
    plugin.log('Fetching url: %s' % add_url, lvl=plugin.DEBUG)
    Response = urlquick.post(
                                add_url,
                                headers=headers,
                                max_age=0
                           ).json()
    success = Response['success']
    if success:
        plugin.notify(
                        plugin.localize(30208),
                        plugin.localize(30204),
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

def CONTEXT_MENU(item, itemID, profile_id, profile_type, is_master):
    item.context.script(
                            add_to_my_list,
                            Script.localize(30212),
                            itemID=itemID,
                            profile_id=profile_id,
                            profile_type=profile_type,
                            is_master=is_master
                       )
    return

def CONTEXT_MENU2(item, itemID, title, productType):
    item.context.script(
                            export_to_library,
                            Script.localize(30211),
                            title=title,
                            itemID=itemID,
                            productType=productType
                       )
    return

def check_folder_path(path):
    end = ''
    if '/' in path and not path.endswith('/'):
        end = '/'
    if '\\' in path and not path.endswith('\\'):
        end = '\\'
    return path + end

def folder_exists(path):
    return xbmcvfs.exists(check_folder_path(path))

def create_folder(path):
    if not folder_exists(path):
        xbmcvfs.mkdirs(path)


def save_file(path, filename, content, mode='wb'):
    if filename == '':
        file_path = path
    else:
        file_path = os.path.join(path, filename)
    file_handle = xbmcvfs.File(translatePath(file_path), mode)
    try:
        file_handle.write(bytearray(content))
    except:
        file_handle.write(bytearray(content.encode('utf-8')))

def create_cache_file():
    if not xbmcvfs.exists('special://profile/addon_data/plugin.video.shahid/exported.json'):
        content = '{"movies": {},"tvshows": {}}'
        file_handle = xbmcvfs.File(translatePath('special://profile/addon_data/plugin.video.shahid/exported.json'), 'wb')
        file_handle.write(bytearray(ensure_native_str(content, 'utf-8')))



@Script.register
def export_to_library(plugin,title, itemID, productType):
    strmcontent = """#EXTM3U
#EXTINF:-1,%s
%s"""
    cache_file = 'special://profile/addon_data/plugin.video.shahid/exported.json'
    create_cache_file()
    cache_data = xbmcvfs.File(translatePath(cache_file)).read()
    exported_json = json.loads(cache_data)
    base_path = plugin.setting.get_string('customlibraryfolder')
    movies_path = os.path.join(base_path, 'movies')
    tvshows_path= os.path.join(base_path, 'tvshows')
    baseurl = 'plugin://plugin.video.shahid/resources/lib/playback_resolver/play_video/?streamId=%s'
    create_folder(movies_path)
    create_folder(tvshows_path)
    if productType == 'MOVIE':
        exported_json['movies'][itemID] = title
        filename = '%s.strm' % title
        url = baseurl % itemID
        content = strmcontent % (title,url)
        save_file(movies_path, filename, ensure_native_str(content, 'utf-8'), mode='wb')
    if productType == 'SHOW':
        exported_json['tvshows'][itemID] = title
        show_path = os.path.join(tvshows_path, title)
        create_folder(show_path)
        headers = get_headers()
        params = get_filter(requesttype='request', showId=itemID)
        json_parser = urlquick.get(PLAYABLE_API, params=params, headers=headers).json()
        for season in json_parser['productModel']['show']['seasons']:
            seasonNumb = int(season['seasonNumber'])
            season_path = os.path.join(show_path, ('S' + ('0' if seasonNumb < 10 else '') + str(seasonNumb)))
            seasonId = season['id']
            params =  get_filter(requesttype='request', seasonId=seasonId)
            season_items = urlquick.get(PLAYABLE_API, params=params, headers=headers).json()
            playListId = season_items['productModel']['playlist']['id']
            count = season_items['productModel']['playlist']['count']
            if count == 0:
                continue
            create_folder(season_path)
            hasMore = "True"
            page=0
            while hasMore == "True":
                page = str(page)
                params = get_filter(
                                        requesttype='request',
                                        playListId=playListId,
                                        pageNumber=page,
                                        pageSize=30
                                   )
                Response = urlquick.get(PLAYLIST_API, params=params, headers=headers).json()
                items = Response['productList']
                hasMore = str(items['hasMore'])
                for item in items['products']:
                    episodeNumb = item['number']
                    streamId = item['id']
                    seinfo = ('S' + ('0' if seasonNumb < 10 else '') + str(seasonNumb) + 'E' + ('0' if episodeNumb < 10 else '') + str(episodeNumb))
                    eptitle = '%s %s%s' % (
                                            title,
                                            ('S' + ('0' if seasonNumb < 10 else '') + str(seasonNumb)),
                                            ('E' + ('0' if episodeNumb < 10 else '') + str(episodeNumb))
                                          )
                    filename = '%s.strm' % eptitle
                    check = xbmcvfs.exists(os.path.join(season_path,filename))

                    if check:
                        continue
                    url = baseurl % streamId
                    content = strmcontent % (eptitle, url)
                    save_file(season_path, filename, ensure_native_str(content, 'utf-8'), mode='wb')
                page = int(page) + 1
    save_file(cache_file, '', ensure_native_str(json.dumps(exported_json), 'utf-8'), mode='wb')
    plugin.notify(
                    plugin.localize(30208),
                    plugin.localize(30210),
                    display_time=5000,
                    sound=True
                 )
