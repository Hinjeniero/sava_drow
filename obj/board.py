"""--------------------------------------------
board module. Contains the entire logic and graphics to build
the game's board.
Have the following classes.
    Board
--------------------------------------------"""

__all__ = ['Board']
__version__ = '1.0'
__author__ = 'David Flaity Pardo'

#Python full fledged libraries
import pygame
import math
import numpy
import os
import random
import threading
import time
from pygame.locals import *
#external libraries
from external.PAdLib import draw as drawing
#Selfmade libraries
from settings import MESSAGES, USEREVENTS, PATHS
from obj.screen import Screen, LoadingScreen
from obj.dice import Dice
from obj.cell import Cell, Quadrant
from obj.paths import Path, PathAppraiser
from obj.ai_player import ComputerPlayer
from obj.players import Player, Character, Restriction
from obj.sprite import Sprite, AnimatedSprite, OnceAnimatedSprite
from obj.ui_element import ButtonAction, TextSprite, InfoBoard, Dialog, ScrollingText
from obj.polygons import Circle, Rectangle, Circumference
from obj.counter import CounterSprite
from obj.help_dialogs import HelpDialogs
from obj.utilities.utility_box import UtilityBox
from obj.utilities.colors import RED, WHITE, BLACK, DARKGRAY, LIGHTGRAY, TRANSPARENT_GRAY
from obj.utilities.exceptions import BadPlayersParameter, BadPlayerTypeException, NotEnoughSpaceException,\
                                    PlayerNameExistsException, TooManyCharactersException
from obj.utilities.decorators import run_async, run_async_not_pooled, time_it
from obj.utilities.logger import Logger as LOG
from obj.utilities.logger import Parser
from obj.utilities.surface_loader import ResizedSurface, no_size_limit
#numpy.set_printoptions(threshold=numpy.nan)

