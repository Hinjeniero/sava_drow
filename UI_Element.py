import pygame, gradients
from polygons import *
from resizer import Resizer
from pygame_test import PygameSuite

BLACK = pygame.Color("black")
WHITE = pygame.Color("white")
RED = pygame.Color("red")
GREEN = pygame.Color("green")
BLUE = pygame.Color("blue")
DARKGRAY = pygame.Color("darkgray")
LIGHTGRAY = pygame.Color("lightgray")

#Graphical element, automatic creation of a menu's elements
class UiElement(pygame.sprite.Sprite):
    """Superclass UI_Element. Subclasses are Button and Slider.
    This class consists of a set of basic polygons like circles or rectangles.

    The strength of this class relies on the automatic generation and extensive flexibility
    due to all the optional parameters in the generation of the element.
    The basic generate_surface of the superclass generates a rectangle. Any other polygon
    should have that method overloaded.
    All colors have a format of a tuple of 4 values of the RGBA form.
    Attributes:
        position: Position that this surface will have on the destination surface if it's drawed.
        size: Size of the surface containing the polygon, is a tuple (width, height).
        surf_color: Background color of the polygon if gradient and image are false. Default is solid red.
        surf_image: Texture to use in the surface. It's a loaded image. Default is None.
        border: True if the polygon has a border. Default is True.
        border_size: Width of the border in pixels. Default is 2 pixels.
        border_color: Color of the border. Default is solid white.
        use_gradient: True if the polygon color is a gradient. Default is True.
        start_color: Starting color of the gradient. Default is gray.
        end_color: Ending color of the gradient. Default is dark gray.
        gradient_type: Orientation of the gradient, 0 for vertical, 1 or whatever for horizontal. Default is 0 (Vertical)
    """
    def __init__(self, element_position, element_size,\
                surf_image=None, element_color=RED,\
                border=True, border_size=2, border_color=WHITE,\
                use_gradient=True, start_color=LIGHTGRAY, end_color=DARKGRAY, gradient_type=0):
        #Hierarchy from sprite
        super().__init__()
        self.hitbox = Rectangle.generate_surface(element_size, surf_image, element_color,\
                                use_gradient, start_color, end_color, gradient_type,\
                                border, border_size, border_color)
        self.image = self.hitbox.copy() 
        self.rect = pygame.Rect(element_position, self.image.get_size()) #Position + size
    
    def draw_text(self, surface, text, text_color, text_alignment, font, font_size):
        font = pygame.font.Font(font, font_size)
        text_surf = font.render(text, True, text_color)
        y_pos = (self.rect.height//2)-(text_surf.get_height()//2)
        #1 is left, 2 is right, 0 is centered
        x_pos = self.rect.width*0.02 if text_alignment is 1 else self.rect.width-text_surf.get_width() if text_alignment is 2 else (self.rect.width//2)-(text_surf.get_width()//2)
        surface.blit(text_surf, (x_pos, y_pos))
        return text_surf
        
    def draw(self, surface):
        pass

class Button (UiElement):
    def __init__(self, element_position, element_size, text, font_text, max_font_size,\
                surf_image=None, element_color=RED, text_alignment=0, text_color=WHITE,\
                border=True, border_size=2, border_color=WHITE,\
                use_gradient=True, start_color=LIGHTGRAY, end_color=DARKGRAY, gradient_type=0,\
                shows_value=True):
        #Initializing super class
        super().__init__(element_position, element_size, surf_image, element_color,\
                        border, border_size, border_color, use_gradient, start_color, end_color, gradient_type)
        fnt_size = Resizer.max_font_size(text, self.rect.size, max_font_size, font_text)
        self.text_surface = self.draw_text(self.image, text, text_color, text_alignment, font_text, fnt_size)
        self.speed = 5
        self.mask_color = WHITE
        self.transparency = 0
        self.transparency_speed = 15

    def update(self):
        self.rect.x += self.speed
        if self.rect.x < self.speed:    self.speed = -self.speed

        self.transparency += self.transparency_speed
        if self.transparency >= 255:    self.transparency_speed = -self.transparency_speed 

    def return_active_surface(self):
        overlay = pygame.Surface(self.rect.size).fill(self.mask_color)
        return self.image.copy().blit(overlay, (0,0))

class Slider (UiElement):
    def __init__(self, element_position, element_size, text, font_text, max_font_size,\
                surf_image=None, element_color=RED, text_alignment=1, text_color=WHITE,\
                border=True, border_size=2, border_color=WHITE,\
                use_gradient=True, start_color=LIGHTGRAY, end_color=DARKGRAY, gradient_type=0,\
                shows_value=True, slider_color=GREEN, slider_gradient=True, slider_startcolor=(255, 50, 50, 255), slider_endcolor=(100, 50, 50, 255),\
                slider_border=True, slider_border_color=BLACK, slider_border_size=2, slider_type=1):
        #Initializing super class
        super().__init__(element_position, element_size, surf_image, element_color,\
                        border, border_size, border_color, use_gradient, start_color, end_color, gradient_type)
        fnt_size = Resizer.max_font_size(text, self.rect.size, max_font_size, font_text)//2
        self.text_surface = self.draw_text(self.image, text, text_color, text_alignment, font_text, fnt_size)
        self.slider_surface = self.draw_slider(self.image, slider_color, slider_gradient, slider_startcolor, slider_endcolor, slider_border,\
                                            slider_border_color, slider_border_size, slider_type)

    #Adds the slider to the surface parameter, and returns the slider surface for further purposes
    def draw_slider (self, surface, slider_color, slider_gradient, start_color, end_color, slider_border, slider_border_color, slider_border_size, slider_type):
        radius = self.rect.height//2
        if slider_type < 2:
            slider_surf = Circle.generate_surface(self.rect.size, radius,\
                                                slider_color, slider_gradient, start_color, end_color,\
                                                slider_border, slider_border_size, slider_border_color)
            if slider_type is 1: #ellipse instead of circle
                slider_size = slider_surf.get_size()
                slider_surf = pygame.transform.scale(slider_surf, (slider_size[0]//3, slider_size[1])) #TODO get some type of ratio instead of just a third of the size
        else: #TODO rectangular one
            pass
        center_position = tuple([(self.rect.width-slider_surf.get_width())//2, 0]) #To adjust the offset error due to transforming the surface.
        surface.blit(slider_surf, tuple(center_position)) #Drawing the slider in the entire image surface
        return slider_surf

    #Position must be between 0 and 1
    #When we know in which form will the parameter be passed, we will implement this
    def set_slider_position(self, new_position):
        pass

if __name__ == "__main__":
    timeout = 20
    testsuite = PygameSuite(fps=144)
    slidie = Slider((50, 50), (100, 25), "test1.5", None, 200)
    slidou = Slider( (250, 50), (300, 25),"test1.5", None, 200)
    slede = Slider( (600, 50), (600, 25), "test1.5", None, 200)
    slada = Slider( (200, 100), (400, 50), "test1.5", None, 200, slider_type=0)
    buttkun = Button( (200, 200), (800, 50),"Shitty Button", None, 200)
    baton = Button((200, 300), (800, 400), "SUPER BUTTON", None, 200)
    print(type(baton))
    print(issubclass(type(baton), UiElement))
    #Adding elements
    testsuite.add_elements(slidou, slidie, slede, slada, buttkun, baton)
    testsuite.loop(seconds = timeout)