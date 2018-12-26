
"""--------------------------------------------
sprite module. Contains classes that work as a layer over the pygame.Sprite.sprite class.
Have the following classes, inheriting represented by tabs:
    Sprite
        ↑TextSprite
        ↑AnimatedSprite
        ↑MultiSprite
--------------------------------------------"""

__all__ = ['Sprite', 'TextSprite', 'AnimatedSprite', 'MultiSprite']
__version__ = '0.5'
__author__ = 'David Flaity Pardo'

#Python libraries
import pygame
from os import listdir
from os.path import isfile, join, dirname
#External libraries
import gradients
#Selfmade libraries
from colors import WHITE, RED, LIGHTGRAY, DARKGRAY
from resizer import Resizer
from utility_box import UtilityBox
from exceptions import ShapeNotFoundException, NotEnoughSpritesException
from logger import Logger as LOG

#Global variables, read-only
ANIMATION_INTERVAL      = (0.00, 1.00)  #Real interval
ANIMATION_STEP          = 0.03          #30 steps until max value
MAX_TRANSPARENCY        = 255           #255 is 100% transparency

class Sprite(pygame.sprite.Sprite):
    """Layer that inherits from pygame.sprite.Sprite. Adds useful attributes and methods.
    This will be used as the base Sprite class in all the project scope. Can be added to Groups.
    
    Attributes:
        image (:obj:`pygame.Surface`):  Inherited from pygame.sprite.Sprite. Face of the sprite.
                                        Generated after image_params. No need to set it directly.
        rect (:obj:`pygame.rect.Rect`): Inherited from pygame.sprite.Sprite. Contains the information
                                        regarding the size and position on the screen (in pixels). 
        mask (:obj:`pygame.Mask`):      Created according to self.image. Pygame object used for pixels collisions.
        overlay (:obj:`pygame.Surface`):Surface of the same size and position as the image and sprite itself.
                                        It's used to blit on top of the sprite with different degrees of transparency
                                        and color to simulate animation.

        id (str):   Identity/name/identifier of this sprite.
        real_rect (:tuples: 2 int,int): Contains a float of iterval (0, 1), that saves the proportion vs display size.
                                        First tuple contains the position, second one the size.
        ----e.g.: display 1280*720, element size 128*72 and position 24, 7. Real rect: ((0.02, 0.01), (0.10, 0.10))----

        params (dict):  Contains all the parameters to create the self.image surface.
                        Check generate_surface to see the not ignored params.   
        resolution (tuple): Current resolution of the display.
        animation_value (int):  Number to set the transparency of the overlay. Goes up and back down. 
                                Used for the overlay's animation.
        animation_step (float): Ammount added/substrated from animation_value. Used for the overlay's animation.   
        visible (boolean):  True and the sprite will be drawn, False will not. Literal definition of 'visible'.
        use_overlay (boolean): True if we use the self.overlay attribute to simulate animation.
        active (boolean):   True if the element is in the state `active`. Not used inside the object itself. 
                            This attribute is to be used in inhereting classes or outside the object scope alltogether.
        hover (boolean):    True if the element is i the state `hover`, this means that the mouse is hovering this sprite.
        enabled (boolean):  True if the element can be interacted with. When False, the element will be half-gray and without animation.
        """

    def __init__(self, id_, position, size, canvas_size, **image_params):
        """Constructor of Sprite class.
        Args:
            id_ (str):  Identifier of the Sprite.
            position (:tuple: int,int): Position of the Sprite in the screen. In pixels.
            size (:tuple: int,int):     Size of the Sprite in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display. In pixels.
            image_params (:dict:):  Dict of keywords and values as parameters to create the self.image attribute.
                                    Variety going from fill_color and use_gradient to text_only.
        Params dict attributes: TODO modify this
            position: Position that this surface will have on the destination surface if it's drawed.
            size: Size of the surface containing the polygon, is a tuple (width, height).
            surf_color: Background color of the polygon if gradient and image are false. Default is solid red.
            surf_image: Texture to use in the surface. It's a loaded image. Default is None.
            border: True if the polygon has a border. Default is True.
            border_size: Width of the border in pixels. Default is 2 pixels.
            border_color: Color of the border. Default is solid white.
            use_gradient: True if the polygon color is a gradient. Default is True.
            start_color: Starting color of the gradient. Default is gray.
            end_color: Ending color of the gradient. Default is dark gray.
            gradient_type: Orientation of the gradient, 0 for vertical, 1 or whatever for horizontal. Default is 0 (Vertical)
        """
        super().__init__()
        self.params         = image_params
        #Basic stuff---------------------------------
        self.id             = id_
        self.rect           = pygame.Rect(position, size) 
        self.image, self.overlay = Sprite.generate_surface(self.rect, **image_params)
        self.mask           = pygame.mask.from_surface(self.image) 
        #Additions to interesting funcionality-------
        self.real_rect      =   (tuple([x/y for x,y in zip(position, canvas_size)]),\
                                tuple([x/y for x,y in zip(size, canvas_size)]))
        self.resolution     = canvas_size      
        #Animation and showing-----------------------
        self.animation_value= 0
        self.animation_step = ANIMATION_STEP
        self.visible        = True
        self.use_overlay    = True
        self.active         = False
        self.enabled        = True
        self.hover          = False
        self.generate()

    def generate(self):
        """Generates the object, executes all the actions that are needed upon calling of the init method.
        A METHOD TO OVERLOAD, SUPERCLASS (UIELEMENT) DOES NOTHING.
        """
        pass

    def draw(self, surface):
        """Draws the sprite over a surface. Draws the overlay too if use_overlay is True.
        Args:
            surface (:obj: pygame.Surface): Surface to draw the Sprite. It's usually the display.
        """
        if self.visible:
            surface.blit(self.image, self.rect)
            if self.enabled:
                if self.use_overlay and self.active:    self.draw_overlay(surface)               
                self.update()

    def update_mask(self):
        """Updates the mask attribute afther the image attribute. To use after a change in self.image."""
        self.mask = pygame.mask.from_surface(self.image)

    def draw_overlay(self, surface):
        """Draws the overlay over a surface.
        Args:
            surface (:obj: pygame.Surface): Surface to draw the Sprite. It's usually the display
        """
        surface.blit(self.overlay, self.rect)
        self.animation_frame()

    def get_canvas_size(self):
        """Returns the current resolution size that this Sprite has. THIS IS NOT THE SIZE OF THE SPRITE.
        Returns:
            tuple(int, int):    Resolution/canvas size of this Sprite."""
        return self.resolution

    def get_rect_if_canvas_size(self, canvas_size):
        return pygame.Rect(tuple([x*y for x,y in zip(self.real_rect[0], canvas_size)]),\
        tuple([x*y for x,y in zip(self.real_rect[1], canvas_size)]))

    def set_canvas_size(self, canvas_size):
        """Set an internal resolution (NOT SIZE). Updates self.real_rect and self.resolution.
        Args:
            canvas_size (:tuple: int,int): Resolution to set.
        """
        self.resolution = canvas_size
        new_position    = tuple([int(x*y) for x,y in zip(self.real_rect[0], canvas_size)]) 
        new_size        = tuple([int(x*y) for x,y in zip(self.real_rect[1], canvas_size)])
        self.set_rect(pygame.Rect(new_position, new_size))
        LOG.log('debug', "Succesfully changed sprite ", self.id, " to ", self.rect.size, ", due to the change to resolution ", canvas_size)

    def set_size(self, size):
        """Changes the size of the Sprite. Updates rect and real_rect, and changes image and mask to match the size.
        Args:
            size (:obj: pygame.Rect||:tuple: int,int): New size of the Sprite. In pixels.
        """
        self.rect       = pygame.rect.Rect(self.rect.topleft, size)
        self.real_rect  =  (self.real_rect[0], tuple([x/y for x,y in zip(size, self.resolution)]))
        self.regenerate_image()
        LOG.log('debug', "Succesfully changed sprite ", self.id, " size to ",size)

    def set_position(self, position):
        """Changes the position of the Sprite. Updates rect and real_rect.
        Args:
            position (:obj: pygame.Rect||:tuple: int,int): New position of the Sprite. In pixels.
        """
        self.rect       = pygame.rect.Rect(position, self.rect.size)
        self.real_rect  =  (tuple([x/y for x,y in zip(position, self.resolution)]), self.real_rect[1])
        LOG.log('debug', "Succesfully changed sprite ",self.id, " position to ",position)

    def set_rect(self, rect):
        """Sets a new Rect as the Sprite rect. Uses the rect.size and rect.topleft to change size and position
        Only executes set_position and set_size if the position or size of the rect is different from the original one. """
        if self.rect.topleft != rect.topleft:   self.set_position(rect.topleft)
        if self.rect.size != rect.size:         self.set_size(rect.size)

    def set_visible(self, visible):
        """Sets the visible attribute. This attribute is used to draw or not the Sprite.
        Args:
            visible (boolean): The value to set.
        """
        self.visible = visible

    def set_hover(self, hover):
        """Sets the active attribute. Should be True if the mouse is hovering the Sprite.
        Args:
            hover (boolean): The value to set.
        """
        self.hover = hover

    def set_active(self, active):
        """Sets the visible attribute. Can be used for differen purposes.
        Args:
            active (boolean): The value to set.
        """
        self.active = active
    
    def set_enabled(self, enabled):
        """Sets the enabled attribute. If enabled is False, the element will be deactivated.
        No event or action will be sent or registered. Also, a semitransparent grey color will be blitted.
        Changes to this attribute regenerate the image and use surfaces, and so it will be slow.
        Args:
            enabled (boolean): The value to set.
        """
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
        """Sets the use_overlay attribute. If True, the overlay will be used.
        Args:
            enabled (boolean): The value to set.
        """
        self.use_overlay    = enabled

    def animation_frame(self):
        """Makes the changes to advance the animation one frame. This method is intended to be overloaded.
        In the superclass, it simply changs animation_value and reverse animation_step if needed"""
        self.animation_value    += self.animation_step
        if not ANIMATION_INTERVAL[0] <= self.animation_value <= ANIMATION_INTERVAL[1]:
            self.animation_step     = -self.animation_step
            self.animation_value    = ANIMATION_INTERVAL[0] if self.animation_value < ANIMATION_INTERVAL[0] else ANIMATION_INTERVAL[1]
        self.overlay.set_alpha(int(MAX_TRANSPARENCY*self.animation_value))

    def update(self):
        '''Update method, to be executed after each execution of the method draw.
        Process and change attributes to simulate animation.
        Intended to be overloaded.'''
        pass  

    #For use after changing some input param.
    def regenerate_image(self):
        """Generates the image and overlay again, following the params when the constructor executed.
        Also updates the mask. Intended to be used after changing an important attribute in rect or image."""
        self.image, self.overlay    = Sprite.generate_surface(self.rect, **self.params)
        self.update_mask()

    @staticmethod
    def generate_surface(size, surface=None, texture=None, keep_aspect_ratio=True, shape="Rectangle", transparent=False,\
                        only_text=False, text="default_text", text_color=WHITE, text_font=None,\
                        fill_color=RED, fill_gradient=True, gradient=(LIGHTGRAY, DARKGRAY), gradient_type="horizontal",\
                        overlay_color=WHITE, border=True, border_color=WHITE, border_width=2, **unexpected_kwargs):
        """Generates a pygame surface according to input arguments.
        Args:
            size (:obj: pygame.Rect||:tuple: int,int):  Dimensions of the surface (width, height)
            texture (string):   Path of the image to be loaded as a texture 
            keep_aspect_ratio (boolean):    True to keep the aspect ratio of the image when loading it
            shape (string): Shape of the surface. Options are circle and rectangle.
            ----
            only_text (boolean):    True if we want the surface to only contains a text with a transparent background.
            text (string):  The text to draw. Used if only_text is True. 
            text_color (:tuple: int, int, int): RGB Color of the text. Used if only_text is True.
            text_font (pygame.font):    Font used when rendering the text. Used if only_text is True.
            ----
            fill_color (:tuple: int, int, int): RGB color of the surface background. Used if fill_gradient is False. 
            fill_gradient (boolean):    True if we want a gradient instead of a solid color in the .
            gradient (:tuple of 2 tuples: int, int, int):   Interval of RGB colors of the gradient. (start, end). 
            gradient_type (string): direction of the gradient. Options are Horizontal and Vertical. Used if gradient is True.
            ----
            overlay_color (:tuple: int, int, int):  RGB color of the overlay.
            border (boolean):   True if the surface generated has a border.
            border_color (:tuple: int, int, int):   Color of the border. RGBA/RGB format.
            border_width (int):  Size of the border in pixels.
            unexpected_kwargs (anything):   Just there to not raise an error if unexpecte keywords are received.
        Returns:
            (:obj: pygame.Surface): Surface generated following the keywords"""
        size    = size.size if isinstance(size, pygame.rect.Rect) else size
        shape   = shape.lower()
        overlay = pygame.Surface(size)
        if surface: return surface, overlay #If we creating the sprite from an already created surface
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
                if transparent: #Dont draw the circle itself, only border
                    UtilityBox.add_transparency(surf, border_color)
                else:           #Draw the circle insides too
                    UtilityBox.add_transparency(surf, fill_color, border_color)
                    pygame.draw.circle(surf, fill_color, (radius, radius), radius, 0)
            if border:          
                pygame.draw.circle(surf, border_color, (radius, radius), radius, border_width)
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

