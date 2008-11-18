from PyQt4.QtGui import QMainWindow
from ui_mainWindow import Ui_MainWindow

class EditorMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)