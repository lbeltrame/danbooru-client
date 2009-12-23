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

from PyQt4.QtCore import QObject, SIGNAL, pyqtSignal
from PyQt4.QtGui import QPixmap
from PyKDE4.kdecore import KUrl
from PyKDE4.kio import KIO

import hashes

"""Module that provides a wrapper for Danbooru API calls. Items are stored as
DanbooruItems, which enable easy extraction of information using attributes. To
store lists of individual DanbooruItems, a special class called DanbooruList has
also been provided."""

class Danbooru(QObject):

    """Class which provides a PyKDE4 wrapper to the Danbooru API. It has
    functions to retrieve posts, images, tags and more. It is a subclass of
    QObject and makes use of KDE's KIO to handle network operations
    asynchronously.
    This class provides two custom signals: dataDownloaded (for data that has
    been downloaded, forexample an image) and dataReady (when other network
    operations are complete)."""

    _POST_URL = "post/index.json"
    _TAG_URL = "tag/index.json"
    _POOL_URL = "pool/index.json"
    _ARTIST_URL = "pool/index.json"
    _POOL_INFO_URL = "pool/get.json"

    _RATINGS = ["Safe", "Questionable", "Explicit"]

    dataDownloaded = pyqtSignal(KUrl, QPixmap)
    dataReady = pyqtSignal()

    def __init__(self, api_url, login=None, password=None, parent=None,
                cache=None):

        super(Danbooru, self).__init__(parent)
        result = self.validate_url(api_url)

        if not result:
            raise IOError, "The given URL does not exist."

        self.url = api_url
        self.data = None
        self.cache = cache
        self.__login = login if login else None
        self.__pwhash = hashes.generate_hash(password) if password else None
        self.__rating = None
        # These are needed to update previous results
        self.__limit = None
        self.__tags = None

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

    def _allowed_ratings(self):

        """Function to return the allowed ratings for fetching. If no ratings have
        been defined, it returns all ratings."""

        if not self.__rating:
            return ["Safe", "Questionable", "Explicit"]
        else:
            return self.__rating

    def _set_allowed_ratings(self, rating):

        """Function to set the maximum allowed rating for fetching. Supplied
        ratings that are invalid are silently ignored."""

        if rating not in self._RATINGS:
            return

        if rating == "Safe":
            self.__rating = ["Safe"]
        elif rating == "Questionable":
            self.__rating = ["Safe", "Questionable"]
        elif rating == "Explicit":
            self.__rating = ["Safe", "Questionable", "Explicit"]


    def validate_url(self, url):

        "Validates the input URL and returns the result (True/False)"

        ok = self.__http_exists(url)
        return ok

    def process_tags(self, tags):

        "Method that validates and processes tags."

        pass

    def get_post_list(self, limit=5, tags=None, page=None):

        """Method to get posts with specific tags and limits. There is a hardcoded
        limit of 100 posts in Danbooru, so limits > 100 will be ignored.
        If present, tags must be supplied as a list. Data are stored as a list
        of DanbooruItems."""

        if limit > 100:
            limit = 100

        self.__limit = limit if not self.__limit else self.__limit
        self.__tags = tags if not self.__tags else self.__tags

        limit_parameter = "limit=%d" % limit
        if tags:
            tags = "+".join(tags)
        else:
            tags = ""

        parameters = dict(tags=tags, limit=limit)

        if page:
            parameters["page"] = page

        url_parameters = urllib.urlencode(parameters)
        # Danbooru doesn't want HTML-encoded pluses
        url_parameters = urllib.unquote(url_parameters)

        url_parameters = "?" + url_parameters
        request_url = urlparse.urljoin(self.url, self._POST_URL)
        request_url = urlparse.urljoin(request_url, url_parameters)

        job = KIO.storedGet(KUrl(request_url), KIO.NoReload,
                            KIO.HideProgressInfo)

        self.connect(job, SIGNAL("result (KJob *)"), self.process_post_list)

    def update(self, page=None):

        """Updates previously added results. This should be used to get the next
        page of the same batch."""

        if not self.__limit and not self.__tags:
            return

        self.get_post_list(limit=self.__limit, tags=self.__tags, page=page)

    def process_post_list(self, job):

        """Collects the data from the job and loads it into an object that can
        be read by the JSON parser. Then each element of the data is converted
        into a DanbooruItem and stored in a DanbooruList. Prior to inserting the
        items in the list, they are checked for rating."""

        if job.error():
            self.data = None
            return

        job_data = job.data()
        decoded_data = json.loads(unicode(job_data.data()))

        self.data = DanbooruList()

        allowed_ratings = self.selected_ratings

        for item in decoded_data:
            item = DanbooruItem(item)

            if item.rating in allowed_ratings:
                self.data.append(item)

        self.dataReady.emit()

    def get_tag_list(self):

        "Method to retrieve a list of tags."

        pass

    def get_pool_list(self):

        "Method to retrieve a list of pool IDs."

        pass

    def get_artist_list(self):

        "Method to retrieve a list of artists."

        pass

    def get_image(self, image_url, verbose=False, wait=2):

        """Retrieves a picture (full or thumbnail) for a specific URL.
        It uses KIO.storedGet to download it asynchronously, but setting a
        KIO.Scheduler to queue the jobs. Once the job has finished, it will emit
        the dataDownloaded(KUrl, QPixmap) signal.
        """

        # Not less than two seconds. We want to play nice.
        if wait < 2:
            wait = 2

        image_url = KUrl(image_url)
        flags = KIO.JobFlags(KIO.HideProgressInfo)

        pixmap = QPixmap()
        name = image_url.fileName()

        # No need to download if in cache

        if self.cache is not None:
            if self.cache.find(name, pixmap):
                self.dataDownloaded.emit(image_url, pixmap)
                return

        job = KIO.storedGet(image_url, KIO.NoReload, flags)
        # Schedule: we don't want to overload servers
        KIO.Scheduler.scheduleJob(job)

        self.connect(job, SIGNAL("result (KJob *)"), self.job_download)

    def job_download(self, job):

        """Slot callled from get_image. Loads the image in a QPixmap and inserts
        it into the thumbnail cache, if present. then it emits the
        dataDownloaded signal, which carries the URL of the image and the pixmap
        itself."""

        img = QPixmap()
        name = job.url()
        if job.error():
            job.ui().showErrorMessage()
            return

        img.loadFromData(job.data())

        if self.cache is not None:
            self.cache.insert(job.url().fileName(), img)

        self.dataDownloaded.emit(name, img)

    # Properties

    selected_ratings = property(_allowed_ratings, _set_allowed_ratings)