class Board(Screen):
    """Board class. Inherits from Screen.
    Have all the methods and attributes to make the execution of a turn-based board game possible.
    The board consists of a platform in which the board will be drawn, and the board itself. 
    The board has 4 big circles or iterations, whose circumferences
    are paths that the characters can follow. Over them the cells will be created.
    The board follows a scheme of cells connected in two ways. In one way if they are 
    in the same circumference, or in the perpendicular one if an 'inter_path' exists at that 
    cell that connects both circumferences.
    In short, kinda like a spider web.
    The cells are organized in 4 quadrants (that follow the next scheme with cardinal points):
        quadrant 0 -> From NW to NE
        quadrant 1 -> From NE to SE
        quadrant 2 -> From SE to SW
        quadrant 3 -> From SW to NW
    General class attributes:
        __default_config (:dict:): Contains parameters about the board looks and elements.
            platform_proportion (float):    Size of the platform comparing to the height of the screen.
            platform_alignment (str):   Alignment of the platform within the Screen. Center, Left, Right.
            inter_path_frequency (int): Period of circles until a new inter_path is created between different levels.
            circles_per_lvl (int):  Number of cells/circles in each big circle/level/circumference.
            max_levels (int):   Number of levels/big circles/circumferences.
            path_color (:tuple: int, int, int): RGB color of the paths of the board.
            path_width (int):   Size of the paths themselves. In pixels.
    Attributes:
        turn (int): Current turn in the board.
        loading (:obj: LoadingScreen):  Loading Screen that will be shown when the board hasn't ended loading stuff.
        cells (:obj: pygame.sprite.Group):  The cells/circles themselves. A SpriteGroup containing them.
        quadrants (:dict: int, Quadrant):   Dict containing the quadrants. Each key is the number, and the item is
                                            the quadrant. Each quadrant contain the belonging cells.
        possible_dests (:obj: pygame.sprite.Group): Saves the possible cells that each character can move to (In their turn).
        inter_paths (:obj: pygame.sprite.GroupSingle):  A big transparent Sprite that contains the inter-paths that join circumferences.
        paths (:obj: pygame.sprite.Group):  Saves all the Circumferences in the form of Sprites. Each one is just a transparent circle
                                            with a border. 
        characters (:obj: pygame.sprite.OrderedUpdates):    Group containing all the characters playing on the board.
        active_cell (:obj: pygame.sprite.GroupSingle):  Last cell that the mouse hovered over.
        last_cell (:obj: pygame.sprite.GroupSingle):    Last cell that the character was on. To bring him back if the destiny is not valid.    
        active_path (:obj: pygame.sprite.GroupSingle):  Last circumference that the mouse hovered over. Turns Red.
        active_char (:obj: pygame.sprite.GroupSingle):  Char that the mouse is hovering over. Can pick up it if we press the left button.
        drag_char (:obj: pygame.sprite.GroupSingle):    Selected char that we are dragging with the mouse movement. Can Drop it wherever.
        platform (:obj: pygame.Surface):    Platform that will be drawn under the board itself.
        distances (:obj: numpy:int):   Graph of distances between cells connected (without changing direction of the path between them).
        enabled_paths (:obj: numpy:boolean):   Graph of directly connected cells.
        current_map (:dict: int, Cell): Current situation of the map, with all the characters and such. It's useful to the characters
                                        that can't move bypassing allies and restrictions like that.
        total_players (int):    Counter with the total of players that have been requested to be added on the board.
        loaded_players (int):   Counter with the total of players that have been succesfully loaded onto the board (With their chars).
        players (:list: Player):List with all the Player objects.
        player_index (int):     Index of the current player playing.
        """
    __default_config = {'quadrants_overlap'     : True,
                        'random_filling'        : True,
                        'loading_screen'        : True,
                        'platform_proportion'   : 0.95,
                        'platform_alignment'    : "center",
                        'platform_texture'      : None,
                        'platform_sprite'       : None,
                        'platform_transparency' : 128,
                        'inter_path_frequency'  : 2,
                        'circles_per_lvl'       : 16,
                        'max_levels'            : 4,
                        'center_cell'           : False,
                        'path_color'            : WHITE,
                        'path_width'            : 8,
                        'char_proportion'       : 1.4,
                        'loading_screen_text'   : "",
                        'cell_texture'          : None,
                        'cell_border'           : None,
                        'circumference_texture' : None,
                        'interpath_texture'     : None,
                        'scoreboard_texture'    : None,
                        'promotion_texture'     : None,
                        'infoboard_texture'     : None,
                        'dice_textures_folder'  : None,
                        'fitness_button_texture': None,
                        'help_button_texture'   : None,
                        'counter_round_time'    : None,
                        'show_last_mov_line'    : True
    }
    #CHANGE MAYBE THE THREADS OF CHARACTER TO JOIN INSTEAD OF NUM PLAYERS AND SHIT
    def __init__(self, id_, event_id, end_event_id, resolution, *players, empty=False, initial_dice_screen=True, **params):
        """Board constructor. Inherits from Screen.
        Args:
            id_ (str):  Identifier of the Screen.
            event_id (int): Identifier of the Screen event.
            end_event_id (int): Event that signals the end of the game in this board.
            resolution (:tuple: int,int):   Size of the Screen. In pixels.
            *players (:obj: Player):    All the players that will play on this board, separated by commas.
            **params (:dict:):  Dict of keywords and values as parameters to create the Screen.
                                platform_proportion, platform_alignment, inter_path_frequency, circles_per_lvl,\
                                max_levels, path_color, path_width.
        """
        super().__init__(id_, event_id, resolution, **params)
        self.start_timestamp = 0
        self.turn           = 0
        self.char_turns     = 0
        #Graphic elements
        self.loading_screen = None  #Created in Board.generate
        self.overlay_console= None
        self.console_active = True
        self.cells          = pygame.sprite.Group()
        self.quadrants      = {}
        self.locked_cells   = []
        self.possible_dests = pygame.sprite.Group()
        self.fitnesses      = {}
        self.inter_paths    = pygame.sprite.GroupSingle()
        self.dice           = pygame.sprite.GroupSingle()
        self.current_dice   = pygame.sprite.GroupSingle()   #Dice that we are shuffling currently
        self.fitness_button = pygame.sprite.GroupSingle()
        self.help_button    = pygame.sprite.GroupSingle()
        self.thinking_sprite= pygame.sprite.GroupSingle()
        self.counter_sprite = pygame.sprite.GroupSingle()
        self.paths          = pygame.sprite.Group()
        self.effects        = pygame.sprite.Group()
        self.characters     = pygame.sprite.OrderedUpdates()
        self.current_player = None  #Created in add_player
        self.scoreboard     = None  #Created in Board.generate
        self.scoreboard_flag= False
        self.show_score     = False
        self.promotion_table= None  #Created in Board.generate
        self.promotion_flag = threading.Event()
        self.gray_overlay   = None  #Created in Board.generate
        self.show_promotion = False

        #Utilities to keep track
        self.active_cell    = pygame.sprite.GroupSingle()
        self.last_cell      = pygame.sprite.GroupSingle()
        self.active_path    = pygame.sprite.GroupSingle()
        self.active_char    = pygame.sprite.GroupSingle()
        self.drag_char      = pygame.sprite.GroupSingle()
        self.platform       = None  #Created in Board.generate
        self.last_movement  = None  #Updated in each move_character method
        self.last_real_movm = None  #Updated in each move_character method
        self.last_char      = None  #Updated in each move_character method
        #Paths and maping
        self.distances      = None  #Created in Board.generate
        self.enabled_paths  = None  #Created in Board.generate
        self.current_map    = {}
        
        #Players 
        self.total_players  = 0
        self.loaded_players = 0
        self.players        = []
        self.player_index   = 0

        #Started and misc
        self.events         = {}
        self.end_event_id   = end_event_id
        self.starting_dices = {}    #Flags to know which dices have been casted. A bit redundant, but its done this way
        self.dices_values   = {}
        self.ai_turn        = False
        self.ai_turn_flag   = threading.Event()
        self.started        = False
        self.finished       = False
        self.generated      = False
        self.admin_mode     = False
        self.swapper        = None
        self.end            = False
        Board.generate(self, empty, initial_dice_screen, *players)
    
    ###SIMULATES ON_SCREEN CONSOLEEEE
    def LOG_ON_SCREEN(self, *msgs, **text_params):
        """Adds a message to the overlay console.
        Args:
            msgs()
            text_params()"""
        text = Parser.parse_texts(*msgs)
        LOG.log('info', text)
        self.overlay_console.add_msg(text, **text_params)

    #ALL THE GENERATION OF ELEMENTS AND PLAYERS NEEDED
    @staticmethod
    def generate(self, empty, initial_dice_screen, *players):
        """Method called in the constructor. Creates the complex objects (Not basic types)"""
        self.start_timestamp = time.time()
        UtilityBox.join_dicts(self.params, Board.__default_config)
        #INIT
        self.ai_turn_flag.set()
        self.generate_events()
        self.generate_onscreen_console()
        if self.params['loading_screen']:
            self.loading_screen = LoadingScreen(self.id+"_loading", self.event_id, self.resolution, text=self.params['loading_screen_text'])
        #REST
        self.platform = self.generate_platform()
        if not empty:
            self.generate_mapping()
            self.generate_environment(initial_dice_screen)
        else:
            self.LOG_ON_SCREEN("WARNING: Generating board in empty mode, needs server attributes to work")
        self.add_players(*players)
        self.swapper = self.character_swapper() #Simple generator to promote characters
        self.swapper.send(None) #Needed in the first execution of generator

    def generate_onscreen_console(self):
        """Generates the overlay console (Gray half transparent with white messages)."""
        start = time.time()
        self.overlay_console = ScrollingText('updates', self.event_id, self.resolution, transparency=180)
        LOG.log('debug', 'The console has been generated in ', (time.time()-start)*1000, 'ms')

    def generate_events(self):
        """Generate all the possible events emitted by the board."""
        self.events['win'] = pygame.event.Event(self.end_event_id, command='win')
        self.events['lose'] = pygame.event.Event(self.end_event_id, command='lose')
        self.events['bad_dice'] = pygame.event.Event(self.event_id, command='bad_dice')
        self.events['my_turn'] = pygame.event.Event(self.event_id, command='my_turn')
        self.events['cpu_turn'] = pygame.event.Event(self.event_id, command='cpu_turn')
        self.events['next_turn'] = pygame.event.Event(self.event_id, command='next_turn')
        self.events['admin_on'] = pygame.event.Event(self.event_id, command='admin', value = True)
        self.events['admin_off'] = pygame.event.Event(self.event_id, command='admin', value = False)
        self.events['turncoat'] = pygame.event.Event(self.event_id, command='turncoat')
        self.events['hide_dialog_temp'] = pygame.event.Event(self.event_id, command='hide_dialog_temp', value=2)    #Will hide whatever dialog in 3 seconds

    @no_size_limit
    def generate_platform(self):
        """Creates the platform behind the board itself. Used to make it easier to see the cells and characters."""
        platform_size   = tuple(min(self.resolution)*self.params['platform_proportion'] for _ in self.resolution)
        centered_pos    = tuple(x//2-y//2 for x, y in zip(self.resolution, platform_size))
        platform_pos    = (0, centered_pos[1]) if 'left' in self.params['platform_alignment']\
        else centered_pos if 'center' in self.params['platform_alignment']\
        else (self.resolution[0]-platform_size[0], centered_pos[1])
        if not self.params['platform_sprite']:
           platform = Rectangle(self.id+"_platform", platform_pos, platform_size, self.resolution, texture=self.params['platform_texture'])
           platform.image.set_alpha(self.params['platform_transparency'])
           return platform
        return self.params['platform_sprite']

    def generate_mapping(self):
        """Adds the map related structures, like the enabled paths graph and the distances matrix."""
        axis_size = self.params['circles_per_lvl']*self.params['max_levels']
        if self.params['center_cell']:
            axis_size += 1
        dimensions          = (axis_size, axis_size)
        self.distances      = numpy.full(dimensions, -888, dtype=int)   #Says the distance between cells
        self.enabled_paths  = numpy.zeros(dimensions, dtype=bool)       #Shows if the path exist

    @time_it
    def generate_environment(self, initial_dice_screen=False):
        """Builds all the graphical elements of the board, and also the mapping related structures."""
        threads = [self.generate_all_cells(), self.generate_paths(offset=True), self.generate_map_board(), self.generate_infoboard(), self.generate_effects()]
        if initial_dice_screen:
            threads.append(self.generate_dice_screen())
        #Waiting for threads
        for end_event in threads:   end_event.wait()
        self.adjust_cells()
        threads = [self.generate_inter_paths(), self.generate_dice()]
        for end_event in threads:   end_event.wait()
        #Generate fitness and help buttons
        fitness_button = ButtonAction('fitness_button', "", self.event_id, (0, 0), tuple(x*0.1 for x in self.resolution), self.resolution,\
                                    texture=self.params['fitness_button_texture'], text="")

        fitness_pos_y = self.dice.sprite.rect.centery-((fitness_button.rect.height//2+self.dice.sprite.rect.height//2)//0.9)
        fitness_button.set_center((self.dice.sprite.rect.x, fitness_pos_y))
        #help_button
        help_button = ButtonAction('help_button', "", self.event_id, (0, 0), tuple(x*0.1 for x in self.resolution), self.resolution,\
                                    texture=self.params['help_button_texture'], text="")
        help_pos_y = self.dice.sprite.rect.centery-((help_button.rect.height//2+self.dice.sprite.rect.height//2)//0.9)
        help_button.set_center((self.dice.sprite.rect.x+self.dice.sprite.rect.width, help_pos_y))
        #thinking_sprite
        thinking_sprite = AnimatedSprite('ia_thinking_sprite', (0, 0), self.dice.sprite.rect.size, self.resolution, sprite_folder=PATHS.HOURGLASS_FOLDER, resize_mode='fill', animation_delay=3)
        thinking_pos_y = help_button.rect.centery - help_button.rect.height//1.9 - thinking_sprite.rect.height//1.9  #1.5 instead of 2 to get some separation/margin
        thinking_sprite.set_center((help_button.rect.centerx, thinking_pos_y)) #Could also use self.infoboard.rect.centerx instead of the dice. But its the same.
        thinking_sprite.set_visible(False)
        #Adding buttons to matching groupsingles
        self.fitness_button.add(fitness_button), self.help_button.add(help_button), self.thinking_sprite.add(thinking_sprite)
        #Checking the counter
        if self.params['counter_round_time']:
            counter_sprite = CounterSprite('board_round_timer', (0, 0), self.dice.sprite.rect.size, self.resolution, 0.1, self.params['counter_round_time'])
            counter_sprite_center_x = self.thinking_sprite.sprite.rect.centerx - thinking_sprite.rect.width//1.9 -counter_sprite.rect.width//1.9  #1.9 width instead of 2 to get some separation/margin
            counter_sprite.set_center((counter_sprite_center_x, self.thinking_sprite.sprite.rect.centery)) #Could also use self.infoboard.rect.centerx instead of the dice. But its the same.
            counter_sprite.set_enabled(False)
            self.counter_sprite.add(counter_sprite)
        HelpDialogs.add_help_dialogs(self.id, (fitness_button, help_button), self.resolution)
        #End, and saving to the sprites attribute of screen so the set_canvas_size resize them when necessary.
        self.save_sprites()
        self.generated = True

    @run_async
    def generate_dice_screen(self, transparency=128):
        """Generates the dice screen so players can try their luck to get their turn!"""
        start = time.time()
        dice_screen = Dialog('Initial_dices_screen', self.event_id, self.resolution, self.resolution, fill_color=DARKGRAY, rows=3, cols=4)
        dice_screen.image = dice_screen.image.convert()
        dice_screen.image.set_alpha(transparency)
        self.add_dialogs(dice_screen)
        LOG.log('debug', 'The dice screen has been generated in ', (time.time()-start)*1000, 'ms')

    @run_async
    def add_dices_to_screen(self, player_list):
        """In this way is easily overridable for network board to work properly"""
        dice_screen = self.get_dialog('dice', 'init')
        if dice_screen: #If the dialog was found
            for player in player_list:
                self.starting_dices[player.uuid] = threading.Event()
                self.dices_values[player.uuid] = None
                dice_screen.add_text_element(str(player.uuid), player.name, 4//len(player_list), scale=0.60)
            for player in player_list:
                dice = Dice(str(player.uuid), (0, 0), tuple(0.15*x for x in self.resolution), self.resolution, shuffle_time=1500,\
                            sprite_folder=self.params['dice_textures_folder'], animation_delay=3, limit_throws=1, overlay=False)
                dice.add_turn(player.uuid)
                dice_screen.add_sprite_to_elements(4//len(player_list), dice)
                if player.human:
                    dice.reactivating_dice()
                else:
                    dice.deactivating_dice()

    @run_async
    def generate_all_cells(self, custom_cell_radius=None, growing_cells=True, growing_ratio=8/7):
        """Generate all the cells of the board. Does this by calling generate_cells, and changing the radius.
        The first inside circumference is done changing too the number of cells in it.
        Args:
            custom_cell_radius (int):   Radius of the cells themselves."""
        self.cells.empty()
        self.active_cell.empty()
        ratio       = self.platform.rect.height//(2*self.params['max_levels'])
        radius      = 0
        small_radius= ratio//4 if not custom_cell_radius else int(custom_cell_radius)
        for i in range (0, self.params['max_levels']):
            radius              += ratio
            if i is 0:          self.cells.add(self.__generate_cells(radius-ratio//3, self.platform.rect.center, small_radius, 4, 0, initial_offset=-45, texture=self.params['cell_texture']))
            else:               self.cells.add(self.__generate_cells(radius-ratio//3, self.platform.rect.center, small_radius, self.params['circles_per_lvl'], i, texture=self.params['cell_texture']))
            if growing_cells:   small_radius = int(small_radius*growing_ratio)
        if self.params['center_cell']:
            self.cells.add(self.__generate_center_cell(small_radius, self.params['circles_per_lvl'], self.params['max_levels'], texture=self.params['cell_texture']))
        LOG.log('DEBUG', "Generated cells of ", self.id)
        self.LOG_ON_SCREEN("All the cells have been generated")
        self.assign_quadrants()

    def __generate_cells(self, radius, center, circle_radius, circle_number, lvl, initial_offset=-90, **cell_params):
        """Generate the cells of one circumference/level of the board. 
        Args:
            radius (int):   Radius of the circumference that will support the cells. In short, which level.
                            In pixels.
            center (:tuple: int, int):  Center of the circumference. Will be used to position the cells (using cos and sin).
                                        In pixels.
            circle_radius (int):    Radius of each cell. In pixels.
            circle_number (int):    Ammount of cells per circumference (per level).
            initial_offset (float||int, default=-90):    Initial offset to draw the first cell. If its lower than 2*pi, will
                                                        be considered in radians. Degrees otherwise. -90 degrees makes the first
                                                        cell to appear at y=1, x=0.
            **cell_params (:dict:): Dict of keywords and values as parameters to modify the surface of the cells.
                                    This way, we can have a little more personalized look on the cells.
        """
        cells = []
        two_pi  = 2*math.pi
        initial_offset = initial_offset*(math.pi/180) if abs(initial_offset) > two_pi\
        else initial_offset%360*(math.pi/180) if abs(initial_offset) > 360 else initial_offset
        angle   = initial_offset*(math.pi/180) if initial_offset > two_pi else initial_offset
        distance= two_pi/circle_number
        index   = 0
        while angle < (two_pi+initial_offset):
            position    = (center[0]+(radius*math.cos(angle))-circle_radius, center[1]+(radius*math.sin(angle))-circle_radius)
            cells.append(Cell((lvl, index), lvl*circle_number+index, position, (circle_radius*2, circle_radius*2), self.resolution, angle=angle, **cell_params))
            index       += 1
            angle       += distance
        return cells

    def __generate_center_cell(self, radius, circle_number, lvl_number, **cell_params):
        """Creates the center cell if the center_cell flag of **params is true."""
        index = circle_number*lvl_number
        for i in range(0, 4):
            self.enabled_paths[i][index], self.enabled_paths[index][i] = True, True
            self.distances[i][index], self.distances[index][i] = 1, 1
        cell = Cell((lvl_number-1, circle_number), index, tuple(center-radius for center in self.platform.rect.center), (radius*2, radius*2), self.resolution, **cell_params)
        cell.promotion = True
        cell.owner = 11110000
        if self.params['cell_border']:
            cell.add_border(self.params['cell_border'])
        cell.set_center(self.platform.rect.center)
        return cell

    def assign_quadrants(self):
        """Get the cells, sorts them, and inserts them in the appropiate quadrant.
        Args:
            *cells (:obj: Cell):    Cells to sort and assign to the quadrants. Separated by commas."""
        quadrants = {}
        for cell in self.cells:
            if cell.get_level() < 1\
            or cell.get_real_index() >= self.params['circles_per_lvl']*self.params['max_levels']: 
                continue   #We are not interested in this cell, next one
            quads = self.__get_quadrant(cell.get_index())
            for quadrant in quads:
                try:                quadrants[quadrant].append(cell)
                except KeyError:    quadrants[quadrant] = [cell]
        for quadrant_number, quadrant_cells in quadrants.items():
            self.quadrants[quadrant_number] = Quadrant(quadrant_number, self.params['circles_per_lvl'],\
                                                        self.params['inter_path_frequency'], *quadrant_cells)
        if not self.params['quadrants_overlap']:
            Quadrant.delete_overlapping_cells(*self.quadrants.values())

    def __get_quadrant(self, cell_index):
        """Gets the respective quadrant of the cell index received.
        Returns:
            (tuple: int):   Numerical id of the appropiate quadrant.
                            Can be one or two quadrants if the cell is a border."""
        ratio = self.params['circles_per_lvl']//4
        result, rest = (cell_index+ratio//2)//ratio,  (cell_index+ratio//2)%ratio
        if result >= 4:                 #We gone beyond the last quadrant boi, circular shape ftw
            if rest is 0:   return 3, 0 #Last and first quadrant, it's that shared cell
            else:           return 0,    #Associated with first quadrant
        if rest is 0 and result is not 0: return result, result-1
        return result,
    
    @run_async
    def generate_map_board(self):
        """Fills the essential graphs of the current board.
        One graph of booleans for directly connected cells.
        One graph of ints for connected cells (Without change of direction).""" 
        self.__map_enabled_paths()
        self.__map_distances()
    
    def __map_enabled_paths(self):
        """Fills the graph of directly connected cells.
        The code is a bit different for the inside level, since it doesn't have
        then same number of cells as the outside levels (circumferences)."""
        lvls, circles = self.params['max_levels'], self.params['circles_per_lvl']
        for x in range(0, circles*lvls):
            interior_limit = 4
            self.enabled_paths[x][x] = True
            #Center
            if x < interior_limit:
                if x is interior_limit-1:           #Have to connect w/ the other end of the circle               
                    self.enabled_paths[0][interior_limit-1], self.enabled_paths[interior_limit-1][0] = True, True 
                    continue    #next iteration                    
            
            #Those dont exist at all
            elif interior_limit <= x < circles:     #Those dont exist (4 -> circles-1)
                self.enabled_paths[x][x] = None
                continue        #next iteration
            
            #If first circle, check interpaths to get that done
            elif circles <= x < circles*2:
                interpath_exists = self.__get_inside_cell(x) #Check if interpath in this circle
                if interpath_exists is not None:
                    self.enabled_paths[x][interpath_exists], self.enabled_paths[interpath_exists][x] = True, True
                    for y in range(x, (lvls-1)*circles, circles):   #From interior -> exterior
                        self.enabled_paths[y][y+circles], self.enabled_paths[y+circles][y] = True, True

            #No more special conditions, normal cells
            if (x+1)%circles is 0:                  #last circle of this lvl, connect with first one:
                self.enabled_paths[x][(x-circles)+1], self.enabled_paths[(x-circles)+1][x] = True, True
            else:                                   #Connect with next circle
                self.enabled_paths[x][x+1], self.enabled_paths[x+1][x] = True, True
        LOG.log('DEBUG', "Paths of this map: \n", self.enabled_paths)       

    def __map_distances(self):
        """Fills the graph of connected cells. Does this by checking (every cell vs every other cell)
        if they are in the same inter-circumference path or the same circumference. 
        In that case, writes the distance between both."""
        lvls, circles = self.params['max_levels'], self.params['circles_per_lvl']
        #First level
        interior_limit = 4
        for x in range(0, interior_limit):
            for y in range(x, interior_limit):
                self.distances[x][y], self.distances[y][x] = abs(x-y), abs(x-y)

        #Exterior levels
        for x in range(circles, lvls*circles):
            for y in range(x, lvls*circles):
                if x//circles is y//circles: #If they are in teh same level
                    self.distances[x][y], self.distances[y][x] = abs(x-y), abs(x-y)

        #Distances first complete circle among interpaths
        for x in range(circles, circles*2):
            interpath_exists = self.__get_inside_cell(x) #Check if interpath in this circle
            if interpath_exists is not None:
                for y in range(x, lvls*circles, circles):
                    self.distances[interpath_exists][y], self.distances[y][interpath_exists] = abs(y-interpath_exists)//circles, abs(y-interpath_exists)//circles
                for y in range(x, lvls*circles, circles):   #From interior -> exterior
                    for z in range(y, lvls*circles, circles):
                        self.distances[y][z], self.distances[z][y] = abs(y-z)//circles, abs(y-z)//circles

        self.__parse_two_way_distances()
        LOG.log('DEBUG', "Distances of this map: \n", self.distances)  

    @run_async
    @no_size_limit
    def generate_infoboard(self):
        """Generates the infoboard of the game, containing the board turn, the current player, the last movement, etc."""
        infoboard = InfoBoard(self.id+'_infoboard', 0, (0, 0), (0.15*self.resolution[0], self.resolution[1]),\
                    self.resolution, texture=self.params['infoboard_texture'], keep_aspect_ratio = False, rows=8, cols=2)
        infoboard.set_position((self.resolution[0]-infoboard.rect.width, 0))
        infoboard.add_text_element('turn_label', 'Board turn', 1, scale=1.4)
        infoboard.add_text_element('turn', str(self.turn+1), 1, scale=0.6)
        infoboard.add_text_element('turn_char_label', 'Char turn', 1, scale=1.4)
        infoboard.add_text_element('turn_char', str(self.char_turns+1), 1, scale=0.6)
        infoboard.add_text_element('player_name_label', 'Playing: ', 1, scale=1.2)
        infoboard.add_text_element('player_name', '------------', 1, scale=0.9)                        #Dummy text
        infoboard.add_text_element('last_movement_label', 'LAST MOVE: ', 2, scale = 0.8)
        infoboard.add_text_element('last_character', 'Typeofchar', 1, scale=1.2)
        infoboard.add_text_element('last_movement', ' A-99 to A-99 ', 1)    #Dummy text
        self.infoboard = infoboard
        self.LOG_ON_SCREEN("The game infoboard has been generated")

    @run_async
    def generate_effects(self):
        """Creates the particle effects that show when a character either moves or captures another one"""
        explosion_effect = OnceAnimatedSprite('explosion_effect', (0, 0), tuple(x*0.20 for x in self.resolution), self.resolution,\
                                            sprite_folder=PATHS.FIRE_RING, animation_delay=2)   #Position will change later anyway
        selection_effect = OnceAnimatedSprite('selection_effect', (0, 0), tuple(x*0.15 for x in self.resolution), self.resolution,\
                                            sprite_folder=PATHS.GOLDEN_RING, animation_delay=2)   #Position will change later anyway
        start_teleport_effect = OnceAnimatedSprite('start_teleport', (0, 0), tuple(x*0.15 for x in self.resolution), self.resolution,\
                                            sprite_folder=PATHS.SMOKE_RING, animation_delay=2)   #Position will change later anyway
        end_teleport_effect = OnceAnimatedSprite('end_teleport', (0, 0), tuple(x*0.15 for x in self.resolution), self.resolution,\
                                            sprite_folder=PATHS.BLUE_RING, animation_delay=2)   #Position will change later anyway                                                                                        
        explosion_effect.set_enabled(False)
        self.effects.add(explosion_effect, selection_effect, start_teleport_effect, end_teleport_effect)

    @run_async_not_pooled
    def update_infoboard(self):
        """Called after each board turn. Updates the elements of the board infoboard."""
        self.infoboard.update_element('turn', str(self.turn+1))
        self.infoboard.update_element('turn_char', str(self.char_turns+1))
        self.infoboard.update_element('player_name', self.current_player.name)
        if self.last_movement:
            self.infoboard.update_element('last_movement', ' '+self.last_movement[0]+' to '+self.last_movement[1]+' ')
            self.infoboard.update_element('last_character', self.last_char.get_type())

    @run_async
    def generate_dice(self):
        """Creates and adds the board dice (NOT the dice screen)."""
        dice = Dice('dice', (0, 0), tuple(0.1*x for x in self.resolution), self.resolution, shuffle_time=1500, sprite_folder=self.params['dice_textures_folder'], animation_delay=2)
        dice.set_position((self.infoboard.rect.centerx-dice.rect.width//2, self.resolution[1]-(dice.rect.height*2)))
        self.dice.add(dice)
        self.LOG_ON_SCREEN("Dice has been generated")

    @no_size_limit
    def generate_dialogs(self):
        """Builds the promotion table and gray overlay."""
        self.scoreboard = self.generate_scoreboard()
        promotion_table = Dialog(self.id+'_promotion', USEREVENTS.DIALOG_USEREVENT, (self.resolution[0]//1.05, self.resolution[1]//8),\
                                self.resolution, keep_aspect_ratio = False, texture=self.params['promotion_texture'])
        self.promotion_table = promotion_table
        self.gray_overlay = ScrollingText('nuthing', self.event_id, self.resolution, transparency=128)
        self.LOG_ON_SCREEN("The board scoreboard and promotion table have been generated.")

    def generate_scoreboard(self):
        """Generates the scoreboard that shows when pressing tab"""
        scoreboard = InfoBoard(self.id+'_scoreboard', USEREVENTS.DIALOG_USEREVENT, (0, 0), (self.resolution[0]//1.1, self.resolution[1]//1.5),\
                                self.resolution, keep_aspect_ratio = False, rows=len(self.players)+1, cols=len(self.players[0].get_stats().keys()),
                                texture=self.params['scoreboard_texture'])
        scoreboard.set_position(tuple(x//2-y//2 for x, y in zip(self.resolution, scoreboard.rect.size)))
        return scoreboard

    @run_async
    @no_size_limit
    def generate_inter_paths(self):
        """Create the paths that connect circumferences between themselves.
        Does this by drawing bezier curves under the designated cells of each level.
        Create one Surface with all the curves drawn in it."""
        self.inter_paths.empty()
        surface = pygame.Surface(self.resolution)
        UtilityBox.add_transparency(surface, self.params['path_color'])
        self.__adjust_number_of_paths()
        #A loop of one circumference
        for i in range(0, self.params['circles_per_lvl']):
            if (i+1)%self.params['inter_path_frequency'] is 0:
                self.draw_inter_path(surface, i)
        surface = surface.subsurface(self.platform.rect)
        interpaths_sprite = Sprite('inter_paths', self.platform.rect.topleft, surface.get_size(), self.resolution, surface=surface)
        if self.params['interpath_texture']:
            interpaths_sprite.image = UtilityBox.overlap_trace_texture(interpaths_sprite.image, ResizedSurface.get_surface(self.params['interpath_texture'],\
                                            interpaths_sprite.rect.size, 'fill', True))
        self.inter_paths.add(interpaths_sprite)
        self.LOG_ON_SCREEN("The interpath has been generated")

    def draw_inter_path(self, surface, index):
        """Draw a bezier curve on a surface. It uses the indexes in (level, index) scheme.
        Args:
            surface (:obj: pygame.Surface). The surface to draw on the curves.
            index (int):    The index of each level that must be connected.
                            (3, 1) -> (2, 1), etc...
            """
        point_list = []
        #This loop goes outside-inside over the circumferences, getting the cells with the same index IN THAT LEVEL.
        for i in range(self.params['max_levels']-1, 0, -1):
            point_list.append(self.get_cell(i, index).center)
        point_list.append(self.get_cell(0, self.__get_inside_cell(index)).center) #Final point
        UtilityBox.draw_bezier(surface, color=self.params['path_color'], width=self.params['path_width'], *(tuple(point_list)))

    ###UPDATING OF THE ELEMENTS MID-GAME
    @run_async_not_pooled
    def update_scoreboard(self):
        """Called after each board turn, updates the scoreboard text elements."""
        if not self.scoreboard_flag:    #THis is to not overlap turns updates.
            try:
                self.scoreboard_flag = True
                if self.scoreboard.taken_spaces is 0:   #If the infoboard is empty (First time filling it up)
                    for key in self.players[0].get_stats().keys():
                        self.scoreboard.add_text_element(str(hash(key)), key, 1)
                for player in self.players:
                    player_stats = player.get_stats()
                    for key, value in player_stats.items():
                        text_sprite = self.scoreboard.get_sprite(str(hash((player.uuid, key))))
                        if not text_sprite: #If this sprite wasnt created yet
                            text_color = WHITE if not player.dead else DARKGRAY
                            self.scoreboard.add_text_element(str(hash((player.uuid, key))), value, 1, color=text_color)
                        elif text_sprite.text != str(value):
                            text_sprite.set_text(value)
                self.scoreboard_flag = False
                LOG.log('debug', 'The scoreboard has been successfully updated.')
            except NotEnoughSpaceException: #Lets clear it and try again
                self.scoreboard.clear()
                self.scoreboard_flag = False
                self.update_scoreboard()

    @run_async_not_pooled
    def update_promotion_table(self, *chars):
        """Called after the show_promotion flag is set to True.
        Clears the promotion table and adds the character that the current player can upgrade the pawn to."""
        self.promotion_table.full_clear()
        self.promotion_table.set_rows(1)
        self.promotion_table.set_cols(len(chars))
        for char in chars:
            if not char.upgradable: #Upgradable ones cannot be upgraded to
                char.use_overlay = False
                self.promotion_table.add_sprite_to_elements(1, char, resize_sprite=False)   #It takes too much time if we wait for the resizing
        self.promotion_flag.set()
        LOG.log('debug', 'The promotion table has been successfully updated.')

    def adjust_cells(self):
        """Adjust the position of the cells to eliminate the offset that they show after generation."""
        for cell in self.cells:
            if cell.get_index()>=self.params['circles_per_lvl']:
                continue
            circumf = next(path for path in self.paths if str(cell.get_level()) in path.id)
            offset = circumf.width//2
            cell.rect.x -= offset*math.cos(cell.angle)
            cell.rect.y -= offset*math.sin(cell.angle)
            cell.set_position(cell.rect.topleft)

    def save_sprites(self):
        """Copies all the references of the sprites to the sprites list declared on the superclass.
        Do this to modify all the graphical elements at once when needed in a more seamless manner.
        Also because the super().draw method only draws the self.sprites.
        Only adds the graphics regarding the board, the characters and player addons will be drawn later."""
        self.sprites.add(self.platform, self.inter_paths.sprite, *self.paths.sprites(), *self.cells.sprites(),\
                        self.infoboard, self.dice, self.fitness_button, self.help_button, self.thinking_sprite,\
                        self.counter_sprite, self.effects)

    def __adjust_number_of_paths(self):
        """Checks the inter path frequency. If the circles are not divisible by that frequency,
        it rounds up the said frequency parameter."""
        circles, paths = self.params['circles_per_lvl'], self.params['inter_path_frequency']
        if circles%paths is not 0:
            self.params['inter_path_frecuency'] = circles//math.ceil(circles/paths) 
            LOG.log('DEBUG', "Changed number of paths from ", paths, " to ", self.params['inter_path_frecuency'])                                
        
    def __parse_two_way_distances(self):
        """Since our circumferencial path has a circular shape, to go from one cell to another,
        we can go by two ways. This means that the maximum distance is half the distance of a circumference.
        This methos parses those distances that need it, since they were generated without taking into account
        this detail."""
        lvls, circles = self.params['max_levels'], self.params['circles_per_lvl']
        interior_limit = 4
        limit = interior_limit//2
        #Interior circle
        for x in range(0, interior_limit):
            for y in range(0, interior_limit):
                if self.distances[x][y] > limit:
                    dist = abs(self.distances[x][y]-limit)
                    self.distances[x][y], self.distances[y][x] = dist, dist 
        #Complete circles
        limit = circles//2
        for x in range(circles, lvls*circles):
            for y in range(circles, lvls*circles):
                if self.distances[x][y] > limit:    
                    dist = abs(circles-self.distances[x][y])
                    self.distances[x][y],self.distances[y][x] = dist, dist   

    #Map lvl 1 circles to the lvl0 circle (less circles)
    def __get_inside_cell(self, index):
        """Returns:
            (int): The correspondant cell index of the inside circumference for an index of the outside levels."""
        ratio = self.params['circles_per_lvl']//4
        return (index%self.params['circles_per_lvl'])//ratio if (index+1)%self.params['inter_path_frequency'] is 0 else None

    def set_admin_mode(self, admin):
        """Changes the admin mode flag."""
        self.admin_mode = admin

    @run_async
    @no_size_limit
    def generate_paths(self, offset=False):
        """Creates the circumferences themselves. Does this by getting the platform size,
        and dividing it by the number of levels/circumferences of self.params. 
        Args:
            offset (boolean):   True if we don't want the circumferences to be so close to the platform borders."""
        self.paths.empty()
        self.active_path.empty()
        ratio = self.platform.rect.height//self.params['max_levels']
        radius = ratio//2-ratio//6 if offset else ratio//2
        for i in range (0, self.params['max_levels']):
            out_circle = Circumference('circular_path_'+str(i), tuple(x-radius for x in self.platform.rect.center),\
                        (radius*2, radius*2), self.resolution, fill_gradient=False, overlay=False, texture=self.params['circumference_texture'],\
                        border_color=self.params['path_color'], border_width=self.params['path_width'])
            self.paths.add(out_circle)
            radius+=ratio//2
        self.LOG_ON_SCREEN("All the circumferences have been generated")
        LOG.log('DEBUG', "Generated circular paths in ", self.id)

    def get_cell(self, lvl, index):
        """Args:
            lvl (int):  Level of the requested cell.
            index (int):Index of the requested cell.
        Returns:
            (:obj: Cell):   The cell that has the level and index arguments."""
        for cell in self.cells:
            if lvl is cell.get_level() and index is cell.get_index():
                return cell
        return False

    def get_cell_by_real_index(self, index):
        """Args:
            index (int):    Real index of the requested cell.
        Returns:
            (:obj: Cell):   The cell that has the real index."""
        for cell in self.cells:
            if index is cell.get_real_index():  
                return cell
        return False

    def update_map(self):
        """Generates the current map, changing enemies and allies of each Cell according to which player is asking.
        Args:
            to_who (str): Player who is asking.
        """ 
        for cell in self.cells:
            self.current_map[cell.get_real_index()]=cell.to_path(self.current_player.uuid)
        LOG.log('DEBUG', "Generated the map of paths for ", self.current_player.name)
    
    def update_cells(self, *cells):
        """Called after each complete board turn. Updates the current_map structure."""
        for cell in cells:
            self.current_map[cell.get_real_index()]=cell.to_path(self.current_player.uuid)

    def set_resolution(self, resolution):
        """Changes the resolution of the Screen. It also resizes all the Screen elements.
        Args:
            resolution (:tuple: int, int):  Resolution to set. In pixels."""
        super().set_resolution(resolution)
        threads = [self.generate_inter_paths()]
        self.loading_screen.set_resolution(resolution)
        for player in self.players:
            player.set_resolution(resolution)
        #Othewise the bezier curves just get fucked up when resizing back and forth.
        self.sprites.empty()
        for end_event in threads:   end_event.wait() #When those are done
        self.save_sprites()

    def ALL_PLAYERS_LOADED(self):
        """ Checks if all of the board players have been created and loaded succesfully.
        Once it is done, it activates some of the board flags, and generates and updates some attributes.
        Also, if the starting dice screen is activated, it is shown to make the throws.
        Returns:
            (boolean): True if all the requested players have been loaded already."""
        if not self.started and (self.loaded_players is self.total_players) and self.generated:
            self.add_dices_to_screen(self.players)  #Won't do anything if the flag initial_dice_screen is False
            self.console_active = False
            self.play_sound('success')
            self.show_dialog('dice', send_event=False)  #Won't show if the flag initial_dice_screen is False
            self.generate_dialogs()
            thread = self.update_scoreboard()
            thread.join()   #Waiting for the structures to be created
            #Now ordering players and starting the first screen of the game
            self.players.sort(key=lambda player:player.order)   #This won't be the final order, its just an order to throw the dices
            self.player_index = len(self.players)-1  #To make the next player turn be the self.players[0]
            self.current_player = self.players[-1]  #To make the next player turn be the self.players[0]
            self.turn -= 1
            self.current_player.turn -= 1  #To make the next player turn be the self.players[0]
            #End of that gibberish
            self.started = True
            LOG.log('info', 'Generating the board and all of its players took ', time.time()-self.start_timestamp," seconds.")
            self.start_timestamp = time.time()
            self.next_player_turn()

    def get_event(self, id):
        """Gets the first event whose identificator contains or matches the id input argument.
        Args:
            id (String):    Id to search for in the events of the board.
        Returns:
            (:obj: pygame.Event | None):    Returns an event if a matching one is found, None otherwise."""
        return next((event for key, event in self.events.items() if id in key), None)

    def post_event(self, id):
        """Gets the first event whose identificator contains or matches the id input argument.
        Afterwards, if an event was found, it is posted in the pygame event queue to trigger the adequate action. 
        Args:
            id (String):    Id to search for in the events of the board."""
        event_to_send = self.get_event(id)
        if event_to_send:
            pygame.event.post(event_to_send)

    def create_player(self, name, number, chars_size, cpu=False, cpu_mode=None, cpu_time=None, empty=False, **player_settings):
        """Queues the creation of a player on the async method.
        Args:
            name (str): Identifier of the player
            number (int):   Number assignated by arriving order. Will assign a quadrant too.
            chars_size (:tuple: int, int):  Size of the image of the characters. In pixels.
            **player_settings (:dict:): Contains the more specific parameters to create the player.
                                        Ammount of each type of char, name of their actions, and their folder paths.
        """
        self.total_players += 1
        for player in self.players:
            if name == player.name:
                raise PlayerNameExistsException("The player name "+name+" already exists")
        if not empty and sum(x['ammount'] for x in player_settings.values()) > len(self.quadrants[0].cells):
            raise TooManyCharactersException('There are too many characters in player for a quadrant.')
        self.__create_player(name, number, chars_size, cpu, empty, cpu_mode, cpu_time, **player_settings)
        LOG.log('DEBUG', "Queue'd player to load, total players ", self.total_players, " already loaded ", self.loaded_players)

    def __add_player(self, player):
        """Adds a player to the board. ALso gets each one of the player's characters
        and drop them in any cell of the belonging quadrant.
        Args:
            player (:obj: Player):  Player to add to the board
        Raises:
            BadPlayerTypeException: If the player argument is not of type Player."""
        if isinstance(player, Player): 
            self.players.append(player)
            if len(player.characters.sprites()) > 0:
                current_level = self.quadrants[player.order].max_border_lvl()
                rank = player.characters.sprites()[0].rank
                HelpDialogs.add_characters_dialogs(player.characters, self.resolution)   #Adding the help 
                for character in player.characters:
                    if character.rank < rank:
                        current_level -= 1
                        rank = character.rank
                    character.set_size(tuple(int(x*self.params['char_proportion'] )for x in self.cells.sprites()[0].rect.size))
                    cell = self.quadrants[player.order].get_cell(border_level=current_level, random_cell=self.params['random_filling'])
                    cell.add_char(character)
                    character.set_cell(cell)
                    self.characters.add(character)  
                    if cell.promotion:
                        cell.owner = player.uuid
                        if self.params['cell_border']:
                            cell.add_border(self.params['cell_border'])
                    #self.LOG_ON_SCREEN("Character ", character.id, " spawned with position ", cell.pos)
                    #LOG.log('DEBUG', "Character ", character.id, " spawned with position ", cell.pos)
                player.pause_characters()
                self.LOG_ON_SCREEN("Created the ", player.name, " successfully")
            self.loaded_players += 1
            self.ALL_PLAYERS_LOADED()
            return True
        raise BadPlayerTypeException("A player in the board can't be of type "+str(type(player)))
        
    def add_players(self, *players):
        """Adds all the players and their characters.
        Args:
            *players (:obj: Player):    The players to add. Separated by commas."""
        if not isinstance(players, (tuple, list)):    raise BadPlayersParameter("The list of players to add can't be of type "+str(type(players)))
        for player in players:  self.__add_player(player)

    @run_async
    def __create_player(self, player_name, player_number, chars_size, cpu, empty, ai_mode, ai_time, **player_params):
        """Asynchronous method (@run_async decorator). Creates a player with the the arguments and adds him to the board.
        Args:
            player_name (str):  Identifier of the player
            player_number (int):Number assignated by arriving order. Will assign a quadrant too.
            chars_size (:tuple: int, int):  Size of the image of the characters. In pixels.
            **player_params (:dict:):   Contains the more specific parameters to create the player.
                                        Ammount of each type of char, name of their actions, and their folder paths.
        Returns:
            (:obj:Threading.thread):    The thread doing the work. It is returned by the decorator."""
        if cpu:
            player = ComputerPlayer(self.enabled_paths, self.distances, self.params['circles_per_lvl'], player_name,\
                                    player_number, chars_size, self.resolution, ai_mode=ai_mode, timeout=ai_time, **player_params)
        else:
            player = Player(player_name, player_number, chars_size, self.resolution, empty=empty, **player_params)
        self.__add_player(player)

    def play_effect(self, id_, center_position):
        """Shows a particle effect in the input position in the board"""
        effect = next((sprite for sprite in self.effects if id_.lower() in sprite.id.lower() or sprite.id.lower() in id_.lower()), None)
        if effect:
            effect.rect.center = center_position
            effect.set_enabled(True)
    
    def get_effect(self, id_):
        """Return an effect if the id input matches, or None otherwise"""
        return next((sprite for sprite in self.effects if id_.lower() in sprite.id.lower() or sprite.id.lower() in id_.lower()), None)

    def draw(self, surface):
        """Draws the board and all of its elements on the surface.
        Blits them all and then updates the display.
        Args:
            surface (:obj: pygame.Surface): Surface to draw the board.
        """
        try:
            if not self.started and self.params['loading_screen']:
                if self.overlay_console.has_changed():
                    self.loading_screen.draw(surface)
                    if self.console_active and not (self.dialog and self.dialog.visible):
                        self.overlay_console.draw(surface)
                return
            super().draw(surface)   #Draws background and sprites
            if self.params['show_last_mov_line'] and self.last_real_movm:
                start_pos, end_pos = self.get_cell_by_real_index(self.last_real_movm[0]).rect.center, self.get_cell_by_real_index(self.last_real_movm[1]).rect.center
                # direction = (1 if start_pos[0]<end_pos[0] else -1, 1 if start_pos[1]<end_pos[1] else -1)
                # start_pos = tuple(original + (self.cells.sprites()[0].radius)*direction for original, direction in zip(start_pos, direction))
                pygame.draw.lines(surface, BLACK, False, (start_pos, end_pos), (self.resolution[0]//300)+2)
                pygame.draw.lines(surface, WHITE, False, (start_pos, end_pos), self.resolution[0]//300)

            for char in self.characters:
                char.draw(surface)
            if self.current_player:
                self.current_player.draw(surface)   #This draws the player's infoboard
            if self.promotion_table and self.show_promotion:
                self.gray_overlay.draw(surface)
                try:
                    self.promotion_table.draw(surface)
                except IndexError:  #Sometimes happens here after chosing a char
                    pass
            if self.show_score and self.scoreboard:
                self.scoreboard.draw(surface)
            elif self.console_active:
                self.overlay_console.draw(surface)
            if self.dialog and self.dialog.visible:
                self.gray_overlay.draw(surface)
                self.dialog.draw(surface)
        except pygame.error: 
            LOG.log(*MESSAGES.LOCKED_SURFACE_EXCEPTION)
        
    def event_handler(self, event, keys_pressed, mouse_buttons_pressed, mouse_movement=False, mouse_pos=(0, 0)):
        """Handles any pygame event. This allows for user interaction with the object.
        Args:
            event (:obj: pygame.event): Event received from the pygame queue.
            keys_pressed (:dict: pygame.keys):  Dict in which the keys are keys and the items booleans.
                                                Said booleans will be True if that specific key was pressed.
            mouse_buttons_pressed (:list: booleans):    List with 3 positions regarding the 3 normal buttons on a mouse.
                                                        Each will be True if that button was pressed.
            mouse_movement (boolean, default=False):    True if there was mouse movement since the last call.
            mouse_pos (:tuple: int, int, default=(0,0)):Current mouse position. In pixels.
        """
        if not self.finished and (self.started or self.dialog):
            super().event_handler(event, keys_pressed, mouse_buttons_pressed, mouse_movement=mouse_movement, mouse_pos=mouse_pos)

    def keyboard_handler(self, keys_pressed, event):
        """Handles any pygame keyboard related event. This allows for user interaction with the object.
        Args:
            keys_pressed (:dict: pygame.keys):  Dict in which the keys are keys and the items booleans.
                                                Said booleans will be True if that specific key was pressed.
        """
        super().keyboard_handler(keys_pressed, event)
        if self.dialog:
            return
        if keys_pressed[pygame.K_TAB]:
            self.show_score = not self.show_score

    #Does all the shit related to the mouse hovering an option
    def mouse_handler(self, event, mouse_buttons, mouse_movement, mouse_position):
        """Handles any mouse related pygame event. This allows for user interaction with the object.
        Args:
            event (:obj: pygame.event): Event received from the pygame queue.
            mouse_buttons (List->boolean): List with 3 positions regarding the 3 normal buttons on a mouse.
                                            Each will be True if that button was pressed.
            mouse_movement( boolean, default=False):    True if there was mouse movement since the last call.
            mouse_position (Tuple-> (int, int), default=(0,0)):   Current mouse position. In pixels.
        """
        #IF THERE IS A DIALOG ON TOP WE MUST NOT INTERACT WITH WHAT IS BELOW IT
        if self.dialog: #Using it here since we wont have ever a scrollbar in a board, and this saves cycles wuen a dialog is not active
            #Thats why we call the super method here instead of doing in the overloaded method.
            super().mouse_handler(event, mouse_buttons, mouse_movement, mouse_position)
            return
        if not self.ai_turn_flag.is_set():  #We don't want the majority of mouse interactions to work in the CPU turn
            return
        #CHECKING BUTTONS FIRST. CLICK DOWN
        if event.type == pygame.MOUSEBUTTONDOWN:  #On top of the char and clicking on it
            self.play_sound('key')
            #Help dialogs showing
            if mouse_buttons[1] and self.help_button.sprite.enabled:
                #First lets check if there is any dialog left TODO
                # element = next((char for char in self.characters if char.dialog_active), None)
                # new_element = None
                # if not element:
                #     element = next((element for element in self.sprites if element.dialog_active), None)
                # if self.active_char.sprite:
                #     self.active_char.sprite.set_help_dialog_state(not self.active_char.sprite.dialog_active)
                #     new_element = self.active_char.sprite
                # elif self.fitness_button.sprite.hover:
                #     self.fitness_button.sprite.set_help_dialog_state(not self.active_char.sprite.dialog_active)
                #     new_element = self.fitness_button.sprite
                # elif self.help_button.sprite.hover:
                #     self.help_button.sprite.set_help_dialog_state(not self.active_char.sprite.dialog_active)
                #     new_element = self.help_button.sprite
                # if element and new_element is not element:
                #     element.hide_help_dialog()
                return
            if self.show_promotion:
                try:
                    element = next(element for element in self.promotion_table.elements if element.hover)
                    self.swapper.send(element)
                    self.next_player_turn()
                except StopIteration:    #No hover found :(
                    return
            elif self.active_char.sprite: 
                self.pickup_character()
            elif self.dice.sprite.hover and not self.ai_turn:
                self.shuffle()
            elif self.fitness_button.sprite.hover:
                self.fitness_button.sprite.set_enabled(not self.fitness_button.sprite.enabled)
            elif self.help_button.sprite.hover:
                self.help_button.sprite.set_enabled(not self.help_button.sprite.enabled)

        #CLICK UP
        elif event.type == pygame.MOUSEBUTTONUP:  #If we are dragging it we will have a char in here
            if self.drag_char.sprite:   self.drop_character()
        
        #NOW CHECKING MOUSE MOVEMENT
        if mouse_movement and not self.dice.sprite.currently_shuffling:
            mouse_sprite = UtilityBox.get_mouse_sprite()
            if self.show_promotion:
                for element in self.promotion_table.elements:                           element.set_hover(False)
                for colliding in self.promotion_table.get_collisions(mouse_sprite):     colliding.set_hover(True)
                return

            if not self.ai_turn:
                #Checking if Im holding a sprite
                if self.drag_char.sprite:
                    self.drag_char.sprite.rect.center = mouse_position
                    if self.get_effect('selection_effect'):
                        if not self.get_effect('selection_effect').enabled:
                            self.play_effect('selection_effect', mouse_position)
                        else:
                            self.get_effect('selection_effect').rect.center = mouse_position
                
                #Checking collision with cells (Using this instead of hit_sprite because the hit method is different)
                collided_cell = pygame.sprite.spritecollideany(mouse_sprite, self.cells, collided=pygame.sprite.collide_circle)
                self.set_active_cell(collided_cell)
            #Checking collision with paths (Using this instead of hit_sprite because the hit method is different)
            path = pygame.sprite.spritecollideany(mouse_sprite, self.paths, collided=pygame.sprite.collide_mask)
            self.set_active_path(path)

            if pygame.sprite.spritecollideany(mouse_sprite, self.dice, collided=pygame.sprite.collide_mask):
                self.dice.sprite.set_hover(True)
            else:
                self.dice.sprite.set_hover(False)

            if pygame.sprite.spritecollideany(mouse_sprite, self.fitness_button, collided=pygame.sprite.collide_mask):
                self.fitness_button.sprite.set_active(True)
                self.fitness_button.sprite.set_hover(True)
            else:
                self.fitness_button.sprite.set_active(False)
                self.fitness_button.sprite.set_hover(False)
                
            if pygame.sprite.spritecollideany(mouse_sprite, self.help_button, collided=pygame.sprite.collide_mask):
                self.help_button.sprite.set_active(True)
                self.help_button.sprite.set_hover(True)
            else:
                self.help_button.sprite.set_active(False)
                self.help_button.sprite.set_hover(False)

    def shuffle(self):
        """Shuffles and throws the board's infoboard's dice. Upon returning a value, the method
        dice_result_value is called. A result can yield you a turncoat method or the losing of your turn."""
        self.play_sound('die_shuffle')
        self.dice.sprite.shuffle()

    def character_swapper(self):
        """This is to try a generator in a kinda non-generator situation"""
        while True:
            original_char = yield
            new_char = yield
            cell = self.get_cell_by_real_index(original_char.current_pos)
            cell.add_char(new_char)
            player = next(player for player in self.players if player.uuid == original_char.owner_uuid)
            player.revive_char(new_char, original_char)
            new_char.set_size(tuple(x*self.params['char_proportion'] for x in cell.rect.size))
            new_char.set_cell(cell)
            new_char.set_hover(False)
            self.characters.remove(original_char)
            self.characters.add(new_char)
            LOG.log('info', 'Character ', original_char.id, ' switched to ', new_char.id)
            self.after_swap(original_char, new_char)

    def after_swap(self, orig_char, new_char):
        """Args:
            orig_char(:Obj:Character):  Character that will be exchanged for the captured one.
            new_char(:Obj:Character):   Character that has been freed again and placed on the cell of the original one.
        Method that executes after a character swap is done."""
        self.show_promotion = False
        self.play_effect('explosion', new_char.rect.center)

    def pickup_character(self, get_dests=True):
        """Picks up a character. Adds it to the drag char Group, and check in the LUT table
        the movements that are possible taking into account the character restrictions.
        Then it draws an overlay on the possible destinations."""
        LOG.log('debug', 'Selected ', self.active_char.sprite.id)
        self.drag_char.add(self.active_char.sprite)
        self.drag_char.sprite.set_selected(True)
        self.last_cell.add(self.active_cell.sprite)
        if get_dests and self.last_cell.sprite.get_real_index() not in self.locked_cells:
            movements = self.drag_char.sprite.get_paths(self.enabled_paths, self.distances, self.current_map,\
                                                            self.active_cell.sprite.index, self.params['circles_per_lvl'])
            if self.fitness_button.sprite.enabled:  #If we want them to show
                self.generate_fitnesses(self.active_cell.sprite.get_real_index(), movements)
            for movement in movements:
                if movement[-1] not in self.locked_cells:
                    self.possible_dests.add(self.get_cell_by_real_index(movement[-1]))
            for dest in self.possible_dests:
                dest.set_active(True)

    @run_async_not_pooled
    def generate_fitnesses(self, source_cell, destinations, lite=False):
        """Gets the fitness for each movement consisting of moving from a source position to a destination.
        This score will be only processed once in each turn. Afterwards it will be only fetched.
        the lite flag call a less complex but less reliable algorithm"""
        try:
            self.fitnesses[source_cell]
        except KeyError:
            self.fitnesses[source_cell] =   PathAppraiser.rate_movements(self.active_cell.sprite.get_real_index(), tuple(x[-1] for x in destinations), self.enabled_paths,\
                                                                self.distances, self.current_map, self.cells.sprites(), self.params['circles_per_lvl']) if not lite else \
                                            PathAppraiser.rate_movements_lite(self.active_cell.sprite.get_real_index(), tuple(x[-1] for x in destinations), self.enabled_paths,\
                                                                    self.current_map, self.cells.sprites(), self.params['circles_per_lvl'])
        for fitness_key, fitness_value in self.fitnesses[source_cell].items():
            if self.drag_char.sprite:   #If we didnt drop the char before the fitnesses were assigned
                dest_cell = self.get_cell_by_real_index(fitness_key)
                dest_cell.show_fitness_value(fitness_value)
            else:
                break

    def hide_fitnesses(self, source_cell):
        """Hide the graphical string that shows the score of each cell."""
        try:
            cells_to_hide = list(self.fitnesses[source_cell].keys())
            for fitness_key in cells_to_hide:
                dest_cell = self.get_cell_by_real_index(fitness_key)
                dest_cell.hide_fitness_value()
        except KeyError:
            pass #This is due to pick and drop the char too fast, so we still haven't assigned the fitnesses for that cell
            
    def drop_character(self):
        """Drops a character. Deletes it from the drag char Group, and checks if the place in which
        has been dropped is a possible destination. If it is, it drops the character in that cell.
        Otherwise, the character will be returned to the last Cell it was in."""
        LOG.log('debug', 'Dropped ', self.drag_char.sprite.id)
        self.hide_fitnesses(self.last_cell.sprite.get_real_index())
        moved = False
        self.drag_char.sprite.set_selected(False)
        self.drag_char.sprite.set_hover(False)
        if self.last_cell.sprite is self.active_cell.sprite:
            self.drag_char.sprite.set_center(self.last_cell.sprite.center)
            LOG.log('debug', 'Moving towards the same cell you were in doesnt count')
        elif self.possible_dests.has(self.active_cell.sprite)\
        or self.admin_mode and self.active_cell.sprite:
            self.move_character(self.drag_char.sprite)
            moved = True
        else:
            self.drag_char.sprite.set_center(self.last_cell.sprite.center)
            self.play_sound('warning')
            LOG.log('debug', 'Cant move the char there')
        self.drag_char.empty()
        for dest in self.possible_dests:
            dest.set_active(False)
        self.possible_dests.empty()
        return moved

    def shuffling_frame(self):
        """Increases the time between frame change in the dice, thus creating a 'slowing down' animation for the dice."""
        self.current_dice.sprite.increase_animation_delay()

    def assign_current_dice(self, dice_id):
        """Changes the dice that will receive the user interactions."""
        if self.dialog and 'dice' in self.dialog.id and not all(flag.is_set() for flag in self.starting_dices.values()):    #This is a throw in the starting dices
            self.play_sound("die_shuffle")
            if not self.current_dice.sprite or not self.current_dice.sprite.currently_shuffling:    #If there is no dice of is not shuffling
                self.current_dice.add(next((dice for dice in self.dialog.elements if dice.id == dice_id), None))

    def dice_value_result(self, event):
        """ Gets the value of a local dice throw and registers it in the board dice, or the starting dice screen,
        whatever it matches to.
        Args:
            event(:obj: pygame.Event):  Event containing the local dice throw result"""
        value = int(event.value)
        received_dice_id = event.id #The received dice id is the same uuid as the matching player uuid
        if self.dialog and 'dice' in self.dialog.id:    #This is a throw in the starting dices
            self.play_sound("die_throw")
            self.starting_dices[int(received_dice_id)].set()
            self.dices_values[int(received_dice_id)] = value
            next(dice for dice in self.dialog.elements if dice.id == received_dice_id).deactivating_dice(value=value) #We disable the received dice.
            if all(flag.is_set() for flag in self.starting_dices.values()): #CHECKING IF ALL THE DICES IN THE STARTING SCREEN HAVE BEEN THROWN
                all_values = [(player_uuid, value) for player_uuid, value in self.dices_values.items()]
                all_values.sort(key=lambda player_value: player_value[-1], reverse=True)
                ordered_players = [next(player for player in self.players if player.uuid == player_throwvalue[0]) for player_throwvalue in all_values]
                self.players = ordered_players
                #Synchronizing turns again
                self.turn=-1    #WIll start after the last line of this method, in the self.turn 0
                for player in self.players:    
                    player.turn=0
                #And now settings everything so the next turn is the player with the highest throw
                self.current_player = self.players[-1]  #To make the next player turn be the self.players[0]
                self.current_player.turn -= 1  #To compensate for this turn addition
                self.player_index = len(self.players)-1  #To make the next player turn be the self.players[0]
                self.post_event('hide_dialog_temp') #So we have time to check the results
                self.current_dice.empty()
                self.current_dice.add(self.dice.sprite)
            value = -1  #To jump to the next player turn line.
        if value == Dice.GOLD_VALUE:
            self.activate_turncoat_mode()
            return
        self.next_player_turn()

    def activate_turncoat_mode(self):
        """Allows the current player to choose any of the characters on the board to play, as long as it is not an enemy matron mother."""
        #block the cells with matrons and... the last one of the turncoat. The last one persists for the next turn. dunno how to do the later
        self.post_event('turncoat')
        for cell in self.cells:
            if cell.has_char() and 'mother' in cell.get_char().get_type():
                self.locked_cells.append(cell.get_real_index())
        for char in self.characters:
            if not 'mother' in char.get_type():
                char.set_active(True)
                char.set_state('idle')
        for path in self.current_map:
            if path.ally:   #Not to worry, those changes will be cleared in the next player turn
                path.ally = False
                path.enemy = True
                path.access = True

    def move_character(self, character):
        """Moves effectively the input character, cleaning the last cell and adding it to the new one.
        Also takes care of any additional triggered action, like a capture or the activation of a dialog.
        Args:
            character(:obj: Character): Character to move.
        """
        LOG.log('debug', 'The chosen cell is possible, moving')
        active_cell = self.active_cell.sprite
        self.last_cell.sprite.empty_cell() #Emptying to delete the active char from there
        character.set_cell(active_cell)  #Positioning the char
        if not active_cell.is_empty():
            self.kill_character(active_cell, self.drag_char.sprite) #Killing char if there is one 
        active_cell.add_char(character)
        try:
            self.current_player.register_movement(character)
        except AttributeError:  #Turncoat mode
            character.movements += 1
        self.update_cells(self.last_cell.sprite, active_cell)
        self.last_movement = (self.last_cell.sprite.text_pos, active_cell.text_pos)
        self.last_real_movm = (self.last_cell.sprite.index, active_cell.index)
        self.last_char = character
        #Showing effects
        self.play_effect('start_teleport', self.last_cell.sprite.rect.center)
        self.play_effect('end_teleport', active_cell.rect.center)
        self.play_sound('success')
        #Not last cell anymore, char was dropped succesfully
        self.last_cell.empty()
        #THIS CONDITION TO SHOW THE UPGRADE TABLE STARTS HERE
        if active_cell.promotion and (None != active_cell.owner != character.owner_uuid):
            if 'champion' in self.drag_char.sprite.get_type().lower():
                self.update_character(self.drag_char.sprite)
            elif self.drag_char.sprite.upgradable\
            and any(not char.upgradable for char in self.current_player.fallen):
                self.promotion_flag.clear()
                self.update_promotion_table(*tuple(char for char in self.current_player.fallen if not char.upgradable))
                self.show_promotion = True
                self.swapper.send(self.drag_char.sprite)
                return
        self.next_char_turn(self.drag_char.sprite)

    def update_character(self, char):
        """Makes a character evolve. This is used with the Holy Champion for now.
        It is capable of capturing and be killed after this, and his value increases too.
        To execute when placed on the promotion cell (If the char fills the conditions).
        Args:
            char(:Obj:Character):   Character to make changes to."""
        char.can_kill = True
        char.can_die = True
        char.value *= 3

    def next_char_turn(self, char):
        """Advances a character turn. Each movement of a character ends with this method.
        This could trigger a change of player or not. It all depends on the character moved.
        Also activates and deactivates characters as it is needed.
        Args:  
            char(:obj:Character):   Last character moved that triggered this method."""
        self.fitnesses = {} #Cleaning the history of fitnesses
        self.char_turns += 1
        if self.char_turns >= char.turns:
            self.char_turns = 0
            self.next_player_turn()
        elif self.char_turns < char.turns and self.char_turns == 1:
            self.update_infoboard()
            self.current_player.pause_characters()
            char.set_state('idle')
            char.active = True  #Only can move this one afterwards
            if not self.current_player.human:
                self.do_ai_player_turn()
                return
        char.update_info_sprites()

    def next_player_turn(self, use_stop_state=True):
        """Advances a player turn. Called after each player is done with his actions in a turn.
        Increases the turn in the player and in the board, and updates the current_map structure, according to
        the final result of this board turn actions. Also changes the current player.
        Pauses and unpauses specific characters if needed.
        Calls the AI player logic if his turn is the next one.
        Args:
            use_stop_state(boolean):    Flag, if it is true the characters of the old current player are paused.
        """
        self.current_player.turn += 1
        del self.locked_cells[:]    #Clearing it just in case
        old_index = self.player_index
        while True:
            self.player_index += 1
            if self.player_index >= len(self.players):
                self.player_index = 0
                self.turn += 1
            if not self.players[self.player_index].dead\
            and (self.players[self.player_index].turn is self.turn or self.player_index is old_index):
                self.current_player = self.players[self.player_index] 
                self.update_map()
                if use_stop_state:
                    self.players[old_index].pause_characters()
                    self.current_player.unpause_characters()
                break
        self.dice.sprite.add_turn(self.current_player.uuid)
        self.update_scoreboard()
        self.update_infoboard()
        if not self.current_player.human:
            self.current_player.pause_characters()  #We don't want the human players fiddling with the chars
            self.do_ai_player_turn()

    @run_async_not_pooled
    def do_ai_player_turn(self, result=None):
        """All the logic executed in a complete computer player controlled turn.
        Gets the next movement according to the player's settings (IA mode, timeout per round...),
        picks a character from the promotion table if this one is shown...
        In short, the IA player turn.
        Args: 
            result(Tuple->(int, int), default=None):  The movement executed by the computer player in this turn."""
        if self.end:    #We make here the only check since this is one of the methods that can call itself and go on until the end of the game
            return
        self.ai_turn_flag.wait()
        self.ai_turn_flag.clear()
        if not all(flag.is_set() for flag in self.starting_dices.values()): #IF this structure is empty, due to not having starting dices, it also returns True.
            computer_dice = next(dice for dice in self.dialog.elements if str(dice.id) == str(self.current_player.uuid))
            computer_dice.reactivating_dice()
            computer_dice.hitbox_action()
            self.ai_turn_flag.set()
            return
        #Counter of round time
        self.counter_sprite.sprite.start_counter()
        self.counter_sprite.sprite.set_enabled(True)
        start = time.time()
        self.ai_turn = True
        self.thinking_sprite.sprite.set_visible(True)
        char_that_must_move = []
        restricted_movements = []
        if self.char_turns is not 0:    #If we moved a character that can move more than once
            char_that_must_move.append(self.get_cell_by_real_index(self.last_real_movm[-1]).get_char())
            restricted_movements = self.last_real_movm
        movement = self.current_player.get_movement(self.__hash__(), self.current_map, self.cells, self.current_player.uuid, [player.uuid for player in self.players],\
                                                    chars_allowed=char_that_must_move, restricted_movements=restricted_movements)
        LOG.log('debug', "Movement chosen was ", movement)
        character = self.get_cell_by_real_index(movement[0]).get_char()
        self.drag_char.add(character)
        self.last_cell.add(self.get_cell_by_real_index(movement[0]))
        self.active_cell.add(self.get_cell_by_real_index(movement[-1]))
        self.move_character(character)  #In here the turn is incremebted one (next_char_turn its executed)
        should_go_next_turn = False
        if self.show_promotion: #If the update table was triggered
            self.promotion_flag.wait()
            #Should get the highest valued char. And wait until it is full. Also do this for usual players (human ones), but whatever
            char_revived = random.choice(self.promotion_table.elements.sprites())
            self.swapper.send(char_revived)
            should_go_next_turn = True
        self.drag_char.empty()
        self.thinking_sprite.sprite.set_visible(False)
        self.ai_turn = False
        if result:  #We return the movement performed. Useful for network board. 
            result = movement
        self.counter_sprite.sprite.set_enabled(False)
        LOG.log('info', "The CPU turn took ", (time.time()-start), " seconds.")
        self.ai_turn_flag.set()
        if should_go_next_turn:
            self.next_player_turn()

    def kill_character(self, cell, killer):
        """Captures or 'kills' a character in a cell.
        Args:
            cell(:obj: Cell):   Cell in which resides the character to be captured
            killer (:obj: Character):   Character that captures the one in the cell."""
        self.play_effect('explosion', cell.rect.center)
        corpse = cell.kill_char()
        self.update_cells(cell)
        self.characters.remove(corpse)  #To delete it from the char list in board. It's dead.
        #Search for it in players to delete it
        for player in self.players:
            if player.has_char(corpse):
                player.remove_char(corpse)
                self.check_player(player)
        try:
            self.current_player.add_kill(corpse, killer)
        except AttributeError:  #AttributeError: \'NoneType\' object has no attribute \'kills\', that's because we are in turncoat mode
            LOG.log('Info', 'Nice turncoat capture by ', killer.id, '! He didnt even see it coming!')
            killer.kills -= 1
        LOG.log('debug', 'The character ', corpse.id,' was killed!')
        self.play_sound('oof')

    def check_player(self, player):
        """Checks if the input player can still play in the game, by checking if his essential piece (matron mother)
        is still alive.
        If there is only a player left, it ends the game and shows the winner.
        Args:
            player(:obj: Player):   Player to check."""
        if player.has_lost():
            self.characters.remove(player.characters)
            for char in player.characters:
                self.get_cell_by_real_index(char.current_pos).empty_cell()
            if sum(1 for player in self.players if not player.dead) <= 1:  #WE HAVE A WINNER!
                self.win()

    def win(self):
        """Method to execute when a winner is decided. Shows a popup, play a sound and ends the board."""
        LOG.log("info", "Winner winner chicken dinner!")
        self.play_sound('win')
        self.post_event('win')
        self.finished = True    #To disregard events except esc and things like that
        self.show_score = True  #To show the infoboard.
        self.end = True
        winner = next((player for player in self.players if not player.dead), None)
        if winner:
            LOG.log('info', 'The winner was ', winner.name)
            LOG.log('info', winner) #The rest of the info

    def set_active_cell(self, cell):
        """Changes the current active cell, the last one that the user interacted with. This shows graphically too.
        Args: 
            cell (:obj: Cell):  The new active cell."""
        if self.active_cell.sprite: #If there is already an sprite in active_cell
            if cell is not self.active_cell.sprite: #If its not the same cell that is already active, or is None
                self.active_cell.sprite.set_active(False)
                self.active_cell.sprite.set_hover(False)
                self.active_char.empty()
                self.active_cell.empty()
            else:   #If its the same one (Hovering or mouse still)
                return
        if cell:    #If its not None
            cell.set_active(True)
            cell.set_hover(True)
            if self.drag_char.sprite:
                self.drag_char.sprite.set_hover(True)
            self.active_cell.add(cell)
            char = self.active_cell.sprite.has_char()
            if char and char.active:
                self.active_char.add(char)
        else:
            if self.drag_char.sprite:
                self.drag_char.sprite.set_hover(False)

    def set_active_path(self, path):
        """Changes the current active circular path. This shows graphically. Has no impact in the logic or other methods.
        Args:
            path (:obj: Circumference):  New active circular path."""
        if self.active_path.sprite: #If there is already an sprite in active_cell
            if path is not self.active_path.sprite: #If its not the same cell that is already active, or is None
                self.active_path.sprite.set_active(False)
                self.active_path.sprite.set_hover(False)
                self.active_path.empty()
            else:   #If its the same one (Hovering or mouse still)
                return
        if path:    #If its not None
            path.set_active(True)
            path.set_hover(True)
            self.active_path.add(path)
        
    def destroy(self):
        """Sets the end flag to true. This will end the methods that depends on it."""
        self.end = True

    def __hash__(self):
        """Returns the hash value of this board instance."""
        _ = self.params
        return hash((_['quadrants_overlap'], _['inter_path_frequency'], _['circles_per_lvl'], _['max_levels'],\
                    _['center_cell']))