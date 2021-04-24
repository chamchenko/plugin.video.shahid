# -*- coding: utf-8 -*-
# Copyright: (c) 2016, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.shahid

from __future__ import unicode_literals
from codequick import Script
import urlquick

@Script.register
def clear_cache(plugin):
    # Clear urlquick cache
    urlquick.cache_cleanup(-1)
    Script.notify(
                    'Info',
                    'Cache Cleared Successfully',
                    display_time=5000,
                    sound=True
                 )
