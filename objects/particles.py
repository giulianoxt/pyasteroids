from random import uniform

from OpenGL.GL import *

from PyQt4.QtGui import QImage
from PyQt4.QtOpenGL import QGLWidget
from PyQt4.QtCore import QPointF, QRectF

from util.config import Config
from util.misc import apply_irange
from util.opengl import spherical_billboarding


class ParticleSystem(object):
    @classmethod
    def from_template(cls, section, level, pos = None, vel = None):
        cfg = Config('effects', section)
        
        num_particles = cfg.get('num_particles')
        
        pos_irange = cfg.get('position_irange')
        pos = pos if (pos is not None) else cfg.get('position')
        
        vel_irange = cfg.get('velocity_irange')
        vel = vel if (vel is not None) else cfg.get('velocity')
        
        duration = cfg.get('duration')
        duration_irange = cfg.get('duration_irange')
        
        color_seq = cfg.get('color_sequence')
        
        quad_sz = cfg.get('quad_size')
        
        img_path = cfg.get('image_path')
        
        return cls(
            level, num_particles, pos, pos_irange,
            vel, vel_irange, duration, duration_irange,
            color_seq, quad_sz, 'resources/images/'+img_path
        )
    
    def __init__(self, screen, num_particles, pos, pos_irange, vel,
            vel_irange, duration, duration_irange, color_seq, quad_sz, img_path):
        
        self.screen = screen
        self.num_particles = num_particles
        
        self.setup_texture(img_path)
        #self.setup_display_list(quad_sz)
        
        self.particles = set()
        
        rect = QRectF(0.,0.,quad_sz,quad_sz)
        rect.moveCenter(QPointF(0.,0.))
        
        for i in xrange(self.num_particles):
            pos = apply_irange(pos, pos_irange)
            vel = apply_irange(vel, vel_irange)
            duration = duration + uniform(*duration_irange)
            
            #p = Particle(pos, vel, color_seq, self.display_list, duration)
            p = Particle(pos, vel, color_seq, (self.texture, rect, self.screen.qpainter), duration)
            
            self.particles.add(p)
        
    def setup_texture(self, img_path):
#        self.texture = glGenTextures(1)
#        
#        glBindTexture(GL_TEXTURE_2D, self.texture)
#        
#        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
#        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
#        
#        img = QImage(img_path)
#        img = QGLWidget.convertToGLFormat(img)
#        
#        glTexImage2D(GL_TEXTURE_2D, 0, 3, img.width(), img.height(),
#            0, GL_RGBA, GL_UNSIGNED_BYTE, img.bits().asstring(img.numBytes()))
#            
#        glBindTexture(GL_TEXTURE_2D, 0)

        self.texture = QImage(img_path)

        
#    def setup_display_list(self, sz):
#        sz = sz / 2.
#        self.display_list = glGenLists(1)
#        
#        glNewList(self.display_list, GL_COMPILE)
#        
#        glBegin(GL_QUADS)
#        glTexCoord2f(1.,1.); glVertex3f(sz,sz,0.)
#        glTexCoord2f(1.,0.); glVertex3f(sz,-sz,0.)
#        glTexCoord2f(0.,0.); glVertex3f(-sz,-sz,0.)
#        glTexCoord2f(0.,1.); glVertex3f(-sz,sz,0.)
#        glEnd()
#        
#        glEndList() 

        
    def tick(self, time_elapsed):
        erase = set()
        
        for p in self.particles:
            if (not p.tick(time_elapsed)):
                erase.add(p)
        
        self.particles.difference_update(erase)
        
        if (not len(self.particles)):
            self.screen.remove_object(self)
    
    def draw(self):
        glPushAttrib(GL_CURRENT_BIT | GL_ENABLE_BIT)
        
        glDisable(GL_DEPTH_TEST)
        
        #glBindTexture(GL_TEXTURE_2D, self.texture)
        
        cam_pos = self.screen.camera.pos
        
        for p in self.particles:
            p.draw(cam_pos)
        
        #glBindTexture(GL_TEXTURE_2D, 0)
        glPopAttrib()

    
class Particle(object):
    #def __init__(self, pos, vel, color_seq, display_list, duration):
    def __init__(self, pos, vel, color_seq, (image,r,p), duration):
        self.pos = pos
        self.vel = vel
        
        self.elapsed = 0.
        self.duration = duration
        
        self.alpha = 1.
        
        self.color_seq = color_seq
        self.color = self.color_seq[0]
        self.color_step = float(self.duration) / len(self.color_seq)
        
        #self.display_list = display_list
        self.image = image
        self.image_rect = r 
        self.painter = p
    
    def draw(self, cam_pos):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        
        glTranslatef(*self.pos)
        
        spherical_billboarding(cam_pos, self.pos)
        
        c = self.color
        glColor4ub(c[0],c[1],c[2],self.alpha)
        
        #glCallList(self.display_list)
        self.painter.drawImage(self.image_rect, self.image)
        
        glPopMatrix()
    
    def tick(self, time_elapsed):
        self.elapsed += time_elapsed
        
        if (self.elapsed >= self.duration):
            return False        
        
        self.alpha = int((self.elapsed / self.duration) * 255)

        self.color = self.color_seq[int(self.elapsed / self.color_step)]
        
        self.pos += self.vel.scalar(time_elapsed)

        return True
