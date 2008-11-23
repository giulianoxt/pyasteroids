from OpenGL.GL import *
from OpenGL.GLU import *

from util.config import ConfigManager


_fovy = float(ConfigManager.getVal('game','OpenGL','y_field_of_view'))
_z_near = float(ConfigManager.getVal('game','OpenGL','z_near'))
_z_far = float(ConfigManager.getVal('game','OpenGL','z_far')) 
      
def setup_perspective(width, height):
    glViewport(0,0,width,height)
        
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
        
    gluPerspective(_fovy,float(width)/height,_z_near,_z_far)