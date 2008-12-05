from objects import Object
from physics.shape import Shape
from objects.gun import SimpleShootInvasor

class EnemyShip(Object):
    def __init__(self, model, shape, element):
        Object.__init__(self, model, shape, element)
        self.level = None
	self.time_interval_shot = 1.0
	self.elapsed = 0.0
	self.gun_pos = None

    def tick(self, time_elapsed):
        Object.tick(self, time_elapsed)
        
        self.elapsed += time_elapsed
        
        if (self.elapsed >= self.time_interval_shot):
	    self.elapsed = 0.
	    _info = {
	    'destructible'    : False,
	    'destroys_player' : False,
	    'target'          : False
	    }
	    vec_dir = (self.level.ship.shape.position - self.shape.position -  self.gun_pos).normalizing().scalar(70.)
	    bullet_pos = self.shape.position + self.gun_pos
	    shape_bull = Shape(0.01, bullet_pos)
	    shape_bull.velocity = vec_dir
	    #
	    #(self, model, shape, element, lvl, duration, damage)
	    obj_sh = SimpleShootInvasor(self.level.models['InvasorSimpleGun'][0], shape_bull, _info, self.level, 20, 5)
	    self.level.add_object(obj_sh)
	    #
	       