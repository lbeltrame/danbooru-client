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

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QWidget
from PyKDE4.kdecore import KUrl
from PyKDE4.kdeui import KDialog, KMessageBox
from PyKDE4.kio import KIO, KRun, KFileDialog, KFile

from ui_actiondialog import Ui_ActionDialog

class ActionWidget(QWidget, Ui_ActionDialog):

    def __init__(self, url=None, parent=None):

        super(ActionWidget, self).__init__(parent)
        self.setupUi(self)

        self.actions = ["view", "download"]
        self.fname = KUrl(url).fileName()

    def action(self):

        index = self.actionSelectComboBox.currentIndex()
        return self.actions[index]

class ActionDialog(KDialog):

    def __init__(self, url, parent=None):

        super(ActionDialog, self).__init__(parent)

        self.url = url
        self.actionwidget = ActionWidget(self.url, self)
        self.setMainWidget(self.actionwidget)
        self.setCaption("Download or display image")

        self.__actions = dict(view=self.view, download=self.download)

    def accept(self):

        action = self.actionwidget.action()
        self.__actions[action]()

        KDialog.accept(self)

    def view(self):

        # Garbage collection ensues if we don't keep a reference around
        self.display = KRun(KUrl(self.url), self, 0, False, True, '')
        if self.display.hasError():
            KMessageBox.error(self,
                             "An error occurred while downloading the image.",
                             "Download error")
            self.reject(self)

    def download(self):

        start_name = KUrl(self.url).fileName()
        start_url = KUrl("kfiledialog:///danbooru/%s" % unicode(start_name))
        mimetype_job = KIO.mimetype(KUrl(self.url), KIO.HideProgressInfo)

        if KIO.NetAccess.synchronousRun(mimetype_job, self):
            mimetype = mimetype_job.mimetype()

        caption = "Save image file"

        # Build the save dialog
        save_dialog = KFileDialog(start_url, mimetype, self)
        save_dialog.setOperationMode(KFileDialog.Saving)
        modes = KFile.Modes(KFile.File | KFile.LocalOnly)

        save_dialog.setMode(modes)
        save_dialog.setConfirmOverwrite(True)
        save_dialog.setInlinePreviewShown(True)
        save_dialog.setCaption(caption)

        if save_dialog.exec_():

            filename = save_dialog.selectedUrl()

            if not filename:
                return

            ok = KIO.NetAccess.download(KUrl(self.url), filename.toLocalFile(),
                                        self)
            if not ok:
                KMessageBox.error(self, KIO.NetAccess.lastErrorString())
                return

