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
            
            self.info[f_name] = ''
            self.fields.add(Field(f_name, img, img_pos, info_rect))

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
            field.draw(self.qpainter, None, QColor.fromRgb(255,255,255), None)

class Field(object):
    flags = Qt.AlignVCenter | Qt.AlignHCenter
    
    def __init__(self, name, img, pos, rect):
        self.name = name
        self.img = img
        self.pos = pos
        self.rect = rect
        
    def draw(self, painter, font, color, info):
        painter.drawImage(self.pos, self.img)
        
        #painter.setFont(font)
        #painter.setPen(color)
        #painter.drawText(self.rect, Field.flags, info)

        painter.setPen(color)
        painter.fillRect(self.rect, color)
