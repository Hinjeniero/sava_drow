"""--------------------------------------------
players module. Contains the entire logic and graphics that 
make up the players.
Have the following classes, inheriting represented by tabs:
    Player
    Character
        ↑Warrior
        ↑Wizard
        ↑Priestess
        ↑Pawn
        ↑MatronMother
--------------------------------------------"""

__all__ = ["Player", "Character", "Warrior", "Wizard", "Priestess", "Pawn", "MatronMother"]
__version__ = '0.9'
__author__ = 'David Flaity Pardo'

#Python libraries
import pygame
from os import listdir
from os.path import isfile, join, dirname
#Selfmade libraries
from exceptions import BadCharacterInitException, StateNotFoundException
from resizer import Resizer
from paths import IMG_FOLDER, Restriction, Movements
from logger import Logger as LOG
from decorators import run_async
from sprite  import AnimatedSprite
from ui_element import InfoBoard
from utility_box import UtilityBox

class Player(object):
    """Player class. Each player has a name, some characters and his own turn.
    Attributes:
        name (str): Name of the player.
        order (int):Order of arrival. A numerical identifier, if you prefer.
        characters (:obj: pygame.sprite.Group): Group of AnimatedSprites that contains all the
                                                different characters that belong to the player.
        infoboard (:obj: InfoBoard):    UiElement subclass. A graphic element that shows all the information
                                        of the player. To be drawn when is the player's turn.
        turn (int): Current turn of this player.
    
    """
    def __init__(self, name, order, sprite_size, canvas_size, infoboard=None, **character_params):
        """Player constructor.
        Args:
            name (str): Name of the player.
            order (int):    Order of arrival. A numerical identifier, if you prefer.
            sprite_size (:tuple: int, int): Size of the image of the characters. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            **character_params (:dict:):    Contains the more specific parameters to create the characters.
                                            Ammount of each type of char, name of their actions, and their folder paths."""
        self.name       = name
        self.order      = order
        self.characters = Character.factory(name, sprite_size, canvas_size, **character_params)
        self.infoboard  = None  #Created in generate
        self.turn       = 0
        self.kills      = 0
        self.corpses    = []    #Contains dead chars.
        self.movements  = 0
        Player.generate(self, canvas_size, **character_params)

    @staticmethod
    def generate(self, canvas_size, **character_params):
        infoboard = InfoBoard(self.name+'_infoboard', pygame.USEREVENT+3, (0, 0), (0.15*canvas_size[0], canvas_size[1]),\
                            canvas_size, texture=IMG_FOLDER+'\\infoboard.png', keep_aspect_ratio = False, cols=6)
        cols = infoboard.get_cols()
        infoboard.add_text_element('initial_padding', '', cols)
        infoboard.add_text_element('player_name', self.name, cols-2)   #Player name
        infoboard.add_text_element('player_number', 'id: '+str(self.order+1), cols-2)   #Player order
        infoboard.add_text_element('player_chars', 'characters: '+str(len(self.characters)), cols-2)   #Player total ammount of chars
        self.infoboard = infoboard

    def register_movement(self, character):
        self.movements += 1
        self.get_character(character).movements += 1

    def add_kill(self, corpse, killer):
        self.kills+=1
        self.corpses.append(corpse)
        self.get_character(killer).kills += 1

    def pause_characters(self):
        for character in self.characters:
            character.set_state("stop")
            character.set_active(False)

    def unpause_characters(self):
        for character in self.characters:
            character.set_state("idle")
            character.set_active(True)      

    def get_character(self, character):
        for char in self.characters:
            if character is char:
                return char

    def update(self):
        self.infoboard.get_sprite('char').set_text('characters: '+str(len(self.characters.sprites())))
        self.infoboard.regenerate_image()

    def draw(self, surface):
        self.infoboard.draw(surface)

    def set_resolution(self, resolution):
        """Resizes the infoboard and the player's characters"""
        if self.infoboard:
            #self.infoboard.set_canvas_size(resolution)
            print("AFTER "+str(len(self.infoboard.sprites)))
        for char in self.characters:
            char.set_canvas_size(resolution)

    def has_char(self, char):
        return self.characters.has(char)

    def remove_char(self, char):
        if self.has_char(char):
            self.characters.remove(char)
            self.update()

