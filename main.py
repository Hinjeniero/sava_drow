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

@run_async
def create_main_menu(result):   #TODO THIS COULD BE AN ONLY METHOD
    #Create elements, main menu buttons (POSITIONS AND SIZES ARE IN PERCENTAGES OF THE CANVAS_SIZE, can use absolute integers too)
    gradients       = UtilityBox.rainbow_gradient_generator(((255, 0, 0),(0, 0, 255)), 7)
    positions       = UtilityBox.size_position_generator(7, 0.40, 0.05, 0.20, 0)
    button_size     = next(positions)
    button_path     = PATHS.DARK_LONG_BUTTON
    buttonStart     = UIElement.factory('button_start', "start_game_go_main_board", USEREVENTS.MAINMENU_USEREVENT, next(positions), button_size,\
                                        INIT_PARAMS.INITIAL_RESOLUTION, text="Start new game", keep_aspect_ratio = False,\
                                        gradient=next(gradients), gradient_type='vertical', texture=button_path)
    buttonOnlineHost= UIElement.factory('button_online_host', "host_network_start_online_game_go_main_board", USEREVENTS.MAINMENU_USEREVENT, next(positions), button_size,\
                                        INIT_PARAMS.INITIAL_RESOLUTION, text="Host LAN game", keep_aspect_ratio = False,\
                                        gradient=next(gradients), gradient_type='vertical', texture=button_path)
    buttonOnlineCli = UIElement.factory('button_online_client', "client_network_start_online_game_go_main_board", USEREVENTS.MAINMENU_USEREVENT, next(positions), button_size,\
                                        INIT_PARAMS.INITIAL_RESOLUTION, text="Connect to LAN game", keep_aspect_ratio = False,\
                                        gradient=next(gradients), gradient_type='vertical', texture=button_path)
    buttonContinue  = UIElement.factory('button_continue', "continue_game_go_main_board", USEREVENTS.MAINMENU_USEREVENT, next(positions), button_size,\
                                        INIT_PARAMS.INITIAL_RESOLUTION, text="Continue last game", keep_aspect_ratio = False,\
                                        gradient=next(gradients), gradient_type='vertical', texture=button_path)
    buttonConfig    = UIElement.factory('button_params_menu', "go_menu_params_config", USEREVENTS.MAINMENU_USEREVENT, next(positions), button_size,\
                                        INIT_PARAMS.INITIAL_RESOLUTION, text="Parameters", gradient = next(gradients), gradient_type='vertical', texture=button_path, keep_aspect_ratio = False)
    buttonSound     = UIElement.factory('button_sound', "go_menu_sound_music", USEREVENTS.MAINMENU_USEREVENT, next(positions), button_size,\
                                        INIT_PARAMS.INITIAL_RESOLUTION, text="Music menu", gradient = next(gradients), gradient_type='vertical', texture=button_path, keep_aspect_ratio = False)
    buttonGraphics  = UIElement.factory('button_graphics', "go_menu_graphics_display", USEREVENTS.MAINMENU_USEREVENT, next(positions), button_size,\
                                        INIT_PARAMS.INITIAL_RESOLUTION, text="Graphics menu", gradient = next(gradients), gradient_type='vertical', texture=button_path, keep_aspect_ratio = False)
    buttonContinue.set_enabled(False)
    
    #Create Menu
    bg = AnimationGenerator.factory(STRINGS.INITIAL_ANIMATED_BG, INIT_PARAMS.INITIAL_RESOLUTION, PARAMS.ANIMATION_TIME, INIT_PARAMS.ALL_FPS, INIT_PARAMS.INITIAL_FPS)
    main_menu   = Menu('main_menu', USEREVENTS.MAINMENU_USEREVENT, INIT_PARAMS.INITIAL_RESOLUTION, buttonStart, buttonOnlineHost, buttonOnlineCli, buttonContinue, buttonConfig, buttonSound, buttonGraphics,
                        animated_background=bg, background_path=PATHS.DEFAULT_BG, songs_paths=MENU_SONGS, do_align=False)
    main_menu.add_dialogs(DialogGenerator.create_exit_dialog(tuple(x//2 for x in INIT_PARAMS.INITIAL_RESOLUTION), INIT_PARAMS.INITIAL_RESOLUTION))
    result.append(main_menu) 

@run_async
def create_config_menu(result):
    #positions           = UtilityBox.size_position_generator(9, 0.60, 0.05)
    #button_size         = next(positions)
    button_size = (0.60, 0.15)
    positions   = UtilityBox.size_position_generator_no_adjustment(*button_size, 0.05, 0.15)
    gradients   = UtilityBox.looped_rainbow_gradient_generator(((255, 0, 0), (0, 0, 0)), 3)
    #buttonLoadingScreen
    buttonLoadingScreen = UIElement.factory('button_loading', "change_loading_board", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=STRINGS.YES_NO_OPTIONS, text="Show screen while board loads", text_alignment='left',\
                                            gradient = next(gradients))
    buttonCountPlayers  = UIElement.factory('button_players', "add_players_board", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=PARAMS.PLAYERS_AMMOUNT, text="Number of players", text_alignment='left',\
                                            gradient = next(gradients))
    buttonGameModes     = UIElement.factory('button_game_mode', "change_game_mode", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=STRINGS.GAMEMODES, text="Game Mode", text_alignment='left',\
                                            gradient = next(gradients))
    buttonBoardSize     = UIElement.factory('button_board_size', "set_board_size", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=STRINGS.BOARD_SIZES, text="Board Size", text_alignment='left',\
                                            gradient = next(gradients))
    buttonRandomFilling = UIElement.factory('button_board_fill', "set_random_board_dropping_fill", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=STRINGS.YES_NO_OPTIONS, text="Random board fill order", text_alignment='left',\
                                            gradient = next(gradients))
    buttonCenterCell    = UIElement.factory('button_center_cell', "set_board_center_cell", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=STRINGS.YES_NO_REVERSED, text="Center cell on board", text_alignment='left',\
                                            gradient = next(gradients))
    buttonNumPawns      = UIElement.factory('button_pawns', "set_pawns_board", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=CHARACTERS.PAWN_OPTIONS, text="Number of pawns", text_alignment='left',\
                                            gradient = next(gradients))
    buttonNumWarriors   = UIElement.factory('button_warriors', "set_warriors_board", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=CHARACTERS.WARRIOR_OPTIONS, text="Number of warriors", text_alignment='left',\
                                            gradient = next(gradients))
    buttonNumWizards    = UIElement.factory('button_wizards', "set_wizards_board", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=CHARACTERS.WIZARD_OPTIONS, text="Number of wizards", text_alignment='left',\
                                            gradient = next(gradients))
    buttonNumPriestesses= UIElement.factory('button_priestesses', "set_priestess_board", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=CHARACTERS.PRIESTESS_OPTIONS, text="Number of priestess", text_alignment='left',\
                                            gradient = next(gradients))
    buttonNumMothers    = UIElement.factory('button_matrons', "set_matronmothers_board", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=CHARACTERS.MATRONMOTHER_OPTIONS, text="Number of Matron Mothers", text_alignment='left',\
                                            gradient = next(gradients))
    buttonHolyChampions = UIElement.factory('button_champions', "set_champions_board", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=CHARACTERS.HOLYCHAMPION_OPTIONS, text="Number of Holy Champions", text_alignment='left',\
                                            gradient = next(gradients))
    params_menu = Menu("menu_params_config", USEREVENTS.CONFIG_USEREVENT, INIT_PARAMS.INITIAL_RESOLUTION, buttonLoadingScreen, buttonCountPlayers, buttonGameModes, buttonBoardSize,\
                        buttonRandomFilling, buttonCenterCell, buttonNumPawns, buttonNumWarriors, buttonNumWizards, buttonNumPriestesses, buttonNumMothers, buttonHolyChampions,\
                        background_path=PATHS.DEFAULT_BG, gradient = (RED, BLACK), do_align=False, songs_paths=None)
    result.append(params_menu)

@run_async
def create_sound_menu(result):
    #Sliders/buttons of the music and sound menu
    positions           = UtilityBox.size_position_generator(6, 0.80, 0.05)
    button_size         = next(positions)
    #TODO create method in utilitybox for this shit
    sliderMenuMusic     = UIElement.factory('slider_music_volume', "set_menu_music_volume", USEREVENTS.SOUND_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=SOUND_PARAMS.INIT_VOLUME, text="Menus music volume", slider_type='circular',\
                                            gradient = (RED, BLACK), slider_start_color = RED, slider_end_color = WHITE)
    sliderMenuSounds    = UIElement.factory('slider_sound_volume', "set_menu_sound_volume", USEREVENTS.SOUND_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=SOUND_PARAMS.INIT_VOLUME, text="Menus sound volume", slider_type='elliptical')
    sliderBoardMusic    = UIElement.factory('slider_board_music_volume', "set_board_music_volume", USEREVENTS.SOUND_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=SOUND_PARAMS.INIT_VOLUME, text="Board music volume", slider_type='rectangular')
    sliderBoardSounds   = UIElement.factory('slider_board_sound_volume', "set_board_sound_volume", USEREVENTS.SOUND_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=SOUND_PARAMS.INIT_VOLUME, text="Board sound volume")
    buttonBoardSongs    = UIElement.factory('button_board_song', 'change_board_song', USEREVENTS.SOUND_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=BOARD_CROPPED_SONGS, text='Selected board song', text_proportion = 0.50)
    buttonMenusSongs    = UIElement.factory('button_menu_song', 'change_menu_song', USEREVENTS.SOUND_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=MENU_CROPPED_SONGS, text='Selected menus song', text_proportion = 0.50)
    #Deactivating board sounds, will be activated when the board is created and the game starts
    sliderBoardMusic.set_enabled(False)
    sliderBoardSounds.set_enabled(False)
    buttonBoardSongs.set_enabled(False)
    sound_menu          = Menu("menu_volume_music", USEREVENTS.SOUND_USEREVENT, INIT_PARAMS.INITIAL_RESOLUTION, sliderMenuMusic, sliderMenuSounds, sliderBoardMusic, sliderBoardSounds,\
                                buttonBoardSongs, buttonMenusSongs, background_path=PATHS.DEFAULT_BG, do_align=False, songs_paths=None)
    sound_menu.add_animation(AnimationGenerator.characters_crossing_screen(INIT_PARAMS.INITIAL_RESOLUTION, *INIT_PARAMS.ALL_FPS))
    result.append(sound_menu)

@run_async
def create_video_menu(result):
    positions           = UtilityBox.size_position_generator(5, 0.80, 0.10, 0.10, final_offset=0.15)
    button_size         = next(positions)
    buttonRes   = UIElement.factory('button_resolution', "change_resolution_screen_display", USEREVENTS.GRAPHIC_USEREVENT, next(positions), button_size,\
                                    INIT_PARAMS.INITIAL_RESOLUTION, default_values=INIT_PARAMS.RESOLUTIONS, text="Resolution",text_alignment='left')
    buttonFps   = UIElement.factory('button_fps', "change_fps_frames_per_second", USEREVENTS.GRAPHIC_USEREVENT, next(positions), button_size,\
                                    INIT_PARAMS.INITIAL_RESOLUTION, default_values=INIT_PARAMS.ALL_FPS, text="Frames per second",text_alignment='left')
    buttonFullscreen = UIElement.factory('button_fps', "set_display_mode_fullscreen", USEREVENTS.GRAPHIC_USEREVENT, next(positions), button_size,\
                                INIT_PARAMS.INITIAL_RESOLUTION, default_values=STRINGS.YES_NO_REVERSED, text="Fullscreen")                                    
    buttonBgsMenu   = UIElement.factory('button_menu_bgs', "set_animated_background_menu", USEREVENTS.GRAPHIC_USEREVENT, next(positions), button_size,\
                                    INIT_PARAMS.INITIAL_RESOLUTION, default_values=STRINGS.ANIMATED_BGS, text="Set menu background",text_alignment='left')
    buttonBgsBoard  = UIElement.factory('button__board_bgs', "set_animated_background_board", USEREVENTS.GRAPHIC_USEREVENT, next(positions), button_size,\
                                    INIT_PARAMS.INITIAL_RESOLUTION, default_values=STRINGS.ANIMATED_BGS, text="Set board background", text_alignment='left')
    graphics_menu   = Menu("menu_graphics_display", USEREVENTS.GRAPHIC_USEREVENT, INIT_PARAMS.INITIAL_RESOLUTION, buttonRes, buttonFps, buttonFullscreen,\
                            buttonBgsMenu, buttonBgsBoard, background_path=PATHS.DEFAULT_BG, do_align=False, songs_paths=None)
    graphics_menu.add_animation(AnimationGenerator.character_teleporting_screen(INIT_PARAMS.INITIAL_RESOLUTION, *INIT_PARAMS.ALL_FPS))
    result.append(graphics_menu)

def create_board_params():
    board_params = {}
    bg = AnimationGenerator.factory(STRINGS.INITIAL_ANIMATED_BG, INIT_PARAMS.INITIAL_RESOLUTION, PARAMS.ANIMATION_TIME, INIT_PARAMS.ALL_FPS, INIT_PARAMS.INITIAL_FPS)
    board_params['cell_texture'] = PATHS.CELL_BASIC
    board_params['cell_border'] = PATHS.CELL_GOLDEN_BORDER 
    board_params['circumference_texture'] = PATHS.CIRCUMFERENCE_RUST
    board_params['songs_paths'] = BOARD_SONGS
    board_params['animated_background'] = bg
    board_params['platform_sprite'] = AnimationGenerator.animated_tree_platform(INIT_PARAMS.INITIAL_RESOLUTION)
    return board_params

@time_it
def pre_start():
    start_pygame()
    draw_start_bg()
    game = Game('sava_drow', INIT_PARAMS.INITIAL_RESOLUTION, INIT_PARAMS.INITIAL_FPS)
    menus = []
    threads = [create_main_menu(menus), create_sound_menu(menus), create_config_menu(menus), create_video_menu(menus)]
    for menu_thread in threads:
        menu_thread.join()
    game.add_screens(*menus)
    game.update_board_params(**create_board_params())
    return game

@no_size_limit
def draw_start_bg():
    start_bg = ResizedSurface.get_surface(PATHS.START_BG, INIT_PARAMS.INITIAL_RESOLUTION, 'fill', False)
    pygame.display.get_surface().blit(start_bg, (0, 0))
    pygame.display.flip()

if __name__ == "__main__":
    game = pre_start()
    game.start()