import pygame
from os import listdir
from os.path import isfile, join, dirname
from exceptions import BadCharacterInitException, StateNotFoundException
from resizer import Resizer
from paths import IMG_FOLDER, Path
from logger import Logger as LOG
from decorators import run_async
from ui_element import InfoBoard
from sprite  import AnimatedSprite
from utility_box import UtilityBox

__all__ = ["Player", "Character", "Warrior", "Wizard", "Priestess", "Pawn"]

NEXT_SPRITE_COUNTER = 10

#The only purpose of this class is to organize the shit inside characters a little but better
class Restrictions(object):
    def __init__(self, max_dist=1, move_along_lvl = False, move_along_index = False):
        self.dist               = max_dist          #Max spaces that a char can move
        self.only_same_lvl      = move_along_lvl    #If only can move along the same level
        self.only_same_index    = move_along_index  #If only can move along the same index

class Player(object):
    def __init__(self, name, order, pieces_qty, sprite_size, canvas_size, infoboard=None, **sprite_paths): #TODO infoboard shoudlnt be none
        self.name       = name
        self.order      = order
        self.characters = Character.factory(name, pieces_qty, sprite_size, canvas_size, **sprite_paths)
        self.infoboard  = infoboard
        self.turn       = -1
    
class Character(AnimatedSprite):
    __default_aliases   = { "idle" : "idle",
                            "fight" : "fight",
                            "pickup" : "pickup",
                            "drop" : "drop",
                            "action" : "action",
                            "die" : "die"    
    }
    def __init__(self, my_player, _id, position, size, canvas_size, sprites_path, *sprite_list, **aliases):
        LOG.log('DEBUG', "Initializing character ", _id, " of player ", my_player)
        super().__init__(_id, position, size, canvas_size, *sprite_list, sprite_folder=sprites_path)
        self.my_master  = my_player
        self.movement   = Restrictions()
        self.state      = "idle"
        self.aliases    = aliases
        self.count      = 0
        UtilityBox.join_dicts(self.aliases, Character.__default_aliases)
    
    def get_master(self):
        return self.my_master

    def set_state(self, state):
        self.state  = state
        for index in range (0, len(self.ids)):
            if state in self.ids[index]:
                self.animation_index = index
                return True
        raise StateNotFoundException("Character doesn't have the state "+str(state))

    def animation_frame(self):
        #Do it properly so it finds the next one even going all the way around the list
        index = self.animation_index+1
        while True:
            if self.state in self.ids[index].lower():
                self.animation_index = index
                break
            if index is self.animation_index:           #A complete loop with no matches, only one sprite of the action in self.state
                break
            index=index+1 if index < len(self.ids)-1 else 0  #going back to start

    def hitbox_action(self, command, value=-1):
        #if  "mouse" in command and "sec" in command:        self.dec_index()
        #elif "mouse" in command and "first" in command:     self.inc_index()
        pass
    
    def mvnt_possible(self, source, destiny):
        return True

    def set_selected(self, selected):
        self.state=self.aliases['pickup'] if selected is True else self.aliases['idle']
    
    @staticmethod
    def generate_paths(existing_paths, initial_index, restrictions):
        max_dist    = restrictions.dist+1
        solutions   = []
        path        = []
        to_check    = [(initial_index, 0)]  #sturcture of (index, step_of_this_index)
        iterations  = 0
        while len(to_check) > 0:
            iterations += 1
            path.append(to_check.pop(-1)[0])
            if len(path) is max_dist:
                solutions.append(path.copy())                       #Add solution
                if len(to_check) > 0:               del path[to_check[-1][1]:]  #Restore path to the last bifurcation
                continue
            #Adding destinations to to_check if there is an existant path with the current index (path last index)
            for dest in range(0, len(existing_paths[0])):
                if dest not in path\
                and existing_paths[path[-1]][dest]: to_check.append((dest, len(path)))
        LOG.log('DEBUG', "Number of iterations searching paths of distance ",restrictions.dist," -> ",iterations)
        return solutions

    '''def valid_mvnt(self, movement):
        init_pos, dest_pos = movement[0], movement[1]
        if init_pos is not dest_pos:
            if not self.movement.bypass_enemies and dest_pos.has_enemy():
                return False 
            if not self.movement.bypass_allies and dest_pos.has_ally():
                return False
            if (init_pos.get_lvl() is not dest_pos.get_lvl() and self.movement.move_in_same_lvl)\
            and (init_pos.get_index() is not dest_pos.get_index() and self.movement.move_in_same_index):
                return False
        return True'''

    def __modify_paths(self, paths, map, solutions):
        pass #Do nothing, this must be 

    @staticmethod
    @run_async
    def __char_loader(char_constructor, result, count, *params, **kwparams):
        #the method referente is .add if its a pygame.sprite.group, else .append because its supposed to be a list
        add_to_result = result.add if isinstance(result, pygame.sprite.Group) else result.append
        for _ in range (0, count):          
            add_to_result(char_constructor(*params, **kwparams))

    @staticmethod
    def factory(player_name, pieces_qty, sprite_size, canvas_size, **sprite_paths):
        LOG.log('INFO', "----Factory, making ", player_name, " characters----")
        if not isinstance(pieces_qty, dict):    raise BadCharacterInitException("pieces_qty must be dictionary, not "+str(type(pieces_qty)))   
        if not isinstance(sprite_paths, dict):  raise BadCharacterInitException("sprite_paths must be dictionary, not "+str(type(sprite_paths)))
        characters                          = pygame.sprite.Group()
        threads                             = []

        path, number_of = IMG_FOLDER+"\\pawn", 8
        if "pawn" in pieces_qty:            number_of   = pieces_qty["pawn"]
        if "pawn" in sprite_paths:          path        = sprite_paths["pawn"]
        threads.append(Character.__char_loader(Pawn, characters, number_of, player_name, "pawn", (0, 0), sprite_size, canvas_size, path))

        path, number_of = IMG_FOLDER+"\\warrior", 4
        if "warrior" in pieces_qty:         number_of   = pieces_qty["warrior"]
        if "warrior" in sprite_paths:       path        = sprite_paths["warrior"]
        threads.append(Character.__char_loader(Pawn, characters, number_of, player_name, "warrior", (0, 0), sprite_size, canvas_size, path))

        path, number_of = IMG_FOLDER+"\\wizard", 2
        if "wizard" in pieces_qty:          number_of   = pieces_qty["wizard"]
        if "wizard" in sprite_paths:        path        = sprite_paths["wizard"]
        threads.append(Character.__char_loader(Wizard, characters, number_of, player_name, "wizard", (0, 0), sprite_size, canvas_size, path))

        path, number_of = IMG_FOLDER+"\\priestess", 1
        if "priestess" in pieces_qty:       number_of   = pieces_qty["priestess"]
        if "priestess" in sprite_paths:     path        = sprite_paths["priestess"]       
        threads.append(Character.__char_loader(Priestess, characters, number_of, player_name, "priestess", (0, 0), sprite_size, canvas_size, path))

        for t in threads:
            t.join()        #Threading.join
        LOG.log('INFO', "----Factory, done making ", player_name, " characters----")
        return characters

    @staticmethod
    def all_paths_factory(char_type, paths_map, distances_map, cells_per_level):
        lvl_size        = cells_per_level
        destinations    = {}
        length          = len(paths_map[0]) #Want to know how many indexes the map has
        if 'pawn' in char_type:         restrictions, results = Pawn.RESTRICTIONS, Pawn.MOVEMENTS
        elif 'warrior' in char_type:    restrictions, results = Warrior.RESTRICTIONS, Warrior.MOVEMENTS
        elif 'wizard' in char_type:     restrictions, results = Wizard.RESTRICTIONS, Wizard.MOVEMENTS
        elif 'priest' in char_type:     restrictions, results = Priestess.RESTRICTIONS, Priestess.MOVEMENTS
        elif 'matron' in char_type:     restrictions, results = MatronMother.RESTRICTIONS, MatronMother.MOVEMENTS
        else:                           raise BadCharacterInitException("this type of char is not accepted. AllPathsFactory")
        if restrictions.dist is 1:          #No need to check much, only if the immediate path exists
            for x in range(0, length):      
                for y in range(x, length):
                    if x is y:              continue                    #Same cell, no movmnt
                    if paths_map[x][y]:
                        try:                destinations[x].append((y, x))   #The list of destinations already exist for this index
                        except KeyError:    destinations[x] = [(y, x)]       #It doesn't, have to create it
                        try:                destinations[y].append((x, y))
                        except KeyError:    destinations[y] = [(x, y)] 
        if restrictions.dist < 2:   #If less that two but not one, infinite distance w/ restrictions
            for x in range(0, length):      
                for y in range(x, length):
                    if x is y:              continue    #Same cell not movmnt
                    if restrictions.only_same_index:    #If the dest cell doesn't abide by this restriction
                        if not paths_map[x][y] or x%lvl_size is not y%lvl_size:
                            continue                    #Next iteration
                    if restrictions.only_same_lvl:      #If the dest cell doesn't abide by this restriction
                        if x//lvl_size is not y//lvl_size:    
                            continue                    #Next iteration
                    #All conditions cleared, its a possible destiny
                    try:                destinations[x].append((y, x))   #The list of destinations already exist for this index
                    except KeyError:    destinations[x] = [(y, x)]       #It doesn't, have to create it
                    try:                destinations[y].append((x, y))
                    except KeyError:    destinations[y] = [(x, y)] 
        else:                       #For complex paths, we need a submethod
            for x in range(0, length):
                destinations[x] = Character.generate_paths(paths_map, x, restrictions)
        results = destinations

