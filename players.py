import pygame
from os import listdir
from os.path import isfile, join, dirname
from exceptions import BadCharacterInitException, BadCharacterActionException
from resizer import Resizer
from paths import IMG_FOLDER, Path
__all__ = ["Player", "Character", "Warrior", "Wizard", "Priestess", "Pawn"]
NEXT_SPRITE_COUNTER = 10

#The only purpose of this class is to organize the shit inside characters a little but better
class Restrictions(object):
    def __init__(self, max_dist=1, move_along_lvl = False, move_along_index = False, bypass_allies=True, bypass_enemies=True, approach_enemies=False):
        self.dist               = max_dist          #Max spaces that a char can move
        self.move_in_same_lvl   = move_along_lvl    #If only can move along the same level
        self.move_in_same_index = move_along_index  #If only can move along the same index
        self.bypass_allies      = bypass_allies     #If can move bypassing allies in a cell
        self.bypass_enemies     = bypass_enemies	#If can move bypassing enemies in a cell
        self.approach_enemies   = approach_enemies  #If can only move in a way that will approach him to enemies

class Player(object):
    def __init__(self, name, order, pieces_qty, sprite_size, infoboard=None, **sprite_paths): #TODO infoboard shoudlnt be none
        self.name       = name
        self.order      = order
        self.characters = Character.factory(pieces_qty, sprite_size, **sprite_paths)
        self.turn       = -1
    
    def draw_characters(self, surface, active=True):
        pass
    
