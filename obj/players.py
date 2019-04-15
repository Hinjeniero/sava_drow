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
        ↑HolyChampion
--------------------------------------------"""

__all__ = ["Player", "Character", "Warrior", "Wizard", "Priestess", "Pawn", "MatronMother", "HolyChampion"]
__version__ = '0.9'
__author__ = 'David Flaity Pardo'

#Python libraries
import pygame
import uuid
from os import listdir
from os.path import isfile, join, dirname
#Selfmade libraries
from settings import PATHS, CHARACTERS
from obj.sprite  import AnimatedSprite, TextSprite
from obj.ui_element import InfoBoard
from obj.paths import Restriction, Movements
from obj.utilities.exceptions import BadCharacterInitException, StateNotFoundException, SwapFailedException
from obj.utilities.resizer import Resizer
from obj.utilities.logger import Logger as LOG
from obj.utilities.decorators import run_async
from obj.utilities.utility_box import UtilityBox
from obj.utilities.surface_loader import no_size_limit

class Player(object):
    """Player class. Each player has a name, some characters and his own turn.
    Attributes:
        uuid (int): Unique identifier of this player.
        name (str): Name of the player.
        order (int):Order of arrival. A numerical identifier, if you prefer.
        characters (:obj: pygame.sprite.Group): Group of AnimatedSprites that contains all the
                                                different characters that belong to the player.
        infoboard (:obj: InfoBoard):    UiElement subclass. A graphic element that shows all the information
                                        of the player. To be drawn when is the player's turn.
        turn (int): Current turn of this player.
        kills (int):Number of kills of this player (Captured enemy characters).
        movements (int):    Number of movements of this player across the board (Sum of all the characters).
        corpses (list->Character):  The captured characters. Saved to use the information on captures and such.
        dead (boolean): True if this player has lost the essential characters, and cannot continue playing. False otherwise.
    """
    def __init__(self, name, order, sprite_size, canvas_size, human=True, infoboard=None, obj_uuid=None, empty=False, avatar=None, **character_params):
        """Player constructor.
        Args:
            name (str): Name of the player.
            order (int):    Order of arrival. A numerical identifier, if you prefer.
            sprite_size (:tuple: int, int): Size of the image of the characters. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            infoboard (:obj: Infoboard, default=None):  Infoboard of the player. It's shown through the game.
            uuid (int, default=None):   Unique id of this player. If it's not supplied, it will be generated later.
            empty (boolean, default=False): True if we create this player without characters (They will be added later).
                                            In this case the character_params will not be used, and are not necessary.
            **character_params (:dict:):    Contains the more specific parameters to create the characters.
                                            Ammount of each type of char, name of their actions, and their folder paths."""
        self.uuid       = obj_uuid if obj_uuid else uuid.uuid1().int
        self.human      = human
        self.avatar     = None
        self.name       = name
        self.order      = order
        self.characters = None
        self.infoboard  = None  #Created in generate
        self.turn       = 0
        self.kills      = 0
        self.movements  = 0
        self.throws     = 0
        self.corpses    = []    #Contains dead chars of the other players.
        self.fallen     = []    #Contains my captured/killed pieces
        self.dead       = False #If the player has already lost
        Player.generate(self, sprite_size, canvas_size, empty, **character_params)

    @staticmethod
    def generate(self, sprite_size, canvas_size, empty, **character_params):
        """Called at the end of the constructor. Generates the uuid, the characters, and the infoboard
        (Following the input parameters, and if it's needed).
        Args:
            self (:obj: Player):    Player that needs to have its attributes generated.
            sprite_size (:tuple:-> int, int): Size of the image of the characters. In pixels.
            canvas_size (:tuple:-> int, int): Resolution of the screen. In pixels.
            empty (boolean):    True if we want to generate the player's characters too.
            **character_params (:dict:):Contains the more specific parameters to create the characters.
                                        Ammount of each type of char, name of their actions, and their folder paths.
            """
        if self.avatar:
            pass    #TODO THIS SHIT
        if not empty:
            self.characters = Character.factory(self.name, self.uuid, sprite_size, canvas_size, **character_params)
        else:
            self.characters = pygame.sprite.OrderedUpdates()
        self.generate_infoboard(canvas_size)

    @no_size_limit
    def generate_infoboard(self, resolution):
        infoboard = InfoBoard(self.name+'_infoboard', 0, (0, 0), (0.15*resolution[0], resolution[1]),\
                            resolution, texture=PATHS.INFOBOARD, keep_aspect_ratio = False, cols=6)
        cols = infoboard.get_cols()
        if self.avatar:
            pass
        else:
            infoboard.add_text_element('initial_padding', '', cols)
        infoboard.add_text_element('player_name', self.name, cols-2)   #Player name
        infoboard.add_text_element('player_number', 'id: '+str(self.order+1), cols-2)   #Player order
        infoboard.add_text_element('player_chars', 'Total characters: '+str(len(self.characters)), cols)   #Player total ammount of chars
        infoboard.add_text_element('player_kills', 'Total kills: '+str(self.kills), cols)
        infoboard.add_text_element('player_movements', 'Total movements: '+str(self.movements), cols)
        self.infoboard = infoboard

    def register_movement(self, character):
        """Saves the movements into the stats of the player and character.
        Args:
            character (:obj: Character):    Character that did the movements."""
        self.movements += 1
        self.get_character(character).movements += 1

    def add_kill(self, corpse, killer):
        """Adds a kill to the player and to the character that did the kill/capture.
        Also saves the captured/killed character, just in case that we need to show some stats about it later.
        Args:
            corpse (:obj: Character):   Character that was killed/captured.
            killer (:obj: Character):   Character that did the kill/capture."""
        self.kills += 1
        self.corpses.append(corpse)
        self.get_character(killer).kills += 1

    def pause_characters(self):
        """Set the state of all the characters of this player to 'stop'. Depending on the sprites, this
        will set them to a grayscale animation, to simbolize that they are 'stopped'.
        Also sets the active attribute of all of them to False."""
        for character in self.characters:
            character.set_state("stop")
            character.set_active(False)

    def unpause_characters(self):
        """Set the state of all the characters of this player to 'idle'. Depending on the sprites, this
        will set them to a full color animation, to simbolize that they are in movement and active again.
        Also sets the active attribute of all of them to True."""
        for character in self.characters:
            character.set_state("idle")
            character.set_active(True)

    def get_character(self, character):
        """Tries to get a character from this player.
        Args:
            character (:obj: Character):    Character that is searched for in this player.
        Returns:
            (Character||None):  Returns the asked character if it's found, None otherwise."""
        for char in self.characters:
            if character is char:
                return char

    def update(self):
        """Updates the infoboard of the player with the current stats."""
        self.infoboard.get_sprite('name').set_text(self.name)   #The name can change in infoboard
        self.infoboard.get_sprite('chars').set_text('Total characters: '+str(len(self.characters)))
        self.infoboard.get_sprite('movements').set_text('Total movements: '+str(self.movements))
        self.infoboard.get_sprite('kills').set_text('Total kills: '+str(self.kills))
        self.infoboard.regenerate_image()

    def draw(self, surface):
        """Draws the infoboard of the player containing all of the current stats.
        Args:
            surface (:obj: pygame.Surface): Surface to draw the infoboard onto."""
        self.infoboard.draw(surface)

    def set_resolution(self, resolution):
        """Resizes the infoboard and the player's characters.
        Args:
            resolution (tuple -> int, int): New resolution of the player."""
        if self.infoboard:
            self.infoboard.set_canvas_size(resolution)
        for char in self.characters:
            char.set_canvas_size(resolution)

    def revive_char(self, dead_char, sacrifice):
        if dead_char in self.fallen and self.characters.has(sacrifice):
            self.characters.add(dead_char)
            self.characters.remove(sacrifice)
            self.fallen.append(sacrifice)
            self.fallen.remove(dead_char)
        else:
            raise SwapFailedException("Either the revived char or the killed orc weren't found in this player")

    def has_char(self, char):
        """Checks if a character exists/is contained in this player.
        Args:
            char (:obj: Character): Character to search for.
        Returns:
            (boolean):  True if the character is within this player, False otherwise."""
        return self.characters.has(char)

    def remove_char(self, char):
        """Removes the input character from the player. Obviously, if it's not found in this player
        this doesn't remove anything.
        If its founf and after removing it, a check is done in this player to see if it still has an
        essential piece/character. If it doesn't, the dead flag is set to True..
        Args:
            char (:obj: Character): Character to be found and removed."""
        if self.has_char(char):
            self.characters.remove(char)
            self.fallen.append(char)
            self.update()
            if char.essential:  #If the killed one was a matron mother or a promoted/bonus char 
                for character in self.characters:
                    if character.essential:
                        return
                self.dead = True
    
    def has_lost(self):
        """Returns:
            (boolean): True if the dead flag is True, False otherwise."""
        return self.dead

    def most_used_class(self):
        """Returns the current most used class of this player, by total number of movements
        across all the characters belonging to the same class.
        Returns:
            ()"""
        if len(self.characters) > 0:
            classes = {}
            for char in self.characters:
                try:
                    classes[char.get_type()] += char.movements
                except KeyError:
                    classes[char.get_type()] = char.movements
            subclass = max(classes, key=lambda key: classes[key])
            return (subclass, classes[subclass])

    def best_class(self):
        """Returns the current best class of this player, by total ammount of kills
        across all the characters belonging to the same class.
        Returns:
            ()"""
        if len(self.characters) > 0:
            classes = {}
            for char in self.characters:
                try:
                    classes[char.get_type()] += char.kills
                except KeyError:
                    classes[char.get_type()] = char.kills
            subclass = max(classes, key=lambda key: classes[key])
            return (subclass, classes[subclass])

    def most_used_character(self):#TODO same shit as below
        """Returns ths player character with the most movements.
        Returns:
            ()"""
        if len(self.characters) > 0:
            char = max(self.characters, key=lambda char: char.movements)
            return char.id+" - "+str(char.movements)

    def best_character(self):   #TODO Return name or something
        """Returns this player characther with the most kills.
        Returns:
            ()"""
        if len(self.characters) > 0:
            char = max(self.characters, key=lambda char: char.kills)
            return char.id+" - "+str(char.kills)

    def get_stats(self):
        """Builds a dict with the current information and state of the player.
        Returns:
            (Dict):   Dict with all the player current info."""
        return {'Player name': self.name,
                'Total kills': str(self.kills),
                'Total movs': str(self.movements),
                'Best class (K)': str(self.best_class()),
                'Best char (K)': self.best_character(),
                'Most used class (M)': str(self.most_used_class()),
                'Most used char (M)': self.most_used_character()}        

    def stats_json(self):
        """Builds a json with the current information and state of the player.
        The main key is 'stats', followed by a list of tuples with the schema (key(str), value(anything))
        Returns:
            (Dict->List->Tuples->(str, any)):   JSON with all the player current info."""
        return {'stats':[('Player name: ', self.name),
                        ('Player number: ', str(self.order)),
                        ('Total kills: ', str(self.kills)),
                        ('Total movements: ', str(self.movements)),
                        ('Best class (kills): ', str(self.best_class())),
                        ('Best character (kills): ', self.best_character()),
                        ('Most used class (movements): ', str(self.most_used_class())),
                        ('Most used character (movements): ', self.most_used_character())]}

    def json(self):
        """Builds a JSON with the player most essential info.
        Returns:
            (Dict): JSON with the player essential info, like uuid, name, order, etc."""
        return  {'uuid': self.uuid,           
                'name': self.name,
                'order': self.order,
                'turn': self.turn,
                'dead': self.dead}

class Character(AnimatedSprite):
    """Character class. Inherits from AnimatedSprite.
    Each moving character is a subclass or class related to this one.
    Implements logic and graphics that allows it to have different states (or actions),
    different possible paths based on the same map (Due to the specific Restriction on movement),
    and to belong to different players.
    General class attributes:
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
    def __init__(self, player_uuid, id_, position, size, canvas_size, sprites_path, obj_uuid=None, aliases={}, **params):
        """Character constructor.
        Args:
            my_player (str):    Owning/Master player of this Character.
            position (:tuple: int, int):    Position of the character in the screen. In pixels.
            size (:tuple: int, int):    Size of every surface of the character. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            **aliases (:dict:): How each standarized action will be named in the loaded images.
        """
        params['hover_surfaces'] = True
        super().__init__(id_, position, size, canvas_size, sprite_folder=sprites_path, **params)
        self.uuid       = obj_uuid if obj_uuid else uuid.uuid1().int
        self.aliases    = CHARACTERS.DEFAULT_ALIASES.copy()
        self.owner_uuid = player_uuid
        self.state      = None  #Generated in Character.generate()
        self.index      = 0
        self.kills      = 0
        self.kill_sprite= None
        self.movements  = 0
        self.mov_sprite = None
        self.essential  = False
        self.can_kill   = True
        self.can_die    = True
        self.turns      = 1
        self.rank       = 0
        self.order      = 0
        self.upgradable = False
        self.current_pos= 0
        self.value      = 1
        Character.generate(self, aliases)

    @staticmethod
    def generate(self, aliases):
        self.aliases.update(aliases)
        self.state = self.aliases['idle']
        self.update_info_sprites()

    def set_size(self, size, update_rects=True):
        super().set_size(size, update_rects=update_rects)
        self.update_info_sprites()

    def update_info_sprites(self):
        self.kill_sprite = TextSprite('kills', (0, 0), self.rect.size, self.resolution,\
                                    'K:'+str(self.kills))
        self.movm_sprite = TextSprite('movements', (0, 0), self.rect.size, self.resolution,\
                                    'M:'+str(self.movements))
        self.update_info_positions()

    def update_info_positions(self):
        self.kill_sprite.set_position((self.rect.x, self.rect.y-self.kill_sprite.rect.height))
        self.movm_sprite.set_position((self.rect.x+self.kill_sprite.rect.width, self.rect.y-self.movm_sprite.rect.height))

    def get_type(self):
        """This to overload."""
        return 'character'

    def draw(self, surface, offset=None):
        super().draw(surface, offset=offset)
        if self.hover:
            self.kill_sprite.draw(surface, offset=offset)
            self.movm_sprite.draw(surface, offset=offset)

    def json(self, cell_index=None):
        """This to share in the online variant and drop in the same positions."""
        response = {'uuid': self.uuid,
                    'id': self.id,
                    'player': self.owner_uuid,
                    'type': self.get_type()}
        if cell_index:
            response['cell'] = cell_index    
        return response

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
        paths = []
        #print("RSEULTS INDEX ")
        #print(result[index])
        for path in result[index]:
            if current_map[path[-1]].accessible() and not current_map[path[-1]].has_ally():
                paths.append(path)
        #print("AFTER CHECKING FOR ALLIES ")
        #print(paths)
        return paths
    
    def set_cell(self, cell):
        self.set_center(cell.center)
        self.current_pos = cell.get_real_index()
        self.update_info_positions()

    def promote(self):
        self.essential = True

    def demote(self):
        self.essential = False

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
        return self.owner_uuid

    def set_state(self, state):
        """Changes the current state of the character (The action that the char is performing).
        Args:
            state (str): New state to set."""
        if any(state.lower() in name.lower() for name in self.names)\
        or any(name.lower() in state.lower() for name in self.names):  #If the current state has any sprite
            state = state.lower()
            for key_alias, alias in self.aliases.items():
                if state in key_alias or key_alias in state or state in alias or alias in state:
                    self.state  = self.aliases[key_alias]
                    break
            for index in range (0, len(self.names)):
                if self.state in self.names[index].lower() or self.names[index].lower() in self.state:
                    self.animation_index = index
                    return True
            raise StateNotFoundException("Character doesn't have the state "+str(state))    #Should never reach here

    def animation_frame(self):
        """Does the animation between frames. Should only be called when the self.animation_delay is reached.
        Searchs in the list of sprites the following one of the current sprite, that matches with the state of the character."""
        old_index = self.animation_index
        while True:
            super().animation_frame()
            if self.state.lower() in self.names[self.animation_index].lower()\
            or self.names[self.animation_index].lower() in self.state.lower()\
            or self.animation_index == old_index:
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
        character_types = ['pawn', 'warrior', 'wizard', 'priestess', 'matron_mother', 'holy_champion']
        ammounts        = {'pawn': Pawn.DEFAULT_AMMOUNT, 'warrior': Warrior.DEFAULT_AMMOUNT, 'wizard': Wizard.DEFAULT_AMMOUNT,\
                            'priestess': Priestess.DEFAULT_AMMOUNT, 'matron_mother': MatronMother.DEFAULT_AMMOUNT,\
                            'holy_champion': HolyChampion.DEFAULT_AMMOUNT}
        img_paths       = {'pawn': Pawn.DEFAULT_PATH, 'warrior': Warrior.DEFAULT_PATH, 'wizard': Wizard.DEFAULT_PATH,\
                            'priestess': Priestess.DEFAULT_PATH, 'matron_mother': MatronMother.DEFAULT_PATH,\
                            'holy_champion': HolyChampion.DEFAULT_PATH}
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
    def factory(player_name, player_uuid, sprite_size, canvas_size, **character_settings):
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
        characters  = []
        threads     = []

        for key in character_settings.keys():
            #Character.generate_char()
            char_init = Character.get_constructor_by_key(key)
            #Actual loading
            threads.append(Character.__char_loader(char_init, characters, character_settings[key]['ammount'],\
                            player_uuid, player_name+'_'+key, (0, 0), sprite_size, canvas_size, character_settings[key]['path']))
                            #player_uuid,      id_,         position,    size,      canvas_size, sprites_path
        for end_event in threads:   
            end_event.wait()        #Threading.join
        LOG.log('INFO', "----Factory, done making ", player_name, " characters----")
        characters.sort(key=lambda char: (char.rank, char.order), reverse=True)  #To drop first the most important characters
        return pygame.sprite.OrderedUpdates(*characters)

    @staticmethod
    def get_constructor_by_key(key):
        return Pawn if 'pawn' in key else Wizard if 'wizard' in key\
        else Warrior if 'warrior' in key else Priestess if 'priestess' in key\
        else MatronMother if 'matron' in key else HolyChampion if 'champ' in key\
        else None
    
    @staticmethod
    def get_sprite_folder_by_key(key):
        return Pawn.DEFAULT_PATH if 'pawn' in key else Wizard.DEFAULT_PATH if 'wizard' in key\
        else Warrior.DEFAULT_PATH if 'warrior' in key else Priestess.DEFAULT_PATH if 'priestess' in key\
        else MatronMother.DEFAULT_PATH if 'matron' in key else HolyChampion.DEFAULT_PATH if 'champ' in key\
        else None

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
            if char_class:
                add_to_result(char_class(*params, **kwparams))

    def __hash__(self):
        return hash((self.uuid, self.owner_uuid, self.id))

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
    RESTRICTIONS    = Restriction()
    DEFAULT_PATH    = PATHS.WARRIOR
    DEFAULT_AMMOUNT = 4

    def __init__(self, player_uuid, id_, position, size, canvas_size, sprites_path, obj_uuid=None, **params):
        """Warrior constructor. 
        Args:       
            my_player (str):    Owning/Master player of this Character.
            id_ (str):  Identifier/name of this Character.
            position (:tuple: int, int):    Position of the character in the screen. In pixels.
            size (:tuple: int, int):    Size of every surface of the character. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            **aliases (:dict:): How each standarized action will be named in the loaded images.
        """
        super().__init__(player_uuid, id_, position, size, canvas_size, sprites_path, aliases=CHARACTERS.WARRIOR_ALIASES, obj_uuid=obj_uuid, **params)
        self.turns  = 2
        self.rank   = 1
        self.order  = 1
        self.value  = 3
        
    def get_paths(self, graph, distances, current_map, index, level_size):
        """Gets all the possible paths for each cell for a Warrior type with his Restriction in movement.
        If the result is None, means that the paths for the restrictions of this Character were not requested before.
        (They are done only when requested). After that, they are saved in a LUT table for later use.
        Default RESTRICTION is: max distance = 1, turns=2
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
    
    def get_type(self):
        """This to overload."""
        return 'warrior'

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
    DEFAULT_PATH    = PATHS.WIZARD
    DEFAULT_AMMOUNT = 2

    def __init__(self, player_uuid, id_, position, size, canvas_size, sprites_path, obj_uuid=None, **params):
        """Wizard constructor. 
        Args:       
            my_player (str):    Owning/Master player of this Character.
            id_ (str):  Identifier/name of this Character.
            position (:tuple: int, int):    Position of the character in the screen. In pixels.
            size (:tuple: int, int):    Size of every surface of the character. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            **aliases (:dict:): How each standarized action will be named in the loaded images.
        """
        super().__init__(player_uuid, id_, position, size, canvas_size, sprites_path, aliases=CHARACTERS.WIZARD_ALIASES, obj_uuid=obj_uuid, **params)
        self.rank   = 1
        self.order  = 2
        self.value  = 6

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

    def get_type(self):
        """This to overload."""
        return 'wizard'

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
    DEFAULT_PATH    = PATHS.PRIESTESS
    DEFAULT_AMMOUNT = 2

    def __init__(self, player_uuid, id_, position, size, canvas_size, sprites_path, obj_uuid=None, **params):
        """Priestess constructor. 
        Args:       
            my_player (str):    Owning/Master player of this Character.
            id_ (str):  Identifier/name of this Character.
            position (:tuple: int, int):    Position of the character in the screen. In pixels.
            size (:tuple: int, int):    Size of every surface of the character. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            **aliases (:dict:): How each standarized action will be named in the loaded images.
        """
        super().__init__(player_uuid, id_, position, size, canvas_size, sprites_path, aliases=CHARACTERS.PRIESTESS_ALIASES, obj_uuid=obj_uuid, **params)
        self.rank   = 1
        self.order  = 3
        self.value  = 5

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
        unfiltered_paths = super().get_paths(graph, distances, current_map, index, level_size, Priestess.RESTRICTIONS)
        results = []
        for path in unfiltered_paths:
            if not any(current_map[path[i]].has_ally() or current_map[path[i]].has_enemy() for i in range(1, len(path)-1)):
                results.append(path)
        #print("AFTER CHECKING FOR allies and enemies in the middle of the path ")
        #print(results)
        return results

    def get_type(self):
        """This to overload."""
        return 'priestess'

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
    DEFAULT_PATH    = PATHS.PAWN
    DEFAULT_AMMOUNT = 8

    def __init__(self, player_uuid, id_, position, size, canvas_size, sprites_path, obj_uuid=None, **params):
        """Pawn constructor. 
        Args:       
            my_player (str):    Owning/Master player of this Character.
            id_ (str):  Identifier/name of this Character.
            position (:tuple: int, int):    Position of the character in the screen. In pixels.
            size (:tuple: int, int):    Size of every surface of the character. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            **aliases (:dict:): How each standarized action will be named in the loaded images.
        """
        super().__init__(player_uuid, id_, position, size, canvas_size, sprites_path, aliases=CHARACTERS.PAWN_ALIASES, obj_uuid=obj_uuid, **params)
        self.upgradable = True

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
        for path in unfiltered_paths:
            enemies.update(self.get_enemies_distances(current_map, path))
        #Now, we compare the enemies distance to those that we would have in the 2-4 possible positions
        destinies = super().get_paths(graph, distances, current_map, index, level_size, Pawn.RESTRICTIONS)
        if len(enemies) == 0:   #If no enemies detected, every path is possible
            return destinies
        #If enemies detected
        for new_path in destinies:  #For each destiny possible for the pawn
            if new_path[-1] in enemies.keys():  #If the enemy is in the immediate cell
                results.append(new_path)
                continue
            unfiltered_new_paths = super().get_paths(graph, distances, current_map, new_path[-1], level_size, Pawn.CHECK_ENEMIES)   #We get the unfiltered paths that may end in enemies
            for path in unfiltered_new_paths:   #For each one of those
                if path[-1] in enemies.keys():  #We check if ends in an enemy of the old position, then we compare distances
                    if (len(path)-1) < enemies[path[-1]]:
                        results.append(new_path)
                        break
        return results

    def get_enemies_distances(self, current_map, path):
        #If the destiny has an enemy and there is no ally in the middle. Those don't need to be checked again
        enemies = {}
        if current_map[path[-1]].has_enemy(): #Checking if in the end of this path tehre is an enemy
            if not any(current_map[path[i]].has_ally() or current_map[path[i]].has_enemy() for i in range(1, len(path)-1)): #Checking if in the middle steps there is an ally
                enemies[path[-1]] = len(path)-1
        return enemies

    def get_type(self):
        """This to overload."""
        return 'pawn'

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
    DEFAULT_PATH    = PATHS.MATRONMOTHER
    DEFAULT_AMMOUNT = 1

    def __init__(self, player_uuid, id_, position, size, canvas_size, sprites_path, obj_uuid=None, **params):
        """MatronMother constructor. 
        Args:       
            my_player (str):    Owning/Master player of this Character.
            id_ (str):  Identifier/name of this Character.
            position (:tuple: int, int):    Position of the character in the screen. In pixels.
            size (:tuple: int, int):    Size of every surface of the character. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            **aliases (:dict:): How each standarized action will be named in the loaded images.
        """
        super().__init__(player_uuid, id_, position, size, canvas_size, sprites_path, aliases=CHARACTERS.MATRONMOTHER_ALIASES, obj_uuid=obj_uuid, **params)
        self.essential  = True
        self.rank       = 2
        self.order      = 5
        self.value      = 10

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

    def get_type(self):
        """This to overload."""
        return 'matron_mother'

class HolyChampion(Character):
    """HolyChampion class. Inherits from Character.
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
    #RESTRICTIONS    = Restriction() Don't have restrictions on its own, its a mix of other chars
    DEFAULT_PATH    = PATHS.HOLYCHAMPION
    DEFAULT_AMMOUNT = 1

    def __init__(self, player_uuid, id_, position, size, canvas_size, sprites_path, obj_uuid=None, **params):
        """HolyChampion constructor. 
        Args:       
            my_player (str):    Owning/Master player of this Character.
            id_ (str):  Identifier/name of this Character.
            position (:tuple: int, int):    Position of the character in the screen. In pixels.
            size (:tuple: int, int):    Size of every surface of the character. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            **aliases (:dict:): How each standarized action will be named in the loaded images.
        """
        super().__init__(player_uuid, id_, position, size, canvas_size, sprites_path, aliases=CHARACTERS.HOLYCHAMPION_ALIASES, obj_uuid=obj_uuid, **params)
        self.essential  = True
        self.rank       = 2
        self.order      = 4
        self.can_kill   = False
        self.can_die    = False
        self.value      = 4

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
        results = []
        results.extend(super().get_paths(graph, distances, current_map, index, level_size, Wizard.RESTRICTIONS))
        priestess_paths = super().get_paths(graph, distances, current_map, index, level_size, Priestess.RESTRICTIONS)
        for path in priestess_paths:
            if not any(current_map[path[i]].has_ally() or current_map[path[i]].has_enemy() for i in range(1, len(path)-1))\
            and path not in results:
                results.append(path)
        return results

    def get_type(self):
        """This to overload."""
        return 'holy_champion'