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
File: actiondialog.py
Author: Luca Beltrame
Description: Widget and dialog to display and download images from Danbooru.
'''

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QWidget
from PyKDE4.kdecore import KUrl, i18n
from PyKDE4.kdeui import KDialog, KMessageBox
from PyKDE4.kio import KIO, KRun, KFileDialog, KFile

import danbooru2nepomuk
from ui.ui_actiondialog import Ui_ActionDialog


class ActionWidget(QWidget, Ui_ActionDialog):

    def __init__(self, url=None, pixmap=None, parent=None):

        super(ActionWidget, self).__init__(parent)
        self.setupUi(self)

        self.actions = ["view", "download"]
        self.fname = KUrl(url).fileName()

        if not pixmap.isNull():
            self.pictureLabel.setPixmap(pixmap)

    def action(self):

        "Returns the selected action by the user."

        index = self.actionSelectComboBox.currentIndex()
        return self.actions[index]


class ActionDialog(KDialog):

    """Class that provides a dialog that prompts the user to choose an action
    for the selected image."""

    def __init__(self, url, pixmap=None, preferences=None, parent=None):

        super(ActionDialog, self).__init__(parent)

        self.url = url
        self.display = None
        self.tagging = preferences.nepomuk_enabled
        self.blacklist = preferences.tag_blacklist
        self.actionwidget = ActionWidget(self.url, pixmap, self)
        self.setMainWidget(self.actionwidget)
        self.setCaption(i18n("Download or display image"))

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

        """Function that triggers the download of the image to a user-supplied
        directory."""

        start_name = KUrl(self.url).fileName()
        start_url = KUrl("kfiledialog:///danbooru/%s" % unicode(start_name))
        mimetype_job = KIO.mimetype(KUrl(self.url), KIO.HideProgressInfo)

        # Small enough to be synchronous
        if KIO.NetAccess.synchronousRun(mimetype_job, self):
            mimetype = mimetype_job.mimetype()

        caption = i18n("Save image file")

        # Build the save dialog
        save_dialog = KFileDialog(start_url, mimetype, self)
        save_dialog.setOperationMode(KFileDialog.Saving)
        modes = KFile.Modes(KFile.File | KFile.LocalOnly)

        # Set the parameters
        save_dialog.setMode(modes)
        save_dialog.setConfirmOverwrite(True)
        save_dialog.setInlinePreviewShown(True)
        save_dialog.setCaption(caption)

        if save_dialog.exec_():

            filename = save_dialog.selectedUrl()

            if not filename:
                return

            download_job = KIO.file_copy(KUrl(self.url), filename, -1)

            self.connect(download_job, SIGNAL("result( KJob *)"),
                                              self.download_slot)

    def download_slot(self, job):

        "Slot called by the KJob handling the download."

        if job.error():
            job.ui().showErrorMessage()
            return

        start_name = job.srcUrl().fileName()
        download_name = job.destUrl().toLocalFile()

        if self.tagging:
            result = danbooru2nepomuk.nepomuk_running()
            if result:

                # The user may select an arbitrary file name, so we tag
                # using the original file name obtained from the URL
                tags = danbooru2nepomuk.extract_tags(start_name,
                                                     blacklist=self.blacklist)
                # danbooru2nepomuk wants strings or QStrings
                danbooru2nepomuk.tag_file(download_name, tags)

