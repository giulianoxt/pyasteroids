import yaml

from random import uniform
from itertools import chain

from OpenGL.GL import *
from OpenGL.GLU import *

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QImage
from PyQt4.QtOpenGL import QGLWidget

from util.config import Config

from physics.shape import Shape
from model.opengl import GLModel
from physics.vector3d import Vector3d

from objects import Object
from objects.portal import Portal
from objects.planet import Planet
from objects.asteroid import Asteroid
from objects.spaceship import SpaceShip
from objects.gun import SimpleGun, SimpleShoot

from screens.camera import Camera


class Level(object):
    def __init__(self, level_number):
        self.number = level_number
        
        self.camera = None
        self.controller = None
        
        self.objects = set()
        self.asteroids = set()
        self.shoots = set()
        self.planets = set()
        self.portals = set()
        self.ship = None
        
        cfg = Config('levels',str(level_number))
        
        level_name = cfg.get('name')    
        self.load_file(level_name)
        
        skybox = cfg.get('skybox')
        #self.setup_skybox('resources/'+skybox)
    
    def add_object(self, obj):
        if (isinstance(obj, SimpleShoot)):
            self.shoots.add(obj)
        elif (isinstance(obj, Portal)):
            self.portals.add(obj)
        elif (isinstance(obj, Planet)):
            self.planets.add(obj)
        elif (isinstance(obj, Asteroid)):
            self.asteroids.add(obj)
        elif (isinstance(obj, SpaceShip)):
            self.ship = obj
        elif (isinstance(obj, Object)):
            self.objects.add(obj)

    def remove_object(self, obj):
        if (isinstance(obj, SimpleShoot)):
            self.shoots.remove(obj)
        elif (isinstance(obj, Portal)):
            self.portals.remove(obj)
        elif (isinstance(obj, Planet)):
            self.planets.remove(obj)
        elif (isinstance(obj, Asteroid)):
            self.asteroids.remove(obj)
        elif (isinstance(obj, SpaceShip)):
            self.ship = None
        elif (isinstance(obj, Object)):
            self.objects.remove(obj)
    
    def all_objects(self):
        return chain(
            self.shoots, self.portals, self.planets,
            self.asteroids, (self.ship,), self.objects
        )
    
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
        
        self.dimensions = Vector3d(*lvl['scene']['dimensions'])
        
        poss = { }
        
        for object in lvl['scene']['objects']:
            element_name = object['element']
            
            shape = None
            
            model, element = models[element_name]
            
            mass = float(object['mass'])
            
            rvel = object['rotation_velocity']

            movement = object['movement']['type']

            if (movement == 'static'):
                pos = Vector3d(*object['pos'])
                poss[element_name] = pos
                
                shape = Shape(mass, pos)	       	
            elif (movement == 'orbit'):
                shape = Shape(mass, poss[object['movement']['center_planet_name']])
                shape.rotation_radius = object['movement']['radius']
                shape.rot_vel_xy = object['movement']['rot_velocity_xy']
                shape.rot_vel_z = object['movement']['rot_velocity_z']

            shape.velocity_angular_x = rvel[0]
            shape.velocity_angular_y = rvel[1]
            shape.velocity_angular_z = rvel[2]
                       
            type = element['type']
            
            type_class = {
                'planet'       : Planet,
                'asteroid'     : Asteroid,
                'start_portal' : Portal,
                'end_portal'   : Portal,
            }
                                    
            _object = type_class[type](model, shape, element)
            
            self.add_object(_object)
        
        self.make_spaceship(lvl, models)
        self.make_guns(models)

    def make_spaceship(self, lvl, models):
        pos = None
        
        for obj in self.portals:
            if (obj.type == 'start'):
                pos = obj.shape.position
                break
            
        shape = Shape(lvl['ship']['mass'], pos)
        
        model, element = models[lvl['ship']['model']]
        
        self.ship = SpaceShip(model, shape, element)

        self.camera = Camera(self.ship, lvl['ship']['camera-dist'])

        self.add_object(self.ship)

    def make_guns(self, models):
        model = models['SimpleGun'][0]
        self.ship.simple_gun = SimpleGun(model, self.ship, self)

    def draw(self):
        self.camera.put_in_position()
        
        #self.draw_skybox(self.camera.pos)

        for obj in self.all_objects():
            obj.draw()
    
    def tick(self, time_elapsed):
        for obj in tuple(self.all_objects()):
            obj.tick(time_elapsed)

        self.wrap_ship()
        #self.update_mouse_spin(time_elapsed)
        self.camera.tick(time_elapsed)
        #self.update_skybox(time_elapsed)

    def setup_skybox(self, image_path):
        self.skybox_textures = glGenTextures(6)
        sides = ('front','left','back','right','top','bottom')
        
        for (tex_id, side) in zip(self.skybox_textures, sides):  
            glBindTexture(GL_TEXTURE_2D, tex_id)
        
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
            img = QImage(image_path+'-'+side+'.png')
            img = QGLWidget.convertToGLFormat(img)
        
            glTexImage2D(GL_TEXTURE_2D, 0, 3, img.width(), img.height(),
                0, GL_RGBA, GL_UNSIGNED_BYTE, img.bits().asstring(img.numBytes()))
            
            glBindTexture(GL_TEXTURE_2D, 0)
        
        self.sky_angles = [uniform(-180.,180.) for i in xrange(3)]
        self.sky_angles_vel = [uniform(-0.5,0.5) for i in xrange(3)]

    def update_skybox(self, time_elapsed):
        for i in xrange(3):
            self.sky_angles[i] += self.sky_angles_vel[i] * time_elapsed

    def draw_skybox(self, pos):
        if (pos is None):
            return
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        
        glTranslate(pos.x,pos.y,pos.z)
        
        for i in xrange(3):
            l = [0.,0.,0.]; l[i] = 1.
            glRotate(self.sky_angles[i], *l)

        glPushAttrib(GL_ENABLE_BIT)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_BLEND)

        glColor3f(1.,1.,1.)

        # front
        glBindTexture(GL_TEXTURE_2D, self.skybox_textures[0])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(0.5,-0.5,-0.5)
        glTexCoord2f(1, 0); glVertex3f(-0.5, -0.5, -0.5)
        glTexCoord2f(1, 1); glVertex3f( -0.5,  0.5, -0.5)
        glTexCoord2f(0, 1); glVertex3f(  0.5,  0.5, -0.5 )
        glEnd()

        # left
        glBindTexture(GL_TEXTURE_2D, self.skybox_textures[1])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(  0.5, -0.5,  0.5 )
        glTexCoord2f(1, 0); glVertex3f(  0.5, -0.5, -0.5 )
        glTexCoord2f(1, 1); glVertex3f(  0.5,  0.5, -0.5 )
        glTexCoord2f(0, 1); glVertex3f(  0.5,  0.5,  0.5 )
        glEnd()

        # back
        glBindTexture(GL_TEXTURE_2D, self.skybox_textures[2])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f( -0.5, -0.5,  0.5 )
        glTexCoord2f(1, 0); glVertex3f(  0.5, -0.5,  0.5 )
        glTexCoord2f(1, 1); glVertex3f(  0.5,  0.5,  0.5 )
        glTexCoord2f(0, 1); glVertex3f( -0.5,  0.5,  0.5 )
        glEnd()

        # right
        glBindTexture(GL_TEXTURE_2D, self.skybox_textures[3])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f( -0.5, -0.5, -0.5 )
        glTexCoord2f(1, 0); glVertex3f( -0.5, -0.5,  0.5 )
        glTexCoord2f(1, 1); glVertex3f( -0.5,  0.5,  0.5 )
        glTexCoord2f(0, 1); glVertex3f( -0.5,  0.5, -0.5 )
        glEnd()

        # top
        glBindTexture(GL_TEXTURE_2D, self.skybox_textures[4])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex3f( -0.5,  0.5, -0.5 )
        glTexCoord2f(0, 0); glVertex3f( -0.5,  0.5,  0.5 )
        glTexCoord2f(1, 0); glVertex3f(  0.5,  0.5,  0.5 )
        glTexCoord2f(1, 1); glVertex3f(  0.5,  0.5, -0.5 )
        glEnd()

        # bottom
        glBindTexture(GL_TEXTURE_2D, self.skybox_textures[5])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f( -0.5, -0.5, -0.5 )
        glTexCoord2f(0, 1); glVertex3f( -0.5, -0.5,  0.5 )
        glTexCoord2f(1, 1); glVertex3f(  0.5, -0.5,  0.5 )
        glTexCoord2f(1, 0); glVertex3f(  0.5, -0.5, -0.5 )
        glEnd()

        glBindTexture(GL_TEXTURE_2D, 0)

        glPopAttrib();
        glPopMatrix();

    def keyPressEvent(self, event):
        k = event.key()
        
        if (k == Qt.Key_Escape):
            self.controller.pop_screen(self)
        elif (k == Qt.Key_W):
            self.ship.move_forward()
        elif (k == Qt.Key_Up):
            self.ship.spin('up', True)
        elif (k == Qt.Key_Down):
            self.ship.spin('down', True)
        elif (k == Qt.Key_Left):
            self.ship.spin('left', True)
        elif (k == Qt.Key_Right):
            self.ship.spin('right', True)
        #elif (k == Qt.Key_A):
        #    self.ship.strafing('left',True)
        #elif (k == Qt.Key_D):
        #    self.ship.strafing('right',True)
        elif (k == Qt.Key_B):
            if (not event.isAutoRepeat()):
                self.camera.invert()
        elif (k == Qt.Key_Space):
            if (not event.isAutoRepeat()):
                self.ship.simple_gun.start_shoot()
        else:
            event.ignore()

    def keyReleaseEvent(self, event):
        if (event.isAutoRepeat()):
            return
        
        k = event.key()

        if (k == Qt.Key_Up):
            self.ship.spin('up', False)
        elif (k == Qt.Key_Down):
            self.ship.spin('down', False)
        elif (k == Qt.Key_Left):
            self.ship.spin('left', False)
        elif (k == Qt.Key_Right):
            self.ship.spin('right', False)
        #elif (k == Qt.Key_A):
        #    self.ship.strafing('left',False)
        #elif (k == Qt.Key_D):
        #    self.ship.strafing('right',False)
        elif (k == Qt.Key_B):
            if (not event.isAutoRepeat()):
                self.camera.invert()
        elif (k == Qt.Key_Space):
            if (not event.isAutoRepeat()):
                self.ship.simple_gun.end_shoot()
        else:
            event.ignore()

    def mousePressEvent(self, event):
        b = event.button()
        
        if (b == Qt.LeftButton):
            self.ship.simple_gun.start_shoot()
        else:
            event.ignore()
    
    def mouseReleaseEvent(self, event):
        b = event.button()
        
        if (b == Qt.LeftButton):
            self.ship.simple_gun.end_shoot()
        else:
            event.ignore()

    def update_mouse_spin(self, time_elapsed):
        if (self.controller is None):
            return

        pos = self.controller.cursor().pos()
        x, y = pos.x(), pos.y()

        m_center = self.controller.mouse_center

        self.controller.cursor().setPos(*m_center)

        self.ship.mouse_spin(x-m_center[0], y-m_center[1], time_elapsed)

    def wrap_ship(self):
        pos = self.ship.shape.position
        dx, dy, dz = map(lambda x : x / 2., self.dimensions)
        
        if (pos.x > dx):
            pos.x -= dx
        elif (pos.x < -dx):
            pos.x += dx
            
        if (pos.y > dy):
            pos.y -= dy
        elif (pos.y < -dy):
            pos.y += dy            
            
        if (pos.z > dz):
            pos.z -= dz
        elif (pos.z < -dz):
            pos.z += dz
