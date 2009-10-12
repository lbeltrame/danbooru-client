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

import sip
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

#TODO: Switch to model/view

class ThumbnailView(QWidget):

    thumbnailDownloaded = pyqtSignal() # To notify changes

    def __init__(self,api_data, cache=None, parent=None):

        #FIXME: Use the configured values
        super(ThumbnailView, self).__init__(parent)

        self.column_index = 0
        self.max_row_items = 3
        self.row_index = 0
        self.api_data = api_data
        self.cache = cache
        self.parent = parent
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,
                                       QSizePolicy.MinimumExpanding))

        self.grid_layout = QGridLayout(self)
        self.grid_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.setLayout(self.grid_layout)
        self.grid_layout.setSizeConstraint(QLayout.SetDefaultConstraint)

    def insert_items(self, widget):

        if self.column_index >= self.max_row_items:
            self.row_index += 1
            self.column_index = 0
        self.grid_layout.addWidget(widget, self.row_index, self.column_index)
        self.column_index += 1
        self.adjustSize()

        self.thumbnailDownloaded.emit()

    def create_image_label(self, pixmap=None, index=0):

        label = KUrlLabel()

        pixmap = QPixmap() if not pixmap else pixmap

        if pixmap.isNull():
            return

        label.setPixmap(pixmap)
        full_img_url = self.api_data.get_picture_url(index)
        label.setUrl(full_img_url.toString())
        label.leftClickedUrl.connect(self.retrieve_url)

        return label

    def display_thumbnails(self, urls):

        # This works because the list keep stuff in order
        for index, url in enumerate(urls):

            pixmap, name = self.api_data.get_image(url)
            label = self.create_image_label(pixmap, index)
            if label:
                self.insert_items(label)
            else:
                continue

            if not self.cache.find(name, pixmap):
                self.cache.insert(name, pixmap)
            time.sleep(1)

    def retrieve_url(self, url):
        print "Clicked", url

    def has_items(self):
        pass

    def reset(self):

        pass

