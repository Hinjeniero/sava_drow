import pygame, gradients
from colors import *
from resizer import Resizer
from exceptions import ShapeNotFoundException
from logger import Logger as LOG
from os import listdir
from os.path import isfile, join, dirname

MIN_ANIMATION_VALUE     = 0.00
MAX_ANIMATION_VALUE     = 1.00
ANIMATION_STEP          = 0.03      #Like 1/30, so in 60 fps it does a complete loop
MAX_TRANSPARENCY        = 255

class Sprite(pygame.sprite.Sprite):
    def __init__(self, _id, position, size, canvas_size, **image_params):
        super().__init__()
        #Basic stuff
        self.id             = _id
        self.rect           = pygame.Rect(position, size) 
        self.image, self.overlay    = Sprite.generate_surface(image_params)
        self.mask           = pygame.mask.from_surface(self.image) 
        #Additions to interesting funcionality
        self.real_rect      = (tuple([x/y for x,y in zip(position, canvas_size)]), tuple([x/y for x,y in zip(size, canvas_size)]))      
        #Made for regeneration purposes and such, have the percentage of the screen that it occupies
        #Animation and showing
        self.animation_value= 0
        self.animation_step = ANIMATION_STEP
        self.visible        = True
        #input args to generate again if needed (change of size e.g.)
        self.params         = image_params

    def draw(self, surface, offset=(0, 0)):
        if self.visible:
            position = tuple([x+y for x,y in zip(offset, self.rect.topleft)])
            self.overlay.set_alpha(int(MAX_TRANSPARENCY*self.animation_value))
            surface.blits((self.image, position), (self.overlay, position))
            self.update()

    def get_canvas_size(self):
        return tuple([x//y for x,y in zip(self.rect.size, self.real_rect[1])])

    def set_canvas_size(self, canvas_size):
        new_position    = tuple([int(x*y) for x,y in zip(self.real_rect[0], canvas_size)]), 
        new_size        = tuple([int(x*y) for x,y in zip(self.real_rect[1], canvas_size)])
        self.rect       = (new_position, new_size)
        self.image, self.overlay    = Sprite.generate_surface(self.rect, self.image_params)
        self.mask = pygame.mask.from_surface(self.image)
        LOG.log('debug', "Succesfully changed sprite ", self.id, " to ", self.rect.size, ", due to the change to resolution ", canvas_size)

    def set_visible(self, visible):
        self.visible = visible

    def animation_frame(self):
        self.animation_value += self.animation_step
        if not MIN_ANIMATION_VALUE <= self.animation_value <= MAX_ANIMATION_VALUE:
            self.animation_step = -self.animation_step
            self.animation_value = MIN_ANIMATION_VALUE if self.animation_value < MIN_ANIMATION_VALUE else MAX_ANIMATION_VALUE

    def update(self):
        '''Update method, will process and change image attributes to simulate animation when drawing'''
        self.animation_frame()

    @staticmethod
    def generate_surface(size, texture=None, keep_aspect_ratio=True, shape="Rectangle",\
                        only_text=False, text="default_text", text_color=WHITE, text_font=None,\
                        fill_color=RED, fill_gradient=True, gradient=(LIGHTGRAY, DARKGRAY), gradient_type="horizontal",\
                        overlay_color=WHITE, border=True, border_color=WHITE, border_width=2):
        """Generates a pygame surface according to input arguments.
        Args:
            size: Rect or tuple containing the dimensions of the surface (width, height)
            texture:
            keep_aspect_ratio:
            shape:
            ----
            only_text:
            text:
            text_color:
            text_font:
            ----
            fill_color: Solid color of the circle. 
            fill_gradient: True if we want a circle w/ a gradient. Priority over solid colors.
            gradient:
            gradient_type:
            ----
            overlay_color:
            border: True if the circle has a border.
            border_size: Size of the border in pixels.
            border_color: Color of the border. RGBA/RGB format.
        
        Returns:
            A surface containing the circle."""

        size    = size.size if isinstance(size, pygame.rect.Rect) else size
        shape   = shape.lower()
        overlay = pygame.Surface(size)
        #GENERATING IMAGE
        if only_text:   #Special case: If we want a sprite object with all the methods, but with only a text with transparent background
            font_size   = Resizer.max_font_size(text, size, 500, text_font)
            return pygame.font.Font(text_font, font_size).render(text, True, text_color), overlay         
        if texture:     #If we get a string with the path of a texture to load onto the surface
            return Resizer.resize_same_aspect_ratio(pygame.image.load(texture).convert_alpha(), size), overlay if keep_aspect_ratio\
            else pygame.transform.smoothscale(pygame.image.load(texture).convert_alpha(), size), overlay
        
        #In the case that we are still running this code and didn't return, means we dont have a texture nor a text, and have to generate the shape
        radius  = size[0]//2
        surf    = pygame.Surface(size)
        if shape == 'circle':
            if fill_gradient:   surf = gradients.radial(radius, gradient[0], gradient[1])
            else:               pygame.draw.circle(surf, fill_color, (radius, radius), radius, 0)
            if border:          pygame.draw.circle(surf, border_color, (radius, radius), radius, border_width)
            pygame.draw.circle(overlay, overlay_color, (radius, radius), radius, 0)
        elif shape == 'rectangle':
            if fill_gradient:   surf = gradients.vertical(size, gradient[0], gradient[1]) if gradient_type == 0 \
                                else gradients.horizontal(size, gradient[0], gradient[1])
            else:               surf.fill(fill_color)
            if border:          pygame.draw.rect(surf, border_color, (0,0), size, border_width)
            overlay.fill(overlay_color)
        else:
            raise ShapeNotFoundException("Available shapes: Rectangle, Circle. "+shape+" is not accepted")
        return surf, overlay

#This only accepts textures
class AnimatedSprite(Sprite):
    def __init__(self, _id, position, size, canvas_size, sprite_folder, **image_params):
        super().__init__(_id, position, size, canvas_size, **image_params)
        #Adding parameters to control a lot of sprites instead of only one
        self.sprites            = pygame.sprite.OrderedGroup()
        self.hover_sprites      = pygame.sprite.OrderedGroup()
        self.original_sprites   = pygame.sprite.OrderedGroup()
        self.ids                = []
        self.masks              = []
        self.hover              = False
        self.animation_index    = 0
        self.add_sprites(size, sprite_folder)
        self.image  = self.current_sprite()     #Assigning a logical sprite in place of the decoy one of the super()
        self.mask   = self.current_mask()       #Same shit to mask

    def __get_original_sprite(self, sprite_id):
        for i in range(0, len(self.ids)):
            if sprite_id == self.ids[i]:    return self.original_sprites.sprites()[i]
        return False

    def add_sprite(self, sprite_path, size):
        result = self.__get_original_sprite(sprite_path)  #Check if first timer
        if not result:
            frame = pygame.image.load(sprite_path)
            self.original_sprites.add(frame)
        else:
            frame = result
        self.sprites.add(Resizer.resize_same_aspect_ratio(frame, self.rect.size))
        self.hover_sprites.add(Resizer.resize_same_aspect_ratio(frame, [int(x*1.5) for x in self.rect.size]))
        self.masks.append(pygame.mask.from_surface(frame))
        self.ids.append(sprite_path.lower())

    #This method is tested already
    def add_sprites(self, size, sprite_folder):
        sprite_images = [sprite_folder+'\\'+f for f in listdir(sprite_folder) if isfile(join(sprite_folder, f))]
        for sprite_image in sprite_images:
            if sprite_image.lower().endswith(('.png', '.jpg', '.jpeg', 'bmp')):
                self.add_sprite(sprite_image, size)

    def draw(self, surface):
        self.image = self.current_sprite() if not self.hover else self.current_hover_sprite()
        surface.blit(self.image, self.rect)

    def set_canvas_size(self, canvas_size):
        super().set_canvas_size(canvas_size)    #Changing the sprite size and position to the proper place
        self.sprites.empty()                    #Cleaning idle sprites
        self.hover_sprites.empty()              
        self.masks.clear()
        for path in self.ids:   self.add_sprite(path, self.rect.size)

    def update(self):
        '''Update method, will process and change image attributes to simulate animation when drawing'''
        self.animation_index = self.animation_index+1 if self.animation_index < (len(self.sprites.sprites())-1) else 0

    def set_hover(self, hover):
        self.hover = hover

    def current_sprite(self):
        return self.sprites.sprites()[self.animation_index]

    def current_hover_sprite(self):
        return self.hover_sprites.sprites()[self.animation_index]

    def current_mask(self):
        return self.masks[self.animation_index]

class MultiSprite(Sprite):
    def __init__(self, shit):
        super().__init__(shit)
        self.animation_sprites  = []
        self.hover_sprites      = []
        self.animation_index    = 0

