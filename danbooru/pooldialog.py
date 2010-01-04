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
File: pooldialog.py
Author: Luca Beltrame
Description: Dialog for selecting pools to download.
'''

from PyQt4.QtGui import QWidget, QTableWidgetItem
from PyKDE4.kdeui import KDialog

from ui.ui_poolwidget import Ui_PoolWidget


class PoolWidget(QWidget, Ui_PoolWidget):

    def __init__(self, pool_data, parent=None):

        super(PoolWidget, self).__init__(parent)
        self.setupUi(self)

        self.data = pool_data
        self.data = [item for item in pool_data if item.post_count != 0]

        self.populate_table()

    def populate_table(self):

        self.poolDataTable.setRowCount(len(self.data))

        for row_no, pool_item in enumerate(self.data):

            item_id = QTableWidgetItem(unicode(pool_item.id))
            item_name = QTableWidgetItem(pool_item.name)
            item_count = QTableWidgetItem(unicode(pool_item.post_count))

            self.poolDataTable.setItem(row_no, 0, item_id)
            self.poolDataTable.setItem(row_no, 1, item_name)
            self.poolDataTable.setItem(row_no, 2, item_count)
            self.poolDataTable.resizeColumnsToContents()
            self.poolDataTable.sortItems(0)


class PoolDialog(KDialog):

    def __init__(self, pool_data, parent=None):

        super(PoolDialog, self).__init__(parent)

        self.pool_widget = PoolWidget(pool_data)
        self.setMainWidget(self.pool_widget)
