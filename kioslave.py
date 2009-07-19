#!/usr/bin/env python

import sys
import os
import time
import json

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyKDE4.kdecore import *
from PyKDE4.kdeui import *
from PyKDE4.kio import KIO


app_name="helloworld"
catalog = ""
program_name = ki18n("helloworld")
version = "1.0"
description = ki18n("Test")
license = KAboutData.License_GPL
copyright = ki18n("(C) 2009 Luca Beltrame")
text = ki18n("succhiate")
home_page = "http://www.dennogumi.org"
bug_email = "einar@heavensinferno.net"

about_data = KAboutData(app_name, catalog, program_name, version, description,
                        license, copyright, text, home_page, bug_email)

class MainWindow(KXmlGuiWindow):

    def __init__(self):
        KXmlGuiWindow.__init__(self)
        self.area = QWidget()
        self.layout = QGridLayout(self.area)
        self.temp = KPushButton("Start operation")
        #self.urls = [KUrl("http://www.dennogumi.org/wp-content/gallery/cache/275__320x240_img_0293.jpg"),
        #        KUrl("http://www.dennogumi.org/wp-content/themes/vigilance/images/sidebar/desktop.png")]

        self.urls = list()

        self.setCentralWidget(self.temp)
        self.start_index = 0
        self.firstrun = True
        self.cache = KPixmapCache("danbooru")
        self.get_api()
        self.temp.clicked.connect(self.get_data)
    
    def get_api(self):
        api_url = "http://konachan.net/post/index.json?limit=5"
        job = KIO.storedGet(KUrl(api_url))
        self.connect(job, SIGNAL("finished(KJob*)"), self.process_api)

    def process_api(self, job):
        data = job.data()
        values = json.loads(str(data))
        for item in values:
            url = item["preview_url"]
            self.urls.append(url)
        self.urls = [KUrl(item) for item in self.urls]

    def get_data(self):
        
        for url in self.urls:
            name = url.fileName()
            pixmap = QPixmap()

            if not self.cache.find(name, pixmap):
                arfa = KIO.storedGet(url, KIO.NoReload, KIO.DefaultFlags)
                # Won't work using new-style signal overloads
                self.connect(arfa, SIGNAL("finished(KJob*)"), self.dataishere)
            else:
                self.setCentralWidget(self.area)
                label = QLabel()
                label.setPixmap(pixmap)
                self.layout.addWidget(label, 0, self.start_index)
                self.start_index += 1
                self.area.setLayout(self.layout)
        self.get_api()

    def dataishere(self, job):

        img = QImage()
        data = job.data()
        img.loadFromData(data)

        if not img.isNull():
            label = QLabel()
            pixmap = QPixmap(img)
            label.setPixmap(pixmap)
            self.layout.addWidget(label, 0, self.start_index)
            self.start_index += 1

            name = job.url().fileName()
            
            if not self.cache.find(name, pixmap):
                self.cache.insert(name, pixmap)

        if self.firstrun:
            self.setCentralWidget(self.area)
            self.area.setLayout(self.layout)
            self.firstrun =False

        time.sleep(2)

KCmdLineArgs.init(sys.argv, about_data)
app = KApplication()
mw = MainWindow()
mw.show()
app.exec_()
