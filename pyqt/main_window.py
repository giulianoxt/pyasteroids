from PyQt4.QtGui import QMainWindow

from pyqt.ui.mainForm import Ui_mainForm as uiMainWindow


class AsteroidsMainWindow(QMainWindow, uiMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
