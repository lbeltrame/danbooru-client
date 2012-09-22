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

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui

import PyKDE4.kdecore as kdecore
import PyKDE4.kdeui as kdeui

import api.remote as remote
from ui.ui_connectwidget import Ui_connectForm


class ConnectWidget(QtGui.QWidget, Ui_connectForm):

    "Widget used in the dialog for a Danbooru connection."

    connectionEstablished = QtCore.pyqtSignal(remote.DanbooruService)
    rejected = QtCore.pyqtSignal()

    def __init__(self, urls=None, parent=None):

        super(ConnectWidget, self).__init__(parent)
        self.setupUi(self)
        self.danbooruUrlComboBox.setFocus()
        self.closeButton.setIcon(kdeui.KIcon("dialog-close"))
        self.closeButton.setToolTip(kdecore.i18n("Close the dialog and"
        " discard changes"))

        self._connection = None

        if urls is not None:
            for index, item in enumerate(urls):
                self.danbooruUrlComboBox.insertUrl(index,
                    kdecore.KUrl(item))

        self.buttonBox.accepted.connect(self.accept)
        self.closeButton.clicked.connect(self.rejected.emit)

    @property
    def url(self):

        "Returns the currently selected Danbooru URL."

        return self.danbooruUrlComboBox.currentText()

    @property
    def username(self):

        "Returns the inserted username."

        return self.userLineEdit.text()

    @property
    def password(self):

        "Returns the inserted password."

        return self.passwdLineEdit.text()

    def accept(self):

        url = self.url
        login = self.username
        password = self.password

        username = None if login.isEmpty() else login
        password = None if password.isEmpty() else password

        if url.isEmpty():
            return

        self._connection = remote.DanbooruService(unicode(url), username,
                                                  password=password)
        self.connectionEstablished.emit(self._connection)







