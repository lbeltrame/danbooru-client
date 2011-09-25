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

from PyQt4.QtCore import pyqtSignal, Qt,  QString
from PyQt4.QtGui import QWidget, QLabel
from PyKDE4.kdecore import i18n
from PyKDE4.kdeui import KAcceleratorManager,  KMessageBox

import thumbnailview
from ui.ui_thumbnailarea import Ui_ThumbnailArea


class DanbooruTabWidget(QWidget, Ui_ThumbnailArea):

    """Class that provides an area where individual ThumbnailViews (from
    thumbnailview.py) can be placed in, using a tabbed interface. The class uses
    an internal list for each page added, to avoid garbage collection issues.
    Methods to create tabs are not called directly, but are instead slots called
    upon by signal.
    """

    def __init__(self, api_data=None, preferences=None, post_limit=None,
                 parent=None):

        """Initialize a new ThumbnailArea. api_data is a reference to a
        Danbooru object, while preferences is a reference to a
        KConfigXT instance."""

        super(DanbooruTabWidget, self).__init__(parent)
        self.setupUi(self)

        self.preferences = preferences
        self.api_data = api_data
        self.__pages = list()
        self.__firstpage = True
        self.__current_index = 0
        self.post_limit = post_limit

        KAcceleratorManager.setNoAccel(self.thumbnailTabWidget)
        self.nextPageButton.setDisabled(True)

        button_toggle = partial(self.nextPageButton.setDisabled, False)

        self.api_data.postDownloadFinished.connect(button_toggle)
        self.api_data.postDownloadFinished.connect(self.__check)
        self.nextPageButton.clicked.connect(self.update_search_results)

        self.new_page()

    def __iter__(self):

        "Yields every stored page in the thumbnail area."

        for item in self.__pages:
            yield item

    def __check(self):

        """Check whether results were received or not."""

        current_index = self.thumbnailTabWidget.currentIndex()

        widget = self.thumbnailTabWidget.widget(current_index)

        if not widget:

            self.setUpdatesEnabled(False)
            self.thumbnailTabWidget.removeTab(current_index)
            label = QLabel(i18n("No matching posts found for this page."
                                "\nWere you looking for a tag in the sidebar?"))
            label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            text = i18n("Page %1 (empty)", current_index + 1)

            index = self.thumbnailTabWidget.addTab(label, text)
            self.thumbnailTabWidget.setCurrentIndex(index)
            self.nextPageButton.setDisabled(False)
            self.setUpdatesEnabled(True)

    def new_page(self):

        "Slot used to create a new page."

        if self.__firstpage:
            self.create_tab()
            self.__firstpage = False
        else:
            self.create_tab()
            self.nextPageButton.setDisabled(True)

    def create_tab(self):

        """Creates a new tab in the tab widget, and adds it to the internal
        lists. Returns the inserted widget and the index it was inserted in."""

        current_page = self.thumbnailTabWidget.currentIndex() + 1
        next_page = 1 if current_page == 0 else current_page + 1
        page_name = i18n("Page %1", next_page)

        view = thumbnailview.DanbooruPostView(self.api_data, self.preferences)

        # We add the item to a list to keep a reference of it around

        self.__pages.append(view)

        index = self.thumbnailTabWidget.addTab(view, page_name)
        self.thumbnailTabWidget.setCurrentIndex(index)
        self.__current_index = index + 1

    def clear(self):

        "Removes all pages in the widget."

        self.thumbnailTabWidget.clear()
        self.__pages = list()
        self.__firstpage = True
        self.__current_index = 0
        self.nextPageButton.setDisabled(True)
        self.new_page()

    def selected_images(self):

        "Returns a list of the selected images in all pages."

        images = list()

        for view in self:

            selected = view.selected_images()

            if selected:
                images.extend(selected)

        return images

    def update_search_results(self):

        """Update the search results using the same parameters as originally
        supplied."""

        self.nextPageButton.setDisabled(True)
        self.new_page()
        current_page = self.__current_index + 1

        self.api_data.get_post_list(limit=self.post_limit,
                                    tags=self.api_data.current_tags,
                                    page=current_page,
                                    blacklist=self.preferences.tag_blacklist,
                                    rating=self.preferences.max_allowed_rating)