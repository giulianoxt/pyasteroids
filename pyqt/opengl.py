from time import time

from OpenGL.GL import *
from OpenGL.GLU import *

from PyQt4 import QtCore
from PyQt4.QtOpenGL import QGLWidget
from PyQt4.QtCore import Qt, QTimer, QObject

from util.config import Config

from model.opengl import GLModel

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
        
        
        
        # TODO: remover isso abaixo. Soh pra testes
        
        self.test_model = GLModel(open(
            'resources/models/planets/io.ply')
        )
        self.test_model.x_r = 0
        self.test_model.y_r = 0
        self.test_model.z_r = 0
        
        glEnable(GL_LIGHTING)
        
        glMaterialfv(GL_FRONT, GL_AMBIENT, (.5,.5,.5,1.))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (.9,.9,.9,.8))
        glLightfv(GL_LIGHT0, GL_POSITION, (0.,500.,10000.,1.))

        glEnable(GL_LIGHT0) 
        

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
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        
        # TODO: CAMERA PROVISORIA! fazer uma classe Camera
        gluLookAt(0.,0.,50.,0.,0.,-1.,0.,1.,0.)

    def paintGL(self):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        
        # TODO: esquema de drawing. Isso aqui eh soh pra teste
        glScalef(10.,10.,10.)
              
        glRotatef(self.test_model.x_r,1.,0.,0.)
        glRotatef(self.test_model.y_r,0.,1.,0.)
        glRotatef(self.test_model.z_r,0.,0.,1.)
        
        self.test_model.draw()
        
        glPopMatrix()
    
    def tick(self):
        new_time = time()
        elapsed = new_time - self.last_time
        self.last_time = new_time
        
        self.fps = 1 / elapsed
        
        #print 'fps = ', int(self.fps)
        
        
        #TODO: atualizar o estado dos objetos aqui
        self.test_model.x_r += 0.2
        self.test_model.z_r += 0.1
        self.test_model.y_r += 0.2
        
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
