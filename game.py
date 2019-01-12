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
from ui_element import UIElement, TextSprite, InfoBoard, Dialog
from colors import RED, BLACK, WHITE
from paths import IMG_FOLDER, SOUND_FOLDER
from logger import Logger as LOG
from utility_box import UtilityBox
from board_generator import BoardGenerator
from exceptions import  NoScreensException, InvalidGameElementException,\
                        EmptyCommandException, ScreenNotFoundException

class Game(object):
    SOUND_KEYWORDS = ['sound', 'music', 'song']
    GRAPHIC_KEYWORDS = ['resolution', 'display', 'fps']
    CONFIG_KEYWORDS = ['char', 'player', 'mode', 'game', 'ammount', 'pawn', 'warrior',
                        'wizard', 'matron', 'priest']

    def __init__(self, id_, resolution, fps, **board_params):
        self.id             = id_
        self.display        = None  #Created in Game.generate()
        self.clock          = pygame.time.Clock()
        self.screens        = []
        self.started        = False
        self.resolution     = resolution
        self.fps            = fps
        self.last_inputs    = []    #Easter Eggs  
        self.game_config    = {}    #Created in Game.generate()
        self.current_screen = None  #Created in Game.start()
        self.board_generator= None  #Created in Game.generate()
        Game.generate(self)

    @staticmethod
    def generate(self):
        pygame.display.set_mode(self.resolution)
        self.display = pygame.display.get_surface()
        self.board_generator = BoardGenerator()
        #pygame.time.set_timer(pygame.USEREVENT+4, 1000//params['fps'])

    def add_screens(self, *screens):
        for screen in screens:
            if isinstance(screen, Screen):
                self.screens.append(screen)
            else:                           
                raise InvalidGameElementException('Can`t add an element of type '+str(type(screen)))

    def command_handler(self, command, value): #TODO Write here logic to handle board parameters (players and such) changes and shit
        LOG.log('DEBUG', 'Requested change of pygame params: ', command, '->', value)
        if len(command) > 0:
            cmd = command.lower()
            if any(kw in command for kw in Game.GRAPHIC_KEYWORDS):
                self.graphic_handler(cmd, value)
            elif any(kw in command for kw in Game.SOUND_KEYWORDS):
                self.sound_handler(cmd, value)
            elif any(kw in command for kw in Game.CONFIG_KEYWORDS):
                self.config_handler(cmd, value)
            else:
                LOG.log('INFO', 'Unknown command "', command, '"')
    
    def config_handler(self, command, value):
        if 'mode' in command or 'game' in command:
            self.board_generator.set_gamemode(value)
        if 'player' in command:
            self.board_generator.players = value
        if 'pawn' in command:
            self.board_generator.pawns = value
        if 'warrior' in command:
            self.board_generator.warriors = value
        if 'wizard' in command:
            self.board_generator.wizards = value
        if 'priestess' in command:
            self.board_generator.priestesses = value
        if 'matron' in command:
            self.board_generator.matron_mothers = value

    def graphic_handler(self, command, value):
        if 'fps' in command:          
            self.fps = value
            for screen in self.screens:
                screen.update_fps(value)
        elif 'res' in command:   
            self.resolution = value
            self.set_resolution(value)

    def set_resolution(self, resolution):
        self.display = pygame.display.set_mode(resolution)
        for screen in self.screens:     
            screen.set_resolution(resolution)
        LOG.log('DEBUG', "Changed resolution to ", resolution)

    def sound_handler(self, command, value):
        """Kinda an unconventional method, calls the whatever method """
        #Getting the affected screens:
        sound = True if 'sound' in command else False
        music = True if 'song' in command or 'music' in command else False
        change_volume = True if 'volume' in command else False
        change_song = True if ('change' in command or 'set' in command) and music else False
        affects_menus = True if 'menu' in command else False
        affects_boards = True if 'board' in command else False

        if change_volume:
            if affects_menus:
                self.call_screens_method('menu', Screen.set_volume, value, sound, music)
            if affects_boards:
                self.call_screens_method('board', Screen.set_volume, value, sound, music)
        elif change_song:
            if affects_menus:
                self.call_screens_method('menu', Screen.set_song, value)
            if affects_boards:
                self.call_screens_method('board', Screen.set_song, value)

    def event_handler(self, events):
        all_keys            = pygame.key.get_pressed()          #Get all the pressed keyboard keys
        all_mouse_buttons   = pygame.mouse.get_pressed()        #Get all the pressed mouse buttons
        mouse_pos           = pygame.mouse.get_pos()            #Get the current mouse position
        mouse_mvnt          = pygame.mouse.get_rel()!=(0,0)     #True if get_rel returns non zero vaalues

        for event in events:
            #For every event we will call this
            self.current_screen.event_handler(event, all_keys, all_mouse_buttons, mouse_movement=mouse_mvnt, mouse_pos=mouse_pos)
            if event.type == pygame.QUIT:               
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:        
                    self.esc_handler()
                else:
                    self.process_last_input(event)
            elif event.type >= pygame.USEREVENT:        
                self.user_command_handler(event)
        return False

    def process_last_input(self, event):
        self.current_screen.hide_popups()
        if len(self.last_inputs) > 20:
            del self.last_inputs[0]
        self.last_inputs.append(pygame.key.name(event.key))
        self.check_easter_eggs()

    def set_easter_eggs(self):
        res = self.resolution
        size = (900, 80)
        position = tuple(x//2 - y//2 for x, y in zip(res, size))
        image = IMG_FOLDER+'\\pixel_panel_2.png'
        text_size = 0.95
        popup_acho = UIElement.factory( 'secret_acho', '', 0, position, size, res, texture=image, keep_aspect_ratio=False,
                                        text='Gz, you found a secret! all your SFXs will be achos now.', text_proportion=text_size)
        popup_acho.use_overlay = False
        popup_running = UIElement.factory( 'secret_running', '', 0, position, size, res, texture=image, keep_aspect_ratio=False,
                                        text='Gz, you found a secret! The background music is now Running in the 90s.', text_proportion=text_size)
        popup_running.use_overlay = False
        popup_dejavu = UIElement.factory( 'secret_dejavu', '', 0, position, size, res, texture=image, keep_aspect_ratio=False,
                                        text='Gz, you found a secret! The background music is now Dejavu.', text_proportion=text_size)
        popup_dejavu.use_overlay = False
        for screen in self.screens:
            screen.add_popups(popup_acho, popup_running, popup_dejavu)

    def check_easter_eggs(self):
        secret = None
        easter_egg_sound = False
        easter_egg_music = False
        if len(self.last_inputs) > 3:
            if 'acho' in ''.join(self.last_inputs).lower():
                self.current_screen.show_popup('secret_acho')
                LOG.log('INFO', 'SECRET DISCOVERED! From now on all the sfxs on all the screens will be achos.')
                secret = 'acho.ogg'
                easter_egg_sound = True
            elif 'running' in ''.join(self.last_inputs).lower():
                self.current_screen.show_popup('secret_running')
                LOG.log('INFO', 'SECRET DISCOVERED! From now on the music in all your screens will be Running in the 90s.')
                secret = 'running90s.ogg'
                easter_egg_music = True
            elif 'dejavu' in ''.join(self.last_inputs).lower():
                self.current_screen.show_popup('secret_dejavu')
                LOG.log('INFO', 'SECRET DISCOVERED! From now on the music in all your screens will be Dejavu!')
                secret = 'dejavu.ogg'
                easter_egg_music = True

            if secret:
                self.current_screen.play_sound('secret')
                for screen in self.screens:
                    if easter_egg_sound:
                        screen.hijack_sound(SOUND_FOLDER+'\\secret\\'+secret)
                    elif easter_egg_music:
                        screen.hijack_music(SOUND_FOLDER+'\\secret\\'+secret)
                        for screen in self.screens:
                            for animation in screen.animations:
                                animation.speedup(3)
                    self.last_inputs.clear()
            
    def esc_handler(self):
        LOG.log('DEBUG', "Pressed esc in ", self.current_screen.id)
        id_screen = self.current_screen.id.lower()
        if 'main' in id_screen and 'menu' in id_screen: self.__esc_main_menu()
        elif 'menu' in id_screen:                       self.__esc_menu()
        elif 'board' in id_screen:                      self.__esc_board()

    def __esc_board(self):
        self.change_screen('main', 'menu')

    def __esc_menu(self):
        self.change_screen("main", "menu")

    def __esc_main_menu(self):
        if self.current_screen.have_dialog() and not self.current_screen.dialog_active():
            self.current_screen.show_dialog()   
        elif self.current_screen.have_dialog() and self.current_screen.dialog_active():  
            self.current_screen.hide_dialog()  

    def get_screen(self, *keywords):
        screen = None
        count = 0
        for i in range(0, len(self.screens)):
            matches = len([0 for j in keywords if j in self.screens[i].id])
            if matches > count:   
                screen = self.screens[i]
                count = matches
        return screen

    def call_screens_method(self, keywords, method, *method_args, **method_kwargs):
        #hasattr(Dynamo, 'mymethod') and callable(getattr(Dynamo, 'mymethod'))
        if isinstance(keywords, str):   #If it's only a keyword (A string)
            keywords = keywords,        #String to tuple
        try:
            for screen in self.screens:
                if all(kw in screen.id for kw in keywords):
                    method(screen, *method_args, **method_kwargs)
        except AttributeError:
            LOG.log('error', 'The method ', str(method), ' is not found in the class Screen')

    def change_screen(self, *keywords):
        LOG.log('DEBUG', "Requested change of screen to ", keywords)
        count = 0
        new_index = 0
        for i in range(0, len(self.screens)):
            matches = len([0 for j in keywords if j in self.screens[i].id])
            if matches > count:   
                count = matches
                new_index = i
        if count is not 0:
            if self.screens[new_index].has_music():
                self.current_screen.pause_music()
                self.current_screen = self.screens[new_index]
                self.current_screen.play_music()
            else:
                self.current_screen = self.screens[new_index]
            LOG.log('DEBUG', "Changed to  ", self.current_screen.id)
        else:  
            raise ScreenNotFoundException('A screen with any of the keywords'+ str(keywords)+'wasn`t found')

    def disable_params(self):
        #self.get_screen('main', 'menu').disable_sprite('params', 'button')
        self.get_screen('params', 'menu', 'config').disable_all_sprites()

    def user_command_handler(self, event):
        """Ou shit the user command handler, good luck m8
        USEREVENT when MENUS:           Change in current settings (Could be config, sound or graphics)
        UESREVENT+1 when MENUS:         Change of screen
        USEREVENT+2 when BOARD:         Action in them
        USEREVENT+3 when NOTIFICATIONS: popups and shit
        USEREVENT+4:                    Signal that forces drawing.
        """
        if event.type < pygame.USEREVENT:       
            return False
        elif event.type is pygame.USEREVENT:
            self.command_handler(event.command, event.value)
        elif event.type is pygame.USEREVENT+1:
            if 'start' in event.command and not self.started:
                self.initiate()
            self.change_screen(*event.command.split('_'))
        elif event.type is pygame.USEREVENT+2:  
            pass    #Board actions
        elif event.type is pygame.USEREVENT+3:  
            pass    #Dialog actions

    def check_state(self):
        if len(self.screens) > 0:
            if any(isinstance(screen, Menu) and 'main' in screen.id for screen in self.screens):
                return True
        raise NoScreensException('A game needs at least a main menu to start.')

    def first_log(self):
        LOG.log('INFO', "GAME STARTING!")
        LOG.log('INFO', "----Initial Pygame parameters----")
        LOG.log('INFO', "Game initial frames per second: ", self.fps)
        LOG.log('INFO', "RESOLUTION: ", self.display.get_size())

    def update_board_params(self, **params):
        self.board_generator.set_board_params(**params)

    def initiate(self):
        self.started = True
        self.screens.append(self.board_generator.generate_board(self.resolution))

    def start(self):
        try:
            self.set_easter_eggs()
            self.check_state()
            self.first_log()
            self.current_screen = self.screens[0]
            self.current_screen.play_music()
            while True:
                self.clock.tick(self.fps)
                end = self.event_handler(pygame.event.get())
                self.current_screen.draw(self.display)
                pygame.display.update()
                if end:
                    break
            sys.exit()
        except Exception as exc:
            raise exc

