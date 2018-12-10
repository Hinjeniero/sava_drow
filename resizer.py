import pygame
from exceptions import BadResizerParamException

class Resizer (object):
    #Gives an approximate in exchange for having a logaritmic execution time
    #Could have more accurate results saving the best result in the iterations (minimum difference with size), but this is good enough for the game.
    #Results have an error margin of 0-2 in font size with the maximum best result (example of max error, perfect font size is 99, result is 97).
    #200->100->50->75->87->93->96->97, factor is 0 here.
    @staticmethod
    def max_font_size(text, max_size, max_font_size, font=None):
        factor = max_font_size//2 #We start substracting
        font_size = max_font_size
        while factor is not 0:
            font = pygame.font.Font(None, font_size)
            current_size = font.size(text) #Getting the needed size to render this text with i size

            if all(current<max for current, max in zip(current_size, max_size)):
                font_size += factor
            else: #This equals any(current>max for current, max in zip(current_size, max_size))
                font_size -= factor
            factor = factor//2
        return font_size
        
    @staticmethod 
    def resize_same_aspect_ratio(element, new_size):
        if isinstance(element, pygame.sprite.Sprite):   return Resizer.__sprite_resize(element, new_size)
        elif isinstance(element, pygame.Surface):       return Resizer.__surface_resize(element, new_size)
        else:                                           BadResizerParamException("Can't resize element of type "+str(type(element)))

    #Resizing the surface to fit in the hitbox preserving the ratio, instead of fuckin it up
    @staticmethod
    def __surface_resize(surface, new_size):
        ratio = min([new/old for new, old in zip(new_size, surface.get_size())])
        return pygame.transform.smoothscale(surface, tuple([int(ratio*size) for size in surface.get_size()])) #Resizing the surface
    
    @staticmethod
    def __sprite_resize(sprite, new_size):
        ratio = min([new/old for new, old in zip(new_size, sprite.rect.size)])
        sprite.rect.size = tuple([int(ratio*size) for size in sprite.rect.size])
        sprite.image = pygame.transform.smoothscale(sprite.image, sprite.rect.size)
        return ratio