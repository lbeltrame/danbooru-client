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

import hashlib

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui

import PyKDE4.kdecore as kdecore
import PyKDE4.kdeui as kdeui

import api.remote as remote
from ui.ui_connectwidget import Ui_connectForm

_SALTS = {"http://yande.re": "choujin-steiner--{}--",
          "http://konachan.com": "So-I-Heard-You-Like-Mupkids-?--{}--",
          "http://konachan.net": "So-I-Heard-You-Like-Mupkids-?--{}--",
          "http://danbooru.donmai.us": "choujin-steiner--{}--"}


Wallet = kdeui.KWallet.Wallet
KWallet = kdeui.KWallet

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

        winid = self.parent().winId()

        self.setup_urls(urls)

        self.buttonBox.accepted.connect(self.accept)
        self.closeButton.clicked.connect(self.rejected.emit)

        self._wallet_available = False
        self._wallet = Wallet.openWallet(Wallet.NetworkWallet(), winid,
                                         Wallet.Asynchronous)
        self._wallet.walletOpened.connect(self._check_wallet)

        self.danbooruUrlComboBox.currentIndexChanged[QtCore.QString].connect(
            self._adjust_wallet)


    @property
    def url(self):

        "Returns the currently selected Danbooru URL."

        return self.danbooruUrlComboBox.currentText()

    def _set_username(self, username):
        self.userLineEdit.setText(username)

    def _get_username(self):
            return self.userLineEdit.text()

    def _set_password(self, password):
        self.passwdLineEdit.setText(password)

    def _get_password(self):
        return self.passwdLineEdit.text()

    username = property(_get_username, _set_username)
    password = property(_get_password, _set_password)

    def accept(self):

        url = self.url
        login = self.username
        password = self.password

        if url.isEmpty():
            return

        username = None if login.isEmpty() else login
        password = None if password.isEmpty() else password

        salt = _SALTS.get(unicode(url))

        if salt is None:
            username = None
            password = None

        if self._wallet_available:
            if not self._wallet.hasEntry(self.url):
                data_map = dict(username=self.username, password=self.password)
                self._wallet.writeMap(self.url, data_map)

        if username is not None and password is not None:
            password = salt.format(password)
            password = hashlib.sha1(password).hexdigest()

        self._connection = remote.DanbooruService(unicode(url), username,
                                                  password=password)
        self.connectionEstablished.emit(self._connection)
        self.hide()

    def setup_urls(self, urls):

        self.danbooruUrlComboBox.clear()

        if urls is not None:
            for index, item in enumerate(urls):
                self.danbooruUrlComboBox.insertUrl(index,
                    kdecore.KUrl(item))

    def _adjust_wallet(self, name):

        self.username = QtCore.QString()
        self.password = QtCore.QString()

        if not self._wallet_available:
            return

        if self._wallet.hasEntry(name):
            code, data_map = self._wallet.readMap(name)

            if code != 0:
                return

            self.username = data_map[QtCore.QString("username")]
            self.password = data_map[QtCore.QString("password")]

    def _check_wallet(self, result):

        if not result:
            return

        self._wallet_available = True

        if not self._wallet.hasFolder(Wallet.PasswordFolder()):
           self._wallet.createFolder(Wallet.PasswordFolder())

        self._adjust_wallet(self.danbooruUrlComboBox.currentText())





