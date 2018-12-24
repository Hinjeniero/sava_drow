__all__ = ["Player", "Character", "Warrior", "Wizard", "Priestess", "Pawn", "MatronMother"]
__version__ = '0.9'
__author__ = 'David Flaity Pardo'

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
        self.index      = 0 #Index of the cell that it is in
    
    def get_paths(self, graph, distances, current_map):
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
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path, **aliases)

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
    CHECK_ENEMIES   = Restrictions(max_dist=0, move_along_lvl=True, move_along_index=True)
    DEFAULT_PATH    = IMG_FOLDER+'\\Pawn'
    DEFAULT_AMMOUNT = 8
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path, **aliases):
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path, **aliases)

    def get_paths(self, initial_pos, distances, current_map):
        results = []
        unfiltered_paths = Movements.get_movements(hash(Pawn.CHECK_ENEMIES))[initial_pos]
        enemies = {}
        for path in unfiltered_paths:
            #If the destiny has an enemy and there is no ally in the middle. Those don't need to be checked again
            if current_map[path[-1]].has_enemy(self.my_master)\
            and not any(path[i].has_ally(self.my_master) for i in range(1, len(path)-1)):
                enemies[path[-1]] = distances[initial_pos][path[-1]]  #Distance to the enemy. The key is the destiny
        #Now, we compare the enemies distance to those that we would have in the 2-4 possible positions
        for new_index in Movements.get_movements(hash(Pawn.RESTRICTIONS))[initial_pos]:
            for enemy_index, enemy_dist in enemies.items():
                if distances[new_index][enemy_index] < enemy_dist:  
                    results.append((initial_pos,new_index))
                    break   #breaking the first loop
        print("PAWN, CHECKING RESULTS FOR "+str(initial_pos)+" -> "+str(results))
        return results

    def set_paths(self, existing_paths, distances, cells_per_lvl):
        Movements.set_movements(existing_paths, distances, Pawn.RESTRICTIONS, cells_per_lvl)

    def get_enemies_distances(self, initial_pos, distances):
        pass
            
class MatronMother(Character):
    RESTRICTIONS    = Restrictions()
    DEFAULT_PATH    = IMG_FOLDER+'\\Matron_Mother'
    DEFAULT_AMMOUNT = 1
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path, **aliases):
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path, **aliases)
        #self.movement   = Restrictions(bypass_enemies=True)

    def get_paths(self, index, current_map):
        result = Movements.get_movements(hash(MatronMother.RESTRICTIONS))
        return None if not result else result[index]

    def set_paths(self, existing_paths, distances, cells_per_lvl):
        Movements.set_movements(existing_paths, distances, MatronMother.RESTRICTIONS, cells_per_lvl)