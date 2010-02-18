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


'''
File: thumbnailarea.py
Author: Luca Beltrame
Description: Module handling the thumbnail area, which presents several
ThumbnailViews using a tabbed interface.
'''

from functools import partial

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QWidget, QLabel
from PyKDE4.kdecore import i18n
from PyKDE4.kdeui import KAcceleratorManager

import thumbnailview
from ui.ui_thumbnailarea import Ui_ThumbnailArea


class ThumbnailArea(QWidget, Ui_ThumbnailArea):

    """Class that provides an area where individual ThumbnailViews (from
    thumbnailview.py) can be placed in, using a tabbed interface. The class uses
    an internal list for each page added, to avoid garbage collection issues.
    Methods to create tabs are not called directly, but are instead slots called
    upon by signal.

    This class provides the following custom signals:

        - downloadDone - used to relay the downloadCompleted signal from
        the ThumbnailView;
        - thumbnailRetrieved - used to rely the thumbnailDownloaded signal from
        the ThumbnailView."""

    downloadDone = pyqtSignal()
    thumbnailRetrieved = pyqtSignal()

    def __init__(self, api_data=None, preferences=None, parent=None):

        """Initialize a new ThumbnailArea. api_data is a reference to a
        Danbooru object, while preferences is a reference to a
        KConfigXT instance."""

        super(ThumbnailArea, self).__init__(parent)
        self.setupUi(self)

        self.preferences = preferences
        self.api_data = api_data
        self.__pages = list()
        self.__firstpage = True
        self.__current_index = 0

        KAcceleratorManager.setNoAccel(self.thumbnailTabWidget)
        self.nextPageButton.setDisabled(True)

        self.nextPageButton.clicked.connect(self.new_page)
        self.api_data.postDataReady.connect(self.fetch_posts)

    def __iter__(self):

        "Yields every stored page in the thumbnail area."

        for item in self.__pages:
            yield item

    def new_page(self):

        "Slot used to create a new page."

        if self.__firstpage:
            view, index = self.create_tab()
            view.display_thumbnails()
            self.__firstpage = False
        else:
            self.__current_index += 1
            self.nextPageButton.setDisabled(True)
            self.api_data.update(page=self.__current_index + 1)

    def thumbnail_retrieved(self):

        self.thumbnailRetrieved.emit()

    def download_done(self):

        self.downloadDone.emit()

    def create_tab(self):

        """Creates a new tab in the tab widget, and adds it to the internal
        lists. Returns the inserted widget and the index it was inserted in."""

        current_page = self.thumbnailTabWidget.currentIndex() + 1
        next_page = 1 if current_page == 0 else current_page + 1
        page_name = "Page %d" % next_page
        enable_button = partial(self.nextPageButton.setDisabled, False)

        view = thumbnailview.ThumbnailView(self.api_data, self.preferences)

        # PyKDE4 suffers from garbage collection issues with widgets like
        # KPageWidget or KTabWidget. Therefore, we add the item to a list to
        # keep a reference of it around

        self.__pages.append(view)

        view.thumbnailDownloaded.connect(self.thumbnail_retrieved)
        view.downloadCompleted.connect(self.download_done)
        view.downloadCompleted.connect(enable_button)

        index = self.thumbnailTabWidget.addTab(view, page_name)

        return view, index

    def fetch_posts(self):

        """Slot used to fetch posts, calling the display_thumbnail of the
        thumbnail view corresponding to the current index."""

        if not self.api_data.post_data:

            label = QLabel(i18n("No matching posts found for this page."))
            label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.__current_index += 1
            text = "Page %d (empty)" % self.__current_index

            index = self.thumbnailTabWidget.addTab(label, text)
            self.thumbnailTabWidget.setCurrentIndex(index)
            self.nextPageButton.setDisabled(False)
            return

        if self.__firstpage:
            self.new_page()
        else:
            view, index = self.create_tab()
            view.display_thumbnails()
            self.thumbnailTabWidget.setCurrentIndex(index)

    def clear(self):

        "Removes all pages in the widget."

        self.thumbnailTabWidget.clear()
        self.__pages = list()
        self.__firstpage = True
        self.__current_index = 0
        self.nextPageButton.setDisabled(True)

    def selected_images(self):

        "Returns a list of the selected images in all pages."

        images = list()

        for view in self:

            selected = view.selected_images()

            if selected:
                images.extend(selected)

        return images

    def update_data(self, api_data):

        "Updates the API data."

        self.api_data = api_data

        # As we changed object, the connection to the item points still to the
        # old one. Therefore, we need to re-connect the signal again

        self.api_data.postDataReady.connect(self.fetch_posts)
