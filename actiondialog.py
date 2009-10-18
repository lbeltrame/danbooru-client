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

from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

from ui_actiondialog import Ui_ActionDialog

class ActionWidget(QWidget, Ui_ActionDialog):

    def __init__(self, url=None, parent=None):

        super(ActionDialog, self).__init__(parent)

        self.actions = ["view", "download"]

        self.fname = KUrl(url).fileName()
        self.url = url
        self.nameLabel.setText(self.fname)

        self.setupUi(self)

class ActionDialog(KDialog):

    def __init__(self, parent=None):

        super(ActionDialog, self).__init__(parent)
        self.setMainWidget(ActionWidget)



