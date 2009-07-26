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
        api_init = api.Danbooru("http://konachan.com/")
        posts = api_init.get_post_list()
        urls = api_init.get_thumbnail_urls(posts)

        self.temp = KPushButton("Start operation")
        self.setCentralWidget(self.temp)
        self.view = imagewidget.ThumbnailView(urls, self.cache)
        self.temp.clicked.connect(self.start)

    def start(self):
        self.setCentralWidget(self.view)
        self.view.retrieve_thumbnails()
    
KCmdLineArgs.init(sys.argv, about_data)
app = KApplication()
mw = MainWindow()
mw.show()
app.exec_()
