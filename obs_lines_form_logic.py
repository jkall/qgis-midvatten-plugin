# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from sqlite3 import dbapi2 as sqlite
import midvatten_utils as utils        # Whenever some global midvatten_utilities are needed

myDialog = None

def formOpen(dialog,layerid,featureid):
    global myDialog        #
    myDialog = dialog
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

    # Wire up our own signals.
    buttonBox.accepted.connect(validate)
    buttonBox.rejected.connect(myDialog.reject)

def validate():  # Make sure mandatory fields are not empty.
    if not (myDialog.findChild(QLineEdit,"obsid").text().length() > 0):
        utils.pop_up_info("obsid must not be empty!")
    elif myDialog.findChild(QLineEdit,"obsid").text()=='NULL':
        utils.pop_up_info("obsid must not be NULL!")
    else:
        # make sure flowtype is within allowed data domain
        myDialog.accept()