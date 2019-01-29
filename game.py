"""--------------------------------------------
game module. It's the overseer of all the modules of the game.
Highest level in the hierarchy.
Have the following classes:
    Game
--------------------------------------------"""
__all__ = ['Game']
__version__ = '0.5'
__author__ = 'David Flaity Pardo'

#Python librariess
import pygame
import os
import threading
import sys
from pygame.locals import *
from pygame.key import *
from obj.screen import Screen
#Selfmade Libraries
from obj.utilities.decorators import run_async
from obj.board import Board
from obj.menu import Menu
from obj.ui_element import UIElement, TextSprite, InfoBoard, Dialog
from obj.utilities.colors import RED, BLACK, WHITE
from obj.utilities.logger import Logger as LOG
from obj.utilities.utility_box import UtilityBox
from board_generator import BoardGenerator
from obj.utilities.exceptions import  NoScreensException, InvalidGameElementException,\
                        EmptyCommandException, ScreenNotFoundException, TooManyCharactersException
from obj.utilities.surface_loader import ResizedSurface
from settings import PATHS, USEREVENTS, SCREEN_FLAGS, INIT_PARAMS, PARAMS
from animation_generator import AnimationGenerator

class Game(object):
    def __init__(self, id_, resolution, fps, **board_params):
        self.id             = id_
        self.display        = None  #Created in Game.generate()
        self.clock          = pygame.time.Clock()
        self.screens        = []
        self.started        = False
        self.resolution     = resolution
        self.fps            = fps
        self.fps_text       = None
        self.last_inputs    = []    #Easter Eggs  
        self.game_config    = {}    #Created in Game.generate()
        self.current_screen = None  #Created in Game.start()
        self.board_generator= None  #Created in Game.generate()
        self.popups         = pygame.sprite.OrderedUpdates()  
        self.fullscreen     = False
        Game.generate(self)

    @staticmethod
    def generate(self):
        pygame.display.set_mode(self.resolution)
        self.display = pygame.display.get_surface()
        self.board_generator = BoardGenerator()
        self.set_timers()

    def set_timers(self):
        pygame.time.set_timer(USEREVENTS.TIMER_ONE_SEC, 1000) #Each second

    def add_screens(self, *screens):
        for screen in screens:
            if isinstance(screen, Screen):
                self.screens.append(screen)
            else:
                raise InvalidGameElementException('Can`t add an element of type '+str(type(screen)))

    def user_command_handler(self, event):
        """Ou shit the user command handler, good luck m8
        USEREVENT+0: Change of screens
        UESREVENT+1: Change in sound settings
        USEREVENT+2: Change in graphic settings
        USEREVENT+3: Change in board configuration settings
        USEREVENT+4: Action in board. Unused rn.
        USEREVENT+5: Action in dialogs/etc. Unused rn.
        USEREVENT+6: Signals the end of the current board.
        USEREVENT+7: Called every second. Timer.
        """
        if event.type < pygame.USEREVENT:       
            return False
        elif event.type is USEREVENTS.MAINMENU_USEREVENT:
            if 'start' in event.command.lower():
                self.initiate()
            self.change_screen(*event.command.lower().split('_'))
        elif event.type is USEREVENTS.SOUND_USEREVENT:
            self.sound_handler(event.command.lower(), event.value)
        elif event.type is USEREVENTS.GRAPHIC_USEREVENT:  
            self.graphic_handler(event.command.lower(), event.value)
        elif event.type is USEREVENTS.CONFIG_USEREVENT:  
            self.config_handler(event.command.lower(), event.value)
        elif event.type is USEREVENTS.DIALOG_USEREVENT:
            if 'scroll' in event.command:
                self.current_screen.set_scroll(event.value)
        elif event.type is USEREVENTS.END_CURRENT_GAME:
            self.show_popup('win')
            self.current_screen.play_sound('win')
            self.started = False
            self.change_screen('main', 'menu')
            self.get_screen('params', 'menu', 'config').enable_all_sprites(True)
            self.get_screen('main', 'menu').enable_sprites(False, 'continue')
            #TODO REstart params of params menu
        elif event.type is USEREVENTS.TIMER_ONE_SEC:
            self.fps_text = UtilityBox.generate_fps(self.clock, size=tuple(int(x*0.05) for x in self.resolution))
    
    def config_handler(self, command, value):
        characters = ('pawn', 'warrior', 'wizard', 'priestess', 'matron')
        if 'game' in command or 'mode' in command:
            self.board_generator.set_game_mode(value)
            if not 'custom' in value.lower() or 'free' in value.lower():
                self.get_screen('params', 'menu', 'config').enable_sprites(False, 'set', 'board')
            else:
                self.get_screen('params', 'menu', 'config').enable_all_sprites()
        elif 'size' in command:
            self.board_generator.set_board_size(value)
        elif 'player' in command:
            self.board_generator.players = value
        elif any(char in command for char in characters):
            self.board_generator.set_character_ammount(command, value)
        elif 'loading' in command:
            if 'on' in value.lower() or value == 1 or 'yes' in value.lower():
                self.board_generator.set_board_params(loading_screen=True)
            else:
                self.board_generator.set_board_params(loading_screen=False)
        elif 'center' in command:
            if 'on' in value.lower() or value == 1 or 'yes' in value.lower():
                self.board_generator.set_board_params(center_cell=True)
            else:
                self.board_generator.set_board_params(center_cell=False)
        elif 'fill' in command or 'drop' in command:
            if 'on' in value.lower() or value == 1 or 'yes' in value.lower():
                self.board_generator.set_board_params(random_filling=True)
            else:
                self.board_generator.set_board_params(random_filling=False)

    def graphic_handler(self, command, value):
        if 'fps' in command:          
            self.fps = value
            for screen in self.screens:
                screen.update_fps(value)
        elif 'res' in command:   
            self.resolution = value
            self.set_resolution(value)
        elif 'fullscreen' in command:
            if 'on' in value.lower() or value == 1 or 'yes' in value.lower():
                self.display = pygame.display.set_mode(self.resolution, SCREEN_FLAGS.FULLSCREEN)
                self.fullscreen = True
            else:
                self.display = pygame.display.set_mode(self.resolution, SCREEN_FLAGS.WINDOWED)
                self.fullscreen = False
        elif 'bg' in command or 'background' in command:
            if 'menu' in command:
                self.set_background(self.get_screen('main', 'menu'), value)
            elif 'board' in command:
                self.set_background(self.get_screen('board'), value)

    def set_resolution(self, resolution):
        if self.fullscreen:
            self.display = pygame.display.set_mode(self.resolution, SCREEN_FLAGS.FULLSCREEN)
        else:
            self.display = pygame.display.set_mode(self.resolution, SCREEN_FLAGS.WINDOWED)
        ResizedSurface.clear_lut()  #Clear the lut of resized surfaces
        for screen in self.screens:
            screen.set_resolution(resolution)
        for popup in self.popups.sprites():
            popup.set_canvas_size(resolution)
        LOG.log('DEBUG', "Changed resolution to ", resolution)

    @run_async
    def set_background(self, screen, new_bg_id):
        new_animated_bg = AnimationGenerator.factory(new_bg_id, self.resolution, PARAMS.ANIMATION_TIME,\
                                                    INIT_PARAMS.ALL_FPS, self.fps)
        screen.animated_background = True
        screen.background = new_animated_bg

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
        if any(all_mouse_buttons):
            self.hide_popups()
        for event in events:
            #For every event we will call this
            self.current_screen.event_handler(event, all_keys, all_mouse_buttons, mouse_movement=mouse_mvnt, mouse_pos=mouse_pos)
            if event.type == pygame.QUIT:               
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:        
                    self.esc_handler()
                elif event.key == pygame.K_F4 and (all_keys[pygame.K_LALT] or all_keys[pygame.K_RALT]):
                    return True
                else:
                    self.process_last_input(event)
            elif event.type >= pygame.USEREVENT:        
                self.user_command_handler(event)
        return False

    def process_last_input(self, event):
        self.hide_popups()
        if len(self.last_inputs) > 20:
            del self.last_inputs[0]
        self.last_inputs.append(pygame.key.name(event.key))
        self.check_easter_eggs()

    def set_easter_eggs(self):
        res = self.resolution
        size = (900, 80)
        position = tuple(x//2 - y//2 for x, y in zip(res, size))
        image = PATHS.LONG_POPUP
        text_size = 0.95
        popup_acho = UIElement.factory( 'secret_acho', '', 0, position, size, res, texture=image, keep_aspect_ratio=False,
                                        text='Gz, you found a secret! all your SFXs will be achos now.', text_proportion=text_size)
        popup_acho.use_overlay = False
        popup_running = UIElement.factory('secret_running90s', '', 0, position, size, res, texture=image, keep_aspect_ratio=False,
                                        text='Gz, you found a secret! The background music is now Running in the 90s.', text_proportion=text_size)
        popup_running.use_overlay = False
        popup_dejavu = UIElement.factory('secret_dejavu', '', 0, position, size, res, texture=image, keep_aspect_ratio=False,
                                        text='Gz, you found a secret! The background music is now Dejavu.', text_proportion=text_size)
        popup_dejavu.use_overlay = False
        popup_chars  = UIElement.factory('toomany_chars', '', 0, position, size, res, texture=image, keep_aspect_ratio=False,
                                        text='Too many chars, change the params.', text_proportion=text_size)
        popup_chars.use_overlay = False
        popup_winner = UIElement.factory('winner', '', 0, position, size, res, texture=image, keep_aspect_ratio=False,
                                        text='Gz, you won!', text_proportion=text_size)                                        
        self.add_popups(popup_acho, popup_running, popup_dejavu, popup_winner, popup_chars)

    def add_popups(self, *popups):
        for popup in popups:
            popup.set_active(False)
            popup.set_visible(False)
            self.popups.add(popup)

    def show_popup(self, id_):
        for popup in self.popups.sprites():
            if id_ in popup.id:
                popup.set_visible(True)
                popup.set_active(True)
                return
        LOG.log('debug', 'Popup ', id_,'not found')
    
    def hide_popups(self):
        for popup in self.popups.sprites():
            popup.set_active(False)
            popup.set_visible(False)

    def check_easter_eggs(self):
        secret = None
        easter_egg_sound = False
        easter_egg_music = False
        if len(self.last_inputs) > 3:
            if 'acho' in ''.join(self.last_inputs).lower():
                LOG.log('INFO', 'SECRET DISCOVERED! From now on all the sfxs on all the screens will be achos.')
                secret = 'acho.ogg'
                easter_egg_sound = True
            elif 'running' in ''.join(self.last_inputs).lower():
                LOG.log('INFO', 'SECRET DISCOVERED! From now on the music in all your screens will be Running in the 90s.')
                secret = 'running90s.ogg'
                easter_egg_music = True
            elif 'dejavu' in ''.join(self.last_inputs).lower():
                LOG.log('INFO', 'SECRET DISCOVERED! From now on the music in all your screens will be Dejavu!')
                secret = 'dejavu.ogg'
                easter_egg_music = True
            #If an easter egg was triggered:
            if secret:
                self.show_popup(secret.split('.')[0])
                self.current_screen.play_sound('secret')
                for screen in self.screens:
                    if easter_egg_sound:
                        screen.hijack_sound(PATHS.SECRET_FOLDER+secret)
                    elif easter_egg_music:
                        screen.hijack_music(PATHS.SECRET_FOLDER+secret)
                        for animation in screen.animations:
                            animation.speedup(2)
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

    def enable_board_sliders(self):
        self.get_screen('music', 'menu').enable_all_sprites()

    def check_state(self):
        if len(self.screens) > 0:
            if any(isinstance(screen, Menu) and 'main' in screen.id for screen in self.screens):
                return True
        raise NoScreensException('A game needs at least a main menu to start.')

    def init_log(self):
        LOG.log('INFO', "GAME STARTING!")
        LOG.log('INFO', "----Initial Pygame parameters----")
        LOG.log('INFO', "Game initial frames per second: ", self.fps)
        LOG.log('INFO', "RESOLUTION: ", self.display.get_size())

    def update_board_params(self, **params):
        self.board_generator.set_board_params(**params)

    def initiate(self):
        try:
            if self.get_screen('board'):
                for i in range(0, len(self.screens)):
                    if 'board' in self.screens[i].id:
                        old_board = self.screens[i]
                        self.screens[i] = self.board_generator.generate_board(self.resolution)
                        if old_board.music_chan:
                            self.screens[i].set_volume(old_board.music_chan.get_volume())
                        self.screens[i].sound_vol = old_board.sound_vol
                        break
            else:
                self.screens.append(self.board_generator.generate_board(self.resolution))
        except TooManyCharactersException:
            self.show_popup('chars')
            return
        self.get_screen('params', 'menu', 'config').enable_all_sprites(False)
        self.get_screen('music', 'menu', 'sound').enable_all_sprites(True)
        self.get_screen('main', 'menu').enable_all_sprites(True)
        self.started = True

    def start(self):
        try:
            self.set_easter_eggs()
            self.check_state()
            self.init_log()
            self.current_screen = self.screens[0]
            self.current_screen.play_music()
            end = False
            while not end:
                self.clock.tick(self.fps)
                self.current_screen.draw(self.display)
                end = self.event_handler(pygame.event.get())
                if self.fps_text:
                    self.display.blit(self.fps_text, tuple(int(x*0.02) for x in self.resolution))
                for popup in self.popups.sprites():
                    popup.draw(self.display)
                pygame.display.update()
            sys.exit()
        except Exception as exc:
            raise exc

