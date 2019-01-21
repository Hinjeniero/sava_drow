
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

class ResizedSurface(object):
    """Loader of the resized/modified images/surfaces"""
    RESIZED_SURFACES_LOADED = Dictionary()
    def __init__(self, path, intended_size, resize_mode, smooth_resize, keep_aspect_ratio=True):
        self.path = path
        self.intended_size = intended_size
        self.resize_mode = resize_mode
        self.smooth = smooth_resize
        self.keep_aspect_ratio = keep_aspect_ratio
        self.surface = None

    def set_surface(self, surface):
        self.surface = surface

    def __str__(self):
        return 'path: '+self.path+', intended size: '+str(self.intended_size)+', Resize mode: '+str(self.resize_mode)+\
                ', Resize smooth: '+str(self.smooth)+', keep_aspect_ratio: '+str(self.keep_aspect_ratio)+'-------------'

    def __hash__(self):
        return hash((self.path, self.intended_size, self.resize_mode, self.smooth, self.keep_aspect_ratio))

    @staticmethod
    def load_surfaces(folder, intended_size, resize_mode, resize_smooth, keep_aspect_ratio, *keywords, strict=False):
        """To load from a folder. Can use keywords"""
        if len(keywords) is 0 or None in keywords:
            paths = UtilityBox.get_all_files(folder, *IMAGE_FORMATS)
        else:
            if not isinstance(keywords, tuple):
                keywords = (keywords,)
            paths = UtilityBox.get_filtered_files(folder, IMAGE_FORMATS, keywords, strict=strict)
        return ResizedSurface.get_surfaces(intended_size, resize_mode, resize_smooth, keep_aspect_ratio, *paths)    

    @staticmethod
    def get_surfaces(intended_size, resize_mode, resize_smooth, keep_aspect_ratio, *paths):
        """Gerts all the surfaces from the paths"""
        surfaces = {}
        for path in paths:
            surfaces[path] = ResizedSurface.get_surface(path, intended_size, resize_mode,\
                            resize_smooth, keep_aspect_ratio)
        return surfaces

    @staticmethod
    def get_surface(path, intended_size, resize_mode, resize_smooth, keep_aspect_ratio=True):
        surface = ResizedSurface(path, intended_size, resize_mode, resize_smooth, keep_aspect_ratio=keep_aspect_ratio)
        hash_key = hash(surface)
        if hash_key in ResizedSurface.RESIZED_SURFACES_LOADED.keys():
            #print("THIS ONE WAS ALREADY LOADED "+str(surface))
            return ResizedSurface.RESIZED_SURFACES_LOADED.get_item(hash_key).surface
        else:
            #print("THIS ONE WAS NOT LOADED "+str(surface))
            orig_surf = SurfaceLoader.get_surface(path) #Getting the original file
            final_surf = Resizer.resize(orig_surf, intended_size, mode=resize_mode, smooth=resize_smooth,\
                                        keep_aspect_ratio=keep_aspect_ratio)
            surface.set_surface(final_surf)
            ResizedSurface.add_surface(surface)
            return final_surf

    @staticmethod
    def add_surface(ResizedSurface):
        ResizedSurface.RESIZED_SURFACES_LOADED.add_item(hash(ResizedSurface), ResizedSurface)

    @staticmethod
    def clear_lut():
        ResizedSurface.RESIZED_SURFACES_LOADED.clear()

class SurfaceLoader(object):
    """Loader of the original unresized/unmodified images/surfaces"""
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
        paths = UtilityBox.get_filtered_files(folder, IMAGE_FORMATS, keywords, strict=strict)
        for image_path in paths:
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
        