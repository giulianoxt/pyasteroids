# Version 0.2
# 15/11/2008

from math import *

def atan2(y, x):
	if ( x == 0 ):
		return (pi()/2.0)
	else:
		return atan(y/x)

class Vector3d:
	def __init__(self, x_val, y_val, z_val):
		self.x = x_val
		self.y = y_val
		self.z = z_val
	
	@classmethod
	def x_axis(cls):
		return Vector3d(1., 0., 0.)
	
	@classmethod
	def y_axis(cls):
		return Vector3d(0., 1., 0.)
	
	@classmethod
	def z_axis(cls):
		return Vector3d(0., 0., 1.)
	
	# length of vector
	def get_mod(self):
		return sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
	# addition
	def __add__(self, vec3d):
		return Vector3d(self.x + vec3d.x, self.y + vec3d.y, self.z + vec3d.z)
	
	# subtraction
	def __sub__(self, vec3d):
		return Vector3d(self.x - vec3d.x, self.y - vec3d.y, self.z - vec3d.z)
	
	# dot scalar
	def __mul__(self, vec3d):
		return (self.x*vec3d.x + self.y*vec3d.y + self.z*vec3d.z)
	
	def __iter__(self):
		return iter((self.x, self.y, self.z))
	
	def __str__(self):
		return str((self.x, self.y, self.z))

	def __repr__(self):
		return str(self)
	
	def __getitem__(self, i):
		return (self.x, self.y, self.z)[i]
	
	def __setitem__(self, i, v):
		slots = [self.x, self.y, self.z]
		slots[i] = v
		self.x, self.y, self.z = slots
	
	def __len__(self):
		return 3
	
	# cross product
	def cross_product(self, vec3d):
		x_cp = self.y*vec3d.z - self.z*vec3d.y
		y_cp = self.z*vec3d.x - self.x*vec3d.z
		z_cp = self.x*vec3d.y - self.y*vec3d.x
		return Vector3d(x_cp, y_cp, z_cp)
	
	# returns angle ( radians ) two vectors
	def angle(self, vec3d):
		return acos( (self*vec3d)/(self.get_mod()*vec3d.get_mod()) )
	
	# scalar multiplication
	def scalar(self, k):
		return Vector3d(self.x*k, self.y*k, self.z*k)
	
	# returns a unitary vector
	def normalizing(self):
		try:
			tmp_mod = self.get_mod()
			return Vector3d(self.x/tmp_mod, self.y/tmp_mod, self.z/tmp_mod)
		except ZeroDivisionError:
			return Vector3d(0.,0.,0.)
	
	# angle ( radians ) between the positive x-axis and vector projected onto the xy-plane
	def angle_phi(self):
		return atan2(self.y, self.x)
	
	# angle ( radians ) between the positive z-axis and the vector
	def angle_theta(self):
		return atan2(sqrt(self.x*self.x + self.y*self.y), self.z)
	
	# following the theory about rotations on:
	# http://answers.google.com/answers/threadview/id/361441.html
	def rotated(self, degrees, axis):
		r = radians(degrees)
		a, b, c = axis.normalizing()
		
		q0, q1, q2, q3 = cos(r/2), sin(r/2)*a, sin(r/2)*b, sin(r/2)*c
		
		M = [
			[q0+q1-q2-q3, 2*(q1*q2 - q0*q3), 2*(q1*q3 - q0*q2)],
			[2*(q2*q1 + q0*q3), q0 - q1 + q2 - q3, 2*(q2*q3 - q0*q1)],
			[2*(q3*q1 - q0*q2), 2*(q3*q2 + q0*q1), q0 - q1 - q2 + q3]
		]
		
		x, y, z = self
		
		nx, ny, nz = Vector3d(*[
			M[0][0]*x + M[0][1]*y + M[0][2]*z,
			M[1][0]*x + M[1][1]*y + M[1][2]*z,
			M[2][0]*x + M[2][1]*y + M[2][2]*z,
		])

		return Vector3d(nx,ny,nz)

	def adjust_complex(self):
		self.x = self.x.real
		self.y = self.y.real
		self.z = self.z.real

try:
	import psyco
	psyco.bind(Vector3d)
except:
	pass
