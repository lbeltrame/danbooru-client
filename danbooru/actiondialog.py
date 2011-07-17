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

import PyQt4.QtCore as QtCore

import PyKDE4.kdecore as kdecore
import PyKDE4.kdeui as kdeui
import PyKDE4.kio as kio

import danbooru2nepomuk
from ui.ui_actiondialog import Ui_ActionDialog


class ActionWidget(QtCore.QWidget, Ui_ActionDialog):

    def __init__(self, url=None, pixmap=None, parent=None):

        super(ActionWidget, self).__init__(parent)
        self.setupUi(self)

        self.actions = ["view", "download"]
        self.fname = kdecore.KUrl(url).fileName()
        label_text = kdecore.i18n("<a href='%s'>Direct image link</a>" % url)
        self.linkLabel.setText(label_text)

        pretty_url = kdecore.KUrl(url).prettyUrl()
        self.linkLabel.setToolTip(pretty_url)

        if not pixmap.isNull():
            self.pictureLabel.setPixmap(pixmap)

    def action(self):

        "Returns the selected action by the user."

        index = self.actionSelectComboBox.currentIndex()
        return self.actions[index]


class ActionDialog(kdeui.KDialog):

    """Class that provides a dialog that prompts the user to choose an action
    for the selected image."""

    fetchTags = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, url, pixmap=None, tags=None, preferences=None,
                 parent=None):

        super(ActionDialog, self).__init__(parent)

        self.url = url
        self.display = None
        self.preferences = preferences
        self.tagging = preferences.nepomuk_enabled
        self.blacklist = preferences.tag_blacklist

        self.actionwidget = ActionWidget(self.url, pixmap, self)
        self.setMainWidget(self.actionwidget)
        self.setCaption(kdecore.i18n("Download or display image"))

        self.tags = [item for item in tags if item not in self.blacklist]

        self.actionwidget.tagList.addItems(self.tags)
        self.actionwidget.tagList.itemDoubleClicked.connect(self.fetch)
        self.__actions = dict(view=self.view, download=self.download)

    def accept(self):

        action = self.actionwidget.action()
        self.__actions[action]()

        kdeui.KDialog.accept(self)

    def fetch(self, item):

        "Fetches the related tags from the user's selection."

        self.fetchTags.emit(item.text())
        self.reject()

    def view(self):

        """Triggers the display of the image using the user's default image
        viewer."""

        # Garbage collection ensues if we don't keep a reference around
        self.display = kio.KRun(kdecore.KUrl(self.url), self, 0,
                                False, True, '')

        if self.display.hasError():

            messagewidget = kdeui.KMessageWidget(self)
            messagewidget.setMessageType(kdeui.KMessageWidget.Error)
            text = kdecore.i18n("An error occurred while "
                                "downloading the image.")
            messagewidget.setText(text)

    def download(self):

        """Function that triggers the download of the image to a user-supplied
        directory."""

        start_name = kdecore.KUrl(self.url).fileName()
        start_url = kdecore.KUrl("kfiledialog:///danbooru/%s" %
                                 unicode(start_name))

        # Get the mimetype to be passed to the save dialog
        mimetype_job = kio.KIO.mimetype(kdecore.KUrl(self.url),
                                        kio.KIO.HideProgressInfo)

        # Small enough to be synchronous
        if kio.KIO.NetAccess.synchronousRun(mimetype_job, self):
            mimetype = mimetype_job.mimetype()

        caption = kdecore.i18n("Save image file")

        enable_previews = kio.KFileDialog.ShowInlinePreview
        confirm_overwrite = kio.KFileDialog.ConfirmOverwrite
        options = kio.KFileDialog.Option(enable_previews | confirm_overwrite)

        filename = kio.KFileDialog.getSaveFileName(start_url,
            mimetype, self, caption, options)

        if not filename:
            return

        download_url = kdecore.KUrl(self.url)
        download_job = kio.KIO.file_copy(download_url, filename, -1)
        download_job.result.connect(self.download_slot)

    def download_slot(self, job):

        "Slot called by the KJob handling the download."

        if job.error():
            job.ui().showErrorMessage()
            return

        download_name = job.destUrl().toLocalFile()

        if self.tagging:
            danbooru2nepomuk.tag_danbooru_item(download_name, self.tags)
