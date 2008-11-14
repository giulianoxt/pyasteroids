import psyco
import random

from sys import argv
from PyQt4.QtGui import QApplication

from pyqt.main_window import AsteroidsMainWindow
from util.config import ConfigManager

def start_pyasteroids():
    random.seed()
    
    # Faster processing
    psyco.full()

    a = QApplication(argv)

    # Load the config files in memory
    ConfigManager()

    # Creates the window (GLWidget is created there)
    win = AsteroidsMainWindow() 

    # Pop-up the window
    win.show()

    # Gives control to Qt
    a.exec_()


if __name__ == '__main__':
    start_pyasteroids()
