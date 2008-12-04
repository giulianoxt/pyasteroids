from itertools import chain
from math import atan2, degrees

from OpenGL.GL import *
from OpenGL.GLU import *

from PyQt4.QtCore import Qt, QPoint, QRect
from PyQt4.QtGui import QImage,  QColor, QFont

from game.state import Player

from util.misc import format_time
from util.config import Config, ConfigManager, FontManager

from util.opengl import default_perspective
from util.opengl import ortho_projection, custom_ortho_projection


class Interface(object):
    def __init__(self, level_number, level):
        self.level_number = level_number
        
        self.info = {}
        self.fields = set()
        
        self.level = level
        self.player_state = Player.get_instance()
                
        cfg = Config('interface', 'Settings')
        font_name = cfg.get('field_font')
        font_size = cfg.get('field_font_sz')
        self.field_font = FontManager.getFont(font_name)
        self.field_font.setPointSize(font_size)
        self.field_color = QColor.fromRgb(*cfg.get('field_color'))
        
        for f_name in ConfigManager.getOptions('interface', 'Fields'):
            s = ConfigManager.getVal('interface', 'Fields', f_name)
            s = map(str.strip, s.split('||'))
            
            img = QImage('resources/images/'+s[0])
            img_pos = QPoint(*eval(s[1]))
            info_rect = QRect(*eval(s[2]))
            scale = float(s[3])
            
            if (len(s) >= 5):
                font = QFont(self.field_font)
                font.setPointSize(int(s[4]))
            else:
                font = self.field_font
            
            img_w, img_h = img.width(), img.height()
            img_rect = QRect(
                img_pos.x(), img_pos.y(),
                int(img_w*scale), int(img_h*scale)
            )
            
            self.info[f_name] = ''
            
            self.fields.add(Field(f_name, img, img_rect, info_rect, font))
        
        self.radar = Radar.from_config('E-Radar', self)
        self.missile = GuidedMissile.from_config('GuidedMissile', self)

    def with_controller(self):
        self.controller.set_hook('SMSTextMessage', 'TutorialIntro')
        self.controller.push_screen('MovingMessage', 'Show_Level_Name', self.level.title)

    def tick(self, time_elapsed):
        ps = self.player_state
        ship_shape = self.level.ship.shape
        
        self.controller.tick_parent(self, time_elapsed)
        
        self.info['alt'] = str(int(ship_shape.position.y))
        
        self.info['speed'] = str(int(ship_shape.velocity.get_mod()))
        
        self.info['time'] = format_time(self.level.time)
        
        hp = int((ps.hp * 100.) / ps.max_hp)
        self.info['life'] = '%d%% [%d]' % (hp, ps.lifes)
        
        self.info['score'] = str(ps.score)
        
        self.info['targets'] = '%d / %d' % (ps.targets, ps.initial_targets)
        
        self.info['fps'] = 'fps: ' + str(int(self.controller.show_fps))
        
        self.info['e-rockets'] = str(self.level.ship.simple_missile.num_rockets)
    
    def draw(self):        
        self.controller.draw_parent(self)
        
        ortho_projection(
            self.controller.width(), self.controller.height()
        )
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        painter = self.qpainter
        
        for field in self.fields:
            field.draw(painter, self.field_color, self.info[field.name])
        
        self.missile.draw(painter)
        self.radar.draw(painter)
    
    def keyPressEvent(self, event):
        if (event.isAutoRepeat()):
            return True
        
        k = event.key()
        
        if (k == Qt.Key_R):
            obj = self.level.ship.simple_missile.single_shoot()
            self.missile.lock(obj)
            return
            
        return True

    def mousePressEvent(self, event):
        b = event.button()
        
        if (b == Qt.RightButton):
            obj = self.level.ship.simple_missile.single_shoot()
            self.missile.lock(obj)
            return
        
        return True


class Field(object):
    flags = Qt.AlignVCenter | Qt.AlignHCenter
    
    def __init__(self, name, img, img_rect, info_rect, font):
        self.name = name
        self.img = img
        self.img_rect = img_rect
        self.info_rect = info_rect
        self.font = font
        
    def draw(self, painter, color, info):
        painter.drawImage(self.img_rect, self.img)
        
        painter.setFont(self.font)
        painter.setPen(color)
        painter.drawText(self.info_rect, Field.flags, info)


