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

class TestDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super(TestDelegate, self).__init__(parent)

    def sizeHint(self, option, index):

        variant = index.model().data(index)

        if variant.isNull():
            return QStyledItemDelegate.sizeHint(self, option, index)

        icon = QIcon(variant)

        if icon.isNull():
            return QStyledItemDelegate.sizeHint(self, option, index)

        size = icon.actualSize(QSize(1024, 1024))

        return QSize(size.width()+3, size.height()+3)

class ThumbnailViewItem(QTableWidgetItem):

    def __init__(self, image=None, url=None, data=None):

        super(ThumbnailViewItem, self).__init__()
        self.url = url

        if image is not None:
            self.image = QIcon(image)

        self.setIcon(self.image)

        # Avoid empty lists as well
        if data:
            height = data.height
            width = data.width
            size = data.size / float (1024000)

        height = "Height: %d pixels" % height
        width = "Width: %d pixels" % width
        size = "Size: %d Mb" % size

        text = "\n".join((height, width, size))
        self.setToolTip(text)


class ThumbnailView(QTableWidget):

    thumbnailDownloaded = pyqtSignal() # To notify changes

    def __init__(self, api_data, cache=None, columns=3, parent=None):
        super(ThumbnailView, self).__init__(parent)

        self.setColumnCount(columns)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.setShowGrid(False)
        #self.setItemPrototype(ThumbnailViewItem)
        self.setIconSize(QSize(1024, 1024))
        #self.setItemDelegate(TestDelegate(self))

        self.__max_columns = columns
        self.__column_index = 0
        self.__max_row_items = 3
        self.__row_index = 0

        self.api_data = api_data
        self.cache = cache

        self.itemClicked.connect(self.retrieve_url)

    def retrieve_url(self, item):
        print "Click logitech click"
        print item.url

    def create_image_item(self, pixmap=None, item=None):

        pixmap = QPixmap() if not pixmap else pixmap

        if pixmap.isNull():
            return

        if item is None:
            return

        full_img_url = item.full_url
        item = ThumbnailViewItem(image=pixmap, url=full_img_url,
                                 data=item)
        return item

    def insert_items(self, thumbnail_item):

        if self.__column_index >= self.__max_columns:
            self.__row_index += 1
            self.__column_index = 0

        self.setItem(self.__row_index, self.__column_index, thumbnail_item)
        self.__column_index += 1
        self.resizeRowsToContents()
        self.resizeColumnsToContents()

        self.thumbnailDownloaded.emit()

    def setup_rows(self, item_no):

        result = item_no // self.__max_columns
        self.setRowCount(result+1)

    def display_thumbnails(self):

        self.setup_rows(len(self.api_data.data))

        # This works because the list keep stuff in order
        for index, item in enumerate(self.api_data.data):

            pixmap, name = self.api_data.get_image(item.thumbnail_url)
            item = self.create_image_item(pixmap, item)
            if item:
                self.insert_items(item)
            else:
                continue

            if not self.cache.find(name, pixmap):
                self.cache.insert(name, pixmap)
            time.sleep(1)


