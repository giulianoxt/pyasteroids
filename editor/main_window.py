import os

from PyQt4.QtGui import QMainWindow

from ui_mainWindow import Ui_MainWindow

from model.opengl import GLModel


class EditorMainWindow(QMainWindow, Ui_MainWindow):
    instance = None
    
    def __init__(self):
        QMainWindow.__init__(self)

        EditorMainWindow.instance = self
        
        self.setupUi(self)
        
        self.models = {}
    
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
                
                self.models[filename] = GLModel(open(dirpath+'/'+file, 'r'))

                self.listWidget.addItem(filename)
