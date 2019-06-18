import pygame
import os

class USEREVENTS:
    """Identificators of each type of custom event that we create and detect.
    Each ID is a value between 24 (int until it are reserved for pygame) and 32 (max number allowed)"""
    MAINMENU_USEREVENT  = pygame.USEREVENT
    SOUND_USEREVENT     = pygame.USEREVENT+1
    GRAPHIC_USEREVENT   = pygame.USEREVENT+2
    CONFIG_USEREVENT    = pygame.USEREVENT+3
    BOARD_USEREVENT     = pygame.USEREVENT+4
    DIALOG_USEREVENT    = pygame.USEREVENT+5
    END_CURRENT_GAME    = pygame.USEREVENT+6
    TIMER_ONE_SEC       = pygame.USEREVENT+7

class INIT_PARAMS:
    """Global variables that will hold each parameter of the game's configuration.
    The names are pretty self-explanatory, so no problem there."""
    INITIAL_RESOLUTION = (1280, 720)
    # INITIAL_RESOLUTION = (1920, 1080)
    RESOLUTIONS = (INITIAL_RESOLUTION, (1366, 768), (1600, 900), (1920, 1080), (640, 360), (848, 480), (1024, 576))
    INITIAL_FPS = 60
    ALL_FPS     = (INITIAL_FPS, 120, 20, 30)
    MIXER       = (44100, -16, 2, 2048)
    MOUSE_VISIBLE = True
    GAME_NAME   = 'Sava Drow'

class PARAMS:
    """Hold some of the options for configurations and some default parameters. Further comments in the not so clear ones."""
    BOARD_ID = 'main_board' 
    AI_MODES = ('Totally random', 'Half random-fitness', 'Fitness best move', 'Alpha-beta', 'Alpha-beta w/ ordering', 'Monte Carlo Search')   #All possible IA modes strings. 
    PLAYERS_AMMOUNT = (2, 3, 4)     #ALl possible ammounts of total players in a game. 1 is for testing
    HUMAN_PLAYERS = (2, 3, 4, 0, 1)
    AI_PLAYERS = (0, 1, 2, 3, 4)          #ALl possible ammounts of computer controlled players in a game. If we want 4, choose 4 playeres and computer vs computer.
    CPU_TIMEOUTS = (10, 30, 1, 2, 5)
    ANIMATION_TIME = 25     #TODO Being honest, I dont remember what this was for. Will have to come back later.
    NUM_THREADS = 32    #Max number of concurrent active threads when drawing threads from the threading pool (Normal run_async decorator).

class CHARACTERS:
    """Default variables that regard the characters. They are used when creating an instance of that class or any of it's subclasses."""
    #Default ammount of each subclass of character in a classic board.
    PAWN_AMMOUNT = 8
    WARRIOR_AMMOUNT = 2
    WIZARD_AMMOUNT = 2
    PRIESTESS_AMMOUNT = 2
    MATRONMOTHER_AMMOUNT = 1
    HOLYCHAMPION_AMMOUNT = 0
    CHARACTER_SETTINGS = {'pawn':{'ammount': PAWN_AMMOUNT},
                    'warrior':{'ammount': WARRIOR_AMMOUNT},
                    'wizard':{'ammount': WIZARD_AMMOUNT},
                    'priestess':{'ammount': PRIESTESS_AMMOUNT},
                    'matron_mother':{'ammount': MATRONMOTHER_AMMOUNT},
                    'holy_champion':{'ammount': HOLYCHAMPION_AMMOUNT}
    }
    
    #All options for the ammount of each subclass, when the user chose custom game mode. 
    #Take care, since if the total number of characters is greater than the spaces designated for each player (in a board), you will receive an error.""
    PAWN_OPTIONS = (PAWN_AMMOUNT, 16, 24, 32, 0, 4)
    WARRIOR_OPTIONS = (WARRIOR_AMMOUNT, 4, 6, 8, 0, 1)
    WIZARD_OPTIONS = (WIZARD_AMMOUNT, 4, 6, 8, 0, 1)
    PRIESTESS_OPTIONS = (PRIESTESS_AMMOUNT, 4, 6, 8, 0, 1)
    MATRONMOTHER_OPTIONS = (MATRONMOTHER_AMMOUNT, 2, 4)
    HOLYCHAMPION_OPTIONS = (HOLYCHAMPION_AMMOUNT, 1, 2, 4)

    #Aliases of each action. The aliases are just a way to associate an action of the character (key) with the name
    #of the frames (images in your hard disk) that you want to show when performing that action.
    DEFAULT_ALIASES = {"idle" : "idle", "fight" : "fight", "attack" : "attack", "pickup" : "pickup",\
                        "drop" : "drop", "action" : "action", "die" : "die", "stop": "stop"}
    PAWN_ALIASES = {'pickup': 'running'}
    WARRIOR_ALIASES = {'pickup': 'run'}
    WIZARD_ALIASES = {'pickup': 'pick'}
    PRIESTESS_ALIASES = {'pickup': 'run'}
    MATRONMOTHER_ALIASES = {'pickup': 'pick'}
    HOLYCHAMPION_ALIASES = {'pickup': 'pick'}

