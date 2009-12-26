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

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QWidget
from PyKDE4.kdeui import KAcceleratorManager

import thumbnailview
from ui.ui_thumbnailarea import Ui_ThumbnailArea

class ThumbnailArea(QWidget, Ui_ThumbnailArea):

    downloadCompleted = pyqtSignal()

    def __init__(self, api_data=None, preferences=None, parent=None):

        """Initialize a new ThumbnailArea. api_data is a reference to a Danbooru
        object, while preferences is a reference to a KConfigXT instance."""

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
        self.api_data.dataReady.connect(self.fetch_posts)

    def __iter__(self):

        for item in self.__pages:
            yield item

    def new_page(self):

        "Slot used to create a new page."

        current_page = self.thumbnailTabWidget.currentIndex() + 1
        next_page = 1 if current_page == 0 else current_page + 1
        page_name = "Page %d" % next_page

        view = thumbnailview.ThumbnailView(self.api_data, self.preferences)
        index = self.thumbnailTabWidget.addTab(view, page_name)

        # PyKDE4 suffers from garbage collection issues with widgets like
        # KPageWidget or KTabWidget. Therefore, we add the item to a list to
        # keep a reference of it around

        self.__pages.append(view)
        view.downloadCompleted.connect(self.downloadCompleted.emit)

        # Update the data if it's not the first page

        if index != 0:
            self.api_data.update(page=index+1)
            self.__current_index = index
            self.thumbnailTabWidget.setCurrentIndex(index)
            return
        else:
            view.display_thumbnails()
            self.nextPageButton.setDisabled(False)

    def fetch_posts(self):

        """Slot used to fetch posts, calling the display_thumbnail of the
        thumbnail view corresponding to the current index."""

        if not self.api_data.data:
            return

        if self.__firstpage:
            # We don't have an index yet, use a different approach
            self.new_page()
            self.__firstpage = False
            return

        view = self.thumbnailTabWidget.widget(self.__current_index)
        view.display_thumbnails()

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

        for thumbnailview in self:

            selected = thumbnailview.selected_images()

            if selected:
                images.extend(selected)

        return images

    def update_data(self, api_data):

        "Updates the API data."

        self.api_data = api_data

        # As we changed object, the connection to the item points still to the
        # old one. Therefore, we need to re-connect the signal again

        self.api_data.dataReady.connect(self.fetch_posts)

