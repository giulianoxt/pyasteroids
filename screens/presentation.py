from OpenGL.GL import *
from OpenGL.GLU import *

from screens.level import Level

class Intro(object):
    def __init__(self, *args, **kwargs):
        pass
    
    def draw(self):
        pass
    
    def tick(self, time_elapsed):
        self.controller.pop_screen(self)
        self.controller.push_screen('Level', 1)
        self.controller.push_screen('Interface', 1, Level.instance)