class SOUND_PARAMS:
    """Parameters of the sound of the game."""
    SOUND_CHANNELS_AMMOUNT = 8  #Maximum simultaneous sound channels
    INIT_VOLUME = 0.01          #Initial sound volume. Go with caution, it can be VERY loud.

#---Miscellaneous
class SCREEN_FLAGS:
    """Screen flags that will be used when the game is in fullscreen or window-mode.
    Don't touch without reading the pygame documentation portraying this."""
    FULLSCREEN  = pygame.HWSURFACE | pygame.FULLSCREEN | pygame.DOUBLEBUF
    WINDOWED    = pygame.DOUBLEBUF

class SIZES:
    """Image size parameters. The MAX_SURFACE_SIZE is the maximum axis size than a loaded image can have.
    Without it, the game ate more RAM than a multitab google chrome session. Can be deactivated using the no_max_size decorator."""
    MAX_SURFACE_SIZE = 256
    
class EXTENSIONS:
    """Accepted formats in each of the cases."""
    SOUND_FORMATS = ('.ogg', '.mp3')
    MUSIC_FORMATS = ('.ogg', '.mp3')
    IMAGE_FORMATS = ('.png', '.jpg', '.jpeg', 'bmp', '.gif', '.tga', '.pcx', '.tif', '.lbm', '.pbm', '.xbm')

class STRINGS:
    """Strings that make up all the configuration options on the different menus. There is also some list/tuples with other purposes tho.
    Also contain parameters related to texts."""
    CHARS_PER_LINE = 36 #When using the return_lines_number method in utility_box.py, it will calculate the result according to this.
    GAMEMODES = ('Custom', 'Classic', 'Great Wheel')
    PLAYER_NAMES = ['Mitches', 'Hayesshine', 'Rolbo Gordonggins', 'Spencerpop', 'Palka', 'Rainrobinson', 'Kingolas', 'Zippotudo',
                    'Zimrcia', 'Coxobby Ohmswilson', 'Uwotm8', 'Orangeman', 'npc', 'Totallynot Arobot', 'Bigba Lshanging']
    BOARD_SIZES = ('Normal', 'Lite', 'Small', 'Extra', 'Huge', 'Insane', 'MemoryError')
    SPRITE_NAMES = ('Manolo', 'Eustaquio', 'Zimamamio')
    MOVE_KEYWORDS = ('run', )
    YES_NO_OPTIONS = ('On', 'Off')
    YES_NO_REVERSED = ('Off', 'On')
    ANIMATED_BGS = ('Animated waterfall', 'Animated rain tree', 'Animated rain china', 'Animated waterfall cave', 'Layered industrial')
    INITIAL_ANIMATED_BG = ANIMATED_BGS[0]
    CELLS = ('Basic', 'Dark', 'Bordered')
    IA_MODES = ('Fitness choosing', 'Alpha Beta deepening', 'Learning Machine')

#STATE MACHINES
class STATES:
    """Possible states for a screen. Unused right now, very useful for future expansions."""
    SCREEN = ('idle', 'stopped', 'cutscene')

