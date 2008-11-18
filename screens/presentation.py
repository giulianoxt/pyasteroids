from OpenGL.GL import *
from OpenGL.GLU import *

class Intro(object):
    def __init__(self, *args, **kwargs):
        pass
    
    def draw(self):
        pass
    
    def tick(self, time_elapsed):
        self.controller.push_screen('Level','first-crusade')
