import pygame
import os

#PYGAME_USEREVENTS
class USEREVENTS:
    MAINMENU_USEREVENT  = pygame.USEREVENT
    SOUND_USEREVENT     = pygame.USEREVENT+1
    GRAPHIC_USEREVENT   = pygame.USEREVENT+2
    CONFIG_USEREVENT    = pygame.USEREVENT+3
    BOARD_USEREVENT     = pygame.USEREVENT+4
    END_CURRENT_GAME    = pygame.USEREVENT+6
    TIMER_ONE_SEC       = pygame.USEREVENT+7

#GLOBAL VARIABLES, LIKE ALL THE FPS ALLOWED; ETC; ETC
#---Graphics/PARAMS
class INIT_PARAMS:
    INITIAL_RESOLUTION = (1280, 720)
    RESOLUTIONS = (INITIAL_RESOLUTION, (1366, 768), (1600, 900), (1920, 1080), (256, 144), (640, 360), (848, 480), (1024, 576))
    INITIAL_FPS = 60
    ALL_FPS     = (INITIAL_FPS, 120, 20, 30)
    MIXER       = (44100, -16, 2, 2048)
    MOUSE_VISIBLE = True
    GAME_NAME   = 'Sava Drow'

class PARAMS:
    BOARD_ID    = 'main_board'
    CHARACTER_SETTINGS = {'pawn':{'ammount': 4, 'aliases':{'pickup': 'running'}},
                    'warrior':{'ammount': 2, 'aliases':{'pickup': 'run'}},
                    'wizard':{'ammount': 2, 'aliases':{'pickup': 'pick'}},
                    'priestess':{'ammount': 2, 'aliases':{'pickup': 'run'}},
                    'matron_mother':{'ammount': 1, 'aliases':{'pickup': 'pick'}},
    }

#---Miscellaneous
class SCREEN_FLAGS:
    FULLSCREEN  = pygame.HWSURFACE | pygame.FULLSCREEN | pygame.DOUBLEBUF
    WINDOWED    = pygame.DOUBLEBUF
class SIZES:
    MAX_SURFACE_SIZE = 256

class EXTENSIONS:
    SOUND_FORMATS = ('.ogg', '.mp3')
    MUSIC_FORMATS = ('.ogg', '.mp3')
    IMAGE_FORMATS = ('.png', '.jpg', '.jpeg', 'bmp', '.gif', '.tga', '.pcx', '.tif', '.lbm', '.pbm', '.xbm')

class STRINGS:
    #Strings, but not related to texts, more like names and shit
    GAMEMODES = ('Normal', 'Lite', 'Small', 'Extra', 'Huge', 'Insane', 'MemoryError')
    PLAYER_NAMES = ['Mitches', 'Hayesshine', 'Rolbo Gordonggins', 'Spencerpop', 'Palka', 'Rainrobinson', 'Kingolas', 'Zippotudo',
                    'Zimrcia', 'Coxobby Ohmswilson', 'Uwotm8', 'Orangeman', 'npc', 'Totallynot Arobot', 'Bigba Lshanging']
    SPRITE_NAMES = ('Manolo', 'Eustaquio', 'Zimamamio')
    MOVE_KEYWORDS = ('run', )

#PATHS TO FILES/IMAGES/SOUNDS
#---Global paths(Container paths)
class PATHS:
    GAME_FOLDER = os.path.dirname(__file__)
    IMAGE_FOLDER = os.path.join(GAME_FOLDER, 'img\\')
    AUDIO_FOLDER = os.path.join(GAME_FOLDER, 'sounds\\')
    #---Specific paths
    CHAR_PATHS = (IMAGE_FOLDER+'Pawn', IMAGE_FOLDER+'Warrior', IMAGE_FOLDER+'Wizard', IMAGE_FOLDER+'Priestess', IMAGE_FOLDER+'Matronmother')
    DOOR_PATH = (IMAGE_FOLDER+'\\Portal')
    MENU_SONGS_PATH = AUDIO_FOLDER+'menu'
    BOARD_SONGS_PATH = AUDIO_FOLDER+'board'
    COMMON_SONGS_PATH = AUDIO_FOLDER+'common'

    POPUP_IMAGE = IMAGE_FOLDER+'\\pixel_panel_2.png'