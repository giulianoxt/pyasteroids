from math import *

from OpenGL.GL import *

from game.state import Player

from objects import Object

from util import sign
from util.config import Config

from physics.vector3d import Vector3d
from physics.quaternion import Quaternion


class SpaceShip(Object):
    def __init__(self, model, shape, element, level):
        Object.__init__(self, model, shape, element)
        
        cfg = Config('physics','Ship')
        
        self.move_force_sz = cfg.get('move_force')
        self.spin_velocity = cfg.get('spin_velocity')
        self.strafe_force = cfg.get('strafe_force')
        self.shape.forces_res.append(cfg.get('vacuum_resistance'))
        self.breake_rate = cfg.get('breake_rate')
        
        self.mouse_sensivity = Config('game','Mouse').get('sensivity')
        
        self.level = level
        
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
        
        self.strafe = {
            'forward': False,
            'left'  : False,
            'right' : False,
            'breake' : False
        }
        
        self.strafe_vectors = {
            'forward':Vector3d(0.,0.,-0.7),
            'left'  : Vector3d(-0.9,0.,0.),
            'right' : Vector3d(0.9,0.,0.),
            'breake' : Vector3d(0.,0.,1.)
        }
        
        self.angles = [0.,0.]
        self.mouse_target = [0.,0.]
        
        self.collision_set = set()
        self.keep_colliding = set()

    def draw(self):        
        glMatrixMode(GL_MODELVIEW)
        
        glPushMatrix()
                
        glTranslate(*self.shape.position)

        axis, angle = self.rotation.get_axis_angle()
        
        ax, ay, az = axis

        glRotatef(angle, ax, ay, az)
               
        self.model.draw()
        
        glPopMatrix()

        self.rotation.normalize()

    def tick(self, time_elapsed):       
        Object.tick(self, time_elapsed)
                
        self.update_mouse_track(time_elapsed)
        self.update_spinning(time_elapsed)
        self.update_strafe(time_elapsed)
        
        self.simple_gun.tick(time_elapsed)
        self.simple_missile.tick(time_elapsed)
        
        self.collision_set = self.keep_colliding
        self.keep_colliding = set()
        
    def update_spinning(self, time_elapsed):
        for dir in self.spinning:
            if (self.spinning[dir]):
                axis, sign = self.vectors[dir]
                angle = self.spin_velocity * time_elapsed * sign
                
                r = Quaternion.from_axis_angle(axis, angle)
                
                self.rotation = self.rotation * r

        self.ship_dir = self.rotation * Vector3d(0.,0.,-1.)
        self.up_dir = self.rotation * Vector3d(0.,1.,0.)

    def move_forward(self):
        force = self.ship_dir.normalizing().scalar(self.move_force_sz)
        
        self.shape.forces_tmp.append(force)
    
    def update_strafe(self, time_elapsed):
        for dir in self.strafe:
            if (self.strafe[dir]):
                if (dir == 'breake'):
                    self.shape.forces_res_tmp.append(self.breake_rate)
                else:
                    sz = self.strafe_vectors[dir].get_mod()
                    
                    v = (self.rotation * self.strafe_vectors[dir])
                    self.shape.forces_tmp.append(v.scalar(self.strafe_force*sz))
    
    def spin(self, dir, b):
        self.spinning[dir] = b

    def strafing(self, dir, b):
        self.strafe[dir] = b

    def update_mouse_track(self, time_elapsed):
        eps = 0.1
        ax, ay = self.angles
        tx, ty = self.mouse_target
        
        if (fabs(ax - tx) <= eps):
            self.angles[0] = 0.0
            self.mouse_target[0] = 0.0
        else:
            before = sign(tx - ax)
            d = self.spin_velocity * time_elapsed * sign(tx - ax)
            self.angles[0] += d
            after = sign(tx - self.angles[0])
            
            if (before != after):
                self.angles[0] = 0.0
                self.mouse_target[0] = 0.0
            
            r = Quaternion.from_axis_angle(Vector3d(0.,1.,0.), d)
            self.rotation = self.rotation * r
            
        if (fabs(ay - ty) <= eps):
            self.angles[1] = 0.0
            self.mouse_target[1] = 0.0
        else:
            before = sign(ty - ay)
            d = self.spin_velocity * time_elapsed * sign(ty - ay)
            self.angles[1] += d
            after = sign(ty - self.angles[1])
            
            if (before != after):
                self.angles[1] = 0.0
                self.mouse_target[1] = 0.0
            
            r = Quaternion.from_axis_angle(Vector3d(1.,0.,0.), d)
            self.rotation = self.rotation * r

    def mouse_spin(self, dx, dy, time_elapsed):
        if (dx != 0.):
            ax = self.mouse_sensivity * dx * -1.
            self.mouse_target[0] += ax
        
        if (dy != 0.):
            ay = self.mouse_sensivity * dy * -1.
            self.mouse_target[1] += ay

    def collided(self, obj):
        self.keep_colliding.add(obj)
        
        if (obj in self.collision_set):
            return
        
        if (obj.hostile):
            Player.get_instance().got_hit(obj)

        self.level.controller.push_screen('FadeMessage', 'Ship_Hit')
