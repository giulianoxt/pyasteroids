from sys import argv
from PyQt4.QtGui import QApplication
from util.config import ConfigManager
from editor.main_window import EditorMainWindow

if __name__ == '__main__':
    ConfigManager()
    
    app = QApplication(argv)
    
    win = EditorMainWindow()
    win.show()
    
    app.exec_()
