"""--------------------------------------------
tutorial_board module. Contains a board subclass with messags and a mock game.
Have the following classes.
    TutorialBoard
--------------------------------------------"""
import pygame
from obj.board import Board
from strings import TUTORIAL
from obj.utilities.utility_box import UtilityBox
from obj.utilities.decorators import run_async

class TutorialBoard(Board):
    """TutorialBoard class. Inherits from Board.
    Attributes:
        uuid (int): Identifier of this NetworkBoard/Client.
        reconnect (boolean):    True if to reconnect after losing connection, False otherwise.
    """

    def __init__(self, id_, event_id, end_event_id, resolution, obj_uuid=None, **params):
        """TutorialBoard constructor.
        Args:
            id_ (str):  Identifier of the Screen.
            event_id (int): Identifier of the Screen event.
            end_event_id (int): Event that signals the end of the game in this board.
            resolution (:tuple: int,int):   Size of the Screen. In pixels.
            **params (:dict:):  Dict of keywords and values as parameters to create the Screen.
                                platform_proportion, platform_alignment, inter_path_frequency, circles_per_lvl,\
                                max_levels, path_color, path_width.
        """
        params['loading_screen_text'] = 'Loading tutorial'
        super().__init__(id_, event_id, end_event_id, resolution, **params) #To generate the environment later
        self.msgs_shown = {hash(MSG): False for MSG in TUTORIAL.ALL_MSGS}   #Kinda like triggers that fire once
        self.tutorial_console = None

    @run_async
    def show_message(self, msg):
        try:
            if not self.msgs_shown[hash(msg)]:
                self.console_active = True
                self.msgs_shown[hash(msg)] = True
                self.LOG_ON_SCREEN(msg,  msg_size=(0.60, 0.90), text_lines=UtilityBox.line_number(msg))
        except KeyError:
            pass    #the fuck msg are you trying to show
    
    def hide_messages(self):
        self.console_active = False
        self.overlay_console.clear_msgs()

    def ALL_PLAYERS_LOADED(self):
        super().ALL_PLAYERS_LOADED()
        if self.started:
            self.hide_messages()

    def pickup_character(self):
        char_type = self.active_char.sprite.get_type()
        if 'pawn' in char_type and not self.msgs_shown[hash(TUTORIAL.MESSAGE_MOVE_PAWN)]:
            self.show_message(TUTORIAL.MESSAGE_MOVE_PAWN)
        elif 'warrior' in char_type and not self.msgs_shown[hash(TUTORIAL.MESSAGE_MOVE_WARRIOR)]:
            self.show_message(TUTORIAL.MESSAGE_MOVE_WARRIOR)
        elif 'wizard' in char_type and not self.msgs_shown[hash(TUTORIAL.MESSAGE_MOVE_WIZARD)]:
            self.show_message(TUTORIAL.MESSAGE_MOVE_WIZARD)
        elif 'priest' in char_type and not self.msgs_shown[hash(TUTORIAL.MESSAGE_MOVE_PRIESTESS)]:
            self.show_message(TUTORIAL.MESSAGE_MOVE_PRIESTESS)
        elif 'holy' in char_type and not self.msgs_shown[hash(TUTORIAL.MESSAGE_MOVE_HOLYCHAMPION)]:
            self.show_message(TUTORIAL.MESSAGE_MOVE_HOLYCHAMPION)
        elif 'matron' in char_type and not self.msgs_shown[hash(TUTORIAL.MESSAGE_MOVE_MATRONMOTHER)]:
            self.show_message(TUTORIAL.MESSAGE_MOVE_MATRONMOTHER)
        else:
            super().pickup_character()
    
    def set_active_cell(self, cell):
        super().set_active_cell(cell)
        self.show_message(TUTORIAL.MESSAGE_HOVER_CELL)

    def mouse_handler(self, event, mouse_buttons, mouse_movement, mouse_position):
        if mouse_movement and not self.msgs_shown[hash(TUTORIAL.MESSAGE_BOARD)]:
            self.show_message(TUTORIAL.MESSAGE_BOARD)
            return
        if self.console_active:
            if event.type == pygame.MOUSEBUTTONDOWN:    #IF DICE: Do shit. Go activating and deactivating the spritse in the order that we want thhe player to play them.
                self.hide_messages()
            return
        super().mouse_handler(event, mouse_buttons, mouse_movement, mouse_position)

    def shuffle(self):
        if not self.msgs_shown[hash(TUTORIAL.MESSAGE_DICE)]:
            self.show_message(TUTORIAL.MESSAGE_DICE)
            return
        super().shuffle()

    def activate_only_chars_type(self, type, player):
        """More or less the steps that we want the noob player to take (The order I mean)"""
        pass
    
        