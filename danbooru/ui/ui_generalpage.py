#!/usr/bin/env python
# coding=UTF-8
#
# Generated by pykdeuic4 from ui_src/generalpage_new.ui on Sun Oct 25 19:28:57 2009
#
# WARNING! All changes to this file will be lost.
from PyKDE4 import kdecore
from PyKDE4 import kdeui
from PyQt4 import QtCore, QtGui

class Ui_GeneralPage(object):
    def setupUi(self, GeneralPage):
        GeneralPage.setObjectName("GeneralPage")
        GeneralPage.resize(283, 62)
        self.formLayout = QtGui.QFormLayout(GeneralPage)
        self.formLayout.setObjectName("formLayout")
        self.thumbnalLabel = QtGui.QLabel(GeneralPage)
        self.thumbnalLabel.setObjectName("thumbnalLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.thumbnalLabel)
        self.kcfg_thumbnailMaxRetrieve = KIntSpinBox(GeneralPage)
        self.kcfg_thumbnailMaxRetrieve.setMinimum(1)
        self.kcfg_thumbnailMaxRetrieve.setMaximum(10)
        self.kcfg_thumbnailMaxRetrieve.setProperty("value", 3)
        self.kcfg_thumbnailMaxRetrieve.setObjectName("kcfg_thumbnailMaxRetrieve")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.kcfg_thumbnailMaxRetrieve)
        self.columnLabel = QtGui.QLabel(GeneralPage)
        self.columnLabel.setObjectName("columnLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.columnLabel)
        self.kcfg_displayColumns = KIntSpinBox(GeneralPage)
        self.kcfg_displayColumns.setMinimum(1)
        self.kcfg_displayColumns.setMaximum(100)
        self.kcfg_displayColumns.setObjectName("kcfg_displayColumns")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.kcfg_displayColumns)

        self.retranslateUi(GeneralPage)
        QtCore.QMetaObject.connectSlotsByName(GeneralPage)

    def retranslateUi(self, GeneralPage):
        self.thumbnalLabel.setText(kdecore.i18n("Default number of thumbnails to retrieve"))
        self.columnLabel.setText(kdecore.i18n("Number of columns to display"))

from PyKDE4.kdeui import KIntSpinBox