class TextSprite(Sprite):
    """Class TextSprite. Inherits from Sprite, and the main surface is a text, from pygame.font.render.
    General class attributes: #Can be overloaded in **params
        text_font (:obj: pygame.font):  font to use when rendering the text. Default is None.
        text_color (:tuple: int, int, int): RGB Color of the text. Default is white (255, 255, 255).
    Attributes:
        text (str): Text that will be drawn.
    """
    __default_config = {'text_font'      : None,
                        'text_color'     : WHITE
    }

    def __init__(self, id_, position, size, canvas_size, text, **params):
        """Constructor of textSprite.
        Args:
            id_ (str):  Identifier of the Sprite.
            position (:tuple: int,int): Position of the Sprite in the screen. In pixels.
            size (:tuple: int,int):     Size of the Sprite in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display. In pixels.
            text (string):  Text of the text sprite. Will be drawn on image and saved.
            params (:dict:):    Dict of keywords and values as parameters to create the self.image attribute.
                                Includes attributes about the TextSprite, like the text color and the font used.            
        """
        UtilityBox.join_dicts(params, TextSprite.__default_config)  #Adding missing keys of default config to params
        super().__init__(id_, position, size, canvas_size, only_text=True, text=text, **params)
        self.rect.size  = self.image.get_size()  #The size can change in texts fromn the initial one
        self.real_rect  = (self.real_rect[0], tuple([x/y for x,y in zip(self.rect.size, self.resolution)]))  #The size can change in texts fromn the initial one
        self.text       = text

    def set_text(self, text):
        """Changes the text of the TextSprite, and regenerates the image to show the changes.
        Args:
            text (string): Text to set in the Sprite.
        """
        if text is not self.text:
            self.text           = text
            self.params['text'] = text
            self.regenerate_image()
        
