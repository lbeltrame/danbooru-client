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

from ui_generalpage import Ui_GeneralPage

class Preferences(KConfigSkeleton):

    """Class to handle preferences."""

    def __init__(self, *args):
        KConfigSkeleton.__init__(self, *args)

        self.setCurrentGroup("General")

        self._danbooru_boards_list = QStringList()
        predefined_urls = QStringList(["http://moe.imouto.org",
                                 "http://konachan.com",
                                 "http://konachan.net"])
        self._danbooru_boards = self.addItemStringList("danbooruUrls",
                                                       self._danbooru_boards_list,
                                                       predefined_urls)

        self._max_retrieve = self.addItemInt("thumbnailMaxRetrieve", 100, 100)

        self._nepomuk_enabled = self.addItemBool("nepomukEnabled", False, False)

        self._tag_blacklist_values = QStringList()
        predefined_blacklist = QStringList(["tagme", "jpeg_artifacts", "scan",
                                            "fixme", "crease"])
        self._tag_blacklist = self.addItemStringList("tagBlacklist",
                                                     self._tag_blacklist_values,
                                                     predefined_blacklist)

        self._column_number = self.addItemInt("columnNumber", 3, 3)

        #TODO: Should user/passwords for the API be stored here?
        self.readConfig()

    @property
    def boards_list(self):
        return self._danbooru_boards.value()

    @property
    def thumbnail_no(self):
        return self._max_retrieve.value()

    @property
    def column_no(self):
        return self._column_number.value()

    @property
    def nepomuk_enabled(self):
        return self._nepomuk_enabled.value()

    @property
    def tag_blacklist(self):
        return self;_tag_blacklist.value()

class PreferencesDialog(KConfigDialog):

    def __init__(self, parent=None, name=None, preferences=None):
        super(PreferencesDialog, self).__init__(parent, name, preferences)

        self.setButtons(KDialog.ButtonCode(KDialog.Ok |KDialog.Apply |
                                            KDialog.Cancel))

        self.general_page = GeneralPage(self, preferences)
        self.general_page_item = self.addPage(self.general_page, 'General')
        self.general_page_item.setIcon(KIcon("preferences-web-browser-shortcuts"))

class GeneralPage(QWidget, Ui_GeneralPage):

    def __init__(self, parent=None, preferences=None):

        super(GeneralPage, self).__init__(parent)
        self.setupUi(self)

        self.kcfg_danbooruUrls.insertStringList(preferences.boards_list)
        self.kcfg_thumbnailMaxRetrieve.setValue(preferences.thumbnail_no)

        regex =(r"(http|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?")
        regex = QRegExp(regex)

        self._validator = QRegExpValidator(regex, self)
        self.kcfg_danbooruUrls.lineEdit().setValidator(self._validator)
