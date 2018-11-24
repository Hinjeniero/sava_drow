import pygame, math, numpy, os, random, functools
from utility_box import UtilityBox
from pygame.locals import *
import gradients #Gradients in polygons
import ptext #Gradients in text
from polygons import *
from colors import *
from screen import Screen 
from exceptions import BadPlayersParameter, BadPlayerTypeException, PlayerNameExistsException
from decorators import run_async
from players import Player
from paths import IMG_FOLDER, Path
from ui_element import TextSprite
from logger import Logger as LOG
POSITION_CHAR = (10, 10)

@functools.total_ordering
class Cell(pygame.sprite.Sprite):
    def __init__(self, circle, grid_position):
        super().__init__()
        self.image  = circle.image
        self.rect   = circle.rect
        self.center = circle.center
        self.pos    = grid_position
        self.chars  = pygame.sprite.Group

    def get_level(self):
        return self.pos[0]
    
    def get_index(self):
        return self.pos[1]

    def has_enemy(self, who_asking):
        for character in self.chars:
            if character.get_master() != who_asking: return True
        return False

    def has_ally(self, who_asking):
        for character in self.chars:
            if character.get_master() == who_asking: return True
        return False

    def to_path(self, who_asking):
        return Path(self.pos, self.has_enemy(who_asking), self.has_ally(who_asking))
    
    def __lt__(self, cell):
        return self.pos[0]<cell.pos[0] if self.pos[0] != cell.pos[0] else self.pos[1]<cell.pos[1]

    def __le__(self, cell):
        return True if self.pos[0]<cell.pos[0] else True if self.pos[1]<cell.pos[1] else self.__eq__(cell)

    def __gt__(self, cell):
        return self.pos[0]>cell.pos[0] if self.pos[0] != cell.pos[0] else self.pos[1]>cell.pos[1]
    
    def __ge__(self, cell):
        return True if self.pos[0]>cell.pos[0] else True if self.pos[1]>cell.pos[1] else self.__eq__(cell)
    
    def __eq__(self, cell):
        return all(mine == his for mine, his in zip (self.pos, cell.pos))

    def __hash__(self):
        return hash(self.pos)

