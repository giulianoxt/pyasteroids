from math import *
from itertools import chain

from physics.vector3d import Vector3d 

_eps = 1e-2

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
		
		self.rotation_center = Vector3d(pos.x, pos.y, pos.z)
		
		self.rotation_radius = None
		self.rot_xy = 0.
		self.rot_z = 0.
		self.rot_vel_xy = 0.
		self.rot_vel_z = 0.
		
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
		
		self.forces_res_tmp = []

	def calculate_rotation(self, delta):
		if (self.rotation_radius is None):
			return
		
		previous_pos = self.position.scalar(1.)
		
		self.rot_xy = self.rot_xy + self.rot_vel_xy*delta
		self.rot_z = self.rot_z + self.rot_vel_z*delta
		self.position.x = self.rotation_center.x + self.rotation_radius*sin(self.rot_z)*cos(self.rot_xy)
		self.position.y = self.rotation_center.y + self.rotation_radius*sin(self.rot_z)*sin(self.rot_xy)	
		self.position.z = self.rotation_center.z + self.rotation_radius*cos(self.rot_z)	
		
		self.fake_vel = (self.position - previous_pos).scalar(1. / delta)
		
	def calculate_aceleration(self):
		self.aceleration = sum(chain(self.forces, self.forces_tmp), Vector3d(0.,0.,0.))
		
		f_res = sum(chain(self.forces_res, self.forces_res_tmp), 0.)
		
		if (f_res >= 1.0):
			f_res = 1.0
		
		# clear temporary forces
		self.forces_tmp = []
		self.forces_res_tmp = []
		
		v = self.velocity.get_mod()
		res_mod = v * f_res
		
		self.aceleration = self.aceleration.scalar(1.0 / self.mass)
		self.aceleration = self.aceleration + self.velocity.normalizing().scalar(-res_mod)
		
		if (self.aceleration.get_mod() <= _eps):
			self.aceleration = Vector3d(0.,0.,0.)
		
	def calculate_velocity(self, delta):
		self.velocity = self.velocity + self.aceleration.scalar(delta)
		
		if (self.velocity.get_mod() <= _eps):
			self.velocity = Vector3d(0.,0.,0.)
		
	def calculate_position(self, delta):
		self.position = self.position + self.velocity.scalar(delta)

	def calculate_angle(self, delta):
		self.angle_x = self.angle_x + self.velocity_angular_x*delta
		self.angle_y = self.angle_y + self.velocity_angular_y*delta
		self.angle_z = self.angle_z + self.velocity_angular_z*delta

	def update(self, delta):
		self.calculate_rotation(delta)
		self.calculate_aceleration()
		self.calculate_velocity(delta)
		self.calculate_position(delta)
		self.calculate_angle(delta)


try:
	import psyco
	psyco.bind(Shape)
except:
	pass
