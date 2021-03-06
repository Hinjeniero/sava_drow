"""--------------------------------------------
polygon module. Contains basic polygons that inherit from Sprite.
Have the following classes, inheriting represented by tabs:
    Polygon
        ↑Circle
        ↑Rectangle
--------------------------------------------"""

__all__ = ['Circle', 'Rectangle']
__version__ = '1.0'
__author__ = 'David Flaity Pardo'

import pygame
from obj.utilities.utility_box import UtilityBox
from obj.sprite import MultiSprite, Sprite
from obj.utilities.colors import RED

class Polygon(MultiSprite):
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
        color: Background color of the polygon if gradient and image are false. Default is solid red.
        texture: Texture to use in the surface. It's a loaded image. Default is None.
        border: True if the polygon has a border. Default is True.
        border_size: Width of the border in pixels. Default is 2 pixels.
        border_color: Color of the border. Default is solid white.
        gradient: True if the polygon color is a gradient. Default is True.
        start_color: Starting color of the gradient. Default is gray.
        end_color: Ending color of the gradient. Default is dark gray.
        gradient_type: Orientation of the gradient, 0 for vertical, 1 or whatever for horizontal. Default is 0 (Vertical)
    """
    euclidean_distances = UtilityBox.EUCLIDEAN_DISTANCES #LUT to store the euclidean distances. Useful in the circles hitbox checking
    
    def __init__(self, _id, position, size, canvas_size, **params):
        """Polygon constructor."""            
        super().__init__(_id, position, size, canvas_size, **params)

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

class Circle(Polygon):
    """Circle class, inherits from polygon.
    Adds a radius and center attributes. Also has collision methods based on euclidean distances."""

    def __init__(self, id_, position, size, canvas_size, active_color=RED, **params):
        """Circle constructor.
        Args:
            id_ (str):  Identifier of the Sprite.
            position (:tuple: int,int): Position of the Sprite in the screen. In pixels.
            size (:tuple: int,int):     Size of the Sprite in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display. In pixels.
            active_color (tuple->(int, int, int, int), default=RED):    Default color of the overlay when this element is active.    
            params (:dict:):  Dict of keywords and values as parameters to create the self.image attribute.
                                    Variety going from fill_color and use_gradient to text_only."""
        params['shape'] = 'circle'
        super().__init__(id_, position, size, canvas_size, **params)
        self.radius = min(x for x in size)//2
        self.center = self.rect.center
        self.overlay = Sprite.generate_overlay(self.image, active_color)
    
    def set_size(self, size, update_rects=True):
        """Changes the size of the Circle. Updates the radius and center attributes.
        Args:
            update_rects (boolean, default:True):   Flag. If its true, the real rect attributes will be updated after the input position.
            size (:obj: pygame.Rect||:tuple: int,int):  New size of the Sprite. In pixels.
        """
        super().set_size(size, update_rects)
        self.radius = min(x for x in size)//2
        self.center = self.rect.center
    
    def set_position(self, position, update_rects=True):
        """Changes the position of the Sprite. Updates rect and real_rect.
        Args:
            position (:obj: pygame.Rect||:tuple: int,int): New position of the Sprite. In pixels.
            update_rects (boolean, default:True):   Flag. If its true, the real rect attributes will be updated after the input position.
        """
        super().set_position(position, update_rects=update_rects)
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

class Circumference(Circle):
    """Circumference class, inherits from Circle.
    Draws only the border of a Circle as an image."""

    def __init__(self, id_, position, size, canvas_size, active_color=RED, **params):
        """Circumference constructor.
        Args:
            id_ (str):  Identifier of the Sprite.
            position (:tuple: int,int): Position of the Sprite in the screen. In pixels.
            size (:tuple: int,int):     Size of the Sprite in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display. In pixels.
            active_color (tuple->(int, int, int, int), default=RED):    Default color of the overlay when this element is active.    
            params (:dict:):  Dict of keywords and values as parameters to create the self.image attribute.
                                    Variety going from fill_color and use_gradient to text_only."""
        params['transparent'] = True
        params['border'] = True
        super().__init__(id_, position, size, canvas_size, active_color=active_color, **params)
        self.width = UtilityBox.get_circumference_width(self.image)

class Rectangle(Polygon):
    """Rectangle class, inherits from Polygon."""

    def __init__(self, _id, position, size, canvas_size, **params):
        """Rectangle constructor.
        Args:
            id_ (str):  Identifier of the Sprite.
            position (:tuple: int,int): Position of the Sprite in the screen. In pixels.
            size (:tuple: int,int):     Size of the Sprite in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display. In pixels.
            params (:dict:):  Dict of keywords and values as parameters to create the self.image attribute.
                                    Variety going from fill_color and use_gradient to text_only."""
        params['shape'] = 'rectangle'
        super().__init__(_id, position, size, canvas_size, **params)