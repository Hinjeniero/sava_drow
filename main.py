"""--------------------------------------------
main module. Starts everything.
--------------------------------------------"""
__version__ = '0.1'
__author__ = 'David Flaity Pardo'

#Python librariess
import pygame
import os
import threading
import sys
import faulthandler
from pygame.locals import *
from pygame.key import *
from obj.screen import Screen
#Selfmade Libraries
from settings import USEREVENTS, INIT_PARAMS, PATHS, CHARACTERS, PARAMS,\
                    STRINGS, EXTENSIONS, SCREEN_FLAGS, SOUND_PARAMS
from game import Game
from animation_generator import AnimationGenerator
from dialog_generator import DialogGenerator
from obj.help_dialogs import HelpDialogs
from obj.board import Board
from obj.menu import Menu
from obj.sprite import AnimatedSprite
from obj.ui_element import UIElement, TextSprite, InfoBoard, Dialog, TextBox
from obj.utilities.colors import RED, BLACK, WHITE, GREEN
from obj.utilities.logger import Logger as LOG
from obj.utilities.surface_loader import ResizedSurface, no_size_limit
from obj.utilities.utility_box import UtilityBox
from obj.utilities.decorators import time_it, run_async

#This because segmentation fault
faulthandler.enable()

#MUSIC
MENU_SONGS = UtilityBox.get_all_files(PATHS.MENU_SONGS, *EXTENSIONS.MUSIC_FORMATS)
BOARD_SONGS = UtilityBox.get_all_files(PATHS.BOARD_SONGS, *EXTENSIONS.MUSIC_FORMATS)
COMMON_SONGS = UtilityBox.get_all_files(PATHS.COMMON_SONGS, *EXTENSIONS.MUSIC_FORMATS)
MENU_SONGS.extend(COMMON_SONGS)
BOARD_SONGS.extend(COMMON_SONGS)
#Music for the buttons, to show the titles and that shit
MENU_CROPPED_SONGS = [song.split('\\')[-1].split('.')[0] for song in MENU_SONGS]
BOARD_CROPPED_SONGS = [song.split('\\')[-1].split('.')[0] for song in BOARD_SONGS]

def start_pygame(resolution=INIT_PARAMS.INITIAL_RESOLUTION):
    pygame.mixer.pre_init(*INIT_PARAMS.MIXER)
    pygame.init()
    pygame.mouse.set_visible(INIT_PARAMS.MOUSE_VISIBLE)
    pygame.display.set_caption(INIT_PARAMS.GAME_NAME)
    MY_SCREEN_RESOLUTION = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    if MY_SCREEN_RESOLUTION not in INIT_PARAMS.RESOLUTIONS:
        INIT_PARAMS.RESOLUTIONS = INIT_PARAMS.RESOLUTIONS + (MY_SCREEN_RESOLUTION,)
    pygame.display.set_mode(resolution, SCREEN_FLAGS.WINDOWED)  

def generate_ui_elements(results, thread_list, element_size, user_event_id, **params):
    """accepts args in each send, and yields the thread working on the element. 
    In this way we dont have to repeat the kwargs every single time.
    Don't work with elements that contain another elements (Infoboards)."""
    while True:
        id_, command, position, new_kwargs = yield
        params.update(new_kwargs)
        thread_list.append(UIElement.threaded_factory(results, id_, command, user_event_id, position, element_size, INIT_PARAMS.INITIAL_RESOLUTION, **params))

def generate_ui_elements_different_sizes(results, thread_list, user_event_id, **params):
    """accepts args in each send, and yields the thread working on the element. 
    In this way we dont have to repeat the kwargs every single time.
    Don't work with elements that contain another elements (Infoboards).
    Difference with the base method is that in this one you have to send the size too"""
    while True:
        id_, command, position, size, new_kwargs = yield
        params.update(new_kwargs)
        thread_list.append(UIElement.threaded_factory(results, id_, command, user_event_id, position, size, INIT_PARAMS.INITIAL_RESOLUTION, **params))

