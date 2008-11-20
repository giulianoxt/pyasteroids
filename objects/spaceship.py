from objects import Object

from util.config import Config

from physics.vector3d import Vector3d
from physics.quaternion import Quaternion


class SpaceShip(Object):
    def __init__(self, model, shape, element):
        Object.__init__(self, model, shape)
        
        cfg = Config('physics','Ship')
        
        self.move_force_sz = cfg.get('move_force')
        self.spin_velocity = cfg.get('spin_velocity')
        
        self.rotation = None
        
        self.shape.mark = True

    def tick(self, time_elapsed):       
        Object.tick(self, time_elapsed)
        
        sh = self.shape
        ax, ay, az = sh.angle_x, sh.angle_y, sh.angle_z

        self.rotation = Quaternion.from_axis_rotations(ax,ay,az)

        self.ship_dir = self.rotation * Vector3d(0.,0.,-1.).normalizing()

        self.up_dir = self.rotation * Vector3d(0.,1.,0.).normalizing()
        
#        print 'position = ', self.shape.position
#        print 'acc = ', self.shape.aceleration
#        print 'vel = ', self.shape.velocity

    def move_forward(self):
        force = self.ship_dir.normalizing().scalar(self.move_force_sz)
        
        self.shape.forces_tmp.append(force)
    
    def move_left(self):
        pass
    
    def move_right(self):
        pass
    
    def spin_up(self):
        pass
    
    def spin_down(self):
        pass
    
    def spin_left(self):
        pass
    
    def spin_right(self):
        pass
