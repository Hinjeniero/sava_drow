"""--------------------------------------------
board_generator module.
Have the following classes:
    BoardGenerator
--------------------------------------------"""
__all__ = ['BoardGenerator']
__version__ = '1.0'
__author__ = 'David Flaity Pardo'

#Python libraries
import random
import pygame

#Selfmade libraries
from settings import USEREVENTS, STRINGS, PARAMS, CHARACTERS, PATHS
from obj.utilities.exceptions import TooManyPlayersException, ZeroPlayersException,\
                                    NotEnoughHumansException
from obj.board import Board
from obj.tutorial_board import TutorialBoard
from obj.network_board import NetworkBoard
from obj.board_server import Server
from obj.utilities.logger import Logger as LOG
from obj.utilities.decorators import time_it

class BoardGenerator(object):
    """BoardGenerator class. Takes upon itself the task of creating a board that follows all the
    parameters that have been ingrained in it. This class is necessary due to the extensive ammount of possible
    and customizable parameters.
    Attributes:
        uuid (int): Unique identifier of the game itself. Used in online sessions and boards.
        tutorial (boolean): Flag that is True when the Tutorial mode has been selected.
        online (boolean):   Flag that is True when the game is between computers and the board is a network board.
        server (boolean):   Flag that is True when this computer is the one that will hold the server.
        private (boolean):  Flag that is True when the online server created is private, and only accesible by direct connection.
        direct_connect (boolean):   Flag that is True when the option of direct connect is selected. This changes the dialogs that are shown.
        only_cpu (boolean): Flag that is True when its an only cpu players board/game.
        only_human (boolean):   Flag that is True when its an only human players board/game.
        players (int):  Total number of players that the board/game will hold/have
        computer_players (int): Total number of computer controlled players that the board/game will hold/have
        computer_players_mode (String): AI mode used by the CPU players to choose movements.
        game_mode (String): Game mode chosen.
        prefab_size (String):   Prefabricated board size chosen.
        characters_params (Dict->Any:Any):  Base parameters of all the characters in a board. 
        board_params (Dict-> Any:Any):  Input parameters of a board object. Controls things like graphics and number of cells.
    """
    def __init__(self, uuid):
        """BoardGenerator constructor.
        Args:
            uuid (int): Unique identifier of the game/user itself."""
        self.uuid = uuid
        self.tutorial = False
        self.online = False
        self.server = False
        self.private = False
        self.direct_connect = True
        self.players = 2
        self.cpu_players = 0
        self.cpu_timeout = 10
        self.human_players = 2
        self.computer_players_mode = 'random'
        self.game_mode = 'classic'
        self.prefab_size = 'default'
        self.characters_params = CHARACTERS.CHARACTER_SETTINGS.copy()
        self.board_params = {'quadrants_overlap': True, 'cell_texture': PATHS.CELL_BASIC}

    def set_cell_texture(self, cell_texture):
        """Changes the board cells texture (By changing the string, the actual creation is chosen after this string).
        Args:
            cell_texture (String):  String describing the new texture used in the board cells."""
        cell_texture = cell_texture.lower()
        if 'dark' in cell_texture:
            self.board_params['cell_texture'] = PATHS.DARK_CELL
        elif 'double' in cell_texture or 'border' in cell_texture:
            self.board_params['cell_texture'] = PATHS.BORDERED_CELL
        else:
             self.board_params['cell_texture'] = PATHS.CELL_BASIC

    def set_players(self, players):
        """Changes the total number of players.
        Args:
            players (int):  New number of players that will participate in this board."""
        self.players = players
        if self.players <= 2:
            self.board_params['quadrants_overlap'] = True
        else:
            self.board_params['quadrants_overlap'] = False

    def set_round_time_cpu(self, round_time):
        """Change the round time for the computer players."""
        self.cpu_timeout = round_time
        self.board_params['counter_round_time'] = self.cpu_timeout

    def set_cpu_players(self, cpu_players):
        """Changes the ammount of cpu players."""
        self.cpu_players = cpu_players
        if cpu_players is 0:
            self.board_params['counter_round_time'] = None
            return
        self.board_params['counter_round_time'] = self.cpu_timeout

    def set_game_mode(self, gamemode):
        """Changes the current gamemode.
        Args:
            gamemode (String):  New chosen gamemode for the next game."""
        self.game_mode = gamemode.lower()

    def set_board_size(self, size):
        """Changes the current prefabricated size.
        Args:
            size (String):  New chosen prefabricated size of the board for the next game."""
        self.prefab_size = size.lower()

    def set_character_ammount(self, char, ammount):
        """Changes the ammount per player of some subtype of Character.
        Args:
            char (String):  Subtype of character to change.
            ammount (int):  New ammount of a subtype of character that each player will possess."""
        for type_of_char in self.characters_params.keys():
            if char in type_of_char or type_of_char in char:
                self.characters_params[type_of_char]['ammount'] = ammount
                LOG.log('INFO', 'Changed ', type_of_char, ' ammount to ', ammount)
                break
                
    def set_board_params(self, **params):
        """Changes the board input parameters.
        Args:
            **params (Dict->Any:Any):  New parameters for the board."""
        self.board_params.update(params)

    def add_players(self, board, **char_settings):
        """Auxiliar method used to add all the players (And the corresponding ammount of each) to an already created board.
        Differentiates between computer and human players.
        Args:
            board (:obj:Board): Created board to add players to.
            **char_settings (Dict->Any:Any):    Parameters of the characters that will hold each player.
        """
        if self.online and not self.server:
            return
        human_players_added, cpu_players_added = 0, 0
        for i in range (0, 4, 4//self.players):     #Im the host or an online game or a local game.
            if human_players_added < self.human_players:    #First we add all the human players, the cpu players will come after those
                board.create_player(random.choice(STRINGS.PLAYER_NAMES), i, (200, 200), cpu=False, **char_settings)
                human_players_added += 1
                continue
            if cpu_players_added < self.cpu_players:
                board.create_player(random.choice(STRINGS.PLAYER_NAMES), i, (200, 200), cpu=True, cpu_mode=self.computer_players_mode, cpu_time=self.cpu_timeout, **char_settings)
                cpu_players_added += 1
        if self.online:
            board.server.set_chars(sum(x['ammount'] for x in char_settings.values()))

    def get_actual_total_players(self):
        """Gets the sum of the computer players and human players attributes (Not the total players)"""
        return self.cpu_players+self.human_players

    @time_it
    def generate_board(self, resolution):
        """Creates and returns a board with players, following the previously setted attributes.
        Args:
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
        Returns:
            (:obj: Board | NetworkBoard):   Generated board, ready to be used in a game."""
        LOG.log('info', 'Selected gamemode is ', self.game_mode)
        LOG.log('info', 'Selected size is ', self.prefab_size)
        try:
            if resolution != self.board_params['platform_sprite'].resolution:
                self.board_params['platform_sprite'].set_canvas_size(resolution)
        except KeyError:
            pass
        try:
            self.board_params['animated_background'].set_resolution(resolution)
        except KeyError:
            pass
        if self.tutorial:
            return self.generate_tutorial(resolution)
        #From here on, we have to check the total numbe4r of playersç
        if self.get_actual_total_players() > self.players:
            raise TooManyPlayersException("The sum of cpu and human players it's more than the total players ammount")
        elif self.get_actual_total_players() is 0:
            raise ZeroPlayersException("You can't create a board with no players")
        elif self.online and self.server and self.human_players < 2:  #If you are the host
            raise NotEnoughHumansException("You can't start an online game with less than 2 human players. Create a local one instead.")
        if 'classic' in self.game_mode:
            return self.generate_classic(resolution)
        if 'great' in self.game_mode:
            return self.generate_great_wheel(resolution)
        #else gamemode is custom or unrecognized
        elif any(kw in self.prefab_size for kw in ('default', 'normal', 'medium')):
            board = self.generate_default(resolution)
        elif any(kw in self.prefab_size for kw in ('lite', 'light')):
            board = self.generate_lite(resolution)
        elif any(kw in self.prefab_size for kw in ('small', 'easy')):
            board = self.generate_small(resolution)
        elif any(kw in self.prefab_size for kw in ('xtra', 'extra', 'more', 'bigger')):
            board = self.generate_extra(resolution)
        elif any(kw in self.prefab_size for kw in ('huge', 'exxtra', 'hard')):
            board = self.generate_huge(resolution)
        elif any(kw in self.prefab_size for kw in ('insane', 'very hard', 'cantsee', 'nightmare')):
            board = self.generate_insane(resolution)
        elif any(kw in self.prefab_size for kw in ('test', 'impossible', 'notreal', 'purpose', 'zero', 'memoryerror')):
            board = self.generate_test(resolution)
        #END
        self.add_players(board, **self.characters_params)
        return board

    def generate_base_board(self, resolution, **board_params):
        """Creates and returns a board without players, following the previously setted attributes and input arguments.
        Args:
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
            **params (Dict->Any:Any):   Parameters for the board.
        Returns:
            (:obj: Board | NetworkBoard):   Generated board, ready to be used in a game."""
        if self.online:
            if self.server:
                server = Server(self.players, private=self.private, obj_uuid=self.uuid)
                return NetworkBoard(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution,\
                                    direct_connection=self.direct_connect, host=True, server=server, **board_params)
            return NetworkBoard(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution,\
                                    direct_connection=self.direct_connect, **board_params)
        return Board(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution, **board_params)
            
    def generate_tutorial(self, resolution):
        """Creates and returns a tutorial board with players. This tutorial board has way fewer characters than a normal game, 
        and one of each subtype, since its designed so the player learns. 
        Args:
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
        Returns:
            (:obj: Board):  Generated board, ready to be used in a game."""
        players_setting = self.players
        board_params = self.board_params.copy()
        board_params['max_levels'] = 4
        board_params['circles_per_lvl'] = 8
        board_params['random_filling'] = True
        board_params['center_cell'] = True
        board = TutorialBoard(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution, **board_params)
        char_settings = self.characters_params.copy()
        char_settings['pawn']['ammount'] = 2
        char_settings['warrior']['ammount'] = 1
        char_settings['wizard']['ammount'] = 1
        char_settings['priestess']['ammount'] = 1
        char_settings['matron_mother']['ammount'] = 1
        char_settings['holy_champion']['ammount'] = 1
        self.players = 2
        self.add_players(board, **char_settings)
        self.players = players_setting
        return board

    def generate_classic(self, resolution):
        """Creates and returns a classic board with players, following the previously setted attributes.
        Args:
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
        Returns:
            (:obj: Board | NetworkBoard):   Generated board, ready to be used in a game."""
        board_params = self.board_params.copy()
        board_params['max_levels'] = 4
        board_params['circles_per_lvl'] = 16
        board_params['random_filling'] = False
        board_params['center_cell'] = False
        board = self.generate_base_board(resolution, **board_params)
        #SETTING CHARS AMMOUNTS
        char_settings = self.characters_params.copy()
        if self.board_params['quadrants_overlap']:
            char_settings['pawn']['ammount'] = 7
            char_settings['warrior']['ammount'] = 3
            char_settings['wizard']['ammount'] = 2
            char_settings['priestess']['ammount'] = 2
            #TOTAL 15
        else:
            char_settings['pawn']['ammount'] = 5
            char_settings['warrior']['ammount'] = 1
            char_settings['wizard']['ammount'] = 1
            char_settings['priestess']['ammount'] = 1
            #TOTAL 9
        char_settings['matron_mother']['ammount'] = 1
        #ADDING PLAYERS AND RETURNING
        self.add_players(board, **char_settings)
        return board

    def generate_great_wheel(self, resolution):
        """Creates and returns a great wheel board with players, following the previously setted attributes.
        The great wheel board posses a center cell, and its a bit bigger than the classic one. Also holds more character and
        holy champions.
        Args:
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
        Returns:
            (:obj: Board | NetworkBoard):   Generated board, ready to be used in a game."""
        board_params = self.board_params.copy()
        board_params['max_levels'] = 5
        board_params['circles_per_lvl'] = 16
        board_params['random_filling'] = False
        board_params['center_cell'] = True
        board = self.generate_base_board(resolution, **board_params)
        #SETTING CHARS AMMOUNTS
        char_settings = self.characters_params.copy()
        if self.players <= 2:
            char_settings['pawn']['ammount'] = 9
            char_settings['warrior']['ammount'] = 4
            char_settings['wizard']['ammount'] = 2
            char_settings['priestess']['ammount'] = 2
            char_settings['holy_champion']['ammount'] = 2
            #TOTAL 20
        else:
            char_settings['pawn']['ammount'] = 7
            char_settings['warrior']['ammount'] = 1
            char_settings['wizard']['ammount'] = 1
            char_settings['priestess']['ammount'] = 1
            char_settings['holy_champion']['ammount'] = 1
            #TOTAL 12
        char_settings['matron_mother']['ammount'] = 1
        #ADDING PLAYERS AND RETURNING
        self.add_players(board, **char_settings)
        return board

    #PREFABRICATED SIZES FROM HERE ON
    def generate_default(self, resolution):
        """Creates and returns a default sized board without players.
        Args:
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
        Returns:
            (:obj: Board | NetworkBoard):   Generated board, ready to be used in a game."""
        self.board_params['max_levels'] = 4
        self.board_params['circles_per_lvl'] = 16
        return self.generate_base_board(resolution, **self.board_params)

    def generate_lite(self, resolution):
        """Creates and returns a lite sized board without players.
        Args:
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
        Returns:
            (:obj: Board | NetworkBoard):   Generated board, ready to be used in a game."""
        self.board_params['max_levels'] = 3
        self.board_params['circles_per_lvl'] = 16
        return self.generate_base_board(resolution, **self.board_params)

    def generate_small(self, resolution):
        """Creates and returns a small sized board without players.
        Args:
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
        Returns:
            (:obj: Board | NetworkBoard):   Generated board, ready to be used in a game."""
        self.board_params['max_levels'] = 3
        self.board_params['circles_per_lvl'] = 8
        return self.generate_base_board(resolution, **self.board_params)
    
    def generate_extra(self, resolution):
        """Creates and returns an extra big sized board without players.
        Args:
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
        Returns:
            (:obj: Board | NetworkBoard):   Generated board, ready to be used in a game."""
        self.board_params['max_levels'] = 5
        self.board_params['circles_per_lvl'] = 16
        return self.generate_base_board(resolution, **self.board_params)

    def generate_huge(self, resolution):
        """Creates and returns an huge sized board without players.
        Args:
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
        Returns:
            (:obj: Board | NetworkBoard):   Generated board, ready to be used in a game."""
        self.board_params['max_levels'] = 5
        self.board_params['circles_per_lvl'] = 32
        return self.generate_base_board(resolution, **self.board_params)

    def generate_insane(self, resolution):
        """Creates and returns an insanely big sized board without players.
        Args:
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
        Returns:
            (:obj: Board | NetworkBoard):   Generated board, ready to be used in a game."""
        self.board_params['max_levels'] = 6
        self.board_params['circles_per_lvl'] = 32
        return self.generate_base_board(resolution, **self.board_params)

    def generate_test(self, resolution):
        """Creates and returns a way too big sized board without players.
        In fact, its so big that some path finder methods will throw a memoryerror in this board
            if the game is being executed in a 32-bits python.
        Args:
            resolution (Tuple->int, int):   Current Resolution of the screen. In pixels.
        Returns:
            (:obj: Board | NetworkBoard):   Generated board, ready to be used in a game."""
        self.board_params['max_levels'] = 6
        self.board_params['circles_per_lvl'] = 64
        return self.generate_base_board(resolution, **self.board_params)
