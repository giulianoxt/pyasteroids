
class Deque(object):
    def __init__(self):
        self.head = [None, None]
        self.tail = self.head
        self.size = 0
    
    def push_back(self, obj):
        new = [obj, None]
        self.tail[1] = new
        self.tail = new
        
        self.size += 1
    
    def push_front(self, obj):
        new = [obj, self.head[1]]
        self.head = [None, new]
        
        self.size += 1
    
    def pop_front(self):
        if (not self.size):
            return
        
        obj = self.head[1][0]
        
        self.head = [None, self.head[1][1]]
                     
        self.size -= 1
                    
        return obj

    def __len__(self):
        return self.size

    def __str__(self):
        s = '['
        nod = self.head[1]
        
        while (nod is not None):
            s += str(nod[0])
            nod = nod[1]
            
            if (nod is not None):
                s += ', '
        
        s += ']'
        
        return s


if (__name__ == '__main__'):
    d = Deque()
    
    for i in xrange(10):
        d.push_back(i)
        d.push_front(i)
    
    print d
    print len(d)

    while len(d):
        print d.pop_front(),
