import pygame
from polygons import Rectangle, Circle


#Graphical element
class UI_Element: 
    def __init__(self, text, hitbox_size, position, text_position=0, hitbox_color=(255, 0, 0), hitbox_border=True, gradient=True, \
    startcolor=(200, 200, 200, 255), endcolor=(100, 100, 100, 255), gradient_type=0, hitbox_image=None, text_color=(255, 255, 255), \
    shows_value=True):
        self.font = None #Text surface
        self.font_pos = None
        self.background = None #Hitbox color
        self.hitbox = Rectangle(position[0], position[1], hitbox_size[0], hitbox_size[1], color=hitbox_color, surface=None)#Contains the position and the size
        self.hitbox_surf = None #Hitbox surface

    #Resizing the surface to fit in the hitbox preserving the ratio, instead of fuckin it up
    def surface_resize(self):
        new_surf_size = list(self.hitbox_surf.get_size()) #Copy of the size of the surface
        for surf_axis_size, hitbox_axis_size in zip(new_surf_size, self.hitbox.size):
            if surf_axis_size > hitbox_axis_size:
                ratio = (hitbox_axis_size/surf_axis_size)
                for i in range (0, len(new_surf_size)): #This way it modifies the list, the normal iterator doesn't work that way, assigning names and shit
                    new_surf_size[i] = int(new_surf_size[i]*ratio)
        self.surface = pygame.transform.scale(self.surface, tuple(new_surf_size)) #Resizing the surface

    #Sets the surface position on the hitbox
    def set_surface_pos(self, horizontal_offset=0, centering = 0):
        position = list(self.font_pos)
        if centering is 0: #Center
            position[0] = (self.hitbox.size[0]/2) - (self.surface.get_size()[0]/2)
        elif centering is 1: #Left
            position[0] = horizontal_offset
        elif centering is 2:
            position[0] = self.hitbox.size[0]-horizontal_offset
        self.surface_position = tuple(position)

class Slider_Element(UI_Element):
    def __init__(self, text, hitbox_size, position, text_position=0, hitbox_color=(255, 0, 0), hitbox_border=True, gradient=True, \
    startcolor=(200, 200, 200, 255), endcolor=(100, 100, 100, 255), gradient_type=0, hitbox_image=None, text_color=(255, 255, 255), \
    shows_value=True):
        super().__init__(text, hitbox_size, position, hitbox_color, hitbox_border, gradient, startcolor, endcolor, gradient_type, \
        hitbox_image, text_color, shows_value)

class Button_Element(UI_Element):
    def __init__(self, text, hitbox_size, position, text_position=1, hitbox_color=(255, 0, 0), hitbox_border=True, gradient=True, \
    startcolor=(200, 200, 200, 255), endcolor=(100, 100, 100, 255), gradient_type=0, hitbox_image=None, text_color=(255, 255, 255), \
    shows_value=True):
        super().__init__(text, hitbox_size, position, hitbox_color, hitbox_border, gradient, startcolor, endcolor, gradient_type, \
        hitbox_image, text_color, shows_value)
