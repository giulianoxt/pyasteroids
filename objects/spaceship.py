from OpenGL.GL import *

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
        
        self.mouse_sensivity = Config('game','Mouse').get('sensivity')
        
        self.rotation = Quaternion.from_axis_rotations(0.,0.,0.)
        
        self.ship_dir = None
        self.up_dir = None
        
        self.spinning = {
            'up'    : False,
            'down'  : False,
            'left'  : False,
            'right' : False
        }
        
        self.vectors = {
            'up'    : (Vector3d.x_axis(), 1.),
            'down'  : (Vector3d.x_axis(), -1.),
            'left'  : (Vector3d.y_axis(), 1.),
            'right' : (Vector3d.y_axis(), -1.)
        }

    def draw(self):        
        glMatrixMode(GL_MODELVIEW)
        
        glPushMatrix()
                
        glTranslate(*self.shape.position)

        axis, angle = self.rotation.get_axis_angle()
        
        ax, ay, az = axis

        glRotatef(angle, ax, ay, az)
        
        self.model.draw()
        
        glPopMatrix()

    def tick(self, time_elapsed):       
        Object.tick(self, time_elapsed)
        
        self.update_directions()
        self.update_spinning(time_elapsed)
        
    def update_directions(self):
        self.ship_dir = self.rotation * Vector3d(0.,0.,-1.)

        self.up_dir = self.rotation * Vector3d(0.,1.,0.)

    def update_spinning(self, time_elapsed):
        for dir in self.spinning:
            if (self.spinning[dir]):
                axis, sign = self.vectors[dir]
                angle = self.spin_velocity * time_elapsed * sign
                
                r = Quaternion.from_axis_angle(axis, angle)
                
                self.rotation = self.rotation * r

    def move_forward(self):
        force = self.ship_dir.normalizing().scalar(self.move_force_sz)
        
        self.shape.forces_tmp.append(force)
    
    def move_left(self):
        pass
    
    def move_right(self):
        pass
    
    def spin(self, dir, b):
        self.spinning[dir] = b

    def mouse_spin(self, dx, dy):
        if (dx != 0):
            ax = self.mouse_sensivity * dx * -1.
            r = Quaternion.from_axis_angle(Vector3d.y_axis(),ax)
            
            self.rotation = self.rotation * r    
            
        if (dy != 0):
            ay = self.mouse_sensivity * dy * -1.
            r = Quaternion.from_axis_angle(Vector3d.x_axis(),ay)
            
            self.rotation = self.rotation * r
