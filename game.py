"""--------------------------------------------
game module. It's the overseer of all the modules of the game.
Highest level in the hierarchy.
Have the following classes:
    Game
--------------------------------------------"""
__all__ = ['Game']
__version__ = '0.2'
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
from ui_element import UIElement, TextSprite, InfoBoard
from colors import RED, BLACK, WHITE
from paths import IMG_FOLDER
from logger import Logger as LOG
from utility_box import UtilityBox
from exceptions import  NoScreensException, InvalidGameElementException,\
                        EmptyCommandException, ScreenNotFoundException

pygame.init()
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mouse.set_visible(True)
pygame.display.set_caption('sava drow')
pygame.display.set_mode((800, 600))
CHANGES_WERE_MADE   = False

class Game(object):
    def __init__(self, *screens, resolution=(1280, 720), mouse_visible=True, fps=60, show_fps=True, title="Game"):
        self.pygame_params      = self.generate_pygame_vars(resolution=resolution, fps=fps)
        self.screens            = []
        self.players            = [] 
        self.show_fps           = show_fps
        if len(screens) > 0:    self.add_elements(*screens) 
        else:                   raise NoScreensException("A game needs at least a screen to work")
        
        #Helpful but unnecesary attributes, only for the sake of clean code
        self.__current_screen   = self.screens[0]

    def add_elements(self, *elements):
        for element in elements:
            if isinstance(element, Screen): self.screens.append(element)
            else:                           raise InvalidGameElementException("Can't add an element of type "+str(type(element)))

    def generate_pygame_vars(self, resolution=(1280, 720), fps=60):
        params                  = {}
        params['fps']           = fps
        params['clock']         = pygame.time.Clock()
        params['clock'].tick(params['fps'])
        params['display']       = pygame.display.get_surface()
        if resolution is not params['display'].get_size(): 
            params['display']   = pygame.display.set_mode(resolution)
        LOG.log('INFO', "----Initial Pygame parameters----")
        LOG.log('INFO', "FPS: ", params['fps'])
        LOG.log('INFO', "RESOLUTION: ", params['display'].get_size())
        pygame.time.set_timer(pygame.USEREVENT+4, 1000//params['fps'])
        return params

    def change_pygame_var(self, command, value):
        LOG.log('DEBUG', "Requested change of pygame params: ", command, "->", value)
        global CHANGES_WERE_MADE
        CHANGES_WERE_MADE   = True
        cmd                 = command.lower()
        if len(cmd) <= 0:           raise EmptyCommandException("Received an empty command string")
        elif 'fps' in cmd:          self.pygame_params['clock'].tick(value)
        elif 'resolution' in cmd:   self.__set_resolution(value)
        elif 'music' in cmd:        pass
        elif 'sound' in cmd:        pass
    
    def __set_resolution(self, resolution):
        self.pygame_params['display'] = pygame.display.set_mode(resolution)
        for screen in self.screens:     screen.set_resolution(resolution)
        LOG.log('DEBUG', "Changed resolution to ", resolution)

    def event_handler(self, events):
        all_keys            = pygame.key.get_pressed()          #Get all the pressed keyboard keys
        all_mouse_buttons   = pygame.mouse.get_pressed()        #Get all the pressed mouse buttons
        mouse_pos           = pygame.mouse.get_pos()            #Get the current mouse position
        mouse_mvnt          = (pygame.mouse.get_rel() != (0,0)) #True if get_rel returns non zero vaalues

        for event in events:
            if event.type == pygame.QUIT:               return False
            elif event.type == pygame.KEYDOWN\
                and event.key == pygame.K_ESCAPE:       self.esc_handler()
            #elif event.type == pygame.KEYDOWN:          self.__keyboard_handler(event, keys_pressed)
            elif event.type >= pygame.USEREVENT:        self.user_command_handler(event)
            self.__current_screen.event_handler(event, all_keys, all_mouse_buttons, mouse_movement=mouse_mvnt, mouse_pos=mouse_pos)
        return True

    def esc_handler(self):
        LOG.log('DEBUG', "Pressed esc in ", self.__current_screen.id)
        id_screen = self.__current_screen.id.lower()
        if 'main' in id_screen and 'menu' in id_screen: self.__esc_main_menu()
        elif 'menu' in id_screen:                       self.__esc_menu()
        elif 'board' in id_screen:                      self.__esc_board()

    def __esc_board(self):
        self.change_screen("main", "menu")

    def __esc_menu(self):
        if CHANGES_WERE_MADE:   self.change_screen("main", "menu")
        else:                   self.change_screen("main", "menu")

    def __esc_main_menu(self):
        if self.__current_screen.have_dialog() and not self.__current_screen.dialog_is_active():        self.__current_screen.show_dialog()   
        elif self.__current_screen.have_dialog() and self.__current_screen.dialog_is_active():  self.__current_screen.hide_dialog()  

    def change_screen(self, *keywords):
        LOG.log('DEBUG', "Requested change of screen to ", keywords)
        count = 0
        for i in range(0, len(self.screens)):
            matches = len([0 for j in keywords if j in self.screens[i].id])
            if matches > count:   
                self.__current_screen = self.screens[i]
                count = matches
        if count is 0:  raise ScreenNotFoundException("A screen with those keywords wasn't found")
        else:           LOG.log('DEBUG', "Changed to  ", self.__current_screen.id)
 
    def user_command_handler(self, event):
        """Ou shit the user command handler, good luck m8
        USEREVENT when MENUS:           Change in settings
        UESREVENT+1 when MENUS:         Change of screen
        USEREVENT+2 when BOARD:         Action in them
        USEREVENT+3 when NOTIFICATIONS: popups and shit
        USEREVENT+4:                    Signal that forces drawing.
        """
        if event.type < pygame.USEREVENT:       return False
        elif event.type is pygame.USEREVENT:    self.change_pygame_var(event.command, event.value)
        elif event.type is pygame.USEREVENT+1:  self.change_screen(*event.command.split('_'))
        elif event.type is pygame.USEREVENT+2:  pass    #Board actions
        elif event.type is pygame.USEREVENT+3:  pass    #Dialog actions
        elif event.type is pygame.USEREVENT+4:          #Moment to draaaw, signal every fps/1sec
            self.__current_screen.draw(self.pygame_params['display'])
            if self.show_fps:
                UtilityBox.draw_fps(self.pygame_params['display'], self.pygame_params['clock'])
            pygame.display.update()

    def start(self):
        LOG.log('INFO', "GAME STARTING!")
        try:
            loop = True
            while loop:
                self.pygame_params['clock'].tick(self.pygame_params['fps'])
                loop = self.event_handler(pygame.event.get())
            sys.exit()
        except Exception as exc:
            raise exc
#List of (ids, text)
if __name__ == "__main__":
    resolutions = ((1280, 720), (1366, 768), (1600, 900), (640, 480), (800, 600), (1024, 768), (1280, 1024))
    pygame.display.set_mode(resolutions[0])
    res = resolutions[0]
    #Create elements, main menu buttons (POSITIONS AND SIZES ARE IN PERCENTAGES OF THE CANVAS_SIZE, can use absolute integers too)
    buttonStart         = UIElement.factory('button_start', "start_game_go_main_board", pygame.USEREVENT+1, (0.05, 0.10),\
                                            (0.90, 0.20), res, text="Start game", keep_aspect_ratio = False, texture=IMG_FOLDER+"//button.png")
    buttonParamsMenu    = UIElement.factory('button_params_menu', "go_menu_params_config", pygame.USEREVENT+1, (0.05, 0.40),\
                                            (0.90, 0.20), res, text="Parameters", gradient = (RED, BLACK))
    buttonSoundMenu     = UIElement.factory('button_sound', "go_menu_sound_music", pygame.USEREVENT+1, (0.05, 0.70), (0.90, 0.20),\
                                            res, text="Music menu", gradient = (RED, BLACK))
    #buttons of parameters menu
    buttonRes           = UIElement.factory('button_resolution',"change_resolution_screen_display", pygame.USEREVENT, (0.05, 0.05), (0.90, 0.10), res, default_values=resolutions, text="Resolution",     text_alignment = 'left')
    buttonCountPlayers  = UIElement.factory('button_players', "change_number_count_players",      pygame.USEREVENT, (0.05, 0.20), (0.90, 0.10), res, default_values=(2, 3, 4),   text="Number of players",   text_alignment = 'left')
    buttonNumPawns      = UIElement.factory('button_pawns', "change_number_count_pawns",        pygame.USEREVENT, (0.15, 0.35), (0.80, 0.10), res, default_values=(4, 8),      text="Number of pawns",     text_alignment = 'left')
    buttonNumWarriors   = UIElement.factory('button_warriors', "change_number_count_warriors",     pygame.USEREVENT, (0.15, 0.50), (0.80, 0.10), res, default_values=(1, 2, 4),   text="Number of warriors",  text_alignment = 'left')
    buttonNumWizards    = UIElement.factory('button_wizards', "change_number_count_wizards",      pygame.USEREVENT, (0.15, 0.65), (0.80, 0.10), res, default_values=(1, 2),      text="Number of wizards",   text_alignment = 'left')
    buttonNumPriestess  = UIElement.factory('button_priestesses', "change_number_count_priestess",    pygame.USEREVENT, (0.15, 0.80), (0.80, 0.10), res, default_values=(1, 1),      text="Number of priestess", text_alignment = 'left')
    
    '''#Exit dialog and its buttons
    dialog_resolution   = tuple(x//2 for x in res)
    dialog_position     = tuple(x//2-y//2 for x, y in zip(res, dialog_resolution))
    acceptButton        = UIElement.factory("accept_notification",          pygame.USEREVENT+2, (0.00, 0.80), (0.50, 0.20), dialog_resolution, None, text="ACCEPT") #Could do this in realtion with the total canvas size
    cancelButton        = UIElement.factory("cancel_notification",          pygame.USEREVENT+2, (0.50, 0.80), (0.50, 0.20), dialog_resolution, None, text="CANCEL")
    exitDialog          = UIElement.factory("exit_main_menu_notification",  pygame.USEREVENT+2, dialog_position, dialog_resolution, res, None, acceptButton, cancelButton, text="Exit this shit?")'''
    
    #Sliders of the music and sound menu
    sliderMenuMusic     = UIElement.factory('slider_music_volume', "change_menu_music_volume", pygame.USEREVENT, (0.05, 0.10), (0.80, 0.15), res, default_values=(0.75), text="Menus music volume", slider_type='circular',\
                        gradient = (RED, BLACK), slider_start_color = RED, slider_end_color = WHITE)
    sliderMenuSounds    = UIElement.factory('slider_sound_volume', "change_menu_sound_volume", pygame.USEREVENT, (0.05, 0.30), (0.80, 0.15), res, default_values=(0.75), text="Menus sound volume", slider_type='elliptical')
    sliderBoardMusic    = UIElement.factory('slider_board_music_volume', "change_board_music_volume",pygame.USEREVENT, (0.05, 0.50), (0.80, 0.15), res, default_values=(0.75), text="Board music volume", slider_type='rectangular')
    sliderBoardSounds   = UIElement.factory('slider_board_sound_volume', "change_board_sound_volume",pygame.USEREVENT, (0.05, 0.70), (0.80, 0.15), res, default_values=(0.75), text="Board sound volume")
    
    #Create Menu and board
    main_menu   = Menu("main_menu",         pygame.USEREVENT,   res,\
                buttonStart, buttonParamsMenu, buttonSoundMenu, background_path=IMG_FOLDER+'\\background.jpg')
    sound_menu  = Menu("menu_volume_music", pygame.USEREVENT+1, res,\
                sliderMenuMusic, sliderMenuSounds, sliderBoardMusic, sliderBoardSounds, background_path=IMG_FOLDER+'\\background.jpg')
    params_menu = Menu("menu_params_config",pygame.USEREVENT+1, res,\
                buttonRes, buttonCountPlayers, buttonNumPawns, buttonNumWarriors, buttonNumWizards, buttonNumPriestess, background_path=IMG_FOLDER+'\\background.jpg')

    main_board = Board("main_board", pygame.USEREVENT+7, res, background_path = IMG_FOLDER+'\\board_2.jpg')
    
    #TODO in only string form.
    textSprite1 = TextSprite("testSprite", (0, 0), (200, 100), res, "YESSS")
    textSprite2 = TextSprite("testSprite", (0, 0), (200, 100), res, "MaybBEEEE")
    textSprite3 = TextSprite("testSprite", (0, 0), (200, 100), res, "no.")
    textSprite4 = TextSprite("testSprite", (0, 0), (600, 100), res, "NUUUUNMAKLE")

                            #id_, userevent, element_position, element_size, canvas_size, *elements, **params
    infoboard = InfoBoard("test", USEREVENT+2, (0, 0), (400, 400), res, (textSprite1, 1), (textSprite2, 2), (textSprite3, 3), (textSprite4, 6))
    main_board.temp_infoboard = infoboard

    character_settings = {'pawn':{'number': 1, 'aliases':{'pickup': 'running'}},
                        'warrior':{'number': 1, 'aliases':{'pickup': 'run'}},
                        'wizard':{'number': 1, 'aliases':{'pickup': 'pick'}},
                        'priestess':{'number': 1, 'aliases':{'pickup': 'run'}},
                        'matron_mother':{'number': 0, 'path': IMG_FOLDER+'\\priestess', 'aliases':{'pickup': 'pick'}},
    }
    main_board.create_player("Zippotudo", 0, (100, 100), **character_settings)
    #TODO EACH PLAYERS GETS HIS INFOBOARD
    game = Game(main_menu, sound_menu, params_menu, main_board, title="Sava Drow", resolution=res)
    game.start()

