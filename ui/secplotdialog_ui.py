# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'secplotdialog_ui.ui'
#
# Created: Sun Dec  1 22:20:57 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_SecPlotWindow(object):
    def setupUi(self, SecPlotWindow):
        SecPlotWindow.setObjectName(_fromUtf8("SecPlotWindow"))
        SecPlotWindow.setWindowModality(QtCore.Qt.WindowModal)
        SecPlotWindow.resize(704, 389)
        self.gridLayout_3 = QtGui.QGridLayout(SecPlotWindow)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.splitter = QtGui.QSplitter(SecPlotWindow)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.frame = QtGui.QFrame(self.splitter)
        self.frame.setMinimumSize(QtCore.QSize(180, 0))
        self.frame.setMaximumSize(QtCore.QSize(275, 16777215))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout = QtGui.QGridLayout(self.frame)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.wlvltableComboBox = QtGui.QComboBox(self.frame)
        self.wlvltableComboBox.setObjectName(_fromUtf8("wlvltableComboBox"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.wlvltableComboBox)
        self.verticalLayout_3.addLayout(self.formLayout)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.datetimelistWidget = QtGui.QListWidget(self.frame)
        self.datetimelistWidget.setObjectName(_fromUtf8("datetimelistWidget"))
        self.verticalLayout.addWidget(self.datetimelistWidget)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_4 = QtGui.QLabel(self.frame)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout_2.addWidget(self.label_4)
        self.timeframelistWidget = QtGui.QListWidget(self.frame)
        self.timeframelistWidget.setObjectName(_fromUtf8("timeframelistWidget"))
        self.verticalLayout_2.addWidget(self.timeframelistWidget)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.line = QtGui.QFrame(self.frame)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout_3.addWidget(self.line)
        self.formLayout_2 = QtGui.QFormLayout()
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.label_5 = QtGui.QLabel(self.frame)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_5)
        self.textcolComboBox = QtGui.QComboBox(self.frame)
        self.textcolComboBox.setObjectName(_fromUtf8("textcolComboBox"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.textcolComboBox)
        self.verticalLayout_3.addLayout(self.formLayout_2)
        self.formLayout_3 = QtGui.QFormLayout()
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_2)
        self.drillstoplineEdit = QtGui.QLineEdit(self.frame)
        self.drillstoplineEdit.setObjectName(_fromUtf8("drillstoplineEdit"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.FieldRole, self.drillstoplineEdit)
        self.verticalLayout_3.addLayout(self.formLayout_3)
        self.pushButton = QtGui.QPushButton(self.frame)
        self.pushButton.setMaximumSize(QtCore.QSize(250, 16777215))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout_3.addWidget(self.pushButton)
        self.gridLayout.addLayout(self.verticalLayout_3, 0, 0, 1, 1)
        self.plotareawidget = QtGui.QWidget(self.splitter)
        self.plotareawidget.setMinimumSize(QtCore.QSize(500, 0))
        self.plotareawidget.setObjectName(_fromUtf8("plotareawidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.plotareawidget)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.mplplotlayout = QtGui.QVBoxLayout()
        self.mplplotlayout.setObjectName(_fromUtf8("mplplotlayout"))
        self.gridLayout_2.addLayout(self.mplplotlayout, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.splitter, 0, 0, 1, 1)
        self.label.setBuddy(self.wlvltableComboBox)
        self.label_3.setBuddy(self.wlvltableComboBox)
        self.label_4.setBuddy(self.wlvltableComboBox)
        self.label_5.setBuddy(self.wlvltableComboBox)
        self.label_2.setBuddy(self.wlvltableComboBox)

        self.retranslateUi(SecPlotWindow)
        QtCore.QMetaObject.connectSlotsByName(SecPlotWindow)

    def retranslateUi(self, SecPlotWindow):
        SecPlotWindow.setWindowTitle(QtGui.QApplication.translate("SecPlotWindow", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SecPlotWindow", "wlvl", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("SecPlotWindow", "datetime", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("SecPlotWindow", "timeframe", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("SecPlotWindow", "text", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("SecPlotWindow", "drillstop", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("SecPlotWindow", "Replot", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SecPlotWindow = QtGui.QDialog()
    ui = Ui_SecPlotWindow()
    ui.setupUi(SecPlotWindow)
    SecPlotWindow.show()
    sys.exit(app.exec_())