class NETWORK:
    """Network settings, used when connecting to other players, be it in LAN or through the internet"""
    #Settings if yo are the server
    LOCAL_LOOPBACK_IP = '127.0.0.1'
    LOCAL_IP = None                 #This can be modified once at the beginning! It's the only variable that is modified in execution!
    SERVER_ALIAS = 'TEST_SERVER'    #The name that your server will have in the community list if you set it to public
    SERVER_REFRESH_TIME = 1         #Refresh time of the server
    SERVER_CONNECTION_REFRESH = 1   #Refrest time of the server connection
    SERVER_CONNECTION_TIMEOUT = 30
    SERVER_IP = '0.0.0.0'
    SERVER_PORT = 6397
    #Settings to connect to
    # CLIENT_IP = '192.168.1.254'      #USED TO CONNECT TO AN EXTERNAL COMPUTER AS A SERVER
    # CLIENT_LOCAL_IP = '127.0.0.1'    #USED IF IM THE SERVER
    CLIENT_TIMEOUT_CONNECT = 30
    CLIENT_TIMEOUT_RECEIVE = 30
    #URLS
    GET_IP = 'http://jsonip.com'
    TABLE_SERVERS_URL = 'http://savadrow.servegame.com'
    # TABLE_SERVERS_LOCAL_URL = 'http://192.168.1.254'  #Direction of the host of the node service returning the public servers
    TABLE_SERVERS_PORT = 9001
    TABLE_SERVERS_ADD_ENDPOINT = '/host/add'
    TABLE_SERVERS_UPDATE_ENDPOINT = '/host/update'
    TABLE_SERVERS_DELETE_ENDPOINT = '/host/delete'
    TABLE_SERVERS_GET_ALL_ENDPOINT = '/host/get/all'
    
class MESSAGES:
    """Messages used in recurrent errors with the pygame library."""
    LOCKED_SURFACE_EXCEPTION = ('Warning', 'A surface was locked during the blit, skipping until next frame.')

