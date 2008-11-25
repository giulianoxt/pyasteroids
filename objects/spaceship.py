from math import *

from OpenGL.GL import *

from objects import Object

from util import sign
from util.config import Config

from physics.vector3d import Vector3d
from physics.quaternion import Quaternion


class SpaceShip(Object):
    def __init__(self, model, shape, element):
        Object.__init__(self, model, shape, element)
        
        cfg = Config('physics','Ship')
        
        self.move_force_sz = cfg.get('move_force')
        self.spin_velocity = cfg.get('spin_velocity')
        self.strafe_velocity = cfg.get('strafe_velocity')
        
        self.mouse_sensivity = Config('game','Mouse').get('sensivity')
        
        #self.rotation = Quaternion.from_axis_rotations(0.,0.,0.)
        
        self.ship_dir = None
        self.up_dir = None
        
        self.spinning = {
            'up'    : False,
            'down'  : False,
            'left'  : False,
            'right' : False
        }
#                
#        self.vectors = {
#            'up'    : (Vector3d.x_axis(), 1.),
#            'down'  : (Vector3d.x_axis(), -1.),
#            'left'  : (Vector3d.y_axis(), 1.),
#            'right' : (Vector3d.y_axis(), -1.)
#        }
#        
#        self.strafe = {
#            'left'  : False,
#            'right' : False
#        }
#        
#        self.strafe_vectors = {
#            'left'  : Vector3d(-1.,0.,0.),
#            'right' : Vector3d( 1.,0.,0.)
#        }
        
        self.angles = [0.,0.]
        #self.mouse_target = [0.,0.]

    def draw(self):        
        glMatrixMode(GL_MODELVIEW)
        
        glPushMatrix()
                
        glTranslate(*self.shape.position)

#        axis, angle = self.rotation.get_axis_angle()
#        
#        ax, ay, az = axis
#
#        glRotatef(angle, ax, ay, az)

        glRotatef(self.angles[0],1.,0.,0.)
        glRotatef(self.angles[1],0.,1.,0.)
               
        self.model.draw()
        
        glPopMatrix()

#        self.rotation.normalize()

    def tick(self, time_elapsed):       
        Object.tick(self, time_elapsed)
        
        #self.update_mouse_track(time_elapsed)
        self.update_spinning(time_elapsed)
        #self.update_strafe(time_elapsed)
        self.simple_gun.tick(time_elapsed)
        
    def update_spinning(self, time_elapsed):
        a = self.spin_velocity * time_elapsed
        
        if (self.spinning['up']):
            self.angles[0] += a
        if (self.spinning['down']):
            self.angles[0] -= a
        if (self.spinning['left']):
            self.angles[1] += a
        if (self.spinning['right']):
            self.angles[1] -= a
        
        self.rotation = Quaternion.from_axis_rotations(self.angles[0],self.angles[1],0)
        self.ship_dir = self.rotation * Vector3d(0.,0.,-1.)
        self.up_dir = self.rotation * Vector3d(0.,1.,0.)
        
#        for dir in self.spinning:
#            if (self.spinning[dir]):
#                axis, sign = self.vectors[dir]
#                angle = self.spin_velocity * time_elapsed * sign
#                
#                r = Quaternion.from_axis_angle(axis, angle)
#                
#                self.rotation = self.rotation * r
#
#        self.ship_dir = self.rotation * Vector3d(0.,0.,-1.)
#        self.up_dir = self.rotation * Vector3d(0.,1.,0.)

    def move_forward(self):
        force = self.ship_dir.normalizing().scalar(self.move_force_sz)
        
        self.shape.forces_tmp.append(force)
    
#    def update_strafe(self, time_elapsed):
#        for dir in self.strafe:
#            if (self.strafe[dir]):
#                d = self.strafe_velocity * time_elapsed
#        
#                move = (self.rotation * self.strafe_vectors[dir])
#                move = move.normalizing().scalar(d)
#                
#                self.shape.position += move
    
    def spin(self, dir, b):
        self.spinning[dir] = b

#    def strafing(self, dir, b):
#        self.strafe[dir] = b

#    def update_mouse_track(self, time_elapsed):
#        eps = 0.1
#        ax, ay = self.angles
#        tx, ty = self.mouse_target
#        
#        if (fabs(ax - tx) <= eps):
#            self.angles[0] = 0.0
#            self.mouse_target[0] = 0.0
#        else:
#            before = sign(tx - ax)
#            d = self.spin_velocity * time_elapsed * sign(tx - ax)
#            self.angles[0] += d
#            after = sign(tx - self.angles[0])
#            
#            if (before != after):
#                self.angles[0] = 0.0
#                self.mouse_target[0] = 0.0
#            
#            r = Quaternion.from_axis_angle(Vector3d(0.,1.,0.), d)
#            self.rotation = self.rotation * r
#            
#        if (fabs(ay - ty) <= eps):
#            self.angles[1] = 0.0
#            self.mouse_target[1] = 0.0
#        else:
#            before = sign(ty - ay)
#            d = self.spin_velocity * time_elapsed * sign(ty - ay)
#            self.angles[1] += d
#            after = sign(ty - self.angles[1])
#            
#            if (before != after):
#                self.angles[1] = 0.0
#                self.mouse_target[1] = 0.0
#            
#            r = Quaternion.from_axis_angle(Vector3d(1.,0.,0.), d)
#            self.rotation = self.rotation * r
#
#    def mouse_spin(self, dx, dy, time_elapsed):
#        if (dx != 0.):
#            ax = self.mouse_sensivity * dx * -1.
#            self.mouse_target[0] += ax
#        
#        if (dy != 0.):
#            ay = self.mouse_sensivity * dy * -1.
#            self.mouse_target[1] += ay
