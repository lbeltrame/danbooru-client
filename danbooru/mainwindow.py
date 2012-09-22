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

# TODO: Move connection dialog to a widget inside centralWidget

from __future__ import division

import sys
import os

from PyQt4.QtCore import Qt, QSize, QVariant
from PyQt4.QtGui import (QLabel, QPixmap, QProgressBar, QSizePolicy,
                         QKeySequence, QDockWidget)
from PyKDE4.kdecore import KStandardDirs, KUrl, i18n
from PyKDE4.kdeui import (KXmlGuiWindow, KPixmapCache, KAction,
                          KStandardAction, KIcon, KConfigDialog,
                          KToggleAction, KDualAction, KStandardShortcut)
from PyKDE4.kio import KFileDialog, KIO

import preferences
import thumbnailarea
import tagwidget
import fetchdialog
import connectdialog
import connectwidget
import poolwidget
import danbooru2nepomuk

class MainWindow(KXmlGuiWindow):

    "Class which displays the main Danbooru Client window."

    def __init__(self,  *args):

        "Initialize a new main window."

        super(MainWindow,  self).__init__(*args)
        self.cache = KPixmapCache("danbooru")
        self.preferences = preferences.Preferences()
        self.api = None
        self.connect_widget = None
        self.__ratings = None
        self.__step = 0

        self.url_list = self.preferences.boards_list
        self.max_retrieve = self.preferences.thumbnail_no

        self.statusbar = self.statusBar()
        self.progress = QProgressBar()
        self.thumbnailarea = None
        self.tag_dock = None
        self.pool_dock = None

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
        self.pool_toggle_action = KToggleAction(KIcon("image-x-generic"),
                                            i18n("Pools"), self)
        self.tag_display_action = KDualAction(i18n("Show tags"),
                                              i18n("Hide tags"),
                                              self)
        self.tag_display_action.setIconForStates(KIcon("image-x-generic"))
        self.tag_display_action.setEnabled(False)

        # Shortcuts
        connect_default = KAction.ShortcutTypes(KAction.DefaultShortcut)
        connect_active = KAction.ShortcutTypes(KAction.ActiveShortcut)

        self.connect_action.setShortcut(KStandardShortcut.open())
        self.fetch_action.setShortcut(KStandardShortcut.find())

        self.fetch_action.setEnabled(False)
        self.batch_download_action.setEnabled(False)
        self.pool_toggle_action.setEnabled(False)

    def setup_action_collection(self):

        """Set up the action collection by adding the actions."""

        action_collection = self.actionCollection()

        # Addition to the action collection
        action_collection.addAction("connect", self.connect_action)
        action_collection.addAction("fetch", self.fetch_action)
        action_collection.addAction("clean", self.clean_action)
        action_collection.addAction("batchDownload", self.batch_download_action)
        action_collection.addAction("poolDownload", self.pool_toggle_action)
        action_collection.addAction("tagDisplay", self.tag_display_action)

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
        self.pool_toggle_action.toggled.connect(self.pool_toggle)
        self.tag_display_action.activeChangedByUser.connect(self.tag_display)

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

    def setup_connections(self):

        """Set up connections for post and tag retrieval."""

        if self.api is None:
            return

        self.api.postRetrieved.connect(self.update_progress)
        self.api.postDownloadFinished.connect(self.download_finished)
        self.api.tagRetrieved.connect(self.tag_dock.widget().add_tags)
        self.tag_dock.widget().itemDoubleClicked.connect(
            self.fetch_tagged_items)

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

        if self.connect_widget is None:
            self.connect_widget = connectwidget.ConnectWidget(self.url_list,
                                                              self)
            self.connect_widget.connectionEstablished.connect(
                self.handle_connection)
            self.connect_widget.rejected.connect(self.restore)

            self.statusbar.addPermanentWidget(self.connect_widget, 100)
        else:
            self.statusbar.addPermanentWidget(self.connect_widget, 100)
            self.connect_widget.show()

    def restore(self):

        self.statusbar.removeWidget(self.connect_widget)

    def handle_connection(self, connection):

        self.api = None
        self.api = connection
        self.api.cache = self.cache

        self.thumbnailarea = None
        self.pool_dock = None
        self.statusbar.removeWidget(self.connect_widget)

        if self.pool_dock is not None:
            self.pool_dock.hide()
            self.pool_dock.widget().clear()
            self.pool_toggle_action.setChecked(False)

        if self.thumbnailarea is not None:
            #TODO: Investigate usability
            self.clear(clear_pool=True)
            self.thumbnailarea.clear()
            self.thumbnailarea.api_data = self.api
            self.setup_connections()

        self.api.cache = self.cache

        self.statusBar().showMessage(i18n("Connected to %s" % self.api.url),
                                     3000)
        self.fetch_action.setEnabled(True)

        # Set up pool widget

        pool_widget = poolwidget.DanbooruPoolWidget(self.api)
        self.pool_dock = QDockWidget("Pools", self)
        self.pool_dock.setObjectName("PoolDock")
        self.pool_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.pool_dock.setWidget(pool_widget)
        self.pool_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.pool_dock)
        self.pool_dock.widget().poolDownloadRequested.connect(
            self.pool_prepare)
        self.pool_dock.hide()

        self.pool_toggle_action.setEnabled(True)

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

            if self.thumbnailarea is None:
                self.setup_area()

            if self.tag_dock is not None:
                self.tag_dock.widget().clear()

            self.thumbnailarea.post_limit = limit
            blacklist= list(self.preferences.tag_blacklist)
            self.api.get_post_list(tags=tags, limit=limit,
                                   rating=max_rating,
                                   blacklist=blacklist)

            tags = [item for item in tags if item]

            if not tags:
                # No related tags, fetch the most recent 20
                tags = ""
                self.api.get_tag_list(name=tags,blacklist=blacklist,
                                      limit=20)
            else:
                self.api.get_related_tags(tags=tags, blacklist=blacklist)

    def fetch_tagged_items(self, item):

        """Fetch items found in the tag list widget."""

        tag_name = unicode(item.text())
        self.clear()

        blacklist = self.preferences.tag_blacklist
        limit = self.preferences.thumbnail_no
        rating = self.preferences.max_allowed_rating

        self.api.get_post_list(page=1, tags=[tag_name],
                                blacklist=blacklist,
                                limit=limit,
                                rating=rating)
        self.api.get_related_tags(tags=[tag_name], blacklist=blacklist)

    def pool_toggle(self, checked):

        "Toggle the presence/absence of the pool dock."

        if not self.api:
            return

        if not checked:
            self.pool_dock.hide()
        else:
            self.pool_dock.show()

    def pool_prepare(self, pool_id):

        """Prepare the central area for pool image loading."""

        if self.thumbnailarea is None:
            self.setup_area()
        else:
            self.clear(clear_pool=False)

        self.api.get_pool(pool_id)

    def batch_download(self, ok):

        "Download images in batch."

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

            file_name = KUrl(file_url).fileName()
            destination.addPath(file_name)

            job = KIO.file_copy(KUrl(file_url), destination, -1)
            job.setProperty("tags", QVariant(tags))
            job.result.connect(self.batch_download_slot)

    def setup_area(self):

        "Set up the central widget to display thumbnails."

        self.thumbnailarea = thumbnailarea.DanbooruTabWidget(self.api,
            self.preferences, self)

        self.setCentralWidget(self.thumbnailarea)

        # Set up tag widget

        blacklist = self.preferences.tag_blacklist
        tag_widget = tagwidget.DanbooruTagWidget(blacklist, self)
        self.tag_display_action.setActive(True)
        self.tag_display_action.setEnabled(True)
        self.tag_dock = QDockWidget("Similar tags", self)
        self.tag_dock.setObjectName("TagDock")
        self.tag_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.tag_dock.setWidget(tag_widget)
        self.tag_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.RightDockWidgetArea, self.tag_dock)

        # Container signal-slot connections

        self.setup_connections()

    def download_finished(self):

        """Slot called when all the data has been completed. Clears the progress
        bar and resets it to 0."""

        if not self.batch_download_action.isEnabled():
            self.batch_download_action.setEnabled(True)

        self.__step = 0
        self.progress.hide()

    def update_progress(self):

        "Update the progress bar."

        if not self.progress.isVisible():
            self.progress.show()

        self.__step += 1
        self.progress.setValue(self.__step)

    def clear(self, clear_pool=True):

        "Clear the central widget."

        if self.thumbnailarea is None:
            return

        self.thumbnailarea.clear()
        self.tag_dock.widget().clear()
        if clear_pool:
            self.pool_dock.widget().clear()
        self.batch_download_action.setEnabled(False)

    def clean_cache(self):

        "Purge the thumbnail cache."

        self.cache.discard()
        self.statusBar().showMessage(i18n("Thumbnail cache cleared."))

    def batch_download_slot(self, job):

        """Slot called when doing batch download, for each file retrieved.

        If Nepomuk tagging is enabled, each file is tagged using the item's
        respective tags.

        """

        if job.error():
            job.ui().showErrorMessage()
        else:
            if self.preferences.nepomuk_enabled:
                tags = job.property("tags").toPyObject()
                danbooru2nepomuk.tag_danbooru_item(job.destUrl().path(),
                                                   tags)

    def tag_display(self, state):

        """Display or hide the tag dock."""

        if self.tag_dock is None:
            self.tag_display_action.setActive(False)
            return

        if state:
            self.tag_dock.show()
        else:
            self.tag_dock.hide()