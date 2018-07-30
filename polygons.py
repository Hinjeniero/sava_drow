import pygame, gradients 

__all__ = ["Circle", "Rectangle"]

class Polygon(pygame.sprite.Sprite):
    """Superclass polygon. Subclasses are Rectangle and Circle.
    This class consists of a basic pygame polygon that inherits from 
    pygame.Sprite that has a surface associated.

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
    def __init__(self, position, size,\
                surf_image=None, surf_color=(255, 0, 0, 255),\
                border=True, border_size=2, border_color=(255, 255, 255, 255),\
                use_gradient=True, start_color=(200, 200, 200, 255), end_color=(100, 100, 100, 255), gradient_type=0):
        self.image=None
        self.rect=None

class Circle(Polygon):
    def __init__(self, position, size,\
                surf_image=None, surf_color=(255, 0, 0),\
                border=True, border_size=2, border_color=(255,255,255),\
                use_gradient=True, start_color=(200, 200, 200, 255), end_color=(100, 100, 100, 255), gradient_type=0):
        #Hierarchy from sprite
        super().__init__(position, size, surf_color, surf_image, border, border_size, border_color, use_gradient, start_color, end_color, gradient_type)

        self.radius = size//2
        self.center_position = tuple([x+self.radius for x in position]) #Under the assumption that it's a square
        self.image = Circle.generate_surface(size, surf_image, surf_color, use_gradient, start_color, end_color, gradient_type, border, border_size, border_color)
        self.rect = pygame.Rect(position, self.image.get_size()) #Position + size
    
    @staticmethod
    def generate_surface (surf_size, radius, surf_color, use_gradient, start_color, end_color, border, border_size, border_color):
        surf = pygame.Surface(surf_size)
        if use_gradient: surf = gradients.radial(radius, start_color, end_color) 
        else: pygame.draw.circle(surf, surf_color, (radius, radius), radius, 0)
        if border: pygame.draw.circle(surf, border_color,(radius, radius), radius, border_size)
        return surf

class Rectangle(Polygon):
    def __init__(self, position, size,\
                surf_image=None, surf_color=(255, 0, 0),\
                border=True, border_size=2, border_color=(255,255,255),\
                use_gradient=True, start_color=(200, 200, 200, 255), end_color=(100, 100, 100, 255), gradient_type=0):
        #Hierarchy from polygon
        super().__init__(position, size, surf_color, surf_image, border, border_size, border_color, use_gradient, start_color, end_color, gradient_type)

        self.image = Rectangle.generate_surface(size, surf_image, surf_color, use_gradient, start_color, end_color, gradient_type, border, border_size, border_color)
        self.rect = pygame.Rect(position, self.image.get_size()) #Position + size

    @staticmethod
    def generate_surface(surf_size, image, surf_color, use_gradient, start_color, end_color, gradient_type, border, border_size, border_color):
        if image: #Texture checking
            surf = pygame.transform.scale(pygame.image.load(image).convert_alpha(), surf_size)
            if border: border = pygame.mask.from_surface(surf, 200) #IF image needs a border, mask. Not using it right now TODO
        else:
            surf = pygame.Surface(surf_size)
            if use_gradient: surf = gradients.vertical(surf_size, start_color, end_color) if gradient_type == 0 else gradients.horizontal(surf_size, start_color, end_color) #Checking if gradient and type of gradient
            else: surf.fill(surf_color)
            if border and border_size is not 0: pygame.draw.rect(surf, border_color,(0,0)+surf_size, border_size) #Drawing the border in the surface, dont want no existant borders
        return surf