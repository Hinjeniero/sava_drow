FONT = './local/zelda_font.ttf'
#MONOSPACED_FONT = './local/HyliaSerifBeta.ttf'
MONOSPACED_FONT = './local/ShareTechMono.ttf'

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
    SERVER_TABLE_KEYS = ('NAME', 'IP', 'PORT', 'PLAYERS', 'DEPLOYMENT')

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

class TUTORIAL:
    MESSAGE_BOARD = "This is the board. It's composed of the cells themselves, placed in a circular shape. We will call the circles 'circumferences', and the paths that connect between them rank or interpath."
    MESSAGE_MOVE_PAWN = "The pawn can move one space along any circumferences or rank, as long as the movement brings them closer to an enemy piece."
    MESSAGE_DESTINIES_BLINKING = "The possible destinies appear when you pick up any character."
    MESSAGE_FITNESS_NUMBERS = "If you have it activated, the possible movements will be evaluated in a scale 0->1."
    MESSAGE_MOVE_WARRIOR = "Due to their superior stamina, the warriors can move for two turns instead of one, capturing in each one. But because the heavy armor that they wear, each turn will only yield an one space movement"
    MESSAGE_MOVE_WIZARD = "A wizard can travel to positions that are three linked spaces away, regardless of intervening pieces."
    MESSAGE_MOVE_PRIESTESS = "Priestess can move along any rank or circumference if there are not intervening pieces in the middle of the path."
    MESSAGE_MOVE_MATRONMOTHER = "This is the matron mother. If it gets captured, you lose the game. It can move one space in any direction, regardless of circumstances"
    ALL_MSGS = [MESSAGE_BOARD, MESSAGE_MOVE_PAWN, MESSAGE_DESTINIES_BLINKING, MESSAGE_FITNESS_NUMBERS, MESSAGE_MOVE_WIZARD, MESSAGE_MOVE_PRIESTESS, MESSAGE_MOVE_MATRONMOTHER]

class CHARACTERS_DIALOGS:
    pass