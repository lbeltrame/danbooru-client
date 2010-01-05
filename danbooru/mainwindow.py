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

from PyQt4.QtCore import Qt, QSize, SIGNAL
from PyQt4.QtGui import (QLabel, QPixmap, QProgressBar, QSizePolicy,
                         QKeySequence)
from PyKDE4.kdecore import KStandardDirs, KUrl, i18n
from PyKDE4.kdeui import (KXmlGuiWindow, KPixmapCache, KAction,
                          KStandardAction, KIcon, KConfigDialog, KMessageBox)
from PyKDE4.kio import KFileDialog, KIO

import preferences
import thumbnailarea
import fetchdialog
import connectdialog
import pooldialog

class MainWindow(KXmlGuiWindow):

    "Class which displays the main Danbooru Client window."

    def __init__(self):

        "Initialize a new main window."

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
        self.thumbnailarea = None
        self.progress.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # FIXME: Hackish, but how to make it small otherwise?
        self.progress.setMinimumSize(100, 1)
        self.statusbar.addPermanentWidget(self.progress)
        self.progress.hide()

        # Various instance bits needed
        self.api = None
        self.__ratings = None
        self.__step = 0

        self.read_config()
        self.setup_actions()

    def read_config(self):

        """Reads the configuration from the instance variable of the preferences,
        and sets some parameters."""

        self.url_list = self.preferences.boards_list
        self.max_retrieve = self.preferences.thumbnail_no

    def setup_tooltips(self):

        "Sets tooltips for the actions."

        self.connect_action.setToolTip(i18n("Connect to a Danbooru board"))
        self.fetch_action.setToolTip(
            i18n("Fetch thumbnails from a Danbooru board")
        )
        self.batch_download_action.setToolTip(i18n("Batch download images"))

    def create_actions(self):

        "Creates actions for the main window."

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

        # No sense in enabling fetch and batch at start
        if not self.api:
            self.fetch_action.setEnabled(False)
            self.batch_download_action.setEnabled(False)
            self.pool_download_action.setEnabled(False)

    def setup_actions(self):

        """Wrapper function that creates actions, setups tooltips, adds actions
        to the action collection, and connects relevant signals."""

        self.create_actions()
        self.setup_tooltips()

        # Addition to the action collection
        self.actionCollection().addAction("connect", self.connect_action)
        self.actionCollection().addAction("fetch", self.fetch_action)
        self.actionCollection().addAction("clean", self.clean_action)
        self.actionCollection().addAction("batchDownload",
                                          self.batch_download_action)
        self.actionCollection().addAction("poolDownload",
                                          self.pool_download_action)
        KStandardAction.quit (self.close, self.actionCollection())
        KStandardAction.preferences(self.show_preferences,
                                    self.actionCollection())

        # Connect signals
        self.connect_action.triggered.connect(self.connect_danbooru)
        self.fetch_action.triggered.connect(self.fetch)
        self.clean_action.triggered.connect(self.clean_cache)
        self.batch_download_action.triggered.connect(self.batch_download)
        self.pool_download_action.triggered.connect(self.pool_download)
        # Show tooltips in the status bar as well
        self.actionCollection().actionHovered.connect(self.action_tooltip)

        setupGUI_args = [
            QSize(500, 400), self.StandardWindowOption(
                self.ToolBar | self.Keys | self.Create | self.Save | self.StatusBar)
        ]

        #Check first in standard locations for danbooruui.rc

        rc_file = KStandardDirs.locate("appdata", "danbooruui.rc")
        if rc_file.isEmpty():
            # Not found, check elsewhere
            setupGUI_args.append(os.path.join(sys.path [0],
                                                   "danbooruui.rc"))
        else:
            setupGUI_args.append(rc_file)

        self.setupGUI(*setupGUI_args)

        # Remove handbook menu entry: the call needs to be put later than
        # setupGUI or the action won't exist, leading to no effect

        self.actionCollection().removeAction(
            self.actionCollection().action("help_contents"))

    def action_tooltip(self, action):

        "Slot to show statusbar help when actions are hovered."

        if action.isEnabled():
            self.statusBar().showMessage(action.toolTip(), 2000)

    def show_preferences(self):

        "Shows the preferences dialog."

        if KConfigDialog.showDialog("Preferences dialog"):
            return
        else:
            dialog = preferences.PreferencesDialog(self, "Preferences dialog",
                                                   self.preferences)
            dialog.show()
            dialog.settingsChanged.connect(self.read_config)

    def connect_danbooru(self, ok):

        "Connects to a Danbooru board."

        dialog = connectdialog.ConnectDialog(self.url_list, self)

        if dialog.exec_():
            self.api = None
            self.api = dialog.danbooru_api()
            self.api.poolDataReady.connect(self.pool_select)

            if self.thumbnailarea is not None:
                # Update API reference in the thumbnailarea
                self.thumbnailarea.update_data(self.api)

            self.api.cache = self.cache
            # Preferences gives us a QStringList, so convert
            self.api.blacklist = list(self.preferences.tag_blacklist)
            self.statusBar().showMessage(i18n("Connected to %s" % self.api.url),
                                         3000)
            self.fetch_action.setEnabled(True)
            self.pool_download_action.setEnabled(True)

    def retrieve(self, tags, limit):

        "Retrieves posts from the currently connected Danbooru board."

        try:
            self.api.get_post_list(limit=limit, tags=tags)
        except ValueError, error:
            first_line = "Could not download information from the specified board."
            second_line = "This means connection problems, or that the board"
            third_line = "has a broken API."
            error_line = "Returned error: %s" % error
            message = '\n'.join((first_line, second_line, third_line,
                                 error_line))
            KMessageBox.error(self, i18n(message),
                              i18n("Error retrieving posts"))

    def fetch(self, ok):

        "Fetches the actual data from the connected Danbooru board."

        if not self.api:
            return

        dialog = fetchdialog.FetchDialog(self.max_retrieve,
                                         preferences=self.preferences,
                                         parent=self)

        if dialog.exec_():
            # Clear only if we pressed OK
            self.clear()
            tags = dialog.tags()
            limit = dialog.limit()
            self.api.selected_ratings = dialog.max_rating()

            if not self.thumbnailarea:
                self.setup_area()
            self.retrieve(tags, limit)
        else:
            return

    def pool_download(self, ok):

        if not self.api:
            return

        self.api.get_pool_list()

    def pool_select(self):

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

    def setup_area(self):

        "Sets up the central widget to display thumbnails."

        self.thumbnailarea = thumbnailarea.ThumbnailArea(self.api,
                                                         self.preferences,
                                                         self)

        self.setCentralWidget(self.thumbnailarea)
        self.thumbnailarea.thumbnailDownloaded.connect(self.update_progress)
        self.thumbnailarea.downloadCompleted.connect(self.download_finished)

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

        "Purges the thumbnail cache."

        self.cache.discard()
        self.statusBar().showMessage(i18n("Thumbnail cache cleared."))

    def job_slot_result(self, job):

        if job.error():
            job.ui().showErrorMessage()
