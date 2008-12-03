from OpenGL.GL import *

from objects import Object

from game.state import Player

from physics.shape import Shape
from physics.vector3d import Vector3d

from util.config import Config


class SimpleGun(object):
    def __init__(self, model, ship, level):
        self.model = model
        self.ship = ship
        self.level = level
         
        cfg = Config('game','SimpleGun')
        self.duration = cfg.get('duration')
        self.pos = Vector3d(*cfg.get('pos'))
        self.shoot_period = 1. / cfg.get('shoot_rate')
        self.shoot_velocity_sz = cfg.get('shoot_velocity')
        self.damage = cfg.get('damage')
        
        self.shooting = False
        self.since_last_shoot = 0.0
        
    def tick(self, time_elapsed):
        self.update_shoot(time_elapsed)
    
    def update_shoot(self, time_elapsed):
        if (not self.shooting):
            return
        
        self.since_last_shoot += time_elapsed
        
        if (self.since_last_shoot >= self.shoot_period):
            self.since_last_shoot -= self.shoot_period
            self.single_shoot()
    
    def start_shoot(self):
        if (self.shooting):
            return

        self.shooting = True
        self.single_shoot()
        self.since_last_shoot = 0.0
    
    def end_shoot(self):
        if (not self.shooting):
            return
        
        self.shooting = False
        self.since_last_shoot = 0.0
    
    _info = {
        'destructible'    : False,
        'destroys_player' : False,
        'target'          : False
    }
    
    def single_shoot(self):
        d = self.pos.get_mod()
        ship_rot = self.ship.rotation 
        
        bullet_pos = self.ship.shape.position + (ship_rot * self.pos).scalar(d)
        
        shape = Shape(0.01, bullet_pos)
        
        v_sz = self.shoot_velocity_sz + self.ship.shape.velocity.get_mod()
        shape.velocity = self.ship.ship_dir.normalizing().scalar(v_sz)

        obj = SimpleShoot(self.model, shape,
            SimpleGun._info, self.level, self.duration, self.damage
        )
        
        self.level.add_object(obj)


class SimpleShoot(Object):
    def __init__(self, model, shape, element, lvl, duration, damage):
        Object.__init__(self, model, shape, element)
        
        self.duration = duration
        self.elapsed = 0.0
        self.lvl = lvl
        self.damage = damage
        
    def tick(self, time_elapsed):
        Object.tick(self, time_elapsed)
        
        self.elapsed += time_elapsed
        
        if (self.elapsed >= self.duration):
            self.lvl.remove_object(self)
            
    def collided_with_asteroid(self, ast):        
        l = [('remove', self)]
        
        if (ast.destructible):
            ast.hp -= self.damage
            if (ast.hp <= 0):
                Player.get_instance().object_destroyed(ast)
                l.append(('remove', ast))
        
        return l
        
    collided_with_planet = collided_with_asteroid
