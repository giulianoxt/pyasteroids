from math import *

from OpenGL.GL import *
from OpenGL.GLU import *

from util.config import ConfigManager
from physics.vector3d import Vector3d

_fovy = float(ConfigManager.getVal('game','OpenGL','y_field_of_view'))
_z_near = float(ConfigManager.getVal('game','OpenGL','z_near'))
_z_far = float(ConfigManager.getVal('game','OpenGL','z_far')) 


def default_perspective(width, height, x = 0, y = 0):
    glViewport(x,y,width,height)
        
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
        
    gluPerspective(_fovy,float(width)/height,_z_near,_z_far)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    glClear(GL_DEPTH_BUFFER_BIT)

def custom_ortho_projection(x, y, left, right, bottom, top):
    w = abs(left - right)
    h = abs(top - bottom)
    
    glViewport(x,y,w,h)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    gluOrtho2D(left,right,bottom,top)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    glClear(GL_DEPTH_BUFFER_BIT)
    
def ortho_projection(width, height):
    custom_ortho_projection(0, 0, 0, width, height, 0)

def spherical_billboarding(cam_pos, obj_pos):
    look_at = Vector3d(0.,0.,0.)
    obj_to_cam_proj = Vector3d(0.,0.,0.)
    up_aux = Vector3d(0.,0.,0.)
    angle_cosine = 0.

    obj_to_cam_proj.x = cam_pos.x - obj_pos.x
    obj_to_cam_proj.z = cam_pos.z - obj_pos.z
    
    look_at.z = 1.
    
    obj_to_cam_proj = obj_to_cam_proj.normalizing()
    
    up_aux = look_at.cross_product(obj_to_cam_proj)
    
    angle_cosine = look_at * obj_to_cam_proj
    
    if (angle_cosine < 0.99990 and angle_cosine > -0.9999):
        glRotatef(degrees(acos(angle_cosine)), *up_aux)
    
    obj_to_cam = (cam_pos - obj_pos).normalizing()
    
    angle_cosine = obj_to_cam_proj * obj_to_cam
     
    if (angle_cosine < 0.99990 and angle_cosine > -0.9999):
        if (obj_to_cam[1] < 0):
            glRotatef(degrees(angle_cosine),1.,0.,0.)
        else:
            glRotatef(degrees(angle_cosine),-1.,0.,0.)

try:
    import psyco
    psyco.bind(spherical_billboarding)
except:
    pass
