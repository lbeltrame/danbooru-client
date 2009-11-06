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

import re

from PyQt4.QtCore import QRegExp
from PyQt4.QtGui import QWidget, QRegExpValidator
from PyKDE4.kdeui import KDialog

from ui.ui_fetchdialog import Ui_FetchDialog

class FetchWidget(QWidget, Ui_FetchDialog):

    def __init__(self, limit, parent =None):

        super(FetchWidget, self).__init__(parent)

        self.setupUi(self)
        self.postSpinBox.setValue(limit)
        # Allow only letters, numbers, commas and underscores
        regexp = QRegExp(r"^[a-zA-Z,_0-9]+$")
        self.validator = QRegExpValidator(regexp, self)
        self.tagLineEdit.setValidator(self.validator)

    def rating_limit(self):
        return self.__RATINGS[self.ratingComboBox.text()]


class FetchDialog(KDialog):

    __RATINGS = dict(Safe=["safe"], Questionable=["safe", "questionable"],
                     Explicit=["safe", "questionable", "explicit"])

    def __init__(self, default_limit, parent=None):

        super(FetchDialog, self).__init__(parent)

        self.__tags = None
        self.__limit = None
        self.__rating = None
        self.fetchwidget = FetchWidget(default_limit, self)

        self.setMainWidget(self.fetchwidget)

    def tags(self):
        return self.__tags

    def limit(self):
        return self.__limit

    def max_rating(self):
        return self.__rating

    def strip_tags(self, taglist):
        return [tag.strip() for tag in taglist]

    def accept(self):

        self.__tags = self.fetchwidget.tagLineEdit.text()
        self.__tags = unicode(self.__tags)
        self.__tags = self.__tags.split(",")
        self.__tags = self.strip_tags(self.__tags)
        # Tags don't have spaces
        self.__tags =  [re.sub("\s","_", item) for item in self.__tags]

        self.__limit = self.fetchwidget.postSpinBox.value()
        text = unicode(self.fetchwidget.ratingComboBox.currentText())
        self.__rating = self.__RATINGS[text]
        KDialog.accept(self)
