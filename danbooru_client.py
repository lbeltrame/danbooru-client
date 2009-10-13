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

from __future__ import division

import sys
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

import imagewidget
import fetchdialog
import connect_dialog

class MainWindow(KXmlGuiWindow):

    def __init__(self):

        KXmlGuiWindow.__init__(self)
        self.cache = KPixmapCache("danbooru")
        self.welcome = QLabel("Welcome to Danbooru Client!")
        self.welcome.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.welcome)
        self.setup_config()
        self.setup_actions()

        self.progress = None
        self.thumbnailview = None
        self.__step = 0

    def setup_config(self):

        #FIXME: Temporary, to test things, before moving to KConfigXT
        self.config = KGlobal.config()
        self.general_config = KConfigGroup(self.config, "General")
        url_list = self.general_config.readEntry("lastVisited",QStringList())
        self.url_history = url_list.toStringList()

    def setup_actions(self):

        connect_action = KAction(KIcon("document-open-remote"),
                                 i18n("Connect"), self)
        fetch_action = KAction(KIcon("download"), i18n("Fetch"), self)

        connect_default = KAction.ShortcutTypes(KAction.DefaultShortcut)
        connect_active = KAction.ShortcutTypes(KAction.ActiveShortcut)

        connect_action.setShortcut(QKeySequence.Open,
                                   connect_default | connect_active)
        fetch_action.setShortcut(QKeySequence.Find,
                                 connect_default | connect_active)

        self.actionCollection().addAction("connect", connect_action)
        self.actionCollection().addAction("fetch", fetch_action)

        KStandardAction.quit (self.close, self.actionCollection())
        KStandardAction.preferences(self.prefs_test, self.actionCollection())

        connect_action.triggered.connect(self.connect_danbooru)
        fetch_action.triggered.connect(self.fetch)

        self.setupGUI(QSize(300,200), KXmlGuiWindow.Default,
                      os.path.join(sys.path [0], "danbooruui.rc"))

    def prefs_test(self):
        print "Config button clicked"

    def connect_danbooru(self, ok):

        dialog = connect_dialog.ConnectDialog(self.url_history, self)

        if dialog.exec_():
            self.api = dialog.danbooru_api()
            self.general_config.writeEntry("lastVisited", dialog.url_history())
            self.general_config.config().sync()
            self.statusBar().showMessage("Connected to %s" % self.api.url,  3000)

    def setup_area(self):

        self.thumbnailview = imagewidget.ThumbnailView(self.api,
                                                       cache=self.cache)
        self.setCentralWidget(self.thumbnailview)
        self.thumbnailview.thumbnailDownloaded.connect(self.update_progress)

    def update_progress(self):

        if self.progress is None:
            return

        self.progress.progressBar().setValue(self.__step)
        self.__step += 1

    def retrieve(self, tags, limit):

        posts = self.api.get_post_list(limit=limit, tags=tags)

        if not posts:
            return

        urls = self.api.get_thumbnail_urls()

        max_steps = len(urls)

        self.progress = KProgressDialog(self, "Retrieving", "Retrieving images...")
        self.progress.adjustSize()
        self.progress.setAutoClose(True)
        self.progress.setAllowCancel(False)
        self.progress.progressBar().setMaximum(max_steps)

        self.thumbnailview.display_thumbnails(urls)

        # Reset the counter in case of subsequent fetches
        self.__step = 0

    def clear(self):

        if self.thumbnailview is None:
            return

        self.thumbnailview.clear()

    def fetch(self, ok):

        if not self.api:
            return

        self.clear()

        dialog = fetchdialog.FetchDialog(self)

        if dialog.exec_():
            tags = dialog.tags()
            limit = dialog.limit()

            self.setup_area()
            self.retrieve(tags, limit)

        else:
            return

def main():

    app_name="DanbooruRetrieve"
    catalog = ""
    program_name = ki18n("Danbooru Client")
    version = "1.0"
    description = ki18n("A client for Danbooru sites.")
    license = KAboutData.License_GPL
    copyright = ki18n("(C) 2009 Luca Beltrame")
    text = ki18n("Some descriptive text goes here.")
    home_page = "http://www.dennogumi.org"
    bug_email = "einar@heavensinferno.net"

    about_data = KAboutData(app_name, catalog, program_name, version, description,
                        license, copyright, text, home_page, bug_email)

    KCmdLineArgs.init(sys.argv, about_data)
    app = KApplication()
    mw = MainWindow()
    mw.show()
    app.exec_()

if __name__ == '__main__':
    main()
