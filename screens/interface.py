from OpenGL.GL import *
from OpenGL.GLU import *

from PyQt4.QtGui import QImage,  QColor
from PyQt4.QtCore import Qt, QPoint, QRect

from util.config import ConfigManager
from util.opengl import ortho_projection


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

    def tick(self, time_elapsed):
        self.controller.tick_parent(self, time_elapsed)
        
        # gather data for self.info dict
        pass
    
    def draw(self):        
        self.controller.draw_parent(self)
        
        glClear(GL_DEPTH_BUFFER_BIT)
        
        ortho_projection(
            self.controller.width(), self.controller.height()
        )
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        for field in self.fields:
            field.draw(self.qpainter, None, QColor.fromRgb(255,255,255,100), None)

class Field(object):
    flags = Qt.AlignVCenter | Qt.AlignHCenter
    
    def __init__(self, name, img, img_rect, info_rect):
        self.name = name
        self.img = img
        self.img_rect = img_rect
        self.info_rect = info_rect
        
    def draw(self, painter, font, color, info):
        painter.drawImage(self.img_rect, self.img)
        
        #painter.setFont(font)
        #painter.setPen(color)
        #painter.drawText(self.rect, Field.flags, info)

        painter.setPen(color)
        painter.fillRect(self.info_rect, color)