class Character(AnimatedSprite):
    """Character class. Inherits from AnimatedSprite.
    Each moving character is a subclass or class related to this one.
    Implements logic and graphics that allows it to have different states (or actions),
    different possible paths based on the same map (Due to the specific Restriction on movement),
    and to belong to different players.
    General class attributes:
        __default_config (:dict:): Contains parameters about the actions aliases. Those aliases are highly dependent
        on how your images are named. It's kind like a parser of those names, since series of sprites are not always
        named the same. Another workaround is name those series of images with the same as the default alias.
        In that way you will link each action in the folder (divided in sprites), with each action here in the character.
            idle (str): When the character is doing nothing.
            fight (str):    When the character is fighting another char.
            pickup (str):   When the char has been picked up by the mouse.
            drop (str): When the char has been dropped down by the mouse (after pickup).
            action (str): Wildcard name for whatever action we want.
            die (str):  When the character dies.
    Attributes:
        aliases (str):  Name of the owning player.
        my_master (int):Order of arrival. A numerical identifier, if you prefer.
        state (str):    Current state of the character (what it is doing).
        index (int):    Index of the current cell that the character is residing in. Unused rn.
    """
    __default_aliases   = { "idle" : "idle",
                            "fight" : "fight",
                            "pickup" : "pickup",
                            "drop" : "drop",
                            "action" : "action",
                            "die" : "die",
                            "stop": "stop" 
    }
    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path, **aliases):
        """Character constructor.
        Args:
            my_player (str):    Owning/Master player of this Character.
            position (:tuple: int, int):    Position of the character in the screen. In pixels.
            size (:tuple: int, int):    Size of every surface of the character. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            **aliases (:dict:): How each standarized action will be named in the loaded images.
        """
        LOG.log('DEBUG', "Initializing character ", id_, " of player ", my_player)
        super().__init__(id_, position, size, canvas_size, sprite_folder=sprites_path)
        self.aliases    = Character.__default_aliases.copy()
        self.aliases.update(aliases)
        self.my_master  = my_player
        self.state      = self.aliases['idle']
        self.index      = 0
        self.kills      = 0
        self.movements  = 0
    
    def get_paths(self, graph, distances, current_map, index, level_size, movement_restriction):
        """Gets all the possible paths for each cell (of a specific subclass) with this overloaded method.
        If the result is None, means that the paths for the restrictions of this Character were not requested before.
        (They are done only when requested). After that, they are saved in a LUT table for later use.
        Args:   
            graph (:obj: numpy.Matrix:boolean): Graph with all the directly connected cells (distance=1).
            distances (:obj: numpy:int):   Graph of distances between cells connected (without changing direction of the path between them).
            current_map (:dict: int, Cell): Current situation of the map, with all the enemies and allies.
            index (int):    Current cell of the Character, we don't want to return the entire destinies for each cell.
            level_size (int):   Number of cells per circumference. This is only used if its necessary to set the paths.
            movement_restriction (:obj: Restriction):   The movement restriction to which to get the possible destinies.
        Returns:
            (:list: tuple): List with all the possible paths to take if the Character is in the index cell.
                            Each path is composed by all the steps to take (all the cell indexes from start until destiny)."""
        result = Movements.get_movements(hash(movement_restriction))
        if not result:
            self.set_paths(graph, distances, movement_restriction, level_size)
            result = Movements.get_movements(hash(movement_restriction))
        paths = result.copy()
        i = 0
        while i < len(paths[index]):
            if current_map[paths[index][i][-1]].has_ally():
                del paths[index][i]
                i -= 1
            i += 1
        return result[index]
    
    def set_paths(self, graph, distances, level_size, movement_restriction):
        """Sets all the possible paths for each cell (of a specific subclass) with this overloaded method.
        Args:
            graph (:obj: numpy.Matrix:boolean): Graph with all the directly connected cells (distance=1).
            distances (:obj: numpy:int):    Graph of distances between cells connected (without changing direction).
            level_size (int):  Number of cell in one circumference.
            movement_restriction (:obj: Restriction):   The movement restriction to which to set the possible destinies."""
        Movements.set_movements(graph, distances, movement_restriction, level_size)

    def get_master(self):
        """Returns:
            (str): Player that owns this character."""
        return self.my_master

    def set_state(self, state):
        """Changes the current state of the character (The action that the char is performing).
        Args:
            state (str): New state to set."""
        state = state.lower()
        for key_alias, alias in self.aliases.items():
            if state in key_alias or key_alias in state or state in alias or alias in state:
                self.state  = self.aliases[key_alias]
                break
        for index in range (0, len(self.names)):
            if self.state in self.names[index].lower() or self.names[index].lower() in self.state:
                self.animation_index = index
                return True
        raise StateNotFoundException("Character doesn't have the state "+str(state))

    def animation_frame(self):
        """Does the animation between frames. Should only be called when the self.animation_delay is reached.
        Searchs in the list of sprites the following one of the current sprite, that matches with the state of the character."""
        index = self.animation_index
        while True:
            index=index+1 if index < (len(self.surfaces)-1) else 0  #going back to start
            if self.state in self.names[index].lower():
                self.animation_index = index
                break
            if index is self.animation_index:           #A complete loop with no matches, only one sprite of the action in self.state
                break

    def hitbox_action(self, command, value=-1):
        """Action performed when the character is interacted with.
        Unused rn.
        Args: etc."""
        #if  "mouse" in command and "sec" in command:        self.dec_index()
        #elif "mouse" in command and "first" in command:     self.inc_index()
        pass

    def set_selected(self, selected):
        """Set the current state of the character to 'pickup', since its being selected by the current player.
        Args:
            selected (boolean): True if the character is being selected by the player."""
        self.state=self.aliases['pickup'] if selected is True else self.aliases['idle']

    @staticmethod
    def parse_json_char_params(json_params):
        """Parse and complete the dict (in a json fashion) that contains all the customizable parameters of a all the characters.
        This gets called in factory.
        Args:
            json_params (:dict:):   All the parameters that can be modified on the characters of a player. Contains:
                                    The folder path of surfaces, the ammount and aliases of each subtype of character."""
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
        """Produces all the characters of a player. Even with this name, it doesn't follow the factory pattern.
        First of all, parses the input settings to avoid errors. After that, loads each character of each subtype
        in a separate thread, with the already parsed and corrected settings. When all the threads are finished, returns
        the characters (when all the threads join).
        Args:
            player_name (str):  Owning/Master player of this Character.
            sprite_size (:tuple: int, int): Size of every surface of the character. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            **character_settings (:dict:):  All the information for the creation of each subtype of character. Contains:
                                            Keys are the subtype of the specific character. Items are:
                                                                                            Path, Aliases, Ammount.
        Returns:
            (:list: Character): List containing all the characters requested by the player.
        """
        LOG.log('INFO', "----Factory, making ", player_name, " characters----")
        Character.parse_json_char_params(character_settings)
        characters  = pygame.sprite.Group()
        threads     = []

        for key in character_settings.keys():
            char_init = Pawn if 'pawn' in key else Wizard if 'wizard' in key\
            else Warrior if 'warrior' in key else Priestess if 'priestess' in key\
            else MatronMother if 'matron' in key else None
            #Actual loading
            threads.append(Character.__char_loader(char_init, characters, character_settings[key]['ammount'],\
                            player_name, player_name+key, (0, 0), sprite_size, canvas_size, character_settings[key]['path'],\
                            **character_settings[key]['aliases']))
        for t in threads:   t.join()        #Threading.join
        LOG.log('INFO', "----Factory, done making ", player_name, " characters----")
        return characters

    @staticmethod
    @run_async
    def __char_loader(char_class, result, count, *params, **kwparams):
        """Loads asynchronically characters of a specific subclass with its surfaces,
        Done async since its a pretty heavy process.
        Accepts sprite groups and lists as array of data to add the loaded characters.
        Args:
            char_class (:obj: class name):  Class name to call its constructor in here. No need for parenthesis, just the name.
                                            (Pawn, Priestess...).
            result (:obj: pygame.sprite.Group||list):   Array to which to add the loaded characters when the method ends.
                                                        We can't return the char directly since its loaded on a subthread.
            count (int):    Ammount of characters of the char_class that we want to create.
            *params (:obj:argument):    Parameters of the character constructor. Those are:
                                        id_, position, size, canvas_size, sprites_path
            **kwparams: (:obj: keywords):   Named parameters of the character constructor. Those are:
                                            **Aliases: 'idle', 'fight', etc. All the action aliases.
        Returns:
            (:obj: Threading.thread):   Thread loading the characters."""
        add_to_result = result.add if isinstance(result, pygame.sprite.Group) else result.append
        for _ in range (0, count):
            add_to_result(char_class(*params, **kwparams))

