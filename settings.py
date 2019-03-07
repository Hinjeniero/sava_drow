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
    PLAYERS_AMMOUNT = (2, 4, 1) #1 is for testing
    ANIMATION_TIME = 25

class CHARACTERS:
    PAWN_AMMOUNT = 8
    WARRIOR_AMMOUNT = 2
    WIZARD_AMMOUNT = 2
    PRIESTESS_AMMOUNT = 2
    MATRONMOTHER_AMMOUNT = 1
    HOLYCHAMPION_AMMOUNT = 0
    CHARACTER_SETTINGS = {'pawn':{'ammount': PAWN_AMMOUNT, 'aliases':{'pickup': 'running'}},
                    'warrior':{'ammount': WARRIOR_AMMOUNT, 'aliases':{'pickup': 'run'}},
                    'wizard':{'ammount': WIZARD_AMMOUNT, 'aliases':{'pickup': 'pick'}},
                    'priestess':{'ammount': PRIESTESS_AMMOUNT, 'aliases':{'pickup': 'run'}},
                    'matron_mother':{'ammount': MATRONMOTHER_AMMOUNT, 'aliases':{'pickup': 'pick'}},
                    'holy_champion':{'ammount': HOLYCHAMPION_AMMOUNT, 'aliases':{'pickup': 'pick'}}
    }
    PAWN_OPTIONS = (PAWN_AMMOUNT, 16, 24, 32, 0, 4)
    WARRIOR_OPTIONS = (WARRIOR_AMMOUNT, 4, 6, 8, 0, 1)
    WIZARD_OPTIONS = (WIZARD_AMMOUNT, 4, 6, 8, 0, 1)
    PRIESTESS_OPTIONS = (PRIESTESS_AMMOUNT, 4, 6, 8, 0, 1)
    MATRONMOTHER_OPTIONS = (MATRONMOTHER_AMMOUNT, 2, 4)
    HOLYCHAMPION_OPTIONS = (HOLYCHAMPION_AMMOUNT, 1, 2, 4)

class SOUND_PARAMS:
    SOUND_CHANNELS_AMMOUNT = 8
    INIT_VOLUME = 0.01

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
    GAMEMODES = ('Custom', 'Classic', 'Great Wheel')
    BOARD_SIZES = ('Normal', 'Lite', 'Small', 'Extra', 'Huge', 'Insane', 'MemoryError')
    PLAYER_NAMES = ['Mitches', 'Hayesshine', 'Rolbo Gordonggins', 'Spencerpop', 'Palka', 'Rainrobinson', 'Kingolas', 'Zippotudo',
                    'Zimrcia', 'Coxobby Ohmswilson', 'Uwotm8', 'Orangeman', 'npc', 'Totallynot Arobot', 'Bigba Lshanging']
    SPRITE_NAMES = ('Manolo', 'Eustaquio', 'Zimamamio')
    MOVE_KEYWORDS = ('run', )
    YES_NO_OPTIONS = ('On', 'Off')
    YES_NO_REVERSED = ('Off', 'On')
    INITIAL_ANIMATED_BG = 'Animated waterfall'
    ANIMATED_BGS = (INITIAL_ANIMATED_BG, 'Animated rain tree',
                    'Animated rain china', 'Animated waterfall cave', 'Layered industrial')
    CELLS = ('Basic', 'Dark', 'Bordered')
#STATE MACHINES
class STATES:
    SCREEN = ('idle', 'stopped', 'cutscene')

class NETWORK:
    #Settings if yo are the server
    SERVER_REFRESH_TIME = 1
    SERVER_CONNECTION_REFRESH = 1
    SERVER_CONNECTION_TIMEOUT = 30
    SERVER_IP = '0.0.0.0'
    SERVER_PORT = 6397
    #Settings to connect to
    CLIENT_LOCAL_IP = 'localhost'    #USED IF IM THE SERVER
    CLIENT_IP = '192.168.1.254'      #USED TO CONNECT TO AN EXTERNAL COMPUTER AS A SERVER
    CLIENT_TIMEOUT_CONNECT = 30
    CLIENT_TIMEOUT_RECEIVE = 30

class MESSAGES:
    LOCKED_SURFACE_EXCEPTION = ('Warning', 'A surface was locked during the blit, skipping until next frame.')

