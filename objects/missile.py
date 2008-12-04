from random import uniform
from itertools import chain

from OpenGL.GL import *

from objects import Object

from game.state import Player

from physics.shape import Shape
from physics.vector3d import Vector3d

from util.config import Config
from util.misc import dot_distance, xisinstance


class SimpleMissile(object):
    def __init__(self, model, ship, level):
        self.model = model
        self.ship = ship
        self.level = level
         
        cfg = Config('game','SimpleMissile')
        self.pos = Vector3d(*cfg.get('pos'))
        self.initial_velocity = cfg.get('initial_velocity')
        self.attraction_vel = cfg.get('attraction_velocity')
        self.damage = cfg.get('damage')
        self.num_rockets = cfg.get('num_rockets')
        
    def tick(self, time_elapsed):
        pass

    _info = {
        'destructible'    : False,
        'destroys_player' : False,
        'target'          : False
    }
    
    def single_shoot(self):
        if (self.num_rockets > 0):
            self.num_rockets -= 1
        else:
            return
        
        d = self.pos.get_mod()
        ship_rot = self.ship.rotation 
        
        ship_pos = self.ship.shape.position
        
        bullet_pos = ship_pos + (ship_rot * self.pos).scalar(d)
        
        shape = Shape(0.01, bullet_pos)
        
        v_sz = self.ship.shape.velocity.get_mod() + self.initial_velocity
        shape.velocity = self.ship.ship_dir.normalizing().scalar(v_sz)

        shape.velocity_angular_x = uniform(-280.,280.)
        shape.velocity_angular_y = uniform(-280.,280.)
        shape.velocity_angular_z = uniform(-280.,280.)

        target_obj = None
        min_dist = 1073741824
        
        for obj in chain(self.level.planets, self.level.asteroids):
            if (not obj.target):
                continue
            
            pos = obj.shape.position
            d = dot_distance(ship_pos, pos)
            if (d < min_dist):
                min_dist = d
                target_obj = obj

        if (target_obj is None):
            self.num_rockets += 1
            return

        obj = Missile(self.model, shape,
            SimpleMissile._info, self.level, self.damage,
            target_obj, self.attraction_vel
        )
        
        self.level.add_object(obj)
        
        return obj


class Missile(Object):
    def __init__(self, model, shape, element, lvl, damage, target_obj, attract_v):
        Object.__init__(self, model, shape, element)
        
        self.lvl = lvl
        self.damage = damage
        self.target = target_obj
        
        self.velocity = attract_v
        
        self.dir = Vector3d(0.,0.,0.)
        
    def tick(self, time_elapsed):
        if (hasattr(self.target, 'destroyed') and self.target.destroyed):
            self.lvl.remove_object(self)
            return
        
        self.dir = (self.target.shape.position - self.shape.position).normalizing()
        
        v = self.dir.scalar(self.velocity)
        
        self.shape.velocity = v
        
        Object.tick(self, time_elapsed)

    def collided_with_asteroid(self, ast):
        l = [('remove', self)]
        
        if (ast.destructible):
            ast.hp -= self.damage
            if (ast.hp <= 0):
                Player.get_instance().object_destroyed(ast)
                l.append(('remove', ast))
            
            self.lvl.controller.push_screen('MovingMessage', 'Show_Missile_Hit')
        else:
            self.lvl.controller.push_screen('MovingMessage', 'Show_Missile_Miss')
        
        return l

    collided_with_planet = collided_with_asteroid
