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

"""This module contains classes which wrap Danbooru's XML
API requests into proper objects."""

class DanbooruPost(object):

    """A class representing a Danbooru post.

    :param data: The parsed XML answer from the API call
    :param pixmap: A ``QPixmap`` which contains the thumbnail (default:
                   :const:`None`
    """

    def __init__(self, data, pixmap=None):

        self.__data = data
        self.__pixmap = None

    def __getattr__(self, value):

        if value not in self.__data.attrib:
            return None
        else:
            return self.__data.attrib[value]

    @property
    def pixmap(self):

        """A QPixmap instance holding the thumbnail of the post,
        or :const:`None` if the thumbnail has not been downloaded"""

        return self.__pixmap

    @pixmap.setter
    def pixmap(self, pixmap):

        if pixmap.isNull():
            return

        self.__pixmap = pixmap

    @property
    def rating(self):

        """The rating for the image.

        Either *Safe*, *Questionable*, or *Explicit* depending on the post

        """

        ratings = dict(s="Safe", q="Questionable", e="Explicit")

        return ratings[self.__data.attrib["rating"]]

    @property
    def tags(self):

        """The tags for the image."""

        return self.__data.attrib["tags"].split(" ")


class DanbooruTag(object):

    """A class representing a Danbooru tag."""

    _TYPES = {0: "General", 1: "artist", 3: "copyright",
              4: "character"}

    def __init__(self, data):

        self.__data = data

    def __getattr__(self, value):

        if value not in self.__data.attrib:
            return None
        else:
            return self.__data.attrib[value]

    @property
    def type(self):

        """The type of the tag, among "General", "artist",
        "copyright" and "character"."""

        tag_type = int(self._data.attrib["type"])
        return self._TYPES[tag_type]


class DanbooruPool(object):
    pass
