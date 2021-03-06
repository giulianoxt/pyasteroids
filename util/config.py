import os

from ConfigParser import ConfigParser

from PyQt4.QtGui import QFont, QFontDatabase

_config_dir = os.path.join('resources','config')


class ConfigManager(object):
    instance = None
    
    @classmethod
    def getInstance(cls):
        if (ConfigManager.instance is None):
            ConfigManager.instance = ConfigManager()
        
        return ConfigManager.instance
    
    def __init__(self):
        ConfigManager.instance = self
        
        self.parsers = {}
        
        dir = _config_dir
        
        for file in os.listdir(dir):
            filepath = os.path.join(dir, file)
            filename = '.'.join(file.split('.')[:-1])
            
            if (not os.path.isfile(filepath)):
                continue
            
            fd = open(filepath,'r')
            self.parsers[filename] = ConfigParser()
            self.parsers[filename].readfp(fd)
            fd.close()
    
    @classmethod
    def getVal(cls, file, section, option):
        cm = ConfigManager.getInstance()
        return cm.parsers[file].get(section,option)
    
    @classmethod
    def setVal(cls, file, section, option, val):
        cm = ConfigManager.getInstance()
        cm.parsers[file].set(section, option, val)
    
    @classmethod
    def getFiles(cls):
        return ConfigManager.getInstance().parsers.keys()
    
    @classmethod
    def getSections(cls, file):
        cm = ConfigManager.getInstance()
        return cm.parsers[file].sections()
    
    @classmethod
    def getOptions(cls, file, section):
        cm = ConfigManager.getInstance()
        return cm.parsers[file].options(section)


class Config(object):
    def __init__(self, file = '', section = ''):
        self.file = file
        self.section = section
        
    def get(self, key):
        return eval(ConfigManager.getVal(self.file, self.section, key))
    
    def set(self, key, val):
        ConfigManager.setVal(self.file, self.section, key, str(val))


class FontManager(object):
    instance = None

    def __init__(self):
        if (FontManager.instance is None):
            FontManager.instance = self
        
        self.fonts = {}
        
        for font_name in ConfigManager.getOptions('interface','Fonts'):
            tmp = ConfigManager.getVal('interface','Fonts',font_name)
            path, family = tuple(map(str.strip,tmp.split('||'))) 

            QFontDatabase.addApplicationFont('resources/fonts/' + path)

            self.fonts[font_name] = QFont(family)
    
    @classmethod
    def getFont(cls, font_name):
        fm = FontManager.instance
        return QFont(fm.fonts[font_name])
