#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Copyright 2009 Luca Beltrame <einar@heavensinferno.net>
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

"""The :mod:`danbooru2nepomuk` module handles tagging items downloaded frm
Danbooru boards into Nepomuk."""

import itertools
import re

import PyQt4.QtCore as QtCore

from PyKDE4.nepomuk import Nepomuk
from PyKDE4.kdecore import KUrl

# Regexp to filter out the board name and post ID from the filename
BOARD_REGEX = re.compile("(.*[0-9]+)\s(.*)(.jpe?g|.gif|.png|.tif)")


def tag_danbooru_item(filename, tags, blacklist=None):

    """Tag a file using a specific :class:`DanbooruItem` tags."""

    resource_manager = Nepomuk.ResourceManager.instance()

    if not resource_manager.initialized():
        # Nepomuk not running - bail out
        return

    absolute_path = QtCore.QFileInfo(filename).absoluteFilePath()
    resource = Nepomuk.File(KUrl(absolute_path))

    for tag in tags:

        if blacklist is not None and tag in blacklist:
            continue

        nepomuk_tag = Nepomuk.Tag(tag)
        nepomuk_tag.setLabel(tag)
        resource.addTag(nepomuk_tag)


def mass_tag_items(filenames, danbooru_items, blacklist):

    """Tag a list of items.

    This is used with batch downloading."""

    for filename, danbooru_item in itertools.izip(filenames, danbooru_items):
        tag_danbooru_item(filename, danbooru_item, blacklist)
