class Circle:
    def __init__(self, posx, posy, radius, color=(255, 0, 0), surface=None, width=0):
        self.pos = (int(posx), int(posy))
        self.radius = int(radius)
        self.color = color
        if surface is None:
            pass
        else:
            self.surface = surface
            self.surface_pos = (int(posx-self.radius), int(posy-self.radius))
        self.width = int(width)

    def add_surface(self, surface):
        self.surface = surface

class Rectangle:
    def __init__(self, posx, posy, sizex, sizey, color=(255, 0, 0), surface=None, width=0):
        self.pos = (int(posx), int(posy))
        self.size = (int(sizex), int(sizey))
        self.color = color
        if surface is None:
            pass
        else:
            self.surface = surface
        self.width = int(width)
    
    def add_surface(self, surface):
        self.surface = surface