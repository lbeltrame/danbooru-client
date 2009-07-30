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
from PyQt4.QtGui import QPixmap

from PyKDE4.kdecore import KUrl, KTemporaryFile
from PyKDE4.kio import KIO

"Module that provides a wrapper for Danbooru API calls."

class Danbooru(object):

    "Class to provide a Python wrapper to the Danbooru API."

    POST_URL = "post/index.json"
    TAG_URL = "tag/index.json"

    def __init__(self, api_url, cache=None):
        
        if not api_url.endswith("/"):
            api_url = api_url + "/"

        self.url = api_url
        self.cache = cache

        check_job = KIO.stat(KUrl(self.url), KIO.HideProgressInfo)
        if not KIO.NetAccess.synchronousRun(check_job, None):
            print "There was an error retrieving the API url!"

    def get_post_list(self, limit=5, tags=None):
        
        limit_parameter = "limit=%d" % limit
        request_url = ''.join((self.url, self.POST_URL, "?",
                                    limit_parameter))
        data = None
        tempfile = QString()
        if KIO.NetAccess.download(KUrl(request_url), tempfile, None):
            api_response = open(tempfile)
            data = json.load(api_response)
            KIO.NetAccess.removeTempFile(tempfile)
        else:
            pass
            #FIXME: Process errors
                
        return data
    
    def get_thumbnail_urls(self, json_data):

        urls = list()
        for item in json_data:
            preview_url = KUrl(item["preview_url"])
            urls.append(preview_url)

        return urls

    def get_picture_url(self, picture_index, json_data):
        
        picture_data = json_data[picture_index]
        picture_url = KUrl(picture_data["file_url"])

        return picture_url
        
    def retrieve_thumbnail(self, url):
        
        name = url.fileName()
        pixmap = QPixmap()

        if not self.cache.find(name, pixmap):
            tempfile = KTemporaryFile()

            if tempfile.open():
                flags = KIO.JobFlags(KIO.Overwrite | KIO.HideProgressInfo)
                job = KIO.file_copy(KUrl(url), KUrl(tempfile.fileName()),
                                    None, flags)
                
                if KIO.NetAccess.synchronousRun(job, self):
                    pixmap = QPixmap.load(job.destUrl().path())
                    KIO.NetAccess.removeTempFile(tempfile.fileName())
                    return pixmap, name
        else:
            return pixmap, name

