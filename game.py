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
import pickle
import uuid
from pygame.locals import *
from pygame.key import *
from obj.screen import Screen
#Selfmade Libraries
from dialog_generator import DialogGenerator
from obj.utilities.decorators import run_async
from obj.board import Board
from obj.menu import Menu
from obj.ui_element import UIElement, TextSprite, InfoBoard, Dialog
from obj.utilities.colors import RED, BLACK, WHITE
from obj.utilities.logger import Logger as LOG
from obj.utilities.utility_box import UtilityBox
from obj.utilities.decorators import END_ALL_THREADS
from board_generator import BoardGenerator
from obj.utilities.exceptions import  NoScreensException, InvalidGameElementException, GameEndException,\
                        EmptyCommandException, ScreenNotFoundException, TooManyCharactersException
from obj.utilities.surface_loader import ResizedSurface
from settings import PATHS, USEREVENTS, SCREEN_FLAGS, INIT_PARAMS, PARAMS
from animation_generator import AnimationGenerator

class Game(object):
    def __init__(self, id_, resolution, fps, **board_params):
        self.id             = id_
        self.uuid           = None  #Created in Game.start()
        self.display        = None  #Created in Game.generate()
        self.clock          = pygame.time.Clock()
        self.screens        = []
        self.started        = False
        self.resolution     = resolution
        self.fps            = fps
        self.fps_text       = None
        self.last_inputs    = []    #Easter Eggs 
        self.last_command   = None
        self.game_config    = {}    #Created in Game.generate()
        self.current_screen = None  #Created in Game.start()
        self.board_generator= None  #Created in Game.generate()
        self.popups         = pygame.sprite.OrderedUpdates()  
        self.fullscreen     = False
        self.count_lock     = threading.Lock()
        self.countdown      = 0
        self.waiting_for    = []  #Waiting for second tuple[0], to do method tuple[1]
        self.todo           = []
        Game.generate(self)

    @staticmethod
    def generate(self):
        pygame.display.set_mode(self.resolution)
        self.generate_uuid()
        self.display = pygame.display.get_surface()
        self.board_generator = BoardGenerator(self.uuid)
        self.set_timers()

    def generate_uuid(self):
        try:
            uuid_file = open(PATHS.UUID_FILE, "rb")
            self.uuid = pickle.load(uuid_file)
            LOG.log('info', 'UUID FOUND! Your UUID is ', self.uuid)
        except FileNotFoundError:
            self.uuid = uuid.uuid1().int
            uuid_file = open(PATHS.UUID_FILE, "wb")
            pickle.dump(self.uuid, uuid_file)
            uuid_file.close()
            LOG.log('info', "UUID was not found, generated a new one. Your new UUID is ", self.uuid) 

    def set_timers(self):
        pygame.time.set_timer(USEREVENTS.TIMER_ONE_SEC, 1000) #Each second

    def __add_timed_execution(self, second, method, *args, **kwargs):
        """Dunno the effects of this if this is called from another class.
        The seconds are the seconds from this instant, not in absolute terms."""
        self.waiting_for.append((int(self.countdown+second), method, args, kwargs))
        self.waiting_for.sort(key=lambda method: method[0])

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
        try:
            if event.type < pygame.USEREVENT:       
                return False
            elif event.type is USEREVENTS.MAINMENU_USEREVENT:
                if 'start' in event.command.lower():
                    if 'tutorial' in event.command.lower():
                        self.board_generator.tutorial = True
                    elif 'online' in event.command.lower() or 'network' in event.command.lower():
                        self.board_generator.online = True
                        if 'host' in event.command.lower():
                            self.board_generator.server = True
                            if 'private' in event.command.lower():
                                self.board_generator.private = True
                        elif 'server' in event.command.lower() and ('get' in event.command.lower() or 'explore' in event.command.lower()):
                            self.board_generator.server = False
                            self.board_generator.direct_connect = False
                        else:
                            self.board_generator.server = False
                            self.board_generator.direct_connect = True
                    else:
                        self.board_generator.online = False
                    #After we decided on the board type
                    if all('human', 'cpu') in event.command.lower():
                        self.board_generator.only_cpu = False
                        self.board_generator.only_human = False
                    elif 'human' in event.command.lower():
                        self.board_generator.only_human = True
                    else:   #CPU players only
                        self.board_generator.only_cpu = True
                    self.initiate()
                self.change_screen(*event.command.lower().split('_'))
            elif event.type is USEREVENTS.SOUND_USEREVENT:
                self.sound_handler(event.command.lower(), event.value)
            elif event.type is USEREVENTS.GRAPHIC_USEREVENT:  
                self.graphic_handler(event.command.lower(), event.value)
            elif event.type is USEREVENTS.CONFIG_USEREVENT:  
                self.config_handler(event.command.lower(), event.value)
            elif event.type is USEREVENTS.BOARD_USEREVENT:
                try:
                    self.board_handler(event.command.lower(), value=event.value)
                except AttributeError:
                    try:
                        self.board_handler(event.command.lower())
                    except AttributeError:
                        self.get_screen('main', 'board').dice.sprite.increase_animation_delay()
            elif event.type is USEREVENTS.DIALOG_USEREVENT:
                if 'scroll' in event.command:
                    self.current_screen.set_scroll(event.value)
                else:
                    try:
                        self.dialog_handler(event.command.lower(), value=event.value)
                    except AttributeError:
                        self.dialog_handler(event.command.lower())
            elif event.type is USEREVENTS.END_CURRENT_GAME:
                if 'win' in event.command.lower():
                    self.end_board(win=True)
                else:
                    self.end_board()
            elif event.type is USEREVENTS.TIMER_ONE_SEC:
                self.count_lock.acquire()
                self.countdown += 1
                while len(self.waiting_for) > 0 and self.countdown >= self.waiting_for[0][0]:
                    self.todo.append(self.waiting_for.pop(0)[1:])
                self.count_lock.release()
                self.fps_text = UtilityBox.generate_fps(self.clock, size=tuple(int(x*0.05) for x in self.resolution))
        except AttributeError:
            LOG.error_traceback()

    def end_board(self, win=False):
        if win:
            self.show_popup('win')
        else:
            self.show_popup('lose')
        self.__add_timed_execution(3, self.hide_popups)
        self.__add_timed_execution(7, self.restart_main_menu)

    def restart_main_menu(self):
        self.started = False
        self.change_screen('main', 'menu')
        self.get_screen('params', 'menu', 'config').enable_all_sprites(True)
        self.get_screen('main', 'menu').enable_sprites(False, 'continue')

    def dialog_handler(self, command, value=None):
        if not self.last_command:   #In this case the dialog just popped-up
            self.last_command = command
            return
        if 'ip' in command:
            self.current_screen.set_ip_port(ip=value)
        elif 'port' in command:
            self.current_screen.set_ip_port(port=int(value))
        elif 'cancel' in command or 'no' in command or 'false' in command:
            print("CANCEL BUTTON WAS PRESSED")
            self.current_screen.hide_dialog()
            if 'ip' in command or 'port' in self.last_command:
                self.current_screen.destroy()
                self.restart_main_menu()
            self.last_command = None
        else:   #The OK button was pressed
            print("OK BUTTON WAS PRESSED")
            if 'exit' in command:
                raise GameEndException("Byebye!")
            elif 'input' in command:
                self.current_screen.dialog.trigger_all_elements()
                self.current_screen.hide_dialog()
                self.last_command = None
            else:
                LOG.log('warning', 'the command ',command,' is not recognized.')

    def config_handler(self, command, value):
        characters = ('pawn', 'warrior', 'wizard', 'priestess', 'matron')
        if 'game' in command or 'mode' in command:
            self.board_generator.set_game_mode(value)
            if not 'custom' in value.lower() or 'free' in value.lower():
                self.get_screen('params', 'menu', 'config').enable_sprites(False, 'set', 'board')
            else:
                self.get_screen('params', 'menu', 'config').enable_all_sprites()
        elif 'cell' in command and ('texture' in command or 'image' in command or 'type' in command):
            self.board_generator.set_cell_texture(value)
        elif 'size' in command:
            self.board_generator.set_board_size(value)
        elif 'player' in command and 'total' in command:
            self.board_generator.set_players(value)
        elif any(char in command for char in characters):
            self.board_generator.set_character_ammount(command, value)
        elif 'loading' in command:
            if 'on' in value.lower() or value == 1 or 'yes' in value.lower():
                self.board_generator.set_board_params(loading_screen=True)
            else:
                self.board_generator.set_board_params(loading_screen=False)
        elif 'center' in command:
            print("CENTER CELL")
            if 'on' in value.lower() or value == 1 or 'yes' in value.lower():
                print("TRUE")
                self.board_generator.set_board_params(center_cell=True)
            else:
                self.board_generator.set_board_params(center_cell=False)
        elif 'fill' in command or 'drop' in command:
            if 'on' in value.lower() or value == 1 or 'yes' in value.lower():
                self.board_generator.set_board_params(random_filling=True)
            else:
                self.board_generator.set_board_params(random_filling=False)
        elif 'computer' in command:
            if 'player' in command:
                self.board_generator.computer_players = value
            elif 'mode' in command:
                self.board_generator.computer_players_mode = value.lower()

    def board_handler(self, command, value=None):
        if 'turn' in command:
            self.show_popup('turn')
        elif 'dice' in command: #The current player shuffled the dice
            self.get_screen('main', 'board').dice_value_result(int(value))
        elif 'conn' in command and 'error' in command:
            self.show_popup('connection_error')
            self.__add_timed_execution(3, self.restart_main_menu)
            self.__add_timed_execution(3, self.hide_popups)
        elif 'admin' in command:
            if value:
                self.show_popup('enemy_admin_on')
            else:
                self.show_popup('enemy_admin_off')

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
        self.resolution = resolution
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
                else:   #How to differentiate when to writing in an input box and when to start an easter egg
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

    def set_popups(self):
        self.add_popups(*DialogGenerator.generate_popups(self.resolution,\
                        ('secret_acho', 'Gz, you found a secret! all your SFXs will be achos now.'),\
                        ('secret_admin', 'Admin mode activated! You can move your character to any cell.'),\
                        ('secret_running90s', 'Gz, you found a secret! The background music is now Running in the 90s.'),\
                        ('secret_dejavu', 'Gz, you found a secret! The background music is now Dejavu.'),\
                        ('toomany_chars', 'Too many chars, can`t generate a board. Change the params.'),\
                        ('winner', 'Gz, you won! You sure showed them!'),\
                        ('loser', 'You lost! Use your head more the next time!'),\
                        ('next_turn', 'It`s your turn! Wreak some havoc!'),\
                        ('connection_error', 'There was a connection error, check the console for details.'),\
                        ('enemy_admin_on', 'Other player activated the admin mode! Be careful!'),\
                        ('enemy_admin_off', 'The admin mode was deactivated in another board.'),\
                        ))

    def add_popups(self, *popups):
        for popup in popups:
            popup.set_active(False)
            popup.set_visible(False)
            self.popups.add(popup)

    def show_popup(self, id_):
        for popup in self.popups:
            if id_ in popup.id or popup.id in id_:
                popup.set_visible(True)
                popup.set_active(True)
                return
        LOG.log('warning', 'Popup ', id_,'not found')

    def get_popup(self, id_):
        for popup in self.popups:
            if id_ in popup.id or popup.id in id_:
                return popup
    
    def hide_popups(self):
        for popup in self.popups:
            popup.set_active(False)
            popup.set_visible(False)

    def check_easter_eggs(self):
        secret = None
        easter_egg_sound = False
        easter_egg_music = False
        last_inputs = ''.join(self.last_inputs).lower()
        if len(self.last_inputs) > 3:
            if 'acho' in last_inputs:
                LOG.log('INFO', 'SECRET DISCOVERED! From now on all the sfxs on all the screens will be achos.')
                secret = 'acho.ogg'
                easter_egg_sound = True
            elif 'running' in last_inputs:
                LOG.log('INFO', 'SECRET DISCOVERED! From now on the music in all your screens will be Running in the 90s.')
                secret = 'running90s.ogg'
                easter_egg_music = True
            elif 'dejavu' in last_inputs:
                LOG.log('INFO', 'SECRET DISCOVERED! From now on the music in all your screens will be Dejavu!')
                secret = 'dejavu.ogg'
                easter_egg_music = True
            elif 'admin' in last_inputs:
                LOG.log('INFO', 'Admin mode activated!')
                self.show_popup('admin')
                for screen in self.screens:
                    try:
                        screen.set_admin_mode(not screen.admin_mode)
                    except AttributeError:
                        continue
                self.last_inputs.clear()
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
        if not self.current_screen.dialog_active():
            self.current_screen.show_dialog('exit')   
        else:  
            self.current_screen.hide_dialog()
            self.last_command = None
            
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

    def start(self, *first_screen_keywords):
        try:
            self.set_popups()
            self.check_state()
            self.init_log()
            self.current_screen = self.get_screen(*first_screen_keywords)
            self.current_screen.play_music()
            end = False
            while not end:
                try:
                    self.clock.tick(self.fps)
                    if len(self.todo) > 0:
                        timed_exec = self.todo.pop(0)                   #One execution per frame
                        timed_exec[0](*timed_exec[1], **timed_exec[2])  #Executing the method
                    self.current_screen.draw(self.display)
                    end = self.event_handler(pygame.event.get())
                    if self.fps_text:
                        self.display.blit(self.fps_text, tuple(int(x*0.02) for x in self.resolution))
                    for popup in self.popups:
                        popup.draw(self.display)
                    pygame.display.update()
                except GameEndException:
                    end = True
        except Exception:
            LOG.error_traceback()
        for screen in self.screens:
            screen.destroy()
        END_ALL_THREADS()
        sys.exit()

