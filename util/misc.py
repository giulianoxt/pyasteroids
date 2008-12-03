from math import *
from random import uniform

from physics.vector3d import Vector3d


xisinstance = lambda x, cls : x.__class__ == cls

def format_time(seconds):
    m = int(seconds / 60.)
    s = int(seconds % 60.)
    
    return '%02d:%02d' % (m,s)

def apply_irange(v, v_irange):
    if (len(v_irange) == 1):
        v_irange = v_irange*3
    
    v = Vector3d(*v) 
    for i in xrange(len(v)):
        v[i] += uniform(*v_irange[i])

    return v

def dot_distance(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    dz = p1[2] - p2[2]
    
    return sqrt(dx**2 + dy**2 + dz**2)
