from OpenGL.GL import *
from OpenGL.GLU import *

from PyQt4.QtGui import QImage,  QColor
from PyQt4.QtCore import Qt, QPoint, QRect

from util.config import Config, ConfigManager, FontManager
from util.opengl import ortho_projection, custom_ortho_projection


class Interface(object):
    def __init__(self, level_number):
        self.level_number = level_number
        
        self.info = {}
        self.fields = set()
        
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
        
        # gather data for self.info dict
        pass
    
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
                self.field_color, '123 opa'
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
        
        self.view_x = view_rect.topLeft().x()
        self.view_y = view_rect.topLeft().y()
        self.view_w = view_rect.width()
        self.view_h = view_rect.height() 
        
        self.interface = interface
        
    def draw(self, painter):
        c = self.interface.controller
        w, h = c.width(), c.height()
        ortho_projection(w,h)
        
        painter.drawImage(self.image_rect, self.image)
        
        self.setup_projection()

    def setup_projection(self):
        custom_ortho_projection(
            self.view_x, self.view_y, self.view_w, self.view_h
        )


class GuidedMissile(FrameView):
    def draw(self, painter):
        FrameView.draw(self, painter)
        
        glBegin(GL_TRIANGLES)
        glVertex3f(50.,0.,0.)
        glVertex3f(80.,0.,0.)
        glVertex3f(80.,30.,0.)
        glEnd()


class Radar(FrameView):
    def draw(self, painter):
        FrameView.draw(self, painter)
