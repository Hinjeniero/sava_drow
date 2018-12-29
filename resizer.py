"""--------------------------------------------
resizer module. In here is all the logic related to the transformation
of surfaces and the related information of type pygame.Surface.
Have the following classes:
    Resizer
--------------------------------------------"""
__all__ = ['Resizer']
__version__ = '0.2'
__author__ = 'David Flaity Pardo'

#Python libraries
import pygame
#Selfmade libraries
from exceptions import BadResizerParamException

class Resizer (object):
    """Resizer class. Contains the methods related to surfaces transformation and analyzing."""
    @staticmethod
    def max_font_size_limited(text, size, max_font_size, font_type=None):
        """Gives the maximum font size that makes a text fit in a specific pixel size. (With a font size limit). 
        It's an approximate in exchange for having a logaritmic execution time.
        Results have an error margin of 0-2 in font size comparing with the absolute best result possible.
        E.G. perfect font size is 99, result is 97. 200->100->50->75->87->93->96->97, factor reachs 0 at this step.
        Args:
            text (str): The text that will be rendered. Longer strings give greater widths.
            size (:tuple: int, int):Size in which to fit the text. In pixels.
            max_font_size (int):    Font size upper limit. The absolute maximum font size that we establish.
            font_type (pygame.font):    Font itself that will be used.
        Returns:
            (int): The greatest font size that can fit (When the text is rendered) in the input size.
        """
        factor = max_font_size//2 #We start substracting
        font_size = max_font_size
        while factor is not 0:
            font = pygame.font.Font(font_type, font_size)
            current_size = font.size(text) #Getting the needed size to render this text with i size

            if all(current<size for current, size in zip(current_size, size)):
                font_size += factor
            else: #This equals any(current>max for current, max in zip(current_size, max_size))
                font_size -= factor
            factor = factor//2
        return font_size

    #Gives an approximate in exchange for having a logaritmic execution time
    #Determines the max font size.
    @staticmethod
    def max_font_size(text, size, font_type=None):
        """Gives the maximum font size that makes a text fit in a specific pixel size.
        Achieves this by getting the maximum upper limit that makes a rendered text overflow the desired size.
        Makes this by starting from 1 and multiplying by 2 in each iteration.
        Once this is done, it calls the auxiliary method to reach the font size with an upper limit set.
        Args:
            text (str): The text that will be rendered. Longer strings give greater widths.
            size (:tuple: int, int):Size in which to fit the text. In pixels.
            font_type (pygame.font):    Font itself that will be used.
        Returns:
            (int): The greatest font size that can fit (When the text is rendered) in the input size."""
        font_size       = 1
        current_size    = (0, 0)
        while not any(current>size for current, size in zip(current_size, size)):   #While not hitting the upper limit
            font = pygame.font.Font(font_type, font_size)
            current_size = font.size(text) #Getting the needed size to render this text with i size
            font_size *= 2
        return Resizer.max_font_size_limited(text, size, font_size, font_type=font_type)
        
    @staticmethod 
    def resize_same_aspect_ratio(element, new_size):
        """Resizes a surface to the closest size achievable to the input
        without changing the original object aspect ratio relation.
        This way the modified object looks way more natural than just a stretched wretch.
        Accepts both pygame.Surface and pygame.sprite.Sprite.
        Args:
            element (:obj: pygame.Surface||pygame.sprite.Sprite):   Element to resize.
            new_size (:tuple: int, int):    New desired size for the input element.
        Returns:
            (pygame.Surface||:tuple:int):   The resized Surface if the input was a surface.
                                            A tuple of the ratios used to resize if the input was a sprite.
        """
        if isinstance(element, pygame.sprite.Sprite):   return Resizer.__sprite_resize(element, new_size)
        elif isinstance(element, pygame.Surface):       return Resizer.__surface_resize(element, new_size)
        else:                                           BadResizerParamException("Can't resize element of type "+str(type(element)))

    #Resizing the surface to fit in the hitbox preserving the ratio, instead of fuckin it up
    @staticmethod
    def __surface_resize(surface, new_size):
        """Resizes a surface to the closest size achievable to the input
        without changing the original aspect ratio relation.
        Args:
            surface (:obj: pygame.Surface): Surface to resize.
            new_size (:tuple: int, int):    New desired size for the input element.
        Returns:
            (pygame.Surface):   The resized Surface."""
        ratio = min([new/old for new, old in zip(new_size, surface.get_size())])
        return pygame.transform.smoothscale(surface, tuple([int(ratio*size) for size in surface.get_size()])) #Resizing the surface
    
    @staticmethod
    def __sprite_resize(sprite, new_size):
        """Resizes a Sprite to the closest size achievable to the input
        without changing the original aspect ratio relation.
        The changes are made in the sprite itself.
        Args:
            sprite (:obj: pygame.sprite.Sprite):    Sprite to resize.
            new_size (:tuple: int, int):    New desired size for the input element.
        Returns:
            (:tuple:int):   A tuple of the ratios used to resize if the input was a sprite."""
        ratio = min([new/old for new, old in zip(new_size, sprite.rect.size)])
        sprite.rect.size = tuple([int(ratio*size) for size in sprite.rect.size])
        sprite.image = pygame.transform.smoothscale(sprite.image, sprite.rect.size)
        return ratio