import pygame
import os

#PYGAME_USEREVENTS
class USEREVENTS:
    MAINMENU_USEREVENT  = pygame.USEREVENT
    SOUND_USEREVENT     = pygame.USEREVENT+1
    GRAPHIC_USEREVENT   = pygame.USEREVENT+2
    CONFIG_USEREVENT    = pygame.USEREVENT+3
    BOARD_USEREVENT     = pygame.USEREVENT+4
    DIALOG_USEREVENT    = pygame.USEREVENT+5
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
    CHARACTER_SETTINGS = {'pawn':{'ammount': 0, 'aliases':{'pickup': 'running'}},
                    'warrior':{'ammount': 0, 'aliases':{'pickup': 'run'}},
                    'wizard':{'ammount': 0, 'aliases':{'pickup': 'pick'}},
                    'priestess':{'ammount': 0, 'aliases':{'pickup': 'run'}},
                    'matron_mother':{'ammount': 0, 'aliases':{'pickup': 'pick'}},
    }

class SOUND_PARAMS:
    SOUND_CHANNELS_AMMOUNT = 8
    INIT_BOARD_VOLUME = 0.25
    INIT_MENU_VOLUME = 0.25
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

#STATE MACHINES
class STATES:
    SCREEN = ('idle', 'stopped', 'cutscene')

#PATHS TO FILES/IMAGES/SOUNDS
#---Global paths(Container paths)
class PATHS:
    GAME_FOLDER = os.path.dirname(__file__)
    IMAGE_FOLDER = os.path.join(GAME_FOLDER, 'img\\')
    AUDIO_FOLDER = os.path.join(GAME_FOLDER, 'sounds\\')
    SOUNDS_FOLDER = AUDIO_FOLDER+'common\\'
    #Characters
    PAWN = IMAGE_FOLDER+'Pawn'
    WIZARD = IMAGE_FOLDER+'Wizard'
    WARRIOR = IMAGE_FOLDER+'Warrior'
    PRIESTESS = IMAGE_FOLDER+'Priestess'
    MATRONMOTHER = IMAGE_FOLDER+'Matronmother'
    SANS = IMAGE_FOLDER+'sans_hd'
    #---Specific paths, animation_generator
    CHARS = (PAWN, WARRIOR, WIZARD, PRIESTESS,MATRONMOTHER)
    DOOR = IMAGE_FOLDER+'Portal'
    ANIMATED_TREE = IMAGE_FOLDER+'Tree'
    ANIMATED_WATERFALL_BG = IMAGE_FOLDER+'Waterfall'
    ANIMATED_CAVE_WATERFALL_BG = IMAGE_FOLDER+'Waterfall_dark'
    ANIMATED_RAIN_TREE_BG = IMAGE_FOLDER+'Rain_tree'
    ANIMATED_RAIN_CHINESE_BG = IMAGE_FOLDER+'Rain_chinese'
    INDUSTRIAL_LAYERED_BG = IMAGE_FOLDER+'Industrial'
    #---Main, the songs folders
    MENU_SONGS = AUDIO_FOLDER+'menu'
    BOARD_SONGS = AUDIO_FOLDER+'board'
    COMMON_SONGS = AUDIO_FOLDER+'common'
    #---Screen
    DEFAULT_BG = IMAGE_FOLDER+'background.jpg'
    LOADING_BG = IMAGE_FOLDER+'loading_background.png'
    LOADING_STATIC_CIRCLE = IMAGE_FOLDER+'loading_circle.png'
    LOADING_ANIMATED_CIRCLE = ''
    #---Menus, buttons and such
    LONG_POPUP = IMAGE_FOLDER+'pixel_panel_2.png'
    SHORT_BUTTON = IMAGE_FOLDER+'button.png'
    INFOBOARD = IMAGE_FOLDER+'infoboard.png'