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
File: fetchdialog.py
Author: Luca Beltrame
Description: Module that implements the fetch dialog for the Danbooru Client
application
'''

import re

from PyQt4.QtCore import QRegExp
from PyQt4.QtGui import QWidget, QRegExpValidator
from PyKDE4.kdeui import KDialog

from ui.ui_fetchdialog import Ui_FetchDialog


class FetchWidget(QWidget, Ui_FetchDialog):

    """Class that constructs the widget used for setting the parameters to fetch
    posts from a Danbooru board."""

    def __init__(self, limit, default_rating=None, parent =None):

        super(FetchWidget, self).__init__(parent)
        self.setupUi(self)

        self.__rating_mappings = {"Safe":self.safeRadioButton,
                                  "Questionable":self.questionableRadioButton,
                                  "Explicit":self.explicitRadioButton}

        self.postSpinBox.setValue(limit)
        # Allow only letters, numbers, commas and underscores
        regexp = QRegExp(r"^[a-zA-Z,_0-9]+$")
        self.validator = QRegExpValidator(regexp, self)
        self.tagLineEdit.setValidator(self.validator)

        if default_rating:
            default_rating = unicode(default_rating)
            self.setup_rating(default_rating)

    def setup_rating(self, rating):

        if rating in self.__rating_mappings:
            print "Here"
            self.__rating_mappings[rating].setChecked(True)

    def selected_rating(self):

        """Returns the user's selected rating, depending on the checked radio
        button."""

        if self.safeRadioButton.isChecked():
            return "Safe"
        elif self.questionableRadioButton.isChecked():
            return "Questionable"
        elif self.explicitRadioButton.isChecked():
            return "Explicit"


class FetchDialog(KDialog):

    """Class that provides a dialog to set parameters for fetching posts from a
    Danbooru board."""

    def __init__(self, default_limit, preferences=None, parent=None):

        super(FetchDialog, self).__init__(parent)

        self.__tags = None
        self.__limit = None
        self.__rating = None
        self.fetchwidget = FetchWidget(default_limit,
                                       preferences.max_allowed_rating,
                                       parent=self)

        self.setMainWidget(self.fetchwidget)

    def tags(self):

        "Returns the user selected tags."

        return self.__tags

    def limit(self):

        "Returns the post limit (maximum 100) selected by the user."

        return self.__limit

    def max_rating(self):

        "Returns the maximum allowed rating chosen by the user."

        return self.__rating

    def strip_tags(self, taglist):

        "Strips whitespace from tags."

        return [tag.strip() for tag in taglist]

    def accept(self):

        self.__tags = self.fetchwidget.tagLineEdit.text()
        self.__tags = unicode(self.__tags)
        self.__tags = self.__tags.split(",")
        self.__tags = self.strip_tags(self.__tags)
        # Tags don't have spaces
        self.__tags =  [re.sub("\s","_", item) for item in self.__tags]

        self.__limit = self.fetchwidget.postSpinBox.value()
        self.__rating = self.fetchwidget.selected_rating()
        KDialog.accept(self)
