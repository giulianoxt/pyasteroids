"""
    Code for interpreting a .ply file
    as a OpenGL polygon mesh
"""

from math import sqrt

from OpenGL.GL import *

from PyQt4.QtGui import QImage
from PyQt4.QtOpenGL import QGLWidget

from model.ply import PLYModel

from physics.vector3d import Vector3d
from physics.collision import BoundingSphere


class GLModel(object):
    def __init__(self, file, translate = (0.,0.,0.), rotate = (0.,0.,0.), scale = 0.):
        self.ply = PLYModel(file)
        
        self.textures = None
        self.dlist = None
        
        if (not 'vertex' in self.ply or not 'face' in self.ply):
            raise Exception('Invalid PLY model')
        
        if ('material' in self.ply and 'material_index' in self.ply['face'][0]):
            self.generate_textures()      
    
        self.sphere = BoundingSphere()
    
        self.make_display_list(translate, rotate, scale)
    
    def generate_textures(self):
        num_text = len(self.ply['material'])
        
        self.textures = glGenTextures(num_text)
        
        if (num_text == 1):
            self.textures = [self.textures]
        else:
            self.textures = list(self.textures)
        
        for i in xrange(num_text):
            text_id = self.textures[i]
            text_path = self.ply['material'][i]['texture_map'].strip()
            
            if (not len(text_path)):
                self.textures[i] = None
                continue

            glBindTexture(GL_TEXTURE_2D, text_id)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            img = QImage(text_path)
            img = QGLWidget.convertToGLFormat(img)
            
            glTexImage2D(GL_TEXTURE_2D, 0, 3, img.width(), img.height(),
                0, GL_RGBA, GL_UNSIGNED_BYTE, img.bits().asstring(img.numBytes()))
            
            glBindTexture(GL_TEXTURE_2D, 0)
            
        if (not any(self.textures)):
            self.textures = None           
       
    def make_display_list(self, translate, rotate, scale):
        self.dlist = glGenLists(1)
        glNewList(self.dlist, GL_COMPILE)
        
        glTranslate(*translate)
        
        for ((x,y,z),a) in zip(((1.,0.,0.), (0.,1.,0.), (0.,0.,1.)), rotate):
            glRotatef(a,x,y,z)
        
        self.scale = scale
        self.offset = translate
        
        glScalef(*([scale]*3))
        
        self.direct_draw()
        
        glEndList()
        
        del self.ply

    def __del__(self):
        if (hasattr(self,'textures') and self.textures):
            glDeleteTextures(self.textures)
        
        if (self.dlist):
            glDeleteLists(self.dlist, 1)

    def direct_draw(self):
        faces = self.ply['face']
        vertex_list = self.ply['vertex']
        textures = self.textures
        
        def has_texture(face):
            return (textures and textures[f['material_index']])
        
        max_x, max_y, max_z = 0., 0., 0.
        
        for f in faces:
            ht = has_texture(f)
            
            if (ht):
                glBindTexture(GL_TEXTURE_2D, textures[f['material_index']])
            
            v_index_l = f['vertex_indices']
            
            if (len(v_index_l) == 3):
                glBegin(GL_TRIANGLES)
            else:
                glBegin(GL_QUADS)
            
            for v in (vertex_list[i] for i in v_index_l):
                glNormal3f(v['nx'],v['ny'],v['nz'])
                
                if (ht):
                    glTexCoord2f(v['s'],v['t'])

                glVertex3f(v['x'],v['y'],v['z'])
                
                if (v['x'] > max_x):
                    max_x = v['x']
                if (v['y'] > max_y):
                    max_y = v['y']
                if (v['z'] > max_z):
                    max_z = v['z']
            
            glEnd()
            
            if (ht):
                glBindTexture(GL_TEXTURE_2D, 0)
    
        max_x = (max_x + self.offset[0]) * self.scale
        max_y = (max_y + self.offset[1]) * self.scale
        max_z = (max_z + self.offset[2]) * self.scale
        
        self.sphere.center = Vector3d(0.,0.,0.)
        self.sphere.radius = sqrt(max_x**2 + max_y**2 + max_z**2)
    
    def draw(self):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        
        glCallList(self.dlist)
        
        glPopMatrix()
    

# Testing
if (__name__ == '__main__'):  
    f = open('../resources/models/long-spaceship/long-spaceship.ply','r')
    
    try:
        model = GLModel(f) 
    finally:
        f.close()