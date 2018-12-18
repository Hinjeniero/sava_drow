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
    def __init__(self, max_dist=1, move_along_lvl = False, move_along_index = False, bypass_allies=True, bypass_enemies=True, approach_enemies=False):
        self.dist               = max_dist          #Max spaces that a char can move
        self.move_in_same_lvl   = move_along_lvl    #If only can move along the same level
        self.move_in_same_index = move_along_index  #If only can move along the same index
        self.bypass_allies      = bypass_allies     #If can move bypassing allies in a cell
        self.bypass_enemies     = bypass_enemies	#If can move bypassing enemies in a cell
        self.approach_enemies   = approach_enemies  #If can only move in a way that will approach him to enemies

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

    #map is of type numpy, and paths of type 
    def generate_paths(self, existing_paths, board_map, distance_map, initial_pos): #TODO Initial pos is a pasth and we are passing it as a utple
        print("Searching paths for "+self.id)
        possible_paths  = []    #All solutions
        current_path    = []    #Currebt solutionb
        checked         = []    #Checked already    
        to_check        = [(initial_pos, initial_pos)] #Both are paths type objects. Every objects of us is (path, path)
        #LOG.log('DEBUG', "Initial lenght of to check is ", len(to_check))
        while len(to_check) > 0:
            current_square     = to_check.pop(-1)
            current_path.append(current_square)
            #LOG.log('DEBUG', '---------------')
            #LOG.log('DEBUG', "BEFORE: Lenght of to check is ", len(to_check))
            #IF we already have a path that is the max distance
            if len(current_path)-1 is self.movement.dist:
                #LOG.log('DEBUG', 'LEnght of current path ', [(x[0].pos, x[1].pos) for x in current_path], "Is the distance")
                self.add_path(current_path, possible_paths)
                current_path.pop(-1)
                current_square  = current_path[-1]
            else:
                #For every cell possibly connected to the actual one
                for i in range (0, len(existing_paths[current_square[1].index])):   #Existing paths only contains booleans
                    if existing_paths[current_square[1].index][i]\
                    and i is not current_square[1].index:                               #If actually connected (The bool is Tr)                
                        dest_cell = board_map[i]                                            #Assigning the cell using the index
                        next_step = (current_square[1], dest_cell)                          #Creating the tuple step (init cell -> dest cell)
                        if next_step not in checked and next_step not in to_check:          #If we have not done this step and dont have it already queued 
                                if self.valid_mvnt(next_step):   to_check.append(next_step)     #If the step is valid for the character restrictions, append the step
            #If our cell is not connected to the last one appended to check, we have to regress one more step in this backtracking
            #LOG.log('DEBUG', "AFTER: Lenght of to check is ", len(to_check))
            while len(to_check) > 0 and current_square[1] is not to_check[-1][0]:
                #LOG.log('DEBUG', "if ", current_square[1].pos, " is not ", to_check[-1][0].pos, ", entered")
                current_path.pop(-1)
                current_square = current_path[-1]
        return possible_paths

    def add_path(self, path_to_add, final_list):
        path = []
        for element in path_to_add:
            if isinstance(element, (tuple, list)):    
                if isinstance(element[0], tuple): #Nested tuple
                    path.append(tuple(x for x in element[0]))
                elif isinstance(element[0], Path):
                    path.append(tuple(x for x in element[1].pos))
                elif isinstance(element, (float, int)):   
                    path.append(element)
            elif isinstance(element, Path):         path.append(tuple(x for x in element.pos))
            elif isinstance(element, (float, int)):   path.append(element)
        LOG.log('DEBUG', "PATH FOUND! ", path)
        final_list.append(path)

    def valid_mvnt(self, movement):
        init_pos, dest_pos = movement[0], movement[1]
        if init_pos is not dest_pos:
            if not self.movement.bypass_enemies and dest_pos.has_enemy():
                return False 
            if not self.movement.bypass_allies and dest_pos.has_ally():
                return False
            if (init_pos.get_lvl() is not dest_pos.get_lvl() and self.movement.move_in_same_lvl)\
            and (init_pos.get_index() is not dest_pos.get_index() and self.movement.move_in_same_index):
                return False
        return True

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
        
class Warrior(Character):
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path):
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path)
        self.movement   = Restrictions(max_dist=2)

class Wizard(Character):
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path):
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path)
        self.movement   = Restrictions(max_dist=3)

class Priestess(Character):
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path):
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path)
        self.movement   = Restrictions(max_dist=-1, move_along_lvl=True, move_along_index=True, bypass_allies=False, bypass_enemies=False)

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
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path):
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path)
        self.movement   = Restrictions(approach_enemies=True)
    
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
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path):
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path)
        self.movement   = Restrictions(bypass_enemies=True)