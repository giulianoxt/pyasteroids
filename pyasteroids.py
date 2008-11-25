import random

from sys import argv
from PyQt4.QtGui import QApplication

from util.config import ConfigManager
from pyqt.main_window import AsteroidsMainWindow


def start_pyasteroids():
    random.seed()
    
    # Faster processing
    try:
        import psyco
        psyco.full()
    except:
        print 'You currently do not have the Psyco module in your PYTHONPATH.'
        print 'It is highly advisable to install it for a much better gaming performance.'
        print 'Official site: http://psyco.sourceforge.net/'

    # Load the config files in memory'
    ConfigManager()

    app = QApplication(argv)

    # Creates the window (GLWidget is created there)
    win = AsteroidsMainWindow()

    # Pop-up the window    
    win.show()

    # Gives control to Qt
    app.exec_()
    

if __name__ == '__main__':
    print '# PyAsteroids3D #\n'
    
    start_pyasteroids()
    
    print 'Leaving...'
    