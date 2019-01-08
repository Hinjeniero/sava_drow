"""--------------------------------------------
board_generator module.
Have the following classes:
    BoardGenerator
--------------------------------------------"""
__all__ = ['BoardGenerator']
__version__ = '0.1'
__author__ = 'David Flaity Pardo'

from paths import IMG_FOLDER

#To hold the differenmt board configurations of whatever. And return a different board per gammemode.
PLAYER_NAMES = ['Mitches', 'Hayesshine', 'Rolbo Gordonggins', 'Spencerpop', 'Palka', 'Rainrobinson', 'Kingolas', 'Zippotudo',
                'Zimrcia', 'Coxobby Ohmswilson', 'Uwotm8', 'Orangeman', 'npc', 'Totallynot Arobot', 'Bigba Lshanging']
CHARACTER_SETTINGS = {'pawn':{'number': 1, 'aliases':{'pickup': 'running'}},
                    'warrior':{'number': 1, 'aliases':{'pickup': 'run'}},
                    'wizard':{'number': 0, 'aliases':{'pickup': 'pick'}},
                    'priestess':{'number': 0, 'aliases':{'pickup': 'run'}},
                    'matron_mother':{'number': 0, 'path': IMG_FOLDER+'\\priestess', 'aliases':{'pickup': 'pick'}},
}

#main_board.create_player("Rabudo", 1, (200, 200), **character_settings)
class BoardGenerator(object):
    def __init__(self):
        self.players = 2
        self.current_player = 1
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

    def generate_board(self):
        return True

    def generate_lite(self, **params):
        return 0

    def generate_small(self, **params):
        return 0
    
    def generate_extra(self, **params):
        return 0

    def generate_huge(self, **params):
        return 0