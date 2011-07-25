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

import PyQt4.QtGui as QtGui

import PyKDE4.kdecore as kdecore


class DanbooruTagWidget(QtGui.QListWidget):

    """A tag widget for Danbooru Tags"""

    def __init__(self, blacklist, parent=None):

        super(DanbooruTagWidget, self).__init__(parent)

        self.tag_list = list()
        self.blacklist = blacklist

    def add_tags(self, tag):

        tag_type = tag.type
        tag_name = tag.name

        if tag_name in self.blacklist:
            return

        self.tag_list.append(tag.name)

        item = QtGui.QListWidgetItem(tag_name)
        item.setToolTip(kdecore.i18n("Type: %1\nNumber of items: %2", tag_type,
                                     tag.count))

        self.addItem(item)

    def clear(self):

        super(DanbooruTagWidget, self).clear()
        self.tag_list = list()
