# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainForm.ui'
#
# Created: Fri Nov 14 10:06:41 2008
#      by: PyQt4 UI code generator 4.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_mainForm(object):
    def setupUi(self, mainForm):
        mainForm.setObjectName("mainForm")
        mainForm.resize(1200,600)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(mainForm.sizePolicy().hasHeightForWidth())
        mainForm.setSizePolicy(sizePolicy)
        mainForm.setMinimumSize(QtCore.QSize(1200,600))
        mainForm.setMaximumSize(QtCore.QSize(1200,600))
        self.widget = GLController(mainForm)
        self.widget.setGeometry(QtCore.QRect(0,0,1200,600))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")

        self.retranslateUi(mainForm)
        QtCore.QMetaObject.connectSlotsByName(mainForm)

    def retranslateUi(self, mainForm):
        mainForm.setWindowTitle(QtGui.QApplication.translate("mainForm", "PyAsteroids 3D", None, QtGui.QApplication.UnicodeUTF8))

from pyqt.opengl import GLController
