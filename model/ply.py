"""
    Code for .ply model handling 
"""

class PLYModel(dict):
    "map element_name -> list of elements"
    
    def __init__(self, filename):
        file = open(filename, 'r')
        
        if (file.readline().strip() != 'ply'):
            raise Exception('File not in .ply format')
        
        self.elements = []
        
        skipline = None
        
        while True:
            if (skipline is None):
                line = file.readline().strip().split()
            else:
                line = skipline
                skipline = None
                
            cod = line[0]
            
            if (cod == 'format'):
                if (line[1] != 'ascii' or line[2] != '1.0'):
                    raise Exception('Ply format not supported')
            elif (cod == 'comment'):
                continue
            elif (cod == 'element'):
                element = ElementHeader(line[1], int(line[2]))
                
                while True:
                    line = file.readline().strip().split()
                    
                    if (line[0] != 'property'):
                        skipline = line
                        break
                    
                    element.properties.append(PropertyHeader(line[2],line[1]))
                
                self.elements.append(element)
            elif (cod == 'end_header'):
                break

            
class ElementHeader(object):
    def __init__(self, name, count):
        self.name = name
        self.count = count
        self.properties = []

        
class PropertyHeader(object):
    def __init__(self, name, type):
        self.name = name
        self.type = type



# Testing
if (__name__ == '__main__'):
    ply = PLYModel('../resources/models/long-spaceship/long-spaceship.ply')
    
    for el in ply.elements:
        print 'el.name = ', el.name
        print 'el.count = ', el.count
