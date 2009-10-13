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

#TODO: Switch to model/view

class ThumbnailView(QTableWidget):

    thumbnailDownloaded = pyqtSignal() # To notify changes

    def __init__(self, api_data, cache=None, columns=3, parent=None):
        super(ThumbnailViewNG, self).__init__(parent)

        self.setColumnCount(columns)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.setShowGrid(False)

        self.__max_columns = columns
        self.__column_index = 0
        self.__max_row_items = 3
        self.__row_index = 0

        self.api_data = api_data
        self.cache = cache

    def retrieve_url(self, url):
        print "Click logitech click"

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

    def insert_items(self, imagelabel):

        if self.__column_index >= self.__max_columns:
            self.__row_index += 1
            self.__column_index = 0

        #FIXME: Ugly hack, but works
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(imagelabel)
        layout.addSpacing(6)
        widget.setLayout(layout)

        self.setCellWidget(self.__row_index, self.__column_index, widget)
        self.__column_index += 1
        self.resizeRowsToContents()
        self.resizeColumnsToContents()

        self.thumbnailDownloaded.emit()

    def setup_rows(self, item_no):

        result = item_no // self.__max_columns
        self.setRowCount(result+1)

    def display_thumbnails(self, urls):

        self.setup_rows(len(urls))

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


