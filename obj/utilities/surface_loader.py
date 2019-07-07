"""--------------------------------------------
surface_loader module. In here is all the logic related to the transformation
of surfaces and the related information of type pygame.Surface.
Have the following classes:
    ResizedSurface
    SurfaceLoader
--------------------------------------------"""

__all__ = ['ResizedSurface', 'SurfaceLoader']
__version__ = '1.0'
__author__ = 'David Flaity Pardo'

#Python libraries
import pygame
from wrapt import synchronized
#Selfmade libraries
from settings import EXTENSIONS
from obj.utilities.synch_dict import Dictionary
from obj.utilities.utility_box import UtilityBox
from obj.utilities.decorators import time_it
from obj.utilities.logger import Logger as LOG
from obj.utilities.resizer import Resizer
#from memory_profiler import profile

"""This one is a decorator."""
def no_size_limit(function):
    """Times the input function and prints the result on screen. 
    The time library is needed.
    Args:
        function (function):    Function whose execution will be timed.
        *args (:list: arg):     Input arguments of the function.
        **kwargs (:dict: kwarg):Input keyword arguments of the function.
    Returns:
        (any):  Returns whatever the function itself returns."""
    def wrapper(*args, **kwargs):
        SurfaceLoader.disable_max_size()
        result = function(*args, **kwargs)
        SurfaceLoader.enable_max_size()
        return result
    return wrapper

class ResizedSurface(object):
    """ResizedSurface class, with two parts:
    The first one, an object that holds a surface that has been resized, and various attributes
    that describe the way in what the resizing was done.
    
    The second one, container of static methods to load modified surfaces, with a LUT as well to not repeat the same
    data over and over.
    The key in said LUT is the hash that comes out of all the resizing attributes and the image path.
    """
    RESIZED_SURFACES_LOADED = Dictionary()  #LUT of images, saved in their resized state.
    def __init__(self, path, intended_size, resize_mode, smooth_resize, keep_aspect_ratio=True):
        """ResizedSurface constructor."""
        self.path = path
        self.intended_size = intended_size
        self.resize_mode = resize_mode
        self.smooth = smooth_resize
        self.keep_aspect_ratio = keep_aspect_ratio
        self.surface = None

    def set_surface(self, surface):
        """Sets a new surface to this instance."""
        self.surface = surface

    def __str__(self):
        return 'path: '+self.path+', intended size: '+str(self.intended_size)+', Resize mode: '+str(self.resize_mode)+\
                ', Resize smooth: '+str(self.smooth)+', keep_aspect_ratio: '+str(self.keep_aspect_ratio)+'-------------'

    def __hash__(self):
        return hash((self.path, self.intended_size, self.resize_mode, self.smooth, self.keep_aspect_ratio))

    @staticmethod
    def load_surfaces(folder, intended_size, resize_mode, resize_smooth, keep_aspect_ratio, *keywords, strict=False):
        """Loads all the images in a folder, resizes them, and returns a dictionary that contains them. Can use keywords"""
        if len(keywords) is 0 or None in keywords:
            paths = UtilityBox.get_all_files(folder, *EXTENSIONS.IMAGE_FORMATS)
        else:
            if not isinstance(keywords, tuple):
                keywords = (keywords,)
            paths = UtilityBox.get_filtered_files(folder, EXTENSIONS.IMAGE_FORMATS, keywords, strict=strict)
        return ResizedSurface.get_surfaces(intended_size, resize_mode, resize_smooth, keep_aspect_ratio, *paths)    

    @staticmethod
    def get_surfaces(intended_size, resize_mode, resize_smooth, keep_aspect_ratio, *paths):
        """Gets all the surfaces from the parameter paths."""
        surfaces = {}
        for path in paths:
            surfaces[path] = ResizedSurface.get_surface(path, intended_size, resize_mode,\
                            resize_smooth, keep_aspect_ratio)
        return surfaces

    @staticmethod
    def get_surface(path, intended_size, resize_mode='fit', resize_smooth=True, keep_aspect_ratio=True):
        """loads the image with the input path, resizes and returns it.L
        If it has been loaded before with the same resizing parameters, it is simply fetched from the LUT"""
        surface = ResizedSurface(path, intended_size, resize_mode, resize_smooth, keep_aspect_ratio=keep_aspect_ratio)
        hash_key = hash(surface)
        if hash_key in ResizedSurface.RESIZED_SURFACES_LOADED.keys():
            return ResizedSurface.RESIZED_SURFACES_LOADED.get_item(hash_key).surface
        else:
            orig_surf = SurfaceLoader.get_surface(path) #Getting the original file
            final_surf = Resizer.resize(orig_surf, intended_size, mode=resize_mode, smooth=resize_smooth,\
                                        keep_aspect_ratio=keep_aspect_ratio)
            surface.set_surface(final_surf)
            ResizedSurface.add_surface(surface)
            return final_surf

    # @staticmethod
    # def get_surface(path, intended_size, resize_mode='fit', resize_smooth=True, keep_aspect_ratio=True):
    #     """Same method as the one above, but this one aleawys loads the images, without using the LUT.
    #     Used for testing and comparison purposes"""
    #     surface = ResizedSurface(path, intended_size, resize_mode, resize_smooth, keep_aspect_ratio=keep_aspect_ratio)
    #     orig_surf = SurfaceLoader.get_surface(path) #Getting the original file
    #     final_surf = Resizer.resize(orig_surf, intended_size, mode=resize_mode, smooth=resize_smooth,\
    #                                 keep_aspect_ratio=keep_aspect_ratio)
    #     surface.set_surface(final_surf)
    #     ResizedSurface.add_surface(surface)
    #     return final_surf

    @staticmethod
    def add_surface(ResizedSurface):
        """Adds an item to the LUT."""
        ResizedSurface.RESIZED_SURFACES_LOADED.add_item(hash(ResizedSurface), ResizedSurface)

    @staticmethod
    def clear_lut():
        """Clears the LUT."""
        ResizedSurface.RESIZED_SURFACES_LOADED.clear()

