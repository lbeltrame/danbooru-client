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

import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyKDE4.kdecore import *
from PyKDE4.kdeui import *
from PyKDE4.kio import KIO

class ThumbnailView(QWidget):

    def __init__(self, urls, cache, parent=None):

        #FIXME: Pass a dictionary of parameters, much better
        super(ThumbnailView, self).__init__(parent)
        
        self.urls = urls
        self.cache = cache
        self.column_index = 0
        self.max_row_items = 3
        self.row_index = 0

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

    def insert_items(self, widget):

        if self.column_index >= self.max_row_items:
            self.row_index += 1
            self.column_index = 0
        self.layout.addWidget(widget, self.row_index, self.column_index)
        self.column_index += 1

    def create_image_label(self, image=None, pixmap=None):
        
        label = QLabel()
        try:
            pixmap = QPixmap.fromImage(image) if not pixmap else pixmap
        except TypeError:
            pixmap = QPixmap()
        
        if pixmap.isNull():
            return
        
        label.setPixmap(pixmap)
        
        return label, pixmap
          
    def retrieve_thumbnails(self):
        
        for url in self.urls:
            name = url.fileName()
            pixmap = QPixmap()

            if not self.cache.find(name, pixmap):
                tempfile = KTemporaryFile()

                if tempfile.open():
                    flags = KIO.JobFlags(KIO.Overwrite | KIO.HideProgressInfo)
                    job = KIO.file_copy(KUrl(url), KUrl(tempfile.fileName()),
                                        -1, flags)
                    job.ui().setWindow(self)
                    
                    if KIO.NetAccess.synchronousRun(job, self):
                        self.process_thumbnails(job)
                        KIO.NetAccess.removeTempFile(tempfile.fileName())
            else:
                label, pixmap = self.create_image_label(pixmap=pixmap)
                if label is not None:
                    self.insert_items(label)

    def process_thumbnails(self, job):

        img = QImage()
        dest = job.destUrl()
        img.load(dest.path())

        if not img.isNull():

            label, pixmap = self.create_image_label(image=img)
            
            if label is not None:
                self.insert_items(label)
                name = job.srcUrl().fileName()
                      
                if not self.cache.find(name, pixmap):
                    self.cache.insert(name, pixmap)

        time.sleep(1) #TODO: Make configurable
