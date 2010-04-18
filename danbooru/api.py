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

"""Module that provides a wrapper for Danbooru API calls. Items are stored as
DanbooruItems, which enable easy extraction of information using attributes. To
store lists of individual DanbooruItems, a special class called DanbooruPostList
has also been provided."""

import urlparse
import urllib
from xml.dom import minidom

from PyQt4.QtCore import QObject, SIGNAL, pyqtSignal
from PyQt4.QtGui import QPixmap
from PyKDE4.kdecore import KUrl
from PyKDE4.kio import KIO

import hashes


class Danbooru(QObject):

    """Class which provides a PyKDE4 wrapper to the Danbooru API. It has
    functions to retrieve posts, images, tags and more. It is a subclass of
    QObject and makes use of KDE's KIO to handle network operations
    asynchronously.

    This class provides the following custom signals:

        - dataDownloaded, for image data that has been downloaded, which
        includes the KUrl pointing to the URL of the downloaded image, and the
        QPixmap of the image itself;
        - postDataReady, when network operations are complete;
        - poolDataReady, when pool retrieval operations are complete;
        - checkCompleted, when the check for the existence of the page is
        completed, and returns a bool indicating success or not;
        - tagsRetrieved, when tags have been retrieved.

    The class also provides the selected_ratings attribute, which is used to
    filter items that are being retrieved depending on the maximum rating used
    (Safe, Questionable, or Explicit)."""

    _POST_URL = "post/index.xml"
    _TAG_URL = "tag/index.xml"
    _POOL_URL = "pool/index.xml"
    _ARTIST_URL = "pool/index.xml"
    _POOL_DATA_URL = "pool/show.xml"

    _RATINGS = ["Safe", "Questionable", "Explicit"]

    # Signals

    dataDownloaded = pyqtSignal(KUrl, QPixmap)
    postDataReady = pyqtSignal()
    poolDataReady = pyqtSignal()
    checkCompleted = pyqtSignal(bool)
    tagsRetrieved = pyqtSignal()

    def __init__(self, api_url, login=None, password=None, parent=None,
                cache=None):


        super(Danbooru, self).__init__(parent)

        self.validate_url(api_url)

        # Basic attributes
        self.url = api_url
        self.post_data = None
        self.pool_data = None
        self.cache = cache

        # Login attributes
        self.__login = login if login else None
        self.__pwhash = hashes.generate_hash(password) if password else None

        # Specific attributes for tags and updates
        self.__rating = None
        self.__limit = None
        self.__tags = None
        self.__blacklist = None
        self.similar_tag_elements = None

    def __check_response(self, job):

        "Checks the HTTP response from the job."

        if job.error():
            self.checkCompleted.emit(False)
            return

        # Get the HTTP response
        response = unicode(job.queryMetaData("responsecode"))

        if response == "200" or response == "304":
            self.checkCompleted.emit(True)
        else:
            self.checkCompleted.emit(False)
            return


    def _read_blacklist(self):

        "Reads the current tag blacklist, if present."

        if not self.__blacklist or not isinstance(self.__blacklist, list):
            return

        return self.__blacklist

    def _write_blacklist(self, blacklist):

        "Sets the current tag blacklist. The input must be a list."

        if not isinstance(blacklist, list):
            return

        self.__blacklist = blacklist

    def _allowed_ratings(self):

        """Function to return the allowed ratings for fetching. If no ratings
        have been defined, it returns all ratings."""

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

        "Check whether a given URL exists, using KIO asynchronously."

        check_job = KIO.get(KUrl(url), KIO.NoReload, KIO.HideProgressInfo)
        self.connect(check_job, SIGNAL("result (KJob *)"), self.__check_response)

    def danbooru_request_url(self, url, parameters=None):

        "Creates and encodes a Danbooru URL appropriately."

        if parameters:
            url_parameters = urllib.urlencode(parameters)
            # Danbooru doesn't want HTML-encoded pluses
            url_parameters = urllib.unquote(url_parameters)
            url_parameters = "?" + url_parameters

        request_url = urlparse.urljoin(self.url, url)

        if parameters:
            request_url = urlparse.urljoin(request_url, url_parameters)

        return request_url

    def get_post_list(self, limit=5, tags=None, page=None):

        """Method to get posts with specific tags and limits. There is a
        hardcoded limit of 100 posts in Danbooru, so limits > 100 will be
        ignored. If present, tags must be supplied as a list. Data are
        stored as a DanbooruPostList of DanbooruItems. Different pages can
        be accessed setting the page parameter."""

        if limit > 100:
            limit = 100

        self.__limit = limit if limit else self.__limit
        self.__tags = tags if tags else self.__tags

        if tags:
            tags = "+".join(tags)
        else:
            tags = ""

        parameters = dict(tags=tags, limit=limit)

        if page:
            parameters["page"] = page

        request_url = self.danbooru_request_url(self._POST_URL, parameters)

        job = KIO.storedGet(KUrl(request_url), KIO.NoReload,
                            KIO.HideProgressInfo)

        self.connect(job, SIGNAL("result (KJob *)"), self.process_post_list)

    def update(self, page=None, what="posts"):

        """Updates previously added results. This should be used to get the
        next page of the same batch."""

        if what == "posts":

            if not self.__limit and not self.__tags:
                return

            self.get_post_list(limit=self.__limit, tags=self.__tags, page=page)

    def process_post_list(self, job):

        """Collects the data from the job and loads it into an object that can
        be read by the XML parser. Then each element of the data is converted
        into a DanbooruPostItem and stored in a DanbooruPostList. Prior to
        inserting the items in the list, they are checked for rating."""

        if job.error():
            self.post_data = None
            return

        job_data = job.data()
        parsed_data = minidom.parseString(unicode(job_data.data()))
        decoded_data = parsed_data.getElementsByTagName("post")

        self.post_data = DanbooruPostList()

        allowed_ratings = self.selected_ratings

        for item in decoded_data:
            item = DanbooruPostItem(item)
            blacklisted_tags = None

            # See if our items have blacklisted tags
            if self.blacklist:
                blacklisted_tags = [tag for tag in item.tags if tag in
                                    self.blacklist]

            if blacklisted_tags:
                continue

            if item.rating in allowed_ratings:
                self.post_data.append(item)

        self.postDataReady.emit()

    def get_tag_list(self, limit=10, pattern=""):

        "Method to retrieve a list of tags."

        parameters = dict(name=pattern, limit=limit)

        request_url = self.danbooru_request_url(self._TAG_URL, parameters)

        job = KIO.storedGet(KUrl(request_url), KIO.NoReload,
                            KIO.HideProgressInfo)

        self.connect(job, SIGNAL("result (KJob *)"), self.process_tag_list)

    def process_tag_list(self, job):

        "Method that processes tags from the XML."

        if job.error():
            self.post_data = None
            return

        job_data = job.data()
        parsed_data = minidom.parseString(unicode(job_data.data()))
        decoded_data = parsed_data.getElementsByTagName("tag")

        self.similar_tag_elements = decoded_data
        self.tagsRetrieved.emit()

    def get_pool_list(self, page=None):

        """Retrieves pool lists from the boards that support it. Additional
        pages can be accessed by setting the page parameter."""

        if page:
            parameters = dict(page=page)
        else:
            parameters = None

        request_url = self.danbooru_request_url(self._POOL_URL, parameters)

        job = KIO.storedGet(KUrl(request_url), KIO.NoReload,
                            KIO.HideProgressInfo)

        self.connect(job, SIGNAL("result (KJob *)"), self.process_pool_list)

    def get_pool_id(self, pool_id):

        """Retrieves a list of posts associated with the pool ID. Does not work
        on all Danbooru versions, unfortunately."""

        parameters = dict(id=pool_id)
        request_url = self.danbooru_request_url(self._POOL_DATA_URL, parameters)

        job = KIO.storedGet(KUrl(request_url), KIO.NoReload,
                            KIO.HideProgressInfo)

        # They're just posts - so redirect to posts handling
        self.connect(job, SIGNAL("result (KJob *)"), self.process_post_list)

    def process_pool_list(self, job):

        """Collects the data from the pool job and loads it into an object
        that can be read by the XML parser. Then each element of the data is
        converted into a DanbooruPoolItem and stored in a list."""

        if job.error():
            self.pool_data = None
            return

        job_data = job.data()
        response = unicode(job.data().data())

        parsed_data = minidom.parseString(response)
        decoded_data = parsed_data.getElementsByTagName("pool")

        pool_list = list()

        for item in decoded_data:

            pool_item = DanbooruPoolItem(item)
            pool_list.append(pool_item)

        self.pool_data = pool_list

        self.poolDataReady.emit()

    def get_artist_list(self):

        "Method to retrieve a list of artists."

        pass

    def get_image(self, image_url, wait=2):

        """Retrieves a picture (full or thumbnail) for a specific URL.
        It uses KIO.storedGet to download it asynchronously, but setting a
        KIO.Scheduler to queue the jobs. Once the job has finished, it will
        emit the dataDownloaded(KUrl, QPixmap) signal.
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

        """Slot callled from get_image. Loads the image in a QPixmap and
        inserts it into the thumbnail cache, if present. then it emits the
        dataDownloaded signal, which carries the URL of the image and the
        pixmap itself."""

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
    blacklist = property(_read_blacklist, _write_blacklist)



class DanbooruPostList(object):

    """Specialized container for Danbooru post items. It contains a lists of
    DanbooruItems and at the same time it also stores thumbnail and full image
    urls. The dictionaries are used to keep indices to the internal list, and
    they're used to return the corresponding item (standard index access is
    also possible)."""

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
            except (TypeError, IndexError):
                return

    def __contains__(self, key):

        """Keys are checked in the various dictionary, and also in the list of
        items."""

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

    """Base class for item retrieved from Danbooru. Do not use directly. Use the
    appropriate subclass for your type of data instead."""

    def __init__(self, post_data):

        self._data = post_data.attributes

    def __getattr__(self, name):

        if name not in self._data:
            return None
        else:
            return self._data[name]


class DanbooruPostItem(DanbooruItem):

    """Class to store information about a Danbooru post item retrieved via the
    REST API. The various XML attributes can be accessed through
    properties."""

    @property
    def thumbnail_url(self):

        "URL of the thumbnail"

        return self._data["preview_url"].value

    @property
    def full_url(self):

        "URL of the full image"

        return self._data["file_url"].value

    @property
    def size(self):

        "Size of the full image"

        return self._data["file_size"].value

    @property
    def tags(self):

        "Tags associated to the post. Returned as list."

        tags = self._data["tags"].value
        tags = tags.split(" ")
        return tags

    @property
    def width(self):

        "Width of the full image"

        return self._data["width"].value

    @property
    def height(self):

        "Height of the full image"

        return self._data["height"].value

    @property
    def post_id(self):

        "Danbooru unique post ID"

        return self._data["id"].value

    @property
    def source(self):

        "Original source for the image, if applicable."

        return self._data["source"].value

    @property
    def rating(self):

        "Rating for the image."

        ratings = dict(s="Safe", q="Questionable", e="Explicit")

        return ratings[self._data["rating"].value]


class DanbooruPoolItem(DanbooruItem):

    """Class to store information about a Danbooru pool item retrieved via the
    REST API. The various XML attributes can be accessed through
    properties."""

    @property
    def id(self):

        "ID of the pool. Used for post retrieval purposes."

        return int(self._data["id"].value)

    @property
    def name(self):

        "Name of the pool."

        name = self._data["name"].value
        name = name.replace("_"," ")

        return name

    @property
    def post_count(self):

        "Posts in the pool"

        return int(self._data["post_count"].value)
