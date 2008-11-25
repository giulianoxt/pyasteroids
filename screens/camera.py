from OpenGL.GL import *
from OpenGL.GLU import *

from physics.vector3d import Vector3d

v3d = Vector3d


class Camera(object):
    def __init__(self, ship, camera_dist):
        self.ship = ship
        self.dist = camera_dist

        self.pos = None
        self.look = None
        self.up = None

        self.s = -1.

        self.recalculate_vectors()
            
    def recalculate_vectors(self):
        if (self.ship.ship_dir is None):
            return
        
        ship_dir = self.ship.ship_dir
        up_dir = self.ship.up_dir
        
        oposite = ship_dir.scalar(self.s)
        oposite = oposite.scalar(self.dist)

        self.pos = self.ship.shape.position + oposite
        self.look = self.ship.shape.position + ship_dir
        self.up = up_dir
        
    def put_in_position(self):
        if (self.pos is None):
            return
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        ex, ey, ez = self.pos
        lx, ly, lz = self.look
        ux, uy, uz = self.up
        
        gluLookAt(ex,ey,ez,lx,ly,lz,ux,uy,uz)
    
    def tick(self, time_elapsed):
        self.recalculate_vectors()
        
    def invert(self):
        self.s *= -1.
