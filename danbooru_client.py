#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Copyright 2009 Luca Beltrame <einar@heavensinferno.net>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License, version 2.
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

import sys
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

import imagewidget
import api

app_name="DanbooruRetrieve"
catalog = ""
program_name = ki18n("Danbooru Client")
version = "1.0"
description = ki18n("A client for Danbooru sites.")
license = KAboutData.License_GPL
copyright = ki18n("(C) 2009 Luca Beltrame")
text = ki18n("Test")
home_page = "http://www.dennogumi.org"
bug_email = "einar@heavensinferno.net"

about_data = KAboutData(app_name, catalog, program_name, version, description,
                        license, copyright, text, home_page, bug_email)

class MainWindow(KXmlGuiWindow):

    def __init__(self):
        
        KXmlGuiWindow.__init__(self)
        self.cache = KPixmapCache("danbooru")
        self.config = KGlobal.config()
        self.welcome = QLabel("Welcome to Danbooru Client!")
        self.welcome.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.welcome)
        self.setup_actions()

    def setup_actions(self):

        connect_action = KAction(KIcon("document-open-remote"),
                                 i18n("Connect"), self)
        connect_default = KAction.ShortcutTypes(KAction.DefaultShortcut)
        connect_active = KAction.ShortcutTypes(KAction.ActiveShortcut)
        connect_action.setShortcut(QKeySequence.Open,
                                   connect_default | connect_active)

        self.actionCollection().addAction("connect", connect_action)
        KStandardAction.quit (app.quit, self.actionCollection())
        KStandardAction.preferences(self.prefs_test, self.actionCollection())
        self.setupGUI(QSize(300,200), KXmlGuiWindow.Default,
                      os.path.join(sys.path [0], "danbooruui.rc"))

    def prefs_test(self):
        print "Config button clicked"

    
KCmdLineArgs.init(sys.argv, about_data)
app = KApplication()
mw = MainWindow()
mw.show()
app.exec_()
