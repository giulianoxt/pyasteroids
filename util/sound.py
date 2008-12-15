from PyQt4.QtGui import QSound, QMessageBox

from util.config import ConfigManager

def pyqt_play_sound(sound, loops):
    if (loops != 0):
        sound.setLoops(loops)
    sound.play()
    
def pyqt_stop_sound(sound):
    sound.stop()
    
def pygame_play_sound(sound, loops):
    sound.play(loops)

def pygame_stop_sound(sound):
    sound.stop()


class SoundManager(object):
    instance = None
    
    @classmethod
    def getInstance(cls):
        if (SoundManager.instance is None):
            SoundManager.instance = SoundManager()
            
        return SoundManager.instance
    
    def __init__(self):
        if (SoundManager.instance is None):
            SoundManager.instance = self
        else:
            return
        
        SoundClass = None
        self.play_func = None
        self.stop_func = None
        self.available = True
        
        if (QSound.isAvailable()):
            SoundClasse = QSound
            self.play_func = pyqt_play_sound
            self.stop_func = pyqt_stop_sound
        else:
            try:
                import pygame
                pygame.init()
                pygame.mixer.set_num_channels(12)
                
                SoundClass = pygame.mixer.Sound
                self.play_func = pygame_play_sound
                self.stop_func = pygame_stop_sound
            except:
                QMessageBox.warning(None,'PyAsteroids - Sound',
                    'This platform does not provide sound facilites through Qt nor PyGame. \
                    Sound is disabled')
                
                self.available = False
                return
        
        self.sounds = {}
        
        for sec in ConfigManager.getSections('sounds'):
            self.sounds[sec] = {}
            
            for audio_descr in ConfigManager.getOptions('sounds', sec):
                file, vol = map(str.strip, ConfigManager.getVal('sounds',sec,audio_descr).split('||'))
                vol = float(vol)
                
                sound = SoundClass(file)
                
                if (not (SoundClass is QSound)):
                    sound.set_volume(vol)
                
                self.sounds[sec][audio_descr] = sound
      
    @classmethod
    def play(cls, section, name):
        self = SoundManager.getInstance()
        
        if (self.available):
            sound = self.sounds[section].get(name, None)
            
            if (sound):
                self.play_func(sound,0)
            else:
                print 'SoundManager::play() : Could not find sound [%s] - [%s]' % (section, name)
        
    @classmethod
    def playOnLoop(cls, section, name, n):
        self = SoundManager.getInstance()
        
        if (self.available):
            sound = self.sounds[section].get(name, None)
            
            if (sound):
                self.play_func(sound,n)
            else:
                print 'SoundManager::playOnLoop() : Could not find sound [%s] - [%s]' % (section, name)             
   
    @classmethod
    def stop(cls, section, name):
        self = SoundManager.getInstance()
        
        if (self.available):
            sound = self.sounds[section].get(name, None)
            
            if (sound):
                self.stop_func(sound)
            else:
                print 'SoundManager::stop() : Could not find sound [%s] - [%s]' % (section, name)

