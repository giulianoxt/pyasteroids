from OpenGL.GL import *
from OpenGL.GLU import *

from physics.vector3d import Vector3d

v3d = Vector3d

class Camera(object):
    def __init__(self, ship, camera_dist):
        self.ship = ship
        self.dist = camera_dist

        self.angle_x = self.ship.shape.angle_x
        self.angle_y = self.ship.shape.angle_y
        self.angle_z = self.ship.shape.angle_z

        ship_dir = Vector3d(0.,0.,-1.).normalizing()
        ship_dir = ship_dir.rotated(self.ship.shape.angle_x, v3d(1., 0., 0.))
        ship_dir = ship_dir.rotated(self.ship.shape.angle_y, v3d(0., 1., 0.))
        ship_dir = ship_dir.rotated(self.ship.shape.angle_z, v3d(0., 0., 1.))

        up_dir = Vector3d(0.,1.,0.).normalizing()
        up_dir = up_dir.rotated(self.ship.shape.angle_x, v3d(1., 0., 0.))
        up_dir = up_dir.rotated(self.ship.shape.angle_y, v3d(0., 1., 0.))
        up_dir = up_dir.rotated(self.ship.shape.angle_z, v3d(0., 0., 1.))

        oposite = ship_dir.scalar(-1.)
        oposite = oposite.scalar(self.dist)

        self.pos = self.ship.shape.position + oposite
        self.look = ship_dir.scalar(10000)
        self.up = up_dir
    
    def recalculate_vectors(self):        
        sh = self.ship.shape
        ax, ay, az = self.angle_x, self.angle_y, self.angle_z
        sax, say, saz = sh.angle_x, sh.angle_y, sh.angle_z
        
        if (not (ax != sax or ay != say or az != saz)):
            return        
        
        dax = sax - ax
        day = say - ay
        daz = saz - az
        
        up = self.up.normalizing()
        up = up.rotated(dax, v3d(1., 0., 0.))
        up = up.rotated(day, v3d(0., 1., 0.))
        up = up.rotated(daz, v3d(0., 0., 1.))
        self.up = up
            
        look = self.look.normalizing()
        look = look.rotated(dax, v3d(1., 0., 0.))
        look = look.rotated(day, v3d(0., 1., 0.))
        look = look.rotated(daz, v3d(0., 0., 1.))
        self.look = look.normalizing()
               
        oposite = self.look.scalar(-1.)
        oposite = oposite.scalar(self.dist)
        
        self.pos = self.ship.shape.position + oposite
        
        self.look = self.look.normalizing().scalar(10000)
        
        self.pos.adjust_complex()
        self.look.adjust_complex()
        
        self.angle_x = sax
        self.angle_y = say
        self.angle_z = saz
        
    def put_in_position(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        ex, ey, ez = self.pos
        lx, ly, lz = self.look
        ux, uy, uz = self.up
        
        gluLookAt(ex,ey,ez,lx,ly,lz,ux,uy,uz)
    
    def tick(self, time_elapsed):
        #TODO: update camera vectors according to the ship movement
        self.recalculate_vectors()
