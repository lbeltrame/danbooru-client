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

from PyQt4.QtCore import Qt, QSize, QVariant
from PyQt4.QtGui import (QLabel, QPixmap, QProgressBar, QSizePolicy,
                         QKeySequence)
from PyKDE4.kdecore import KStandardDirs, KUrl, i18n
from PyKDE4.kdeui import (KXmlGuiWindow, KPixmapCache, KAction,
                          KStandardAction, KIcon, KConfigDialog)
from PyKDE4.kio import KFileDialog, KIO

import preferences
import thumbnailarea
import fetchdialog
import connectdialog
import pooldialog
import danbooru2nepomuk

class MainWindow(KXmlGuiWindow):

    "Class which displays the main Danbooru Client window."

    def __init__(self,  *args):

        "Initialize a new main window."

        super(MainWindow,  self).__init__(*args)
        self.cache = KPixmapCache("danbooru")
        self.preferences = preferences.Preferences()
        self.api = None
        self.__ratings = None
        self.__step = 0

        self.url_list = self.preferences.boards_list
        self.max_retrieve = self.preferences.thumbnail_no

        self.statusbar = self.statusBar()
        self.progress = QProgressBar()
        self.thumbnailarea = None
        self.progress.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # FIXME: Hackish, but how to make it small otherwise?
        self.progress.setMinimumSize(100, 1)
        self.statusbar.addPermanentWidget(self.progress)
        self.progress.hide()

        self.setup_welcome_widget()
        self.setup_actions()

    def setup_welcome_widget(self):

        """Load the welcome widget at startup."""

        welcome = QLabel()
        pix = QPixmap(KStandardDirs.locate("appdata","logo.png"))

        welcome.setPixmap(pix)
        welcome.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(welcome)

    def setup_tooltips(self):

        """Set tooltips for the actions."""

        self.connect_action.setToolTip(i18n("Connect to a Danbooru board"))
        self.fetch_action.setToolTip(
            i18n("Fetch thumbnails from a Danbooru board")
        )
        self.batch_download_action.setToolTip(i18n("Batch download images"))

    def create_actions(self):

        """Create actions for the main window."""

        self.connect_action = KAction(KIcon("document-open-remote"),
                                 i18n("Connect"), self)
        self.fetch_action = KAction(KIcon("download"), i18n("Fetch"), self)
        self.clean_action = KAction(KIcon("trash-empty"),
                               i18n("Clear thumbnail cache"),
                               self)
        self.batch_download_action = KAction(KIcon("download"),
                                             i18n("Batch download"), self)
        self.pool_download_action = KAction(KIcon("image-x-generic"),
                                            i18n("Pools"), self)

        # Shortcuts
        connect_default = KAction.ShortcutTypes(KAction.DefaultShortcut)
        connect_active = KAction.ShortcutTypes(KAction.ActiveShortcut)

        self.connect_action.setShortcut(QKeySequence.Open,
                                   connect_default | connect_active)
        self.fetch_action.setShortcut(QKeySequence.Find,
                                 connect_default | connect_active)

        self.fetch_action.setEnabled(False)
        self.batch_download_action.setEnabled(False)
        self.pool_download_action.setEnabled(False)

    def setup_action_collection(self):

        """Set up the action collection by adding the actions."""

        action_collection = self.actionCollection()

        # Addition to the action collection
        action_collection.addAction("connect", self.connect_action)
        action_collection.addAction("fetch", self.fetch_action)
        action_collection.addAction("clean", self.clean_action)
        action_collection.addAction("batchDownload",
                                    self.batch_download_action)
        action_collection.addAction("poolDownload",
                                          self.pool_download_action)

        KStandardAction.quit (self.close, action_collection)
        KStandardAction.preferences(self.show_preferences,
                                    action_collection)

        action_collection.removeAction(
            action_collection.action("help_contents"))
        action_collection.actionHovered.connect(self.setup_action_tooltip)

    def setup_actions(self):

        """Set up the relevant actions, tooltips, and load the RC file."""

        self.create_actions()
        self.setup_tooltips()
        self.setup_action_collection()

        # Connect signals
        self.connect_action.triggered.connect(self.connect)
        self.fetch_action.triggered.connect(self.get_posts)
        self.clean_action.triggered.connect(self.clean_cache)
        self.batch_download_action.triggered.connect(self.batch_download)
        self.pool_download_action.triggered.connect(self.pool_download)

        window_options = self.StandardWindowOption(self.ToolBar| self.Keys |
                                                   self.Create | self.Save |
                                                   self.StatusBar)

        setupGUI_args = [
            QSize(500, 400), self.StandardWindowOption(window_options)
        ]

        #Check first in standard locations for danbooruui.rc

        rc_file = KStandardDirs.locate("appdata", "danbooruui.rc")

        if rc_file.isEmpty():
            setupGUI_args.append(os.path.join(sys.path [0],
                                              "danbooruui.rc"))
        else:
            setupGUI_args.append(rc_file)

        self.setupGUI(*setupGUI_args)

    def setup_action_tooltip(self, action):

        "Show statusbar help when actions are hovered."

        if action.isEnabled():
            self.statusBar().showMessage(action.toolTip(), 2000)

    def show_preferences(self):

        "Show the preferences dialog."

        if KConfigDialog.showDialog("Preferences dialog"):
            return
        else:
            dialog = preferences.PreferencesDialog(self, "Preferences dialog",
                                                   self.preferences)
            dialog.show()
            #FIXME: Needed?
            dialog.settingsChanged.connect(self.read_config)

    def connect(self, ok):

        "Connect to a Danbooru board."

        dialog = connectdialog.ConnectDialog(self.url_list, self)

        if dialog.exec_():
            self.api = None
            self.api = dialog.danbooru_connection
            self.api.cache = self.cache

            if self.thumbnailarea is not None:
                #TODO: Investigate usability
                self.thumbnailarea.clear()
                self.thumbnailarea.api_data = self.api

            self.api.cache = self.cache

            self.statusBar().showMessage(i18n("Connected to %s" % self.api.url),
                                         3000)
            self.fetch_action.setEnabled(True)
            self.pool_download_action.setEnabled(True)

    def get_posts(self, ok):

        "Get posts from the connected Danbooru board."

        if not self.api:
            return

        dialog = fetchdialog.FetchDialog(self.max_retrieve,
                                         preferences=self.preferences,
                                         parent=self)

        if dialog.exec_():

            self.clear()
            tags = dialog.tags
            limit = dialog.limit
            max_rating = dialog.max_rating

            if not self.thumbnailarea:
                self.setup_area()

            self.thumbnailarea.post_limit = limit
            blacklist= list(self.preferences.tag_blacklist)
            self.api.get_post_list(tags=tags, limit=limit,
                                   rating=max_rating,
                                   blacklist=blacklist)

    def pool_download(self, ok):

        "Calls the download of all available pools."

        if not self.api:
            return

        self.api.get_pool_list()

    def pool_select(self):

        """Slot called when the pool data have been downloaded. It constructs
        the pool dialog and then starts the download of the images."""

        if not self.api.pool_data:
            return

        dialog = pooldialog.PoolDialog(self.api.pool_data, self)

        if dialog.exec_():

            selected_pool_id = dialog.selected_id()

            if not self.thumbnailarea:
                self.setup_area()
            else:
                self.thumbnailarea.clear()

            self.api.get_pool_id(pool_id=selected_pool_id)

    def batch_download(self, ok):

        "Slot called for batch downloading of selected images."

        selected_items = self.thumbnailarea.selected_images()

        if not selected_items:
            return

        start_url = KUrl("kfiledialog:///danbooru")
        caption = i18n("Select a directory to save the images to")
        directory = KFileDialog.getExistingDirectoryUrl(start_url, self,
                                                        caption)

        if directory.isEmpty():
            return

        for item in selected_items:

            file_url = item.url_label.url()
            tags = item.data.tags

            # Make a local copy to append paths as addPath works in-place
            destination = KUrl(directory)
            file_name = file_url.fileName()
            destination.addPath(file_name)

            job = KIO.file_copy(KUrl(item), destination, -1)
            job.setProperty("tags", QVariant(tags))
            job.result.connect(self.batch_download_slot)

    def setup_area(self):

        "Sets up the central widget to display thumbnails."

        self.thumbnailarea = thumbnailarea.DanbooruTabWidget(self.api,
            self.preferences, self)

        self.setCentralWidget(self.thumbnailarea)

        self.api.postRetrieved.connect(self.update_progress)
        self.api.postDownloadFinished.connect(self.download_finished)

    def download_finished(self):

        """Slot called when all the data has been completed. Clears the progress
        bar and resets it to 0."""

        if not self.batch_download_action.isEnabled():
            self.batch_download_action.setEnabled(True)

        self.__step = 0
        self.progress.hide()

    def update_progress(self):

        "Updates the progress bar."

        if not self.progress.isVisible():
            self.progress.show()

        self.__step += 1
        self.progress.setValue(self.__step)

    def clear(self):

        "Clears the central widget."

        if self.thumbnailarea is None:
            return

        self.thumbnailarea.clear()
        self.batch_download_action.setEnabled(False)

    def clean_cache(self):

        "Purge the thumbnail cache."

        self.cache.discard()
        self.statusBar().showMessage(i18n("Thumbnail cache cleared."))

    def batch_download_slot(self, job):

        """Slot called when doing batch download, for each file retrieved."""

        if job.error():
            job.ui().showErrorMessage()
        else:
            if self.preferences.nepomuk_enabled:
                tags = job.property("tags").toPyObject()
                danbooru2nepomuk.tag_danbooru_item(job.destUrl().path(),
                                                   tags)
