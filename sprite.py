import pygame, gradients
from colors import *
from resizer import Resizer
from utility_box import UtilityBox
from exceptions import ShapeNotFoundException, NotEnoughSpritesException
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
        self.image, self.overlay    = Sprite.generate_surface(self.rect, **image_params)
        self.mask           = pygame.mask.from_surface(self.image) 
        #Additions to interesting funcionality
        self.real_rect      = (tuple([x/y for x,y in zip(position, canvas_size)]), tuple([x/y for x,y in zip(size, canvas_size)]))      
        #Made for regeneration purposes and such, have the percentage of the screen that it occupies
        #Animation and showing
        self.animation_value= 0
        self.animation_step = ANIMATION_STEP
        self.visible        = True
        self.use_overlay    = True
        self.active         = False
        self.enabled        = True
        self.hover          = False
        #input args to generate again if needed (change of size e.g.)
        self.params         = image_params

    def draw(self, surface):
        if self.visible:
            surface.blit(self.image, self.rect)
            if self.enabled:
                if self.use_overlay and self.active:    self.draw_overlay(surface)               
                self.update()

    def update_mask(self):
        self.mask = pygame.mask.from_surface(self.image)

    def draw_overlay(self, surface):
        surface.blit(self.overlay, self.rect)
        self.animation_frame()

    def get_canvas_size(self):
        return tuple([x//y for x,y in zip(self.rect.size, self.real_rect[1])])

    def get_rect_if_canvas_size(self, canvas_size):
        return pygame.Rect(tuple([x*y for x,y in zip(self.real_rect[0], canvas_size)]),\
        tuple([x*y for x,y in zip(self.real_rect[1], canvas_size)]))

    def set_canvas_size(self, canvas_size):
        new_position    = tuple([int(x*y) for x,y in zip(self.real_rect[0], canvas_size)]), 
        new_size        = tuple([int(x*y) for x,y in zip(self.real_rect[1], canvas_size)])
        self.rect       = (new_position, new_size)
        self.image, self.overlay    = Sprite.generate_surface(self.rect, self.image_params)
        self.mask = pygame.mask.from_surface(self.image)
        LOG.log('debug', "Succesfully changed sprite ", self.id, " to ", self.rect.size, ", due to the change to resolution ", canvas_size)

    def set_visible(self, visible):
        self.visible = visible

    def set_hover(self, hover):
        self.hover = hover

    def set_active(self, active):
        self.active = active
    
    def set_enabled(self, enabled):
        if enabled and not self.enabled:      #Deactivating button
            self.overlay.fill(DARKGRAY)
            self.overlay.set_alpha(128)
            self.image.blit(self.overlay, (0, 0))
            self.enabled        = False
            self.use_overlay    = False
        elif not enabled and self.enabled:    #Activating button
            self.enabled        = True
            self.use_overlay    = True
            self.regenerate_image()         #Restoring image and overlay too

    def enable_overlay(self, enabled):
        self.use_overlay    = enabled

    def animation_frame(self):
        self.animation_value    += self.animation_step
        if not MIN_ANIMATION_VALUE <= self.animation_value <= MAX_ANIMATION_VALUE:
            self.animation_step     = -self.animation_step
            self.animation_value    = MIN_ANIMATION_VALUE if self.animation_value < MIN_ANIMATION_VALUE else MAX_ANIMATION_VALUE
        self.overlay.set_alpha(int(MAX_TRANSPARENCY*self.animation_value))

    def update(self):
        '''Update method, will process and change image attributes to simulate animation when drawing'''
        pass  
            

    #For use after changing some input param.
    def regenerate_image(self):
        self.image, self.overlay    = Sprite.generate_surface(self.rect, **self.params)

    @staticmethod
    def generate_surface(size, texture=None, keep_aspect_ratio=True, shape="Rectangle", transparent=False,\
                        only_text=False, text="default_text", text_color=WHITE, text_font=None,\
                        fill_color=RED, fill_gradient=True, gradient=(LIGHTGRAY, DARKGRAY), gradient_type="horizontal",\
                        overlay_color=WHITE, border=True, border_color=WHITE, border_width=2, **unexpected_kwargs):
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
            font_size   = Resizer.max_font_size(text, size, text_font)
            return pygame.font.Font(text_font, font_size).render(text, True, text_color), overlay 
        if texture:     #If we get a string with the path of a texture to load onto the surface
            surf = Resizer.resize_same_aspect_ratio(pygame.image.load(texture).convert_alpha(), size) if keep_aspect_ratio\
            else pygame.transform.smoothscale(pygame.image.load(texture).convert_alpha(), size)
            return surf, overlay
        #In the case that we are still running this code and didn't return, means we dont have a texture nor a text, and have to generate the shape
        radius  = size[0]//2
        surf    = pygame.Surface(size)
        if shape == 'circle':
            if fill_gradient:   surf = gradients.radial(radius, gradient[0], gradient[1])
            else:  
                colorkey = fill_color
                if not transparent: #Search for another colorkey
                    while colorkey == fill_color or colorkey == border_color: 
                        colorkey = UtilityBox.random_rgb_color()
                    surf.fill(colorkey)
                    pygame.draw.circle(surf, fill_color, (radius, radius), radius, 0)
                else:
                    surf.fill(colorkey)
                surf.set_colorkey(colorkey)
            if border:  pygame.draw.circle(surf, border_color, (radius, radius), radius, border_width)
            pygame.draw.circle(overlay, overlay_color, (radius, radius), radius, 0)
        elif shape == 'rectangle':
            if fill_gradient:   surf = gradients.vertical(size, gradient[0], gradient[1]) if gradient_type == 0 \
                                else gradients.horizontal(size, gradient[0], gradient[1])
            else:               surf.fill(fill_color)
            if border:          pygame.draw.rect(surf, border_color, pygame.rect.Rect((0,0), size), border_width)
            overlay.fill(overlay_color)
        else:
            raise ShapeNotFoundException("Available shapes: Rectangle, Circle. "+shape+" is not accepted")
        return surf, overlay

#TODO make overlay here as another subclass? Or too much of a hassle?

#This only accepts textures
class AnimatedSprite(Sprite):
    def __init__(self, _id, position, size, canvas_size, *sprite_list, sprite_folder=None, **image_params):
        super().__init__(_id, position, size, canvas_size, **image_params)
        #Adding parameters to control a lot of sprites instead of only one
        self.sprites            = []    #Not really sprites, only surfaces
        self.hover_sprites      = []    #Not really sprites, only surfaces
        self.original_sprites   = []    #Not really sprites, only surfaces
        self.ids                = []    
        self.masks              = []
        self.hover              = False
        self.animation_index    = 0
        self.load_sprites(sprite_folder) if sprite_folder else self.add_sprites(*sprite_list)
        self.image              = self.current_sprite()     #Assigning a logical sprite in place of the decoy one of the super()
        self.mask               = self.current_mask()       #Same shit to mask
        self.use_overlay        = False

    def __id_exists(self, sprite_id):
        for i in range(0, len(self.ids)):
            if sprite_id == self.ids[i]:    return self.original_sprites[i]
        return False

    def __surface_exists(self, sprite_surface):
        for i in range(0, len(self.original_sprites)):
            if sprite_surface == self.original_sprites[i]:    
                return self.original_sprites[i]
        return False

    #This method is tested already
    def load_sprites(self, sprite_folder):
        sprite_images = [sprite_folder+'\\'+f for f in listdir(sprite_folder) if isfile(join(sprite_folder, f))]
        for sprite_image in sprite_images:
            if sprite_image.lower().endswith(('.png', '.jpg', '.jpeg', 'bmp')):
                if not self.__id_exists(sprite_image):
                    self.ids.append(sprite_image.lower())
                    self.add_sprite(pygame.image.load(sprite_image))

    def add_sprite(self, surface):
        self.original_sprites.append(surface)
        self.sprites.append(Resizer.resize_same_aspect_ratio(surface, self.rect.size))
        self.hover_sprites.append(Resizer.resize_same_aspect_ratio(surface, [int(x*1.5) for x in self.rect.size]))
        self.masks.append(pygame.mask.from_surface(surface))

    def add_sprites(self, *sprite_surfaces):
        if len(sprite_surfaces) < 1:
            raise NotEnoughSpritesException("To create an animated sprite you have to at least add one.")
        for sprite_surf in sprite_surfaces:
            if isinstance(sprite_surf, pygame.sprite.Sprite): sprite_surf = sprite_surf.image
            if not self.__surface_exists(sprite_surf):
                self.ids.append("no_id")
                self.add_sprite(sprite_surf)

    def draw(self, surface):
        self.image = self.current_sprite() if not self.hover else self.current_hover_sprite()
        surface.blit(self.image, self.rect)

    def set_canvas_size(self, canvas_size):
        super().set_canvas_size(canvas_size)    #Changing the sprite size and position to the proper place
        self.sprites.clear()                    #Cleaning idle sprites
        self.hover_sprites.clear()              
        self.masks.clear()
        for surface in self.original_sprites:   self.add_sprite(surface)

    def animation_frame(self):
        '''Update method, will process and change image attributes to simulate animation when drawing'''
        self.animation_index = self.animation_index+1 if self.animation_index < (len(self.sprites)-1) else 0

    def set_hover(self, hover):
        self.hover = hover

    def current_sprite(self):
        return self.sprites[self.animation_index]

    def current_hover_sprite(self):
        return self.hover_sprites[self.animation_index]

    def current_mask(self):
        return self.masks[self.animation_index]

class MultiSprite(Sprite):
    def __init__(self, _id, position, size, canvas_size, **image_params):
        super().__init__(_id, position, size, canvas_size, **image_params)
        self.sprites        = pygame.sprite.OrderedUpdates()    #Could use a normal list here, but bah

    def add_sprite(self, sprite):
        sprite.use_overlay   = False #Not interested in overlays from a lot of sprites at the same time
        self.sprites.add(sprite)
        self.image.blit(sprite.image, sprite.rect)

    def regenerate_image(self):
        super().regenerate_image()
        for sprite in self.sprites.sprites():   self.image.blit(sprite.image, sprite.rect)

    def set_canvas_size(self, canvas_size):
        super().set_canvas_size(canvas_size)    #Changing the sprite size and position to the proper place
        for sprite in self.sprites.sprites():   
            sprite.set_canvas_size(canvas_size)
            self.image.blit(sprite.image, sprite.rect)

    def get_sprite_abs_position(self, sprite):
        return tuple(relative+absolute for relative, absolute in zip(sprite.rect.topleft, self.rect.topleft))

    def get_sprite_abs_center(self, sprite):
        return tuple(relative+absolute for relative, absolute in zip(sprite.rect.topleft, self.rect.topleft))

    def get_sprite(self, *keywords):
        for sprite in self.sprites.sprites():
            if all(kw in sprite.id for kw in keywords): return sprite