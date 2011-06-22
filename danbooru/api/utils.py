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

import urllib
import urlparse


def danbooru_request_url(board_url, api_url, parameters=None):

    """Create an appropriately-encoded Danbooru URL.

    The processing follows the "normal" way of encoding URLs, minus
    for the plus sign("+") which is kept literal as otherwise it wouldn't be
    understood by the Danbooru API.

    :param board_url: The base URL for generation
    :param api_url: The specific API path
    :param parameters: a dictionary holding the parameters to be added

    :return: A properly encoded Danbooru URL

    """

    if parameters:
        url_parameters = urllib.urlencode(parameters)
        # Danbooru doesn't want HTML-encoded pluses
        url_parameters = urllib.unquote(url_parameters)
        url_parameters = "?" + url_parameters

    request_url = urlparse.urljoin(board_url, api_url)

    if parameters:
        request_url = urlparse.urljoin(request_url, url_parameters)

    return request_url