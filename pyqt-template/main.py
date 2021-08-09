import sys
from pathlib import Path
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy import uic
# import ui.res

__appname__ = 'order-helper'
__organization__ = 'none'

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(Path('ui/main.ui'), self)
        self.load_settings()

    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue('MainWindow/Geometry', self.saveGeometry())
        settings.setValue('MainWindow/State', self.saveState())

    def load_settings(self):
        settings = QSettings()
        self.restoreGeometry(settings.value('MainWindow/Geometry'))
        self.restoreState(settings.value('MainWindow/State'))



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName(__appname__)
    app.setOrganizationName(__organization__)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
