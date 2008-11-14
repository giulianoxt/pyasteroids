import psyco
import random

from sys import argv
from PyQt4.QtGui import QApplication

from pyqt.main_window import AsteroidsMainWindow
from util.config import ConfigManager

def setup_modules():
    random.seed()
    
    # Faster processing
    psyco.full()

    # Load the config files in memory
    ConfigManager()

    # Creates the window (GLWidget is created there)
    win = AsteroidsMainWindow() 

    # Pop-up the window
    win.show()

def start_pyasteroids(a):
    # Gives control to Qt
    a.exec_()


if __name__ == '__main__':
    app = QApplication(argv)
    
    setup_modules()
    start_pyasteroids(app)
