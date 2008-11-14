import os

from ConfigParser import ConfigParser

class ConfigManager(object):
    instance = None
    
    @classmethod
    def getInstance(cls):
        return ConfigManager.instance
    
    def __init__(self):
        ConfigManager.instance = self
        
        self.parsers = {}
        
        dir = os.path.join('resources','config')
        
        for file in os.listdir(os.path.join('resources','config')):
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

