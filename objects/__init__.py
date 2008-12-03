from OpenGL.GL import *

class Object(object):
    def __init__(self, model, shape, element):
        self.model = model
        self.shape = shape
    
        self.target = element['target']
        self.destructible = element['destructible']
        self.hostile = element['destroys_player']
        
        if (self.destructible):
            self.hp = element['hp']
            self.score = element['score']
        
        if (self.hostile):
            self.damage = element['damage']
    
    def draw(self):
        glMatrixMode(GL_MODELVIEW)
        
        glPushMatrix()
                
        glTranslate(*self.shape.position)

        glRotatef(self.shape.angle_x, 1., 0., 0.)
        glRotatef(self.shape.angle_y, 0., 1., 0.)
        glRotatef(self.shape.angle_z, 0., 0., 1.)
        
        self.model.draw()
        
        glPopMatrix()
   
    def tick(self, time_elapsed):
        self.shape.update(time_elapsed)

    def _collided(self, obj):       
        obj_class_name = obj.__class__.__name__
        method_name = 'collided_with_' + obj_class_name.lower()
        
        if (hasattr(self, method_name)):
            return getattr(self, method_name)(obj)
        elif (hasattr(self, 'collided')):
            return self.collided(obj)
        else:
            return None
