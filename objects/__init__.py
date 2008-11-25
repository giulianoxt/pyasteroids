from OpenGL.GL import *

class Object(object):
    def __init__(self, model, shape, element):
        self.model = model
        self.shape = shape
    
        self.destructible = element['destructible']
        self.hp = element['hp'] if self.destructible else -1
        self.hostile = element['destroys_player']
    
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
