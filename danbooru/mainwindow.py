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
from PyKDE4.kio import *

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

    def setup_tooltips(self):

        self.connect_action.setToolTip(i18n("Connect to a Danbooru board"))
        self.fetch_action.setToolTip(
            i18n("Fetch thumbnails from a Danbooru board")
        )
        self.batch_download_action.setToolTip(i18n("Batch download images"))

    def create_actions(self):

        self.connect_action = KAction(KIcon("document-open-remote"),
                                 i18n("Connect"), self)
        self.fetch_action = KAction(KIcon("download"), i18n("Fetch"), self)
        self.clean_action = KAction(KIcon("trash-empty"),
                               i18n("Clear thumbnail cache"),
                               self)
        self.batch_download_action = KAction(KIcon("download"),
                                             i18n("Batch download"), self)

        # Shortcuts
        connect_default = KAction.ShortcutTypes(KAction.DefaultShortcut)
        connect_active = KAction.ShortcutTypes(KAction.ActiveShortcut)
        self.connect_action.setShortcut(QKeySequence.Open,
                                   connect_default | connect_active)
        self.fetch_action.setShortcut(QKeySequence.Find,
                                 connect_default | connect_active)

        # No sense in enabling fetch and batch at start
        if not self.api:
            self.fetch_action.setEnabled(False)
            self.batch_download_action.setEnabled(False)

    def setup_actions(self):

        self.create_actions()
        self.setup_tooltips()

        # Addition to the action collection
        self.actionCollection().addAction("connect", self.connect_action)
        self.actionCollection().addAction("fetch", self.fetch_action)
        self.actionCollection().addAction("clean", self.clean_action)
        self.actionCollection().addAction("batchDownload",
                                          self.batch_download_action)
        KStandardAction.quit (self.close, self.actionCollection())
        KStandardAction.preferences(self.show_preferences,
                                    self.actionCollection())

        # Connect signals
        self.connect_action.triggered.connect(self.connect_danbooru)
        self.fetch_action.triggered.connect(self.fetch)
        self.clean_action.triggered.connect(self.clean_cache)
        self.batch_download_action.triggered.connect(self.batch_download)
        self.actionCollection().actionHovered.connect(self.action_tooltip)

        setupGUI_args = [
            QSize(500, 400), self.StandardWindowOption(
                self.ToolBar | self.Keys | self.Create | self.Save | self.StatusBar)
        ]

        #Check first in standard locations for danbooruui.rc

        rc_file = KStandardDirs.locate("appdata", "danbooruui.rc")
        if rc_file.isEmpty():
            setupGUI_args.append(os.path.join(sys.path [0],
                                                   "danbooruui.rc"))
        else:
            setupGUI_args.append(rc_file)
        self.setupGUI(*setupGUI_args)

        # Remove handbook menu entry
        # Called later than setupGUI or it won't exist yet
        self.actionCollection().removeAction(
            self.actionCollection().action("help_contents"))

    def action_tooltip(self, action):

        if action.isEnabled():
            self.statusBar().showMessage(action.toolTip(), 2000)

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

    def retrieve(self, tags, limit, ratings=None):

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
            self.statusBar().showMessage(i18n("No posts found."), 3000)
            return

        if ratings:
            selected_posts = [item for item in self.api.data if item.rating in
                              ratings]
            if not selected_posts:
                self.statusbar.showMessage(
                    i18n("No posts match your selected rating."), 3000)
                return

            urls = [item.thumbnail_url for item in self.api.data]
        else:
            urls = [item.thumbnail_url for item in self.api.data]

        max_steps = len(urls)

        self.progress.setMaximum(max_steps)
        self.progress.show()

        self.thumbnailview.display_thumbnails()

        # Reset the counter in case of subsequent fetches
        self.__step = 0
        self.progress.hide()
        self.progress.reset()
        self.batch_download_action.setEnabled(True)

    def clear(self):

        if self.thumbnailview is None:
            return

        self.thumbnailview.clear_items()
        self.thumbnailview.clear()
        self.batch_download_action.setEnabled(False)

    def clean_cache(self):

        self.cache.discard()
        self.statusBar().showMessage(i18n("Thumbnail cache cleared."))

    def fetch(self, ok):

        if not self.api:
            return

        dialog = fetchdialog.FetchDialog(self.max_retrieve, self)

        if dialog.exec_():
            # Clear only if we pressed OK
            self.clear()
            tags = dialog.tags()
            limit = dialog.limit()
            ratings = dialog.max_rating()

            self.setup_area()
            self.retrieve(tags, limit, ratings)
        else:
            return

    def batch_download(self, ok):

        selected_items = self.thumbnailview.selected_images()

        if not selected_items:
            return

        start_url = KUrl("kfiledialog:///danbooru")
        caption = i18n("Select a directory to save the images to")
        directory = KFileDialog.getExistingDirectoryUrl(start_url, self, caption)

        if directory.isEmpty():
            return

        for item in selected_items:
            file_url = KUrl(item)

            # Make a local copy to append paths as addPath works in-place
            destination = KUrl(directory)
            file_name = file_url.fileName()
            destination.addPath(file_name)
            job = KIO.file_copy(KUrl(item), destination, -1)
            self.connect(job, SIGNAL("result (KJob *)"), self.job_slot_result)

    def job_slot_result(self, job):

        if job.error():
            job.ui().showErrorMessage()


