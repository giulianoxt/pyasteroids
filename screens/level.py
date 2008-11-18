import yaml

from OpenGL.GL import *

from util.config import Config
from physics.shape import Shape
from model.opengl import GLModel
from physics.vector3d import Vector3d


class Level(object):
    def __init__(self, level_number):
        self.number = level_number
        self.objects = []
        
        level_name = Config('levels','Levels').get(str(level_number))
        
        self.load_file(level_name)
    
    def load_file(self, level_name):
        lvl = yaml.load(open('resources/levels/' + level_name + '.lvl'))

        models = {}

        for element in lvl['elements']:
            file = open('resources/models/'+element['model']['file'], 'r')
            
            models[element['name']] = GLModel(file)
            
            file.close()
        
        for object in lvl['scene']['objects']:
            model = models[object['element']]
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
