# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid



from codequick import run
from codequick import Route
from codequick import Listitem

from codequick.utils import bold
from codequick.utils import keyboard
from random import choice
from .tools import *
from .vars import *
from .movies import CATEGORIES_M
from .movies import BROWSE_MOVIES
from .tvshows import CATEGORIES
from .tvshows import BROWSE_TVSHOWS
from .live_tv import LIVE_TV
from .mixed_content import SEARCH_CONTENT
from .mixed_content import MY_LIST



@Route.register
def root(plugin):
    headers = get_headers()
    if EMAIL and PASSWORD:
        profiles_data = urlquick.get(PROFILES_URL, headers=headers, max_age=0).json()
        pin = profiles_data['pinCode']
    else:
        pin = None
        avatar_k = urlquick.get(AVATAR_URL+'kidsDefault').json()['avatars'][0]['url']
        id_k = ''.join(choice('0123456789abcdef-') for n in range(36)).encode('utf-8')
        avatar_a = urlquick.get(AVATAR_URL+'adultDefault').json()['avatars'][0]['url']
        id_a = ''.join(choice('0123456789abcdef-') for n in range(36)).encode('utf-8')
        profiles_data = {
                            'profiles':[
                                            {
                                                'type':'ADULT',
                                                'default': True,
                                                'id': id_a,
                                                'name': plugin.localize(30302),
                                                "avatar": {"url": formatimg(avatar_a, 'icon')}
                                            },
                                            {
                                                'type':'KID',
                                                'default': True,
                                                'name': plugin.localize(30301),
                                                'id': id_k,
                                                "avatar": {"url": formatimg(avatar_k, 'icon')}
                                            }
                                       ]
                        }
    for profile in profiles_data['profiles']:
        profile_type = profile['type']
        if MODE_KIDS and profile_type != 'KID' and (not EMAIL or not PASSWORD):
            continue
        profile_id = profile['id']
        profile_name = profile['name'].title()
        is_master = profile['default']
        avatar = formatimg(profile['avatar']['url'], 'icon')
        yield Listitem.from_dict(
                                    sub_menu,
                                    bold(profile_name),
                                    art={"thumb": avatar},
                                    params={
                                                'profile_id': profile_id,
                                                'profile_type': profile_type,
                                                'pin': pin,
                                                'is_master': is_master
                                           }
                                )


@Route.register
def sub_menu(plugin, profile_id, profile_type, is_master, pin):
    if profile_type == 'KID':
        plugin.log('Creating Kids Menu', lvl=plugin.WARNING)
        # get kids user id
       
        yield Listitem.from_dict(
                                    LIVE_TV,
                                    bold(plugin.localize(30101)),
                                    params={
                                                'profile_id': profile_id,
                                                'profile_type': profile_type,
                                                'is_master': is_master
                                           }
                                )
        yield Listitem.from_dict(
                                    BROWSE_TVSHOWS,
                                    bold(plugin.localize(30102)),
                                    params={
                                                "genreId":"",
                                                "productSubType": "SERIES",
                                                "page": 0,
                                                'profile_id': profile_id,
                                                'profile_type': profile_type,
                                                'is_master': is_master
                                           }
                                )
        yield Listitem.from_dict(
                                    BROWSE_TVSHOWS,
                                    bold(plugin.localize(30103)),
                                    params={
                                                "genreId":"",
                                                "productSubType": "PROGRAM",
                                                "page": 0,
                                                'profile_id': profile_id,
                                                'profile_type': profile_type,
                                                'is_master': is_master
                                           }
                                )
        yield Listitem.from_dict(
                                    BROWSE_MOVIES,
                                    bold(plugin.localize(30104)),
                                    params={
                                                'genreId':'',
                                                'page': 0,
                                                'profile_id': profile_id,
                                                'profile_type': profile_type,
                                                'is_master': is_master
                                           }
                                )
        yield Listitem.search(
                                SEARCH_CONTENT,
                                profile_id=profile_id,
                                profile_type=profile_type,
                                is_master=is_master
                             )
    else:
        if MODE_KIDS:
            user_input = keyboard(
                                    "Enter your PIN Code",
                                    "",
                                    True
                                 )
            if user_input != pin:
                plugin.notify(
                                plugin.localize(30202),
                                plugin.localize(30201),
                                display_time=5000,
                                sound=True
                             )
                yield False
                return
        plugin.log('Creating Main Menu', lvl=plugin.WARNING)
        yield Listitem.from_dict(
                                    LIVE_TV,
                                    bold(plugin.localize(30101)),
                                    params={
                                                'profile_id': profile_id,
                                                'profile_type': profile_type,
                                                'is_master': is_master
                                           }
                                )
        yield Listitem.from_dict(
                                    CATEGORIES,
                                    bold(plugin.localize(30102)),
                                    params={
                                                "productSubType": "SERIES",
                                                'profile_id': profile_id,
                                                'profile_type': profile_type,
                                                'is_master': is_master
                                           }
                                )
        yield Listitem.from_dict(
                                    CATEGORIES,
                                    bold(plugin.localize(30103)),
                                    params={
                                                "productSubType": "PROGRAM",
                                                'profile_id': profile_id,
                                                'profile_type': profile_type,
                                                'is_master': is_master
                                           }
                                )
        yield Listitem.from_dict(
                                    CATEGORIES_M,
                                    bold(plugin.localize(30104)),
                                    params={
                                                'profile_id': profile_id,
                                                'profile_type': profile_type,
                                                'is_master': is_master
                                           }
                                )
        if EMAIL and PASSWORD:
            yield Listitem.from_dict(
                                        MY_LIST,
                                        bold(plugin.localize(30105)),
                                        params={
                                                'profile_id': profile_id,
                                                'profile_type': profile_type,
                                                'is_master': is_master
                                               }
                                    )
        yield Listitem.search(
                                SEARCH_CONTENT,
                                profile_id=profile_id,
                                profile_type=profile_type,
                                is_master=is_master
                             )
