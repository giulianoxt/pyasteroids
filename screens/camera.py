from OpenGL.GL import *
from OpenGL.GLU import *

from util.deque import Deque
from util.config import Config

from physics.vector3d import Vector3d as v3d


class Camera(object):
    def __init__(self, ship, camera_dist):
        self.ship = ship
        self.dist = camera_dist

        self.pos = None
        self.look = None
        self.up = None

        self.s = -1.

        self.buffer = Deque() # (ship_dir,up_dir) pairs

        self.recalculate_vectors()
            
    def recalculate_vectors(self):
        if (self.ship.ship_dir is None):
            return
        
        if (len(self.buffer) == 0):
            self.init_buffer()
        
        position = self.ship.shape.position
        ship_dir, up_dir = self.update_buffer(self.ship)
        
        oposite = ship_dir.scalar(self.s)
        oposite = oposite.scalar(self.dist)

        self.pos = position + oposite
        self.look = position + ship_dir
        self.up = up_dir
    
    def init_buffer(self):
        sz = Config('game', 'OpenGL').get('camera_buffer_size')
            
        t = (
             v3d(*self.ship.ship_dir),
             v3d(*self.ship.up_dir)
        )
            
        for i in xrange(sz):
            self.buffer.push_back(t)
    
    def update_buffer(self, ship):
        t = (
             v3d(*ship.ship_dir),
             v3d(*ship.up_dir)
        )
        
        obj = self.buffer.pop_front()
        self.buffer.push_back(t)
        
        return obj
    
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
