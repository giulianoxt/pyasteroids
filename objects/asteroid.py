from objects import Object

class Asteroid(Object):
    def __init__(self, model, shape, element):
        Object.__init__(self, model, shape, element)
	self.asteroid_type = None
	self.shot_tick_interval = 100
	self.shot_tick_counter = 0
	self.shot = False

    def tick(self, time_elapsed):
        Object.tick(self, time_elapsed)
	if (self.asteroid_type == 'artificial'):
		self.shot_tick_counter = (self.shot_tick_counter + 1) % self.shot_tick_interval
		if (self.shot_tick_counter == 0):
			self.shot = True