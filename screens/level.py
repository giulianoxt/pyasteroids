import yaml

from OpenGL.GL import *
from OpenGL.GLU import *

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QImage
from PyQt4.QtOpenGL import QGLWidget

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
        self.controller = None
        
        cfg = Config('levels',str(level_number))
        
        level_name = cfg.get('name')    
        self.load_file(level_name)
        
        skybox = cfg.get('skybox')
        self.setup_skybox('resources/'+skybox)
            
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
            
            self.objects.append(_object)
        
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
        self.camera.put_in_position()
        
        self.draw_skybox(self.camera.pos)

        for obj in self.objects:
            obj.draw()
    
    def tick(self, time_elapsed):
        for obj in self.objects:
            obj.tick(time_elapsed)

        self.update_mouse_spin()
        self.camera.tick(time_elapsed)

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

    def draw_skybox(self, pos):
        if (pos is None):
            return
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        
        glTranslated(pos.x,pos.y,pos.z)

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
        elif (k == Qt.Key_A):
            self.ship.move_left()
        elif (k == Qt.Key_D):
            self.ship.move_right()
        elif (k == Qt.Key_Up):
            self.ship.spin('up', True)
        elif (k == Qt.Key_Down):
            self.ship.spin('down', True)
        elif (k == Qt.Key_Left):
            self.ship.spin('left', True)
        elif (k == Qt.Key_Right):
            self.ship.spin('right', True)
        elif (k == Qt.Key_B):
            self.camera.invert()

    def keyReleaseEvent(self, event):
        k = event.key()

        if (k == Qt.Key_Up):
            self.ship.spin('up', False)
        elif (k == Qt.Key_Down):
            self.ship.spin('down', False)
        elif (k == Qt.Key_Left):
            self.ship.spin('left', False)
        elif (k == Qt.Key_Right):
            self.ship.spin('right', False)
        elif (k == Qt.Key_B):
            self.camera.invert()

    def update_mouse_spin(self):
        if (self.controller is None):
            return

        pos = self.controller.cursor().pos()
        x, y = pos.x(), pos.y()

        m_center = self.controller.mouse_center

        self.controller.cursor().setPos(*m_center)

        self.ship.mouse_spin(x-m_center[0], y-m_center[1])
