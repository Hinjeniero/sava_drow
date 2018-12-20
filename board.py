import pygame, math, numpy, os, random
from utility_box import UtilityBox
from pygame.locals import *
import gradients #Gradients in polygons
import ptext #Gradients in text
from polygons import *
from colors import *
from screen import Screen, LoadingScreen
from cell import Cell, Quadrant
from exceptions import BadPlayersParameter, BadPlayerTypeException, PlayerNameExistsException
from decorators import run_async
from players import Player
from paths import IMG_FOLDER, Path
from ui_element import TextSprite
from logger import Logger as LOG
from sprite import Sprite
#numpy.set_printoptions(threshold=numpy.nan)
from players import Character, Restrictions

class Board(Screen):
    __default_config = {'platform_proportion': 0.95,
                        'platform_alignment': "center",
                        'inter_path_frequency': 2, #every 4, every 2, every 1...
                        'circles_per_lvl':  16,
                        'max_levels':       4,
                        'path_color': WHITE,
                        'path_width': 5
    }
    #CHANGE MAYBE THE THREADS OF CHARACTER TO JOIN INSTEAD OF NUM PLAYERS AND SHIT
    def __init__(self, id_, event_id, resolution, *players, **params):
        #Basic info saved
        super().__init__(id_, event_id, resolution, **params)
        self.turn           = -1
        UtilityBox.join_dicts(self.params, Board.__default_config)
        
        #Graphic elements
        self.loading        = LoadingScreen(id_, event_id, resolution, "Loading, hang tight like a japanese pussy",\
                            background_path=IMG_FOLDER+"//loading_background.png")
        self.cells          = pygame.sprite.Group()
        self.quadrants      = {}

        self.possible_paths = pygame.sprite.Group() #To save cells that are destinations of the character
        self.inter_paths    = pygame.sprite.GroupSingle()
        self.paths          = pygame.sprite.Group()
        self.characters     = pygame.sprite.OrderedUpdates()
        self.active_cell    = pygame.sprite.GroupSingle()
        self.active_path    = pygame.sprite.GroupSingle()
        self.active_char    = pygame.sprite.GroupSingle()
        self.drag_char      = pygame.sprite.GroupSingle()
        self.platform       = None
        self.temp_infoboard=None
        
        #Paths and maping
        dimensions          = (self.params['circles_per_lvl']*self.params['max_levels'], self.params['circles_per_lvl']*self.params['max_levels'])
        self.distances      = numpy.full(dimensions, -888, dtype=int)   #Says the distance between cells
        self.enabled_paths  = numpy.zeros(dimensions, dtype=bool)       #Shows if the path exist
        self.current_map    = {}
        self.changed_cells  = ["platano"] #Simply coordinates (indexes)
        
        #Players 
        self.total_players  = 0
        self.loaded_players = 0
        self.players        = []
        self.player_index   = 0
        self.add_players(*players)
        
        #Final of all
        self.generate()
        self.map_board()
    
    def __add_player(self, player):
        if isinstance(player, Player): 
            self.players.append(player)
            for character in player.characters: 
                character.set_size(self.cells.sprites()[0].rect.size)
                c = self.quadrants[player.order].get_random_cell()
                c.add_char(character)
                character.rect.center = c.rect.center
                self.characters.add(character)
                LOG.log('DEBUG', "Character ", character.id, " spawned with position ", c.pos)
            self.loaded_players += 1
            return 0
        raise BadPlayerTypeException("A player in the board can't be of type "+str(type(player)))

    def __adjust_number_of_paths(self):
        circles, paths = self.params['circles_per_lvl'], self.params['inter_path_frequency']
        if circles%paths is not 0:
            self.params['inter_path_frecuency'] = circles//math.ceil(circles/paths) 
            LOG.log('DEBUG', "Changed number of paths from ", paths, " to ", self.params['inter_path_frecuency'])
    
    def assign_quadrants(self, container_center, *cells):
        quadrants = {}
        for cell in cells:
            if cell.get_level() < 1: continue   #We are not interested in this cell, next one
            quads = self.__get_quadrant(cell.get_index())
            for quadrant in quads:
                try:                quadrants[quadrant].append(cell)
                except KeyError:    quadrants[quadrant] = [cell]
        for quadrant_number, quadrant_cells in quadrants.items():
            #LOG.log('debug', quadrant_number, ": ", quadrant_cells)
            self.quadrants[quadrant_number] = Quadrant(quadrant_number, *quadrant_cells)

    def __get_quadrant(self, cell_index):
        ratio = self.params['circles_per_lvl']//4
        result, rest = (cell_index+ratio//2)//ratio,  (cell_index+ratio//2)%ratio
        if result >= 4:                 #We gone beyond the last quadrant boi, circular shape ftw
            if rest is 0:   return 3, 0 #Last and first quadrant, it's that shared cell
            else:           return 0,    #Associated with first quadrant
        if rest is 0 and result is not 0: return result, result-1
        return result,
    
    @run_async
    def __create_player(self, player_name, player_number, chars_number, chars_size, **player_params):
        self.__add_player(Player(player_name, player_number, chars_number, chars_size, self.resolution, **player_params))

    def __current_player(self):
        return self.players[self.player_index]
    
    def __generate_cells(self, radius, center, circle_radius, circle_number, lvl, initial_offset=-90, **cell_params):
        #TODO could pass params in this function if we want coloured circles
        cells = []
        two_pi  = 2*math.pi
        initial_offset = initial_offset*(math.pi/180) if abs(initial_offset) > two_pi\
        else initial_offset%360*(math.pi/180) if abs(initial_offset) > 360 else initial_offset
        angle   = initial_offset*(math.pi/180) if initial_offset > two_pi else initial_offset
        distance= two_pi/circle_number
        index   = 0
        while angle < (two_pi+initial_offset):
            position    = (center[0]+(radius*math.cos(angle))-circle_radius, center[1]+(radius*math.sin(angle))-circle_radius)
            cell_sprite = Circle(str(lvl)+"_"+str(index), position, (circle_radius*2, circle_radius*2), self.resolution, **cell_params)
            cells.append(Cell(cell_sprite, (lvl, index), lvl*circle_number+index))
            index       += 1
            angle       += distance
        return cells

    def map_board(self): #From the action of mapping something
        self.__map_enabled_paths()
        self.__map_distances()
    
    def __map_enabled_paths(self):
        lvls, circles = self.params['max_levels'], self.params['circles_per_lvl'], 
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
                        print("ENABLING PATH FROM "+str(y)+" TO "+str(y+circles))
                        self.enabled_paths[y][y+circles], self.enabled_paths[y+circles][y] = True, True

            #No more special conditions, normal cells
            if (x+1)%circles is 0:                  #last circle of this lvl, connect with first one:
                self.enabled_paths[x][(x-circles)+1], self.enabled_paths[(x-circles)+1][x] = True, True
            else:                                   #Connect with next circle
                self.enabled_paths[x][x+1], self.enabled_paths[x+1][x] = True, True
        LOG.log('DEBUG', "Paths of this map: \n", self.enabled_paths)       

    def __map_distances(self):
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
        ratio = self.params['circles_per_lvl']//4
        return (index%self.params['circles_per_lvl'])//ratio if (index+1)%self.params['inter_path_frequency'] is 0 else None
        
    #Doesnt work propperly
    def __get_outside_cells(self, index):
        cells=[]
        space_between_inter_paths = int((self.params['circles_per_lvl']//4)*(1/self.params['inter_path_frequency']))
        print("SPACE "+str(space_between_inter_paths))
        i = (self.params['circles_per_lvl']//4)-1
        for _ in range(0, (self.params['circles_per_lvl']//4)//self.params['inter_path_frequency']):
            cells.append(i+index*(self.params['circles_per_lvl']//4))
            i -= space_between_inter_paths
        return tuple(cells)

    def __update_map(self): #TODO wwe have to use only changed cells to update, right now doing everything
        self.current_map.clear()
        self.changed_cells.clear()
        for cell in self.cells.sprites():   #They are already ordered
            self.current_map[cell.index] = cell.to_path("Yes") #TODO change this shit
        #for key, path in self.current_map.items():
            #LOG.log('DEBUG', "Dictionary ", key," -> Cell ", path.pos, " with real index ", path.index, " have a path object ", path)

    def drop_char(self):
        pass

    def generate(self):
        platform_size   = tuple(min(self.resolution)*self.params['platform_proportion'] for _ in self.resolution)
        centered_pos    = tuple(x//2-y//2 for x, y in zip(self.resolution, platform_size))
        platform_pos    = (0, centered_pos[1]) if 'left' in self.params['platform_alignment']\
        else centered_pos if 'center' in self.params['platform_alignment']\
        else (self.resolution[0]-platform_size[0], centered_pos[1])
        self.platform   = Rectangle(self.id+"_platform", platform_pos, platform_size, self.resolution)
        self.generate_all_cells()
        self.assign_quadrants(self.platform.rect.center, *self.cells)
        self.generate_paths(offset=True)
        self.generate_inter_paths()

    def generate_all_cells(self, custom_radius=None):
        self.cells.empty()
        self.active_cell.empty()
        ratio       = self.platform.rect.height//(2*self.params['max_levels'])
        radius      = 0
        small_radius= ratio//4 if custom_radius is None else custom_radius
        cell_sprite = Circle('cell', tuple(x-small_radius for x in self.platform.rect.center),\
                    (small_radius*2, small_radius*2), self.resolution)
        cell        = Cell(cell_sprite, (-1, 0), -1)
        self.cells.add(cell)
        for i in range (0, self.params['max_levels']):
            radius      += ratio
            if i is 0:  self.cells.add(self.__generate_cells(radius-ratio//3, self.platform.rect.center, small_radius, 4, 0, initial_offset=-45))
            else:       self.cells.add(self.__generate_cells(radius-ratio//3, self.platform.rect.center, small_radius, self.params['circles_per_lvl'], i))
        LOG.log('DEBUG', "Generated cells of ", self.id)

    def generate_paths(self, offset=False): #BIG PATH CIRCLES
        self.paths.empty()
        self.active_path.empty()
        ratio = self.platform.rect.height//self.params['max_levels']
        radius = ratio//2-ratio//6 if offset else ratio//2
        for _ in range (0, self.params['max_levels']): #Lvl circles
            out_circle = Circle('circular_path', tuple(x-radius for x in self.platform.rect.center),\
                        (radius*2, radius*2), self.resolution, fill_gradient=False,\
                        border_color=self.params['path_color'], border_width=self.params['path_width'], transparent=True)
            self.paths.add(out_circle)
            radius+=ratio//2
        LOG.log('DEBUG', "Generated circular paths in ", self.id)
    
    def generate_inter_paths(self):
        self.inter_paths.empty()
        surface = pygame.Surface(self.resolution)
        UtilityBox.add_transparency(surface, self.params['path_color'])
        self.__adjust_number_of_paths()
        for i in range(0, self.params['circles_per_lvl']):
            if (i+1)%self.params['inter_path_frequency'] is 0:
                self.draw_inter_path(surface, i)

        surface = surface.subsurface(self.platform.rect)
        interpaths_sprite = Sprite('inter_paths', self.platform.rect.topleft, surface.get_size(), self.resolution, surface=surface)
        self.inter_paths.add(interpaths_sprite)

    def draw_inter_path(self, surface, index):
        point_list = []
        for i in range(self.params['max_levels']-1, 0, -1):
            point_list.append(self.get_cell(i, index).center)
        point_list.append(self.get_cell(0, self.__get_inside_cell(index)).center) #Final point
        UtilityBox.draw_bezier(surface, color=self.params['path_color'], width=self.params['path_width'], *(tuple(point_list)))

    def get_cell(self, lvl, index):
        for cell in self.cells:
            #LOG.log('debug', 'CHECKING CELL', cell.get_level(),",",cell.get_index())
            if lvl is cell.get_level() and index is cell.get_index():
                return cell
            else:
                pass
                #LOG.log('debug', 'CELL', cell.get_level(),", ",cell.get_index(), ' is not the searched one ', lvl,', ', index)
        return False

    def generate_map(self, to_who):
        paths = []
        for cell in self.cells: paths.append(cell.to_path(to_who))
        paths.sort()
        LOG.log('DEBUG', "Generated the map of paths in ", self.id)
        return paths

    def set_resolution(self, resolution):
        super().set_resolution(resolution)
        self.loading.set_resolution(resolution)
        self.generate()          #This goes according to self.resolution, so everything is fine.

    def ALL_PLAYERS_LOADED(self):
        return self.loaded_players is self.total_players

    def create_player(self, name, number, chars_size, **player_settings):
        self.total_players          += 1
        for player in self.players:
            if name == player.name: raise PlayerNameExistsException("The player name "+name+" already exists")
        self.__create_player(name, number, chars_size, **player_settings)
        LOG.log('DEBUG', "Queue'd player to load, total players ", self.total_players, " already loaded ", self.loaded_players)

    def add_players(self, *players):
        if not isinstance(players, (tuple, list)):    raise BadPlayersParameter("The list of players to add can't be of type "+str(type(players)))
        for player in players:  self.__add_player(player)

    def draw(self, surface, hitboxes=False):
        if self.ALL_PLAYERS_LOADED():
            if len(self.changed_cells) > 0:     self.__update_map() #TODO do this in another method, ni mouse handler would be good
            super().draw(surface)                                                                           #Draws background
            surface.blit(self.platform.image, self.platform.rect)                                           #Draws board
            self.inter_paths.draw(surface) 
            self.paths.draw(surface)                                                                        #Draws paths between cells

            active_path = self.active_path.sprite
            if active_path is not None: 
                pygame.draw.circle(surface, RED, active_path.rect.center, active_path.radius, 4)            #Draw active path
            self.cells.draw(surface)                                                                        #Draws cells    
            
            active_sprite = self.active_cell.sprite
            if active_sprite is not None: 
                pygame.draw.circle(surface, UtilityBox.random_rgb_color(), active_sprite.rect.center, active_sprite.rect.height//2) #Draws an overlay on the active cell
            self.characters.update()
            self.characters.draw(surface)
            #for char in self.characters: UtilityBox.draw_hitbox(surface, char) #TODO TESTING
            if hitboxes:    UtilityBox.draw_hitboxes(surface, self.cells.sprites())
        else:
            self.loading.draw(surface)
        self.temp_infoboard.draw(surface)
        pygame.display.update()
        
    def event_handler(self, event, keys_pressed, mouse_buttons_pressed, mouse_movement=False, mouse_pos=(0, 0)):
        if self.ALL_PLAYERS_LOADED():
            if event.type == pygame.KEYDOWN:    self.keyboard_handler(keys_pressed)
            else:                               self.mouse_handler(event, mouse_buttons_pressed, mouse_movement, mouse_pos)  

    #Does all the shit related to the mouse hovering an option
    def mouse_handler(self, event, mouse_buttons, mouse_movement, mouse_position):
        mouse_sprite = UtilityBox.get_mouse_sprite(mouse_position)
        
        if event.type == pygame.MOUSEBUTTONDOWN:  #On top of the char and clicking on it
            if self.active_char.sprite is not None:
                LOG.log('INFO', 'Selected ', self.active_char.sprite.id)
                self.drag_char.add(self.active_char.sprite)
                self.drag_char.sprite.set_selected(True)
                #TODO BIG SHIT HERE, THIS IT A BETA METHOD. ASSIGN TO SOMETHING FUCK
                self.drag_char.sprite.generate_paths(self.enabled_paths, self.current_map, self.distances, self.active_cell.sprite.to_path("YES")) 
                #TODO Change name of who asking
        elif event.type == pygame.MOUSEBUTTONUP:  #If we are dragging it we will have a char in here
            if self.drag_char.sprite is not None:
                LOG.log('INFO', 'Dropped ', self.drag_char.sprite.id)
                self.drag_char.sprite.set_selected(False)
                self.drag_char.sprite.rect.center = self.active_cell.sprite.center 
                self.drag_char.empty()    
        if self.drag_char.sprite is not None:   self.drag_char.sprite.rect.center = mouse_position

        if mouse_movement:
            cell = pygame.sprite.spritecollideany(mouse_sprite, self.cells.sprites(), collided=pygame.sprite.collide_circle)
            if cell is not None and not self.active_cell.has(cell):  
                self.active_cell.add(cell)
                LOG.log('debug', 'hovering cell ', self.active_cell.sprite.pos)
            
            path = pygame.sprite.spritecollideany(mouse_sprite, self.paths.sprites(), collided=pygame.sprite.collide_mask)
            if path is not None:    self.active_path.add(path)

            char = pygame.sprite.spritecollideany(mouse_sprite, self.__current_player().characters.sprites(), collided=pygame.sprite.collide_mask)
            if char is not None:    
                char.set_hover(True)
                self.active_char.add(char)
            else:                   
                if self.active_char.sprite is not None:
                    self.active_char.sprite.set_hover(False)
                    self.active_char.empty()

    #TODO KEYBOARD DOES NOT CHANGE ACTIVE CELL, BUT ACTIVE CHARACTER. ACTIVE CELL CHANGE ONLY BY MOUSE
    def keyboard_handler(self, keys_pressed):
        if keys_pressed[pygame.K_DOWN]:         LOG.log('DEBUG', "down arrow in board")
        if keys_pressed[pygame.K_UP]:           LOG.log('DEBUG', "up arrow in board")
        if keys_pressed[pygame.K_LEFT]:         LOG.log('DEBUG', "left arrow in board")
        if keys_pressed[pygame.K_RIGHT]:        LOG.log('DEBUG', "right arrow in board")
        if keys_pressed[pygame.K_KP_ENTER]\
            or keys_pressed[pygame.K_SPACE]:    LOG.log('DEBUG', "space/enter")

#List of (ids, text)
if __name__ == "__main__":
    #Variables
    resolution = (1024, 1024)
    pygame.init()
    screen = pygame.display.set_mode(resolution)
    pygame.mouse.set_visible(True)
    clock = pygame.time.Clock()
    timeout = 20
    #Create Board
    game = Board("testboard", pygame.USEREVENT, resolution)    
    #Start the test
    loop = True
    while loop:
        clock.tick(144)
        game.draw(screen, clock=clock)       #Drawing the sprite group
        for event in pygame.event.get():
            if event.type == pygame.QUIT:       loop = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:    loop = False
            elif event.type >= pygame.USEREVENT:
                print("Received event number "+str(event.type)+", with value "+str(event.value))
            if loop:            #If not exit yet                        
                game.event_handler(event, pygame.key.get_pressed(), pygame.mouse.get_pressed(),\
                                    mouse_movement=(pygame.mouse.get_rel() != (0,0)), mouse_pos=pygame.mouse.get_pos())