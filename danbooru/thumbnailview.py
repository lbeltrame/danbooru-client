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

import actiondialog

_TRANSLATED_RATINGS = dict(
    Safe=kdecore.i18nc("Image for all audiences", "Safe"),
    Questionable=kdecore.i18nc("Image with suggestive themes", "Questionable"),
                          Explicit=kdecore.i18nc("Image with explicit content",
                              "Explicit")
    )


class DanbooruPostWidget(QtGui.QWidget):

    """Widget that displays a DanbooruPost."""

    def __init__(self, danbooru_post, parent=None):

        super(DanbooruPostWidget, self).__init__(parent)

        self.data = danbooru_post

        self.url_label = kdeui.KUrlLabel()
        self.__text_label = QtGui.QLabel()

        label_text = self.label_text()

        self.url_label.setUrl(self.data.file_url)
        self.url_label.setPixmap(self.data.pixmap)

        full_url = kdecore.KUrl(self.data.file_url).fileName()
        self.url_label.setUseTips(True)
        self.url_label.setAlignment(QtCore.Qt.AlignCenter)
        self.url_label.setTipText(full_url)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addStretch()
        self.layout.addWidget(self.url_label)

        if label_text is not None:
            self.__text_label.setText(label_text)
            self.layout.addWidget(self.__text_label)

        self.checkbox = QtGui.QCheckBox()
        self.checkbox.setChecked(False)
        self.checkbox.setText(kdecore.i18n("Select"))

        # Remove the accelerator, we don't want it
        kdeui.KAcceleratorManager.setNoAccel(self.checkbox)

        self.checkbox.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                    QtGui.QSizePolicy.Fixed)
        self.layout.addWidget(self.checkbox)

        # FIXME: Hack to make sure there's enough space around the image,
        # so that things to do not look as cramped

        self.layout.setSpacing(6)

    def label_text(self):

        "Format the text of the item for display."

        height = self.data.height
        width = self.data.width
        file_size = int(self.data.file_size)
        rating = _TRANSLATED_RATINGS[self.data.rating]

        # Properly format the strings according to the locale

        sizestr = kdecore.ki18np("1 pixel", "%1 pixels")
        image_size = kdecore.i18n("Size: %1 x %2",
                                  sizestr.subs(width).toString(),
                                  sizestr.subs(height).toString())
        file_size = kdecore.i18n("File size: %1",
                kdecore.KGlobal.locale().formatByteSize(file_size))
        rating = kdecore.i18n("Rating: %1", rating)

        text = image_size + "\n" + file_size + "\n" + rating

        return text


class DanbooruPostView(QtGui.QTableWidget):

    """A class to show the thumbnails retrieved from a Danbooru board."""

    # Signals

    fetchTags = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, api_data, preferences, parent=None):

        super(DanbooruPostView, self).__init__(parent)

        self.__max_columns = preferences.column_no
        self.__column_index = 0
        self.__row_index = 0
        self.__preferences = preferences
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
        pixmap = widget.data.pixmap
        tags = widget.data.tags

        dialog = actiondialog.ActionDialog(item, pixmap=pixmap,
                                           preferences=self.__preferences,
                                           tags=tags,
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

        item.url_label.leftClickedUrl.connect(self.retrieve_url)

    def selected_images(self):

        """Returns a list of the items that have been checked. Used for batch
        downloading."""

        if not self.__items:
            return

        selected_items = [item for item in self.items()
                          if item.checkbox.isChecked()]

        return selected_items
