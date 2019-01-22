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
from paths import IMG_FOLDER, SOUND_FOLDER
from logger import Logger as LOG
from utility_box import UtilityBox
from game import Game
from animation_generator import AnimationGenerator
from sprite import AnimatedSprite

#CONFIG
INITIAL_RESOLUTION = (1280, 720)
RESOLUTIONS = (INITIAL_RESOLUTION, (1366, 768), (1600, 900), (1920, 1080), (256, 144), (640, 360), (848, 480), (1024, 576))
INITIAL_FPS = 60
ALL_FPS = (INITIAL_FPS, 120, 20, 30)
#MUSIC
MENU_SONGS = UtilityBox.get_all_files(SOUND_FOLDER+'\\menu', '.ogg', '.mp3')
BOARD_SONGS = UtilityBox.get_all_files(SOUND_FOLDER+'\\board', '.ogg', '.mp3')
COMMON_SONGS = UtilityBox.get_all_files(SOUND_FOLDER+'\\common_music', '.ogg', '.mp3')
MENU_SONGS.extend(COMMON_SONGS)
BOARD_SONGS.extend(COMMON_SONGS)
#Music for the buttons, to show the titles and that shit
MENU_CROPPED_SONGS = [song.split('\\')[-1].split('.')[0] for song in MENU_SONGS]
BOARD_CROPPED_SONGS = [song.split('\\')[-1].split('.')[0] for song in BOARD_SONGS]
#GAMEMODES
GAMEMODES = ('Normal', 'Lite', 'Small', 'Extra', 'Huge', 'Insane', 'MemoryError')

def start_pygame(resolution=INITIAL_RESOLUTION):
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()
    pygame.mouse.set_visible(True)
    pygame.display.set_caption('sava drow')
    print(pygame.display.Info())
    pygame.display.set_mode(resolution, pygame.DOUBLEBUF)  

