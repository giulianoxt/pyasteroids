import os

from PyQt4.QtGui import QMainWindow, QApplication

from ui_mainWindow import Ui_MainWindow

from model.opengl import GLModel


class EditorMainWindow(QMainWindow, Ui_MainWindow):
    instance = None
    
    def __init__(self):
        QMainWindow.__init__(self)

        EditorMainWindow.instance = self
        
        self.setupUi(self)
        
        self.models = {}
        
        self.setGeometry(int(QApplication.desktop().width() -
            (QApplication.desktop().width() -
            (QApplication.desktop().width() / 2)) * 1.5) / 2,
            int(QApplication.desktop().height() -
            (QApplication.desktop().height() -
             (QApplication.desktop().height() / 2)) * 1.5) / 2,
            int((QApplication.desktop().width() -
            (QApplication.desktop().width() / 2)) * 1.5),
            int((QApplication.desktop().height() -
            (QApplication.desktop().height() / 2)) * 1.5))
    
    def with_gl_context(self):
        self.load_modules()
    
    def load_modules(self):
        for dir in os.listdir('resources/models'):           
            dirpath = 'resources/models/'+dir
            
            if (not os.path.isdir(dirpath) or dir[0] == '.'):
                continue
            
            for file in os.listdir(dirpath):                
                if (not file.endswith('.ply')):
                    continue
                
                filename = file[:-4]
                
                try:
                    self.models[filename] = GLModel(open(dirpath+'/'+file, 'r'))
                    self.listWidget.addItem(filename)
                except:
                    pass
