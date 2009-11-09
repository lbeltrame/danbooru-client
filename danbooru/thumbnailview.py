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
File: thumbnailview.py
Author: Luca Beltrame
Description: Main widget to display and download thumbnails
'''

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import (QLabel, QWidget, QTableWidget, QVBoxLayout,
                         QHeaderView, QPixmap, QCheckBox, QSizePolicy)

from PyKDE4.kdecore import KUrl, i18n
from PyKDE4.kdeui import KUrlLabel, KAcceleratorManager

import actiondialog

#TODO: Switch to model/view

class ThumbnailViewItem(QWidget):

    def __init__(self, image=None, url=None, data=None):

        super(ThumbnailViewItem, self).__init__()

        self.label = KUrlLabel()

        self.data = data
        label_text = self.label_text()
        self.label.setUrl(url)

        if image is not None:
            self.label.setPixmap(image)

        self.label.setUseTips(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setTipText(KUrl(self.data.full_url).fileName())

        self.__text_label = QLabel()

        self.layout = QVBoxLayout(self)
        self.layout.addStretch()
        self.layout.addWidget(self.label)

        if label_text is not None:
            self.__text_label.setText(label_text)
            self.layout.addWidget(self.__text_label)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(False)
        self.checkbox.setText(i18n("Select"))
        KAcceleratorManager.setNoAccel(self.checkbox)
        self.checkbox.setSizePolicy(QSizePolicy.Fixed,
                                    QSizePolicy.Fixed)
        self.layout.addWidget(self.checkbox)

        self.layout.setSpacing(6) # Ugly hack!

    def label_text(self):

        if self.data is not None:
            height = self.data.height
            width = self.data.width
            size = self.data.size / float (1024000)

            width = "Width: %d pixels" % width
            size = "Size: %1.2f Mb" % size
            height = "Height: %d pixels" % height

            text = "\n".join((width, height, size))
        else:
            text = None

        return text


class ThumbnailView(QTableWidget):

    thumbnailDownloaded = pyqtSignal() # To notify changes

    def __init__(self, api_data, preferences, columns=5, parent=None):

        #FIXME: Add docstrings!

        super(ThumbnailView, self).__init__(parent)
        self.setColumnCount(columns)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.setShowGrid(False)

        self.__max_columns = columns
        self.__column_index = 0
        self.__row_index = 0
        self.__preferences = preferences

        self.api_data = api_data
        self.__items = list()

        self.itemClicked.connect(self.retrieve_url)
        self.api_data.dataDownloaded.connect(self.process_thumbnails)

    def retrieve_url(self, item):

        row = self.currentRow()
        column = self.currentColumn()

        widget = self.cellWidget(row, column)
        pixmap = widget.label.pixmap()

        dialog = actiondialog.ActionDialog(item, pixmap=pixmap,
                                           preferences=self.__preferences,
                                           parent=self)

        if not dialog.exec_():
            return

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

        self.setCellWidget(self.__row_index, self.__column_index, thumbnail_item)

        self.__column_index += 1
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        thumbnail_item.label.leftClickedUrl.connect(self.retrieve_url)

        # As for some reason cellWidget(row, col) returns None
        self.__items.append(thumbnail_item)

        self.thumbnailDownloaded.emit()

    def clear_items(self):
        self.__items = list()
        self.__row_index = 0
        self.__column_index = 0

    def update_data(self, api_data):
        self.api_data = api_data
        # Reconnect, the signal changed
        self.api_data.dataDownloaded.connect(self.process_thumbnails)

    def items(self):
        if not self.__items:
            return
        for item in self.__items:
            yield item

    def setup_rows(self, item_no):

        max_columns = self.__max_columns

        if len(self.api_data.data) <= max_columns:
            max_columns = item_no
            self.setRowCount(1)
        else:
            result = item_no // max_columns
            self.setRowCount(result+1)

    def process_thumbnails(self, url, pixmap):

        # Empty data is worthless: skip!
        if url.isEmpty() or pixmap.isNull():
            return

        item_url = unicode(url.prettyUrl())
        name = url.fileName()
        post_data = self.api_data.data[item_url]

        item = self.create_image_item(pixmap, post_data)
        self.insert_items(item)

    def display_thumbnails(self):

        self.setup_rows(len(self.api_data.data))

        for item in self.api_data.data:
            self.api_data.get_image(item.thumbnail_url)

    def selected_images(self):

        if not self.__items:
            return

        selected_items = list()

        for item in self.items():

            if item.checkbox.isChecked():
                selected_items.append(item.data.full_url)

        return selected_items
