import pygame, gradients, numpy
from utility_box import UtilityBox
#from resizer import Resizer

#COLORS = pygame.color.THECOLORS
__all__ = ["Circle", "Rectangle"]
WHITE = pygame.Color("white")
RED = pygame.Color("red")
DARKGRAY = pygame.Color("darkgray")
LIGHTGRAY = pygame.Color("lightgray")

class Polygon(pygame.sprite.Sprite):
    """Superclass polygon. Subclasses are Rectangle and Circle.
    This class consists of a basic pygame polygon that inherits from 
    pygame.Sprite that has a surface associated.

    The strength of this class relies on the automatic generation and extensive flexibility
    due to all the optional parameters in the generation of the element.
    The basic generate_surface of the superclass generates a rectangle. Any other polygon
    should have that method overloaded.
    All colors have a format of a tuple of 4 values of the RGBA form.
    
    Class attributes:
        euclidean_distances: LUT that contains the possible euclidean distances according to 2 position axis.
    Instance attributes:
        position: Position that this surface will have on the destination surface if it's drawn.
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
    euclidean_distances = UtilityBox.EUCLIDEAN_DISTANCES #LUT to store the euclidean distances. Useful in the circles hitbox checking
    
    def __init__(self, position, size,\
                surf_image=None, surf_color=RED,\
                border=True, border_size=2, border_color=WHITE,\
                use_gradient=True, start_color=LIGHTGRAY, end_color=DARKGRAY, gradient_type=0):
        super().__init__()
        self.image  = None
        self.rect   = None
        self.mask   = None

    def collidepoint(self, point):
        '''Overlay of rect.collidepoint of the sprite. The main use of this function
        is to be overwritten in the case that we want more specific collision with the
        different possible subclasses.
        
        Args:
            point: Position of the point that could be colliding with this sprite.
                Can be a pygame.Rect or a tuple of 2 elements (position x,y)
        
        Returns:
            True if the point collides with the sprite.
            False otherwise.
        
        Raises:
            TypeError: The parameter point format is not correct. Use a tuple or 
                    pygame.Rect instead.'''
        if type(point) is pygame.Rect:
            return self.rect.collidepoint((point.x, point.y))
        elif type(point) is tuple:
            return self.rect.collidepoint(point)
        else:
            raise TypeError("CollidePoint must receive a pygame.Rect or a tuple containing the point coordinates.")

    def update_mask(self):
        self.mask = pygame.mask.from_surface(self.image)

class Circle(Polygon):
    '''ou shit'''
    def __init__(self, position, size,\
                surf_image=None, surf_color=RED,\
                border=True, border_size=2, border_color=WHITE,\
                use_gradient=True, start_color=LIGHTGRAY, end_color=DARKGRAY, gradient_type=0):
        #Hierarchy from sprite
        super().__init__(position, size, surf_color, surf_image, border, border_size, border_color, use_gradient, start_color, end_color, gradient_type)

        self.radius = size[0]//2 if type(size) is tuple else size//2
        self.image = Circle.generate_surface(size, self.radius, surf_color, use_gradient, start_color, end_color, border, border_size, border_color)[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = pygame.Rect(position, self.image.get_size()) #Position + size
        self.center = self.rect.center
    
    def collision(self, rect):
        """Returns if a collision has ocurred.
        Detects the collision getting the euclidean distance using
        the Polygon LUT table, and comparing with the radius.
        
        Args:
            rect: Position of the object that could be colliding with this sprite.
                Can be a pygame.Rect or a tuple of 2 elements (position x,y)
        
        Returns:
            True if the rect object collides with the sprite (distance < radius).
            False otherwise.
        
        Raises:
            TypeError: The parameter rect format is not correct. Use a tuple or 
                    pygame.Rect instead.
        """
        try:
            if type(rect) is pygame.Rect: 
                distance = tuple([abs(x-y) for x,y in zip(self.rect.size, rect.size)]) 
            elif type(rect) is tuple: 
                distance = tuple([abs(x-y) for x,y in zip(self.rect.size, rect)])
            else:
                raise TypeError("Should be a tuple w/ the position or a rect.")
            return Polygon.euclidean_distances[distance[0]][distance[1]] <= self.radius
        except IndexError:  #The distance was too big anyway, no collision.
            return False

    def collidepoint(self, point):
        pass

    @staticmethod
    def generate_surface (surf_size, radius, surf_color, use_gradient, start_color, end_color, border, border_size, border_color):
        """Generates a transparent surface with a circle drawn in it (According to parameters).
        
        Args:
            surf_size: Rect or tuple containing the dimensions of the surface (width, height)
            radius: Radius of the drawn circle
            surf_color: Solid color of the circle. 
            use_gradient: True if we want a circle w/ a gradient. Priority over solid colors.
            start_color: Starting color of the gradient. Only if gradient is True.
            end_color: Ending color of the gradient. Only if gradient is True.
            border: True if the circle has a border.
            border_size: Size of the border in pixels.
            border_color: Color of the border. RGBA/RGB format.
        
        Returns:
            A surface containing the circle.
        """
        surf = pygame.Surface(surf_size)
        if use_gradient: surf = gradients.radial(radius, start_color, end_color) 
        else: pygame.draw.circle(surf, surf_color, (radius, radius), radius, 0)
        if border: pygame.draw.circle(surf, border_color,(radius, radius), radius, border_size)
        if type(surf_size) is pygame.Rect:
            return surf, surf_size
        else:       #We need a coordinate to create a Rect, so if the size is a tuple, 0,0 will it be.
            return surf, pygame.Rect((0,0)+surf_size)

class Rectangle(Polygon):
    def __init__(self, position, size,\
                surf_image=None, surf_color=RED,\
                border=True, border_size=2, border_color=WHITE,\
                use_gradient=True, start_color=LIGHTGRAY, end_color=DARKGRAY, gradient_type=0):
        #Hierarchy from polygon
        super().__init__(position, size, surf_color, surf_image, border, border_size, border_color, use_gradient, start_color, end_color, gradient_type)
        self.image = Rectangle.generate_surface(size, surf_image, surf_color, use_gradient, start_color, end_color, gradient_type, border, border_size, border_color)[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = pygame.Rect(position, self.image.get_size()) #Position + size

    @staticmethod
    def generate_surface(surf_size, image, surf_color, use_gradient, start_color, end_color, gradient_type, border, border_size, border_color):
        """Generates a transparent surface with a rectangle drawn in it (According to parameters).
        The rectangle will leave no transparent pixels, taking up all the surface space.

        Args:
            surf_size: Rect or tuple containing the dimensions of the surface (width, height)
            image: Texture to draw in the surface. Priority over solid colors and gradients.
            surf_color: Solid color of the circle. Only if use_gradient is False.
            use_gradient: True if we want a circle w/ a gradient. 
            start_color: Starting color of the gradient. Only if gradient is True.
            end_color: Ending color of the gradient. Only if gradient is True.
            border: True if the circle has a border.
            border_size: Size of the border in pixels.
            border_color: Color of the border. RGBA/RGB format.
        
        Returns:
            A surface containing the Rectangle.
        #surf = Resizer.resize_same_aspect_ratio(pygame.image.load(image).convert_alpha(), surf_size)
        #if border: border = pygame.mask.from_surface(surf, 200)         #If image needs a border, mask. Not using it right now TODO
        """
        surf_size   = tuple([int(x) for x in surf_size])
        if image:   surf = pygame.transform.smoothscale(pygame.image.load(image).convert_alpha(), surf_size)
        else:
            surf    = pygame.Surface(surf_size)
            if use_gradient:    surf = gradients.vertical(surf_size, start_color, end_color) if gradient_type == 0 else gradients.horizontal(surf_size, start_color, end_color) #Checking if gradient and type of gradient
            else:               surf.fill(surf_color)
            if border and border_size is not 0: pygame.draw.rect(surf, border_color,(0,0)+surf_size, border_size) #Drawing the border in the surface, dont want no existant borders
        
        if type(surf_size) is pygame.Rect:      return surf, surf_size
        else:                                   return surf, pygame.Rect((0,0)+surf_size)