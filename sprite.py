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
from exceptions import  ShapeNotFoundException, NotEnoughSpritesException,\
                        BadSpriteException
from logger import Logger as LOG
from synch_dict import Dictionary
from utility_box import UtilityBox
from surface_loader import SurfaceLoader, ResizedSurface
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
        self.image          = None  #Created in Sprite.generate
        self.overlay        = None  #Created in Sprite.generate
        self.mask           = None  #Created in Sprite.generate
        #Additions to interesting funcionality-------
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
        #Generation
        Sprite.generate(self)   #TO AVOID CALLING THE SUBCLASSES GENERATE WHEN THEIR ATTRIBUTES ARENT INITIALIZED YET.

    @staticmethod
    def generate(self):
        self.image, self.overlay = Sprite.generate_surface(self.rect, **self.params)
        self.mask = pygame.mask.from_surface(self.image)
        self.real_rect = (tuple([x/y for x,y in zip(self.rect.topleft, self.resolution)]),\
                        tuple([x/y for x,y in zip(self.rect.size, self.resolution)]))
        self.rects[self.resolution] = self.rect.copy() 

    def draw(self, surface):
        """Draws the sprite over a surface. Draws the overlay too if use_overlay is True.
        Args:
            surface (:obj: pygame.Surface): Surface to draw the Sprite. It's usually the display.
        """
        if self.visible:
            surface.blit(self.image, self.rect)
            if self.enabled:
                if self.overlay and self.use_overlay and self.active:    
                    self.draw_overlay(surface)               
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

    '''def get_rect_if_canvas_size(self, canvas_size):
        return pygame.Rect( tuple([x*y for x,y in zip(self.real_rect[0], canvas_size)]),\
                            tuple([x*y for x,y in zip(self.real_rect[1], canvas_size)]))'''

    def set_canvas_size(self, canvas_size):
        """Set an internal resolution (NOT SIZE). Updates self.real_rect and self.resolution.
        Args:
            canvas_size (:tuple: int,int): Resolution to set.
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

    def set_size(self, size, update_rects=True): #TODO update documentation
        """Changes the size of the Sprite. Updates rect and real_rect, and changes image and mask to match the size.
        Args:
            size (:obj: pygame.Rect||:tuple: int,int): New size of the Sprite. In pixels.
        """
        self.rect.size = size
        if update_rects:
            self.real_rect  = (self.real_rect[0], tuple(x/y for x,y in zip(size, self.resolution)))
            self.rects[self.resolution] = self.rect.copy()
        self.regenerate_image()
        #LOG.log('debug', "Succesfully changed sprite ", self.id, " size to ",size)

    def set_position(self, position, update_rects=True):
        """Changes the position of the Sprite. Updates rect and real_rect.
        Args:
            position (:obj: pygame.Rect||:tuple: int,int): New position of the Sprite. In pixels.
        """
        self.rect.topleft = position
        if update_rects:
            self.real_rect  = (tuple(x/y for x,y in zip(position, self.resolution)), self.real_rect[1])
            self.rects[self.resolution] = self.rect.copy()
        #LOG.log('debug', "Succesfully changed sprite ",self.id, " position to ",position)

    def set_rect(self, rect, update_rects=True):
        """Sets a new Rect as the Sprite rect. Uses the rect.size and rect.topleft to change size and position
        Only executes set_position and set_size if the position or size of the rect is different from the original one. """
        if self.rect.topleft != rect.topleft:   
            self.set_position(rect.topleft, update_rects)
        if self.rect.size != rect.size:         
            self.set_size(rect.size, update_rects)

    def set_center(self, center):
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
            self.overlay.fill(DARKGRAY)
            self.overlay.set_alpha(180)
            self.image.blit(self.overlay, (0, 0))
            self.enabled        = False
            self.use_overlay    = False
        elif enabled and not self.enabled:    #Activating button
            self.enabled        = True
            self.use_overlay    = True
            self.regenerate_image()         #Restoring image and overlay too

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

    @staticmethod   #TODO UPDATE DOCUMENTATION
    def generate_surface(size, surface=None, texture=None, keep_aspect_ratio=True, resize_mode='fit', resize_smooth=True,\
                        shape="Rectangle", transparent=False, only_text=False, text="default_text", text_color=WHITE, text_font=None,\
                        fill_color=RED, fill_gradient=True, gradient=(LIGHTGRAY, DARKGRAY), gradient_type="horizontal",\
                        overlay=True, overlay_color=WHITE, border=True, border_color=WHITE, border_width=2, **unexpected_kwargs):
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
        if surface:     #If we creating the sprite from an already created surface
            surf    = Resizer.resize(surface, size, mode=resize_mode, smooth=resize_smooth)  
        elif only_text: #If the surface is only a text with transparent background
            surf    = pygame.font.Font(text_font, Resizer.max_font_size(text, size, text_font)).render(text, True, text_color)
        elif texture:   #If we get a string with the path of a texture to load onto the surface
            surf    = ResizedSurface.get_surface(texture, size, resize_mode, resize_smooth, keep_aspect_ratio)
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
        #End of the generation/specification of the pygame.Surface surf.
        if overlay:
            overlay = pygame.Surface(size)
            overlay.fill(overlay_color)
            return surf, overlay
        else:
            return surf, None

    def rects_to_str(self, return_luts_too=False):
        result = 'Id: '+self.id+', Position: '+str(self.rect.topleft)+', Size: '+str(self.rect.size)+\
                '\nReal rect pos: '+str(self.real_rect[0])+', Real rect size: '+str(self.real_rect[0])
        if return_luts_too:
            return result+'\nLut table of rects:\n '+str(self.rects)
        return result

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
        params['only_text']=True
        params['text'] = text
        super().__init__(id_, position, size, canvas_size, **params)
        self.text = text
        TextSprite.generate(self)

    @staticmethod
    def generate(self):
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
        
class AnimatedSprite(Sprite):
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
    __default_config = {'hover_ratio'   : 1.5,
                        'initial_surfaces': (),
                        'sprite_folder' : None,
                        'keywords'      :None,
                        'animation_delay':10, 
                        'resize_mode'   :'fit', 
                        'resize_smooth' :True,
                        'keep_aspect_ratio': True,
                        'keywords_strict' : False   
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
        self.counter            = 0
        self.next_frame_time    = None  #In generate
        self.animation_index    = 0
        #Generation
        AnimatedSprite.generate(self)

    @staticmethod
    def generate(self):
        UtilityBox.join_dicts(self.params, AnimatedSprite.__default_config)
        self.use_overlay = False
        self.next_frame_time = self.params['animation_delay']
        self.params['hover_size'] = tuple(x*self.params['hover_ratio'] for x in self.rect.size)
        if self.params['sprite_folder']:
            self.load_surfaces()
        else:
            self.add_surfaces()
        self.update_size()
        self.image  = self.current_sprite()    #Assigning a logical sprite in place of the decoy one of the super()
        self.mask   = self.current_mask()       #Same shit to mask

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
        if not _['keywords']:
            surfaces = ResizedSurface.load_surfaces(_['sprite_folder'], self.rect.size, _['resize_mode'], _['resize_smooth'],\
                                                    _['keep_aspect_ratio'])
            hover_surfaces = ResizedSurface.load_surfaces(_['sprite_folder'], _['hover_size'], _['resize_mode'],\
                                                        _['resize_smooth'], _['keep_aspect_ratio'])
        else:
            surfaces = ResizedSurface.load_surfaces(_['sprite_folder'], self.rect.size, _['resize_mode'], _['resize_smooth'],\
                                                    _['keep_aspect_ratio'], *_['keywords'], strict=_['keywords_strict'])
            hover_surfaces = ResizedSurface.load_surfaces(_['sprite_folder'], self.rect.size, _['resize_mode'], _['resize_smooth'],\
                                                        _['keep_aspect_ratio'], *_['keywords'], strict=_['keywords_strict'])
        for path in surfaces.keys():
            self.names.append(path)
            self.add_surface(surfaces[path], hover_surfaces[path])

    def add_surfaces(self): #TODO update documentation
        """Check if a surface is loaded already, and adds it to the attribute lists.
        Args:
            surface (str||:obj: pygame.Surface): Surface to add, or path to the image to load."""
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
                _ = self.params
                surface = Resizer.resize(surface, self.rect.size, _['resize_mode'], _['resize_smooth'],\
                                        _['keep_aspect_ratio'])
                hover_surface = Resizer.resize(surface, _['hover_size'], _['resize_mode'],\
                                                _['resize_smooth'], _['keep_aspect_ratio'])
                self.add_surface(surface, hover_surface)

    def add_surface(self, surface, hover_surface):
        """Resizes a surface to a size, and adds it to the non-original surfaces lists.
        Args:
            surface (:obj: pygame.Surface): Surface to resize and add.
            size (:tuple: int, int):    Size to resize the surface to."""
        self.surfaces.append(surface)
        self.hover_surfaces.append(hover_surface)
        self.masks.append(pygame.mask.from_surface(surface))

    def set_canvas_size(self, canvas_size): #TODO CHANGE THIS TO USE LOAD_SURFACES
        """Set an internal resolution (NOT SIZE). Updates self.real_rect and self.resolution.
        Clears the internal lists, and resize all the surfaces again to match the old proportion size/resolution.
        Args:
            canvas_size (:tuple: int,int): Resolution to set.
        """
        #Changing the sprite size and position to the proper place.
        super().set_canvas_size(canvas_size)    
        self.clear_lists()
        if self.params['sprite_folder']:
            self.load_surfaces()
        else:
            self.add_surfaces()
        self.update_size()
        self.image  = self.current_sprite()    #Assigning a logical sprite in place of the decoy one of the super()
        self.mask   = self.current_mask()       #Same shit to mask

    def clear_lists(self):
        """Empty all the internal lists of surfaces and masks, except the original ones (The non-resized).
        To be used after a change in size or something that required new/changed surfaces."""
        self.surfaces.clear()
        self.hover_surfaces.clear()              
        self.masks.clear()

    def animation_frame(self):
        """Changes the current showing surface (changing the index) to the next one."""
        self.animation_index = self.animation_index+1 if self.animation_index < (len(self.surfaces)-1) else 0

    def set_hover(self, hover):
        super().set_hover(hover)
        if hover:
            self.image = self.current_hover_sprite()
        else:
            self.image = self.current_sprite()

    def current_sprite(self):
        """Returns the current surface that will be shown if there are no special states in effect.
        Returns:
            (pygame.Surface):   Surface that should be drawn right now."""
        return self.surfaces[self.animation_index]

    def current_hover_sprite(self):
        """Returns the current surface that will be shown if the hover state is True.
        Returns:
            (pygame.Surface):   Hover surface that should be drawn right now."""
        return self.hover_surfaces[self.animation_index]

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
        if self.counter >= self.next_frame_time:
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
        self.sprites        = pygame.sprite.OrderedUpdates()

    def add_sprite(self, sprite):
        """Add sprite to the Sprite list, and blit it to the image of the MultiSprite
        Args:
            sprite (Sprite):    sprite to add."""
        sprite.use_overlay   = False #Not interested in overlays from a lot of sprites at the same time
        self.sprites.add(sprite)
        #LOG.log('debug', "ADDING SPRITE ", sprite.id, " WITH POS ", sprite.rect.topleft)
        self.image.blit(sprite.image, sprite.rect.topleft)

    def regenerate_image(self):
        """Generates the image again, blitting the Sprites in the sprite list.
        Intended to be used after changing an important attribute in rect or image.
        Those changes propagate through all the sprites."""
        super().regenerate_image()
        for sprite in self.sprites.sprites():   
            self.image.blit(sprite.image, sprite.rect.topleft)

    def set_size(self, size, update_rects=True):
        """Changes the size of the MultiSprite. All the internal Sprites are resized too as result.
        Args;
            size (:tuple: int, int):    New size in pixels."""
        super().set_size(size, update_rects=update_rects)    #Changing the sprite size and position to the proper place
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
            if all(kw in sprite.id for kw in keywords): 
                return sprite

    def add_text_sprite(self, id_, text, alignment="center", text_size=None, **params): 
        '''Generates and adds sprite-based text object following the input parameters.
        Args:
            id_ (str):  Identifier of the TextSprite
            text (str): Text to add
            alignment (str):   To set type of centering for the text. Center, Left, Right.
            text_size (:tuple: int, int):    Size of the text in pixels.
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