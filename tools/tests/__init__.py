from qgis.PyQt import QtGui, QtWidgets
from qgis.core import QgsApplication

# Assurance that this only happens once for each test run
app = QtWidgets.QApplication([])
qgs = QgsApplication([], False)
qgs.initQgis()