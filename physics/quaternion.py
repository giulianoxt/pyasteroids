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
        
        return qx * (qy * qz)
    
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
    
    def get_axis_angle(self):
        try:
            x, y, z, w = self.x, self.y, self.z, self.w
        
            s = sqrt(x**2 + y**2 + z**2)
            a = Vector3d(x / s, y / s, z / s)
        
            return (a, degrees(acos(self.w) * 2.))
        except ZeroDivisionError:
            return (v3d(1.,0.,0.), 0.)
    
    def __mul__(self, q):
        self.normalize()
        
        if (isinstance(q, Quaternion)):
            q.normalize()
            
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


if (__name__ == '__main__'):    
    # 90 pra cima (0,1,0)
    rx = Quaternion.from_axis_angle(v3d(1.,0.,0.), 90.)
    print '1', rx * v3d(0.,0.,-1.)

    # 90 pra esquerda (-1,0,0)
    ry = Quaternion.from_axis_angle(v3d(0.,1.,0.), 90.) 
    print '2', ry * v3d(0.,0.,-1.)

    # caso nao translade o sistema de coordenadas, vai ser: (0,1,0)
    v1 = rx * v3d(0.,0.,-1.)
    v2 = ry * v1
    print '3', v2
    
    # caso translade o sistema de coordenadas, vai ser: (-1,0,0) 
    rxy = rx * ry
    print '4', rxy * v3d(0.,0.,-1.)
    
    # caso nao translade o sistema de coordenadas, vai ser: (-1,0,0) 
    v1 = ry * v3d(0.,0.,-1.)
    v2 = rx * v1
    print '5', v2
    
    # caso translade o sistema de coordenadas, vai ser: (0,1,0)
    ryx = ry * rx
    print '6', ryx * v3d(0.,0.,-1.)