class SurfaceLoader(object):
    """Loader of the original unresized/unmodified images/surfaces"""
    SURFACES_LOADED = Dictionary()  #LUT of images, saved in their original state.
    MAX_SIZE = 256  #Max size per axis that will be imposed when the flag max size is enabled.
    MAX_SIZE_ENABLED = True #Max size flag.
    MAX_SIZE_DISABLE_COUNT = 0  #Counter of methods that deactivated the flag. 

    @synchronized
    @staticmethod
    def disable_max_size():
        """Disables the size limit when loading and saving images in the LUT."""
        SurfaceLoader.MAX_SIZE_DISABLE_COUNT += 1
        SurfaceLoader.MAX_SIZE_ENABLED = False

    @synchronized
    @staticmethod
    def enable_max_size():
        """Enables the size limit when loading and saving images in the LUT.
        Saves memory allocated."""
        SurfaceLoader.MAX_SIZE_DISABLE_COUNT -= 1
        if SurfaceLoader.MAX_SIZE_DISABLE_COUNT is 0:
            SurfaceLoader.MAX_SIZE_ENABLED = True

    @staticmethod
    def change_max_size(value):
        """Changes the size limit when loading and saving images in the LUT."""
        SurfaceLoader.MAX_SIZE = value

    @staticmethod
    @time_it
    def load_surfaces(folder):
        """Load all the images from a folder, and returns the matching surfaces.
        For each image, if its already loaded we will retrieve the surface from a LUT table,
        else we will load it and return it. 
        Only loads images. Accepted formats are png, jpg and bmp
        Args:
            folder(str):    Path of the folder that contains the surfacess (images) to be loaded."""
        surfaces = {}
        for image_path in UtilityBox.get_all_files(folder, *EXTENSIONS.IMAGE_FORMATS):
            surfaces[image_path] = SurfaceLoader.get_surface(image_path)
        LOG.log('debug', 'Loaded ', len(surfaces), ' surface from ', folder)
        return surfaces
    
    @staticmethod
    @time_it
    def load_filtered_surfaces(folder, *keywords, strict=False):
        """Load all the images from a folder, and returns the matching surfaces.
        For each image, if its already loaded we will retrieve the surface from a LUT table,
        else we will load it and return it. 
        Only loads images. Accepted formats are png, jpg and bmp
        Args:
            folder(str):    Path of the folder that contains the surfacess (images) to be loaded."""
        surfaces = {}
        if not isinstance(keywords, tuple):
            keywords = (keywords,)
        paths = UtilityBox.get_filtered_files(folder, EXTENSIONS.IMAGE_FORMATS, keywords, strict=strict)
        for image_path in paths:
            surfaces[image_path] = SurfaceLoader.get_surface(image_path)
        LOG.log('debug', 'Loaded ', len(surfaces), ' surfaces with the keywords ', keywords, ' in the folder ', folder)
        return surfaces

    @staticmethod
    def get_surfaces(*image_paths):
        """Gets all the surfaces from the parameter paths."""
        surfaces = {}
        for image_path in image_paths:
            surfaces[image_path] = SurfaceLoader.get_surface(image_path)
        return surfaces

    @staticmethod
    def get_surface(image_path):
        """Loads the image with the input path, resizes and returns it.
        If the image has been loaded before, it is simply fetched from the LUT"""
        if image_path in SurfaceLoader.SURFACES_LOADED.keys():
            return SurfaceLoader.SURFACES_LOADED.get_item(image_path)
        else:
            surface = SurfaceLoader.load_image(image_path)# pygame.image.load(image_path).convert_alpha()
            if SurfaceLoader.MAX_SIZE_ENABLED and any(x>SurfaceLoader.MAX_SIZE for x in surface.get_size()):
                surface = Resizer.resize(surface, (SurfaceLoader.MAX_SIZE, SurfaceLoader.MAX_SIZE))
            SurfaceLoader.SURFACES_LOADED.add_item(image_path, surface)
            return surface

    # @staticmethod
    # def get_surface(image_path):
    #     """Image_path can be an id too. Same method as the one above, but this one aleawys loads the images, without using the LUT.
    #     Used for testing and comparison purposes"""
    #     surface = SurfaceLoader.load_image(image_path)# pygame.image.load(image_path).convert_alpha()
    #     if SurfaceLoader.MAX_SIZE_ENABLED and any(x>SurfaceLoader.MAX_SIZE for x in surface.get_size()):
    #         surface = Resizer.resize(surface, (SurfaceLoader.MAX_SIZE, SurfaceLoader.MAX_SIZE))
    #     SurfaceLoader.SURFACES_LOADED.add_item(image_path, surface)
    #     return surface
    
    @staticmethod
    @synchronized
    def load_image(image_path):
        """Loads directly an image from a path, without checking LUTS or anything else.
        Converts to alpha before returning it."""
        return pygame.image.load(image_path).convert_alpha()