class Warrior(Character):
    Restrictions    = Restrictions(max_dist=2)
    MOVEMENTS       = {} 
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path):
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path)

class Wizard(Character):
    RESTRICTIONS    = Restrictions(max_dist=3)
    MOVEMENTS       = {} 
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path):
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path)

class Priestess(Character):
    RESTRICTIONS = Restrictions(max_dist=1, move_along_lvl=True, move_along_index=True)
    MOVEMENTS    = {} 
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path):
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path)
        #self.movement   = Restrictions(max_dist=-1, move_along_lvl=True, move_along_index=True)

    #No need for a backtracking in priestess, only two steps.
    def generate_paths(self, existing_paths, board_map, distance_map, initial_pos):
        possible_paths  = []    #All solutions
        for i in range (0, len(existing_paths[initial_pos.index])):
            try:
                if i is not initial_pos.index\
                and distance_map[initial_pos.index][i] > 0:
                            self.add_path([initial_pos, board_map[i]], possible_paths)
            except KeyError:    #Due to the difference in index, due to the different number of circles between levels
                continue
        return possible_paths

class Pawn(Character):
    RESTRICTIONS    = Restrictions()
    MOVEMENTS       = {} 
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path):
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path)
    
    def generate_paths(self, existing_paths, board_map, distance_map, initial_pos):
        print("POSITION "+str(initial_pos.index))
        print("INITIAL DISTANCES")
        initial_distances   = self.__generate_enemies_distances(distance_map, board_map, initial_pos.index)
        unfiltered_paths    = super().generate_paths(existing_paths, board_map, distance_map, initial_pos)
        #print(unfiltered_paths)
        if len(initial_distances) > 0:    #If there is a direct path possible towards an enemy
            for i in range(0, len(unfiltered_paths)):   #For each possible basic path
                dest_pos = None
                for cell in board_map.values():

                    if unfiltered_paths[i][-1] == (cell.get_lvl(), cell.get_index()):
                        dest_pos = cell
                        break
                print("FINAL DISTANCES IN DESTINY "+str(cell.index))
                final_distances = self.__generate_enemies_distances(distance_map, board_map, dest_pos.index)

                #This type of if works because the key is a basic integer, it wouldn't otherwise
                #If there is no less distance with any of the enemies, this path is no good
                delete_path = True
                for key in initial_distances.keys():
                    try:
                        if final_distances[key] < initial_distances[key]: delete_path = False
                    except KeyError:    #This due to the destiny having no connnection to a cell that the start_pos did have.
                        continue
                if delete_path:
                    print("DELETING PATH") 
                    del unfiltered_paths[i]
                    i+=1
        #print(unfiltered_paths)
        return unfiltered_paths #TODO FIX THIS SHIT

    #IN WHERE THE HELL IM CHECKING FOR ENEMIES, WHAT THE FUCK DOES THIS SHIT DO???? 
    def __generate_enemies_distances(self, distance_map, board_map, position):
        distances_to_enemies = {}
        cells_with_enemies = [cell.index for cell in board_map.values() if (cell.index is not position and cell.has_enemy())]
        for cell in board_map.values(): print(cell.index + " has enemy "+str(cell.has_enemy()) + ", ally "+str(cell.has_ally()))
        print(len(cells_with_enemies))
        for cell in cells_with_enemies: print("ENEMIE IN "+str(cell.index))
        raise Exception("dfd")
        if distance_map[position][i] > 0: #Exists direct path to that shit (Same level or big circle [rank or file])
            try:
                if distance_map[position][i] < distances_to_enemies[i]:
                    distances_to_enemies[i] = distance_map[position][i]
            except KeyError:
                distances_to_enemies[i] = distance_map[position][i]
        print(distances_to_enemies)
        return distances_to_enemies
            
class MatronMother(Character):
    RESTRICTIONS    = Restrictions()
    MOVEMENTS       = {} 
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path):
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path)
        #self.movement   = Restrictions(bypass_enemies=True)