import yaml

from OpenGL.GL import *

from PyQt4.QtCore import Qt

from util.config import Config
from physics.shape import Shape
from model.opengl import GLModel
from physics.vector3d import Vector3d

from objects.portal import Portal
from objects.planet import Planet
from objects.asteroid import Asteroid
from objects.spaceship import SpaceShip

from screens.camera import Camera


class Level(object):
    def __init__(self, level_number):
        self.number = level_number
        
        self.objects = []
        self.camera = None
        
        level_name = Config('levels','Levels').get(str(level_number))
        
        self.load_file(level_name)
    
    def load_file(self, level_name):
        lvl = yaml.load(open('resources/levels/' + level_name + '.lvl'))

        self.title = lvl['name']
        self.dimensions = lvl['scene']['dimensions']

        models = {}

        for element in lvl['elements']:
            file = open('resources/models/'+element['model']['file'], 'r')
            
            name = element['name']
            subtitle = element['subtitle']
            
            translate = element['model']['translate']
            rotate = element['model']['rotate']
            scale = element['model']['scale']
            
            gl_model = GLModel(file, translate, rotate, scale)
            
            models[name] = (gl_model, element)            
            
            file.close()
        
        id_object = {}
        
        for object in lvl['scene']['objects']:
            element_name = object['element']
            
            shape = None
            
            model, element = models[element_name]
            
            mass = float(object['mass'])
            
            rvel = object['rotation_velocity']

            movement = object['movement']['type']

            if (movement == 'static'):
                pos = Vector3d(*object['pos'])
                shape = Shape(mass, pos)	       	
                shape.velocity_angular_x = rvel[0]
                shape.velocity_angular_y = rvel[1]
                shape.velocity_angular_z = rvel[2]
            elif (movement == 'orbit'):
                pos = Vector3d(*object['movement']['start_position'])
                shape = Shape(mass, pos)
                
                #center_planet_id = object['movement']['center_planet_id']
                #center_planet_shape = id_object[center_planet_id].shape
                       
            type = element['type']
            
            type_class = {
                'planet'       : Planet,
                'asteroid'     : Asteroid,
                'start_portal' : Portal,
                'end_portal'   : Portal,
            }
            
            _object = type_class[type](model, shape, element)
            
            self.objects.append(_object)
            
            if (hasattr(object, 'id')):
                id_object[object['id']] = _object
        
        self.make_spaceship(lvl, models)

    def make_spaceship(self, lvl, models):
        pos = None
        
        for obj in self.objects:
            if (isinstance(obj, Portal) and (obj.type == 'start')):
                pos = obj.shape.position
                break
            
        shape = Shape(lvl['ship']['mass'], pos)
        
        model, element = models[lvl['ship']['model']]
        
        self.ship = SpaceShip(model, shape, element)
        
        self.camera = Camera(self.ship, lvl['ship']['camera-dist'])
        
        self.objects.append(self.ship)

    def draw(self):
        glMatrixMode(GL_MODELVIEW)
        
        self.camera.put_in_position()
        
        for obj in self.objects:
            obj.draw()
    
    def tick(self, time_elapsed):
        for obj in self.objects:
            obj.tick(time_elapsed)

        self.camera.tick(time_elapsed)

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_Escape):
            self.controller.pop_screen(self)