class FrameView(object):
    @classmethod
    def from_config(cls, section, interface):     
        cfg = Config('interface', section)
         
        img_path = cfg.get('image_path')
        img_pos = cfg.get('image_pos')
        img_scale = cfg.get('image_scale')
        
        img = QImage('resources/images/'+ img_path)
        img_w, img_h = img.width(), img.height()
        img_rect = QRect(
            img_pos[0], img_pos[1],
            int(img_w*img_scale), int(img_h*img_scale)
        )
        
        view_rect = QRect(*cfg.get('view_rect'))
        
        return cls(img, img_rect, view_rect, interface)
    
    def __init__(self, image, image_rect, view_rect, interface):
        self.image = image
        self.image_rect = image_rect
        
        self.view_x = int(view_rect.topLeft().x())
        self.view_y = int(view_rect.topLeft().y())
        self.view_w = int(view_rect.width())
        self.view_h = int(view_rect.height()) 
        self.view_w2 = int(self.view_w / 2.)
        self.view_h2 = int(self.view_h / 2.)
        
        self.interface = interface
        self.level = interface.level
        
    def draw(self, painter):
        c = self.interface.controller
        w, h = c.width(), c.height()
        ortho_projection(w,h)
        
        painter.drawImage(self.image_rect, self.image)
        
        self.setup_projection()


class GuidedMissile(FrameView):
    def __init__(self, *args, **kwargs):
        FrameView.__init__(self, *args, **kwargs)
        
        self.lock_obj = None
        
        self.camera_dist = Config('interface', 'GuidedMissile').get('camera_dist')
        
        self.has_skybox = Config('game', 'OpenGL').get('skybox')
    
    def lock(self, obj):
        self.lock_obj = obj
    
    def unlock(self):
        self.lock_obj = None
    
    def draw(self, painter):
        FrameView.draw(self, painter)
        
        if (self.lock_obj is None):
            return
        
        if (not self.lock_obj in self.level.missiles):
            self.unlock()
            return
        
        glEnable(GL_TEXTURE_2D)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        
        self.setup_camera()
        
        if (self.has_skybox):
            self.level.draw_skybox(self.camera_pos)
        
        for obj in self.level.all_objects():
            obj.draw()
            
        glPopMatrix()
    
    def setup_projection(self):
        default_perspective(
            self.view_w, self.view_h,
            self.view_x, self.view_y
        )

    def setup_camera(self):
        tg_dir = self.lock_obj.dir
        tg_pos = self.lock_obj.shape.position
        
        e = tg_pos + tg_dir.scalar(-self.camera_dist)
        c = self.lock_obj.target.shape.position
        
        gluLookAt(e.x, e.y, e.z, c.x, c.y, c.z, 0., 1., 0.)

        self.camera_pos = e


class Radar(FrameView):
    def __init__(self, *args, **kwargs):
        FrameView.__init__(self, *args, **kwargs)
        
        self.level_dimension_x = int(self.level.dimensions[0] / 2.)
        self.level_dimension_z = int(self.level.dimensions[2] / 2.)

        range = Config('interface','E-Radar').get('radar_range')

        self.radar_dimension_x = int(self.view_w / range)
        self.radar_dimension_y = int(self.view_h / range)
        
        self.ratio_x = float(self.radar_dimension_x) / self.level_dimension_x
        self.ratio_z = float(self.radar_dimension_y) / self.level_dimension_z
        self.ratio_z *= -1.
    
    def draw(self, painter):
        FrameView.draw(self, painter)
        
        ast = self.level.asteroids
        plnt = self.level.planets
        shots = self.level.shots
        missiles = self.level.missiles
        portals = self.level.portals

        pos = self.level.ship.shape.position
        ship_x, ship_y = self.convert_to_local(pos)
        
        dir = self.level.ship.ship_dir
        
        if (dir is None):
            return
        
        sd_x, sd_y = self.convert_to_local(dir)
        angle = degrees(atan2(sd_y, sd_x)) - 90.0
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        
        glRotatef(-angle,0.,0.,1.)
        glTranslatef(-ship_x,-ship_y,0.)
        
        for obj in chain(ast,plnt):
            c = (1.,0.,0.) if obj.target else (0.,0.,1.)
            self.draw_square(obj.shape.position, 5, c)
        
        for obj in portals:
            self.draw_square(obj.shape.position, 5, (0.,1.,0.))
        
        for obj in shots:
            self.draw_square(obj.shape.position, 1.5, (1.,1.,1.))
        
        for obj in missiles:
            self.draw_square(obj.shape.position, 3, (.8,.8,.8))
            
        glPopMatrix()

    def setup_projection(self):
        custom_ortho_projection(
            self.view_x, self.view_y,
            -self.view_w2, self.view_w2,
            -self.view_h2, self.view_h2
        )

    def draw_square(self, pos, s, c):
        x, y = self.convert_to_local(pos)
        
        s = s / 2.
        
        glColor3f(*c)
        
        glBegin(GL_QUADS)
        glVertex2f(s+x,s+y)
        glVertex2f(s+x,-s+y)
        glVertex2f(-s+x,-s+y)
        glVertex2f(-s+x,s+y)
        glEnd()

    def convert_to_local(self, pos):
        return (pos.x * self.ratio_x, pos.z * self.ratio_z)