class PATHS:
    """Contain all the global paths to every local element needed in the game. (FILES/IMAGES/SOUNDS)"""
    #Folders
    ROOT_FOLDER = os.path.dirname(__file__)
    ASSETS_FOLDER = os.path.join(ROOT_FOLDER, 'local\\')
    IMAGE_FOLDER = os.path.join(ASSETS_FOLDER, 'img\\')
    TEXTURES_FOLDER = os.path.join(IMAGE_FOLDER, 'textures\\')
    AUDIO_FOLDER = os.path.join(ASSETS_FOLDER, 'sounds\\')
    SOUNDS_FOLDER = AUDIO_FOLDER+'common\\'
    SECRET_FOLDER = AUDIO_FOLDER+'secret\\'
    AVATAR_FOLDER = IMAGE_FOLDER+'avatars\\'
    EFFECTS_FOLDER = IMAGE_FOLDER+'effects\\'
    UUID_FILE = ASSETS_FOLDER+'myid.sav'    #Your user UUID file, generated only once. Will serve as your session ID too.
    
    #Characters
    PAWN = IMAGE_FOLDER+'Pawn'
    WIZARD = IMAGE_FOLDER+'Wizard'
    WARRIOR = IMAGE_FOLDER+'Warrior'
    PRIESTESS = IMAGE_FOLDER+'Priestess'
    MATRONMOTHER = IMAGE_FOLDER+'Matronmother'
    HOLYCHAMPION = IMAGE_FOLDER+'Matronmother'
    SANS = IMAGE_FOLDER+'sans_hd'
    
    #Char and sprites used in animations (animated backgrounds and such)
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
    
    #Audio folders, separated by screens
    MENU_SONGS = AUDIO_FOLDER+'menu'
    BOARD_SONGS = AUDIO_FOLDER+'board'
    COMMON_SONGS = AUDIO_FOLDER+'common_music\\'
    
    #Sprites and static backgrounds used by the Screen class and LoadingScreen subclass
    DEFAULT_BG = IMAGE_FOLDER+'background.jpg'
    LOADING_BG = IMAGE_FOLDER+'loading_background.png'
    START_BG = IMAGE_FOLDER+'start_background.png'
    LOADING_STATIC_CIRCLE = IMAGE_FOLDER+'loading_circle.png'
    LOADING_ANIMATED_CIRCLE = ''
    
    #Menu sprites, buttons, infoboards and dialogs
    LONG_POPUP = IMAGE_FOLDER+'pixel_panel_2.png'
    SHORT_BUTTON = IMAGE_FOLDER+'button.png'
    SHORT_GOLD_BUTTON = IMAGE_FOLDER+'golden_button.png'
    SHORT_DARK_GOLD_BUTTON = IMAGE_FOLDER+'dark_golden_button.png'
    SHORT_SILVER_BUTTON = IMAGE_FOLDER+'silver_button.png'
    SHORT_GOLD_SHADOW_BUTTON = IMAGE_FOLDER+'golden_button_shadow.png'
    SHORT_SILVER_SHADOW_BUTTON = IMAGE_FOLDER+'silver_button_shadow.png'
    DARK_LONG_BUTTON = IMAGE_FOLDER+'dark_button.png'
    INFOBOARD = IMAGE_FOLDER+'infoboard.png'
    INFOBOARD_GRADIENT = IMAGE_FOLDER+'infoboard_02.png'
    DIALOG_SILVER = IMAGE_FOLDER+'dialog.png'
    
    #Menu sprites, sliders and filling bars
    BROWN_SLIDER = IMAGE_FOLDER+'brown_slider.png'
    GOLD_SLIDER = IMAGE_FOLDER+'gold_slider.png'
    BROWN_BAR = IMAGE_FOLDER+'brown_bar.png'
    RED_BAR = IMAGE_FOLDER+'basic_red_bar.png'
    BLUE_BAR = IMAGE_FOLDER+'blue_bar.png'
    
    #Board elements, cells and circumferences
    CELL_BASIC = IMAGE_FOLDER+'cell_basic.png'
    DARK_CELL = IMAGE_FOLDER+'cell_dark.png'
    BORDERED_CELL = IMAGE_FOLDER+'cell_double.png'
    CELL_GOLDEN_BORDER = IMAGE_FOLDER+'cell_gold_border.png'
    CIRCUMFERENCE_RUST = IMAGE_FOLDER+'circle.png'
    THIN_CIRCUMFERENCE = IMAGE_FOLDER+'thin_circle.png'
    SCOREBOARD_BASIC = IMAGE_FOLDER+'scoreboard.png'
    LONG_RED_BAR = IMAGE_FOLDER+'long_red_bar.png'
    
    #Textures
    BASIC_TEXTURIZED_BG = IMAGE_FOLDER+'background_02.png'
    WOOD_TEXTURE_BASIC = TEXTURES_FOLDER+'wood.jpg'
    WOOD_TEXTURE_DARK = TEXTURES_FOLDER+'dark_wood.png'
    DARK_CAVE_TEXTURE = TEXTURES_FOLDER+'cave.png'
    GRASSLAND_TEXTURE = TEXTURES_FOLDER+'grassland.png'
    DESERT_TEXTURE = TEXTURES_FOLDER+'desert.png'
    DARK_BRICK = IMAGE_FOLDER+'cave_dark_brick.png'

    #Misc objects
    CHEST = IMAGE_FOLDER+'chest.png'
    SHIELD = IMAGE_FOLDER+'shield.png'
    SHIELD_ICON = IMAGE_FOLDER+'shield_icon.png'
    DIAMOND_SPEAR = IMAGE_FOLDER+'diamond_spear.png'
    DICE_FOLDER = IMAGE_FOLDER+'dice\\'
    HOURGLASS_FOLDER = IMAGE_FOLDER+'sandclock\\'
        
    #Icons
    HELP_ICON = IMAGE_FOLDER+'help_icon.png'
    WARNING_ICON = IMAGE_FOLDER+'warning_icon.png'

    #Effects
    BLUE_RING = EFFECTS_FOLDER+'blue_ring\\'
    SMOKE_RING = EFFECTS_FOLDER+'smoke_ring\\'
    FIRE_RING = EFFECTS_FOLDER+'fire_ring\\'
    GOLDEN_RING = EFFECTS_FOLDER+'gold_ring\\'