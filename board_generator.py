"""--------------------------------------------
board_generator module.
Have the following classes:
    BoardGenerator
--------------------------------------------"""
__all__ = ['BoardGenerator']
__version__ = '0.1'
__author__ = 'David Flaity Pardo'

import random
import pygame
from board import Board
from logger import Logger as LOG
from decorators import time_it
from settings import USEREVENTS, STRINGS, PARAMS, CHARACTERS

class BoardGenerator(object):
    def __init__(self):
        self.players = 2
        self.game_mode = 'classic'
        self.prefab_size = 'default'
        self.characters_params = CHARACTERS.CHARACTER_SETTINGS.copy()
        self.board_params = {}

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

    @time_it
    def generate_board(self, resolution):
        #Check type of board
        if self.players > 2:
            self.board_params['quadrants_overlap'] = False
        else:
            self.board_params['quadrants_overlap'] = True

        LOG.log('info', 'Selected gamemode is ', self.game_mode)
        LOG.log('info', 'Selected size is ', self.prefab_size)

        if 'classic' in self.game_mode:
            return self.generate_classic(resolution)
        elif 'great' in self.game_mode:
            return self.generate_great_wheel(resolution)
        #else custom or unrecognized
        if any(kw in self.prefab_size for kw in ('default', 'normal', 'medium')):
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
        for i in range (0, (4//self.players)):
            board.create_player(random.choice(STRINGS.PLAYER_NAMES), i*(4//self.players), (200, 200), **self.characters_params)
        return board

    def generate_default(self, resolution):
        return Board(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution, **self.board_params)

    def generate_classic(self, resolution):
        board = Board(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution,\
                    max_levels=4, circles_per_lvl=16, random_filling=False)
        char_settings = self.characters_params.copy()
        if self.players <= 2:
            char_settings['pawn']['ammount'] = 7
            char_settings['warrior']['ammount'] = 3
            char_settings['wizard']['ammount'] = 2
            char_settings['priestess']['ammount'] = 2
            char_settings['matron_mother']['ammount'] = 1
            #TOTAL 15
        else:
            char_settings['pawn']['ammount'] = 5
            char_settings['warrior']['ammount'] = 1
            char_settings['wizard']['ammount'] = 1
            char_settings['priestess']['ammount'] = 1
            char_settings['matron_mother']['ammount'] = 1
            #TOTAL 9
        for i in range (0, 4//self.players):
            board.create_player(random.choice(STRINGS.PLAYER_NAMES), i*(4//self.players), (200, 200), **char_settings)
        return board

    def generate_great_wheel(self, resolution):
        board = Board(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution,\
                    max_levels=5, circles_per_lvl=16, random_filling=False, center_cell=True)
        char_settings = self.characters_params.copy()
        if self.players <= 2:
            char_settings['pawn']['ammount'] = 9
            char_settings['warrior']['ammount'] = 4
            char_settings['wizard']['ammount'] = 3 # 2 later
            char_settings['priestess']['ammount'] = 3# 2 later
            char_settings['holy_champion']['ammount'] = 0 #2 later
            #TOTAL 20
        else:
            char_settings['pawn']['ammount'] = 7
            char_settings['warrior']['ammount'] = 2 # 1 later
            char_settings['wizard']['ammount'] = 1
            char_settings['priestess']['ammount'] = 1
            char_settings['holy_champion']['ammount'] = 0 #1 later
            #TOTAL 12
        #Those dont change
        char_settings['matron_mother']['ammount'] = 1
        for i in range (0, 4//self.players):
            board.create_player(random.choice(STRINGS.PLAYER_NAMES), i*(4//self.players), (200, 200), **char_settings)
        return board

    def generate_lite(self, resolution):
        self.board_params['max_levels'] = 3
        return Board(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution, **self.board_params)

    def generate_small(self, resolution):
        self.board_params['max_levels'] = 3
        self.board_params['circles_per_lvl'] = 8
        return Board(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution, **self.board_params)
    
    def generate_extra(self, resolution):
        self.board_params['max_levels'] = 5
        self.board_params['circles_per_lvl'] = 16
        return Board(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution, **self.board_params)

    def generate_huge(self, resolution):
        self.board_params['max_levels'] = 5
        self.board_params['circles_per_lvl'] = 32
        return Board(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution, **self.board_params)

    def generate_insane(self, resolution):
        self.board_params['max_levels'] = 6
        self.board_params['circles_per_lvl'] = 32
        return Board(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution, **self.board_params)

    def generate_test(self, resolution):
        self.board_params['max_levels'] = 6
        self.board_params['circles_per_lvl'] = 64
        return Board(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution, **self.board_params)
