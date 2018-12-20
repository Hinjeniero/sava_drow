import pygame
from os import listdir
from os.path import isfile, join, dirname
from exceptions import BadCharacterInitException, StateNotFoundException
from resizer import Resizer
from paths import IMG_FOLDER, Restrictions, Movements
from logger import Logger as LOG
from decorators import run_async
from sprite  import AnimatedSprite
from utility_box import UtilityBox

__all__ = ["Player", "Character", "Warrior", "Wizard", "Priestess", "Pawn", "MatronMother"]

class Player(object):
    def __init__(self, name, order, sprite_size, canvas_size, infoboard=None, **character_params): #TODO infoboard shoudlnt be none
        self.name       = name
        self.order      = order
        self.characters = Character.factory(name, sprite_size, canvas_size, **character_params)
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
    def __init__(self, my_player, _id, position, size, canvas_size, sprites_path, **aliases):
        LOG.log('DEBUG', "Initializing character ", _id, " of player ", my_player)
        super().__init__(_id, position, size, canvas_size, sprite_folder=sprites_path)
        self.aliases    = Character.__default_aliases.copy()
        self.aliases.update(aliases)
        self.my_master  = my_player
        self.limits     = Restrictions()
        self.state      = self.aliases['idle']
    
    def get_paths(self, index_pos, current_map):
        '''Mere interface to be overloaded'''
        return 'This is only an interface'
    
    def set_paths(self, existing_paths, circles_per_lvl):
        '''Mere interface to be overloaded'''
        return 'This is only an interface'

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
        index = self.animation_index
        while True:
            index=index+1 if index < len(self.ids)-1 else 0  #going back to start
            if self.state in self.ids[index].lower():
                self.animation_index = index
                break
            if index is self.animation_index:           #A complete loop with no matches, only one sprite of the action in self.state
                break

    def hitbox_action(self, command, value=-1):
        #if  "mouse" in command and "sec" in command:        self.dec_index()
        #elif "mouse" in command and "first" in command:     self.inc_index()
        pass
    
    def mvnt_possible(self, source, destiny):
        return True

    def set_selected(self, selected):
        self.state=self.aliases['pickup'] if selected is True else self.aliases['idle']

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

    @staticmethod
    @run_async
    def __char_loader(char_class, result, count, *params, **kwparams):
        #the method referente is .add if its a pygame.sprite.group, else .append because its supposed to be a list
        add_to_result = result.add if isinstance(result, pygame.sprite.Group) else result.append
        for _ in range (0, count):
            add_to_result(char_class(*params, **kwparams))

    @staticmethod
    #This contains our default parameters for all the chars
    def parse_json_char_params(json_params):
        character_types = ['pawn', 'warrior', 'wizard', 'priestess', 'matron_mother']
        ammounts        = {'pawn': Pawn.DEFAULT_AMMOUNT, 'warrior': Warrior.DEFAULT_AMMOUNT, 'wizard': Wizard.DEFAULT_AMMOUNT,\
                            'priestess': Priestess.DEFAULT_AMMOUNT, 'matron_mother': MatronMother.DEFAULT_AMMOUNT}
        img_paths       = {'pawn': Pawn.DEFAULT_PATH, 'warrior': Warrior.DEFAULT_PATH, 'wizard': Wizard.DEFAULT_PATH,\
                            'priestess': Priestess.DEFAULT_PATH, 'matron_mother': MatronMother.DEFAULT_PATH}
        #Parsing names of keys
        for key in json_params.keys():          #Iterating input keys
            for correct_key in character_types: #Iterating template keys
                if key in correct_key:          #IF they match, parse the input key to the template key name
                    json_params[correct_key] = json_params.pop(key)
                    break
        #Parsing non existant characters and paths
        for character in character_types:
            try:
                json_params[character]
                try:
                    json_params[character]['path']
                except KeyError:
                    json_params[character]['path'] = img_paths[character]
                try:
                    json_params[character]['number']
                except KeyError:
                    json_params[character]['number'] = ammounts[character]
            except KeyError:
                json_params[character] = {'path': img_paths[character], 'number': ammounts[character]}

    @staticmethod
    def factory(player_name, sprite_size, canvas_size, **character_settings):
        LOG.log('INFO', "----Factory, making ", player_name, " characters----")
        Character.parse_json_char_params(character_settings)
        characters  = pygame.sprite.Group()
        threads     = []

        for key in character_settings.keys():
            char_init = Pawn if 'pawn' in key else Wizard if 'wizard' in key\
            else Warrior if 'warrior' in key else Priestess if 'priestess' in key\
            else MatronMother if 'matron' in key else None
            #Actual loading
            threads.append(Character.__char_loader(char_init, characters, character_settings[key]['number'],\
                            player_name, player_name+key, (0, 0), sprite_size, canvas_size, character_settings[key]['path'],\
                            **character_settings[key]['aliases']))
        for t in threads:   t.join()        #Threading.join
        LOG.log('INFO', "----Factory, done making ", player_name, " characters----")
        return characters

