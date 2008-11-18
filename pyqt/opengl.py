import os
from sys import exc_info
from time import time

from OpenGL.GL import *
from OpenGL.GLU import *

from PyQt4 import QtCore
from PyQt4.QtOpenGL import QGLWidget
from PyQt4.QtCore import Qt, QTimer, QObject

import screens
from util.config import Config


class GLController(QGLWidget):
    def __init__(self, parent):
        try:
            QGLWidget.__init__(self, parent)
        
            cfg = Config('game','OpenGL')
        
            self.fps = cfg.get('fps')
            self.clearColor = cfg.get('clear_color')
        
            self.adjust_widget()
            self.adjust_timer()
        except:
            print 'excecao controller init!, exc = ', exc_info()[1]
    
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
        
        self.screen_stack = []
            
        first_screen = Config('game','Screens').get('first_screen')
           
        self.push_screen(first_screen)

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
        
        #glMatrixMode(GL_MODELVIEW)
        #glLoadIdentity()

    def paintGL(self):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        self.screen_stack[-1].draw()
        
        glPopMatrix()
    
    def tick(self):
        new_time = time()
        elapsed = new_time - self.last_time
        self.last_time = new_time
        
        self.fps = 1 / elapsed
        
        self.screen_stack[-1].tick(elapsed)
        
        self.updateGL()

    # dynamic dispatch of qt events to screens
    def __getattr__(self, attr):
        # if its an event (keyPressEvent, mousePressEvent, etc..)
        if (attr.endswith('Event')):
            # let the top screen handle it
            return getattr(self.screen_stack[-1], attr)
        else:
            raise AttributeError

    def pop_screen(self, screen):
        # erases that screen and all above it
        i = self.screen_stack.index(screen)
        del self.screen_stack[i:]
        
        # if we run out of screens, the game is over
        if (not len(self.screen_stack)):
            self.parent().parent().close()

    def push_screen(self, new_screen_name, *args, **kwargs):   
        NewScreenCls = None
        
        # the new screen class can be in the screens module
        # or in a submodule on that directory
               
        submodules = []
        
        for f in os.listdir('screens'):
            # remove extension
            f = f[0:f.rfind('.')]
            
            try:
                m = __import__('screens.'+f, fromlist=[f])
                submodules.append(m)
            except:
                pass
                
        modules = submodules + [screens]
        
        for mod in modules:
            if (hasattr(mod, new_screen_name)):
                NewScreenCls = getattr(mod, new_screen_name)
                break
        
        # create a new screen instance using the arguments
        # sent by the previous screen
        new_screen = NewScreenCls(*args, **kwargs)
        
        # include a reference to this controller
        new_screen.controller = self
        
        # finally, push it
        self.screen_stack.append(new_screen)