class Warrior(Character):
    """Warrior class. Inherits from Character.
    Warrior can move in 2 turns in 2 linked spaces (1 per turn). 
    This gives him a restriction of distance of 1 and 2 turns. (Its 2 right now, change this).
    General class attributes:    
        RESTRICTIONS (:obj: Restriction):   Restrictions that this type of character have in the movement.
        DEFAULT_PATH (str): Default path of the folder with the surfaces to initiate the sprite.
        DEFAULT_AMMOUNT (int):  Default ammount of this subtype of Character in a player. 
                                Not used directly, this is for the player to read from an above method.
    """
    RESTRICTIONS    = Restriction(max_dist=2)
    DEFAULT_PATH    = IMG_FOLDER+'\\Warrior'
    DEFAULT_AMMOUNT = 4

    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path, **aliases):
        """Warrior constructor. 
        Args:       
            my_player (str):    Owning/Master player of this Character.
            id_ (str):  Identifier/name of this Character.
            position (:tuple: int, int):    Position of the character in the screen. In pixels.
            size (:tuple: int, int):    Size of every surface of the character. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            **aliases (:dict:): How each standarized action will be named in the loaded images.
        """
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path, **aliases)
        
    def get_paths(self, graph, distances, current_map, index, level_size):
        """Gets all the possible paths for each cell for a Warrior type with his Restriction in movement.
        If the result is None, means that the paths for the restrictions of this Character were not requested before.
        (They are done only when requested). After that, they are saved in a LUT table for later use.
        Default RESTRICTION is: max distance = 2 #TODO Change this!
        Args:   
            graph (:obj: numpy.Matrix:boolean): Graph with all the directly connected cells (distance=1).
            distances (:obj: numpy:int):   Graph of distances between cells connected (without changing direction of the path between them).
            current_map (:dict: int, Cell): Current situation of the map, with all the enemies and allies.
            index (int):    Current cell of the Character, we don't want to return the entire destinies for each cell.
            level_size (int):   Number of cells per circumference. This is only used if its necessary to set the paths.
        Returns:
            (:list: tuple): List with all the possible paths to take if Warrior is in the index cell.
                            Each path is composed by all the steps to take (all the cell indexes from start until destiny).
        """
        return super().get_paths(graph, distances, current_map, index, level_size, Warrior.RESTRICTIONS)

