#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Copyright 2009 Luca Beltrame <einar@heavensinferno.net>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License, version 2.
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

import json

from PyQt4.QtCore import QString
from PyKDE4.kdecore import KUrl
from PyKDE4.kio import KIO

"Module that provides a wrapper for Danbooru API calls."

class Danbooru(object):

    "Class to provide a Python wrapper to the Danbooru API."

    POST_URL = "post/index.json"
    TAG_URL = "tag/index.json"
    POOL_URL = "pool/index.json"
    ARTIST_URL = "pool/index.json"

    def __init__(self, api_url):
        
        if api_url is not None:
            ok = KIO.NetAccess.exists(KUrl(api_url),
                                      KIO.NetAccess.DestinationSide, None)
            if not ok:
                return
        else:
            return

        self.url = api_url
        self.data = None

    def process_tags(tags):

        "Method that validates and processes tags."

        pass

    def get_post_list(self, limit=5, tags=None):

        """Method to get posts with specific tags and limits. There is a hardcoded
        limit of 100 posts in Danbooru, so limits > 100 will be ignored.."""
        
        if limit > 100:
            limit = 100

        limit_parameter = "limit=%d" % limit
        request_url = ''.join((self.url, self.POST_URL, "?",
                                    limit_parameter))
        if tags:
            tags = "+".join(tags)
            request_url="&".join((request_url,tags))

        data = None
        tempfile = QString()
        if KIO.NetAccess.download(KUrl(request_url), tempfile, None):
            api_response = open(tempfile)
            self.data = json.load(api_response)
            KIO.NetAccess.removeTempFile(tempfile)
        
        return True

    def get_thumbnail_urls(self):

        if self.data is None:
            return
    
        urls = list()
        for item in self.data:
            preview_url = KUrl(item["preview_url"])
            urls.append(preview_url)

        return urls

    def get_picture_url(self, picture_index):

        if self.data is None:
            return
        
        picture_data = self.data[picture_index]
        picture_url = KUrl(picture_data["file_url"])

        return picture_url
        
    def get_picture(self, picture_url):
        pass


