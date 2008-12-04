import yaml

from random import uniform
from itertools import chain, ifilter

from OpenGL.GL import *
from OpenGL.GLU import *

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QImage
from PyQt4.QtOpenGL import QGLWidget

from util.config import Config
from util.opengl import default_perspective

from model.opengl import GLModel

from physics.shape import Shape
from physics.vector3d import Vector3d
from physics.collision import collide

from objects import Object
from objects.portal import Portal
from objects.planet import Planet
from objects.asteroid import Asteroid
from objects.spaceship import SpaceShip
from objects.particles import ParticleSystem
from objects.gun import SimpleGun, SimpleShoot
from objects.missile import SimpleMissile, Missile

from game.state import Player

from screens.camera import Camera

from util.misc import xisinstance


class Level(object):
    instance = None
    
    def __init__(self, level_number):
        Level.instance = self
        
        self.number = level_number
        
        self.camera = None
        self.controller = None
        
        self.objects = set()
        self.asteroids = set()
        self.shots = set()
        self.planets = set()
        self.portals = set()
        self.particles = set()
        self.missiles = set()
        self.ship = None
        
        cfg = Config('levels',str(level_number))
        
        level_name = cfg.get('name')    
        self.load_file(level_name)
        
        skybox = cfg.get('skybox')
        self.setup_skybox('resources/'+skybox)
        
        self.first = True
    
    def with_controller(self):
        pass
    
    def add_object(self, obj):
        if (xisinstance(obj, SimpleShoot)):
            self.shots.add(obj)
        elif (xisinstance(obj, ParticleSystem)):
            self.particles.add(obj)
        elif (xisinstance(obj, Missile)):
            self.missiles.add(obj)
        elif (xisinstance(obj, Portal)):
            self.portals.add(obj)
        elif (xisinstance(obj, Planet)):
            self.planets.add(obj)
        elif (xisinstance(obj, Asteroid)):
            self.asteroids.add(obj)
        elif (xisinstance(obj, SpaceShip)):
            self.ship = obj
        elif (xisinstance(obj, Object)):
            self.objects.add(obj)
        else:
            raise NotImplementedError()

    def remove_object(self, obj):
        if (xisinstance(obj, SimpleShoot)):
            self.shots.remove(obj)
        elif (xisinstance(obj, ParticleSystem)):
            self.particles.remove(obj)
        elif (xisinstance(obj, Missile)):
            self.missiles.remove(obj)
        elif (xisinstance(obj, Portal)):
            self.portals.remove(obj)
        elif (xisinstance(obj, Planet)):
            self.planets.remove(obj)
        elif (xisinstance(obj, Asteroid)):
            self.asteroids.remove(obj)
        elif (xisinstance(obj, SpaceShip)):
            self.ship = None
        elif (xisinstance(obj, Object)):
            self.objects.remove(obj)
        else:
            raise NotImplementedError
    
    def all_objects(self):
        return chain(
            self.shots, self.portals, self.planets, self.missiles,
            self.asteroids, (self.ship,), self.objects, self.particles
        )
    
    def load_file(self, level_name):
        lvl = yaml.load(open('resources/levels/' + level_name + '.lvl'))

        self.title = lvl['name']
        self.dimensions = lvl['scene']['dimensions']

        self.time = float(lvl['time']) * 60

        models = {}

        for element in lvl['elements']:
            file = open('resources/models/'+element['model']['file'], 'r')
            
            name = element['name']
            subtitle = element['subtitle']
            
            translate = element['model'].get('translate', (0.,0.,0.))
            rotate = element['model'].get('rotate', (0.,0.,0.))
            scale = element['model'].get('scale', 1.)
            rc = element['model'].get('radius_correction', 0.)
            
            gl_model = GLModel(file, translate, rotate, scale, rc)
            
            models[name] = (gl_model, element)            
            
            file.close()
        
        self.dimensions = Vector3d(*lvl['scene']['dimensions'])
        
        type_class = {
            'planet'       : Planet,
            'asteroid'     : Asteroid,
            'start_portal' : Portal,
            'end_portal'   : Portal,
        }
        
        id_table = { }
        
        obj_set = set()
        
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
            elif (movement == 'orbit'):
                center_id = object['movement']['center_planet_id']
                center_obj = id_table[center_id]
                center_pos = Vector3d(*center_obj.shape.position)
                
                shape = Shape(mass, center_pos)
                shape.rotation_radius = object['movement']['radius']
                shape.rot_vel_xy = object['movement']['rot_velocity_xy']
                shape.rot_vel_z = object['movement']['rot_velocity_z']
                shape.rot_xy = object['movement']['rot_xy']
                shape.rot_z = object['movement']['rot_z']

            shape.velocity_angular_x = rvel[0]
            shape.velocity_angular_y = rvel[1]
            shape.velocity_angular_z = rvel[2]
                       
            type = element['type']
                                    
            _object = type_class[type](model, shape, element)
            
            obj_set.add(_object)
            
            if ('id' in object):
                id_table[object['id']] = _object
        
        for obj in obj_set:
            self.add_object(obj)
        
        Player.get_instance().beginning_level(self)
        
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
        
        self.ship = SpaceShip(model, shape, element, self)

        self.camera = Camera(self.ship, lvl['ship']['camera-dist'])

        self.add_object(self.ship)

    def make_guns(self, models):
        model = models['SimpleGun'][0]
        self.ship.simple_gun = SimpleGun(model, self.ship, self)
        
        model = models['SimpleMissile'][0]
        self.ship.simple_missile = SimpleMissile(model, self.ship, self)

    def draw(self):
        default_perspective(self.controller.width(), self.controller.height())
        
        self.camera.put_in_position()
        
        self.draw_skybox(self.camera.pos)

        for obj in self.all_objects():
            obj.draw()
    
    def tick(self, time_elapsed):
        for obj in tuple(self.all_objects()):
            obj.tick(time_elapsed)

        self.wrap_ship()
        
        self.update_mouse_spin(time_elapsed)
        
        self.camera.tick(time_elapsed)
        
        self.update_skybox(time_elapsed)
        
        self.check_collisions(time_elapsed)
        
        self.time -= time_elapsed
    
    def check_collisions(self, time_elapsed):
        self.new, self.erase = set(), set()
        
        self.check_groups((self.ship,), self.planets, self.asteroids)
        self.check_groups(self.shots, self.planets, self.asteroids)
        self.check_groups(self.missiles, self.planets, self.asteroids)

        for obj in self.erase:
            self.remove_object(obj)

        for obj in self.new:
            self.add_object(obj)
    
    def check_groups(self, g_src, *g_dest):
        for obj1 in g_src:
            for obj2 in chain(*g_dest):
                if (collide(obj1,obj2)):
                    s1 = obj1._collided(obj2)
                    self.handle_collision_status(s1)
                    
                    s2 = obj2._collided(obj1)
                    self.handle_collision_status(s2)
                    
    def handle_collision_status(self, st):
        if (st is None):
            return
        
        if (type(st[0]) == type('')):
            st = (st,)
        
        for (op,obj) in st:
            if (op == 'add'):
                self.new.add(obj)
            elif (op == 'remove'):
                self.erase.add(obj)
            else:
                raise NotImplementedError()

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
        if (event.isAutoRepeat()):
            return
        
        k = event.key()
        
        if (k == Qt.Key_Escape):
            self.controller.pop_screen(self)
        elif (k == Qt.Key_Up):
            self.ship.spin('up', True)
        elif (k == Qt.Key_Down):
            self.ship.spin('down', True)
        elif (k == Qt.Key_Left):
            self.ship.spin('left', True)
        elif (k == Qt.Key_Right):
            self.ship.spin('right', True)
        elif (k == Qt.Key_W):
            self.ship.strafing('forward', True)
        elif (k == Qt.Key_A):
            self.ship.strafing('left',True)
        elif (k == Qt.Key_D):
            self.ship.strafing('right',True)
        elif (k == Qt.Key_S):
            self.ship.strafing('breake',True)
        elif (k == Qt.Key_B):
            self.camera.invert()
        elif (k == Qt.Key_Space):
            self.ship.simple_gun.start_shoot()
        elif (k == Qt.Key_P):
            self.controller.push_screen('PauseMessage')
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
        elif (k == Qt.Key_W):
            self.ship.strafing('forward', False)
        elif (k == Qt.Key_A):
            self.ship.strafing('left',False)
        elif (k == Qt.Key_D):
            self.ship.strafing('right',False)
        elif (k == Qt.Key_S):
            self.ship.strafing('breake',False)
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
#        elif (b == Qt.RightButton):
#            self.ship.simple_missile.single_shoot()

    def mouseReleaseEvent(self, event):
        b = event.button()
        
        if (b == Qt.LeftButton):
            self.ship.simple_gun.end_shoot()
        else:
            event.ignore()

    def update_mouse_spin(self, time_elapsed):
        if (self.controller is None):
            return

        if (self.first):
            m_center = self.controller.mouse_center
            self.controller.cursor().setPos(*m_center)
            self.first = False

        pos = self.controller.cursor().pos()
        x, y = pos.x(), pos.y()

        m_center = self.controller.mouse_center

        self.controller.cursor().setPos(*m_center)

        self.ship.mouse_spin(x-m_center[0], y-m_center[1], time_elapsed)

    def wrap_ship(self):
        pos = self.ship.shape.position
        dx, dy, dz = map(lambda x : x / 2., self.dimensions)
        
        if (pos.x > dx):
            pos.x -= dx*2
        elif (pos.x < -dx):
            pos.x += dx*2
            
        if (pos.y > dy):
            pos.y -= dy*2
        elif (pos.y < -dy):
            pos.y += dy*2          
            
        if (pos.z > dz):
            pos.z -= dz*2
        elif (pos.z < -dz):
            pos.z += dz*2