class Wizard(Character):
    """Wizard class. Inherits from Character.
    Warrior can move in 1 turn in 3 linked spaces. 
    This gives him a restriction of distance of 3.
    General class attributes:    
        RESTRICTIONS (:obj: Restriction):   Restrictions that this type of character have in the movement.
        DEFAULT_PATH (str): Default path of the folder with the surfaces to initiate the sprite.
        DEFAULT_AMMOUNT (int):  Default ammount of this subtype of Character in a player. 
                                Not used directly, this is for the player to read from an above method.
    """
    RESTRICTIONS    = Restriction(max_dist=3)
    DEFAULT_PATH    = IMG_FOLDER+'\\Wizard'
    DEFAULT_AMMOUNT = 2

    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path, **aliases):
        """Wizard constructor. 
        Args:       
            my_player (str):    Owning/Master player of this Character.
            id_ (str):  Identifier/name of this Character.
            position (:tuple: int, int):    Position of the character in the screen. In pixels.
            size (:tuple: int, int):    Size of every surface of the character. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            **aliases (:dict:): How each standarized action will be named in the loaded images.
        """
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path, **aliases)

    def get_paths(self, graph, distances, current_map, index, level_size):
        """Gets all the possible paths for each cell for a Wizard type with his Restriction in movement.
        If the result is None, means that the paths for the restrictions of this Character were not requested before.
        (They are done only when requested). After that, they are saved in a LUT table for later use.
        Default RESTRICTION is: max distance = 3
        Args:   
            graph (:obj: numpy.Matrix:boolean): Graph with all the directly connected cells (distance=1).
            distances (:obj: numpy:int):   Graph of distances between cells connected (without changing direction of the path between them).
            current_map (:dict: int, Cell): Current situation of the map, with all the enemies and allies.
            index (int):    Current cell of the Character, we don't want to return the entire destinies for each cell.
            level_size (int):   Number of cells per circumference. This is only used if its necessary to set the paths.
        Returns:
            (:list: tuple): List with all the possible paths to take if Wizard is in the index cell.
                            Each path is composed by all the steps to take (all the cell indexes from start until destiny).
        """
        return super().get_paths(graph, distances, current_map, index, level_size, Wizard.RESTRICTIONS)