class AnimatedSprite(Sprite):
    """Class AnimatedSprite. Inherits from Sprite. Adds all the attributes and methods needed to support
    the funcionality of a classic animated sprite, like a list of surfaces and a setted delay to change between them.
    Args:
        sprites (:list: pygame.Surface):    List of surfaces. Normal size.
        hover_sprites (:list: pygame.Surface):  List of surfaces to use when hover is True. Size is normal*2
        original_sprites (:list: pygame.Surface):   List of surfaces without resizing. Kept original image size.
        ids (:list: strings):   List of paths of the loaded images.
        masks (:list: pygame.Mask): List of masks to control collision. Match with sprites following the list order.
        counter (int):  Counter that controls when to change to the next surface. Works together with next_frame_time.
        next_frame_time (int):  Number of times that draw is called before changing surface to the next one.
        animation_index (int):  Current index in the sprites and mask lists.
    """

    def __init__(self, id_, position, size, canvas_size, *sprite_list, sprite_folder=None, animation_delay=5, **image_params):
        """Constructor of AnimatedSprite. 
        Args:
            id_ (str):  Identifier of the Sprite.
            position (:tuple: int,int): Position of the Sprite in the screen. In pixels.
            size (:tuple: int,int):     Size of the Sprite in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display. In pixels.
            *sprite_list (:obj: pygame.Surface):    Surfaces that are to be added separated by commas.
            sprite_folder (str):    Path of the folder that contains the surfaces to be loaded.
            animation_delay (int):  Frames that occur between each animatino (Change of surface).
            image_params TODO
        """
        super().__init__(id_, position, size, canvas_size)
        #Adding parameters to control a lot of sprites instead of only one
        self.sprites            = []    #Not really sprites, only surfaces
        self.hover_sprites      = []    #Not really sprites, only surfaces
        self.original_sprites   = []    #Not really sprites, only surfaces
        self.ids                = []    
        self.masks              = []
        #Animation
        self.counter            = 0
        self.next_frame_time    = animation_delay
        self.animation_index    = 0
        #Generation
        self.load_sprites(sprite_folder) if sprite_folder else self.add_sprites(*sprite_list)
        self.image              = self.current_sprite()    #Assigning a logical sprite in place of the decoy one of the super()
        self.mask               = self.current_mask()       #Same shit to mask
        self.use_overlay        = False

    def id_exists(self, sprite_id):
        """Check if a id or path has been already loaded.
        Returns:
            (boolean):  True if sprite_id is already loaded, False otherwise."""
        for i in range(0, len(self.ids)):
            if sprite_id == self.ids[i]:    return self.original_sprites[i]
        return False

    def surface_exists(self, sprite_surface):
        """Check if a surface or image has been already loaded.
        Returns:
            (boolean):  True if sprite_surface is already loaded, False otherwise."""
        for i in range(0, len(self.original_sprites)):
            if sprite_surface == self.original_sprites[i]:    
                return self.original_sprites[i]
        return False

    def load_sprites(self, folder):
        """Load all the sprites from a folder, and inserts them in the 3 lists of surfaces that are attributes.
        Only load images.
        Args:
            folder(str):    Path of the folder that contains the surfacess (images) to be loaded."""
        sprite_images = [folder+'\\'+f for f in listdir(folder) if isfile(join(folder, f))]
        for sprite_image in sprite_images:
            if sprite_image.lower().endswith(('.png', '.jpg', '.jpeg', 'bmp')):
                if not self.__id_exists(sprite_image):
                    self.ids.append(sprite_image.lower())
                    self.add_sprite(pygame.image.load(sprite_image))

    def add_sprite(self, surface):
        """Check if a surface is loaded already, and adds it to the attribute lists.
        Args:
            surface (:obj: pygame.Surface): Surface to add."""
        if surface not in self.original_sprites:    self.original_sprites.append(surface)
        self.resize_and_add_sprite(surface, self.rect.size)

    def resize_and_add_sprite(self, surface, size):
        """Resizes a surface to a size, and adds it to the non-original surfaces lists.
        Args:
            surface (:obj: pygame.Surface): Surface to resize and add.
            size (:tuple: int, int):    Size to resize the surface to."""
        self.sprites.append(Resizer.resize_same_aspect_ratio(surface, size))
        self.hover_sprites.append(Resizer.resize_same_aspect_ratio(surface, [int(x*1.5) for x in size]))
        self.masks.append(pygame.mask.from_surface(surface))

    def add_sprites(self, *sprite_surfaces):
        """Gets all the input surfaces, and adds them to the internal lists of surfaces 
        after resizing them. Not the same as load_sprites, this one needs the surfaces already, not a path.
        Args:
            *sprite_surfaces (:obj: pygame.Surface): Surfaces that are to be added separated by commas."""
        if len(sprite_surfaces) < 1:
            raise NotEnoughSpritesException("To create an animated sprite you have to at least add one.")
        for sprite_surf in sprite_surfaces:
            if isinstance(sprite_surf, pygame.sprite.Sprite): sprite_surf = sprite_surf.image
            if not self.__surface_exists(sprite_surf):
                self.ids.append("no_id")
                self.add_sprite(sprite_surf)

    def set_canvas_size(self, canvas_size):
        """Set an internal resolution (NOT SIZE). Updates self.real_rect and self.resolution.
        Clears the internal lists, and resize all the surfaces again to match the old proportion size/resolution.
        Args:
            canvas_size (:tuple: int,int): Resolution to set.
        """
        super().set_canvas_size(canvas_size)    #Changing the sprite size and position to the proper place
        self.clear_lists()
        for surface in self.original_sprites:   self.resize_and_add_sprite(surface, self.rect.size)

    def clear_lists(self):
        """Empty all the internal lists of surfaces and masks, except the original ones (The non-resized).
        To be used after a change in size or something that required new/changed sprites."""
        self.sprites.clear()
        self.hover_sprites.clear()              
        self.masks.clear()

    def animation_frame(self):
        """Changes the current showing surface (changing the index) to the next one."""
        self.animation_index = self.animation_index+1 if self.animation_index < (len(self.sprites)-1) else 0

    def set_size(self, size):
        """Changes the size of all the surfaces that this Sprite contains (except the original ones).
        Args:
            size(:tuple: int, int): New size of the surfaces."""
        super().set_size(size)
        self.clear_lists()
        for surface in self.original_sprites:   self.resize_and_add_sprite(surface, size)
        self.image = self.sprites[0]

    def current_sprite(self):
        """Returns the current surface that will be shown if there are no special states in effect.
        Returns:
            (pygame.Surface):   Surface that should be drawn right now."""
        return self.sprites[self.animation_index]

    def current_hover_sprite(self):
        """Returns the current surface that will be shown if the hover state is True.
        Returns:
            (pygame.Surface):   Hover surface that should be drawn right now."""
        return self.hover_sprites[self.animation_index]

    def current_mask(self):
        """Returns the current surface that will be shown if there are no special states in effect.
        Returns:
            (pygame.Surface):   Surface that should be drawn right now."""
        return self.masks[self.animation_index]

    def update(self):
        """Makes the image flow between surfaces. Compares counter vs animation frame, and if it's time,
        it changes surfaces. To be called each time the sprite is drawn.
        Overloaded method."""
        self.counter += 1
        if self.counter is self.next_frame_time:
            self.counter = 0 
            self.animation_frame()
            self.image = self.current_sprite() if not self.hover else self.current_hover_sprite()

