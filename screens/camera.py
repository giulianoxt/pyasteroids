from OpenGL.GL import *
from OpenGL.GLU import *

from physics.vector3d import Vector3d
from physics.quaternion import Quaternion

v3d = Vector3d


class Camera(object):
    def __init__(self, ship, camera_dist):
        self.ship = ship
        self.dist = camera_dist

        self.pos = None
        self.look = None
        self.up = None

        self.recalculate_vectors()
            
    def recalculate_vectors(self):        
        sh = self.ship.shape
        ax, ay, az = sh.angle_x, sh.angle_y, sh.angle_z

        rotation = Quaternion.from_axis_rotations(ax,ay,az)

        ship_dir = rotation * Vector3d(0.,0.,-1.).normalizing()

        up_dir = rotation * Vector3d(0.,1.,0.).normalizing()
        
        oposite = ship_dir.scalar(-1.)
        oposite = oposite.scalar(self.dist)

        self.pos = sh.position + oposite
        self.look = self.pos + ship_dir
        self.up = up_dir
        
    def put_in_position(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        ex, ey, ez = self.pos
        lx, ly, lz = self.look
        ux, uy, uz = self.up
        
        gluLookAt(ex,ey,ez,lx,ly,lz,ux,uy,uz)
    
    def tick(self, time_elapsed):
        self.recalculate_vectors()
