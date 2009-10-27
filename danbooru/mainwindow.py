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
File: mainwindow.py
Author: Luca Beltrame
Description: Main window module of the Danbooru client application
'''

from __future__ import division

import sys
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyKDE4.kdecore import *
from PyKDE4.kdeui import *
from PyKDE4.kparts import *

import preferences
import thumbnailview
import fetchdialog
import connectdialog

class MainWindow(KXmlGuiWindow):

    def __init__(self):

        KXmlGuiWindow.__init__(self)
        self.cache = KPixmapCache("danbooru")
        self.preferences = preferences.Preferences()

        self.welcome = QLabel()
        pix = QPixmap(KStandardDirs.locate("appdata","logo.png"))
        self.welcome.setPixmap(pix)
        self.welcome.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.welcome)

        self.statusbar = self.statusBar()
        self.progress = QProgressBar()
        self.progress.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # Hackish, but how to make it small otherwise?
        self.progress.setMinimumSize(100, 1)
        self.statusbar.addPermanentWidget(self.progress)
        self.progress.hide()

        self.thumbnailview = None
        self.api = None
        self.__step = 0

        self.read_config()
        self.setup_actions()

    def read_config(self):

        self.url_list = self.preferences.boards_list
        self.max_retrieve = self.preferences.thumbnail_no
        self.column_no = self.preferences.column_no

    def setup_actions(self):

        self.connect_action = KAction(KIcon("document-open-remote"),
                                 i18n("Connect"), self)
        self.fetch_action = KAction(KIcon("download"), i18n("Fetch"), self)
        self.clean_action = KAction(KIcon("trash-empty"),
                               i18n("Clear thumbnail cache"),
                               self)

        connect_default = KAction.ShortcutTypes(KAction.DefaultShortcut)
        connect_active = KAction.ShortcutTypes(KAction.ActiveShortcut)

        self.connect_action.setShortcut(QKeySequence.Open,
                                   connect_default | connect_active)
        self.fetch_action.setShortcut(QKeySequence.Find,
                                 connect_default | connect_active)

        self.actionCollection().addAction("connect", self.connect_action)
        self.actionCollection().addAction("fetch", self.fetch_action)
        self.actionCollection().addAction("clean", self.clean_action)

        KStandardAction.quit (self.close, self.actionCollection())
        KStandardAction.preferences(self.show_preferences,
                                    self.actionCollection())

        self.connect_action.triggered.connect(self.connect_danbooru)
        self.fetch_action.triggered.connect(self.fetch)
        self.clean_action.triggered.connect(self.clean_cache)
        self.actionCollection().actionHovered.connect(self.actiontooltip)

        # No sense in enabling fetch at start
        if not self.api:
            self.fetch_action.setEnabled(False)

        setupGUI_args = [
            QSize(500, 400), self.StandardWindowOption(
                self.ToolBar | self.Keys | self.Create | self.Save | self.StatusBar)
        ]

        #Check first in standard locations

        rc_file = KStandardDirs.locate("appdata", "danbooruui.rc")
        if rc_file.isEmpty():
            setupGUI_args.append(os.path.join(sys.path [0],
                                                   "danbooruui.rc"))
        else:
            setupGUI_args.append(rc_file)

        self.setupGUI(*setupGUI_args)
        # Called later than setupGUI or it won't exist yet
        self.actionCollection().removeAction(
            self.actionCollection().action("help_contents"))

    def actiontooltip(self, action):

        if action.isEnabled():
            self.statusBar().showMessage(action.text())

    def show_preferences(self):

        if KConfigDialog.showDialog("Preferences dialog"):
            return
        else:
            dialog = preferences.PreferencesDialog(self, "Preferences dialog",
                                                   self.preferences)
            dialog.show()
            dialog.settingsChanged.connect(self.read_config)

    def connect_danbooru(self, ok):

        dialog = connectdialog.ConnectDialog(self.url_list, self)

        if dialog.exec_():
            self.api = dialog.danbooru_api()
            self.api.cache = self.cache
            self.statusBar().showMessage(i18n("Connected to %s" % self.api.url),
                                         3000)
            self.fetch_action.setEnabled(True)

    def setup_area(self):

        self.thumbnailview = thumbnailview.ThumbnailView(self.api,
                                                         self.preferences,
                                                        columns=self.column_no)
        self.setCentralWidget(self.thumbnailview)
        self.thumbnailview.thumbnailDownloaded.connect(self.update_progress)

    def update_progress(self):

        self.__step += 1
        self.progress.setValue(self.__step)

    def retrieve(self, tags, limit):

        # Catch errors gracefully
        try:
            posts = self.api.get_post_list(limit=limit, tags=tags)
        except ValueError, error:
            first_line = "Could not download information from the specified board."
            second_line = "This means connection problems, or that the board"
            third_line = "has a broken API."
            error_line = "Returned error: %s" % error
            message = '\n'.join((first_line, second_line, third_line,
                                 error_line))
            KMessageBox.error(self, i18n(message),
                              i18n("Error retrieving posts"))
            return

        if not posts:
            self.satusBar().setMessage(i18n("No posts found."), 3000)
            return

        urls = [item.thumbnail_url for item in self.api.data]

        max_steps = len(urls)

        self.progress.setMaximum(max_steps)
        self.progress.show()

        self.thumbnailview.display_thumbnails()

        # Reset the counter in case of subsequent fetches
        self.__step = 0
        self.progress.reset()
        self.progress.hide()

    def clear(self):

        if self.thumbnailview is None:
            return

        self.thumbnailview.clear()

    def clean_cache(self):

        self.cache.discard()
        self.statusBar().showMessage(i18n("Thumbnail cache cleared."))

    def fetch(self, ok):

        if not self.api:
            return

        self.clear()

        dialog = fetchdialog.FetchDialog(self.max_retrieve, self)

        if dialog.exec_():
            tags = dialog.tags()
            limit = dialog.limit()

            self.setup_area()
            self.retrieve(tags, limit)
        else:
            return
