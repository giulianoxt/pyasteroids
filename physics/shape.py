from physics.vector3d import Vector3d 


class Shape:
	def __init__(self, mass = 0.0, pos = Vector3d(0.,0.,0.)):
		self.mass = mass
		self.position = pos
		self.velocity = Vector3d(0., 0., 0.)
		self.aceleration = Vector3d(0., 0., 0.)
		# angular velocity ( degree/sec )
		self.velocity_angular_x = 0.0
		self.velocity_angular_y = 0.0
		self.velocity_angular_z = 0.0
		# angles ( degree )
		self.angle_x = 0.0 
		self.angle_y = 0.0
		self.angle_z = 0.0
		# forces
		# vector list
		self.forces = []
		# temporary force or impulse
		# vector list
		self.forces_tmp = []
		# resistence force
		# positive real values list 
		self.forces_res = []
	
	def calculate_aceleration(self):

		self.aceleration = Vector3d(0.0, 0.0, 0.0)
		total_forces = self.forces + self.forces_tmp
		
		for f in total_forces :
			self.aceleration = self.aceleration + f
			
		# clear temporary forces
		self.forces_tmp = []
		
		f_res = 0.0
		
		for f in self.forces_res:
			f_res += f
			
		if (f_res > self.aceleration.get_mod()):
			self.aceleration.x = 0.
			self.aceleration.y = 0.
			self.aceleration.z = 0.
		else:
			self.aceleration = self.aceleration + self.aceleration.normalizing().scalar(-f_res)
			self.aceleration = self.aceleration.scalar(1/self.mass) 
		
	def calculate_velocity(self, delta):
		# v = v0 + a.DELTA
		# DELTA is update ratio
		self.velocity = self.velocity + self.aceleration.scalar(delta)
		
	def calculate_position(self, delta):
		self.position = self.position + self.velocity.scalar(delta)

	def calculate_angle(self, delta):
		self.angle_x = self.angle_x + self.velocity_angular_x*delta
		self.angle_y = self.angle_y + self.velocity_angular_y*delta
		self.angle_z = self.angle_z + self.velocity_angular_z*delta

	def update(self, delta):
		self.calculate_velocity(delta)
		self.calculate_position(delta)
		self.calculate_angle(delta)


class OrbitShape(Shape):
	pass
