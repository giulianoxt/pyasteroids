from OpenGL.GL import *
from OpenGL.GLU import *

from util.config import ConfigManager


_fovy = float(ConfigManager.getVal('game','OpenGL','y_field_of_view'))
_z_near = float(ConfigManager.getVal('game','OpenGL','z_near'))
_z_far = float(ConfigManager.getVal('game','OpenGL','z_far')) 
      
def default_perspective(width, height):
    glViewport(0,0,width,height)
        
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
        
    gluPerspective(_fovy,float(width)/height,_z_near,_z_far)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    glClear(GL_DEPTH_BUFFER_BIT)

def custom_ortho_projection(x, y, width, height):
    glViewport(x,y,width,height)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    w, h = map(int, (width, height))
    
    gluOrtho2D(0.,w,h,0.)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    glClear(GL_DEPTH_BUFFER_BIT)
    
def ortho_projection(width, height):
    custom_ortho_projection(0, 0, width, height)
