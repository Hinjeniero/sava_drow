import pygame, gradients
from polygons import Rectangle, Circle
from resizer import Resizer

#Graphical element, automatic creation of a menu's elements
class UI_Element(pygame.sprite.Sprite): 
    def __init__(self, size, abs_position, color=(255, 0, 0), border=True, border_size=2, border_color=(255, 255, 255),\
    gradient=True, startcolor=(200, 200, 200, 255), endcolor=(100, 100, 100, 255), gradient_type=0, image=None):
        #Staaaaaartiiiiiiiiiing
        #self.init_values = locals() #Just in case, not sure if it can be used as this. Want to save the args and kwargs
        super.__init__(self)
        self.hitbox = self.create_surface(size, color, border, gradient, startcolor, endcolor, gradient_type, image, border_size, border_color)
        self.image = self.hitbox.copy()
        self.rect = pygame.Rect(absolute_position, self.image.get_size()) #Position + size

    #THIS ONLY CREATES THE BASIC HITBOX, WITHOUT SLIDER NOR TEXT!
    def create_surface(self, size, color, border, gradient, startcolor, endcolor, gradient_type, image, border_size, border_color):
        if image:
            surf = pygame.transform.scale(pygame.image.load(image).convert_alpha(), size)
            if border:
                border = pygame.mask.from_surface(surf, 200) #Not using it right now TODO
        else:
            surf = pygame.Surface(size)
            if gradient:
                if gradient_type is 0: #vertical
                    surf = gradients.vertical(size, startcolor, endcolor)
                else: #horizontal
                    surf = gradients.horizontal(size, startcolor, endcolor)
            else:
                surf.fill(color)
            if border and border_size is not 0: #Dont want no existant borders
                pygame.draw.rect(surf, border_color, size+(0,0), border_size) #Drawing the border in the surface
        #In this point, the only thing left is the text
        return surf

    def draw(self, surface):
        pass

class Slider (UI_Element):
    def __init__(self, text, font, max_font_size, size, abs_position, text_position=0, color=(255, 0, 0), border=True, border_size=2, border_color=(255, 255, 255),\ 
    gradient=True, startcolor=(200, 200, 200, 255), endcolor=(100, 100, 100, 255), gradient_type=0, image=None, text_color=(255, 255, 255), shows_value=True):
        #Staaaaaartiiiiiiiiiing
        super().__init__(hsize, absolute_position, color, border, border_size, border_color, gradient, startcolor, endcolor, gradient_type, mage)
        self.add_text(self.image, text, text_color, text_position, font, max_font_size, shows_value)

    def add_text(self, surface, text, text_color, text_position, font, max_font_size, shows_value):
        size = Resizer.max_font_size(text, self.rect.size, font, max_font_size)
        font = pygame.font.Font(font, size)
        text_surf = font.render(text, True, text_color)
        y_pos = (self.rect.height/2)-(text_surf.get_height()/2)
        if text_position is 1: #Aligned left
            surface.blit(text_surf, (0, y_pos))
        elif text_position is 2: #Aligned at the right
            surface.blit(text_surf, (self.rect.width - text_surf.get_width(), y_pos))
        else: #Case 0 (centered), and all the other ones, in case the user is trying to fuck us
            surface.blit(text_surf, ((self.rect.width/2) - (text_surf.get_width()/2), y_pos))

class Button (UI_Element):
    def __init__(self, text, font, max_font_size, size, abs_position, color=(255, 0, 0), border=True, border_size=2, border_color=(255, 255, 255),\ 
    gradient=True, startcolor=(200, 200, 200, 255), endcolor=(100, 100, 100, 255), gradient_type=0, image=None, text_color=(255, 255, 255), shows_value=True,\
    slider_type=0, slider_color=(0, 255, 0), slider_gradient=False, slider_startcolor=(0, 0, 0, 255), slider_endcolor=(255, 255, 255, 255), slider_border=True,\ slider_border_color=(0,0,0), slider_border_size=2):
        #Staaaaaartiiiiiiiiiing
        super().__init__(size, absolute_position, color, border, border_size, border_color, gradient, startcolor, endcolor, gradient_type, image)
        self.add_text(self.image, text, text_color, text_position, font, max_font_size, shows_value)
        self.add_slider(self.image, slider_color, slider_gradient, slider_startcolor, slider_endcolor, slider_border, slider_border_color, slider_border_size)

    def add_text (self, surface, text, text_color, text_position, font, font_size, shows_value):
        size = Resizer.max_font_size(text, self.rect.size, font, font_size)//2
        font = pygame.font.Font(font, size)
        text_surf = font.render(text, True, text_color)
        y_pos = (self.rect.height/2)-(text_surf.get_height()/2)
        if text_position is 1: #Aligned left
            surface.blit(text_surf, (0, y_pos))
        elif text_position is 2: #Aligned at the right
            surface.blit(text_surf, (self.rect.width - text_surf.get_width(), y_pos))
        else: #Case 0 (centered), and all the other ones, in case the user is trying to fuck us
            surface.blit(text_surf, ((self.rect.width/2) - (text_surf.get_width()/2), y_pos))

    def add_slider (self, surface, slider_color, slider_gradient, startcolor, endcolor, slider_border, slider_border_color, slider_border_size):
        radius=self.rect.get_height//2
        center_position = tuple()
        if slider_gradient:
            slider_surf = gradients.radial(radius, startcolor, endcolor)
        else:
            slider_surf = pygame.Surface(radius, radius)
            pygame.draw.circle(slider_surf, slider_color, (0,0), radius, 0)
        if slider_border:
            pygame.draw.circle(slider_surf, slider_border_color, ,radius, slider_border_size)

    def set_slider_position(self, new_position):
        pass