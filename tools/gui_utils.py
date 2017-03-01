# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin handles shared gui tools

 This part is to a big extent based on QSpatialite plugin.
                             -------------------
        begin                : 2016-11-27
        copyright            : (C) 2016 by HenrikSpa (and joskal)
        email                : groundwatergis [at] gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import PyQt4

from midvatten_utils import returnunicode


class SplitterWithHandel(PyQt4.QtGui.QSplitter):
    """
    Creates a splitter with a handle

    Using code from http://stackoverflow.com/questions/2545577/qsplitter-becoming-undistinguishable-between-qwidget-and-qtabwidget
    """
    def __init__(self, *args, **kwargs):
        super(SplitterWithHandel, self).__init__(*args, **kwargs)
        handle = self.handle(1)
        self.setHandleWidth(10)
        layout = PyQt4.QtGui.QVBoxLayout(handle)
        layout.setSpacing(0)
        layout.setMargin(0)
        line = PyQt4.QtGui.QFrame(handle)
        line.setFrameShape(PyQt4.QtGui.QFrame.HLine)
        line.setFrameShadow(PyQt4.QtGui.QFrame.Sunken)
        layout.addWidget(line)


class RowEntry(object):
    def __init__(self):
        self.widget = PyQt4.QtGui.QWidget()
        self.layout = PyQt4.QtGui.QHBoxLayout()
        self.widget.setLayout(self.layout)


class VRowEntry(object):
    def __init__(self):
        self.widget = PyQt4.QtGui.QWidget()
        self.layout = PyQt4.QtGui.QVBoxLayout()
        self.widget.setLayout(self.layout)


class RowEntryGrid(object):
    def __init__(self):
        self.widget = PyQt4.QtGui.QWidget()
        self.layout = PyQt4.QtGui.QGridLayout()
        self.widget.setLayout(self.layout)


class CopyPasteDeleteableQListWidget(PyQt4.QtGui.QListWidget):
    """

    """
    def __init__(self, keep_sorted=False, *args, **kwargs):
        super(CopyPasteDeleteableQListWidget, self).__init__(*args, **kwargs)
        self.setSelectionMode(PyQt4.QtGui.QAbstractItemView.ExtendedSelection)
        self.keep_sorted = keep_sorted

    def keyPressEvent(self, e):
        """
        Method using many parts from http://stackoverflow.com/a/23919177
        :param e:
        :return:
        """

        if e.type() == PyQt4.QtCore.QEvent.KeyPress:
            key = e.key()
            modifiers = e.modifiers()

            if modifiers & PyQt4.QtCore.Qt.ShiftModifier:
                key += PyQt4.QtCore.Qt.SHIFT
            if modifiers & PyQt4.QtCore.Qt.ControlModifier:
                key += PyQt4.QtCore.Qt.CTRL
            if modifiers & PyQt4.QtCore.Qt.AltModifier:
                key += PyQt4.QtCore.Qt.ALT
            if modifiers & PyQt4.QtCore.Qt.MetaModifier:
                key += PyQt4.QtCore.Qt.META

            new_sequence = PyQt4.QtGui.QKeySequence(key)

            if new_sequence.matches(PyQt4.QtGui.QKeySequence.Copy):
                self.copy_data()
            elif new_sequence.matches(PyQt4.QtGui.QKeySequence.Paste):
                self.paste_data()
            elif new_sequence.matches(PyQt4.QtGui.QKeySequence.Delete):
                self.delete_data()
            elif new_sequence.matches(PyQt4.QtGui.QKeySequence.Cut):
                self.cut_data()

    def copy_data(self):
        self.selectedItems()
        stringlist = [item.text() for item in self.selectedItems()]
        PyQt4.QtGui.QApplication.clipboard().setText(u'\n'.join(stringlist))

    def cut_data(self):
        all_items = [self.item(i).text() for i in xrange(self.count())]
        items_to_delete = [item.text() for item in self.selectedItems()]
        PyQt4.QtGui.QApplication.clipboard().setText(u'\n'.join(items_to_delete))
        keep_items = [item for item in all_items if item not in items_to_delete]
        self.clear()
        self.addItems(sorted(keep_items))

    def paste_data(self, paste_list=None):
        if paste_list is None:
            paste_list = PyQt4.QtGui.QApplication.clipboard().text().split(u'\n')

        #Use lists to keep the data ordering (the reason set() is not used
        old_text = self.get_all_data()
        new_items = []
        for alist in [old_text, paste_list]:
            for x in alist:
                if x not in new_items:
                    new_items.append(returnunicode(x))

        self.clear()
        if self.keep_sorted:
            self.addItems(list(sorted(new_items)))
        else:
            self.addItems(list(new_items))

    def delete_data(self):
        all_items = [self.item(i).text() for i in xrange(self.count())]
        items_to_delete = [item.text() for item in self.selectedItems()]
        keep_items = [item for item in all_items if item not in items_to_delete]
        self.clear()
        self.addItems(sorted(keep_items))

    def get_all_data(self):
        return returnunicode([self.item(i).text() for i in xrange(self.count())], keep_containers=True)