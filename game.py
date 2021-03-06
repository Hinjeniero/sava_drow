"""--------------------------------------------
game module. It's the overseer of all the modules of the game.
Highest level in the hierarchy.
Have the following classes:
    Game
--------------------------------------------"""
__all__ = ['Game']
__version__ = '1.0'
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
                        EmptyCommandException, ScreenNotFoundException, TooManyCharactersException, TooManyPlayersException,\
                        ZeroPlayersException, NotEnoughHumansException, ServiceNotAvailableException
from obj.utilities.surface_loader import ResizedSurface
from settings import PATHS, USEREVENTS, SCREEN_FLAGS, INIT_PARAMS, PARAMS
from animation_generator import AnimationGenerator

class Game(object):
    """Game class. Overseer of the entire underlying structure.
    Takes care of changing the screens, of redirecing the inputs, redirecting the events produced
        in each of the screens, managing execution according to parameters and, in short, to connect everything.
    Attributes:
        id (int): Identifier of this game instance.
        uuid (int): Unique identifier of game instance. It is contained in a local file, and it's created if it's missing.
        display (obj: pygame.Surface): Current root surface that will be displayed to the user.
        clock (obj: pygame.time.Clock): Clock that will synchronize and control the game framerate.
        screens (List->Screen): All of the screens of this game. A screen is akin to a complete change of context 
                        (Menu is a screen, and the board is a different one).
        started (Boolean):  Flag that signals when the game itself (A board) had been created and its in execution.
        resolution (:tuple: int, int): Resolution of the screen. In pixels. The display surface will have this initial resolution.
        fps (int):  Current frames per second (Times that the display surface is updated in a second).
        fps_text (:obj: pygame.Surface):    Text of the current fps achieved. Useful to show if we are pushing our computer too far (Not reaching stable fps).
        last_inputs (List->String): Saves the latest keystrokes of the player. Useful to trigger easter eggs.
        last_command (String):  Last command received from a dialog. Switches between a value and None. Used to know when a dialog was just shown and when
                                to execute the command contained within it.
        current_screen (:obj: Screen):  The screen that the game is currently at.
        board_generator (:obj: BoardGenerator): Object with the task of creating the Board/NetworkBoard with the configuration parameters setted beforehand by the user.
        popups (:obj: pygame.sprite.Group): Subtype of Group that holds the different popups or messages that will be shown in the different situations.
        fullscreen (boolean): Flag that shows if the game is currently in Fullscreen mode or Windowed mode.
        count_lock (:obj: threading.Lock): Lock that restrict the access to the countdown variable to one thread at the same time.
        countdown (int): Counter of the seconds that have passed since the game was created. Useful with programmed executions.
        waiting_for (List->Tuple->(Int:Tuple)):     List of programmed tasks. The first member of the tuple is the second of execution (Counting from the issuing),
                                                    and the second member is a tuple like this: (method_direction, *args, **kwargs)<
        todo (List->Tuple->(Method, List, Dict)):   Structure with the tasks that have to be execute already, since their countdown have been reached. 
                                                        The tasks in here are taken care of as soon as possible, in order of arrival.
    """
    def __init__(self, id_, resolution, fps, **board_params):
        """Game constructor.
        Args:
            id_ (int): Identifier of this game instance.
            resolution (:tuple: int, int): Initial resolution of the screen. In pixels.
            fps (int):  Initial frames per second (Times that the display surface is updated in a second).
            board_params (Dict-> Any:Any):  Initial input params that will be used in BoardGenerator (To create a board).
        """
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
        self.current_screen = None  #Created in Game.start()
        self.board_generator= None  #Created in Game.generate()
        self.popups         = pygame.sprite.OrderedUpdates()  
        self.fullscreen     = False
        self.count_lock     = threading.Lock()
        self.countdown      = 0
        self.waiting_for    = []
        self.todo           = []
        Game.generate(self)

    @staticmethod
    def generate(self):
        """Generate method. It's called at the end of the constructor.
        This method complete the object by checking if the uuid file exists, creating the display surface,
            creating the board generator, and setting the timers. In short, it handles the heavy tasks of the constructor.
        Args:
            self (:obj: Game):  Instance of the object that will be modified accordingly."""
        pygame.display.set_mode(self.resolution)
        self.generate_uuid()
        self.display = pygame.display.get_surface()
        self.board_generator = BoardGenerator(self.uuid)
        self.set_timers()

    def generate_uuid(self):
        """Checks if the game's folder contains the UUID file. If it does, it loads it in memory. 
        Otherwise, it is created and saved in a file for future loads."""
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
        """Set and starts the pygame timers. Right now, there is only one, 
        triggering an event each second, to signal that a second has passed."""
        pygame.time.set_timer(USEREVENTS.TIMER_ONE_SEC, 1000) #Each second

    def __add_timed_execution(self, second, method, *args, **kwargs):
        """Add a scheduled execution of a method. The input arguments specify the details.
        Not tested from another class.
        The second argument means the seconds from the instant this methos is called, not in absolute terms.
        Args:
            second (int): Seconds until teh future instant in which the method will be scheduled to be executed.
            method (callback):  Method itself to be executed. Being a cb, has to be the direction of the method, not the call (not parenthesis)
            args (Tuple->Any):  Input saguments of the method call.
            kwargs (Dict->Any:Any): Keyworded input arguments of the method call.
        """
        self.waiting_for.append((int(self.countdown+second), method, args, kwargs))
        self.waiting_for.sort(key=lambda method: method[0])

    def add_screens(self, *screens):
        """Add all of the input screens to the game instance.
        Args:
            screens (Tuple->Screen): The screen instances to be added."""
        for screen in screens:
            if isinstance(screen, Screen):
                self.screens.append(screen)
            else:
                raise InvalidGameElementException('Can`t add an element of type '+str(type(screen)))

    def user_command_handler(self, event):
        """Method that handles all of the custom made commands and events (Greated that pygame.USEREVENT).
        Takes care of the MAINMENU events in the method itself, and the rest of them are redirected to their matching methods.
        Modularization at its finest. The custom events are numerated in the following manner:
            USEREVENT+0: Change of screens
            UESREVENT+1: Change in sound settings
            USEREVENT+2: Change in graphic settings
            USEREVENT+3: Change in board configuration settings
            USEREVENT+4: Action in board. Unused rn.
            USEREVENT+5: Action in dialogs/etc. Unused rn.
            USEREVENT+6: Signals the end of the current board.
            USEREVENT+7: Called every second. Timer.
        Args:
            event (pygame.Event): Event object that will be analyzed to trigger an action.
                                An event object in this game has a type, a command, and sometimes a value as attributes.
        """
        try:
            if event.type < pygame.USEREVENT:       
                return False
            elif event.type is USEREVENTS.MAINMENU_USEREVENT:
                if 'start' in event.command.lower():
                    if self.board_generator.get_actual_total_players() is 0:
                        self.show_popup('zero_players')
                    elif self.board_generator.get_actual_total_players() is 1:
                        self.show_popup('alone_player')
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
                    if not self.initiate(): #IF its not a success, we don't want to continue changing screen
                        return
                self.change_screen(*event.command.lower().split('_'))
            elif event.type is USEREVENTS.SOUND_USEREVENT:
                self.sound_handler(event.command.lower(), event.value)
            elif event.type is USEREVENTS.GRAPHIC_USEREVENT:  
                self.graphic_handler(event.command.lower(), event.value)
            elif event.type is USEREVENTS.CONFIG_USEREVENT:  
                self.config_handler(event.command.lower(), event.value)
            elif event.type is USEREVENTS.BOARD_USEREVENT:
                try:
                    self.board_handler(event, event.command.lower(), value=event.value)
                except AttributeError:
                    try:
                        self.board_handler(event, event.command.lower())
                    except AttributeError:  #The suffling command is the only one with no command
                        self.get_screen('main', 'board').shuffling_frame()
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
        """Makes the actions that show the end of a game. Shows a lose or win popup, and makes you go back to the main menu after a set time.
        Args:
            win (boolean, default=False): Flag that is True if you won the game, and False otherwise."""
        if win:
            self.show_popup('win')
        else:
            self.show_popup('lose')
        self.__add_timed_execution(7, self.restart_main_menu)

    def restart_main_menu(self):
        """Restarts the state of the game, returning to the main menu and disabling any ways to go back to the last game (board screen)."""
        self.started = False
        self.change_screen('main', 'menu')
        self.get_screen('params', 'menu', 'config').enable_all_sprites(True)
        self.get_screen('main', 'menu').enable_sprites(False, 'continue')

    def dialog_handler(self, command, value=None):
        """Handles all the events related to Dialogs.
        Args:
            command (String):   Specific command that the event holds, describes the action to trigger.
            value (Any, default=None):  Sometimes an action will require a value. This one fills that necessity."""
        if 'ip' in command and 'port' in command:   #From table of servers
            try:
                self.current_screen.set_ip_port(ip=value.split(':')[0], port=int(value.split(':')[1]))
                self.current_screen.hide_dialog()
                return
            except AttributeError:
                pass
        elif 'ip' in command:                       #From direct connection dialog
            self.current_screen.set_ip_port(ip=value)
        elif 'port' in command:                     #From direct connection dialog
            self.current_screen.set_ip_port(port=int(value))
        if not self.last_command:   #In this case the dialog just popped-up
            self.last_command = command
            return
        elif 'cancel' in command or 'no' in command or 'false' in command:
            self.current_screen.hide_dialog()
            if 'ip' in command or 'port' in self.last_command:
                self.current_screen.destroy()
                self.restart_main_menu()
            self.last_command = None
        elif 'ok' in command or 'yes' in command or 'agree' in command:   #The OK button was pressed
            if 'exit' in command:
                raise GameEndException("Byebye!")
            elif 'input' in command:
                self.current_screen.dialog.trigger_all_elements()
                self.current_screen.hide_dialog()
            self.last_command = None
        else:
            LOG.log('warning', 'the command ',command,' is not recognized.')

    def config_handler(self, command, value):
        """The events that are related to the configuration of parameters, are checked in this method.
            command (String):   Specific command that the event holds, describes the action to trigger.
            value (Any):  Value to set/change in the specific option or parameter""" 
        characters = ('pawn', 'warrior', 'wizard', 'priestess', 'matron')
        if 'player' in command:
            if 'human' in command:
                self.board_generator.human_players = value
            if 'cpu' in command or 'computer' in command:
                self.board_generator.set_cpu_players(value)
                if value == 0:
                    if 'online' in command:
                        self.get_screen('online', 'menu').enable_sprites(False, 'cpu')
                        self.get_screen('online', 'menu').enable_sprites(True, 'cpu', 'player')
                    else:
                        self.get_screen('game', 'menu').enable_sprites(False, 'cpu')
                        self.get_screen('game', 'menu').enable_sprites(True, 'cpu', 'player')
                else:
                    if 'online' in command:
                        self.get_screen('online', 'menu').enable_sprites(True, 'cpu')
                    else:
                        self.get_screen('game', 'menu').enable_sprites(True, 'cpu')
            if 'total' in command:
                self.board_generator.set_players(value)
        elif 'computer' in command or 'cpu' in command:
            if 'mode' in command:
                self.board_generator.computer_players_mode = value.lower()
            if 'time' in command or 'timeout' in command:
                self.board_generator.set_round_time_cpu(float(value))
        elif 'game' in command or 'mode' in command:
            self.board_generator.set_game_mode(value)
            if not 'custom' in value.lower() or 'free' in value.lower():
                self.get_screen('params', 'menu', 'config').enable_sprites(False, 'set', 'board')
            else:
                self.get_screen('params', 'menu', 'config').enable_all_sprites()
        elif 'cell' in command and ('texture' in command or 'image' in command or 'type' in command):
            self.board_generator.set_cell_texture(value)
        elif 'size' in command:
            self.board_generator.set_board_size(value)
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

    def board_handler(self, event, command, value=None):
        """Board events and NetworkBoard events method. 
            command (String):   Specific command that the event holds, describes the action to trigger.
            value (Any, default=None):  Sometimes an action will require a value. This one fills that necessity."""
        if 'turncoat' in command:
            self.show_popup('turncoat')
        elif 'my' in command and 'turn' in command:
            self.show_popup('my_turn')
        elif 'cpu' in command and 'turn' in command:
            self.show_popup('cpu_turn')
        elif 'turn' in command:
            self.show_popup('next_turn')
        elif 'shuf' in command: #The current player shuffled the dice
            self.get_screen('main', 'board').assign_current_dice(event.id)
        elif 'bad' in command and 'dice' in command:
            self.show_popup('bad_dice_value')
        elif 'dice' in command: #The current player shuffled the dice
            self.get_screen('main', 'board').dice_value_result(event)
        elif 'conn' in command and 'error' in command:
            self.show_popup('connection_error')
            self.current_screen.destroy()
            self.__add_timed_execution(3, self.restart_main_menu)
        elif 'admin' in command:
            if value:
                self.show_popup('enemy_admin_on')
            else:
                self.show_popup('enemy_admin_off')
        elif 'cpu_turn' in command or 'my_turn' in command or 'next_turn' in command:
            self.show_popup(command)
        elif 'pause_game' in command:
            self.show_popup('player_disconnect')
        elif 'server' in command and 'table' in command and 'unreach' in command:
            self.show_popup('servers_table_off')
            self.current_screen.destroy()
            self.__add_timed_execution(3, self.restart_main_menu)
        elif 'hide' in command and 'dialog' in command:
            self.show_popup('dice_turns')
            self.__add_timed_execution(value, self.call_screens_method, 'board', Screen.hide_dialog)
        elif 'internet' in command:
            self.show_popup('no_internet', show_time=30)
        elif 'server' in command and 'exists' in command:
            self.show_popup('server_already_exists', show_time=30)
            self.current_screen.destroy()
            self.__add_timed_execution(3, self.restart_main_menu)

    def graphic_handler(self, command, value):
        """Graphic options related method. Those events will come to here.
            command (String):   Specific command that the event holds, describes the action to trigger.
            value (Any):    Value to set/change in the specific option or parameter."""
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
                self.set_background(value, *self.get_screens('menu'))
            elif 'board' in command:
                self.set_background(value, *self.get_screen('board'))

    def set_resolution(self, resolution):
        """Changes the resolution of the game context. Achieves this by changing the attributes that show the current resolution,
        and by changing all the surfaces sizes. Pretty taxing method, since in most cases the surfaces are created again with the new params.
        Args:
            resolution ((int, int)): New resolution to change to. In pixels. Only one tuple."""
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
    def set_background(self, new_bg_id, *screens):
        """Sets a new animated background to the input screens. The input bg id must match with some of the prefabbed ids
        in the factory method in animation_generator.py.
        Args:
            *screens (:obj: Screens):  All the screens to which to create and add the new animated background.
            new_bg_id (String): Identifier of the desired animated background to create and add.""" 
        new_animated_bg = AnimationGenerator.factory(new_bg_id, self.resolution, PARAMS.ANIMATION_TIME,\
                                                    INIT_PARAMS.ALL_FPS, self.fps)
        for screen in screens:
            screen.animated_background = True
            screen.background = new_animated_bg

    def sound_handler(self, command, value):
        """Sound and music related events are taken care of by this method.
        Args:
            command (String):   Specific command that the event holds, describes the action to trigger.
            value (Any):    Value to set/change in the specific option or parameter."""
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
        """Even if it's called event handler, what this method does is detecting the user inputs (By keyboard and mouse), and
        processing them/redirect them to whichever screen, in a case by case basis.
        Some special cases are:
            ALT+F4: Closes the game itself.
            ESC:    Goes back to the main menu if possible, or show a confirmation dialog.
        Args:
            events (List->pygame.Event):    All the input events that are still stuck in the event queue that pygame provides.
        Returns:
            (boolean):  True if the received input leads to close the game, False otherwise. 
        """
        all_keys            = pygame.key.get_pressed()          #Get all the pressed keyboard keys
        all_mouse_buttons   = pygame.mouse.get_pressed()        #Get all the pressed mouse buttons
        mouse_pos           = pygame.mouse.get_pos()            #Get the current mouse position
        mouse_mvnt          = pygame.mouse.get_rel()!=(0,0)     #True if get_rel returns non zero vaalues 
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.hide_popups()
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
        """Gets the last user input, and acts hiding the current visible popups (Popups hide when any button is clicked).
        Also checks if the last_inputs structure is overloaded (Over 20 chars), and check the easter eggs to trigger the right one if matching. """ 
        self.hide_popups()
        if len(self.last_inputs) > 20:
            del self.last_inputs[0]
        self.last_inputs.append(pygame.key.name(event.key))
        self.check_easter_eggs()

    def set_popups(self):
        """Create the popups (Dialog instances), and adds them to the game itself."""
        self.add_popups(*DialogGenerator.generate_popups(self.resolution,\
                        ('default', 'default warning, I am become error'),\
                        ('secret_acho', 'Gz, you found a secret! all your SFXs will be achos now.'),\
                        ('secret_admin', 'Admin mode activated! You can move your character to any cell.'),\
                        ('secret_running90s', 'Gz, you found a secret! The background music is now Running in the 90s.'),\
                        ('secret_dejavu', 'Gz, you found a secret! The background music is now Dejavu.'),\
                        ('toomany_chars', 'Too many chars, can`t generate a board. Change the params.'),\
                        ('winner', 'Gz, you won! You sure showed them!'),\
                        ('loser', 'You lost! Use your head more the next time!'),\
                        ('next_turn', 'Next turn is an enemy`s! Brace yourself!'),\
                        ('my_turn', 'It`s your turn! Wreak some havoc!'),\
                        ('cpu_turn', 'Its the turn of a computer controlled player!'),\
                        ('turncoat_on', 'Turncoat mode activated! Current player can control any char in this turn.'),\
                        ('servers_table_off', 'The table of public servers can`t be reached, check the service'),\
                        ('connection_error', 'There was a connection error, check the console for details.'),\
                        ('player_disconnected', 'One of the players disconnected, restart the game.'),\
                        ('enemy_admin_on', 'Other player activated the admin mode! Be careful!'),\
                        ('enemy_admin_off', 'The admin mode was deactivated in another board.'),\
                        ('too_many_players', 'The number of cpu and human players surpass the total'),
                        ('zero_players', 'You can`t start a game with no players!'),\
                        ('alone_players', 'The board being generated only has one player in it'),\
                        ('not_enough_players', 'You can`t start an online game with less than 2 human players. Create a local one instead.'),\
                        ('dice_turns', 'Your turns will be ordered following the value that you got in the dice throw'),\
                        ('bad_dice_value', 'Someone threw the dice but got his turn revoked!'),\
                        ('public_service_not_available', 'The service that holds the public servers is unreachable'),\
                        ('starting_board_loading', 'The board loading has started...'),\
                        ('no_internet', 'You are disconnected from the network, the resources will be reachable only locally'),\
                        ('server_already_exists', 'The socket is busy, you already have a server running locally')))

    def add_popups(self, *popups):
        """Add the input popups to the game.
        Args:
            (tuple->:obj: Dialog):  All the popups to add."""
        for popup in popups:
            popup.set_active(False)
            popup.set_visible(False)
            self.popups.add(popup)

    def show_popup(self, id_, show_time=3, automatic_dismiss=True):
        """Makes visible and active the popup that matches with the input id. If it's not found, a warning is shown in console.
        Args:
            id_ (String):   Id or substring of that id to search for in the popup list."""
        for popup in self.popups:
            if id_ in popup.id or popup.id in id_:
                popup.set_visible(True)
                popup.set_active(True)
                if automatic_dismiss:
                    self.__add_timed_execution(show_time, self.hide_popups)
                return
        LOG.log('warning', 'Popup ', id_,'not found')
        self.show_popup('default')

    def get_popup(self, id_):
        """Returns the popup that matches with the input id.
        Args:
            id_ (String):   Id or substring of that id to search for in the popup list.
        Returns:
            (:obj: Dialog | None):  Returns the matching dialog if its found, but None if no one matches."""
        for popup in self.popups:
            if id_ in popup.id or popup.id in id_:
                return popup
    
    def hide_popups(self):
        """Hides all the popups in the game by rendering them invisible and inactive."""  
        for popup in self.popups:
            popup.set_active(False)
            popup.set_visible(False)

    def check_easter_eggs(self):
        """Check for the last user actions to see if an easter egg must be triggered and shown.
        If its done by checking the last_inputs structure, so only keyboard strokes count. Mouse inputs are not saved.
        Some easter eggs are (If the last inputs by the player match the easter egg):
            ACHO:   All the sounds will be switched with an ACHO voice-recorded sound. This is not reversable except for a restart.
            DEJAVU: The background music will be Initial D track Dejavu. This is reversable by changing songs in the sound options.
            RUNNING:The background music will be Initial D track Running in the 90s. This is reversable by changing songs in the sound options.
            ADMIN:  When in a board, it activates the admin mode, that allows players to move their characters wherever they want. 
                    Very useful for testing.
        """
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
        """Esc key keystroke handler. Basically changes back to main menu, and if already in main menu,
        shows a dialog or hides a dialog, depending in if the dialog was already active or not."""
        LOG.log('DEBUG', "Pressed esc in ", self.current_screen.id)
        id_screen = self.current_screen.id.lower()
        if 'main' in id_screen and 'menu' in id_screen:
            if not self.current_screen.dialog_active():
                self.current_screen.show_dialog('exit')   
            else:  
                self.current_screen.hide_dialog()
                self.last_command = None
        elif 'menu' in id_screen or 'board' in id_screen:   
            self.change_screen('main', 'menu')

    def get_screens(self, *keywords):
        """Gets and returns all the screens whose ID have any match with any of the input keywords 
        Args:
            keywords (Tuple->String):   Keywords to search for in the ids of all the screens.
        Returns:
            (List->:obj:Screen):   Returns a list of the screens with matches."""
        screens = []
        for screen in self.screens:
            if any(kw in screen.id for kw in keywords):
                screens.append(screen)
        return screens

    def get_screen(self, *keywords):
        """Gets and returns the screen that have more matches with the input keywords.
        Args:
            keywords (Tuple->String):   Keywords to search for in the ids of all the screens.
        Returns:
            (:obj:Screen | None):   Returns the screen with most matches. If zero matches were found, returns None."""
        screen = None
        count = 0
        for i in range(0, len(self.screens)):
            matches = len([0 for j in keywords if j in self.screens[i].id])
            if matches > count:   
                screen = self.screens[i]
                count = matches
        return screen

    def call_screens_method(self, keywords, method, *method_args, **method_kwargs):
        """Calls the input method of the screen that has more matches with the input keywords.
        It's a hacky way to so it, but hey, it works.
        Args:
            keywords(Tuple->String):    Keywords to search for in the ids of all the screens.
            method (callback):  Method itself to be executed. Being a cb, has to be the direction of the method, not the call (not parenthesis)
            args (Tuple->Any):  Input arguments of the method call.
            kwargs (Dict->Any:Any): Keyworded input arguments of the method call."""
        #hasattr(Dynamo, 'mymethod') and callable(getattr(Dynamo, 'mymethod'))
        if isinstance(keywords, str):   #If it's only a keyword (A string)
            keywords = keywords,        #String to tuple
        try:
            for screen in self.screens:
                if all(kw in screen.id for kw in keywords):
                    method(screen, *method_args, **method_kwargs)
        except AttributeError:
            LOG.log('Warning', 'The method ', str(method), ' is not found in the class Screen')

    def change_screen(self, *keywords):
        """Changes the current screen to the one with most matches with the input keywords.
        This implies to pause the last screen music (If it exists), and also starting the new screen music.
        Raises:
            (ScreenNotFoundException):  When there isn't even a single match with any of the screens."""
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
        """Enable the music menus sliders (The board ones)."""
        self.get_screen('music', 'menu').enable_all_sprites()

    def check_state(self):
        """Checks if the game contains at least a screen, and at least a main menu
        Returns:
            (boolean):  True if the above conditions comply. If not, well, it raises an error. No False here, all or nothing.
        Raises:
            (NoScreensException):   When the game doesn't meet any of the above conditions."""
        if (len(self.screens) > 0) and any(isinstance(screen, Menu) and 'main' in screen.id for screen in self.screens):
            return True
        raise NoScreensException('A game needs at least a main menu to start.')
    
    def init_log(self):
        """Shows the initial LOG messages that prove that the game has started."""
        LOG.log('INFO', "GAME STARTING!")
        LOG.log('INFO', "----Initial Pygame parameters----")
        LOG.log('INFO', "Game initial frames per second: ", self.fps)
        LOG.log('INFO', "RESOLUTION: ", self.display.get_size())

    def update_board_params(self, **params):
        """Self-explanatory, updates the board generator params with the input ones.
        Args:
            params (Dict->Any:Any): Params to update with."""
        self.board_generator.set_board_params(**params)

    def initiate(self):
        """Performs all the initial checks and actions that must be done when creating a new board.
        Enables all disabled buttons. If there are too many characters to fit in the new board, you will be 
        thrown back to the main menu with an exception."""
        try:
            #Showing the starting dialog
            self.show_popup('starting_board_loading', automatic_dismiss=False)
            self.draw()
            self.hide_popups()
            if self.get_screen('board'):
                for i in range(0, len(self.screens)):
                    if 'board' in self.screens[i].id:
                        old_board = self.screens[i]
                        self.screens[i] = self.board_generator.generate_board(self.resolution)
                        if old_board.music_chan:
                            self.screens[i].set_volume(old_board.music_chan.get_volume())
                        self.screens[i].sound_vol = old_board.sound_vol
                        old_board.destroy()
                        break
            else:
                self.screens.append(self.board_generator.generate_board(self.resolution))
        except TooManyCharactersException:
            self.show_popup('chars')
            return False
        except TooManyPlayersException:
            self.show_popup('too_many_players')
            return False
        except ZeroPlayersException:
            self.show_popup('zero_players')
            return False
        except NotEnoughHumansException:
            self.show_popup('not_enough_players')
            return False
        except ServiceNotAvailableException:
            self.show_popup('public_service_not_available', show_time=30)
            return False
        #self.get_screen('params', 'menu', 'config').enable_all_sprites(False)
        self.get_screen('music', 'menu', 'sound').enable_all_sprites(True)
        self.get_screen('main', 'menu').enable_all_sprites(True)
        self.started = True 
        return True

    def draw(self):
        """Draws the entire application in the screen. Also updates the display to show the changes."""
        self.current_screen.draw(self.display)
        if self.fps_text:
            self.display.blit(self.fps_text, tuple(int(x*0.02) for x in self.resolution))
        for popup in self.popups:
            popup.draw(self.display)
        pygame.display.update()

    def start(self, *first_screen_keywords):
        """Starts the game instance. Perform checks and start all the methods needed. 
        Upon calling, you will have a working Game instance that shows something in the screen and that
        you can interact with.
        It contains an infinite loop that processes all inputs and acts accordingly.
        When the loop is broken out of, the method ends, and so does the game itself, closing it.
        Args:
            first_screen_keywords (Tuple->String):  Keywords to set the first screen instance that will be shown to the user.
                                                    Usually, this one should be the main menu.
        """
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
                    end = self.event_handler(pygame.event.get())
                    self.draw()
                except GameEndException:
                    end = True
        except Exception:
            LOG.error_traceback()
        for screen in self.screens:
            screen.destroy()
        END_ALL_THREADS()
        sys.exit()

