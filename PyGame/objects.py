class Circle:
    def __init__(self, radius, pos):
        self.pos = pos
        self.radius = radius
        self.v = 0
    
    def setVandPos(self, a):
        self.v += a
        self.pos += self.v