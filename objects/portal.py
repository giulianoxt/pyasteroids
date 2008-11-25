from objects import Object

class Portal(Object):
    def __init__(self, model, shape, element):
        Object.__init__(self, model, shape, element)
        
        self.type = element['type'].split('_')[0]
