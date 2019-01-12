
import pygame
from synch_dict import Dictionary
from utility_box import UtilityBox
from decorators import time_it
from logger import Logger as LOG

class SurfaceLoader(object):
    SURFACES_LOADED = Dictionary()
    
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
        LOG.log('INFO', 'Checking LUT and loading all the images in ', folder)
        for image_path in UtilityBox.get_all_files(folder, '.png', '.jpg', '.jpeg', 'bmp'):
            surfaces[image_path] = SurfaceLoader.get_surface(image_path)
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
        LOG.log('INFO', 'Checking LUT and loading some of the images in ', folder, ' with keywords ', keywords)
        for image_path in UtilityBox.get_all_files(folder, '.png', '.jpg', '.jpeg', 'bmp'):
            if (not strict and any(kw.lower() in image_path.lower() for kw in keywords))\
            or (strict and all(kw.lower() in image_path.lower() for kw in keywords)):
                surfaces[image_path] = SurfaceLoader.get_surface(image_path)
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
            SurfaceLoader.SURFACES_LOADED.add_item(image_path, surface)
            return surface
        