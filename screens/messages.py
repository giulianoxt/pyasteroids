from OpenGL.GL import *
from OpenGL.GLU import *

from PyQt4.QtGui import QColor
from PyQt4.QtCore import Qt, QRect, QPoint

from util.config import Config, FontManager

from util.opengl import ortho_projection


qt_center_flag = Qt.AlignVCenter | Qt.AlignHCenter


class FadeMessage(object):
    def __init__(self, message, str = None):
        cfg = Config('messages', message)

        if (str is None):
            self.str = cfg.get('message')
        else:
            self.str = str
        
        self.duration = cfg.get('duration')
        self.fade_duration = cfg.get('fade_duration')
        
        self.color = QColor.fromRgb(*cfg.get('color'))
        self.alpha_final = self.color.alpha()
        self.color.setAlpha(0)
        
        self.font = FontManager.getFont(cfg.get('font'))
        self.font.setPointSize(cfg.get('font_size'))
        
        self.font_color = QColor.fromRgb(*cfg.get('font_color'))
        self.font_alpha_final = self.font_color.alpha()
        self.font_color.setAlpha(0)
        
        self.elapsed = 0.0        
        self.state = 0
        self.tick_funcs = [self.tick_fade_in, self.tick_message, self.tick_fade_out]
    
    def with_controller(self):
        self.rect = QRect(0, 0, self.controller.width(), self.controller.height())

    def tick(self, elapsed):
        self.elapsed += elapsed
        self.tick_funcs[self.state](elapsed)
    
    def tick_fade_in(self, elapsed):
        self.controller.tick_parent(self, elapsed)
        
        if (self.elapsed >= self.fade_duration):
            self.elapsed = 0.
            self.state += 1
        else:
            ar = (self.elapsed / self.fade_duration)
            
            self.color.setAlpha(int(ar * self.alpha_final))
            self.font_color.setAlpha(int(ar * self.font_alpha_final))
        
    def tick_message(self, elapsed):
        self.controller.tick_parent(self, elapsed)
        
        if (self.elapsed >= self.duration):
            self.elapsed = 0.
            self.state += 1
    
    def tick_fade_out(self, elapsed):
        self.controller.tick_parent(self, elapsed)
        
        if (self.elapsed >= self.fade_duration):
            self.controller.pop_screen(self)
        else:
            ar = ((self.fade_duration - self.elapsed) / self.fade_duration)
            
            self.color.setAlpha(int(ar * self.alpha_final))
            self.font_color.setAlpha(int(ar * self.font_alpha_final))
    
    def draw(self):
        self.controller.draw_parent(self)
        
        ortho_projection(
            self.controller.width(), self.controller.height()
        )

        self.qpainter.fillRect(self.rect, self.color)
        self.qpainter.setFont(self.font)
        self.qpainter.setPen(self.font_color)
        self.bounding_text_rect = self.qpainter.drawText(self.rect, qt_center_flag, self.str)


class PauseMessage(FadeMessage):
    def __init__(self):
        FadeMessage.__init__(self, 'Pause')
            
    def tick_message(self, elapsed):
        pass
    
    def keyPressEvent(self, event):
        if (event.isAutoRepeat()):
            return
        
        k = event.key()
        
        if (k == Qt.Key_P or k == Qt.Key_Escape):
            self.elapsed = 0.
            self.state = 2


class MovingMessage(FadeMessage):
    def __init__(self, message, str = None, pos = None):
        cfg = Config('messages', message)
        
        if (pos is None):
            self.pos = QPoint(*cfg.get('position'))
        else:
            self.pos = QPoint(*pos)
        
        self.velocity = cfg.get('velocity') 
        
        FadeMessage.__init__(self, message, str)
    
    def with_controller(self):
        self.rect = QRect(0, 0, self.controller.width(), self.controller.height())
        self.rect.moveCenter(self.pos)

    def tick(self, elapsed):        
        FadeMessage.tick(self, elapsed)

        self.pos.setX(self.pos.x() + self.velocity[0] * elapsed)
        self.pos.setY(self.pos.y() + self.velocity[1] * elapsed)
        
        self.rect.moveCenter(self.pos)
    
    def draw(self):
        FadeMessage.draw(self)
        
        self.rect = self.bounding_text_rect
