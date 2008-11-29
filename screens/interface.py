from itertools import chain
from math import atan2, degrees

from OpenGL.GL import *
from OpenGL.GLU import *

from PyQt4.QtGui import QImage,  QColor
from PyQt4.QtCore import Qt, QPoint, QRect

from util.config import Config, ConfigManager, FontManager
from util.opengl import ortho_projection, custom_ortho_projection


class Interface(object):
    def __init__(self, level_number, level):
        self.level_number = level_number
        
        self.info = {}
        self.fields = set()
        
        self.level = level
        
        for f_name in ConfigManager.getOptions('interface', 'Fields'):
            s = ConfigManager.getVal('interface', 'Fields', f_name)
            s = map(str.strip, s.split('||'))
            
            img = QImage('resources/images/'+s[0])
            img_pos = QPoint(*eval(s[1]))
            info_rect = QRect(*eval(s[2]))
            scale = float(s[3])
            
            img_w, img_h = img.width(), img.height()
            img_rect = QRect(
                img_pos.x(), img_pos.y(),
                int(img_w*scale), int(img_h*scale)
            )
            
            self.info[f_name] = ''
            self.fields.add(Field(f_name, img, img_rect, info_rect))
        
        cfg = Config('interface', 'Settings')
        font_name = cfg.get('field_font')
        font_size = cfg.get('field_font_sz')
        self.field_font = FontManager.getFont(font_name)
        self.field_font.setPointSize(font_size)
        self.field_color = QColor.fromRgb(*cfg.get('field_color'))
        
        self.radar = Radar.from_config('E-Radar', self)
        self.missile = GuidedMissile.from_config('GuidedMissile', self)

    def tick(self, time_elapsed):
        self.controller.tick_parent(self, time_elapsed)
        
        self.info['alt'] = str(int(self.level.ship.shape.position.y))
        self.info['speed'] = str(int(self.level.ship.shape.velocity.get_mod()))
    
    def draw(self):        
        self.controller.draw_parent(self)
        
        ortho_projection(
            self.controller.width(), self.controller.height()
        )
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        painter = self.qpainter
        
        for field in self.fields:
            field.draw(
                painter, self.field_font,
                self.field_color, self.info[field.name]
            )
        
        self.missile.draw(painter)
        self.radar.draw(painter)


class Field(object):
    flags = Qt.AlignVCenter | Qt.AlignHCenter
    
    def __init__(self, name, img, img_rect, info_rect):
        self.name = name
        self.img = img
        self.img_rect = img_rect
        self.info_rect = info_rect
        
    def draw(self, painter, font, color, info):
        painter.drawImage(self.img_rect, self.img)
        
        painter.setFont(font)
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
    def draw(self, painter):
        FrameView.draw(self, painter)
    
    def setup_projection(self):
        custom_ortho_projection(
            self.view_x, self.view_y,
            -self.view_w2, self.view_w2,
            -self.view_h2, self.view_h2
        )


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
            x, y = self.convert_to_local(obj.shape.position)
            
            self.draw_square(x, y, 5, (1., 0., 0.))
            
        glPopMatrix()

    def setup_projection(self):
        custom_ortho_projection(
            self.view_x, self.view_y,
            -self.view_w2, self.view_w2,
            -self.view_h2, self.view_h2
        )

    def draw_square(self, x, y, s, c):
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