@run_async
def create_main_menu(result):
    #Create elements, main menu buttons (POSITIONS AND SIZES ARE IN PERCENTAGES OF THE CANVAS_SIZE, can use absolute integers too)
    positions       = UtilityBox.size_position_generator(9, 0.40, 0.05, 0.20, 0)
    button_size     = next(positions)
    #Creation of elements
    elements, threads = [], []
    element_generator = generate_ui_elements(elements, threads, button_size, USEREVENTS.MAINMENU_USEREVENT, resize_mode='fill', texture=PATHS.DARK_LONG_BUTTON)
    element_generator.send(None)    #Starting generator
    #Starts generating
    element_generator.send(('button_start', "start_game_go_main_board", next(positions), {'text': "Start new game"}))
    element_generator.send(('button_online_host', "host_network_start_online_game_go_main_board", next(positions), {'text': "Host public game"}))
    element_generator.send(('button_online_host', "host_private_network_start_online_game_go_main_board", next(positions), {'text': "Host private game"}))
    element_generator.send(('button_explorer_client', "client_start_online_game_get_servers_go_main_board", next(positions), {'text': "Connect to community server"}))
    element_generator.send(('button_online_client', "client_start_online_game_go_main_board", next(positions), {'text': "Connect to private server"}))
    element_generator.send(('button_continue', "continue_game_go_main_board", next(positions), {'text': "Continue last game"}))
    element_generator.send(('button_params_menu', "go_menu_params_config", next(positions), {'text': "Game settings"}))
    element_generator.send(('button_sound', "go_menu_sound_music", next(positions), {'text': "Sound settings"}))
    element_generator.send(('button_graphics', "go_menu_graphics_display", next(positions), {'text': "Graphics settings"}))
    for end_event in threads:   end_event.wait()    #Waiting for all the buttons to be created
    #Create Menu
    bg = AnimationGenerator.factory(STRINGS.INITIAL_ANIMATED_BG, INIT_PARAMS.INITIAL_RESOLUTION, PARAMS.ANIMATION_TIME, INIT_PARAMS.ALL_FPS, INIT_PARAMS.INITIAL_FPS)
    main_menu   = Menu('main_menu', USEREVENTS.MAINMENU_USEREVENT, INIT_PARAMS.INITIAL_RESOLUTION, *elements, animated_background=bg, background_path=PATHS.DEFAULT_BG, songs_paths=MENU_SONGS, do_align=False)
    main_menu.add_dialogs(DialogGenerator.create_exit_dialog('game', tuple(x//2 for x in INIT_PARAMS.INITIAL_RESOLUTION), INIT_PARAMS.INITIAL_RESOLUTION))
    main_menu.add_animation(AnimationGenerator.floating_sprite(INIT_PARAMS.INITIAL_RESOLUTION, (0.5, 0.075), (0.5, 0.125), tuple(0.15*x for x in INIT_PARAMS.INITIAL_RESOLUTION),\
                                                                4, INIT_PARAMS.ALL_FPS, PATHS.IMAGE_FOLDER, keywords=('spider',), text="SAVA DROW"))
    main_menu.enable_sprite('continue', state=False)
    result.append(main_menu) 

@run_async
def create_config_menu(result):
    button_size = (0.60, 0.15)
    positions   = UtilityBox.size_position_generator_no_adjustment(*button_size, 0.05, 0.15)
    gradients   = UtilityBox.looped_rainbow_gradient_generator(((255, 0, 0), (0, 0, 0)), 3)
    
    #Creation of elements
    elements, threads = [], []
    element_generator = generate_ui_elements(elements, threads, button_size, USEREVENTS.CONFIG_USEREVENT, text_alignment='left')
    element_generator.send(None)    #Starting generator
    #Starts generating
    element_generator.send(('button_cell_texture', "change_cell_texture", next(positions), {'default_values': STRINGS.CELLS, 'text': 'Cell type', 'gradient': next(gradients)}))
    element_generator.send(('button_loading', "change_loading_board", next(positions), {'default_values': STRINGS.YES_NO_OPTIONS, 'text': 'Show screen while board loads', 'gradient': next(gradients)}))
    element_generator.send(('button_players', "add_players_board", next(positions), {'default_values': PARAMS.PLAYERS_AMMOUNT, 'text': 'Number of players', 'gradient': next(gradients)}))
    element_generator.send(('button_game_mode', "change_game_mode", next(positions), {'default_values': STRINGS.GAMEMODES, 'text': 'Game Mode', 'gradient': next(gradients)}))
    element_generator.send(('button_board_size', "set_board_size", next(positions), {'default_values': STRINGS.BOARD_SIZES, 'text': 'Board Size', 'gradient': next(gradients)}))
    element_generator.send(('button_board_fill', "set_random_board_dropping_fill", next(positions), {'default_values': STRINGS.YES_NO_OPTIONS, 'text': 'Random board fill order', 'gradient': next(gradients)}))
    element_generator.send(('button_center_cell', "set_board_center_cell", next(positions), {'default_values': STRINGS.YES_NO_REVERSED, 'text': 'Center cell on board', 'gradient': next(gradients)}))
    element_generator.send(('button_pawns', "set_pawns_board", next(positions), {'default_values': CHARACTERS.PAWN_OPTIONS, 'text': 'Number of pawns', 'gradient': next(gradients)}))
    element_generator.send(('button_warriors', "set_warriors_board", next(positions), {'default_values': CHARACTERS.WARRIOR_OPTIONS, 'text': 'Number of warriors', 'gradient': next(gradients)}))
    element_generator.send(('button_wizards', "set_wizards_board", next(positions), {'default_values': CHARACTERS.WIZARD_OPTIONS, 'text': 'Number of wizards', 'gradient': next(gradients)}))
    element_generator.send(('button_priestesses', "set_priestess_board", next(positions), {'default_values': CHARACTERS.PRIESTESS_OPTIONS, 'text': 'Number of priestess', 'gradient': next(gradients)}))
    element_generator.send(('button_matrons', "set_matronmothers_board", next(positions), {'default_values': CHARACTERS.MATRONMOTHER_OPTIONS, 'text': 'Number of Matron Mothers', 'gradient': next(gradients)}))
    element_generator.send(('button_champions', "set_champions_board", next(positions), {'default_values': CHARACTERS.HOLYCHAMPION_OPTIONS, 'text': 'Number of Holy Champions', 'gradient': next(gradients)}))
    for end_event in threads:   end_event.wait()    #Waiting for all the buttons to be created
    HelpDialogs.add_help_dialogs("menu_params_config", elements, INIT_PARAMS.INITIAL_RESOLUTION)
    #Create Menu
    params_menu = Menu("menu_params_config", USEREVENTS.CONFIG_USEREVENT, INIT_PARAMS.INITIAL_RESOLUTION, *elements,\
                        background_path=PATHS.DEFAULT_BG, gradient = (RED, BLACK), do_align=False, songs_paths=None, scroll_texture=PATHS.DESERT_TEXTURE)
    result.append(params_menu)

@run_async
def create_sound_menu(result):
    #Sliders/buttons of the music and sound menu
    positions           = UtilityBox.size_position_generator(6, 0.80, 0.05)
    element_size        = next(positions)
    #Creation of elements
    elements, threads = [], []
    element_generator = generate_ui_elements(elements, threads, element_size, USEREVENTS.SOUND_USEREVENT, default_values=SOUND_PARAMS.INIT_VOLUME)
    element_generator.send(None)    #Starting generator
    #Starts generating
    element_generator.send(('slider_music_volume', "set_menu_music_volume", next(positions), {'text': 'Menus music volume', 'texture':PATHS.GOLD_SLIDER,'dial_texture':PATHS.SHIELD, 'bar_border': 30,'bar_texture': PATHS.BLUE_BAR, 'keep_aspect_ratio':False}))
    element_generator.send(('slider_sound_volume', "set_menu_sound_volume", next(positions), {'text': 'Menus sound volume', 'dial_texture':None, 'dial_shape': 'elliptical','bar_border': 35, 'bar_texture': PATHS.RED_BAR}))
    element_generator.send(('slider_board_music_volume', "set_board_music_volume", next(positions), {'text': 'Board music volume', 'texture':PATHS.BROWN_SLIDER, 'dial_shape': 'rectangular', 'bar_border': 6, 'bar_texture': PATHS.BROWN_BAR}))
    element_generator.send(('slider_board_sound_volume', "set_board_sound_volume", next(positions), {'text': 'Board sound volume', 'dial_texture':PATHS.CHEST}))
    element_generator.send(('button_board_song', "change_board_song", next(positions), {'text': 'Selected board song', 'default_values': BOARD_CROPPED_SONGS,'text_proportion': 0.50}))
    element_generator.send(('button_menu_song', "change_menu_song", next(positions), {'text': 'Selected menus song', 'default_values':MENU_CROPPED_SONGS}))
    for end_event in threads:   end_event.wait()    #Waiting for all the buttons to be created
    #Menu creation
    sound_menu          = Menu("menu_volume_music", USEREVENTS.SOUND_USEREVENT, INIT_PARAMS.INITIAL_RESOLUTION, *elements, background_path=PATHS.DEFAULT_BG, do_align=False, songs_paths=None)
    sound_menu.add_animation(AnimationGenerator.characters_crossing_screen(INIT_PARAMS.INITIAL_RESOLUTION, *INIT_PARAMS.ALL_FPS))
    sound_menu.enable_sprite('board', 'sound', state=False), sound_menu.enable_sprite('board', 'music', state=False), sound_menu.enable_sprite('board', 'song', state=False)
    result.append(sound_menu)

@run_async
def create_video_menu(result):
    positions           = UtilityBox.size_position_generator(5, 0.60, 0.10, 0.10, final_offset=0.15)
    button_size         = next(positions)
    #Creation of elements
    elements, threads = [], []
    element_generator = generate_ui_elements(elements, threads, button_size, USEREVENTS.GRAPHIC_USEREVENT, text_alignment='left', resize_mode='fill', text_proportion=0.45, texture=PATHS.DIAMOND_SPEAR)
    element_generator.send(None)    #Starting generator
    #Starts generating
    element_generator.send(('button_resolution', "change_resolution_screen_display", next(positions), {'text': 'Resolution', 'default_values': INIT_PARAMS.RESOLUTIONS}))
    element_generator.send(('button_fps', "change_fps_frames_per_second", next(positions), {'text': 'Frames per second', 'default_values': INIT_PARAMS.ALL_FPS, 'angle':180}))
    element_generator.send(('button_fullscreen', "set_display_mode_fullscreen", next(positions), {'text': 'Fullscreen', 'default_values': STRINGS.YES_NO_REVERSED, 'angle':None}))
    element_generator.send(('button_menu_bgs', "set_animated_background_menu", next(positions), {'text': 'Set menu background', 'default_values': STRINGS.ANIMATED_BGS, 'angle':180, 'text_proportion': 0.33}))
    element_generator.send(('button_board_bgs', "set_animated_background_board", next(positions), {'text': 'Set board background', 'angle':0}))
    for end_event in threads:   end_event.wait()    #Waiting for all the buttons to be created
    #Menu creation
    graphics_menu   = Menu("menu_graphics_display", USEREVENTS.GRAPHIC_USEREVENT, INIT_PARAMS.INITIAL_RESOLUTION, *elements, background_path=PATHS.DEFAULT_BG, do_align=False, songs_paths=None)
    graphics_menu.add_animation(AnimationGenerator.character_teleporting_screen(INIT_PARAMS.INITIAL_RESOLUTION, *INIT_PARAMS.ALL_FPS))
    result.append(graphics_menu)

def create_board_params():
    board_params = {}
    bg = AnimationGenerator.factory(STRINGS.INITIAL_ANIMATED_BG, INIT_PARAMS.INITIAL_RESOLUTION, PARAMS.ANIMATION_TIME, INIT_PARAMS.ALL_FPS, INIT_PARAMS.INITIAL_FPS)
    board_params['cell_border'] = PATHS.CELL_GOLDEN_BORDER 
    board_params['circumference_texture'] = PATHS.THIN_CIRCUMFERENCE
    board_params['songs_paths'] = BOARD_SONGS
    board_params['animated_background'] = bg
    #board_params['platform_sprite'] = AnimationGenerator.animated_tree_platform(INIT_PARAMS.INITIAL_RESOLUTION)
    board_params['platform_texture'] = PATHS.BASIC_TEXTURIZED_BG 
    board_params['interpath_texture'] = PATHS.WOOD_TEXTURE_DARK
    board_params['scoreboard_texture'] = PATHS.SCOREBOARD_BASIC
    board_params['infoboard_texture'] = PATHS.INFOBOARD_GRADIENT
    board_params['promotion_texture'] = PATHS.LONG_RED_BAR
    board_params['dice_textures_folder'] = PATHS.DICE_FOLDER
    return board_params

@time_it
@no_size_limit
def pre_start():
    start_pygame()
    draw_start_bg()
    game = Game('sava_drow', INIT_PARAMS.INITIAL_RESOLUTION, INIT_PARAMS.INITIAL_FPS)
    menus = []
    threads = [create_main_menu(menus), create_sound_menu(menus), create_config_menu(menus), create_video_menu(menus)]
    for menu_end_event in threads: menu_end_event.wait()
    game.add_screens(*menus)
    game.update_board_params(**create_board_params())
    return game
    
def draw_start_bg():
    start_bg = ResizedSurface.get_surface(PATHS.START_BG, INIT_PARAMS.INITIAL_RESOLUTION, 'fill', False)
    pygame.display.get_surface().blit(start_bg, (0, 0))
    pygame.display.flip()

if __name__ == "__main__":
    game = pre_start()
    game.start('main', 'menu')