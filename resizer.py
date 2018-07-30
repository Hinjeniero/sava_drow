import pygame

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
        
    #Resizing the surface to fit in the hitbox preserving the ratio, instead of fuckin it up
    @staticmethod
    def surface_resize(surface, new_size):
        old_size = surface.get_size()
        for new_axis, old_axis in zip(new_size, old_size):
            if old_axis > new_axis:
                ratio = (new_axis/old_axis)
                for i in range (0, len(new_size)): #This way it modifies the list, the normal iterator doesn't work that way, assigning names and shit
                    new_size[i] = int(new_size[i]*ratio)
        return pygame.transform.scale(surface, tuple(new_size)) #Resizing the surface

    '''@staticmethod
    def draw_hitbox(surface, surface_rect, hitbox_color=(255, 0, 0)):
        size = surface_hitbox.get_size()
        pygame.draw.rect(surface, hitbox_color, rect, 2)'''