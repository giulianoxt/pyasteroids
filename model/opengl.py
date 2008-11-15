"""
    Code for interpreting a .ply file
    as a OpenGL polygon mesh
"""

from OpenGL.GL import *

from PyQt4.QtGui import QImage
from PyQt4.QtOpenGL import QGLWidget

from model.ply import PLYModel


class GLModel(object):
    def __init__(self, file):
        self.ply = PLYModel(file)
        
        self.setup_dl = None
        self.main_dl = None
        self.textures = None
        
        if (not 'vertex' in self.ply or not 'face' in self.ply):
            raise Exception('Invalid PLY model')
        
        if ('material' in self.ply and 'material_index' in self.ply['face'][0]):
            self.generate_textures()      
    
        self.generate_display_list()
    
    def generate_textures(self):
        num_text = len(self.ply['material'])
        
        self.textures = glGenTextures(num_text)
        
        if (num_text == 1):
            self.textures = (self.textures,)
        
        for i in xrange(num_text):
            text_id = self.textures[i]
            text_path = self.ply['material'][i]['texture_map'].strip()
            
            if (not len(text_path)):
                self.textures[i] = None

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
    
    def generate_display_list(self):
        self.main_dl = glGenLists(1)
        glNewList(self.main_dl, GL_COMPILE)
        self.direct_draw()
        glEndList()
        
        del self.ply

    def __del__(self):
        if (self.textures):
            glDeleteTextures(self.textures)
        
        if (self.setup_dl):
            glDeleteLists(self.setup_dl, 1)
        
        if (self.main_dl):
            glDeleteLists(self.main_dl, 1)

    def direct_draw(self):
        faces = self.ply['face']
        vertex_list = self.ply['vertex']
        textures = self.textures
        
        def has_texture(face):
            return (textures and textures[f['material_index']])
        
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
            
            glEnd()
            
            if (ht):
                glBindTexture(GL_TEXTURE_2D, 0)
    
    def draw(self):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        
        if (self.setup_dl is not None):
            glCallList(self.setup_dl)
        
        glCallList(self.main_dl)
        
        glPopMatrix()
    

# Testing
if (__name__ == '__main__'):  
    f = open('../resources/models/long-spaceship/long-spaceship.ply','r')
    
    try:
        model = GLModel(f) 
    finally:
        f.close()