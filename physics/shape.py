from physics.vector3d import Vector3d

#  Apenas os módulos das forças de resistência precisam ser informados, pois esses valors serão somandos
#  e valor dessa soma será multiplicado pelo vetor unitário, mas com sentido inverso, resultante da soma vetorial dos outros dois tipos de vetores 

class Shape:
	
	# m : mass
	def __init__(self, m = 0.0, pos = Vector3d(0.,0.,0.)):
		self.mass = m
		self.position = pos
		self.velocity = Vector3d(0., 0., 0.)
		self.aceleration = Vector3d(0., 0., 0.)
	
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
		
		self.aceleration = self.aceleration + self.aceleration.normalizing().scalar(-f_res)
		self.aceleration = self.aceleration.scalar(1/self.mass) 
		
	def calculate_velocity(self, delta):
		# v = v0 + a.DELTA
		# DELTA is update ratio
		self.velocity = self.velocity + self.aceleration.scalar(delta)
		
	def calculate_position(self, delta):
		self.position = self.position + self.velocity.scalar(delta)
