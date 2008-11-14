import random

from sys import argv
from PyQt4.QtGui import QApplication

from pyqt.main_window import AsteroidsMainWindow
from util.config import ConfigManager

def setup_modules():
    random.seed()
    
    # Faster processing
    try:
        import psyco
        psyco.full()
    except:
        print 'You currently do not have the Psyco module in your PYTHONPATH.'
        print 'It is highly advisable to install it for a much better gaming performance.'
        print 'Official site: http://psyco.sourceforge.net/'

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
    print '# PyAsteroids3D #\n'
    
    app = QApplication(argv)
    
    setup_modules()
    start_pyasteroids(app)
