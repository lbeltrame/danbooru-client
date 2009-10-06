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

'''
File: preferences.py
Author: Luca Beltrame
Description: Preferences module for the Danbooru client.
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import *

class Preferences(KConfigSkeleton):

    """Class to handle preferences."""

    def __init__(self, *args):
        KConfigSkeleton.__init__(self, *args)

        self.setCurrentGroup("General")
        self._last_visited_name = QString()
        self._last_visited = self.addItemString("lastVisited",
                                                self._last_visited_name, "")
        self._max_retrieve = self.addItemInt("thumbnailMaxRetrieve", 100, 100)
        self._tag_blacklist_values = QStringList()
        self._tag_blacklist = self.addItemStringList("tagBlacklist",
                                                     self._tag_blacklist_values)
        #TODO: Should user/passwords for the API be stored here?
        self.readConfig()

