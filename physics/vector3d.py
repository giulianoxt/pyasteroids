# Version 0.2
# 15/11/2008

from cmath import *

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
		tmp_mod = self.get_mod()
		return Vector3d(self.x/tmp_mod, self.y/tmp_mod, self.z/tmp_mod)
	
	# angle ( radians ) between the positive x-axis and vector projected onto the xy-plane
	def angle_phi(self):
		return atan2(self.y, self.x)
	
	# angle ( radians ) between the positive z-axis and the vector
	def angle_theta(self):
		return atan2(sqrt(self.x*self.x + self.y*self.y), self.z)
