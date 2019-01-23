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
from settings import USEREVENTS, STRINGS, PARAMS

class BoardGenerator(object):
    def __init__(self):
        self.players = 2
        self.game_mode = 'default'
        self.characters_params = PARAMS.CHARACTER_SETTINGS.copy()
        self.board_params = {}

    def set_gamemode(self, gamemode):
        self.game_mode = gamemode.lower()

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
        LOG.log('info', 'Selected gamemode is ', self.game_mode)
        if any(kw in self.game_mode for kw in ('default', 'normal', 'medium')):
            board = self.generate_default(resolution)
        elif any(kw in self.game_mode for kw in ('lite', 'light')):
            board = self.generate_lite(resolution)
        elif any(kw in self.game_mode for kw in ('small', 'easy')):
            board = self.generate_small(resolution)
        elif any(kw in self.game_mode for kw in ('xtra', 'extra', 'more', 'bigger')):
            board = self.generate_extra(resolution)
        elif any(kw in self.game_mode for kw in ('huge', 'exxtra', 'hard')):
            board = self.generate_huge(resolution)
        elif any(kw in self.game_mode for kw in ('insane', 'very hard', 'cantsee', 'nightmare')):
            board = self.generate_insane(resolution)
        elif any(kw in self.game_mode for kw in ('test', 'impossible', 'notreal', 'purpose', 'zero', 'memoryerror')):
            board = self.generate_test(resolution)
        #END
        for i in range (0, 4, (4//self.players)):
            board.create_player(random.choice(STRINGS.PLAYER_NAMES), i, (200, 200), **self.characters_params)
        return board

    def generate_default(self, resolution):
        return Board(PARAMS.BOARD_ID, USEREVENTS.BOARD_USEREVENT, USEREVENTS.END_CURRENT_GAME, resolution, **self.board_params)

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
