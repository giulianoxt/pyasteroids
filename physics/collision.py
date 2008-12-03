from math import sqrt

def collide(obj_a, obj_b):
    pos_a = obj_a.shape.position
    radius_a = obj_a.model.radius
    
    pos_b = obj_b.shape.position
    radius_b = obj_b.model.radius
    
    dx = pos_a.x - pos_b.x
    dy = pos_a.y - pos_b.y
    dz = pos_a.z - pos_b.z
    
    d = sqrt(dx**2 + dy**2 + dz**2)
    
    return (d < radius_a + radius_b)
