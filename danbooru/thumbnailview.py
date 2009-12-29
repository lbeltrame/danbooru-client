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

    """Class that handles the thumbnails. It is a modified QWidget that keeps
    track of the URL of the full image, the DanbooruItem associated to it, and
    the actual iamge (a pixmap). It contains a QCheckBox that is used for
    selecting the image for batch download."""

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

        # Remove the accelerator, we don't want it
        KAcceleratorManager.setNoAccel(self.checkbox)
        self.checkbox.setSizePolicy(QSizePolicy.Fixed,
                                    QSizePolicy.Fixed)
        self.layout.addWidget(self.checkbox)

        # FIXME: Hack to make sure there's enough space around the image,
        # so that things to do not look as cramped

        self.layout.setSpacing(6)

    def label_text(self):

        "Adds information on the item stored, which will be then shown."

        if self.data is not None:
            height = self.data.height
            width = self.data.width
            size = self.data.size / float(1024000)
            rating = self.data.rating

            width = "Width: %d pixels" % width
            size = "Size: %1.2f Mb" % size
            height = "Height: %d pixels" % height
            rating = "Rating: %s" % rating

            text = "\n".join((width, height, size, rating))
        else:
            text = None

        return text


class ThumbnailView(QTableWidget):

    """Class used to show the thumbnails retrieved from a Danbooru board. It is
    a subclass of QTableWidget, with some modifications. The number of columns
    can be set, and it follows the preferences set in the main application.

    This class provides two custom signals:

        - thumbnailDownloaded, used to notify other parts of the code when a
        thumbnail is going to be displayed.
        - downloadCompleted,used to notify that all the thumbnails have been
        downloaded
    """

    # Signals

    thumbnailDownloaded = pyqtSignal()
    downloadCompleted = pyqtSignal()

    def __init__(self, api_data, preferences, parent=None):

        """Initialize a new ThumbnailView. api_data is a reference to a
        Danbooru object, preferences a reference to the KConfigXT
        instance."""

        super(ThumbnailView, self).__init__(parent)

        self.setColumnCount(preferences.column_no)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.setShowGrid(False)

        self.__max_columns = preferences.column_no
        self.__column_index = 0
        self.__row_index = 0
        self.__preferences = preferences

        self.api_data = api_data
        self.__items = list()

        self.itemClicked.connect(self.retrieve_url)
        self.api_data.dataDownloaded.connect(self.process_thumbnails)

    def __len__(self):

        "Returns the number of URLs stored."

        return len(self.__items)

    def retrieve_url(self, item):

        """Function that performs actions on the currently clicked thumbnail
        (called from the itemClicked signal). It pops up a (modal) dialog
        asking for actions to perform."""

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

        """This function creates, starting from a DanbooruItem object and a
        pixmap (retrieved from the service), a ThumbnailViewItem that is then
        returned to be added into the table widget of the ThumbnailView. If the
        item or the pixmap are invalid, None is returned."""

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

        """Function that inserts ThumbnailViewItems into the ThumbnailView's
        table widget. Columns and rows index are tracked so that the specific
        parameters asked by the user are upheld. It emits thumbnailDownloaded
        once each item has been added."""

        if self.__column_index >= self.__max_columns:
            self.__row_index += 1
            self.__column_index = 0

        self.setCellWidget(self.__row_index, self.__column_index,
                           thumbnail_item)

        self.__column_index += 1
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        thumbnail_item.label.leftClickedUrl.connect(self.retrieve_url)

        # For some reason cellWidget(row, col) returns None, so we keep an
        # internal list of items

        self.__items.append(thumbnail_item)
        self.thumbnailDownloaded.emit()

    def clear_items(self):

        """Clears the internal list of items. Not needed anymore since the
        addition of pagination support."""

        self.__items = list()
        self.__row_index = 0
        self.__column_index = 0

    def items(self):

        """Generator function that yields each ThumbnailViewItem stored in the
        internal list."""

        if not self.__items:
            return
        for item in self.__items:
            yield item

    def setup_rows(self, item_no):

        """Sets up the proper number of rows depending on the items that have
        been stored in the API data object."""

        max_columns = self.__max_columns

        if len(self.api_data.data) <= max_columns:
            max_columns = item_no
            self.setRowCount(1)
        else:
            result = item_no // max_columns
            self.setRowCount(result + 1)

    def process_thumbnails(self, url, pixmap):

        """Function that processes thumbnails and creates ThumbnailViewItems
        that wil be later inserted into the table widget. It is actually a slot
        called by dataDownloaded, from which it gets the URL and the pixmap.
        Said URL is used to retrieve then the full DanbooruItem from the
        retrieved API data. Once we reach the last item, the dataDownloaded
        signal is disconnected, because otherwise even data sent to other
        thumbnailviews (multi-page setting) would be displayed."""

        # Empty data is worthless: skip!
        if url.isEmpty() or pixmap.isNull():
            return

        item_url = unicode(url.prettyUrl())
        name = url.fileName()
        post_data = self.api_data.data[item_url]

        item = self.create_image_item(pixmap, post_data)
        self.insert_items(item)

        # To support pagination, disconnect after we have reached the last
        # item, so that the data won't be sent to all thumbnailviews

        if self.api_data.data[-1] == post_data:
            self.api_data.dataDownloaded.disconnect()
            self.downloadCompleted.emit()

    def display_thumbnails(self):

        """This function starts the thumbnail retrieval and display. First it
        sets up the right rows in the widget, depending on the data, then it
        gets every image from the thumbnail URLs."""

        self.setup_rows(len(self.api_data.data))

        for item in self.api_data.data:
            self.api_data.get_image(item.thumbnail_url)

    def selected_images(self):

        """Returns a list of the items that have been checked. Used for batch
        downloading."""

        if not self.__items:
            return

        selected_items = list()

        for item in self.items():

            if item.checkbox.isChecked():
                selected_items.append(item.data.full_url)

        return selected_items