def create_dialog(text='You sure?'):
    #Dialog
    dialog = Dialog('dialog', pygame.USEREVENT, (500, 200), INITIAL_RESOLUTION, text=text)
    dialog.add_button(dialog.get_cols()//2, 'ok', 'whatever', gradient=((0, 0, 255, 255),(128, 128, 255, 255)))
    return dialog

def create_main_menu():
    #Create elements, main menu buttons (POSITIONS AND SIZES ARE IN PERCENTAGES OF THE CANVAS_SIZE, can use absolute integers too)
    gradients       = UtilityBox.rainbow_gradient_generator(((255, 0, 0),(0, 0, 255)), 4)
    positions       = UtilityBox.size_position_generator(4, 0.40, 0.05, 0.20, 0)
    button_size     = next(positions)
    #texture=IMG_FOLDER+"//button.png" #TO USE IN THE FIUTUR
    buttonStart     = UIElement.factory('button_start', "start_game_go_main_board", pygame.USEREVENT+1, next(positions), button_size,\
                                        INITIAL_RESOLUTION, text="Start game", keep_aspect_ratio = False,\
                                        gradient=next(gradients), gradient_type='vertical', texture=IMG_FOLDER+'\\button.png')
    buttonConfig    = UIElement.factory('button_params_menu', "go_menu_params_config", pygame.USEREVENT+1, next(positions),button_size,\
                                        INITIAL_RESOLUTION, text="Parameters", gradient = next(gradients), gradient_type='vertical', texture=IMG_FOLDER+'\\button.png', keep_aspect_ratio = False)
    buttonSound     = UIElement.factory('button_sound', "go_menu_sound_music", pygame.USEREVENT+1, next(positions), button_size,\
                                        INITIAL_RESOLUTION, text="Music menu", gradient = next(gradients), gradient_type='vertical', texture=IMG_FOLDER+'\\button.png', keep_aspect_ratio = False)
    buttonGraphics  = UIElement.factory('button_graphics', "go_menu_graphics_display", pygame.USEREVENT+1, next(positions), button_size,\
                                        INITIAL_RESOLUTION, text="Graphics menu", gradient = next(gradients), gradient_type='vertical', texture=IMG_FOLDER+'\\button.png', keep_aspect_ratio = False)
    #Create Menu
    #bg = AnimationGenerator.animated_waterfall_background(INITIAL_RESOLUTION, INITIAL_FPS, *ALL_FPS)
    #bg = AnimationGenerator.animated_cave_waterfall_background(INITIAL_RESOLUTION, INITIAL_FPS, *ALL_FPS)
    #bg = AnimationGenerator.animated_rain_tree(INITIAL_RESOLUTION, INITIAL_FPS, *ALL_FPS)
    #bg = AnimationGenerator.animated_rain_chinese(INITIAL_RESOLUTION, INITIAL_FPS, *ALL_FPS)
    bg = AnimationGenerator.industrial_layered_background(INITIAL_RESOLUTION, INITIAL_FPS, *ALL_FPS)
    main_menu   = Menu('main_menu', pygame.USEREVENT, INITIAL_RESOLUTION, buttonStart, buttonConfig, buttonSound, buttonGraphics,
                        animated_background= bg, background_path=IMG_FOLDER+'\\background.jpg', songs_paths=MENU_SONGS, dialog=create_dialog(),
                        do_align=False)
    return main_menu

def create_config_menu():
    #TODO DRAW NUMBER OF CHARS DOWN BELOW
    positions           = UtilityBox.size_position_generator(6, 0.80, 0.05)
    button_size         = next(positions)
    buttonGameModes     = UIElement.factory('button_game_mode', "change_game_mode", pygame.USEREVENT, next(positions), button_size,\
                                            INITIAL_RESOLUTION, default_values=GAMEMODES, text="Game Mode", text_alignment='left', gradient = (RED, BLACK))
    buttonCountPlayers  = UIElement.factory('button_players', "set_ammount_players", pygame.USEREVENT, next(positions), button_size,\
                                            INITIAL_RESOLUTION, default_values=(2, 4), text="Number of players", text_alignment='left', gradient = ((220, 0, 0, 255), (120, 120, 120, 255)))
    buttonNumPawns      = UIElement.factory('button_pawns', "set_ammount_pawns", pygame.USEREVENT, next(positions), button_size,\
                                            INITIAL_RESOLUTION, default_values=(4, 8), text="Number of pawns", text_alignment='left', gradient = ((170, 0, 0, 255), (170, 170, 170, 255)))
    buttonNumWarriors   = UIElement.factory('button_warriors', "set_ammount_warriors", pygame.USEREVENT, next(positions), button_size,\
                                            INITIAL_RESOLUTION, default_values=(1, 2, 4), text="Number of warriors", text_alignment='left', gradient = ((120, 0, 0, 255), (220, 220, 220, 255)))
    buttonNumWizards    = UIElement.factory('button_wizards', "set_ammount_wizards", pygame.USEREVENT, next(positions), button_size,
                                            INITIAL_RESOLUTION, default_values=(1, 2), text="Number of wizards", text_alignment='left')
    buttonNumPriestesses= UIElement.factory('button_priestesses', "set_ammount_priestess", pygame.USEREVENT, next(positions), button_size,\
                                            INITIAL_RESOLUTION, default_values=(1, 1), text="Number of priestess", text_alignment='left')
    params_menu = Menu("menu_params_config", pygame.USEREVENT+1, INITIAL_RESOLUTION, buttonGameModes, buttonCountPlayers, buttonNumPawns,\
                        buttonNumWarriors, buttonNumWizards, buttonNumPriestesses, background_path=IMG_FOLDER+'\\background.jpg', do_align=False)
    return params_menu

def create_sound_menu():
    #Sliders/buttons of the music and sound menu
    positions           = UtilityBox.size_position_generator(6, 0.80, 0.05)
    button_size         = next(positions)
    #TODO create method in utilitybox for this shit
    sliderMenuMusic     = UIElement.factory('slider_music_volume', "set_menu_music_volume", pygame.USEREVENT, next(positions), button_size,\
                                            INITIAL_RESOLUTION, default_values=(0.75), text="Menus music volume", slider_type='circular',\
                                            gradient = (RED, BLACK), slider_start_color = RED, slider_end_color = WHITE)
    sliderMenuSounds    = UIElement.factory('slider_sound_volume', "set_menu_sound_volume", pygame.USEREVENT, next(positions), button_size,\
                                            INITIAL_RESOLUTION, default_values=(0.75), text="Menus sound volume", slider_type='elliptical')
    sliderBoardMusic    = UIElement.factory('slider_board_music_volume', "set_board_music_volume", pygame.USEREVENT, next(positions), button_size,\
                                            INITIAL_RESOLUTION, default_values=(0.75), text="Board music volume", slider_type='rectangular')
    sliderBoardSounds   = UIElement.factory('slider_board_sound_volume', "set_board_sound_volume", pygame.USEREVENT, next(positions), button_size,\
                                            INITIAL_RESOLUTION, default_values=(0.75), text="Board sound volume")
    buttonBoardSongs    = UIElement.factory('button_board_song', 'change_board_song', pygame.USEREVENT, next(positions), button_size,\
                                            INITIAL_RESOLUTION, default_values=BOARD_CROPPED_SONGS, text='Selected board song', text_proportion = 0.50)
    buttonMenusSongs    = UIElement.factory('button_menu_song', 'change_menu_song', pygame.USEREVENT, next(positions), button_size,\
                                            INITIAL_RESOLUTION, default_values=MENU_CROPPED_SONGS, text='Selected menus song', text_proportion = 0.50)
    #Deactivating board sounds, will be activated when the board is created and the game starts
    sliderBoardMusic.set_enabled(False)
    sliderBoardSounds.set_enabled(False)
    buttonBoardSongs.set_enabled(False)
    sound_menu          = Menu("menu_volume_music", pygame.USEREVENT+1, INITIAL_RESOLUTION, sliderMenuMusic, sliderMenuSounds, sliderBoardMusic, sliderBoardSounds,\
                                buttonBoardSongs, buttonMenusSongs, background_path=IMG_FOLDER+'\\background.jpg', do_align=False)
    sound_menu.add_animation(AnimationGenerator.characters_crossing_screen(INITIAL_RESOLUTION, *ALL_FPS))
    return sound_menu

def create_video_menu():
    positions           = UtilityBox.size_position_generator(3, 0.80, 0.10, 0.10, final_offset=0.15)
    button_size         = next(positions)
    buttonRes   = UIElement.factory('button_resolution',"change_resolution_screen_display", pygame.USEREVENT, next(positions), button_size,\
                                    INITIAL_RESOLUTION, default_values=RESOLUTIONS, text="Resolution",text_alignment='left')
    buttonFps   = UIElement.factory('button_fps', "change_fps_frames_per_second", pygame.USEREVENT, next(positions), button_size,\
                                    INITIAL_RESOLUTION, default_values=ALL_FPS, text="Frames per second",text_alignment='left')
    buttonFullscreen = UIElement.factory('button_fps', "set_display_mode_fullscreen", pygame.USEREVENT, next(positions), button_size,\
                                INITIAL_RESOLUTION, default_values=('Off', 'On'), text="Fullscreen")                                    
    graphics_menu  = Menu(  "menu_graphics_display", pygame.USEREVENT+1, INITIAL_RESOLUTION, buttonRes, buttonFps, buttonFullscreen,\
                            background_path=IMG_FOLDER+'\\background.jpg', do_align=False)
    graphics_menu.add_animation(AnimationGenerator.character_teleporting_screen(INITIAL_RESOLUTION, *ALL_FPS))
    return graphics_menu

def create_board_params():
    board_params = {}
    #board_params['background_path'] = IMG_FOLDER+'\\board_2.jpg'
    board_params['songs_paths'] = BOARD_SONGS
    board_params['animated_background'] = AnimationGenerator.animated_cave_waterfall_background(INITIAL_RESOLUTION, INITIAL_FPS, *ALL_FPS)
    board_params['platform_sprite'] = AnimationGenerator.animated_tree_platform(INITIAL_RESOLUTION)
    return board_params

def main():
    start_pygame()
    game = Game('sava_drow', INITIAL_RESOLUTION, INITIAL_FPS)
    game.add_screens(create_main_menu(), create_sound_menu(), create_config_menu(), create_video_menu())
    game.update_board_params(**create_board_params())
    game.start()

if __name__ == "__main__":
    main()