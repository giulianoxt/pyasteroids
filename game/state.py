from OpenGL.GL import *
from OpenGL.GLU import *

from util.config import Config

from pyqt.opengl import GLController

from util.opengl import default_perspective


class Player(object):
    instance = None
    
    @classmethod
    def get_instance(cls):
        return Player.instance
    
    def __init__(self):
        if (Player.instance is None):
            Player.instance = self
        
        cfg = Config('game', 'Player')
        self.max_hp = cfg.get('max_hp')
        self.initial_lifes = cfg.get('initial_lifes')
        
        self.reset()
        
    def beginning_level(self, level):
        self.reset()
        
        for obj in level.all_objects():
            if (obj is not None and obj.target):
                self.initial_targets += 1
        
        self.targets = self.initial_targets
        
        self.level = level
    
    def object_added(self, obj):
        if (obj.target):
            self.initial_targets += 1
            self.targets += 1
    
    def object_destroyed(self, obj):
        if (obj.target):
            self.targets -= 1
        
        self.score += obj.score
               
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        controller = GLController.get_instance()
        
        default_perspective(controller.width(), controller.height())
        
        self.level.camera.put_in_position()
        
        pos = map(int, gluProject(*obj.shape.position)[0:2])
        pos[1] = controller.height() - pos[1]
        
        glPopMatrix()
        
        controller.push_screen('MovingMessage','Show_Score','+'+str(obj.score),pos)
    
    def got_hit(self, obj):
        if (obj.hostile):
            self.hp -= obj.damage
            
            if (self.hp <= 0):
                self.hp = self.max_hp
                self.lifes -= 1
    
    def reset(self):
        self.hp = self.max_hp
        self.lifes = self.initial_lifes
        self.score = 0
        self.initial_targets = 0
        self.targets = 0