class Priestess(Character):
    """Priestess class. Inherits from Character.
    Priestess can move in 1 turn along a circumference or inter-path. Distance is not an issue.
    It is impeded by intervening allied characters tho. 
    This gives her a restriction of distance of 0. (No restrictions in distance).
    This gives her the restriction of move_only_along_index (True).
    This gives her the restriction of move_only_along_level (True).
    In short, can only move to directly connected cells (Without change in direction mid-path).
    General class attributes:    
        RESTRICTIONS (:obj: Restriction):   Restrictions that this type of character have in the movement.
        DEFAULT_PATH (str): Default path of the folder with the surfaces to initiate the sprite.
        DEFAULT_AMMOUNT (int):  Default ammount of this subtype of Character in a player. 
                                Not used directly, this is for the player to read from an above method.
    """
    RESTRICTIONS    = Restriction(max_dist=0, move_along_lvl=True, move_along_index=True)
    DEFAULT_PATH    = IMG_FOLDER+'\\Priestess'
    DEFAULT_AMMOUNT = 2

    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path, **aliases):
        """Priestess constructor. 
        Args:       
            my_player (str):    Owning/Master player of this Character.
            id_ (str):  Identifier/name of this Character.
            position (:tuple: int, int):    Position of the character in the screen. In pixels.
            size (:tuple: int, int):    Size of every surface of the character. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            **aliases (:dict:): How each standarized action will be named in the loaded images.
        """
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path, **aliases)

    def get_paths(self, graph, distances, current_map, index, level_size):
        """Gets all the possible paths for each cell for a Priestess type with her Restriction in movement.
        If the result is None, means that the paths for the restrictions of this Character were not requested before.
        (They are done only when requested). After that, they are saved in a LUT table for later use.
        Default RESTRICTION is: max distance = 0, move_only_along_index = True,  move_only_along_level = True.
        Args:   
            graph (:obj: numpy.Matrix:boolean): Graph with all the directly connected cells (distance=1).
            distances (:obj: numpy:int):   Graph of distances between cells connected (without changing direction of the path between them).
            current_map (:dict: int, Cell): Current situation of the map, with all the enemies and allies.
            index (int):    Current cell of the Character, we don't want to return the entire destinies for each cell.
            level_size (int):   Number of cells per circumference. This is only used if its necessary to set the paths.
        Returns:
            (:list: tuple): List with all the possible paths to take if Priestess is in the index cell.
                            Each path is composed by all the steps to take (all the cell indexes from start until destiny).
        """
        return super().get_paths(graph, distances, current_map, index, level_size, Priestess.RESTRICTIONS)

