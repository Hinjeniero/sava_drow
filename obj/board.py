"""--------------------------------------------
board module. Contains the entire logic and graphics to build
the game's board.
Have the following classes.
    Board
--------------------------------------------"""

__all__ = ['Board']
__version__ = '0.9'
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
#Selfmade libraries
from settings import MESSAGES, USEREVENTS, PATHS
from obj.screen import Screen, LoadingScreen
from obj.dice import Dice
from obj.cell import Cell, Quadrant
from obj.paths import Path, PathAppraiser
from obj.ai_player import ComputerPlayer
from obj.players import Player, Character, Restriction
from obj.sprite import Sprite
from obj.ui_element import ButtonAction, TextSprite, InfoBoard, Dialog, ScrollingText
from obj.polygons import Circle, Rectangle, Circumference
from obj.utilities.utility_box import UtilityBox
from obj.utilities.colors import RED, WHITE, DARKGRAY, LIGHTGRAY, TRANSPARENT_GRAY
from obj.utilities.exceptions import BadPlayersParameter, BadPlayerTypeException,\
                                    PlayerNameExistsException, TooManyCharactersException, NotEnoughSpaceException
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
                        'help_button_texture'   : None
    }
    #CHANGE MAYBE THE THREADS OF CHARACTER TO JOIN INSTEAD OF NUM PLAYERS AND SHIT
    def __init__(self, id_, event_id, end_event_id, resolution, *players, empty=False, **params):
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
        self.fitness_button = pygame.sprite.GroupSingle()
        self.help_button    = pygame.sprite.GroupSingle()
        self.paths          = pygame.sprite.Group()
        self.characters     = pygame.sprite.OrderedUpdates()
        self.current_player = None  #Created in add_player
        self.scoreboard     = None  #Created in Board.generate
        self.scoreboard_flag= False
        self.show_score     = False
        self.promotion_table= None  #Created in Board.generate
        self.gray_overlay   = None  #Created in Board.generate
        self.show_promotion = False

        #Utilities to keep track
        self.active_cell    = pygame.sprite.GroupSingle()
        self.last_cell      = pygame.sprite.GroupSingle()
        self.active_path    = pygame.sprite.GroupSingle()
        self.active_char    = pygame.sprite.GroupSingle()
        self.drag_char      = pygame.sprite.GroupSingle()
        self.platform       = None  #Created in Board.generate
        
        #Paths and maping
        self.distances      = None  #Created in Board.generate
        self.enabled_paths  = None  #Created in Board.generate
        self.current_map    = {}
        
        #Players 
        self.total_players  = 0
        self.loaded_players = 0
        self.players        = []
        self.player_index   = 0

        #Started
        self.started        = False
        self.finished       = False
        self.generated      = False
        self.admin_mode     = False
        self.win_event      = pygame.event.Event(end_event_id, command='win')
        self.lose_event     = pygame.event.Event(end_event_id, command='lose')
        self.swapper        = None
        Board.generate(self, empty, *players)
    
    ###SIMULATES ON_SCREEN CONSOLEEEE
    def LOG_ON_SCREEN(self, *msgs, **text_params):
        text = Parser.parse_texts(*msgs)
        LOG.log('info', text)
        self.overlay_console.add_msg(text, **text_params)

    #ALL THE GENERATION OF ELEMENTS AND PLAYERS NEEDED
    @staticmethod
    def generate(self, empty, *players):
        UtilityBox.join_dicts(self.params, Board.__default_config)
        #INIT
        self.generate_onscreen_console()
        if self.params['loading_screen']:
            self.loading_screen = LoadingScreen(self.id+"_loading", self.event_id, self.resolution, text=self.params['loading_screen_text'])
        #REST
        self.platform = self.generate_platform()
        if not empty:
            self.generate_mapping()
            self.generate_environment()
        else:
            self.LOG_ON_SCREEN("WARNING: Generating board in empty mode, needs server attributes to work")
        self.add_players(*players)
        self.swapper = self.character_swapper() #Simple generator to promote characters
        self.swapper.send(None) #Needed in the first execution of generator

    def generate_onscreen_console(self):
        start = time.time()
        self.overlay_console = ScrollingText('updates', self.event_id, self.resolution, transparency=180)
        LOG.log('info', 'The console have been generated in ', (time.time()-start)*1000, 'ms')

    @no_size_limit
    def generate_platform(self):
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
        axis_size = self.params['circles_per_lvl']*self.params['max_levels']
        if self.params['center_cell']:
            axis_size += 1
        dimensions          = (axis_size, axis_size)
        self.distances      = numpy.full(dimensions, -888, dtype=int)   #Says the distance between cells
        self.enabled_paths  = numpy.zeros(dimensions, dtype=bool)       #Shows if the path exist

    @time_it
    def generate_environment(self):
        threads = [self.generate_all_cells(), self.generate_paths(offset=True), self.generate_map_board(), self.generate_infoboard()]
        for end_event in threads:   end_event.wait()
        self.adjust_cells()
        threads = [self.generate_inter_paths(), self.generate_dice()]
        for end_event in threads:   end_event.wait()
        #Generate fitness and help buttons
        fitness_button = ButtonAction('fitness_button', "", self.event_id, (0, 0), tuple(x*0.1 for x in self.resolution), self.resolution,\
                                    texture=self.params['fitness_button_texture'], text="")

        #fitness_button.set_position((self.dice.sprite.rect.x, self.dice.sprite.rect.y-fitness_button.rect.height))
        fitness_pos_y = self.dice.sprite.rect.centery-((fitness_button.rect.height//2+self.dice.sprite.rect.height//2)//0.9)
        fitness_button.set_center((self.dice.sprite.rect.centerx, fitness_pos_y))

        help_button = ButtonAction('help_button', "", self.event_id, (0, 0), tuple(x*0.1 for x in self.resolution), self.resolution,\
                                    texture=self.params['help_button_texture'], text="")

        help_pos_y = fitness_button.rect.centery-((fitness_button.rect.height//2+help_button.rect.height//2)//0.9)
        help_button.set_center((fitness_button.rect.centerx, help_pos_y))

        self.fitness_button.add(fitness_button), self.help_button.add(help_button)
        #End, saving
        self.save_sprites()
        self.generated = True

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
            #LOG.log('debug', quadrant_number, ": ", quadrant_cells)
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
        infoboard = InfoBoard(self.id+'_infoboard', 0, (0, 0), (0.15*self.resolution[0], self.resolution[1]),\
                    self.resolution, texture=self.params['infoboard_texture'], keep_aspect_ratio = False, rows=6, cols=2)
        infoboard.set_position((self.resolution[0]-infoboard.rect.width, 0))
        infoboard.add_text_element('turn_label', 'Board turn', 1, scale=1.4)
        infoboard.add_text_element('turn', str(self.turn+1), 1, scale=0.6)
        infoboard.add_text_element('turn_char_label', 'Char turn', 1, scale=1.4)
        infoboard.add_text_element('turn_char', str(self.char_turns+1), 1, scale=0.6)
        infoboard.add_text_element('player_name_label', 'Playing: ', 1)
        self.infoboard = infoboard
        self.LOG_ON_SCREEN("The game infoboard has been generated")

    @run_async_not_pooled
    def update_infoboard(self):
        self.infoboard.update_element('turn', str(self.turn+1))
        self.infoboard.update_element('turn_char', str(self.char_turns+1))
        self.infoboard.update_element('player_name', self.current_player.name)

    @run_async
    def generate_dice(self):
        dice = Dice('dice', (0, 0), tuple(0.1*x for x in self.resolution), self.resolution, shuffle_time=1500, sprite_folder=self.params['dice_textures_folder'], animation_delay=2)
        dice.set_position((self.infoboard.rect.centerx-dice.rect.width//2, self.resolution[1]-(dice.rect.height*2)))
        self.dice.add(dice)
        self.LOG_ON_SCREEN("Dice has been generated")

    @no_size_limit
    def generate_dialogs(self):
        self.scoreboard = self.generate_scoreboard()
        promotion_table = Dialog(self.id+'_promotion', USEREVENTS.DIALOG_USEREVENT, (self.resolution[0]//1.05, self.resolution[1]//8),\
                                self.resolution, keep_aspect_ratio = False, texture=self.params['promotion_texture'])
        self.promotion_table = promotion_table
        self.gray_overlay = ScrollingText('nuthing', self.event_id, self.resolution, transparency=128)
        self.LOG_ON_SCREEN("The board scoreboard and promotion table have been generated.")

    def generate_scoreboard(self):
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
        if not self.scoreboard_flag:    #THis is to not overlap turns updates.
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
            LOG.log('info', 'The scoreboard has been successfully updated.')

    @run_async_not_pooled
    def update_promotion_table(self, *chars):
        self.promotion_table.full_clear()
        self.promotion_table.set_rows(1)
        self.promotion_table.set_cols(len(chars))
        for char in chars:
            if not char.upgradable: #Upgradable ones cannot be upgraded to
                self.promotion_table.add_sprite_to_elements(1, char)
        LOG.log('info', 'The promotion table has been successfully updated.')

    def adjust_cells(self):
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
        self.sprites.add(self.platform, self.inter_paths.sprite, *self.paths.sprites(), *self.cells.sprites(), self.infoboard, self.dice, self.fitness_button, self.help_button)

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
        for cell in cells:
            self.current_map[cell.get_real_index()]=cell.to_path(self.current_player.uuid)

    def set_resolution(self, resolution):
        """Changes the resolution of the Screen. It also resizes all the Screen elements.
        Args:
            resolution (:tuple: int, int):  Resolution to set. In pixels."""
        super().set_resolution(resolution)
        self.loading_screen.set_resolution(resolution)
        for player in self.players:
            player.set_resolution(resolution)
        #Othewise the bezier curves just get fucked up when resizing back and forth.
        self.generate_inter_paths()
        self.sprites.empty()
        self.save_sprites()

    def ALL_PLAYERS_LOADED(self):
        """Returns:
            (boolean): True if all the requested players have been loaded already."""
        if not self.started and (self.loaded_players is self.total_players) and self.generated:
            self.players.sort(key=lambda player:player.order)
            self.play_sound('success')
            if not self.current_player: #If this is the first player added
                self.current_player = self.players[0]
                self.infoboard.add_text_element('player_name', self.players[0].name, 1)
                self.current_player.unpause_characters()
                self.update_map()       #This goes according to current_player
            self.dice.sprite.add_turn(self.current_player.uuid)
            self.started = True
            self.generate_dialogs()
            self.update_scoreboard()
            self.console_active = False

    def create_player(self, name, number, chars_size, cpu=False, cpu_mode=None, empty=False, **player_settings):
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
        self.__create_player(name, number, chars_size, cpu, empty, cpu_mode, **player_settings)
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
                for character in player.characters:
                    if character.rank < rank:
                        current_level -= 1
                        rank = character.rank
                    character.set_size(self.cells.sprites()[0].rect.size)
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
    def __create_player(self, player_name, player_number, chars_size, cpu, empty, ia_mode, **player_params):
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
                                    player_number, chars_size, self.resolution, ia_mode=ia_mode, **player_params)
        else:
            player = Player(player_name, player_number, chars_size, self.resolution, empty=empty, **player_params)
        self.__add_player(player)

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
            super().draw(surface)                   #Draws background
            for char in self.characters:
                char.draw(surface)
            if self.current_player:
                self.current_player.draw(surface)   #This draws the player's infoboard
            if self.promotion_table and self.show_promotion:
                self.gray_overlay.draw(surface)
                self.promotion_table.draw(surface)
            if self.show_score and self.scoreboard:
                self.scoreboard.draw(surface)
            if self.console_active:
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
        Posibilities:
        TODO
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
        Posibilities:
        TODO
        Args:
            event (:obj: pygame.event): Event received from the pygame queue.
            mouse_movement( boolean, default=False):    True if there was mouse movement since the last call.
            mouse_position (:tuple: int, int, default=(0,0)):   Current mouse position. In pixels.
        """
        #IF THERE IS A DIALOG ON TOP WE MUST NOT INTERACT WITH WHAT IS BELOW IT
        if self.dialog: #Using it here since we wont have ever a scrollbar in a board, and this saves cycles wuen a dialog is not active
            #Thats why we call the super method here instead of always
            super().mouse_handler(event, mouse_buttons, mouse_movement, mouse_position)
            return
        
        #CHECKING BUTTONS FIRST. CLICK DOWN
        if event.type == pygame.MOUSEBUTTONDOWN:  #On top of the char and clicking on it
            self.play_sound('key')
            if mouse_buttons[1] and self.help_button.enabled:
                if self.active_char.sprite:
                    self.active_char.sprite.set_help_dialog_state(not self.active_char.sprite.dialog_active)
                    char_w_active_dialog = next((char for char in self.characters if (char.dialog_active and char is not self.active_char.sprite)), None)
                    if char_w_active_dialog:
                        char_w_active_dialog.hide_help_dialog()
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
            elif self.dice.sprite.hover:
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

            if self.drag_char.sprite:   
                self.drag_char.sprite.rect.center = mouse_position
            
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
            new_char.set_size(cell.rect.size)
            new_char.set_cell(cell)
            new_char.set_hover(False)
            self.characters.remove(original_char)
            self.characters.add(new_char)
            LOG.log('info', 'Character ', original_char.id, ' upgraded to ', new_char.id)
            self.after_swap(original_char, new_char)

    def after_swap(self, orig_char, new_char):
        self.show_promotion = False

    def pickup_character(self, get_dests=True):
        """Picks up a character. Adds it to the drag char Group, and check in the LUT table
        the movements that are possible taking into account the character restrictions.
        Then it draws an overlay on the possible destinations."""
        LOG.log('INFO', 'Selected ', self.active_char.sprite.id)
        self.drag_char.add(self.active_char.sprite)
        self.drag_char.sprite.set_selected(True)
        self.last_cell.add(self.active_cell.sprite)
        if get_dests:
            destinations = self.drag_char.sprite.get_paths(self.enabled_paths, self.distances, self.current_map,\
                                                            self.active_cell.sprite.index, self.params['circles_per_lvl'])
            if self.fitness_button.sprite.enabled:  #If we want them to show
                self.generate_fitnesses(self.active_cell.sprite.get_real_index(), destinations)
            for cell_index in destinations:
                if cell_index not in self.locked_cells:
                    self.possible_dests.add(self.get_cell_by_real_index(cell_index[-1]))
            for dest in self.possible_dests:
                dest.set_active(True)

    @run_async_not_pooled
    def generate_fitnesses(self, source_cell, destinations):
        try: 
            self.fitnesses[source_cell]
        except KeyError:
            self.fitnesses[source_cell] = PathAppraiser.rate_movement(self.active_cell.sprite.get_real_index(), tuple(x[-1] for x in destinations), self.enabled_paths,\
                                                                    self.distances, self.current_map, self.cells.sprites(), self.params['circles_per_lvl'])
        for fitness_key, fitness_value in self.fitnesses[source_cell].items():
            if self.drag_char.sprite:   #If we didnt drop the char before the fitnesses were assigned
                dest_cell = self.get_cell_by_real_index(fitness_key)
                dest_cell.show_fitness_value(fitness_value)
            else:
                break

    def hide_fitnesses(self, source_cell):
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
        LOG.log('INFO', 'Dropped ', self.drag_char.sprite.id)
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

    def dice_value_result(self, value):
        if value == 6:
            self.activate_turncoat_mode()
            return
        #TODO SHOW NOTIFICATION MAYBE? IN NETWOK BOARD AND HERE TOO
        self.next_player_turn()

    def activate_turncoat_mode(self):
        #block the cells with matrons and... the last one of the turncoat. The last one ppersists for the next turn. dunno how to do the later
        for cell in self.cells:
            if cell.has_char() and 'mother' in cell.get_char().get_type():
                self.locked_cells.append(cell.get_real_index())
        for char in self.characters:
            char.set_active(True)
            char.set_state('idle')
        for path in self.current_map:
            if path.ally:   #Not to worry, those changes will be cleared in the next player turn
                path.ally = False
                path.enemy = True
                path.access = True

    def move_character(self, character):
        LOG.log('debug', 'The chosen cell is possible, moving')
        active_cell = self.active_cell.sprite
        self.last_cell.sprite.empty_cell() #Emptying to delete the active char from there
        character.set_cell(active_cell)  #Positioning the char
        if not active_cell.is_empty():
            self.kill_character(active_cell, self.drag_char.sprite) #Killing char if there is one 
        active_cell.add_char(character)
        self.current_player.register_movement(character)
        self.update_cells(self.last_cell.sprite, active_cell)
        self.last_cell.empty()  #Not last cell anymore, char was dropped succesfully
        #THIS CONDITION TO SHOW THE UPGRADE TABLE STARTS HERE
        if active_cell.promotion and (None != active_cell.owner != character.owner_uuid):
            if 'champion' in self.drag_char.sprite.get_type().lower():
                self.update_character()
                #return #TODO CHECk THIS
            elif self.drag_char.sprite.upgradable\
            and any(not char.upgradable for char in self.current_player.fallen):
                self.update_promotion_table(*tuple(char for char in self.current_player.fallen if not char.upgradable))
                self.show_promotion = True
                self.swapper.send(self.drag_char.sprite)
                #return
        self.next_char_turn(self.drag_char.sprite)

    def update_character(self):
        self.drag_char.sprite.can_kill = True
        self.drag_char.sprite.can_die = True
        self.drag_char.sprite.value = 8

    def next_char_turn(self, char):
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
            print("Next player is computer controlled!")
            self.current_player.pause_characters()  #We don't want the human players fiddling with the chars
            self.do_ai_player_turn()

    @run_async
    def do_ai_player_turn(self):
        all_fitnesses = []
        all_cells = {}

        #Getting fitnesses if needed. This method is redundant, have to check how to get the fitnesses in the ai player method
        for cell in self.cells:
            if cell.has_char():
                start_index = cell.get_real_index()
                all_cells[start_index] = cell.get_char()
                if cell.get_char().owner_uuid == self.current_player.uuid:
                    destinations = cell.get_char().get_paths(self.enabled_paths, self.distances, self.current_map,\
                                    start_index, self.params['circles_per_lvl'])
                    #print("DESTINATIONS FOR "+str(start_index)+" ARE "+str(destinations))
                    fitnesses_thread = self.generate_fitnesses(start_index, destinations)
                    fitnesses_thread.join()
        #print("FINTNESES" +str(self.fitnesses))
        for start_pos, rated_destinies in self.fitnesses.items():
            for dest, score in rated_destinies.items():
                all_fitnesses.append(((start_pos, dest), score))   #Append a tuple ((start, destiny), fitness_eval_of_movm)
        #At this point, we already have the fitnesses of the entire board
        #Simulation of a player driven pick up
        #print("ALL DESTINATIONS ARE "+str(all_fitnesses))

        movement = self.current_player.get_movement(all_fitnesses, self.current_map, self.cells, self.current_player.uuid, [player.uuid for player in self.players])
        print("MOVEMENT CHOSEN WAS "+str(movement))


        character = self.get_cell_by_real_index(movement[0]).get_char()
        self.drag_char.add(character)
        self.last_cell.add(self.get_cell_by_real_index(movement[0]))
        self.active_cell.add(self.get_cell_by_real_index(movement[-1]))
        self.move_character(character)  #In here the turn is advanced one
        if self.show_promotion: #If the update table was triggered
            char_revived = random.choice(self.promotion_table.elements)
            self.swapper.send(char_revived)
        self.drag_char.empty()
        #self.next_char_turn(character)

    def kill_character(self, cell, killer):
        #Badass Animation
        corpse = cell.kill_char()
        self.update_cells(cell)
        self.characters.remove(corpse)  #To delete it from the char list in board. It's dead.
        #Search for it in players to delete it
        for player in self.players:
            if player.has_char(corpse):
                player.remove_char(corpse)
                self.check_player(player)
        self.current_player.add_kill(corpse, killer)
        LOG.log('debug', 'The character ', corpse.id,' was killed!')
        self.play_sound('oof')

    def check_player(self, player):
        if player.has_lost():
            self.characters.remove(player.characters)
            for char in player.characters:
                self.get_cell_by_real_index(char.current_pos).empty_cell()
            if sum(1 for player in self.players if not player.dead) <= 1:  #WE HAVE A WINNER!
                self.win()

    def win(self):
        LOG.log("info", "Winner winner chicken dinner!")
        self.play_sound('win')
        pygame.event.post(self.win_event)
        self.finished = True    #To disregard events except esc and things like that
        self.show_score = True  #To show the infoboard.

    def set_active_cell(self, cell):
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
            #LOG.log('debug', 'New cell active: ', self.active_cell.sprite.pos)
        else:
            if self.drag_char.sprite:
                self.drag_char.sprite.set_hover(False)

    def set_active_path(self, path):
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
        pass
        #TODO KILL THREADS IF STILL LOADING OR DECREASE PLAYER COUNT TO END FASTER, I DUNNO, WHATEVER