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

from PyQt4.QtCore import QString
from PyQt4.QtGui import QImage
from PyKDE4.kdecore import KUrl, KTemporaryFile
from PyKDE4.kio import KIO

"Module that provides a wrapper for Danbooru API calls."

class Danbooru(object):

    "Class to provide a PyKDE4 wrapper to the Danbooru API."

    _POST_URL = "post/index.json"
    _TAG_URL = "tag/index.json"
    _POOL_URL = "pool/index.json"
    _ARTIST_URL = "pool/index.json"

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
        limit of 100 posts in Danbooru, so limits > 100 will be ignored.
        If present, tags must be supplied as a list."""
        
        if limit > 100:
            limit = 100

        limit_parameter = "limit=%d" % limit
        if tags:
            tags = "+".join(tags)
        else:
            tags = ""
        parameters = "?"+"&".join((tags, limit_parameter))
        request_url = urlparse.urljoin(self.url, self._POST_URL)

        request_url = request_url.rstrip("&") # Remove last &

        tempfile = QString()
        if KIO.NetAccess.download(KUrl(request_url), tempfile, None):
            api_response = open(tempfile)
            self.data = json.load(api_response)
            KIO.NetAccess.removeTempFile(tempfile)
        else:
            return False
        
        return True

    def get_tag_list(self):
        pass

    def get_pool_list(self):
        pass

    def get_artist_list(self):
        pass

    def get_thumbnail_urls(self):

        "Gets thumbnail URLs from the current data."

        if self.data is None:
            return
    
        urls = list()
        for item in self.data:
            preview_url = KUrl(item["preview_url"])
            urls.append(preview_url)

        return urls

    def get_picture_url(self, picture_index):

        "Retrieves an URL for a full picture."

        if self.data is None:
            return
        
        picture_data = self.data[picture_index]
        picture_url = KUrl(picture_data["file_url"])

        return picture_url
        
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
                                         None, flags)
        img = QImage()

        if KIO.NetAccess.synchronousRun(job, self):
            destination = job.destUrl()
            img.load(destination.path())
        
        KIO.NetAccess.removeTempFile(tempfile.fileName())

        return img
