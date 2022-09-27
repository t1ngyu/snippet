import sys
from pathlib import Path
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy import uic
from PyQt5.QtCore import pyqtSignal
# import ui.res
import cv2
import numpy as np
import time
from threading import Thread

__appname__ = 'order-helper'
__organization__ = 'none'

class MainWindow(QMainWindow):
    updateProgress = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(Path('ui/main.ui'), self)
        self.load_settings()   
        self.updateProgress.connect(self.update_ui)
        self.thread = Thread(target=self.thread_func, daemon=True)
        self.thread.start()
        
    def update_ui(self, image):
        image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888).rgbSwapped()
        self.lbl_image.setPixmap(QPixmap.fromImage(image))

    def thread_func(self):
        time.sleep(1)
        while True:
            img = np.zeros((400, 400, 3), np.uint8)
            x = np.random.randint(0, 400)
            y = np.random.randint(0, 400)
            image = cv2.line(img, (0,0), (x,y),(255, 0, 0), 5)
            self.updateProgress.emit(image)

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
