import pygame
import os

#PYGAME_USEREVENTS
MAINMENU_USEREVENT = pygame.USEREVENT
SOUND_USEREVENT = pygame.USEREVENT+1
GRAPHIC_USEREVENT = pygame.USEREVENT+2
CONFIG_USEREVENT = pygame.USEREVENT+3
END_CURRENT_GAME = pygame.USEREVENT+6
TIMER_ONE_SECOND = pygame.USEREVENT+7
#GLOBAL VARIABLES, LIKE ALL THE FPS ALLOWED; ETC; ETC
#---Graphics
INITIAL_RESOLUTION = (1280, 720)
RESOLUTIONS = (INITIAL_RESOLUTION, (1366, 768), (1600, 900), (1920, 1080), (256, 144), (640, 360), (848, 480), (1024, 576))
INITIAL_FPS = 60
ALL_FPS = (INITIAL_FPS, 120, 20, 30)
FULLSCREEN_FLAGS =
WINDOWED_FLAGS =
#---Miscellaneous
GAMEMODES = ('Normal', 'Lite', 'Small', 'Extra', 'Huge', 'Insane', 'MemoryError')
SOUND_FORMATS = ()
MUSIC_FORMATS = ()
IMAGE_FORMATS = ()
#---Strings, but not related to texts, more like names and shit
PLAYER_NAMES = ['Mitches', 'Hayesshine', 'Rolbo Gordonggins', 'Spencerpop', 'Palka', 'Rainrobinson', 'Kingolas', 'Zippotudo',
                'Zimrcia', 'Coxobby Ohmswilson', 'Uwotm8', 'Orangeman', 'npc', 'Totallynot Arobot', 'Bigba Lshanging']
DOOR_PATH = (IMG_FOLDER+'\\Portal')
SPRITE_NAMES = ('Manolo', 'Eustaquio', 'Zimamamio')
MOVE_KEYWORDS = ('run', )

#PATHS TO FILES/IMAGES/SOUNDS
#---Global paths(Container paths)
GAME_FOLDER = os.path.dirname(__file__)
IMAGE_FOLDER = os.path.join(GAME_FOLDER, 'img\\')
AUDIO_FOLDER = os.path.join(GAME_FOLDER, 'sounds\\')
#---Specific paths
CHAR_PATHS = (IMG_FOLDER+'Pawn', IMG_FOLDER+'Warrior', IMG_FOLDER+'Wizard', IMG_FOLDER+'Priestess', IMG_FOLDER+'Matronmother')
MENU_SONGS_PATH
BOARD_SONGS_PATH
COMMON_SONGS_PATH