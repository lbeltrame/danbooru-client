#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Copyright 2011 Luca Beltrame <einar@heavensinferno.net>
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

from functools import partial

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui

import PyKDE4.kdecore as kdecore
import PyKDE4.kdeui as kdeui
import PyKDE4.kio as kio

import danbooru2nepomuk

_TRANSLATED_RATINGS = dict(
    Safe=kdecore.i18nc("Image for all audiences", "Safe"),
    Questionable=kdecore.i18nc("Image with suggestive themes", "Questionable"),
                          Explicit=kdecore.i18nc("Image with explicit content",
                              "Explicit")
    )


class DanbooruPostWidget(QtGui.QWidget):

    """Widget that displays a DanbooruPost."""

    def __init__(self, danbooru_post, parent=None):

        super(DanbooruPostWidget, self).__init__(parent)

        self.data = danbooru_post

        self.url_label = kdeui.KUrlLabel()
        self.__text_label = QtGui.QLabel()
        self.url_to_file = self.data.file_url

        label_text = self.label_text()

        self.url_label.setUrl(self.data.file_url)
        self.url_label.setPixmap(self.data.pixmap)

        full_url = kdecore.KUrl(self.data.file_url).fileName()
        self.url_label.setUseTips(True)
        self.url_label.setAlignment(QtCore.Qt.AlignCenter)
        self.url_label.setTipText(full_url)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addStretch()
        self.layout.addWidget(self.url_label)

        if label_text is not None:
            self.__text_label.setText(label_text)
            self.layout.addWidget(self.__text_label)

        self.checkbox = QtGui.QCheckBox()
        self.checkbox.setChecked(False)
        self.checkbox.setText(kdecore.i18n("Select"))

        # Remove the accelerator, we don't want it
        kdeui.KAcceleratorManager.setNoAccel(self.checkbox)

        self.checkbox.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                    QtGui.QSizePolicy.Fixed)
        self.layout.addWidget(self.checkbox)

        # FIXME: Hack to make sure there's enough space around the image,
        # so that things to do not look as cramped

        self.layout.setSpacing(6)
        self.setup_actions()

    def setup_actions(self):

        """Set up the required KActions."""

        self.menu = kdeui.KMenu(self)
        # self.menu.addTitle("Available actions")
        self.action_collection = kdeui.KActionCollection(self)

        self.download_action = self.action_collection.addAction(
            "download-image")
        self.view_action = self.action_collection.addAction(
            "view-image")
        self.browser_action = self.action_collection.addAction(
            "open-browser")
        self.copy_link_action = self.action_collection.addAction(
            "copy-link")

        self.download_action.setText("Download")
        self.view_action.setText("View image")
        self.browser_action.setText("Open in browser")
        self.copy_link_action.setText("Copy image link")

        self.download_action.setIcon(kdeui.KIcon("download"))
        self.view_action.setIcon(kdeui.KIcon("image-x-generic"))
        self.browser_action.setIcon(kdeui.KIcon("internet-web-browser"))

        self.menu.addAction(self.view_action)
        self.menu.addAction(self.download_action)
        self.menu.addAction(self.browser_action)
        self.menu.addAction(self.copy_link_action)

        self.download_action.triggered.connect(self.download)
        self.view_action.triggered.connect(self.view)
        self.browser_action.triggered.connect(self.open_browser)
        self.copy_link_action.triggered.connect(self.put_in_clipboard)


    def contextMenuEvent(self, event):

        self.menu.exec_(event.globalPos())

    def label_text(self):

        "Format the text of the item for display."

        height = self.data.height
        width = self.data.width
        file_size = int(self.data.file_size)
        rating = _TRANSLATED_RATINGS[self.data.rating]

        # Properly format the strings according to the locale

        sizestr = kdecore.ki18np("1 pixel", "%1 pixels")
        image_size = kdecore.i18n("Size: %1 x %2",
                                  sizestr.subs(width).toString(),
                                  sizestr.subs(height).toString())
        file_size = kdecore.i18n("File size: %1",
                kdecore.KGlobal.locale().formatByteSize(file_size))
        rating = kdecore.i18n("Rating: %1", rating)

        text = image_size + "\n" + file_size + "\n" + rating

        return text

    def download(self, result):

        """Trigger the download of the image to a user-supplied directory."""

        start_name = kdecore.KUrl(self.url_to_file).fileName()
        start_url = kdecore.KUrl("kfiledialog:///danbooru/%s" %
                                 unicode(start_name))

        # Get the mimetype to be passed to the save dialog
        mimetype_job = kio.KIO.mimetype(kdecore.KUrl(self.url_to_file),
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

        download_url = kdecore.KUrl(self.url_to_file)
        filename = kdecore.KUrl(filename)
        download_job = kio.KIO.file_copy(download_url, filename, -1)
        download_job.result.connect(self.download_slot)

    def download_slot(self, job):

        "Slot called by the KJob handling the download."

        if job.error():
            messagewidget = kdeui.KMessageWidget(self)
            messagewidget.setMessageType(kdeui.KMessageWidget.Error)
            text = job.errorText()
            messagewidget.setText(text)

            return

        download_name = job.destUrl().toLocalFile()

        # Grab a reference to the view
        parent_widget = self.parent().parent()

        blacklist = parent_widget.preferences.tag_blacklist
        tagging = parent_widget.preferences.nepomuk_enabled

        if tagging:
            # Get the URL of the board for Nepomuk tagging
            board_name = kdecore.KUrl(parent_widget.api_data.url)
            danbooru2nepomuk.tag_danbooru_item(download_name, self.data.tags,
                                               blacklist, board_name)

    def view(self):

        """Display the image using the user's default image viewer."""

        # Garbage collection ensues if we don't keep a reference around
        self.display = kio.KRun(kdecore.KUrl(self.url_to_file), self, 0,
                                False, True, '')

        if self.display.hasError():

            messagewidget = kdeui.KMessageWidget(self)
            messagewidget.setMessageType(kdeui.KMessageWidget.Error)
            text = kdecore.i18n("An error occurred while "
                                "downloading the image.")
            messagewidget.setText(text)

    def open_browser(self):

        kdecore.KToolInvocation.invokeBrowser(self.url_to_file,
                                              QtCore.QByteArray())

    def put_in_clipboard(self):

        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(self.url_to_file)
