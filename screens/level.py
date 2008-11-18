import yaml

from physics.shape import Shape
from physics.vector3d import Vector3d
from model.opengl import GLModel

from OpenGL.GL import *


class Level(object):
    def __init__(self, levelName):
        lvl = yaml.load(open('resources/levels/' + levelName + '.lvl'))
        
        self.models = {}

        for element in lvl['elements']:
            file = open('resources/models/'+element['model']['file'], 'r')
            
            self.models[element['name']] = GLModel(file)
            
            file.close()
        
        self.objects = []
        
        for object in lvl['scene']['objects']:
            model = self.models[object['element']]
            mass = float(object['mass'])
            
            rvel = object['rotation_velocity']

            if (not 'pos' in object):
                continue

            pos = Vector3d(*object['pos'])
            
            shape = Shape(model, mass, pos)
            
            shape.velocity_angular_x = rvel[0]
            shape.velocity_angular_y = rvel[1]
            shape.velocity_angular_z = rvel[2]
            
            self.objects.append(shape)

    def draw(self):
        glMatrixMode(GL_MODELVIEW)
        
        for shape in self.objects:
            glPushMatrix()

            glTranslate(shape.position.x, shape.position.y, shape.position.z)
            
            glRotatef(shape.angle_x, 1., 0., 0.)
            glRotatef(shape.angle_y, 0., 1., 0.)
            glRotatef(shape.angle_z, 0., 0., 1.)
            
            shape.model.draw()
            
            glPopMatrix()            
    
    def tick(self, time_elapsed):
        for shape in self.objects:
            shape.update(time_elapsed)