#PATHS TO FILES/IMAGES/SOUNDS
#---Global paths(Container paths)
class PATHS:
    ROOT_FOLDER = os.path.dirname(__file__)
    ASSETS_FOLDER = os.path.join(ROOT_FOLDER, 'local\\')
    IMAGE_FOLDER = os.path.join(ASSETS_FOLDER, 'img\\')
    TEXTURES_FOLDER = os.path.join(IMAGE_FOLDER, 'textures\\')
    AUDIO_FOLDER = os.path.join(ASSETS_FOLDER, 'sounds\\')
    SOUNDS_FOLDER = AUDIO_FOLDER+'common\\'
    SECRET_FOLDER = AUDIO_FOLDER+'secret\\'
    #Characters
    PAWN = IMAGE_FOLDER+'Pawn'
    WIZARD = IMAGE_FOLDER+'Wizard'
    WARRIOR = IMAGE_FOLDER+'Warrior'
    PRIESTESS = IMAGE_FOLDER+'Priestess'
    MATRONMOTHER = IMAGE_FOLDER+'Matronmother'
    HOLYCHAMPION = IMAGE_FOLDER+'Matronmother'
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
    EXPLOSIONS = IMAGE_FOLDER+'Explosion'
    ALL_EXPLOSIONS = ['Small', 'Normal', 'big', 'nuclear', 'bomb', 'supernova']
    #---Main, the songs folders
    MENU_SONGS = AUDIO_FOLDER+'menu'
    BOARD_SONGS = AUDIO_FOLDER+'board'
    COMMON_SONGS = AUDIO_FOLDER+'common_music\\'
    #---Screen
    DEFAULT_BG = IMAGE_FOLDER+'background.jpg'
    LOADING_BG = IMAGE_FOLDER+'loading_background.png'
    START_BG = IMAGE_FOLDER+'start_background.png'
    LOADING_STATIC_CIRCLE = IMAGE_FOLDER+'loading_circle.png'
    LOADING_ANIMATED_CIRCLE = ''
    #---Menus, buttons and such
    LONG_POPUP = IMAGE_FOLDER+'pixel_panel_2.png'
    SHORT_BUTTON = IMAGE_FOLDER+'button.png'
    SHORT_GOLD_BUTTON = IMAGE_FOLDER+'golden_button.png'
    SHORT_DARK_GOLD_BUTTON = IMAGE_FOLDER+'dark_golden_button.png'
    SHORT_SILVER_BUTTON = IMAGE_FOLDER+'silver_button.png'
    SHORT_GOLD_SHADOW_BUTTON = IMAGE_FOLDER+'golden_button_shadow.png'
    SHORT_SILVER_SHADOW_BUTTON = IMAGE_FOLDER+'silver_button_shadow.png'
    DARK_LONG_BUTTON = IMAGE_FOLDER+'dark_button.png'
    INFOBOARD = IMAGE_FOLDER+'infoboard.png'
    DIALOG_SILVER = IMAGE_FOLDER+'dialog.png'
    #---sliders
    BROWN_SLIDER = IMAGE_FOLDER+'brown_slider.png'
    GOLD_SLIDER = IMAGE_FOLDER+'gold_slider.png'
    BROWN_BAR = IMAGE_FOLDER+'brown_bar.png'
    RED_BAR = IMAGE_FOLDER+'basic_red_bar.png'
    BLUE_BAR = IMAGE_FOLDER+'blue_bar.png'
    #---Board
    CELL_BASIC = IMAGE_FOLDER+'cell_basic.png'
    DARK_CELL = IMAGE_FOLDER+'cell_dark.png'
    BORDERED_CELL = IMAGE_FOLDER+'cell_double.png'
    CELL_GOLDEN_BORDER = IMAGE_FOLDER+'cell_gold_border.png'
    CIRCUMFERENCE_RUST = IMAGE_FOLDER+'circle.png'
    THIN_CIRCUMFERENCE = IMAGE_FOLDER+'thin_circle.png'
    SCOREBOARD_BASIC = IMAGE_FOLDER+'scoreboard.png'
    LONG_RED_BAR = IMAGE_FOLDER+'long_red_bar.png'
    #---Textures
    BASIC_TEXTURIZED_BG = IMAGE_FOLDER+'background_02.png'
    WOOD_TEXTURE_BASIC = TEXTURES_FOLDER+'wood.jpg'
    WOOD_TEXTURE_DARK = TEXTURES_FOLDER+'dark_wood.png'
    DARK_CAVE_TEXTURE = TEXTURES_FOLDER+'cave.png'
    GRASSLAND_TEXTURE = TEXTURES_FOLDER+'grassland.png'
    DESERT_TEXTURE = TEXTURES_FOLDER+'desert.png'
    #---objects
    CHEST = IMAGE_FOLDER+'chest.png'
    SHIELD = IMAGE_FOLDER+'shield.png'
    DIAMOND_SPEAR = IMAGE_FOLDER+'diamond_spear.png'
    DICE_FOLDER = IMAGE_FOLDER+'dice\\'