class MultiSprite(Sprite):
    """MultiSprite class. It inherits from Sprite. It is a Sprite formed by a lot of Sprites.
    This allows for more complex shapes and Sprites, like buttons and the such.
    The base surface (background+border) is the image generated in the call to the super() constructor.
    After that, more Sprites are added to build the wanted shape and image.
    Attributes:
        sprites (:list: Sprite):    List of the added sprites, that form the MultiSprite
    """
    def __init__(self, id_, position, size, canvas_size, **image_params):
        """Constructor of MultiSprite. 
        Args:
            id_ (str):  Identifier of the Sprite.
            position (:tuple: int,int): Position of the Sprite in the screen. In pixels.
            size (:tuple: int,int):     Size of the Sprite in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display. In pixels.
            image_params (:dict:):  Dict of keywords and values as parameters to create the self.image attribute.
                                    Variety going from fill_color and use_gradient to text_only.
        """
        super().__init__(id_, position, size, canvas_size, **image_params)
        self.sprites        = pygame.sprite.OrderedUpdates()    #Could use a normal list here, but bah

    def add_sprite(self, sprite):
        """Add sprite to the Sprite list, and blit it to the image of the MultiSprite
        Args:
            sprite (Sprite):    sprite to add."""
        sprite.use_overlay   = False #Not interested in overlays from a lot of sprites at the same time
        self.sprites.add(sprite)
        #LOG.log('debug', "ADDING SPRITE ", sprite.id, " WITH POS ", sprite.rect.topleft)
        self.image.blit(sprite.image, sprite.rect)

    def regenerate_image(self):
        """Generates the image again, blitting the Sprites in the sprite list.
        Intended to be used after changing an important attribute in rect or image.
        Those changes propagate through all the sprites."""
        super().regenerate_image()
        for sprite in self.sprites.sprites():   self.image.blit(sprite.image, sprite.rect)

    def set_size(self, size):
        """Changes the size of the MultiSprite. All the internal Sprites are resized too as result.
        Args;
            size (:tuple: int, int):    New size in pixels."""
        super().set_size(size)    #Changing the sprite size and position to the proper place
        for sprite in self.sprites.sprites():   
            sprite.set_canvas_size(size)

    def set_canvas_size(self, canvas_size):
        """Changes the resolution (NOT SIZE) of the MultiSprite. All the internal Sprites are resized too as result.
        Args;
            canvas_size (:tuple: int, int): New resolution in pixels."""
        super().set_canvas_size(canvas_size)    #Changing the sprite size and position to the proper place
        for sprite in self.sprites.sprites():   
            sprite.set_canvas_size(self.rect.size)
        self.regenerate_image()

    def get_sprite_abs_position(self, sprite):
        """Gets the absolute position of a sprite (in pixels) in the screen, instead of a relative in the 
        bigger MultiSprite image.
        Returns:
            (:tuple: int, int): Absolute position of the sprite in the screen"""
        return tuple(relative+absolute for relative, absolute in zip(sprite.rect.topleft, self.rect.topleft))

    def get_sprite_abs_center(self, sprite):
        """Gets the absolute center position of a sprite (in pixels) in the screen, instead of a relative in the 
        bigger MultiSprite image.
        Returns:
            (:tuple: int, int): Absolute center position of the sprite in the screen"""
        return tuple(relative+absolute for relative, absolute in zip(sprite.rect.topleft, self.rect.topleft))

    def get_sprite(self, *keywords):
        """Returns a sprite that matches the keywords.
        Args:
            *keywords (str): keywords that the sprite must contain, separated by commas.
        Returns:
            (Sprite | None):    The Sprite if its found, else None."""
        for sprite in self.sprites.sprites():
            if all(kw in sprite.id for kw in keywords): return sprite

    def add_text_sprite(self, id_, text, alignment="center", text_size=None, **params): 
        '''Generates and adds sprite-based text object following the input parameters.
        Args:
            id_ (str):  Identifier of the TextSprite
            text (str): Text to add
            alignment (str):   To set type of centering for the text. Center, Left, Right.
            text_size (int):    Size of the font (height in pixels).
            params (:dict:):    Dict of keywords and values as parameters to create the TextSprite
                                text_color, e.g.
        '''
        size = self.rect.size if text_size is None else text_size
        #The (0, 0) relative positoin is a decoy so the constructor of textsprite doesn't get cocky
        text = TextSprite(id_, (0, 0), size, self.rect.size, text, **params)
        #We calculate the center AFTER because the text size may vary due to the badly proportionated sizes.W
        center = tuple(x//2 for x in self.rect.size) if 'center' in alignment.lower() else\
        (text.rect.width//2, self.rect.height//2) if 'left' in alignment.lower() else\
        (self.rect.width-text.rect.width//2, self.rect.height//2)
        #With the actual center according to the alignment, we now associate it
        text.rect.center = center
        text.set_position(text.rect.topleft) #To reset the real_rect argument
        self.add_sprite(text)  