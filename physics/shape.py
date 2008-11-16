from physics.vector3d import Vector3d

class Shape:
	
	mass = 0.0
	velocity = Vector3d(0., 0., 0.)
	aceleration = Vector3d(0., 0., 0.)
	
	# forces
	# vector list
	forces = []
	# temporary force or impulse
	# vector list
	forces_tmp = []
	# resistence force
	# positive real values list 
	forces_res = []
	
	# m : mass
	def __init__(self, m):
		self.mass = m
	
	def calculate_aceleration(self):

		self.aceleration = Vector3d(0.0, 0.0, 0.0)
		total_forces = self.forces + self.forces_tmp
		
		for f in total_forces :
			self.aceleration = self.aceleration + f
			
		# clear temporary forces
		forces_tmp = []
		
		f_res = 0.0
		
		for f in self.forces_res:
			f_res += f
		
		self.aceleration = self.aceleration + self.aceleration.normalizing().scalar(-f_res)
		self.aceleration = self.aceleration.scalar(1/self.mass) 
		
	def calculate_velocity(self):
		# v = v0 + a.DELTA
		# DELTA is update ratio
		self.velocity = self.velocity + self.aceleration