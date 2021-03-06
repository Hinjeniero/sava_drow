"""--------------------------------------------
sprite module. Contains classes that work as a layer over the pygame.Sprite.sprite class.
Have the following classes, inheriting represented by tabs:
    Sprite
        ↑TextSprite
        ↑AnimatedSprite
        ↑MultiSprite
--------------------------------------------"""

__all__ = ['Sprite', 'TextSprite', 'AnimatedSprite', 'MultiSprite']
__version__ = '1.0'
__author__ = 'David Flaity Pardo'

#Python libraries
import pygame
import time
from os import listdir
from os.path import isfile, join, dirname
#External libraries
import external.gradients as gradients
import external.ptext as ptext
#Selfmade libraries
from settings import MESSAGES
from obj.utilities.colors import WHITE, BLACK, RED, LIGHTGRAY, DARKGRAY
from obj.utilities.resizer import Resizer
from obj.utilities.utility_box import UtilityBox
from obj.utilities.exceptions import  ShapeNotFoundException, NotEnoughSpritesException,\
                                    BadSpriteException
from obj.utilities.logger import Logger as LOG
from obj.utilities.synch_dict import Dictionary
from obj.utilities.surface_loader import SurfaceLoader, ResizedSurface
from obj.utilities.decorators import run_async
from strings import FONT
#from memory_profiler import profile

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
        Params dict attributes:
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
        self.image          = None  #Created in Sprite.generate
        self.overlay        = None  #Created in Sprite.generate
        self.mask           = None  #Created in Sprite.generate
        #Additions to interesting funcionality-------
        self.abs_position   = None  #Absolute position, in case that we want to draw it from a multisprite
        self.real_rect      = None  #Created in Sprite.generate
        self.rects          = {}  #Created to blit onto another surfaces when needed.
        self.resolution     = canvas_size      
        #Animation and showing-----------------------
        self.animation_value= 0
        self.animation_step = ANIMATION_STEP
        #States
        self.active         = False
        self.hover          = False
        self.enabled        = True
        self.use_overlay    = True
        self.visible        = True
        self.dialog_active  = False #This has the function of adding information to an otherwise element with a not-so-clear purpose
        #Generation
        Sprite.generate(self)   #TO AVOID CALLING THE SUBCLASSES GENERATE WHEN THEIR ATTRIBUTES ARENT INITIALIZED YET.

    @staticmethod
    def generate(self):
        """Generates the complex attributes of the sprite. The image, overlay and mask are created here."""
        self.image, self.overlay = Sprite.generate_surface(self.rect, **self.params)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.size = self.image.get_size()  #In the case that the image has changed sizes when resizing
        self.real_rect = (tuple([x/y for x,y in zip(self.rect.topleft, self.resolution)]),\
                        tuple([x/y for x,y in zip(self.rect.size, self.resolution)]))
        self.rects[self.resolution] = self.rect.copy() 

    def get_id(self):
        """Returns the id of this sprite."""
        return self.id
        
    def draw(self, surface, offset=None):
        """Draws the sprite over a surface. Draws the overlay too if use_overlay is True.
        Args:
            surface (:obj: pygame.Surface): Surface to draw the Sprite. It's usually the display.
            offset (Container: int, int, default=None): Offset in pixels to be taken into account when drawing.
        """
        if offset and offset == (0, 0): offset=None
        if self.visible:
            try:
                position = self.abs_position if self.abs_position else self.rect.topleft
                if offset:
                    surface.blit(self.image, tuple(off+pos for off, pos in zip(offset, position)))
                else:
                    surface.blit(self.image, position)
                if (self.overlay and self.use_overlay and self.active) or not self.enabled:    
                    self.draw_overlay(surface, offset=offset)               
                if self.enabled:
                    self.update()
            except pygame.error:
                LOG.log(*MESSAGES.LOCKED_SURFACE_EXCEPTION)

    def update_mask(self):
        """Updates the mask attribute afther the image attribute. To use after a change in self.image."""
        self.mask = pygame.mask.from_surface(self.image)

    def draw_overlay(self, surface, offset=None):
        """Draws the overlay over a surface.
        Args:
            surface (:obj: pygame.Surface): Surface to draw the Sprite. It's usually the display
        """
        position = self.abs_position if self.abs_position else self.rect.topleft
        if offset:
            surface.blit(self.overlay, tuple(off+pos for off, pos in zip(offset, position)))
        else:
            surface.blit(self.overlay, position)
        if self.enabled:
            self.animation_frame()

    def get_canvas_size(self):
        """Returns the current resolution size that this Sprite has. THIS IS NOT THE SIZE OF THE SPRITE.
        Returns:
            tuple(int, int):    Resolution/canvas size of this Sprite."""
        return self.resolution

    def set_canvas_size(self, canvas_size):
        """Set a new resolution for the container element (Can be the screen itself). 
        Updates self.real_rect and self.resolution.
        Args:
            canvas_size (Tuple-> int,int): Resolution to set.
        """
        self.resolution = canvas_size
        try:
            rect = self.rects[self.resolution]
        except KeyError:
            new_position    = tuple([int(x*y) for x,y in zip(self.real_rect[0], canvas_size)]) 
            new_size        = tuple([int(x*y) for x,y in zip(self.real_rect[1], canvas_size)])
            rect            = pygame.Rect(new_position, new_size)
            self.rects[self.resolution] = rect
        self.set_rect(rect, update_rects=False)
        #LOG.log('debug', "Succesfully changed sprite ", self.id, " to ", self.rect.size, ", due to the change to resolution ", canvas_size)

    def set_size(self, size, update_rects=True, regenerate_image=True):
        """Changes the size of the Sprite. Updates rect and real_rect, and changes image and mask to match the size.
        Args:
            update_rects (boolean, default:True):   Flag. If its true, the real rect attributes will be updated after the input position.
            size (:obj: pygame.Rect||:tuple: int,int):  New size of the Sprite. In pixels.
            regenerate_image (boolean, default:True):   Flag. True makes the sprite regenerate its image when this method is called.
        """
        self.rect.size = size
        if update_rects:
            self.real_rect  = (self.real_rect[0], tuple(x/y for x,y in zip(size, self.resolution)))
            self.rects[self.resolution] = self.rect.copy()
        if regenerate_image:
            self.regenerate_image()

    def set_position(self, position, update_rects=True):
        """Changes the position of the Sprite. Updates rect and real_rect.
        Args:
            position (:obj: pygame.Rect||:tuple: int,int): New position of the Sprite. In pixels.
            update_rects (boolean, default:True):   Flag. If its true, the real rect attributes will be updated after the input position.
        """
        if self.abs_position:
            difference = tuple(x-y for x, y in zip(position, self.rect.topleft))
            self.abs_position = tuple(x+y for x, y in zip(self.abs_position, difference))
        self.rect.topleft = position
        if update_rects:
            self.real_rect  = (tuple(x/y for x,y in zip(position, self.resolution)), self.real_rect[1])
            self.rects[self.resolution] = self.rect.copy()

    def set_rect(self, rect, update_rects=True):
        """Sets a new Rect as the Sprite rect. Uses the rect.size and rect.topleft to change size and position
        Only executes set_position and set_size if the position or size of the rect is different from the original one. """
        if self.rect.topleft != rect.topleft:   
            self.set_position(rect.topleft, update_rects)
        if self.rect.size != rect.size:         
            self.set_size(rect.size, update_rects)

    def set_center(self, center):
        """Changes the center of the Sprite. Updates rect and real_rect.
        Args:
            center (:obj: pygame.Rect||:tuple: int,int):    New position of the Sprite. In pixels.
        """
        if self.rect.topleft != center:
            new_pos = tuple(x-y//2 for x,y in zip(center, self.rect.size))
            self.set_position(new_pos)    #To update the real rect

    def set_active(self, active):
        """Sets the visible attribute. Can be used for differen purposes.
        Args:
            active (boolean): The value to set.
        """
        self.active = active

    def set_hover(self, hover):
        """Sets the active attribute. Should be True if the mouse is hovering the Sprite.
        Args:
            hover (boolean): The value to set.
        """
        self.hover = hover
          
    def set_enabled(self, enabled):
        """Sets the enabled attribute. If enabled is False, the element will be deactivated.
        No event or action will be sent or registered. Also, a semitransparent grey color will be blitted.
        Changes to this attribute regenerate the image and use surfaces, and so it will be slow.
        Args:
            enabled (boolean): The value to set.
        """
        if not enabled and self.enabled:      #Deactivating button
            self.overlay.set_alpha(200)
            self.enabled        = False
        elif enabled and not self.enabled:    #Activating button
            self.enabled        = True

    def set_visible(self, visible):
        """Sets the visible attribute. This attribute is used to draw or not the Sprite.
        Args:
            visible (boolean): The value to set.
        """
        self.visible = visible
        
    def enable_overlay(self, enabled):
        """Sets the use_overlay attribute. If True, the overlay will be used.
        Args:
            enabled (boolean): The value to set.
        """
        self.use_overlay = enabled

    def delete_overlay(self):
        """To save memory. Only to use if we won't use it in any case.
        Can be generated again using regenerate."""
        self.overlay = None
        self.use_overlay = False

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
        Also updates the mask. Intended to be used after changing an important attribute in rect or image.
        Called after an important change in resolution or the sprite params."""
        self.image, self.overlay = Sprite.generate_surface(self.rect, **self.params)
        self.update_mask()
        if not self.enabled and self.use_overlay:
            self.overlay.set_alpha(200)

    @staticmethod
    def generate_surface(size, surface=None, texture=None, overlap_texture=None, active_texture=None, keep_aspect_ratio=True, resize_mode='fit', resize_smooth=True,\
                        only_text=False, text="default_text", text_color=WHITE, text_font=FONT, text_outline=1, text_outline_color=BLACK, text_shadow_dir=(0.0, 0.0), text_lines=1,\
                        shape="Rectangle", transparent=False, fill_color=RED, fill_gradient=True, gradient=(LIGHTGRAY, DARKGRAY), gradient_type="horizontal", angle=None,\
                        overlay=True, overlay_color=WHITE, border=True, border_color=WHITE, border_width=2, **unexpected_kwargs):
        """Generates a pygame surface according to input arguments.
        Args:
            size (:obj: pygame.Rect | Tuple-> int,int):  Dimensions of the surface (width, height)
            surface (:obj: pygame.Surface, default=None): 
            texture (string):   Path of the image to be loaded as a texture 
            overlap_texture (:obj: pygame.Surface, default=None): 
            active_texture (:obj: pygame.Surface, default=None): 
            keep_aspect_ratio (boolean, default=False): True if we want the original aspect ratio to be kept when loaded and resized. 
                                                        False otherwise (False can output severely distorted images, depending on settings).
            resize_mode (String, default='fit'): Mode used when changing the input texture size. It can be two modes:
                                'fit':  The image will adjust itself to the closer size to the input size as possible, without
                                        exceeding it.
                                'fill': The image will adjust itself to the closer size to the input size as possible, without 
                                        any axis being lower than it, effectively 'filling' all the image. If the aspect ratio is to 
                                        be kept, the results may vary.
            resize_smooth (boolean, default=True):  If this flag is true, the resizing will be done smoothing the borders. 
                                                    If its false, the resizing will keep the image 'as-is', and as pixelated as 
                                                    the result could be.
            only_text (boolean):    True if we want the surface to only contains a text with a transparent background.
            text (string):  The text to draw. Used if only_text is True. 
            text_color (Tuple-> int, int, int): RGB Color of the text. Used if only_text is True.
            text_font (pygame.font):    Font used when rendering the text. Used if only_text is True.
            text_outline (int, default=1):  Width of the outline of the rendered text.
            text_outline_color (Tuple-> int, int, int): Outline of the rendered text.
            text_shadow_dir (Tuple-> float, float): Direction of the shadow of the rendered text.
            text_lines (int):   Text lines that the rendered text will be divided into.
            shape (String): Shape of the surface. Options are circle and rectangle.
            transparent (boolean):  Flag that decides if to add transparency or not. Only works with circles.
            fill_color (Tuple-> int, int, int): RGB color of the surface background. Used if fill_gradient is False. 
            fill_gradient (boolean):    True if we want a gradient instead of a solid color in the .
            gradient (Tuple-> 2 Tuples-> int, int, int):   Interval of RGB colors of the gradient. (start, end). 
            gradient_type (string): direction of the gradient. Options are Horizontal and Vertical. Used if gradient is True.
            angle (default=None): Rotation to apply to the result. Only works well with multiples of 90.
            ----
            overlay (boolean):  Flag that says if an overlay will be generated and returned or not.
            overlay_color (Tuple-> int, int, int):  RGB color of the overlay.
            border (boolean):   True if the surface generated has a border.
            border_color (Tuple-> int, int, int):   Color of the border. RGBA/RGB format.
            border_width (int):  Size of the border in pixels.
            **unexpected_kwargs (Dict-> Any:Any):   Just there to not raise an error if unexpected keywords are received.
        Returns:
            (:obj: pygame.Surface): Surface generated following the keywords"""
        text = str(text)
        text_font = FONT if not text_font else text_font
        size    = size.size if isinstance(size, pygame.rect.Rect) else size
        if surface:     #If we creating the sprite from an already created surface
            surf    = Resizer.resize(surface, size, mode=resize_mode, smooth=resize_smooth)  
        elif texture:   #If we get a string with the path of a texture to load onto the surface
            surf    = ResizedSurface.get_surface(texture, size, resize_mode, resize_smooth, keep_aspect_ratio)
        elif only_text: #If the surface is only a text with transparent background
            if text_lines > 1:
                surf = ptext.draw(text, (0, 0), fontsize=Resizer.max_font_size(text, (size[0]*text_lines, size[1]//text_lines), text_font), fontname=text_font,\
                                owidth=text_outline, ocolor=text_outline_color, shadow=text_shadow_dir, width=size[0], surf=None)[0]
            else:
                surf = ptext.draw(text, (0, 0), fontsize=Resizer.max_font_size(text, size, text_font), fontname=text_font,\
                                owidth=text_outline, ocolor=text_outline_color, shadow=text_shadow_dir, surf=None)[0]
                #surf   = pygame.font.Font(text_font, Resizer.max_font_size(text, size, text_font)).render(text, True, text_color)
        else:           #In the case of this else, means we dont have a texture nor a text, and have to generate the shape
            shape   = shape.lower()
            surf    = pygame.Surface(size)
            if 'circ' in shape:
                radius  = size[0]//2
                #Gradient
                if fill_gradient:   
                    surf = gradients.radial(radius, gradient[0], gradient[1])
                else:  
                    if transparent: #Dont draw the circle itself, only border
                        UtilityBox.add_transparency(surf, border_color)
                    else:           #Draw the circle insides too
                        UtilityBox.add_transparency(surf, fill_color, border_color)
                        pygame.draw.circle(surf, fill_color, (radius, radius), radius, 0)
                #Border
                if border:          
                    pygame.draw.circle(surf, border_color, (radius, radius), radius, border_width)
                    #pygame.draw.circle(overlay, overlay_color, (radius, radius), radius, 0)
            elif 'rect' in shape:
                if fill_gradient:   
                    surf = gradients.vertical(size, gradient[0], gradient[1]) if 'vertical' in gradient_type\
                    else gradients.horizontal(size, gradient[0], gradient[1])
                else:               
                    surf.fill(fill_color)
                if border:          
                    pygame.draw.rect(surf, border_color, pygame.rect.Rect((0,0), size), border_width)
            else:
                raise ShapeNotFoundException("Available shapes: Rectangle, Circle. "+shape+" is not recognized")
        if overlap_texture:
            surf = UtilityBox.overlap_trace_texture(surf, overlap_texture)
        #End of the generation/specification of the pygame.Surface surf.
        if angle:   #Only use this with multiples of 90!!
            surf = pygame.transform.rotate(surf, angle)
        if overlay:
            if active_texture:
                overlay = ResizedSurface.get_surface(texture, size, resize_mode, resize_smooth, keep_aspect_ratio)
            else:
                overlay = Sprite.generate_overlay(surf, overlay_color)
            return surf, overlay
        else:
            return surf, None

    def rects_to_str(self, return_luts_too=False):
        result = 'Id: '+self.id+', Position: '+str(self.rect.topleft)+', Size: '+str(self.rect.size)+\
                '\nReal rect pos: '+str(self.real_rect[0])+', Real rect size: '+str(self.real_rect[0])
        if return_luts_too:
            return result+'\nLut table of rects:\n '+str(self.rects)
        return result

    @staticmethod
    def generate_overlay(surf, color):
        """Generates and returns a matching overlay for the input surface."""
        overlay = surf.copy()
        overlay.fill(color, special_flags=pygame.BLEND_ADD)
        colorkey = UtilityBox.get_alike_colorkey(color)
        return UtilityBox.convert_to_colorkey_alpha(overlay, colorkey=colorkey)

class TextSprite(Sprite):
    """Class TextSprite. Inherits from Sprite, and the main surface is a text, from pygame.font.render.
    General class attributes: #Can be overloaded in **params
        text_font (:obj: pygame.font):  font to use when rendering the text. Default is None.
        text_color (:tuple: int, int, int): RGB Color of the text. Default is white (255, 255, 255).
    Attributes:
        text (str): Text that will be drawn.
    """
    __default_config = {'text_font'     : FONT,
                        'text_color'    : WHITE,
                        'text_outline'  : 1,
                        'text_outline_color': BLACK,
                        'text_shadow_dir': (0.0, 0.0),
                        'text_lines'    : 1
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
        params['only_text'] = True
        params['text'] = text
        super().__init__(id_, position, size, canvas_size, **params)
        self.text = text
        TextSprite.generate(self)

    @staticmethod
    def generate(self):
        """Generate method, executed in each constructor."""
        UtilityBox.join_dicts(self.params, TextSprite.__default_config) 
        self.set_size(self.image.get_size())    #The size can change in texts from the initial one

    def set_text(self, text):
        """Changes the text of the TextSprite, and regenerates the image to show the changes.
        Args:
            text (string): Text to set in the Sprite.
        """
        if text is not self.text:
            self.text           = text
            self.params['text'] = text
            self.regenerate_image()

    def regenerate_image(self):
        """Generates the image and overlay again, following the params when the constructor executed.
        Also updates the mask. Intended to be used after changing an important attribute in rect or image.
        Called after an important change in resolution or the sprite params."""
        self.image, self.overlay = Sprite.generate_surface(self.rect, **self.params)
        self.update_mask()
        if not self.enabled and self.use_overlay:
            self.overlay.set_alpha(200)

class MultiSprite(Sprite):
    """MultiSprite class. It inherits from Sprite. It is a Sprite formed by a lot of Sprites.
    This allows for more complex shapes and Sprites, like buttons and the such.
    The base surface (background+border) is the image generated in the call to the super() constructor.
    After that, more Sprites are added to build the wanted shape and image.
    Attributes:
        sprites (:list: Sprite):    List of the added sprites, that form the MultiSprite
    """
    __default_config = {'fade_animation': False,
                        'animation_frames': 30,
                        'animation_direction': 'up'
    }
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
        self.sprites        = pygame.sprite.OrderedUpdates()
        self.in_animation   = False
        self.hover_dialog   = None
        self.dialog_animated= False

    def add_hover_dialog(self, dialog_text, animated=False, dialog_texture=None, dialog_size=None, text_color=WHITE, dialog_lines=1, text_outline=1,\
                        text_outline_color=BLACK, text_shadow_dir=(0.0, 0.0), text_font=FONT, **dialog_kwargs):
        """Creates and adds a hover dialog to this element, that will show information about this sprite."""
        if dialog_text:
            size = dialog_size if dialog_size else self.rect.size
            self.dialog_animated = animated
            self.hover_dialog = MultiSprite(self.id+'_hover_dialog', (0, 0), size, self.rect.size, texture=dialog_texture, resize_mode='fill', **dialog_kwargs)
            self.hover_dialog.set_position(tuple(x//2 - y//2 for x,y in zip(self.rect.size, self.hover_dialog.rect.size)))
            self.add_sprite(self.hover_dialog)
            self.hover_dialog.add_text_sprite(self.id+'_hover_dialog_text', dialog_text, text_size=self.hover_dialog.rect.size, text_font=text_font, text_lines=dialog_lines,\
                                            text_outline=text_outline, text_color=text_color, text_outline_color=text_outline_color, text_shadow_dir=text_shadow_dir)
            self.hover_dialog.set_alpha(0)
            self.hover_dialog.visible = False

    def set_alpha(self, alpha):
        """Changes the alpha of the image of this sprite."""
        self.image.set_alpha(alpha)
        for sprite in self.sprites:
            sprite.image.set_alpha(alpha)

    def add_sprite(self, sprite, add_to_sprite_list=True):
        """Add sprite to the Sprite list, and blit it to the image of the MultiSprite
        Args:
            sprite (Sprite):    sprite to add."""
        sprite.use_overlay = False #Not interested in overlays from a lot of sprites at the same time
        sprite.abs_position = self.get_sprite_abs_position(sprite)
        if add_to_sprite_list:
            self.sprites.add(sprite)

    def set_size(self, size, update_rects=True):
        """Changes the size of the MultiSprite. All the internal Sprites are resized too as result.
        Args;
            size (:tuple: int, int):    New size in pixels."""
        super().set_size(size, update_rects=update_rects)    #Changing the sprite size and position to the proper place
        for sprite in self.sprites:
            sprite.set_canvas_size(self.rect.size)

    def set_position(self, position, update_rects=True):
        """Changes the position of the Sprite. Updates rect and real_rect.
        Args:
            position (:obj: pygame.Rect||:tuple: int,int): New position of the Sprite. In pixels.
            update_rects (boolean, default:True):   Flag. If its true, the real rect attributes will be updated after the input position.
        """
        super().set_position(position, update_rects=update_rects)    #Changing the sprite size and position to the proper place
        for sprite in self.sprites:
            sprite.abs_position = self.get_sprite_abs_position(sprite)

    def get_sprite_abs_position(self, sprite):
        """Gets the absolute position of a sprite (in pixels) in the screen, instead of a relative in the 
        bigger MultiSprite image.
        Returns:
            (:tuple: int, int): Absolute position of the sprite in the screen"""
        position = self.abs_position if self.abs_position else self.rect.topleft
        return tuple(relative+absolute for relative, absolute in zip(sprite.rect.topleft, position))

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
        for sprite in self.sprites:
            if all(kw in sprite.id for kw in keywords): 
                return sprite

    def add_text_sprite(self, id_, text, alignment="center", text_size=None, return_result=False, **params): 
        '''Generates and adds sprite-based text object following the input parameters.
        Args:
            id_ (str):  Identifier of the TextSprite
            text (str): Text to add
            alignment (str):   To set type of centering for the text. Center, Left, Right.
            text_size (:tuple: int, int):    Size of the text in pixels.
            params (:dict:):    Dict of keywords and values as parameters to create the TextSprite
                                text_color, e.g.
        '''
        size = self.rect.size if not text_size else text_size
        #The (0, 0) relative positoin is a decoy so the constructor of textsprite doesn't get cocky
        text = TextSprite(id_, (0, 0), size, self.rect.size, text, **params)
        #We calculate the center AFTER because the text size may vary due to the badly proportionated sizes.W
        center = tuple(x//2 for x in self.rect.size) if 'center' in alignment.lower() else\
        (text.rect.width//2, self.rect.height//2) if 'left' in alignment.lower() else\
        (self.rect.width-text.rect.width//2, self.rect.height//2)
        #With the actual center according to the alignment, we now associate it
        text.set_center(center)
        if return_result:
            return text
        else:
            self.add_sprite(text)

    def set_canvas_size(self, canvas_size):
        """Set a new resolution for the container element (Can be the screen itself). 
        Updates self.real_rect and self.resolution. Also sets the canvas_size of the contained sprites
        to the new size of this element.
        Args:
            canvas_size (Tuple-> int,int): Resolution to set.
        """
        super().set_canvas_size(canvas_size)
        for sprite in self.sprites:
            sprite.set_canvas_size(self.rect.size)
            sprite.abs_position = self.get_sprite_abs_position(sprite)

    def draw(self, surface, offset=None):
        """Draws the sprite over a surface. Draws the overlay too if use_overlay is True.
        Args:
            surface (:obj: pygame.Surface): Surface to draw the Sprite. It's usually the display.
            offset (Container: int, int, default=None): Offset in pixels to be taken into account when drawing.
        """
        if self.visible:
            super().draw(surface, offset=offset)
            for sprite in self.sprites:
                sprite.draw(surface, offset=offset)
                
    def update(self):
        """Updates the information about the sprite. Called after each drawing onto the screen."""
        if self.hover_dialog:
            dialog_alpha = self.hover_dialog.image.get_alpha()
            if self.dialog_active:
                if dialog_alpha < 255:
                    dialog_alpha = dialog_alpha+3 if self.dialog_animated else 255
                    if dialog_alpha > 255: dialog_alpha = 255
                    self.hover_dialog.image.set_alpha(dialog_alpha)
            elif self.hover_dialog.visible:
                if dialog_alpha > 0:
                    dialog_alpha = dialog_alpha-3 if self.dialog_animated else 0
                    if dialog_alpha <= 0: 
                        dialog_alpha = 0
                        self.hover_dialog.visible = False
                    self.hover_dialog.image.set_alpha(dialog_alpha)

    def show_help_dialog(self):
        """Shows the hover dialog, if it has been added previously."""
        if self.hover_dialog:
            self.dialog_active = True
            self.hover_dialog.visible = True
            
    def hide_help_dialog(self):
        """Hides the hover dialog, if it has been added previously."""
        if self.hover_dialog:
            self.dialog_active = False

class AnimatedSprite(MultiSprite):
    """Class AnimatedSprite. Inherits from Sprite. Adds all the attributes and methods needed to support
    the funcionality of a classic animated sprite, like a list of surfaces and a setted delay to change between them.
    General class surfaces:

    Args:
        surfaces (:list: pygame.Surface):    List of surfaces. Normal size.
        hover_surfaces (:list: pygame.Surface):  List of surfaces to use when hover is True. Size is normal*2
        original_surfaces (:list: pygame.Surface):   List of surfaces without resizing. Kept original image size.
        ids (:list: strings):   List of paths of the loaded images.
        masks (:list: pygame.Mask): List of masks to control collision. Match with surfaces following the list order.
        counter (int):  Counter that controls when to change to the next surface. Works together with next_frame_time.
        next_frame_time (int):  Number of times that draw is called before changing surface to the next one.
        animation_index (int):  Current index in the surfaces and mask lists.
    """
    __default_config = {'hover_ratio'   : 1.75,
                        'boomerang_loop': False,
                        'initial_surfaces': (),
                        'hover_surfaces': False,
                        'sprite_folder' : None,
                        'keywords'      : (),
                        'animation_delay':10, 
                        'resize_mode'   :'fit', 
                        'resize_smooth' :True,
                        'keep_aspect_ratio': True,
                        'keywords_strict' : False,
                        'border': False,
                        'border_color': RED,
                        'border_width': 2
    }
    def __init__(self, id_, position, size, canvas_size, **params):
        """Constructor of AnimatedSprite. 
        Args:
            id_ (str):  Identifier of the Sprite.
            position (:tuple: int,int): Position of the Sprite in the screen. In pixels.
            size (:tuple: int,int):     Size of the Sprite in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display. In pixels.
            *sprite_list (:obj: pygame.Surface):    Surfaces that are to be added separated by commas.
            folder (str):    Path of the folder that contains the surfaces to be loaded.
            animation_delay (int):  Frames that occur between each animatino (Change of surface).
        """
        super().__init__(id_, position, size, canvas_size, **params)
        #Adding parameters to control a lot of surfaces instead of only one
        self.names              = []    #Its used to control the state machine
        self.surfaces           = []
        self.hover_surfaces     = []
        self.masks              = []
        #Animation
        self.locked             = False
        self.counter            = 0
        self.animated           = True
        self.animation_step     = 1
        self.next_frame_time    = None  #In generate
        self.animation_index    = 0
        #Generation
        AnimatedSprite.generate(self)

    @staticmethod
    def generate(self):
        """Generate method, called in the construction of each instance.
        Initializes the complex attributes, and loads the stream of images and frames that
        will compose this animated sprite."""
        UtilityBox.join_dicts(self.params, AnimatedSprite.__default_config)
        self.use_overlay = False
        self.next_frame_time = self.params['animation_delay']
        if self.params['hover_surfaces']:
            self.params['hover_size'] = tuple(x*self.params['hover_ratio'] for x in self.rect.size)
        if self.params['sprite_folder']:
            self.load_surfaces()
        else:
            self.add_surfaces()
        self.update_size()
        self.image  = self.current_sprite()     #Assigning a logical sprite in place of the decoy one of the super()
        self.mask   = self.current_mask()       #Same shit to mask
        if len(self.surfaces) <= 1:             #If we want to be able to switch between sprites
            self.animated = False

    def update_size(self):
        """Due to the resizer, we have to check the new size of this sprite."""
        size = (0, 0)
        for surface in self.surfaces:
            size = (max(size[0], surface.get_width()), max(size[1], surface.get_height()))
        self.rect.size = size
 
    def load_surfaces(self):#, folder, keywords=None, resize_mode='fit', resize_smooth=True):
        """Load all the sprites from a folder, and inserts them in the 2 lists of surfaces that are attributes.
        Only load images.
        Args:
            folder(str):    Path of the folder that contains the surfaces (images) to be loaded."""
        _ = self.params
        surfaces = ResizedSurface.load_surfaces(_['sprite_folder'], self.rect.size, _['resize_mode'], _['resize_smooth'],\
                                                _['keep_aspect_ratio'], *_['keywords'], strict=_['keywords_strict'])
        if self.params['hover_surfaces']:
            hover_surfaces = ResizedSurface.load_surfaces(_['sprite_folder'], _['hover_size'], _['resize_mode'], _['resize_smooth'],\
                                                        _['keep_aspect_ratio'], *_['keywords'], strict=_['keywords_strict'])
        for path in surfaces.keys():
            if path not in self.names:
                self.names.append(path)
            if self.params['hover_surfaces']:
                self.add_surface(surfaces[path], hover_surfaces[path])
            else:
                self.add_surface(surfaces[path], None)

    def add_surfaces(self):
        """Gets, resizes the surfaces from the param list 'initial_surfaces', and adds them to the animated sprite."""
        #CHECKING the type
        for image in self.params['initial_surfaces']:
            if isinstance(image, str):  #It's a path
                surface = ResizedSurface.get_surface(image, self.rect.size, _['resize_mode'],\
                                                    _['resize_smooth'], _['keep_aspect_ratio'])
            elif isinstance(image, pygame.Surface): #It's a surface
                surface = image
            elif isinstance(image, pygame.sprite.Sprite):   #It's a sprite
                surface = image.image
            else:   #The fuck is this
                raise BadSpriteException("Can't add a sprite of type "+str(type(image)))
            #Doing the actual work
            if surface not in self.surfaces:
                hover_surface = None
                _ = self.params
                surface = Resizer.resize(surface, self.rect.size, _['resize_mode'], _['resize_smooth'],\
                                        _['keep_aspect_ratio'])
                if self.params['hover_surfaces']:
                    hover_surface = Resizer.resize(surface, _['hover_size'], _['resize_mode'],\
                                                    _['resize_smooth'], _['keep_aspect_ratio'])
                self.add_surface(surface, hover_surface)
                
    def add_surface(self, surface, hover_surface):
        """Adds the input surfaces it to the non-original surfaces lists.
        Args:
            surface (:obj: pygame.Surface): Surface to add.
            hover_surface (:obj: pygame.Surface):   Hover Surface to add."""
        #Checking the border parameter
        if self.params['border']:
            surface = UtilityBox.draw_border(surface, self.params['border_color'], self.params['border_width'])
            if hover_surface:
                hover_surface = UtilityBox.draw_border(hover_surface, self.params['border_color'], self.params['border_width'])
        self.surfaces.append(surface)
        if hover_surface:
            self.hover_surfaces.append(hover_surface)
        self.masks.append(pygame.mask.from_surface(surface))

    def set_size(self, size, update_rects=True):
        """Changes the size of all the surfaces that this Sprite contains (except the original ones).
        Args:
            size(:tuple: int, int): New size of the surfaces."""
        super().set_size(size, update_rects=update_rects)
        self.params['hover_size'] = tuple(x*self.params['hover_ratio'] for x in self.rect.size)
        self.clear_lists()
        if self.params['sprite_folder']:
            self.load_surfaces()
        else:
            self.add_surfaces()
        self.update_size()
        self.image  = self.current_sprite()
        self.mask   = self.current_mask() 

    def clear_lists(self):
        """Empty all the internal lists of surfaces and masks, except the original ones (The non-resized).
        To be used after a change in size or something that required new/changed surfaces."""
        self.surfaces.clear()
        self.hover_surfaces.clear()              
        self.masks.clear()

    def animation_frame(self):
        """Changes the current showing surface (changing the index) to the next one."""
        if self.animated and not self.locked:   #If more than 1 sprites in the list
            self.animation_index += self.animation_step
            if self.animation_index >= len(self.surfaces):
                if not self.params['boomerang_loop']:
                    self.animation_index = 0
                else:
                    self.animation_step = -self.animation_step
                    self.animation_index = len(self.surfaces)-2
            elif self.animation_index < 0:
                if not self.params['boomerang_loop']:
                    self.animation_index = len(self.surfaces)-1
                else:
                    self.animation_step = -self.animation_step
                    self.animation_index = 1        

    def set_hover(self, hover):
        """Sets the hover state of the sprite.
        Also changes the showing sprite if its needed. (Sprites when hovering are bigger)."""
        super().set_hover(hover)
        if hover:
            self.image = self.current_hover_sprite()
        else:
            self.image = self.current_sprite()

    def current_sprite(self):
        """Returns the current surface that will be shown if there are no special states in effect.
        Returns:
            (pygame.Surface):   Surface that should be drawn right now."""
        try:
            return self.surfaces[self.animation_index]
        except IndexError:
            self.animation_index = 0
            return self.surfaces[self.animation_index]

    def current_hover_sprite(self):
        """Returns the current surface that will be shown if the hover state is True.
        Returns:
            (pygame.Surface):   Hover surface that should be drawn right now."""
        if self.params['hover_surfaces']:
            try:
                return self.hover_surfaces[self.animation_index]
            except IndexError:
                self.animation_index = 0
                return self.hover_surfaces[self.animation_index]
        else:
            return self.current_sprite()

    def current_mask(self):
        """Returns the current surface that will be shown if there are no special states in effect.
        Returns:
            (pygame.Surface):   Surface that should be drawn right now."""
        try:
            return self.masks[self.animation_index]
        except IndexError:
            self.animation_index = 0
            return self.masks[self.animation_index]

    def update(self):
        """Makes the image flow between surfaces. Compares counter vs animation frame, and if it's time,
        it changes surfaces. To be called each time the sprite is drawn.
        Overloaded method."""
        self.counter += 1
        if self.counter >= self.next_frame_time:
            self.counter = 0 
            self.animation_frame()
            self.image = self.current_sprite() if not self.hover else self.current_hover_sprite()

class OnceAnimatedSprite(AnimatedSprite):
    """Class OnceAnimatedSprite. Inherits from AnimatedSprite. The difference between it and the super class is
    that this one only play once before stopping. """

    def __init__(self, id_, position, size, canvas_size, **params):
        """OnceAnimatedSprite constructor."""
        super().__init__(id_, position, size, canvas_size, **params)
    
    def animation_frame(self):
        """Changes the current showing surface (changing the index) to the next one."""
        if self.animated:   #If more than 1 sprites in the list
            self.animation_index += self.animation_step
            if self.animation_index >= len(self.surfaces):
                if self.params['boomerang_loop']:
                    self.animation_index = len(self.surfaces)-2
                    self.animation_step = -self.animation_step
                else:
                    self.set_enabled(False)
            elif self.animation_index == 0:
                self.set_enabled(False)

    def set_enabled(self, state):
        """Sets the enabled state of this sprite."""
        super().set_enabled(state)
        self.set_visible(state)
        self.animation_index = 0