class Warrior(Character):
    RESTRICTIONS    = Restrictions(max_dist=2)
    DEFAULT_PATH    = IMG_FOLDER+'\\Warrior'
    DEFAULT_AMMOUNT = 4
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path, **aliases):
        #sprites_path = Warrior.DEFAULT_PATH if not sprites_path else sprites_path
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path, **aliases)
        
    def get_paths(self, index, current_map):
        result = Movements.get_movements(hash(Warrior.RESTRICTIONS))
        return None if not result else result[index]

    def set_paths(self, existing_paths, distances, cells_per_lvl):
        Movements.set_movements(existing_paths, distances, Warrior.RESTRICTIONS, cells_per_lvl)


class Wizard(Character):
    RESTRICTIONS    = Restrictions(max_dist=3)
    DEFAULT_PATH    = IMG_FOLDER+'\\Wizard'
    DEFAULT_AMMOUNT = 2
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path, **aliases):
        #sprites_path = Wizard.DEFAULT_PATH if not sprites_path else sprites_path
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path, **aliases)

    def get_paths(self, index, current_map):
        result = Movements.get_movements(hash(Wizard.RESTRICTIONS))
        return None if not result else result[index]
    def set_paths(self, existing_paths, distances, cells_per_lvl):
        Movements.set_movements(existing_paths, distances, Wizard.RESTRICTIONS, cells_per_lvl)

class Priestess(Character):
    RESTRICTIONS    = Restrictions(max_dist=0, move_along_lvl=True, move_along_index=True)
    DEFAULT_PATH    = IMG_FOLDER+'\\Priestess'
    DEFAULT_AMMOUNT = 2
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path, **aliases):
        #sprites_path = Priestess.DEFAULT_PATH if not sprites_path else sprites_path
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path, **aliases)
        #self.movement   = Restrictions(max_dist=-1, move_along_lvl=True, move_along_index=True)

    def get_paths(self, index, current_map):
        result = Movements.get_movements(hash(Priestess.RESTRICTIONS))
        return None if not result else result[index]
        
    def set_paths(self, existing_paths, distances, cells_per_lvl):
        print("SET PATHS, HASH OF RESTRICTIONS -> "+str(hash(Priestess.RESTRICTIONS)))
        Movements.set_movements(existing_paths, distances, Priestess.RESTRICTIONS, cells_per_lvl)

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
    DEFAULT_PATH    = IMG_FOLDER+'\\Pawn'
    DEFAULT_AMMOUNT = 8
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path, **aliases):
        #sprites_path = Pawn.DEFAULT_PATH if not sprites_path else sprites_path
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path, **aliases)

    def get_paths(self, index, current_map):
        result = Movements.get_movements(hash(Pawn.RESTRICTIONS))
        return None if not result else result[index]

    def set_paths(self, existing_paths, distances, cells_per_lvl):
        Movements.set_movements(existing_paths, distances, Pawn.RESTRICTIONS, cells_per_lvl)

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
    DEFAULT_PATH    = IMG_FOLDER+'\\Matron_Mother'
    DEFAULT_AMMOUNT = 1
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path, **aliases):
        #sprites_path = MatronMother.DEFAULT_PATH if not sprites_path else sprites_path
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path, **aliases)
        #self.movement   = Restrictions(bypass_enemies=True)

    def get_paths(self, index, current_map):
        result = Movements.get_movements(hash(MatronMother.RESTRICTIONS))
        return None if not result else result[index]

    def set_paths(self, existing_paths, distances, cells_per_lvl):
        Movements.set_movements(existing_paths, distances, MatronMother.RESTRICTIONS, cells_per_lvl)