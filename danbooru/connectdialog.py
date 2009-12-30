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
File: connectdialog.py
Author: Luca Beltrame
Description: File to handle connections to Danbooru sites.
'''

from PyQt4.QtGui import QWidget
from PyKDE4.kdecore import KUrl
from PyKDE4.kdeui import KDialog

import api
from  ui.ui_connectdialog import Ui_connectForm


class ConnectWidget(QWidget, Ui_connectForm):

    "Widget used in the dialog for a Danbooru connection."

    def __init__(self, urls=None, parent=None):

        super(ConnectWidget, self).__init__(parent)
        self.setupUi(self)
        self.danbooruUrlComboBox.setFocus()

        if urls is not None:
            for index, item in enumerate(urls):
                self.danbooruUrlComboBox.insertUrl(index, KUrl(item))

    def url(self):

        "Returns the currently selected Danbooru URL."

        return self.danbooruUrlComboBox.currentText()

    def username(self):

        "Returns the inserted username."

        return self.userLineEdit.text()

    def password(self):

        "Returns the inserted password."

        return self.passwdLineEdit.text()


class ConnectDialog(KDialog):

    """Dialog used to "connect" to a Danbooru board. It performs validation of
    the used URLs and stores an API instance if successful, which can be
    retrieved by other objects by calling the danbooru_api() function."""

    def __init__(self, urls=None, parent=None):

        super(ConnectDialog, self).__init__(parent)

        self.__danbooru = None

        self.connect_widget = ConnectWidget(urls, self)
        self.setMainWidget(self.connect_widget)
        self.setButtons(KDialog.ButtonCode(KDialog.Ok | KDialog.Cancel))
        self.setCaption("Enter a Danbooru URL")
        self.adjustSize()

    def accept(self):

        result = self.validate()
        if not result:
            return
        KDialog.accept(self)

    def danbooru_api(self):

        "Returns the Danbooru object retrieved."

        if self.__danbooru is None:
            return

        return self.__danbooru

    def validate(self):

        """Validates the URL, and returns if it is either empty or it is not
        working."""

        url = self.connect_widget.url()
        login = self.connect_widget.username()
        password = self.connect_widget.password()

        login = None if login.isEmpty() else login
        password = None if password.isEmpty() else password

        if url.isEmpty():
            return

        try:
            danbooru = api.Danbooru(unicode(url), login=login, password=password)
        except IOError, error:
            return
        else:
            self.__danbooru = danbooru
            return True
