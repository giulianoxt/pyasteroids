from time import time

from OpenGL.GL import *
from OpenGL.GLU import *

from PyQt4 import QtCore
from PyQt4.QtOpenGL import QGLWidget
from PyQt4.QtCore import Qt, QTimer, QObject

from util.config import Config


class GLController(QGLWidget):
    instance = None
    
    @classmethod
    def getInstance(cls):
        return GLController.instance
    
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        
        if (GLController.instance is None):
            GLController.instance = self
        
        self.parent = parent
        
        cfg = Config('game','OpenGL')
        
        self.fps = cfg.get('fps')
        self.clearColor = cfg.get('clear_color')
               
        self.adjustWidget()
        self.adjustTimer()
    
    def adjustWidget(self):
        self.setAttribute(Qt.WA_KeyCompression,False)
        self.setMouseTracking(True)
    
    def adjustTimer(self):
        self.timer = QTimer(self)
        QObject.connect(self.timer, QtCore.SIGNAL('timeout()'), self.tick)
        self.last_time = time()
        self.timer.start(1000.0 / self.fps)
       
    def initializeGL(self):
        glShadeModel(GL_SMOOTH)
        
        glEnable(GL_BLEND)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POINT_SMOOTH)
        
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                
        glClearColor(*map(lambda c : c / 255.0, self.clearColor))

    def resizeGL(self, width, height):
        QGLWidget.resizeGL(self,width,height)
        
        glViewport(0,0,width,height)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0,width-1,height-1,0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # TODO: draw
        
        glPopMatrix()
    
    def tick(self):
        new_time = time()
        elapsed = new_time - self.last_time
        self.last_time = new_time
        
        self.fps = 1 / elapsed
        
        #TODO: tick
        
        self.updateGL()
    
    def keyPressEvent(self, keyEvent):
        pass
    
    def keyReleaseEvent(self, keyEvent):
        pass

    def mouseMoveEvent(self, mouseEvent):
        pass
    
    def mousePressEvent(self, mouseEvent):
        pass
    
    def mouseReleaseEvent(self, mouseEvent):
        pass

    def contextMenuEvent(self, contextEvent):
        pass
