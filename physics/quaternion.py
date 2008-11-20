from math import *

from physics.vector3d import Vector3d

v3d = Vector3d


class Quaternion(object):
    def __init__(self, x = None, y = None, z = None, w = None):
        self.x = x
        self.y = y
        self.z = z
        self.w = w
    
    @classmethod
    def from_axis_angle(cls, axis, angle):
        q = Quaternion()
        
        axis = axis.normalizing()
        
        a = radians(angle) / 2.
        s = sin(a)
        
        q.w = cos(a)
        
        q.x = axis.x * s
        q.y = axis.y * s
        q.z = axis.z * s
        
        return q
    
    @classmethod
    def from_axis_rotations(cls, rx, ry, rz):
        qx = Quaternion.from_axis_angle(v3d(1.,0.,0.),rx)
        qy = Quaternion.from_axis_angle(v3d(0.,1.,0.),ry)
        qz = Quaternion.from_axis_angle(v3d(0.,0.,1.),rz)
        
        return (qx * qy * qz)
    
    def normalize(self):
        mag = self.w**2 + self.x**2 + self.y**2 + self.z**2
        if (fabs(mag - 1.) > 1e-5):
            mag = sqrt(mag)
            self.w /= mag
            self.x /= mag
            self.y /= mag
            self.z /= mag
    
    def conjugate(self):
        return Quaternion(-self.x, -self.y, -self.z, self.w)
    
    def __mul__(self, q):
        if (isinstance(q, Quaternion)):
            r = Quaternion()
        
            r.w = self.w*q.w - self.x*q.x - self.y*q.y - self.z*q.z
            r.x = self.w*q.x + self.x*q.w + self.y*q.z - self.z*q.y
            r.y = self.w*q.y + self.y*q.w + self.z*q.x - self.x*q.z
            r.z = self.w*q.z + self.z*q.w + self.x*q.y - self.y*q.x

            return r
        elif (isinstance(q, Vector3d)):
            v = q.normalizing()
            
            vec_quat = Quaternion()
            res_quat = Quaternion()
            
            vec_quat.x = v.x
            vec_quat.y = v.y
            vec_quat.z = v.z
            vec_quat.w = 0.
            
            res_quat = vec_quat * self.conjugate()
            res_quat = self * res_quat
            
            return Vector3d(res_quat.x, res_quat.y, res_quat.z)
