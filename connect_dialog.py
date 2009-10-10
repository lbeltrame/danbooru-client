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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

import api
from  ui_connectdialog import Ui_connectForm

class ConnectWidget(QWidget, Ui_connectForm):

    def __init__(self, danbooru=None, parent=None):

        super(ConnectWidget, self).__init__(parent)
        self._history = None
        self.setupUi(self)

        self.urlBox.returnPressed.connect(self.add_history)

    def url(self):
        return self.urlBox.lineEdit().text()

    def username(self):
        return self.userLineEdit.text()

    def password(self):
        return self.passwdLineEdit.text()

    def history(self):
        return self.urlBox.historyItems()

    def add_history(self):

        if self.url().isEmpty():
            return

        self.urlBox.addToHistory(self.url())

class ConnectDialog(KDialog):

    def __init__(self, history=None, parent=None):

        super(ConnectDialog, self).__init__(parent)

        self.danbooru = None

        self.connect_widget = ConnectWidget(self)
        self.setMainWidget(self.connect_widget)
        self.setButtons(KDialog.ButtonCode(KDialog.Ok | KDialog.Cancel))
        self.setCaption("Enter a Danbooru URL")
        if history is not None:
            self.connect_widget.urlBox.setHistoryItems(history, True)

    def accept(self):

        ok = self.validate()
        if not ok:
            return
        KDialog.accept(self)

    def danbooru_api(self):

        if self.danbooru is None:
            return

        return self.danbooru

    def url_history(self):

        return self.connect_widget.history()

    def validate(self):

        url = self.connect_widget.url()
        login = self.connect_widget.username()
        password = self.connect_widget.password()

        login = None if login.isEmpty() else login
        password = None if password.isEmpty() else password

        if url.isEmpty():
            return

        if not url.startsWith("http://"):
            self.urlBox.lineEdit().setText("Please enter a valid Danbooru URL.")
            return
        try:
            danbooru = api.Danbooru(url, login=login, password=password)
        except IOError, error:
            return
        else:
            self.danbooru = danbooru
            return True



