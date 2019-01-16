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
from paths import IMG_FOLDER
from board import Board
from logger import Logger as LOG

#To hold the differenmt board configurations of whatever. And return a different board per gammemode.
PLAYER_NAMES = ['Mitches', 'Hayesshine', 'Rolbo Gordonggins', 'Spencerpop', 'Palka', 'Rainrobinson', 'Kingolas', 'Zippotudo',
                'Zimrcia', 'Coxobby Ohmswilson', 'Uwotm8', 'Orangeman', 'npc', 'Totallynot Arobot', 'Bigba Lshanging']
BOARD_ID = 'main_board'
BOARD_EVENT_ID = pygame.USEREVENT+2
CHARACTER_SETTINGS = {'pawn':{'ammount': 4, 'aliases':{'pickup': 'running'}},
                    'warrior':{'ammount': 2, 'aliases':{'pickup': 'run'}},
                    'wizard':{'ammount': 2, 'aliases':{'pickup': 'pick'}},
                    'priestess':{'ammount': 2, 'aliases':{'pickup': 'run'}},
                    'matron_mother':{'ammount': 1, 'path': IMG_FOLDER+'\\priestess', 'aliases':{'pickup': 'pick'}},
}

class BoardGenerator(object):
    def __init__(self):
        self.players = 2
        self.game_mode = 'default'
        self.characters_params = CHARACTER_SETTINGS.copy()
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
        for i in range (0, self.players):
            board.create_player(random.choice(PLAYER_NAMES), i+1, (200, 200), **self.characters_params)
        return board

    def generate_default(self, resolution):
        return Board(BOARD_ID, BOARD_EVENT_ID, resolution, **self.board_params)

    def generate_lite(self, resolution):
        self.board_params['max_levels'] = 3
        return Board(BOARD_ID, BOARD_EVENT_ID, resolution, **self.board_params)

    def generate_small(self, resolution):
        self.board_params['max_levels'] = 3
        self.board_params['circles_per_lvl'] = 8
        return Board(BOARD_ID, BOARD_EVENT_ID, resolution, **self.board_params)
    
    def generate_extra(self, resolution):
        self.board_params['max_levels'] = 5
        self.board_params['circles_per_lvl'] = 16
        return Board(BOARD_ID, BOARD_EVENT_ID, resolution, **self.board_params)

    def generate_huge(self, resolution):
        self.board_params['max_levels'] = 5
        self.board_params['circles_per_lvl'] = 32
        return Board(BOARD_ID, BOARD_EVENT_ID, resolution, **self.board_params)

    def generate_insane(self, resolution):
        self.board_params['max_levels'] = 6
        self.board_params['circles_per_lvl'] = 32
        return Board(BOARD_ID, BOARD_EVENT_ID, resolution, **self.board_params)

    def generate_test(self, resolution):
        self.board_params['max_levels'] = 6
        self.board_params['circles_per_lvl'] = 64
        return Board(BOARD_ID, BOARD_EVENT_ID, resolution, **self.board_params)

    def to_string(self):
        return 'Players: '+str(self.players)+'\nPawns: '+str(self.pawns)
