"""--------------------------------------------
board_generator module.
Have the following classes:
    BoardGenerator
--------------------------------------------"""
__all__ = ['BoardGenerator']
__version__ = '0.6'
__author__ = 'David Flaity Pardo'

import random
import pygame
from obj.board import Board
from obj.network_board import NetworkBoard
from obj.board_server import Server
from obj.utilities.logger import Logger as LOG
from obj.utilities.decorators import time_it
from settings import USEREVENTS, STRINGS, PARAMS, CHARACTERS, PATHS

class BoardGenerator(object):
    def __init__(self):
        self.online = False
        self.server = False
        self.players = 2
        self.game_mode = 'custom'
        self.prefab_size = 'default'
        self.characters_params = CHARACTERS.CHARACTER_SETTINGS.copy()
        self.board_params = {'quadrants_overlap': True, 'cell_texture': PATHS.CELL_BASIC}

    def set_cell_texture(self, cell_texture):
        cell_texture = cell_texture.lower()
        if 'dark' in cell_texture:
            self.board_params['cell_texture'] = PATHS.DARK_CELL
        elif 'double' in cell_texture or 'border' in cell_texture:
            self.board_params['cell_texture'] = PATHS.BORDERED_CELL
        else:
             self.board_params['cell_texture'] = PATHS.CELL_BASIC

    def set_players(self, players):
        self.players = players
        if self.players <= 2:
            self.board_params['quadrants_overlap'] = True
        else:
            self.board_params['quadrants_overlap'] = False

    def set_game_mode(self, gamemode):
        self.game_mode = gamemode.lower()

    def set_board_size(self, size):
        self.prefab_size = size.lower()

    def set_character_ammount(self, char, ammount):
        for type_of_char in self.characters_params.keys():
            if char in type_of_char or type_of_char in char:
                self.characters_params[type_of_char]['ammount'] = ammount
                LOG.log('INFO', 'Changed ', type_of_char, ' ammount to ', ammount)
                return
                
    def set_board_params(self, **params):
        self.board_params.update(params)

    def add_players(self, board, **char_settings):
        if self.online and not self.server:
            return
        for i in range (0, 4, 4//self.players): #Im the host or a local game.
            board.create_player(random.choice(STRINGS.PLAYER_NAMES), i, (200, 200), **char_settings)
        if self.online:
            board.server.set_chars(sum(x['ammount'] for x in char_settings.values()))
            
    @time_it
    def generate_board(self, resolution):
        LOG.log('info', 'Selected gamemode is ', self.game_mode)
        LOG.log('info', 'Selected size is ', self.prefab_size)
        if 'classic' in self.game_mode:
            return self.generate_classic(resolution)
        elif 'great' in self.game_mode:
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
        if self.online:
            if self.server:
                server = Server(self.players)
                return NetworkBoard(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution, host=True, server=server, **board_params)
            return NetworkBoard(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution, **board_params)
        return Board(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution, **board_params)
            
    def generate_classic(self, resolution):
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
        self.board_params['max_levels'] = 4
        self.board_params['circles_per_lvl'] = 16
        return self.generate_base_board(resolution, **self.board_params)

    def generate_lite(self, resolution):
        self.board_params['max_levels'] = 3
        self.board_params['circles_per_lvl'] = 16
        return self.generate_base_board(resolution, **self.board_params)

    def generate_small(self, resolution):
        self.board_params['max_levels'] = 3
        self.board_params['circles_per_lvl'] = 8
        return self.generate_base_board(resolution, **self.board_params)
    
    def generate_extra(self, resolution):
        self.board_params['max_levels'] = 5
        self.board_params['circles_per_lvl'] = 16
        return self.generate_base_board(resolution, **self.board_params)

    def generate_huge(self, resolution):
        self.board_params['max_levels'] = 5
        self.board_params['circles_per_lvl'] = 32
        return self.generate_base_board(resolution, **self.board_params)

    def generate_insane(self, resolution):
        self.board_params['max_levels'] = 6
        self.board_params['circles_per_lvl'] = 32
        return self.generate_base_board(resolution, **self.board_params)

    def generate_test(self, resolution):
        self.board_params['max_levels'] = 6
        self.board_params['circles_per_lvl'] = 64
        return self.generate_base_board(resolution, **self.board_params)
