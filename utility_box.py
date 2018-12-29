"""--------------------------------------------
utility_box module. All the methods are utilities that will prove
useful along the workspace. Their utility is miscellaneous.
They aren't necessarily related to one common scope. 
Have the following classes:
    Resizer
--------------------------------------------"""
__all__ = ['UtilityBox']
__version__ = '0.1'
__author__ = 'David Flaity Pardo'

#Python libraries
import numpy
import math
import time
import pygame
import gradients
import random 
#External libraries
from PAdLib import draw as Drawing
#Selfmade libraries
from colors import WHITE, RED, BLACK
from decorators import time_it
from resizer import Resizer

@time_it
def euclidean_generator(size=300): #100 will be plenty in our case
    """Creates a LUT table of euclidean distances of a square size (i*i) between points.
    The points themselves are tuple with two ints. In short, two dimensions/axises.
    The euclidean distances are floats. (Euclidean = Square root(distance_x_axis^2 + distance_y_axis^2)).
    Args:
        size (int, default=300):    Maximum size of an axis. 
                                    (If the size is 100, euclidean distances are processed for points going 0->100).
    returns:
        (:obj: numpy.matrix): Matrix of size*size that contains the euclidean distances.
    """
    matrix = numpy.empty([size+1, size+1])
    for x in range (0, size+1):
        for y in range (x, size+1):
            euclidean = math.sqrt(x*x + y*y)
            matrix[x][y] = euclidean
            matrix[y][x] = euclidean
    return matrix

def generate_mouse_sprite(size=(2, 2)):
    """Generates a decoy sprite with a very small size, to simulate collisions with the mouse itself.
    Args:
        size (:tuple: int, int):    Size of the decoy sprite in pixels. Big sizes are discouraged.
    Returns:
        (:obj: pygame.sprite.Sprite): A sprite with the position related with the current mouse placement."""
    mouse_sprite = pygame.sprite.Sprite()           #Creates the associated sprite.
    mouse_sprite.image = pygame.Surface(size)       #Creating surface of mouse sprite
    mouse_sprite.image.fill(BLACK)                  #Filling surface with BLACK solid color
    mouse_sprite.rect = pygame.Rect((0,0), size)    #Decoy sprite to check collision with mouse
    mouse_sprite.mask = pygame.mask.from_surface(mouse_sprite.image)  #Creating the mask to check collisions with masks
    return mouse_sprite      

