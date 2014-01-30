# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'simpleplotdialog.ui'
#
# Created: Thu Jan 30 13:07:55 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(625, 348)
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.plotareawidget = QtGui.QWidget(Dialog)
        self.plotareawidget.setMinimumSize(QtCore.QSize(0, 0))
        self.plotareawidget.setObjectName(_fromUtf8("plotareawidget"))
        self.gridLayout = QtGui.QGridLayout(self.plotareawidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.mplplotlayout = QtGui.QVBoxLayout()
        self.mplplotlayout.setObjectName(_fromUtf8("mplplotlayout"))
        self.gridLayout.addLayout(self.mplplotlayout, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.plotareawidget, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