class Pawn(Character):
    """Pawn class. Inherits from Character.
    Pawn can move in 1 turn a distance of 1. In short, can only move to immediate cells.
    This movement has to bring him closer to an enemy in the same circumference or interpath as him.
    This restriction of going closer to an enemy is not in effect if there is an ally in the middle of the path to said enemy.
    This gives him a restriction of distance of 1.

    General class attributes:    
        RESTRICTIONS (:obj: Restriction):   Restrictions that this type of character have in the movement.
        CHECK_ENEMIES (:obj: Restriction):  Restrictions that this character have when checking for enemies in the paths.
                                            This way it checks for enemies in the same circumference or interpath and saves
                                            the distance, to compare with the possible destinies.
        DEFAULT_PATH (str): Default path of the folder with the surfaces to initiate the sprite.
        DEFAULT_AMMOUNT (int):  Default ammount of this subtype of Character in a player. 
                                Not used directly, this is for the player to read from an above method.
    """
    RESTRICTIONS    = Restriction()
    CHECK_ENEMIES   = Restriction(max_dist=0, move_along_lvl=True, move_along_index=True)
    DEFAULT_PATH    = IMG_FOLDER+'\\Pawn'
    DEFAULT_AMMOUNT = 8

    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path, **aliases):
        """Pawn constructor. 
        Args:       
            my_player (str):    Owning/Master player of this Character.
            id_ (str):  Identifier/name of this Character.
            position (:tuple: int, int):    Position of the character in the screen. In pixels.
            size (:tuple: int, int):    Size of every surface of the character. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            **aliases (:dict:): How each standarized action will be named in the loaded images.
        """
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path, **aliases)

    def get_paths(self, graph, distances, current_map, index, level_size):
        """Gets all the possible paths for each cell for a Pawn type with his Restriction in movement.
        If the result is None, means that the paths for the restrictions of this Character were not requested before.
        (They are done only when requested). After that, they are saved in a LUT table for later use.
        Default RESTRICTION is: max distance = 1, have to move closer to enemies in same level or interpath,
                                except of there is an ally in the middle.
        Args:   
            graph (:obj: numpy.Matrix:boolean): Graph with all the directly connected cells (distance=1).
            distances (:obj: numpy:int):   Graph of distances between cells connected (without changing direction of the path between them).
            current_map (:dict: int, Cell): Current situation of the map, with all the enemies and allies.
            index (int):    Current cell of the Character, we don't want to return the entire destinies for each cell.
            level_size (int):   Number of cells per circumference. This is only used if its necessary to set the paths.
        Returns:
            (:list: tuple): List with all the possible paths to take if Pawn is in the index cell.
                            Each path is composed by all the steps to take (all the cell indexes from start until destiny).
        """
        unfiltered_paths = super().get_paths(graph, distances, current_map, index, level_size, Pawn.CHECK_ENEMIES)
        results = []
        enemies = {}
        #print(unfiltered_paths) TODO delete
        for path in unfiltered_paths:
            #If the destiny has an enemy and there is no ally in the middle. Those don't need to be checked again
            if current_map[path[-1]].has_enemy(): #Checking if in the end of this path tehre is an enemy
                if not any(current_map[path[i]].has_ally() for i in range(1, len(path)-1)): #Checking if in the middle steps there is an ally
                    enemies[path[-1]] = distances[index][path[-1]]  #Distance to the enemy. The key is the destiny index
        #Now, we compare the enemies distance to those that we would have in the 2-4 possible positions
        destinies = super().get_paths(graph, distances, current_map, index, level_size, Pawn.RESTRICTIONS)
        if len(enemies) > 0: #If there is an enemy in any of the direct paths.
            for new_path in destinies:
                for enemy_index, enemy_dist in enemies.items(): #We will check the new distances to enemies in each of the destinies
                    if distances[new_path[-1]][enemy_index] < enemy_dist:  
                        results.append((index, new_path[-1]))
                        break   #breaking the first loop
        else:
            #print("NOT ENEMIES FOUND IN THE PROXIMITIES") TODO delete
            for new_path in destinies:
                results.append((index, new_path[-1])) #Copying herethe paths because I dont want to modify tuples from gods know where.
        return results
            
