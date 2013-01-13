#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Copyright 2011 Luca Beltrame <einar@heavensinferno.net>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License, under
#   version 2 of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the
#   Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys

import PyKDE4.kdecore as kdecore

if sys.version_info.major > 2:
    unicode = str

def danbooru_request_url(board_url, api_url, parameters=None, username=None,
                         password=None):

    """Create an appropriately-encoded Danbooru URL.

    The processing follows the "normal" way of encoding URLs, minus
    for the plus sign("+") which is kept literal as otherwise it wouldn't be
    understood by the Danbooru API.

    :param board_url: The base URL for generation
    :param api_url: The specific API path
    :param parameters: a dictionary holding the parameters to be added

    :return: A properly encoded Danbooru URL

    """

    danbooru_url = kdecore.KUrl(board_url)
    danbooru_url.addPath(api_url)

    if parameters is not None:

        if sys.version_info.major > 2:
            iterator = parameters.items()
        else:
            iterator = parameters.iteritems()

        for key, value in iterator:

            if key == "tags":
                # By adding a plus to tags, we already encoded them
                danbooru_url.addEncodedQueryItem(key, value)

            danbooru_url.addQueryItem(key, unicode(value))

    if username is not None and password is not None:
        danbooru_url.setUserName(username)
        danbooru_url.setPassword(password)

    return danbooru_url
