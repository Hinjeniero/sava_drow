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
from pygame.locals import *
from pygame.key import *
from screen import Screen
#Selfmade Libraries
from board import Board
from menu import Menu
from ui_element import UIElement, TextSprite, InfoBoard, Dialog
from colors import RED, BLACK, WHITE, GREEN
from logger import Logger as LOG
from utility_box import UtilityBox
from game import Game
from animation_generator import AnimationGenerator
from sprite import AnimatedSprite
from settings import USEREVENTS, INIT_PARAMS, PATHS, CHARACTERS, PARAMS,\
                    STRINGS, EXTENSIONS, SCREEN_FLAGS, SOUND_PARAMS
#This because segmentation fault
import faulthandler
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

def create_dialog(text='You sure?'):
    #Dialog
    dialog = Dialog('dialog', USEREVENTS.DIALOG_USEREVENT, (500, 200), INIT_PARAMS.INITIAL_RESOLUTION, text=text)
    dialog.add_button(dialog.get_cols()//2, 'ok', 'whatever', gradient=((0, 0, 255, 255),(128, 128, 255, 255)))
    return dialog

def create_main_menu():
    #Create elements, main menu buttons (POSITIONS AND SIZES ARE IN PERCENTAGES OF THE CANVAS_SIZE, can use absolute integers too)
    gradients       = UtilityBox.rainbow_gradient_generator(((255, 0, 0),(0, 0, 255)), 5)
    positions       = UtilityBox.size_position_generator(5, 0.40, 0.05, 0.20, 0)
    button_size     = next(positions)
    #texture=IMG_FOLDER+"//button.png" #TO USE IN THE FIUTUR
    buttonStart     = UIElement.factory('button_start', "start_game_go_main_board", USEREVENTS.MAINMENU_USEREVENT, next(positions), button_size,\
                                        INIT_PARAMS.INITIAL_RESOLUTION, text="Start new game", keep_aspect_ratio = False,\
                                        gradient=next(gradients), gradient_type='vertical', texture=PATHS.SHORT_BUTTON)
    buttonContinue  = UIElement.factory('button_continue', "continue_game_go_main_board", USEREVENTS.MAINMENU_USEREVENT, next(positions), button_size,\
                                        INIT_PARAMS.INITIAL_RESOLUTION, text="Continue last game", keep_aspect_ratio = False,\
                                        gradient=next(gradients), gradient_type='vertical', texture=PATHS.SHORT_BUTTON)
    buttonConfig    = UIElement.factory('button_params_menu', "go_menu_params_config", USEREVENTS.MAINMENU_USEREVENT, next(positions),button_size,\
                                        INIT_PARAMS.INITIAL_RESOLUTION, text="Parameters", gradient = next(gradients), gradient_type='vertical', texture=PATHS.SHORT_BUTTON, keep_aspect_ratio = False)
    buttonSound     = UIElement.factory('button_sound', "go_menu_sound_music", USEREVENTS.MAINMENU_USEREVENT, next(positions), button_size,\
                                        INIT_PARAMS.INITIAL_RESOLUTION, text="Music menu", gradient = next(gradients), gradient_type='vertical', texture=PATHS.SHORT_BUTTON, keep_aspect_ratio = False)
    buttonGraphics  = UIElement.factory('button_graphics', "go_menu_graphics_display", USEREVENTS.MAINMENU_USEREVENT, next(positions), button_size,\
                                        INIT_PARAMS.INITIAL_RESOLUTION, text="Graphics menu", gradient = next(gradients), gradient_type='vertical', texture=PATHS.SHORT_BUTTON, keep_aspect_ratio = False)
    buttonContinue.set_enabled(False)
    
    #Create Menu
    #bg = AnimationGenerator.animated_waterfall_background(INIT_PARAMS.INITIAL_RESOLUTIO, PARAMS.ANIMATION_TIME,, *INIT_PARAMS.ALL_FPS)
    #bg = AnimationGenerator.animated_cave_waterfall_background(INIT_PARAMS.INITIAL_RESOLUTIO, PARAMS.ANIMATION_TIME,, *INIT_PARAMS.ALL_FPS)
    #bg = AnimationGenerator.animated_rain_tree(INIT_PARAMS.INITIAL_RESOLUTIO, PARAMS.ANIMATION_TIME,, *INIT_PARAMS.ALL_FPS)
    #bg = AnimationGenerator.animated_rain_chinese(INIT_PARAMS.INITIAL_RESOLUTIO, PARAMS.ANIMATION_TIME,, *INIT_PARAMS.ALL_FPS)
    bg = AnimationGenerator.industrial_layered_background(INIT_PARAMS.INITIAL_RESOLUTION, PARAMS.ANIMATION_TIME, *INIT_PARAMS.ALL_FPS)
    main_menu   = Menu('main_menu', USEREVENTS.MAINMENU_USEREVENT, INIT_PARAMS.INITIAL_RESOLUTION, buttonStart, buttonContinue, buttonConfig, buttonSound, buttonGraphics,
                        animated_background= bg, background_path=PATHS.DEFAULT_BG, songs_paths=MENU_SONGS, dialog=create_dialog(),
                        do_align=False)
    
    vertical_shit = UIElement.factory('button_graphics', "go_menu_graphics_display", USEREVENTS.MAINMENU_USEREVENT, (1100, 50), (0.05, 0.80),\
                                        INIT_PARAMS.INITIAL_RESOLUTION, text="YES", default_values=0, gradient_type='vertical')
    main_menu.add_sprites(vertical_shit)
    return main_menu 

def create_config_menu():
    #TODO DRAW NUMBER OF CHARS DOWN BELOW, IN AN ANIMATION. (TOO MUCH WORK)
    positions           = UtilityBox.size_position_generator(9, 0.60, 0.05)
    button_size         = next(positions)
    
    #buttonLoadingScreen
    buttonLoadingScreen = UIElement.factory('button_game_mode', "set_loading_board", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=STRINGS.YES_NO_OPTIONS, text="Show screen while board loads", text_alignment='left',\
                                            gradient = (RED, BLACK))
    buttonRandomFilling = UIElement.factory('button_game_mode', "set_random_board_cells_fill", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=STRINGS.YES_NO_OPTIONS, text="Random board fill order", text_alignment='left',\
                                            gradient = (RED, BLACK))
    buttonGameModes     = UIElement.factory('button_game_mode', "change_game_mode", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=STRINGS.GAMEMODES, text="Game Mode", text_alignment='left',\
                                            gradient = (RED, BLACK))
    buttonCountPlayers  = UIElement.factory('button_players', "set_ammount_players", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=PARAMS.PLAYERS_AMMOUNT, text="Number of players", text_alignment='left',\
                                            gradient = (RED, BLACK))
    buttonNumPawns      = UIElement.factory('button_pawns', "set_ammount_pawns", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=CHARACTERS.PAWN_OPTIONS, text="Number of pawns", text_alignment='left',\
                                            gradient = (RED, BLACK))
    buttonNumWarriors   = UIElement.factory('button_warriors', "set_ammount_warriors", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=CHARACTERS.WARRIOR_OPTIONS, text="Number of warriors", text_alignment='left',\
                                            gradient = (RED, BLACK))
    buttonNumWizards    = UIElement.factory('button_wizards', "set_ammount_wizards", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=CHARACTERS.WIZARD_OPTIONS, text="Number of wizards", gradient = (RED, BLACK), text_alignment='left')
    buttonNumPriestesses= UIElement.factory('button_priestesses', "set_ammount_priestess", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=CHARACTERS.PRIESTESS_OPTIONS, text="Number of priestess", gradient = (RED, BLACK), text_alignment='left')
    buttonNumMothers    = UIElement.factory('button_matrons', "set_ammount_matronmothers", USEREVENTS.CONFIG_USEREVENT, next(positions), button_size,\
                                            INIT_PARAMS.INITIAL_RESOLUTION, default_values=CHARACTERS.MATRONMOTHER_OPTIONS, text="Number of Matron Mothers", text_alignment='left')
    params_menu = Menu("menu_params_config", USEREVENTS.CONFIG_USEREVENT, INIT_PARAMS.INITIAL_RESOLUTION, buttonLoadingScreen, buttonRandomFilling, buttonGameModes, buttonCountPlayers, buttonNumPawns,\
                        buttonNumWarriors, buttonNumWizards, buttonNumPriestesses, buttonNumMothers, background_path=PATHS.DEFAULT_BG, gradient = (RED, BLACK), do_align=False)
    return params_menu

def create_sound_menu():
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
                                buttonBoardSongs, buttonMenusSongs, background_path=PATHS.DEFAULT_BG, do_align=False)
    sound_menu.add_animation(AnimationGenerator.characters_crossing_screen(INIT_PARAMS.INITIAL_RESOLUTION, *INIT_PARAMS.ALL_FPS))
    return sound_menu

def create_video_menu():
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
                            buttonBgsMenu, buttonBgsBoard, background_path=PATHS.DEFAULT_BG, do_align=False)
    graphics_menu.add_animation(AnimationGenerator.character_teleporting_screen(INIT_PARAMS.INITIAL_RESOLUTION, *INIT_PARAMS.ALL_FPS))
    return graphics_menu

def create_board_params():
    board_params = {}
    board_params['songs_paths'] = BOARD_SONGS
    board_params['animated_background'] = AnimationGenerator.animated_cave_waterfall_background(INIT_PARAMS.INITIAL_RESOLUTION,\
                                        INIT_PARAMS.INITIAL_FPS, *INIT_PARAMS.ALL_FPS)
    board_params['platform_sprite'] = AnimationGenerator.animated_tree_platform(INIT_PARAMS.INITIAL_RESOLUTION)
    return board_params

def main():
    start_pygame()
    game = Game('sava_drow', INIT_PARAMS.INITIAL_RESOLUTION, INIT_PARAMS.INITIAL_FPS)
    game.add_screens(create_main_menu(), create_sound_menu(), create_config_menu(), create_video_menu())
    game.update_board_params(**create_board_params())
    game.start()

if __name__ == "__main__":
    main()