FONT = './local/zelda_font.ttf'
#ENGLISH

#SPANISH

#References
MAIN_MENU = ()
GRAPHICS_MENU = ()
MUSIC_MENU = ()
CONFIG_MENU = ()
INFOBOARD = ()

#HELP_DIALOGS_TEXT
#CONFIG_MENU
class CONFIG_BOARD_DIALOGS:
    SERVER_TABLE_KEYS = ('UUID', 'IP', 'PORT', 'PLAYERS', 'START')

class CONFIG_MENU_DIALOGS:
    CELL_TEXTURE_DIALOG= "This setting changes the appearance of the cells. The Basic option is just plain wood, the dark one is some kind of obsidian stone,"+\
            "and the double is slightly darker wood than the basic with a silver ring around it."
    LOADING_SCREEN_DIALOG="True shows a loading screen while the board itself is filled with characters, False shows the board and the characters appear as"+\
            "they are created and placed."

    PLAYERS_NUMBER_DIALOG="Number of players in the board. 4 players will split the board evenly, leaving less space for characters for each player."

    GAMEMODE_DIALOG="Each gamemode contains various unmutable settings, apart from Custom. Default spawns a board of 5 levels deep with 16 cells per level."+\
            "Great Wheel's board has 6 levels and a center cell with special properties."

    BOARD_SIZE_DIALOG="Different sizes from the board, with each one delivering different number of levels and cells. Go as follows: \nNormal: 4 levels, 16 cells: 52 total."+\
            "\nLite: 3 levels, 16 cells: 36 total.\nSmall: 3 levels, 8 cells: 20 total.\nExtra: 5 levels, 16 cells: 68 total.\nHuge: 5 levels, 32 cells: 132 total."+\
            "\nInsane: 6 levels, 32 cells: 164 total.\nMemoryError: 6 levels, 64 cells: 324 total."

    FILLING_ORDER_DIALOG="Filling order of the board. Random is not completely random, only adds a bit of randomness when dropping some characters."

    CENTER_CELL_DIALOG="True spawns a center cell, False doesn't do it. Pretty explicit."

    PAWNS_NUMBER_DIALOG="Number of pawns per player. If the total number of characters surpass the free cell zones for each player, the board won't be spawned."

    WARRIORS_NUMBER_DIALOG="Number of warriors per player. If the total number of characters surpass the free cell zones for each player, the board won't be spawned."

    WIZARDS_NUMBER_DIALOG="Number of wizards per player. If the total number of characters surpass the free cell zones for each player, the board won't be spawned."

    PRIESTESSES_NUMBER_DIALOG="Number of priestesses per player. If the total number of characters surpass the free cell zones for each player, the board won't be spawned."

    MATRON_MOTHERS_NUMBER_DIALOG="Number of matron mothers per player. If the total number of characters surpass the free cell zones for each player, the board won't be spawned."

    HOLY_CHAMPIONS_NUMBER_DIALOG="Number of holy champions per player. If the total number of characters surpass the free cell zones for each player, the board won't be spawned."

class CHARACTERS_DIALOGS:
    pass
    
class TUTORIAL_DIALOGS:
    pass