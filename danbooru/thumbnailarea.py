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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

import thumbnailview
from ui.ui_thumbnailarea import Ui_ThumbnailArea

class ThumbnailArea(QWidget, Ui_ThumbnailArea):

    # Signal that is emitted when a page is added
    pageAdded = pyqtSignal(int)

    def __init__(self, api_data=None, preferences=None, parent=None):

        super(ThumbnailArea, self).__init__(parent)
        self.setupUi(self)

        self.preferences = preferences
        self.api_data = api_data
        self.__pages = list()
        self.__firstpage = True
        self.__current_index = 0

        self.nextPageButton.setDisabled(True)

        self.nextPageButton.clicked.connect(self.new_page)
        self.api_data.dataReady.connect(self.fetch_posts)

    #FIXME: Things are being connected multiple times in mainwindow!

    def new_page(self):

        current_page = self.thumbnailTabWidget.currentIndex() + 1
        next_page = 1 if current_page == 0 else current_page + 1
        page_name = "Page %d" % next_page

        view = thumbnailview.ThumbnailView(self.api_data, self.preferences)

        # addTab returns the index, so let's use it
        index = self.thumbnailTabWidget.addTab(view, page_name)
        self.__pages.append(view) # Prevents GC issues

        # Update the data if it's not the first page

        if index != 0:
            self.api_data.update(page=index+1)
            self.__current_index = index
            return
        else:
            view.display_thumbnails()
            self.nextPageButton.setDisabled(False)

    def fetch_posts(self):

        if not self.api_data.data:
            return

        #TODO: Handle ratings

        if self.__firstpage:
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
        self.nextPageButton.setDisabled(True)


