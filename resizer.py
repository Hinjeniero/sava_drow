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
    def resize(element, new_size, mode='fit'): #TODO UPDATE DOCUMENTATION
        """Resizes a surface to the closest size achievable to the input
        without changing the original object aspect ratio relation.
        This way the modified object looks way more natural than just a stretched wretch.
        Accepts both pygame.Surface and pygame.sprite.Sprite.
        Args:
            element (:obj: pygame.Surface||pygame.sprite.Sprite):   Element to resize.
            new_size (:tuple: int, int):    New desired size for the input element.
        Returns:
            (:tuple: int, int):   A tuple with the resultant size.
        """
        #Getting old size
        if isinstance(element, pygame.Surface):         old_size = element.get_size()
        elif isinstance(element, pygame.sprite.Sprite): old_size = element.rect.size
        else:                                           raise BadResizerParamException("Can't resize element of type "+str(type(element)))
        #Getting the ratio
        if 'fit' in mode:                              
            ratio = min([new/old for new, old in zip(new_size, old_size)])
        elif 'fill' in mode:                         
            ratio = max([new/old for new, old in zip(new_size, old_size)])
        else:                                           raise BadResizerParamException('Mode '+mode+' is not a recognized resizing mode')
        #Multiplyyyying
        result_size = tuple([int(ratio*size) for size in old_size])
        #And returning either a surface or True if success
        if isinstance(element, pygame.Surface):   
            return pygame.transform.smoothscale(element, result_size)
        else:   #Its a sprite
            element.image = pygame.transform.smoothscale(element.image, result_size)
            element.rect.size = result_size
        return True                                    