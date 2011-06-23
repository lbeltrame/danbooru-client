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

from xml.etree import ElementTree

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
import PyKDE4.kdecore as kdecore
from PyKDE4.kio import KIO

import containers
import utils

POST_URL = "post/index.xml"
TAG_URL = "tag/index.xml"
POOL_URL = "pool/index.xml"
ARTIST_URL = "pool/index.xml"
POOL_DATA_URL = "pool/show.xml"
MAX_RATINGS = dict(Safe=("Safe"), Questionable=("Safe", "Questionable"),
                   Explicit=("Safe", "Questionable", "Explicit"))

class DanbooruService(QtCore.QObject):

    """A class which provides a wrapper around Danbooru's RESTful API.

    """

    postRetrieved = QtCore.pyqtSignal(containers.DanbooruPost)
    postDownloadFinished = QtCore.pyqtSignal()
    tagRetrieved = QtCore.pyQtSignal(containers.DanbooruTag)

    def __init__(self, board_url, username=None, password=None, cache=None,
                 parent=None):

        super(DanbooruService, self).__init__(parent)

        self.url = board_url
        self.username = username
        self.password = password
        self.tag_blacklist = None
        self.cache = cache
        self.__data = None

    def __slot_process_post_list(self, job):

        """Slot called from :meth:`get_post_list`."""

        if job.error():
            return

        job_data = job.data()
        self.__data = set()

        parsed_data = ElementTree.XML(unicode(job_data.data()))
        decoded_data = parsed_data.getiterator("post")

        allowed_rating = job.property("ratings").toPyObject()

        if allowed_rating is not None:
            allowed_ratings = MAX_RATINGS[allowed_rating]
        else:
            allowed_ratings = None

        blacklisted_tags = job.property("blacklisted_tags").toPyObject()

        for item in decoded_data:
            item = containers.DanbooruPost(item)

            if blacklisted_tags is not None and blacklisted_tags:
                if any((tag in blacklisted_tags for tag in item.tags)):
                    continue

            # Same for ratings
            if (allowed_ratings is not None
                and item.rating not in allowed_ratings):
                continue
            self.__data.add(item)
            self.download_thumbnail(item)

            #FIXME: Add a download completed signal

    def __slot_download_thumbnail(self, job):

        """Slot called from :meth:`download_thumbnail`."""

        img = QtGui.QPixmap()

        if job.error():
            return

        img.loadFromData(job.data())

        if self.cache is not None:
            self.cache.insert(job.url().fileName(), img)

        danbooru_item = job.property("danbooru_item").toPyObject()
        danbooru_item.pixmap = img

        self.postRetrieved.emit(danbooru_item)
        self.__data.remove(danbooru_item)

        if not self.__data:
            self.__data = None
            self.postDownloadFinished.emit()


    def download_thumbnail(self, danbooru_item):

        """Retrieve a thumbnail for a specific Danbooru item.

        KIO.storedGet is used for asyncrhonous download. Jobs are scheduled
        to prevent server overload.

        :param danbooru_item: An instance of
                              :class:`DanbooruItem <danbooru.api.containers.DanbooruItem>`

        """

        image_url = kdecore.KUrl(danbooru_item.preview_url)
        flags = KIO.JobFlags(KIO.HideProgressInfo)

        pixmap = QtGui.QPixmap()
        name = image_url.fileName()

        # No need to download if in cache

        if self.cache is not None:
            if self.cache.find(name, pixmap):
                danbooru_item.pixmap = pixmap
                self.postRetrieved.emit(danbooru_item)
                return

        job = KIO.storedGet(image_url, KIO.NoReload, flags)
        job.setProperty("danbooru_item", QtCore.QVariant(danbooru_item))

        # Schedule: we don't want to overload servers
        KIO.Scheduler.scheduleJob(job)
        job.result.connect(self.__slot_download_thumbnail)


    def get_post_list(self, page=0, tags=None, limit=100, rating="Safe",
                      blacklist=None):

        """
        Retrieve posts from the Danbooru board.

        There is a fixed limit of 100 posts a time, imposed by the Danbooru
        API: larger numbers are ignored. The limitation can be worked around by
        specifying the "page" to view, like in the web version.

        If the *tags* parameter is set, only posts with these tags will be
        retrieved. Likewise, setting *blacklist* will skip posts whose tags
        are contained in such a blacklist.

        Ratings can be controlled with the *rating* parameter.

        :param page: The page to view (default: 0)
        :param tags: A list of tags to include (if None, use all tags)
        :param limit: The maximum number of items to retrieve (up to 100)
        :param rating: The maximum allowed rating for items, between "Safe",
                       "Questionable", and "Explicit".
        :param blacklist: A blacklist of tags

        """

        if limit > 100:
            limit = 100

        if tags is None:
            tags = ""
        else:
            tags = "+".join(tags)

        parameters = dict(tags=tags, limit=limit)

        if page is not None:
            parameters["page"] = page

        request_url = utils.danbooru_request_url(self.url, POST_URL,
                                                 parameters)

        request_url = kdecore.KUrl(self.url)
        request_url.addPath(POST_URL)
        request_url.addQueryItem("page", str(page))
        request_url.addQueryItem("limit", str(limit))

        job = KIO.storedGet(request_url, KIO.NoReload,
                            KIO.HideProgressInfo)

        job.setProperty("ratings", QtCore.QVariant(rating))
        job.setProperty("blacklisted_tags", QtCore.QVariant(blacklist))

        job.result.connect(self.__slot_process_post_list)

    def get_tag_list(self, page=0):
        pass

    def get_pool_list(self):
        pass

    def get_image(self, image_url):
        pass
