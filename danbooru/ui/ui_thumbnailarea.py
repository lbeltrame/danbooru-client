#!/usr/bin/env python
# coding=UTF-8
#
# Generated by pykdeuic4 from ui_src/thumbnailarea.ui on Sat Dec 19 21:54:57 2009
#
# WARNING! All changes to this file will be lost.
from PyKDE4 import kdecore
from PyKDE4 import kdeui
from PyQt4 import QtCore, QtGui

class Ui_ThumbnailArea(object):
    def setupUi(self, ThumbnailArea):
        ThumbnailArea.setObjectName("ThumbnailArea")
        ThumbnailArea.resize(570, 502)
        self.gridLayout = QtGui.QGridLayout(ThumbnailArea)
        self.gridLayout.setObjectName("gridLayout")
        self.thumbnailTabWidget = KTabWidget(ThumbnailArea)
        self.thumbnailTabWidget.setObjectName("thumbnailTabWidget")
        self.gridLayout.addWidget(self.thumbnailTabWidget, 0, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(370, 21, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.nextPageButton = KPushButton(ThumbnailArea)
        self.nextPageButton.setObjectName("nextPageButton")
        self.gridLayout.addWidget(self.nextPageButton, 1, 1, 1, 1)

        self.retranslateUi(ThumbnailArea)
        QtCore.QMetaObject.connectSlotsByName(ThumbnailArea)

    def retranslateUi(self, ThumbnailArea):
        self.nextPageButton.setText(kdecore.i18n("More results"))

from PyKDE4.kdeui import KPushButton, KTabWidget
