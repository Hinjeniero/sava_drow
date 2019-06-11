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
import timeit
import pygame
import random
import requests
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout
from os import listdir
from os.path import isfile, join, dirname
from wrapt import synchronized
#External libraries
from external.PAdLib import draw as Drawing
#Selfmade libraries
from obj.utilities.colors import WHITE, RED, BLACK
from obj.utilities.decorators import time_it
from obj.utilities.resizer import Resizer
from obj.utilities.logger import Logger as LOG
from settings import PATHS, STRINGS

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
    #yes = [2]  #Test of access times
    #timeit.timeit('"-".join(math.sqrt(240*240 + 255*255))', number=1)
    #print(timeit.timeit(lambda: math.sqrt(240*240 + 255*255), number=1))
    #print(timeit.timeit(lambda: yes[0], number=1))
    return matrix

def test():
    euclidean = math.sqrt(240*240 + 255*255)
    return euclidean

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
    mouse_sprite.mask = pygame.mask.Mask(size)      #Creating the mask to check collisions with masks
    mouse_sprite.mask.fill()                        #Filling the mask with ones.
    return mouse_sprite      

class UtilityBox (object):
    """UtilityBox class.
    General class Attributes:
        MOUSE_SPRITE (:obj: pygame.sprite.Sprite):  Small sprite to simulate mouse collisions.
        EUCLIDEAN_DISTANCES (:obj: numpy.matrix):   LUT table of euclidean distances of two dimensions points.
    """
    MOUSE_SPRITE        = generate_mouse_sprite()
    EUCLIDEAN_DISTANCES = euclidean_generator()
    CHANNEL_SOUND_INDEX = 0
    
    @synchronized
    @staticmethod
    def get_sound_channel():
        if UtilityBox.CHANNEL_SOUND_INDEX is pygame.mixer.get_num_channels():
            pygame.mixer.set_num_channels(pygame.mixer.get_num_channels()+1)
        channel = pygame.mixer.Channel(UtilityBox.CHANNEL_SOUND_INDEX)
        UtilityBox.CHANNEL_SOUND_INDEX += 1
        return channel
    
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
        return frames
    
    @staticmethod
    def generate_fps(clock, font=None, size=(50, 50), color=WHITE):
        """Generates a font surface with the current number of fps (frames per second).
        All the arguments have defaults with basic types because this method GOTTA GO FAST.
        Args:
            surface (:obj: pygame.Surface): Surface to draw the fps.
            clock (:obj: pygame.clock): Clock of the system.
            font (:obj: pygame.font, default=None): Font used to render the fps number.
            size (:tuple: int, int, default=(50, 50)):  Size of the fps drawing. In pixels
            color (:tuple: int, int, int, default=WHITE):   Color of the fps text.
            position (:tuple: int, int, default=(50, 50)):  Position of the fps on the surface. In pixels.
        """
        fnt = pygame.font.Font(font, 50)
        return fnt.render(str(int(clock.get_fps())), True, color)

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
    @time_it
    def rotate(sprite, angle, iterations, offset=0, include_original=False, name=''):
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
        LOG.log('INFO', 'Rotating sprite ', name)
        sprites         = [sprite] 
        orig_surface    = sprite.image
        orig_rect       = sprite.rect
        curr_angle      = angle+offset
        for _ in range (0, iterations):
            surf = pygame.transform.rotozoom(orig_surface, curr_angle, 1)
            #surf = pygame.transform.smoothscale(surf, orig_rect.size)
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
        for i in range(0, surface.get_height(), surface.get_height()//rows):    
            pygame.draw.line(surface, color, (0, i), (surface.get_width(), i))
        for i in range(0, surface.get_width(), surface.get_width()//columns):   
            pygame.draw.line(surface, color, (i, 0), (i, surface.get_height()))

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

    @staticmethod
    def round_borders(surface):
        pass

    @staticmethod
    def get_all_files(root_folder, *extensions):
        result = []
        files = [root_folder+'\\'+f for f in listdir(root_folder) if isfile(join(root_folder, f))]
        for file in files:
            if file.lower().endswith(tuple(extensions)):
                result.append(file)
        return result

    @staticmethod
    def get_filtered_files(root_folder, extensions, keywords, strict=False):
        result = []
        unfiltered_files = UtilityBox.get_all_files(root_folder, *extensions)
        for file_path in unfiltered_files:
            if (not strict and any(kw.lower() in file_path.lower() for kw in keywords))\
            or (strict and all(kw.lower() in file_path.lower() for kw in keywords)):
                result.append(file_path)
        return result
    
    @staticmethod
    def size_position_generator(ammount_elements, width, inter_element_space, initial_offset=0.05, final_offset=0):
        """Returns a generator thyat provides the values
        First value is the size. The rest of them are the positions.
        The final_offset is the same as the interelemental space. If you want 0 final offset, you have to compensate with a negative number."""
        size = (width, ((1-initial_offset-final_offset)/ammount_elements)-inter_element_space)
        yield size
        for index in range (0, ammount_elements):
            position = ((1-width)/2, initial_offset+(index*(size[1]+inter_element_space)))
            yield position

    @staticmethod
    def size_position_generator_no_adjustment(width, height, inter_element_space, initial_offset=0.05):
        """Returns a generator thyat provides the values
        First value is the size. The rest of them are the positions.
        The final_offset is the same as the interelemental space. If you want 0 final offset, you have to compensate with a negative number."""
        index = 1
        while True:
            position = ((1-width)/2, initial_offset+(index*(height+inter_element_space)))
            yield position
            index += 1

    @staticmethod
    def rainbow_gradient_generator(gradient, ammount_elements, transparency=255):
        """To generate the desired colors."""
        transparency = (transparency,)  #Converting to tuple to join in the yields
        start, end = gradient[0], gradient[1]
        step = tuple((end_-start_)//ammount_elements for end_, start_ in zip(end, start))
        start_gradient = start
        for i in range (1, ammount_elements+1):
            end_gradient = tuple(x + i*y for x, y in zip(start, step))
            yield (start_gradient+transparency, end_gradient+transparency)
            start_gradient = end_gradient

    @staticmethod
    def looped_rainbow_gradient_generator(gradient, ammount_elements_per_loop, transparency=255):
        """To generate the desired colors."""
        while True:
            loop_generator = UtilityBox.rainbow_gradient_generator(gradient, ammount_elements_per_loop, transparency)
            for _ in range(0, ammount_elements_per_loop):
                yield next(loop_generator)
            gradient = tuple(reversed(gradient))

    @staticmethod
    def convert_to_colorkey_alpha(surf, colorkey=pygame.color.Color("magenta")):
        newsurf = pygame.Surface(surf.get_size())
        newsurf.fill(colorkey)
        newsurf.blit(surf, (0, 0))
        newsurf.set_colorkey(colorkey)
        return newsurf

    @staticmethod
    def get_alike_colorkey(color, difference=3):
        """A difference of 1 is nto noticed by colorkey, and 2 is weird."""
        colorkey = []
        for channel in color:
            if channel < difference:
                colorkey.append(channel+difference)
                continue
            colorkey.append(channel-difference)
        return tuple(colorkey)

    @staticmethod
    def get_circumference_width(circumference_surf):
        mask = pygame.mask.from_surface(circumference_surf)
        x = circumference_surf.get_width()//2
        counter = 0
        while mask.get_at((x, counter)):
            counter += 1
        return counter

    @staticmethod
    @time_it
    def overlap_trace_texture(base_surf, top_surf, resize_mode='fill', resize_smooth=True, keep_aspect_ratio=True):
        """The params are used if the top_surf is a path that needs to be loaded.
        Topsurf can be a surface or a string"""
        if isinstance(top_surf, str):
            surf = pygame.image.load(top_surf)
            top_surf = Resizer.resize(surf, base_surf.get_size(), mode=resize_mode, smooth=resize_smooth, keep_aspect_ratio=keep_aspect_ratio)
        newsurf = pygame.Surface(base_surf.get_size())
        newsurf.fill((0, 0, 0))
        newsurf.set_colorkey((0, 0, 0))
        mask = pygame.mask.from_surface(base_surf)
        for x in range(0, newsurf.get_width()-1):
            for y in range(0, newsurf.get_height()-1):
                if mask.get_at((x, y)):
                    newsurf.set_at((x, y), top_surf.get_at((x, y)))
        return newsurf

    @staticmethod
    def line_number(text):
        """Returns the number of lines that a text must have based on it length"""
        return math.ceil(len(text)/STRINGS.CHARS_PER_LINE)

    @staticmethod
    def do_request(url, method='GET', params={}, data={}, headers={}, timeout=10.0, sleep_between_petitions=0, return_success_only=False, json_response=True):
        url = 'http:\\'+url if url[0] != 'h' else url
        start = time.time()
        try:
            while True:
                response = requests.request(method, url, params=params, data=data, headers=headers, timeout=timeout)
                if time.time()-start > timeout:
                    return False
                if return_success_only and response.status_code != 200:
                    continue
                if json_response:
                    return response.json()
                return response
        except ReadTimeout:
            return False
        except ConnectionError:
            raise ConnectionError

    @staticmethod
    def normalize_values(*values, start=0, end=255):
        results = []
        for value in values:
            results.append((value-min(start, end))/(max(start, end)-min(start, end)))
            if end < start:
                results[-1] = 1-results[-1]
        if len(values) == 1:
            return results[0]
        return tuple(results) 