"""--------------------------------------------
board module. Contains the entire logic and graphics to build
the game's board.
Have the following classes.
    Board
--------------------------------------------"""

__all__ = ['Board']
__version__ = '0.8'
__author__ = 'David Flaity Pardo'

#Python full fledged libraries
import pygame
import math
import numpy
import os
import random
#Selfmade libraries
from obj.utilities.utility_box import UtilityBox
from pygame.locals import *
from obj.polygons import Circle, Rectangle, Circumference
from obj.utilities.colors import RED, WHITE, DARKGRAY, LIGHTGRAY, TRANSPARENT_GRAY
from obj.screen import Screen, LoadingScreen
from obj.cell import Cell, Quadrant
from obj.utilities.exceptions import BadPlayersParameter, BadPlayerTypeException,\
                        PlayerNameExistsException, TooManyCharactersException
from obj.utilities.decorators import run_async
from obj.players import Player
from obj.paths import Path
from obj.ui_element import TextSprite
from obj.utilities.logger import Logger as LOG
from obj.players import Character, Restriction
from obj.sprite import Sprite

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
    Args:
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
                        'inter_path_frequency'  : 2,
                        'circles_per_lvl'       : 16,
                        'max_levels'            : 4,
                        'center_cell'           : False,
                        'path_color'            : WHITE,
                        'path_width'            : 5,
                        'platform_sprite'       : None
    }
    #CHANGE MAYBE THE THREADS OF CHARACTER TO JOIN INSTEAD OF NUM PLAYERS AND SHIT
    def __init__(self, id_, event_id, end_event_id, resolution, *players, empty=False, **params):
        """Board constructor. Inherits from Screen.
        Args:
            id_ (str):  Identifier of the Screen.
            event_id (int): Identifier of the Screen event.
            resolution (:tuple: int,int):   Size of the Screen. In pixels.
            *players (:obj: Player):    All the players that will play on this board, separated by commas.
            **params (:dict:):  Dict of keywords and values as parameters to create the Screen.
                                platform_proportion, platform_alignment, inter_path_frequency, circles_per_lvl,\
                                max_levels, path_color, path_width.
        """
        super().__init__(id_, event_id, resolution, **params)
        self.turn           = 0
        self.char_turns     = 0
        self.end            = 0     
        #Graphic elements
        self.loading_screen = None  #Created in Board.generate
        self.cells          = pygame.sprite.Group()
        self.quadrants      = {}
        self.possible_dests = pygame.sprite.Group()
        self.inter_paths    = pygame.sprite.GroupSingle()
        self.paths          = pygame.sprite.Group()
        self.characters     = pygame.sprite.OrderedUpdates()
        self.current_player = None  #Created in add_player
        
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
        self.end_event      = pygame.event.Event(end_event_id)
        Board.generate(self, empty, *players)
    
    @staticmethod
    def generate(self, empty, *players):
        UtilityBox.join_dicts(self.params, Board.__default_config)
        #INIT
        axis_size = self.params['circles_per_lvl']*self.params['max_levels']
        if self.params['center_cell']:
            axis_size += 1
        dimensions          = (axis_size, axis_size)
        self.distances      = numpy.full(dimensions, -888, dtype=int)   #Says the distance between cells
        self.enabled_paths  = numpy.zeros(dimensions, dtype=bool)       #Shows if the path exist
        if self.params['loading_screen']:
            self.loading_screen = LoadingScreen(self.id+"_loading", self.event_id, self.resolution, text="Loading, hang tight")
        #REST
        platform_size   = tuple(min(self.resolution)*self.params['platform_proportion'] for _ in self.resolution)
        centered_pos    = tuple(x//2-y//2 for x, y in zip(self.resolution, platform_size))
        
        platform_pos    = (0, centered_pos[1]) if 'left' in self.params['platform_alignment']\
        else centered_pos if 'center' in self.params['platform_alignment']\
        else (self.resolution[0]-platform_size[0], centered_pos[1])

        if not self.params['platform_sprite']:
            self.platform = Rectangle(self.id+"_platform", platform_pos, platform_size, self.resolution)
        else:
            self.platform = self.params['platform_sprite']
        if not empty:
            self.generate_environment()
        self.add_players(*players)

    def generate_environment(self):
        self.generate_all_cells()
        self.assign_quadrants()
        self.generate_paths(offset=True)
        self.generate_inter_paths()
        self.generate_map_board()
        self.save_sprites()        

    def set_scroll(self, value):
        """We dont want scrolls in the board"""
        pass

    def save_sprites(self):
        """Copies all the references of the sprites to the sprites list declared on the superclass.
        Do this to modify all the graphical elements at once when needed in a more seamless manner.
        Also because the super().draw method only draws the self.sprites.
        Only adds the graphics regarding the board, the characters and player addons will be drawn later."""
        self.sprites.add(self.platform, self.inter_paths.sprite, *self.paths.sprites(), *self.cells.sprites())

    def __adjust_number_of_paths(self):
        """Checks the inter path frequency. If the circles are not divisible by that frequency,
        it rounds up the said frequency parameter."""
        circles, paths = self.params['circles_per_lvl'], self.params['inter_path_frequency']
        if circles%paths is not 0:
            self.params['inter_path_frecuency'] = circles//math.ceil(circles/paths) 
            LOG.log('DEBUG', "Changed number of paths from ", paths, " to ", self.params['inter_path_frecuency'])
    
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

    def generate_all_cells(self, custom_cell_radius=None):
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
            radius      += ratio
            if i is 0:  self.cells.add(self.__generate_cells(radius-ratio//3, self.platform.rect.center, small_radius, 4, 0, initial_offset=-45))
            else:       self.cells.add(self.__generate_cells(radius-ratio//3, self.platform.rect.center, small_radius, self.params['circles_per_lvl'], i))
        if self.params['center_cell']:
            self.cells.add(self.__generate_center_cell(small_radius, self.params['circles_per_lvl'], self.params['max_levels']))
        LOG.log('DEBUG', "Generated cells of ", self.id)

    def __generate_center_cell(self, radius, circle_number, lvl_number, **cell_params):
        index = circle_number*lvl_number
        for i in range(0, 4):
            self.enabled_paths[i][index], self.enabled_paths[index][i] = True, True
            self.distances[i][index], self.distances[index][i] = 1, 1
        return Cell((lvl_number-1, circle_number), index, tuple(center-radius for center in self.platform.rect.center), (radius*2, radius*2), self.resolution, **cell_params)

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
            cells.append(Cell((lvl, index), lvl*circle_number+index, position, (circle_radius*2, circle_radius*2), self.resolution, **cell_params))
            index       += 1
            angle       += distance
        return cells

    def generate_paths(self, offset=False):
        """Creates the circumferences themselves. Does this by getting the platform size,
        and dividing it by the number of levels/circumferences of self.params. 
        Args:
            offset (boolean):   True if we don't want the circumferences to be so close to the platform borders."""
        self.paths.empty()
        self.active_path.empty()
        ratio = self.platform.rect.height//self.params['max_levels']
        radius = ratio//2-ratio//6 if offset else ratio//2
        for _ in range (0, self.params['max_levels']): #Lvl circles
            out_circle = Circumference('circular_path', tuple(x-radius for x in self.platform.rect.center),\
                        (radius*2, radius*2), self.resolution, fill_gradient=False, overlay=False,\
                        border_color=self.params['path_color'], border_width=self.params['path_width'])
            self.paths.add(out_circle)
            radius+=ratio//2
        LOG.log('DEBUG', "Generated circular paths in ", self.id)
    
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
        self.inter_paths.add(interpaths_sprite)

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
            self.current_map[cell.get_real_index()]=cell.to_path(self.current_player.name)
        LOG.log('DEBUG', "Generated the map of paths for ", self.current_player.name)
    
    def update_cells(self, *cells):
        for cell in cells:
            self.current_map[cell.get_real_index()]=cell.to_path(self.current_player.name)

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
        for sprite in self.sprites: #Updateing the bezier curves.
            if 'inter' in sprite.id and 'path' in sprite.id:
                sprite = self.inter_paths.sprite
                break

    def ALL_PLAYERS_LOADED(self):
        """Returns:
            (boolean): True if all the requested players have been loaded already."""
        if not self.started and (self.loaded_players is self.total_players):
            self.play_sound('success')
            if not self.current_player: #If this is the first player added
                self.current_player = self.players[0]
                self.current_player.unpause_characters()
                self.update_map()       #This goes according to current_player
            self.started = True

    def create_player(self, name, number, chars_size, **player_settings):
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
        if sum(x['ammount'] for x in player_settings.values()) > len(self.quadrants[0].cells):
            raise TooManyCharactersException('There are too many characters in player for a quadrant.')
        self.__create_player(name, number, chars_size, **player_settings)
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
                LOG.log('DEBUG', "Character ", character.id, " spawned with position ", cell.pos)
            player.pause_characters()
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
    def __create_player(self, player_name, player_number, chars_size, **player_params):
        """Asynchronous method (@run_async decorator). Creates a player with the the arguments and adds him to the board.
        Args:
            player_name (str):  Identifier of the player
            player_number (int):Number assignated by arriving order. Will assign a quadrant too.
            chars_size (:tuple: int, int):  Size of the image of the characters. In pixels.
            **player_params (:dict:):   Contains the more specific parameters to create the player.
                                        Ammount of each type of char, name of their actions, and their folder paths.
        Returns:
            (:obj:Threading.thread):    The thread doing the work. It is returned by the decorator."""
        player = Player(player_name, player_number, chars_size, self.resolution, **player_params)
        self.__add_player(player)

    def draw(self, surface):
        """Draws the board and all of its elements on the surface.
        Blits them all and then updates the display.
        Args:
            surface (:obj: pygame.Surface): Surface to draw the board.
        """
        if not self.started and self.params['loading_screen']:
            self.loading_screen.draw(surface)
            return
        super().draw(surface)                                                                           #Draws background
        for dest in self.possible_dests:
            pygame.draw.circle(surface, WHITE, dest.center, dest.radius)
        for char in self.characters:
            char.draw(surface)
        if self.current_player:
            self.current_player.draw(surface)   #This draws the player's infoboard
            
        
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
        if self.started:
            if event.type == pygame.KEYDOWN:    self.keyboard_handler(keys_pressed)
            else:                               self.mouse_handler(event, mouse_movement, mouse_pos)  

    def pickup_character(self):
        """Picks up a character. Adds it to the drag char Group, and check in the LUT table
        the movements that are possible taking into account the character restrictions.
        Then it draws an overlay on the possible destinations."""
        LOG.log('INFO', 'Selected ', self.active_char.sprite.id)
        self.drag_char.add(self.active_char.sprite)
        self.drag_char.sprite.set_selected(True)
        self.last_cell.add(self.active_cell.sprite)
        destinations = self.drag_char.sprite.get_paths( self.enabled_paths, self.distances, self.current_map,\
                                                        self.active_cell.sprite.index, self.params['circles_per_lvl'])
        for cell_index in destinations:
            self.possible_dests.add(self.get_cell_by_real_index(cell_index[-1]))

    def drop_character(self):
        """Drops a character. Deletes it from the drag char Group, and checks if the place in which
        has been dropped is a possible destination. If it is, it drops the character in that cell.
        Otherwise, the character will be returned to the last Cell it was in."""
        LOG.log('INFO', 'Dropped ', self.drag_char.sprite.id)
        self.drag_char.sprite.set_selected(False)
        self.drag_char.sprite.set_hover(False)
        if self.possible_dests.has(self.active_cell.sprite):
            self.move_character(self.drag_char.sprite)
            self.next_char_turn(self.drag_char.sprite)
        else:
            self.drag_char.sprite.rect.center = self.last_cell.sprite.center
            self.play_sound('warning')
            LOG.log('debug', 'Cant move the char there')
        self.drag_char.empty()
        self.possible_dests.empty()

    def move_character(self, character):
        LOG.log('debug', 'The chosen cell is possible, moving')
        active_cell = self.active_cell.sprite
        self.last_cell.sprite.empty_cell() #Emptying to delete the active char from there
        character.set_cell(active_cell)  #Positioning the char
        if not active_cell.is_empty():
            self.kill_character(active_cell) #Killing char if there is one 
        active_cell.add_char(character)
        self.current_player.register_movement(character)
        self.update_cells(self.last_cell.sprite, active_cell)
        self.last_cell.empty()  #Not last cell anymore, char was droppped succesfully
        
    def next_char_turn(self, char):
        self.char_turns += 1
        if self.char_turns >= char.turns:
            self.char_turns = 0
            self.next_player_turn()
        elif self.char_turns < char.turns and self.char_turns == 1:
            self.current_player.pause_characters()
            char.set_state('idle')
            char.active = True  #Only can move this one afterwards

    def next_player_turn(self):
        self.current_player.turn += 1
        while True:
            self.player_index += 1
            if self.player_index >= len(self.players):
                self.player_index = 0
                self.turn += 1
            if self.players[self.player_index].turn is self.turn:
                self.current_player.pause_characters()
                self.current_player = self.players[self.player_index]
                self.current_player.unpause_characters()
                self.update_map()
                break

    def kill_character(self, cell):
        #Badass Animation
        corpse = cell.kill_char()
        self.update_cells(cell)
        self.characters.remove(corpse)  #To delete it from the char list in board. It's dead.
        #Search for it in players to delete it :)
        for player in self.players:
            if player.has_char(corpse):
                player.remove_char(corpse)
                self.check_player(player)
        self.current_player.add_kill(corpse, self.drag_char.sprite)
        LOG.log('debug', 'The character ', corpse.id,' was killed!')
        self.play_sound('oof')

    def check_player(self, player):
        if player.has_lost():
            self.players.remove(player)
            self.characters.remove(player.characters)
            for char in player.characters:
                self.get_cell_by_real_index(char.current_pos).empty_cell()
            if len(self.players) == 1:  #WE HAVE A WINNER!
                self.play_sound('win')
                self.win()

    def win(self):
        pygame.event.post(self.end_event)

    def keyboard_handler(self, keys_pressed):
        """Handles any pygame keyboard related event. This allows for user interaction with the object.
        Posibilities:
        TODO
        Args:
            keys_pressed (:dict: pygame.keys):  Dict in which the keys are keys and the items booleans.
                                                Said booleans will be True if that specific key was pressed.
        """
        self.play_sound('key')
        if keys_pressed[pygame.K_DOWN]:         LOG.log('DEBUG', "down arrow in board")
        if keys_pressed[pygame.K_UP]:           LOG.log('DEBUG', "up arrow in board")
        if keys_pressed[pygame.K_LEFT]:         LOG.log('DEBUG', "left arrow in board")
        if keys_pressed[pygame.K_RIGHT]:        LOG.log('DEBUG', "right arrow in board")
        if keys_pressed[pygame.K_KP_ENTER]\
            or keys_pressed[pygame.K_SPACE]:    LOG.log('DEBUG', "space/enter")

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
            self.active_cell.add(cell)
            char = self.active_cell.sprite.has_char()
            if char and char.active:
                self.active_char.add(char)
            LOG.log('debug', 'New cell active: ', self.active_cell.sprite.pos)

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

    #Does all the shit related to the mouse hovering an option
    def mouse_handler(self, event, mouse_movement, mouse_position):
        """Handles any mouse related pygame event. This allows for user interaction with the object.
        Posibilities:
        TODO
        Args:
            event (:obj: pygame.event): Event received from the pygame queue.
            mouse_movement( boolean, default=False):    True if there was mouse movement since the last call.
            mouse_position (:tuple: int, int, default=(0,0)):   Current mouse position. In pixels.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:  #On top of the char and clicking on it
            self.play_sound('key')
            if self.active_char.sprite: self.pickup_character()
        elif event.type == pygame.MOUSEBUTTONUP:  #If we are dragging it we will have a char in here
            if self.drag_char.sprite:   self.drop_character()
        if self.drag_char.sprite:   
            self.drag_char.sprite.rect.center = mouse_position

        if mouse_movement:
            mouse_sprite = UtilityBox.get_mouse_sprite()
            
            #Checking collision with cells
            collided_cell = pygame.sprite.spritecollideany(mouse_sprite, self.cells, collided=pygame.sprite.collide_circle)
            self.set_active_cell(collided_cell)

            #Checking collision with paths
            path = pygame.sprite.spritecollideany(mouse_sprite, self.paths, collided=pygame.sprite.collide_mask)
            self.set_active_path(path)