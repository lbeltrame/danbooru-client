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
import urlparse
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import QPixmap
from PyKDE4.kdecore import *
from PyKDE4.kio import KIO

import hashes

"Module that provides a wrapper for Danbooru API calls."

class Danbooru(object):

    "Class to provide a PyKDE4 wrapper to the Danbooru API."

    _POST_URL = "post/index.json"
    _TAG_URL = "tag/index.json"
    _POOL_URL = "pool/index.json"
    _ARTIST_URL = "pool/index.json"

    def __init__(self, api_url, login=None, password=None):

        result = self.validate_url(api_url)

        if not result:
            raise IOError, "The given URL does not exist."

        self.url = api_url
        self.data = None
        self.__login = login if login else None
        self.__pwhash = hashes.generate_hash(password) if password else None

    def validate_url(self, url):
        ok = KIO.NetAccess.exists(KUrl(url), True, None)
        return ok

    def process_tags(self, tags):

        "Method that validates and processes tags."

        pass

    def get_post_list(self, limit=5, tags=None):

        """Method to get posts with specific tags and limits. There is a hardcoded
        limit of 100 posts in Danbooru, so limits > 100 will be ignored.
        If present, tags must be supplied as a list."""

        if limit > 100:
            limit = 100

        #FIXME:Hackish! Needs a programmatic construction
        limit_parameter = "limit=%d" % limit
        if tags:
            tags = "+".join(tags)
            tags = "tags="+tags
        else:
            tags = ""
        parameters = "&".join((tags, limit_parameter))
        parameters = parameters.lstrip("&")
        parameters = "?" + parameters
        request_url = urlparse.urljoin(self.url, self._POST_URL)
        request_url = urlparse.urljoin(request_url, parameters)

        tempfile = QString()

        #FIXME: It's broken with Danbooru 1.13.x

        if KIO.NetAccess.download(KUrl(request_url), tempfile, None):
            api_response = open(tempfile)
            data = json.load(api_response)

            if "sucess" in data[0]:
                if not data[0]["success"]:
                    return False

            KIO.NetAccess.removeTempFile(tempfile)
            self.data = [DanbooruItem(item) for item in data]

        else:
            return False

        return True

    def get_tag_list(self):
        pass

    def get_pool_list(self):
        pass

    def get_artist_list(self):
        pass

    def post_info(self, post_index):

        """Returns information such as size, tags, and the like for a
        given post."""

        if self.data is None:
            return

        data = self.data[post_index]

        height = data["height"]
        width = data["width"]
        size = data["file_size"]

        return (height, width, size)

    def get_image(self, image_url, verbose=False):

        """Retrieves a picture (full or thumbnail) for a specific URL.
        Returns a QImage. If for any reason the picture isn't downloaded,
        returns a null QImage. Set verbose to true to view download progress."""

        tempfile = KTemporaryFile()
        if tempfile.open():

            if not verbose:
                flags = KIO.JobFlags(KIO.Overwrite | KIO.HideProgressInfo)
            else:
                flags = KIO.JobFlags(KIO.Overwrite)

        job = KIO.file_copy(KUrl(image_url), KUrl(tempfile.fileName()),
                                         -1, flags)
        img = QPixmap()
        name = KUrl(image_url).fileName()

        # To prevent server overloads, we can't really use async jobs
        if KIO.NetAccess.synchronousRun(job, None):
            destination = job.destUrl()
            img.load(destination.path())
            time.sleep(2)

        return img, name


class DanbooruItem(object):

    """docstring for DanbooruItem"""

    def __init__(self, json_data):

        self.__data = json_data

    def __getattr__(self, name):

        if name not in self.__data:
            return None
        else:
            return getattr(self, name)

    @property
    def thumbnail_url(self):
        return self.__data["preview_url"]

    @property
    def full_url(self):
        return self.__data["file_url"]

    @property
    def size(self):
        return self.__data["file_size"]

    @property
    def tags(self):
        tags = self.__data["tags"]
        tags = tags.split(" ")
        return tags

    @property
    def width(self):
        return self.__data["width"]

    @property
    def height(self):
        return self.__data["height"]

    @property
    def post_id(self):
        return self.__data["id"]

    @property
    def source(self):
        return self.__data["source"]


