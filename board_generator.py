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

#To hold the differenmt board configurations of whatever. And return a different board per gammemode.
PLAYER_NAMES = ['Mitches', 'Hayesshine', 'Rolbo Gordonggins', 'Spencerpop', 'Palka', 'Rainrobinson', 'Kingolas', 'Zippotudo',
                'Zimrcia', 'Coxobby Ohmswilson', 'Uwotm8', 'Orangeman', 'npc', 'Totallynot Arobot', 'Bigba Lshanging']
BOARD_ID = 'main_board'
BOARD_EVENT_ID = pygame.USEREVENT+2
CHARACTER_SETTINGS = {'pawn':{'number': 1, 'aliases':{'pickup': 'running'}},
                    'warrior':{'number': 1, 'aliases':{'pickup': 'run'}},
                    'wizard':{'number': 0, 'aliases':{'pickup': 'pick'}},
                    'priestess':{'number': 0, 'aliases':{'pickup': 'run'}},
                    'matron_mother':{'number': 0, 'path': IMG_FOLDER+'\\priestess', 'aliases':{'pickup': 'pick'}},
}

class BoardGenerator(object):
    def __init__(self):
        self.players = 2
        self.pawns = 4
        self.wizards = 2
        self.warriors = 2
        self.priestesses = 2
        self.matron_mothers = 1
        self.game_mode = 'default'
        self.board_params = {}

    def set_gamemode(self, gamemode):
        self.game_mode = gamemode

    def set_board_params(self, **params):
        self.board_params.update(params)

    def generate_board(self, resolution):
        alias = ('default', 'normal', 'medium')
        if any(kw in self.game_mode for kw in alias):
            return self.generate_default(resolution)

    def generate_default(self, resolution):
        board = Board(BOARD_ID, BOARD_EVENT_ID, resolution, **self.board_params)
        for i in range (0, self.players):
            board.create_player(random.choice(PLAYER_NAMES), i+1, (200, 200), **CHARACTER_SETTINGS)
        return board

    def generate_lite(self):
        return 0

    def generate_small(self):
        return 0
    
    def generate_extra(self):
        return 0

    def generate_huge(self):
        return 0

    def to_string(self):
        return 'Players: '+str(self.players)+'\nPawns: '+str(self.pawns)
