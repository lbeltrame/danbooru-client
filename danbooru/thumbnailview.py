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

from functools import partial

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui

import PyKDE4.kdecore as kdecore
import PyKDE4.kdeui as kdeui
import PyKDE4.kio as kio

from danboorupostwidget import DanbooruPostWidget

_TRANSLATED_RATINGS = dict(
    Safe=kdecore.i18nc("Image for all audiences", "Safe"),
    Questionable=kdecore.i18nc("Image with suggestive themes", "Questionable"),
                          Explicit=kdecore.i18nc("Image with explicit content",
                              "Explicit")
    )



class DanbooruPostView(QtGui.QTableWidget):

    """A class to show the thumbnails retrieved from a Danbooru board."""

    # Signals

    fetchTags = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, api_data, preferences, parent=None):

        super(DanbooruPostView, self).__init__(parent)

        self.__max_columns = preferences.column_no
        self.__column_index = 0
        self.__row_index = 0
        self.preferences = preferences
        self.__locked = False

        self.api_data = api_data
        self.__items = list()

        self.setColumnCount(self.__max_columns)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()

        resize_mode = QtGui.QHeaderView.ResizeToContents
        self.horizontalHeader().setResizeMode(resize_mode)
        self.verticalHeader().setResizeMode(resize_mode)
        self.setShowGrid(False)
        #self.setDisabled(True)

        enable_ = partial(self.setDisabled, False)

        self.itemClicked.connect(self.retrieve_url)
        self.api_data.postRetrieved.connect(self.create_post)
        #self.api_data.postDownloadFinished.connect(enable_)
        self.api_data.postDownloadFinished.connect(self.stop_download)

    def __len__(self):

        "Returns the number of URLs stored."

        return len(self.__items)


    def stop_download(self):

        self.__locked = True

    def retrieve_url(self, item):

        """Function that performs actions on the currently clicked thumbnail
        (called from the itemClicked signal). It pops up a (modal) dialog
        asking for actions to perform."""

        row = self.currentRow()
        column = self.currentColumn()

        widget = self.cellWidget(row, column)

        if widget is None:
            return

        pixmap = widget.data.pixmap
        tags = widget.data.tags

        dialog = actiondialog.ActionDialog(item, pixmap=pixmap,
                                           preferences=self.preferences,
                                           tags=tags,
                                           board_url=self.api_data.url,
                                           parent=self)

        if not dialog.exec_():
            return

    def items(self):

        """Generator function that yields each ThumbnailViewItem stored in the
        internal list."""

        if not self.__items:
            return
        for item in self.__items:
            yield item

    def create_post(self, data):

        """Function that processes thumbnails and creates ThumbnailViewItems
        that wil be later inserted into the table widget. It is actually a slot
        called by dataDownloaded, from which it gets the URL and the pixmap.
        Said URL is used to retrieve then the full DanbooruItem from the
        retrieved API data. Once we reach the last item, the dataDownloaded
        signal is disconnected, because otherwise even data sent to other
        thumbnailviews (multi-page setting) would be displayed."""

        if self.__locked:
            return

        item = DanbooruPostWidget(data)

        self.__items.append(item)

        if self.rowCount() == 0:
            self.insertRow(0)

        if self.__column_index >= self.columnCount():
            self.__column_index = 0
            self.__row_index += 1
            self.insertRow(self.rowCount())

        self.setCellWidget(self.__row_index, self.__column_index, item)
        self.__column_index += 1

        self.resizeRowsToContents()
        self.resizeColumnsToContents()

        item.url_label.leftClickedUrl.connect(item.view)

    def selected_images(self):

        """Returns a list of the items that have been checked. Used for batch
        downloading."""

        if not self.__items:
            return

        selected_items = [item for item in self.items()
                          if item.checkbox.isChecked()]

        return selected_items
