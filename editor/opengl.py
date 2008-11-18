import os
from time import time

from OpenGL.GL import *
from OpenGL.GLU import *

from PyQt4 import QtCore
from PyQt4.QtOpenGL import QGLWidget
from PyQt4.QtCore import Qt, QTimer, QObject

from util.config import Config


class GLController(QGLWidget):
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        
        cfg = Config('game','OpenGL')
        
        self.fps = cfg.get('fps')
        self.clearColor = cfg.get('clear_color')
        
        self.adjust_widget()
        self.adjust_timer()
    
    def adjust_widget(self):
        self.setAttribute(Qt.WA_KeyCompression,False)
        self.setMouseTracking(True)
    
    def adjust_timer(self):
        self.timer = QTimer(self)
        QObject.connect(self.timer, QtCore.SIGNAL('timeout()'), self.tick)
        self.last_time = time()
        self.timer.start(1000.0 / self.fps)
       
    def initializeGL(self):
        # Enable color blending in polygons
        glEnable(GL_BLEND)
        glShadeModel(GL_SMOOTH)
        
        # Z-buffer testing
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        
        # Texture handling
        glEnable(GL_TEXTURE_2D)
        
        # Enable antialiasing for all primitive renders
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);
        
        # Enable transparency by alpha value
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                
        glClearColor(*map(lambda c : c / 255.0, self.clearColor)) 

    def resizeGL(self, width, height):
        QGLWidget.resizeGL(self,width,height)
        
        glViewport(0,0,width,height)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        cfg = Config('game','OpenGL')
        fovy = cfg.get('y_field_of_view')
        z_near = cfg.get('z_near')
        z_far = cfg.get('z_far')
        gluPerspective(fovy,float(width)/height,z_near,z_far)

    def paintGL(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    def tick(self):
        new_time = time()
        elapsed = new_time - self.last_time
        self.last_time = new_time
        
        self.fps = 1 / elapsed
        
        self.updateGL()