class UtilityBox (object):
    """UtilityBox class.
    General class Attributes:
        MOUSE_SPRITE (:obj: pygame.sprite.Sprite):  Small sprite to simulate mouse collisions.
        EUCLIDEAN_DISTANCES (:obj: numpy.matrix):   LUT table of euclidean distances of two dimensions points.
    """
    MOUSE_SPRITE        = generate_mouse_sprite()
    EUCLIDEAN_DISTANCES = euclidean_generator()

    @staticmethod
    def draw_hitboxes(surface, *sprites, color=RED, width=2):
        """Draw a squared-shaped border surrounding the input sprites.
        Args:
            surface (:obj: pygame.Surface): Surface to draw the hitboxes.
            *sprites (:obj: pygame.sprite.Sprite):  The sprites that will be detected 
                                                    to draw the surrounding square. Separated by commas.
            color (:tuple: int, int, int, default=RED): Color of the drawn border.
            width (int):    Width of the border.
        Raises:
            AttributeError: If there is an input element that is not of the pygame.sprite.Sprite class."""
        if isinstance(sprites, list, tuple): 
            for sprite in sprites: 
                pygame.draw.rect(surface, color, sprite.rect, width)
        else:   
            raise AttributeError("Bad input sprite")

    @staticmethod
    def get_mouse_sprite():
        """Returns:
            (:obj: pygame.sprite.Sprite):   A small sprite positioned in the current mouse position.
                                            Useful for"""
        UtilityBox.MOUSE_SPRITE.rect.topleft = pygame.mouse.get_pos()
        return UtilityBox.MOUSE_SPRITE

    @staticmethod
    def random_rgb_color(*excluded_colors, start=0, end=255):
        """Generates a random rgb color.
        Args:
            *excluded_colors (:tuple: int, int, int):   The RGB colors that are banned. 
                                                        Those cannot be returned as a result.
                                                        Separated by commas.
            start (int, default=0): Start of the interval for each RGB channel. Delimits the choice.    
            end (int, default=255): End of the interval for each RGB channel. Delimits the choice.
        Returns:
            (:tuple: int, int, int):    Color in RGB format (3 channels).
        """
        rand_color = (random.randint(start, end), random.randint(start, end), random.randint(start, end))
        while any(rand_color in excluded_color for excluded_color in excluded_colors):
            rand_color = (random.randint(start, end), random.randint(start, end), random.randint(start, end))
        return rand_color

    @staticmethod
    def draw_fps(surface, clock, font=None, size=(50, 50), color=WHITE, position=(50, 150)):
        """Draws the current number of fps (frames per second) in a surface.
        All the arguments have defaults with basic types because this method GOTTA GO FAST.
        Args:
            surface (:obj: pygame.Surface): Surface to draw the fps.
            clock (:obj: pygame.clock): Clock of the system.
            font (:obj: pygame.font, default=None): Font used to render the fps number.
            size (:tuple: int, int, default=(50, 50)):  Size of the fps drawing. In pixels
            color (:tuple: int, int, int, default=WHITE):   Color of the fps text.
            position (:tuple: int, int, default=(50, 50)):  Position of the fps on the surface. In pixels.
        """ 
        fnt = pygame.font.Font(font, 60)
        frames = fnt.render(str(int(clock.get_fps())), True, color)
        surface.blit(frames, position)

    @staticmethod
    def join_dicts(dict_to_add_keys, dict_to_search_keys):
        """Modified method of the 'update' that every dict has.
        Adds to the first dictionary the keys and associated items 
        of the second input dictionary ONLY if the first dict don't have them.
        Args:
            dict_to_add_keys (:dict:):  Dict that will gain keys from the second dict.
            dict_to_search_keys (:dict:):   Dict that will insert keys into the first dict.
        """
        for key in dict_to_search_keys.keys(): 
            key = key.lower().replace(" ", "_")
            if key not in dict_to_add_keys: 
                dict_to_add_keys[key] = dict_to_search_keys[key]

    @staticmethod
    def rotate(sprite, angle, iterations, offset=0, include_original=False):
        """Generates a list with the input sprite image rotated a fixated number of times,
        each rotation contained in another sprite.
        Args:
            sprite (:obj: pygame.sprite.Sprite):    Input sprite whose image we want to rotate.
            angle (int||float): Angle that will be added to each rotation (On top of previous iterations).
            iteration (int):    Number of times that the image will be rotated.
            offset (int, default=0):    Initial angle added to the first rotation/iteration.
            include_original (boolean, default=False):  True if we include the original input sprite in the result.
        Returns:
            (:list:):   List with all the transformed sprites.
        """
        #TODO implement difference between sprite and surface, to make it a valid method for both
        sprites         = [sprite] 
        orig_surface    = sprite.image
        orig_rect       = sprite.rect
        curr_angle      = angle+offset
        for _ in range (0, iterations):
            surf = pygame.transform.rotate(orig_surface, curr_angle)
            rect = surf.get_rect()
            rect.center = orig_rect.center
            sprite = pygame.sprite.Sprite()
            sprite.image, sprite.rect = surf, rect
            sprites.append(sprite)
            curr_angle += angle
        return sprites[1:] if not include_original else sprites

    @staticmethod
    def draw_grid(surface, rows, columns, color=RED):
        """Draws a grid of lines over a surface. Kinda like a table.
        Args:
            surface (:obj: pygame.Surface): Surface to draw the grid in.
            rows (int): Number of rows of the grid.
            columns (int): Number of columns of the grid.
            color (:tuple: int, int, int, default=RED): Color of the grid borders.
        """
        for i in range(0, surface.get_height(), surface.get_height()//rows):    pygame.draw.line(surface, color, (0, i), (surface.get_width(), i))
        for i in range(0, surface.get_width(), surface.get_width()//columns):   pygame.draw.line(surface, color, (i, 0), (i, surface.get_height()))

    @staticmethod
    def add_transparency(surface, *excluded_colors, use_color=None):
        """Fills a surface with a color and sets it as the colorkey, thus adding an alpha layer.
        After this the surface will be COMPLETELY TRANSPARENT, won't have any of the previous shapes/drawings.
        Args:
            surface (:obj: pygame.Surface): Surface to add transparency to.
            *excluded_colors (:tuple: int, int, int):   The RGB colors that are banned. 
                                                        Those cannot be used as a colorkey.
                                                        Separated by commas.
            use_color (:tuple: int, int, int, default=None):    Color to use when filling the surface
                                                                and setting the colorkey. Only used if it's not None.
        """
        colorkey = UtilityBox.random_rgb_color(*excluded_colors) if not use_color else use_color
        surface.fill(colorkey)
        surface.set_colorkey(colorkey)

    @staticmethod
    def bezier_surface(*points, color=RED, width=3, steps=20):
        """Creates a surface with a bezier curve drawn on it.
        Args:
            *points (:tuple: int, int): All the points that the bezier curve will follow.
            color (:tuple: int, int, int, default=RED): Color of the bezier curve.
            width (int):    Width of the bezier curve. In pixels.
            steps (int):    Steps of the bezier curve. Will be smoother the higher the steps.
        Returns:
            (:obj: pygame.Surface): Surface with the generated bezier curve drawn on it.
        """
        min_axises = (min(point[0] for point in points), min(point[1] for point in points))
        max_axises = (max(point[0] for point in points), max(point[1] for point in points))
        size = tuple(abs(max_axis-min_axis) for max_axis, min_axis in zip(max_axises, min_axises))
        for point in points: #Modyfing points to shift to occupy only the surface
            point = tuple(point_axis-min_axis for point_axis, min_axis in zip(point, min_axises)) #Adjusting to the surface
        surface = pygame.Surface(size)
        UtilityBox.add_transparency(surface, color) #Making the surface transparent
        UtilityBox.draw_bezier(surface, *points, color=color, width=width, steps=steps)
        return surface

    @staticmethod
    def draw_bezier(surface, *points, color=RED, width=3, steps=20):
        """Draws a bezier curve on a surface.
        Args:
            surface (:obj: pygame.Surface): Surface in which the curve will be drawn on.
            *points (:tuple: int, int): All the points that the bezier curve will follow.
            color (:tuple: int, int, int, default=RED): Color of the bezier curve.
            width (int):    Width of the bezier curve. In pixels.
            steps (int):    Steps of the bezier curve. Will be smoother the higher the steps.
        """
        if any(len(point)>2 for point in points): raise TypeError("The tuples must have 2 dimensions")
        point_list = tuple(point for point in points)
        if len(points)>1:   Drawing.bezier(surface, color, point_list, steps, width)