class Character(pygame.sprite.Sprite):
    @staticmethod
    def factory(player_name, pieces_qty, sprite_size, **sprite_paths):
        characters                              = pygame.sprite.Group()
        if not isinstance(pieces_qty, dict):    raise BadCharacterInitException("pieces_qty must be dictionary, not "+str(type(pieces_qty)))   
        if not isinstance(sprite_paths, dict):  raise BadCharacterInitException("sprite_paths must be dictionary, not "+str(type(sprite_paths)))
        
        limit, counter = 8, 0
        if "pawn" in pieces_qty:            limit = pieces_qty["pawn"]
        while counter < limit:
            name = "pawn"+str(counter)    
            if "pawn" in sprite_paths:      characters.add(Pawn(name, sprite_size, sprite_paths["pawn"]))
            else:                           characters.add(Pawn(name, sprite_size, IMG_FOLDER+"\\pawn"))
            counter+=1 

        limit, counter = 4, 0
        if "warrior" in pieces_qty:         limit = pieces_qty["warrior"]
        while counter < limit:
            name = "warrior"+str(counter) 
            if "warrior" in sprite_paths:   characters.add(Warrior(name, sprite_size, sprite_paths["warrior"]))
            else:                           characters.add(Warrior(name, sprite_size, IMG_FOLDER+"\\warrior"))
            counter+=1

        limit, counter = 2, 0
        if "wizard" in pieces_qty:          limit = pieces_qty["wizard"]
        while counter < limit:
            name = "wizard"+str(counter) 
            if "wizard" in sprite_paths:    characters.add(Wizard(name, sprite_size, sprite_paths["wizard"]))
            else:                           characters.add(Wizard(name, sprite_size, IMG_FOLDER+"\\wizard"))
            counter+=1
        
        #ONLY 1 PRIESTESS, MAKES NO SENSE TO HAVE MORE FROM THE START
        if "priestess" in sprite_paths: characters.add(Priestess("priestess", sprite_size, sprite_paths["priestess"]))
        else:                           characters.add(Priestess("priestess", sprite_size, IMG_FOLDER+"\\priestess"))
        return characters

    def __init__(self, my_player, id_, size, sprites_path):
        super().__init__()
        self.my_master  = my_player
        self.id         = id_
        self.rect       = None
        self.image      = None
        self.mask       = None
        self.movement   = Restrictions()
        self.files      = {}
        self.sprites    = {"idle"   : [], 
                        "run"       : [], 
                        "walk"      : [],
                        "attack"    : [],
                        "hurt"      : [],
                        "pick"      : [],
                        "drop"      : [],
                        "die"       : []
        }
        self.big_sprites= {"idle"   : [],
                        "run"       : [], 
                        "walk"      : [],
                        "attack"    : [],
                        "hurt"      : [],
                        "pick"      : [],
                        "drop"      : [],
                        "die"       : []
        }
        self.masks      = {"idle"   : [],
                        "run"       : [], 
                        "walk"      : [],
                        "attack"    : [],
                        "hurt"      : [],
                        "pick"      : [],
                        "drop"      : [],
                        "die"       : []
        }
        self.state      = "idle"
        self.index      = 0
        self.counter    = 0
        self.hover      = False
        self.selected   = False
        self.load_sprites(size, sprites_path)
    
    def get_master(self):
        return self.my_master

    def change_size(self, size):
        for list_ in self.sprites.values():     list_.clear()
        for list_ in self.big_sprites.values(): list_.clear()
        for list_ in self.masks.values():       list_.clear()
        for sprite_path in self.files.keys():   self.__add_sprite(sprite_path, size)
        self.rect.size = self.__current_sprite().get_size()

    def move(self): #move(cols, rows, char_in_middle, char_just_near)
        if 0: return True   #Allowed movm
        if 1: return False  #not allowed

    #This method is tested already
    def load_sprites(self, size, sprite_path):
        sprite_images = [sprite_path+'\\'+f for f in listdir(sprite_path) if isfile(join(sprite_path, f))]
        for sprite_image in sprite_images:
            if sprite_image.lower().endswith(('.png', '.jpg', '.jpeg', 'bmp')):
                self.__add_sprite(sprite_image, size)
        self.image  = self.__current_sprite()
        self.rect   = pygame.Rect((200, 200), self.image.get_size())
        self.mask   = self.__current_mask()
    
    def __add_sprite(self, path, size=None):
        for action in self.sprites.keys():
            if action in path.lower():
                try:                self.files[path] 
                except KeyError:    self.files[path] = pygame.image.load(path)
                if size is None:    self.sprites[action].append(self.files[path])
                else:               self.sprites[action].append(Resizer.resize_same_aspect_ratio(self.files[path], size))
                self.masks[action].append(pygame.mask.from_surface(self.sprites[action][-1]))
                big_sprite = pygame.transform.smoothscale(self.sprites[action][-1], tuple(int(x*1.25 ) for x in self.sprites[action][-1].get_size()))
                self.big_sprites[action].append(big_sprite)
                return

    def update(self): #Make it bigger (Like when in touch with hitbox, this could be done in board itself)
        self.counter        += 1
        if self.counter is NEXT_SPRITE_COUNTER:
            self.counter    = 0
            self.animate()

    def change_action(self, action):
        try:
            self.sprites[action]
            self.state  = action
            self.index  = 0
            self.image  = self.sprites[action][self.index] #TODO big sprite here too
        except KeyError:
            raise BadCharacterActionException("Character doesn't have the action "+str(action))
    
    def __current_sprite(self):
        return self.sprites[self.state][self.index]

    def __current_big_sprite(self):
        return self.big_sprites[self.state][self.index]

    def __current_mask(self):
        return self.masks[self.state][self.index]

    def animate(self):
        #if self.state is not "pick":
        self.index  = 0 if self.index is len(self.sprites[self.state])-1 else self.index+1
        self.image  = self.__current_sprite() if not self.hover else self.__current_big_sprite()
        self.mask   = self.__current_mask()
        #else:   self.index +=1 if self.index < len(self.sprites[self.state])-1 else 0

    def hitbox_action(self, command, value=-1):
        #if  "mouse" in command and "sec" in command:        self.dec_index()
        #elif "mouse" in command and "first" in command:     self.inc_index()
        pass

    def set_selected(self, selected=True):
        self.index  = 0
        if selected: 
            self.state      = "pick"
            self.selected   = True
        else:
            self.state      = "idle"
            self.selected   = False
    
    def is_selected(self):
        return self.selected
    
    def mvnt_possible(self, source, destiny):
        return True
    
    def set_hover(self, active=True):
        if active:  self.image = self.__current_big_sprite()
        else:       self.image = self.__current_sprite()
        self.hover = active

    #THIS NEEDS A FUCKIN BACKTRACKING
    #Map --> graph of booleans
    #paths --> Contain info of all the rooms
    #TODO make sure of the format to return and the format of the input parameters to make a decent implementation
    def generate_paths(self, map, paths, initial_pos):
        possible_paths  = []
        current_path    = []
        checked         = []
        to_check        = [initial_pos]
        while len(to_check) > 0:
            current_pos = to_check.pop(-1)
            checked.append(current_pos)
            current_path.append(current_pos)
            if len(current_path) is self.movement.dist or current_path[-1] is current_path[0]: #TODO HOW TO CHECK PRIESTESS USE CASES OF THE LVL-moving-and-ending
                pass #TODO deep copy the list to possible_paths
                to_check.pop(-1)
                current_path.pop(-1)
            else:
                for cell in map[current_pos]:
                    if cell not in checked and cell not in to_check:
                        if self.valid_mvnt(initial_pos, cell):
                            to_check.append(cell)
        return possible_paths

    def valid_mvnt(self, init_pos, dest_pos):
        if init_pos is not dest_pos:
            if not self.movement.bypass_enemies and dest_pos.has_enemy():
                return False 
            if not self.movement.bypass_allies and dest_pos.has_ally():
                return False
            if (init_pos.get_lvl() is not dest_pos.get_lvl()) and self.movement.move_in_same_lvl:
                return False
            if (init_pos.get_index() is not dest_pos.get_index()) and self.movement.move_in_same_index:
                return False
        return True

    def __modify_paths(self, paths, map, solutions):
        pass #Do nothing, this must be 

class Warrior(Character):
    def __init__(self, my_player, id_, size, sprites_path):
        super().__init__(my_player, id_, size, sprites_path)
        self.movement   = Restrictions(max_dist=2)

class Wizard(Character):
    def __init__(self, my_player, id_, size, sprites_path):
        super().__init__(my_player, id_, size, sprites_path)
        self.movement   = Restrictions(max_dist=3)

class Priestess(Character):
    def __init__(self, my_player, id_, size, sprites_path):
        super().__init__(my_player, id_, size, sprites_path)
        self.movement   = Restrictions(max_dist=-1, move_along_lvl=True, move_along_index=True, bypass_allies=False, bypass_enemies=False)

class Pawn(Character):
    def __init__(self, my_player, id_, size, sprites_path):
        super().__init__(my_player, id_, size, sprites_path)
        self.movement   = Restrictions(approach_enemies=True)

class MatronMother(Character):
    def __init__(self, my_player, id_, size, sprites_path):
        super().__init__(my_player, id_, size, sprites_path)
        self.movement   = Restrictions(bypass_enemies=True)