class DanbooruList(object):

    """Specialized container for Danbooru items. It contains a lists of
    DanbooruItems and at the same time it also stores thumbnail and full image
    urls. The dictionaries are used to keep indices to the internal list, and
    they're used to return the corresponding item (standard index access is also
    possible)."""

    def __init__(self):

        self.__data = list()
        self.__full_url = dict()
        self.__thumbnail_url = dict()

    def __str__(self):
        return str(self.__data)

    def __getitem__(self, key):

        """Keys are first checked in the two internal dictionaries, then if no
        match is found, they're used as indices for the internal list. In case
        of no match, or exception, None is returned."""

        if key in self.__full_url:
            index = self.__full_url[key]
            return self.__data[index]
        elif key in self.__thumbnail_url:
            index = self.__thumbnail_url[key]
            return self.__data[index]
        else:
            # So we can get by index as well 
            try:
                return self.__data[key]
            except ( TypeError, IndexError ):
                return

    def __contains__(self, key):

        if key in self.__full_url:
            return True
        elif key in self.__thumbnail_url:
            return True
        elif key in self.__data:
            return True
        else:
            return False

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        for item in self.__data:
            yield item

    def append(self, item):

        """Append logic similar to lists, but which also includes creating the
        keys for the dictionaries."""

        assert isinstance(item, DanbooruItem)

        last_index = len(self.__data)  if self.__data else 0
        self.__data.append(item)
        self.__full_url[item.full_url] = last_index
        self.__thumbnail_url[item.thumbnail_url] = last_index

class DanbooruItem(object):

    """Class to store information about a Danbooru item retrieved via the REST
    API. The various JSON-encoded fields can be accessed through properties."""

    def __init__(self, json_data):

        self.__data = json_data

    def __getattr__(self, name):

        print self.__data.keys()

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

    @property
    def rating(self):

        ratings = dict(s="Safe", q="Questionable", e="Explicit")

        return ratings[self.__data["rating"]]

