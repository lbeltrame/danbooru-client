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

__all__ = ["DanbooruService"]

import PyQt4.QtCore as QtCore
import PyKDE4.kdecore as kdecore
from PyKDE4.kio import KIO

import containers
import utils

POST_URL = "post/index.xml"
TAG_URL = "tag/index.xml"
POOL_URL = "pool/index.xml"
ARTIST_URL = "pool/index.xml"
POOL_DATA_URL = "pool/show.xml"


class DanbooruService(QtCore.QObject):

    postRetrieved = QtCore.pyqtSignal(containers.DanbooruPost)

    def __init__(self, board_url, username=None, password=None, parent=None):

        super(DanbooruService, self).__init__(parent)

        self.url = board_url
        self.username = username
        self.password = password
        self.tag_blacklist = None

    def __process_post_list(self, job):

        pass

    def get_post_list(self, page=0, tags=None, limit=100, rating="Safe"):

        if limit > 100:
            limit = 100

        if tags is None:
            tags = ""
        else:
            tags = "+".join(tags)

        parameters = dict(tags=tags, limit=limit)

        if page is not None:
            parameters["page"] = page

        request_url = utils.danbooru_request_url(POST_URL, parameters)

        job = KIO.storedGet(KUrl(request_url), KIO.NoReload,
                            KIO.HideProgressInfo)

        job.result.connect(self.__process_post_list)

    def get_tag_list(self, page=0):
        pass

    def get_thumbnails(self, post_list):
        pass

    def get_image(self, image_url):
        pass
