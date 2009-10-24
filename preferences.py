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

from PyQt4.QtCore import QStringList, QSize, QRegExp,Qt
from PyQt4.QtGui import QWidget, QRegExpValidator
from PyKDE4.kdeui import KConfigSkeleton, KConfigDialog, KIcon, KDialog
from PyKDE4.kdecore import i18n

from ui.ui_generalpage import Ui_GeneralPage
from ui.ui_nepomukpage import Ui_NepomukPage
from ui.ui_danboorupage import Ui_DanbooruPage

class Preferences(KConfigSkeleton):

    """Class to handle preferences. Currently, the following items are stored:
        - danbooruUrls - list of Danbooru URLs inserted by the user
        - thumbnailMaxRetrieve - maximum number of thumbnail to retireve
        - nepomukEnabled - whether to use Nepomuk tagging or not
        - tagBlacklist - tags that should not be used while tagging
        - columnNumber - number of columns to display

        Currently usernames and passwords are not saved at all."""

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
        return self._tag_blacklist.value()


class PreferencesDialog(KConfigDialog):

    def __init__(self, parent=None, name=None, preferences=None):

        super(PreferencesDialog, self).__init__(parent, name, preferences)
        self.setButtons(KDialog.ButtonCode(KDialog.Ok |KDialog.Apply |
                                            KDialog.Cancel))

        self.resize(QSize(550, 420))
        self.general_page = GeneralPage(self, preferences)
        self.nepomuk_page = NepomukPage(self, preferences)
        self.general_page_item = self.addPage(self.general_page,
                                              i18n('Layout'))

        self.danbooru_page = DanbooruPage(self, preferences)
        self.danbooru_page_item = self.addPage(self.danbooru_page,
                                               i18n("Danbooru URLs"))

        self.nepomuk_page_item = self.addPage(self.nepomuk_page,
                                              i18n("Tagging"))

        self.general_page_item.setIcon(KIcon("table"))
        self.danbooru_page_item.setIcon(KIcon("preferences-web-browser-shortcuts"))
        self.nepomuk_page_item.setIcon(KIcon("nepomuk"))


class GeneralPage(QWidget, Ui_GeneralPage):

    "Page containing layout options"

    def __init__(self, parent=None, preferences=None):

        super(GeneralPage, self).__init__(parent)
        self.setupUi(self)

        self.kcfg_thumbnailMaxRetrieve.setValue(preferences.thumbnail_no)
        self.kcfg_displayColumns.setValue(preferences.column_no)


class NepomukPage(QWidget, Ui_NepomukPage):

    "Page containing Nepomuk options"

    def __init__(self, parent=None, preferences=None):

        super(NepomukPage, self).__init__(parent)
        self.setupUi(self)

        self.kcfg_nepomukEnabled.setChecked(preferences.nepomuk_enabled)
        self.kcfg_tagBlacklist.insertStringList(preferences.tag_blacklist)

        self.kcfg_nepomukEnabled.stateChanged.connect(self.toggle_editlist)

        if self.kcfg_nepomukEnabled.isChecked():
            self.kcfg_tagBlacklist.setDisabled(False)

    def toggle_editlist(self, state):

        if state == Qt.Checked:
            self.kcfg_tagBlacklist.setDisabled(False)
        elif state == Qt.Unchecked:
            self.kcfg_tagBlacklist.setDisabled(True)


class DanbooruPage(QWidget, Ui_DanbooruPage):

    "Page containing Danbooru URLs"

    def __init__(self, parent=None, preferences=None):

        super(DanbooruPage, self).__init__(parent)
        self.setupUi(self)

        self.kcfg_danbooruUrls.insertStringList(preferences.boards_list)
        regex =(r"(http|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?")
        regex = QRegExp(regex)

        self._validator = QRegExpValidator(regex, self)
        self.kcfg_danbooruUrls.lineEdit().setValidator(self._validator)


