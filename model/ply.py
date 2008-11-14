"""
    Code for .ply model handling 
"""

class PLYModel(dict):
    "map element_name -> list of elements"
    
    def __init__(self, file):       
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
                    
                    element.properties.append(PropertyHeader(line[-1],line[1:-1]))
                
                self.elements.append(element)
            elif (cod == 'end_header'):
                break
            else:
                raise Exception('Invalid header component: ' + cod)

        self.parseElements(file)
    
    def parseElements(self, file):
        cast_func = {
            'int32'   : int,
            'int8'    : int,
            'uint8'   : int,
            'uint32'  : int,
            'float32' : float,
            'string'  : lambda x : x
        }
        
        for el in self.elements:
            l = [] 
            
            for i in xrange(el.count):
                line = file.readline().strip().split()
                
                i = 0
                properties = {}
                
                for p in el.properties:
                    if (not p.type.startswith('list')):
                        properties[p.name] = cast_func[p.type](line[i])
                        i += 1
                    else:
                        p_val = []
                        size = int(line[i])
                        type = p.type.split()[2]
                        cast = cast_func[type]
                        
                        for j in xrange(size):
                            p_val.append(cast(line[i + j + 1]))
                            
                        i += j + 1
                
                l.append(properties)
                    
            self[el.name] = l 


class ElementHeader(object):
    def __init__(self, name, count):
        self.name = name
        self.count = count
        self.properties = []

        
class PropertyHeader(object):
    def __init__(self, name, type):
        self.name = name
        self.type = ' '.join(type)


# Testing
if (__name__ == '__main__'):
    f = open('../resources/models/long-spaceship/long-spaceship.ply')
    
    try:
        ply = PLYModel(f)
        print ply
    finally:
        f.close()
