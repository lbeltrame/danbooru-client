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

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui

import PyKDE4.kdecore as kdecore
import PyKDE4.kdeui as kdeui

from ui import ui_pooldock


class DanbooruPoolWidget(ui_pooldock.Ui_PoolWidget, QtGui.QWidget):

    poolDownloadRequested = QtCore.pyqtSignal(int)

    def __init__(self, api_data, parent=None):

        super(DanbooruPoolWidget, self).__init__(parent)
        self.setupUi(self)

        self._api_data = api_data
        self._current_row = 0

        self._api_data.poolRetrieved.connect(self.add_row)
        self.fetchButton.clicked.connect(self.fetch_pools)
        self.poolTable.itemDoubleClicked.connect(self.get_pool)

        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                           QtGui.QSizePolicy.Fixed)

    def add_row(self, pool_item):

        current_row = self._current_row
        self.poolTable.insertRow(current_row)
        self._current_row += 1

        pool_id = QtGui.QTableWidgetItem(pool_item.id)
        pool_name = QtGui.QTableWidgetItem(pool_item.name)
        pool_posts = QtGui.QTableWidgetItem(pool_item.post_count)
        pool_description = QtGui.QTableWidgetItem(pool_item.description)

        pool_id.setToolTip(kdecore.i18n("Double click to download"))
        pool_name.setToolTip(kdecore.i18n("Double click to download"))
        pool_posts.setToolTip(kdecore.i18n("Double click to download"))
        pool_description.setToolTip(kdecore.i18n("Double click to download"))

        pool_id.setData(QtCore.Qt.UserRole, QtCore.QVariant(pool_item.id))
        pool_name.setData(QtCore.Qt.UserRole, QtCore.QVariant(pool_item.id))
        pool_posts.setData(QtCore.Qt.UserRole, QtCore.QVariant(pool_item.id))
        pool_description.setData(QtCore.Qt.UserRole,
                                 QtCore.QVariant(pool_item.id))

        self.poolTable.setItem(current_row, 0, pool_id)
        self.poolTable.setItem(current_row, 1, pool_name)
        self.poolTable.setItem(current_row, 2, pool_posts)
        self.poolTable.setItem(current_row, 3, pool_description)
        self.poolTable.resizeColumnsToContents()

        self.poolTable.sortItems(0)

    def clear(self):

        self.poolTable.clear()

        row_iterator = reversed(xrange(0, self.poolTable.rowCount()))
        column_iterator = reversed(xrange(0, self.poolTable.columnCount()))

        for row in row_iterator:
            self.poolTable.removeRow(row)

        self._current_row = 0

    def fetch_pools(self):

        self._api_data.get_pool_list()

    def get_pool(self, table_item):

        pool_id =  table_item.data(QtCore.Qt.UserRole).toPyObject()
        pool_id = int(pool_id)
        self.poolDownloadRequested.emit(pool_id)
