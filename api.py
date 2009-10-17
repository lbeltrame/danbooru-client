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
import urllib
import httplib
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import QPixmap
from PyKDE4.kdecore import *
from PyKDE4.kio import KIO

import hashes

"""Module that provides a wrapper for Danbooru API calls. Items are stored as
DanbooruItems, which enable easy extraction of information using attributes."""

class Danbooru(object):

    "Class which provides a PyKDE4 wrapper to the Danbooru API."

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

    def __http_exists(self, url):

        """Check whether a given URL exists. Returns True if found, False if
        otherwise. Adapted from http://code.activestate.com/recipes/286225/"""

        host, path = urlparse.urlsplit(url)[1:3]
        try:
            ## Make HTTPConnection Object
            connection = httplib.HTTPConnection(host)
            connection.request("HEAD", path)
            ## Grab HTTPResponse Object
            responseOb = connection.getresponse()

            if responseOb.status == 200:
                return True
            else:
                return False

        except httplib.HTTPException, e:
            return False

    def validate_url(self, url):

        "Validates the input URL and returns the result (True/False)"

        ok = self.__http_exists(url)
        return ok

    def process_tags(self, tags):

        "Method that validates and processes tags."

        pass

    def get_post_list(self, limit=5, tags=None):

        """Method to get posts with specific tags and limits. There is a hardcoded
        limit of 100 posts in Danbooru, so limits > 100 will be ignored.
        If present, tags must be supplied as a list. Data are stored as a list
        of DanbooruItems."""

        if limit > 100:
            limit = 100

        limit_parameter = "limit=%d" % limit
        if tags:
            tags = "+".join(tags)
        else:
            tags = ""

        parameters = dict(tags=tags, limit=limit)
        url_parameters = urllib.urlencode(parameters)
        # Danbooru doesn't want HTML-encoded pluses
        url_parameters = urllib.unquote(url_parameters)

        url_parameters = "?" + url_parameters
        request_url = urlparse.urljoin(self.url, self._POST_URL)
        request_url = urlparse.urljoin(request_url, url_parameters)
        print request_url
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

    """Class to store information about a Danbooru item retrieved via the REST
    API. The various JSON-encoded fields can be accessed through properties."""

    def __init__(self, json_data):

        self.__data = json_data

    def __getattr__(self, name):

        if name not in self.__data:
            return None
        else:
            return self.__data[name]

    @property
    def thumbnail_url(self):

        "URL of the thumbnail"

        return self.__data["preview_url"]

    @property
    def full_url(self):

        "URL of the full image"

        return self.__data["file_url"]

    @property
    def size(self):

        "Size of the full image"

        return self.__data["file_size"]

    @property
    def tags(self):

        "Tags associated to the post. Returned as list."

        tags = self.__data["tags"]
        tags = tags.split(" ")
        return tags

    @property
    def width(self):

        "Width of the full image"

        return self.__data["width"]

    @property
    def height(self):

        "Height of the full image"

        return self.__data["height"]

    @property
    def post_id(self):

        "Danbooru unique post ID"

        return self.__data["id"]

    @property
    def source(self):

        "Original source for the image, if applicable."

        return self.__data["source"]