class LoadingScreen(Screen):
    def __init__(self, id_, event_id, resolution, text, loading_sprite = None, **params):
        super().__init__(id_, event_id, resolution, **params)
        self.full_sprite    = self.generate_load_sprite(loading_sprite)
        self.loading_sprite = self.copy_sprite(0, *self.full_sprite)
        self.real_rect_sprt = (tuple(x//y for x, y in zip(self.loading_sprite[0].rect.size, self.resolution)),\
                            tuple(x//y for x, y in zip(self.loading_sprite[0].rect.topleft, self.resolution)))
        self.index_sprite   = 0

        self.text_sprite    = TextSprite(self.id, (int(0.6*self.resolution[0]), int(0.1*self.resolution[1])), text=text)
        self.text_sprite.set_position(self.resolution, 0)
        self.count          = 0
    
    def generate_load_sprite(self, path, degrees=45):
        sprite = pygame.sprite.Sprite()
        sprite.image        = pygame.image.load(IMG_FOLDER+"//loading_circle.png") if path is None else pygame.image.load(path)
        sprite.rect         = sprite.image.get_rect()
        sprite.rect.topleft = (self.resolution[0]//2-sprite.rect.width//2, self.resolution[1]-sprite.rect.height*1.5)
        return UtilityBox.rotate(sprite, 360//8, 8)
    
    def update(self):
        if self.count is 100:
            self.index_sprite = 0 if self.index_sprite is (len(self.loading_sprite)-1) else self.index_sprite+1
            self.count = 0
        else: self.count+=1

    def draw(self, surface):
        super().draw(surface)
        surface.blit(self.loading_sprite[self.index_sprite].image, self.loading_sprite[self.index_sprite].rect)
        surface.blit(self.text_sprite.image, self.text_sprite.rect)
        self.update()

    def copy_sprite(self, new_size, *sprite_list):
        sprites_copy = []
        for sprite in sprite_list:
            spr = pygame.sprite.Sprite()
            spr.image, spr.rect = sprite.image.copy(), sprite.rect.copy()
            sprites_copy.append(spr)
        return sprites_copy

    def update_resolution(self, resolution):
        super().update_resolution(resolution)
        #for sprite in self.loading_sprite:
            #sprite.image = pygame.transform.smoot

class Board(Screen):
    __default_config = {'circles_per_lvl':  16,
                        'max_levels':       4,
                        'number_of_paths':  8
    }

    def __init__(self, id_, event_id, resolution, *players, **params):
        #Basic info saved
        super().__init__(id_, event_id, resolution, **params)
        self.turn           = -1
        UtilityBox.check_missing_keys_in_dict(self.params, Board.__default_config)
        #Graphic elements
        self.loading        = LoadingScreen(id_, event_id, resolution, "Loading, hang tight like a japanese pussy", background_path=IMG_FOLDER+"//loading_background.png")
        
        self.cells          = pygame.sprite.Group()
        self.quadrants      = {-1: [], #AXISES, COULD BE UNUSED
                                0: [],
                                1: [],
                                2: [],
                                3: []
        }

        self.trans_paths    = pygame.sprite.Group() #TODO Did you just assume my type?
        self.paths          = pygame.sprite.Group()
        self.characters     = pygame.sprite.OrderedUpdates()
        self.active_cell    = pygame.sprite.GroupSingle()
        self.active_path    = pygame.sprite.GroupSingle()
        self.active_char    = pygame.sprite.GroupSingle()
        self.drag_char      = pygame.sprite.GroupSingle()
        self.platform       = None
        #Paths and maping
        dimensions          = (self.params['circles_per_lvl']*self.params['max_levels'], self.params['circles_per_lvl']*self.params['max_levels'])
        self.map            = numpy.zeros(dimensions, dtype=int)        #Contains characters
        self.distances      = numpy.zeros(dimensions, dtype=int)        #Says the distance between cells
        self.enabled_paths  = numpy.zeros(dimensions, dtype=bool)       #Shows if the path exist
        self.current_map    = []
        #Players 
        self.total_players  = 0
        self.loaded_players = 0
        self.players        = []
        self.player_index   = 0
        self.add_players(*players)
        #Final of all
        self.generate()

    def __current_player(self):
        return self.players[self.player_index]

    def generate(self):
        self.platform       = Rectangle((int(self.resolution[0]*0.025), int(self.resolution[1]*0.025)), (int(self.resolution[1]*0.95), int(self.resolution[1]*0.95)))
        self.generate_all_cells()
        self.generate_paths(offset=True)

    def generate_all_cells(self, custom_radius=None):
        self.cells.empty()
        self.active_cell.empty()
        ratio   = self.platform.rect.height//(2*self.params['max_levels'])
        radius  = 0
        small_radius = ratio//4 if custom_radius is None else custom_radius
        cell = Cell(Circle(tuple(x-small_radius for x in self.platform.rect.center), (small_radius*2, small_radius*2)), (0, -1))
        self.cells.add(cell)
        for i in range (0, self.params['max_levels']):
            radius      += ratio
            if i is 0:  self.cells.add(self.__generate_cells(radius-ratio//3, self.platform.rect.center, small_radius, 4, 0, initial_offset=0.25*math.pi))
            else:       self.cells.add(self.__generate_cells(radius-ratio//3, self.platform.rect.center, small_radius, self.params['circles_per_lvl'], i))
        for cell in self.cells.sprites():
            if cell.get_level() is not 0:  self.__assign_quadrant(cell, self.platform.rect.center)  
            #self.quadrants[cell.get_index()//(self.params['circles_per_lvl']//4)].append(cell)
    
    def __assign_quadrant(self, cell, container_center, count_axis=False):
        x, y = cell.rect.center[0], cell.rect.center[1]
        center_x, center_y = container_center[0], container_center[1]
        if 0 < abs(x - center_x) < 2: x = center_x
        if 0 < abs(y - center_y) < 2: y = center_y
        if not count_axis:  quadrant = 0 if (x>=center_x and y<center_y) else 1 if (x>center_x and y>=center_y)\
                            else 2 if (x<=center_x and y>center_y) else 3
        else:               quadrant = 0 if (x>center_x and y<center_y) else 1 if (x>center_x and y>center_y)\
                             else 2 if (x<center_x and y>center_y) else 3 if (x<center_x and y<center_y) else -1
        
        LOG.log('DEBUG', "x, y => " , x, ", ", y, ", center => ", center_x, ", ", center_y,\
        ", quadrant => ", quadrant, ", cell => ", cell.get_level(), ", ", cell.get_index())
        #TODO use logger hjere
        self.quadrants[quadrant].append(cell)

    #TODO could pass params in this function if we want coloured circles
    def __generate_cells(self, radius, center, circle_radius, circle_number, lvl, initial_offset=0):
        cells = []
        two_pi  = 2*math.pi    
        angle   = initial_offset*(math.pi/180) if initial_offset > two_pi else initial_offset
        distance= two_pi/circle_number
        index=0
        while angle < two_pi:
            position    = (center[0]+(radius*math.cos(angle))-circle_radius, center[1]+(radius*math.sin(angle))-circle_radius) 
            cells.append(Cell(Circle(position, (circle_radius*2, circle_radius*2)), (lvl, index)))
            index       += 1
            angle       += distance
        return cells

    def generate_paths(self, offset=False):
        self.paths.empty()
        self.active_path.empty()
        ratio = self.platform.rect.width//self.params['max_levels']
        radius = ratio//2-ratio//6 if offset else ratio//2
        for _ in range (0, self.params['max_levels']): #Lvl circles
            colorkey = (0, 0, 0)
            out_circle = Circle((self.platform.rect.centerx-radius, self.platform.rect.centery-radius),(radius*2, radius*2), surf_color=colorkey, border_size=3, use_gradient=False)
            out_circle.image.set_colorkey(colorkey)
            out_circle.update_mask()
            self.paths.add(out_circle)
            radius+=ratio//2

        self.__adjust_number_of_paths()
        spr = Rectangle((self.platform.rect.centerx-self.platform.rect.width//2, self.platform.rect.centery), (self.platform.rect.width, 4))
        self.trans_paths.add(*UtilityBox.rotate(spr, 360//self.params['number_of_paths'], self.params['number_of_paths']))

    def __adjust_number_of_paths(self):
        if self.params['circles_per_lvl']%self.params['number_of_paths'] is not 0:
            self.params['number_of_paths'] = self.params['circles_per_lvl']//math.ceil(self.params['circles_per_lvl']/self.params['number_of_paths']) 

    def generate_map(self, to_who):
        paths = []
        for cell in self.cells: paths.append(cell.to_path(to_who))
        paths.sort()
        return paths

    def update_resolution(self, resolution):
        super().update_resolution(resolution)
        self.loading.update_resolution(resolution)
        self.generate()          #This goes according to self.resolution, so everything is fine.

    def ALL_PLAYERS_LOADED(self):
        return self.loaded_players is self.total_players

    def create_player(self, name, number, chars_number, chars_size, **kwparams):
        self.total_players          += 1
        for player in self.players:
            if name == player.name: raise PlayerNameExistsException("The player name "+name+" already exists")
        self.__create_player(name, number, chars_number, chars_size, **kwparams)

    @run_async
    def __create_player(self, player_name, player_number, chars_number, chars_size, **kwparams):
        self.__add_player(Player(player_name, player_number, chars_number, chars_size, **kwparams))

    def add_players(self, *players):
        if not isinstance(players, (tuple, list)):    raise BadPlayersParameter("The list of players to add can't be of type "+str(type(players)))
        for player in players:  self.__add_player(player)

    def __add_player(self, player):
        if isinstance(player, Player): 
            global POSITION_CHAR 
            self.players.append(player)
            for character in player.characters: 
                character.rect.topleft = POSITION_CHAR
                POSITION_CHAR = tuple([x+100 for x in POSITION_CHAR])
                character.change_size((self.cells.sprites()[0].rect.width, self.cells.sprites()[0].rect.width))
                c = random.choice(self.quadrants[player.order])
                character.rect.center = c.rect.center
                self.characters.add(character)
                LOG.log('DEBUG', "Character ", character.id, " has the initial position ", c.pos)
            self.loaded_players += 1
            return 0
        raise BadPlayerTypeException("A player in the board can't be of type "+str(type(player)))

    def draw(self, surface, hitboxes=False, fps=True, clock=None):
        if self.ALL_PLAYERS_LOADED():
            super().draw(surface)                                                                           #Draws background
            surface.blit(self.platform.image, self.platform.rect)                                           #Draws board
            self.paths.draw(surface)                                                                        #Draws paths between cells
            self.trans_paths.draw(surface) 

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
            if fps:         UtilityBox.draw_fps(surface, clock)
        else:
            self.loading.draw(surface)
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
                self.drag_char.add(self.active_char.sprite)
                self.drag_char.sprite.set_selected(True)
        elif event.type == pygame.MOUSEBUTTONUP:  #If we are dragging it we will have a char in here
            if self.drag_char.sprite is not None:
                self.drag_char.sprite.set_selected(False)
                if self.active_cell.sprite is not None: self.drag_char.sprite.rect.center = self.active_cell.sprite.center #TODO can delete the condition when chars are proplery positioned
                self.drag_char.empty()    
        if self.drag_char.sprite is not None:   self.drag_char.sprite.rect.center = mouse_position

        if mouse_movement:
            cell = pygame.sprite.spritecollideany(mouse_sprite, self.cells.sprites(), collided=pygame.sprite.collide_circle)
            if cell is not None:  self.active_cell.add(cell)
            
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
        if keys_pressed[pygame.K_DOWN]:         pass
        if keys_pressed[pygame.K_UP]:           pass
        if keys_pressed[pygame.K_LEFT]:         pass
        if keys_pressed[pygame.K_RIGHT]:        pass
        if keys_pressed[pygame.K_KP_ENTER]\
            or keys_pressed[pygame.K_SPACE]:    pass

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