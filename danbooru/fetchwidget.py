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

import os
import sys

# Python3 compatibility

if sys.version_info.major > 2:
    unicode = str

from PyQt4.QtCore import QRegExp, pyqtSignal
from PyQt4.QtGui import QWidget, QRegExpValidator
from PyQt4.uic import loadUi
from PyKDE4.kdeui import KDialog, KIcon
from PyKDE4.kdecore import i18n

from ui.ui_fetchwidget import Ui_FetchDialog

INDICES = {"Safe": 0, "Questionable": 1, "Explicit": 2}
NAME_MAPPING = {0: "Safe", 1: "Questionable", 2: "Explicit"}

PATH = os.path.dirname(__file__)
FETCH_UI = os.path.join(PATH, "ui_src", "fetchwidget.ui")

class FetchWidget(QWidget):

    dataSent = pyqtSignal(list, unicode, int)
    rejected = pyqtSignal()

    def __init__(self, limit, default_rating=None, tags="", parent=None):

        super(FetchWidget, self).__init__(parent)
        loadUi(FETCH_UI, self)

        self.tags = tags
        self.rating = default_rating
        self.limit = limit

        self.postSpinBox.setValue(limit)
        self.closeButton.setIcon(KIcon("dialog-close"))

        # Allow only letters, numbers, commas and underscores
        #regexp = QRegExp(r"^[a-zA-Z,_0-9:]+$")
        #self.validator = QRegExpValidator(regexp, self)
        #self.tagLineEdit.setValidator(self.validator)

        if default_rating:
            default_rating = unicode(default_rating)
            self.ratingComboBox.setCurrentIndex(INDICES[self.rating])

        self.downloadButton.clicked.connect(self.accept)
        self.closeButton.clicked.connect(self.rejected.emit)

    def accept(self):

        self.tags = self.tagLineEdit.text()
        self.tags = unicode(self.tags)
        self.tags = self.tags.split(",")
        self.tags = [tag.strip().replace(" ","_") for tag in self.tags]
        self.limit = self.postSpinBox.value()
        self.rating = unicode(self.ratingComboBox.currentText())

        self.dataSent.emit(self.tags,
                           NAME_MAPPING[self.ratingComboBox.currentIndex()],
                           self.limit)

    def update_values(self):

       """Update values after a configuration change."""

       self.postSpinBox.setValue(self.limit)
       self.ratingComboBox.setCurrentIndex(INDICES[self.rating])