class MatronMother(Character):
    """MatronMother class. Inherits from Character.
    Pawn can move in 1 turn a distance of 1. In short, can only move to immediate cells.
    There are no more restrictions. This gives her a restriction of distance of 1.

    General class attributes:    
        RESTRICTIONS (:obj: Restriction):   Restrictions that this type of character have in the movement.
        CHECK_ENEMIES (:obj: Restriction):  Restrictions that this character have when checking for enemies in the paths.
                                            This way it checks for enemies in the same circumference or interpath and saves
                                            the distance, to compare with the possible destinies.
        DEFAULT_PATH (str): Default path of the folder with the surfaces to initiate the sprite.
        DEFAULT_AMMOUNT (int):  Default ammount of this subtype of Character in a player. 
                                Not used directly, this is for the player to read from an above method.
    """
    RESTRICTIONS    = Restriction()
    DEFAULT_PATH    = IMG_FOLDER+'\\Matron_Mother'
    DEFAULT_AMMOUNT = 1

    def __init__(self, my_player, id_, position, size, canvas_size, sprites_path, **aliases):
        """MatronMother constructor. 
        Args:       
            my_player (str):    Owning/Master player of this Character.
            id_ (str):  Identifier/name of this Character.
            position (:tuple: int, int):    Position of the character in the screen. In pixels.
            size (:tuple: int, int):    Size of every surface of the character. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            **aliases (:dict:): How each standarized action will be named in the loaded images.
        """
        super().__init__(my_player, id_, position, size, canvas_size, sprites_path, **aliases)
        #self.movement   = Restriction(bypass_enemies=True)

    def get_paths(self, graph, distances, current_map, index, level_size):
        """Gets all the possible paths for each cell for a MatronMother type with her Restriction in movement.
        If the result is None, means that the paths for the restrictions of this Character were not requested before.
        (They are done only when requested). After that, they are saved in a LUT table for later use.
        Default RESTRICTION is: max distance = 0, move_only_along_index = True,  move_only_along_level = True.
        Args:   
            graph (:obj: numpy.Matrix:boolean): Graph with all the directly connected cells (distance=1).
            distances (:obj: numpy:int):   Graph of distances between cells connected (without changing direction of the path between them).
            current_map (:dict: int, Cell): Current situation of the map, with all the enemies and allies.
            index (int):    Current cell of the Character, we don't want to return the entire destinies for each cell.
            level_size (int):   Number of cells per circumference. This is only used if its necessary to set the paths.
        Returns:
            (:list: tuple): List with all the possible paths to take if MatronMoter is in the index cell.
                            Each path is composed by all the steps to take (all the cell indexes from start until destiny).
        """
        return super().get_paths(graph, distances, current_map, index, level_size, MatronMother.RESTRICTIONS)