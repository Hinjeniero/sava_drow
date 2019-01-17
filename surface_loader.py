
import pygame
from synch_dict import Dictionary
from utility_box import UtilityBox
from decorators import time_it
from logger import Logger as LOG
from resizer import Resizer
#from memory_profiler import profile

IMAGE_FORMATS = ('.png', '.jpg', '.jpeg', 'bmp', '.gif', '.tga', '.pcx', '.tif', '.lbm', '.pbm', '.xbm')

#Decorator
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
    
class SurfaceLoader(object):
    SURFACES_LOADED = Dictionary()
    MAX_SIZE = 256
    MAX_SIZE_ENABLED = True
    
    @staticmethod
    def disable_max_size():
        SurfaceLoader.MAX_SIZE_ENABLED = False

    @staticmethod
    def enable_max_size():
        SurfaceLoader.MAX_SIZE_ENABLED = True

    @staticmethod
    def change_max_size(value):
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
        for image_path in UtilityBox.get_all_files(folder, *IMAGE_FORMATS):
            surfaces[image_path] = SurfaceLoader.get_surface(image_path)
        LOG.log('debug', 'Loaded ', len(surfaces), ' surface from ', folder)
        return surfaces
    
    @staticmethod
    @time_it
    def load_surfaces_keywords(folder, *keywords, strict=False):
        """Load all the images from a folder, and returns the matching surfaces.
        For each image, if its already loaded we will retrieve the surface from a LUT table,
        else we will load it and return it. 
        Only loads images. Accepted formats are png, jpg and bmp
        Args:
            folder(str):    Path of the folder that contains the surfacess (images) to be loaded."""
        surfaces = {}
        if not isinstance(keywords, tuple):
            keywords = (keywords,)
        for image_path in UtilityBox.get_all_files(folder, *IMAGE_FORMATS):
            if (not strict and any(kw.lower() in image_path.lower() for kw in keywords))\
            or (strict and all(kw.lower() in image_path.lower() for kw in keywords)):
                surfaces[image_path] = SurfaceLoader.get_surface(image_path)
        LOG.log('debug', 'Loaded ', len(surfaces), ' surfaces with the keywords ', keywords, ' in the folder ', folder)
        return surfaces

    @staticmethod
    def get_surfaces(*image_paths):
        surfaces = {}
        for image_path in image_paths:
            surfaces[image_path] = SurfaceLoader.get_surface(image_path)
        return surfaces

    @staticmethod     
    def get_surface(image_path):
        """Image_path can be an id too"""
        if image_path in SurfaceLoader.SURFACES_LOADED.keys():
            return SurfaceLoader.SURFACES_LOADED.get_item(image_path)
        else:
            surface = pygame.image.load(image_path).convert_alpha()
            if SurfaceLoader.MAX_SIZE_ENABLED and any(x>SurfaceLoader.MAX_SIZE for x in surface.get_size()):
                surface = Resizer.resize(surface, (SurfaceLoader.MAX_SIZE, SurfaceLoader.MAX_SIZE))
            SurfaceLoader.SURFACES_LOADED.add_item(image_path, surface)
            return surface
        