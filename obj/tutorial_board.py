"""--------------------------------------------
tutorial_board module. Contains a board subclass with messags and a mock game.
Have the following classes.
    TutorialBoard
--------------------------------------------"""
import pygame
from obj.board import Board
from strings import TUTORIAL

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

    def show_message(self, msg):
        try:
            if not self.msgs_shown[hash(msg)]:
                self.console_active = True
                self.msgs_shown[hash(msg)] = True
                self.LOG_ON_SCREEN(msg)
        except KeyError:
            pass    #the fuck msg are you trying to show
    
    def hide_messages(self):
        self.console_active = False
        self.overlay_console.clear_msgs()

    def ALL_PLAYERS_LOADED(self):
        super().ALL_PLAYERS_LOADED()
        if self.started:
            self.show_message(TUTORIAL.MESSAGE_BOARD)

    def pickup_character(self):
        char_type = self.active_char.sprite.get_type()
        if 'pawn' in char_type:
            self.show_message(TUTORIAL.MESSAGE_MOVE_PAWN)
        elif 'warrior' in char_type:
            self.show_message(TUTORIAL.MESSAGE_MOVE_WARRIOR)
        elif 'wizard' in char_type:
            self.show_message(TUTORIAL.MESSAGE_MOVE_WIZARD)
        elif 'priest' in char_type:
            self.show_message(TUTORIAL.MESSAGE_MOVE_PRIESTESS)
        elif 'matron' in char_type:
            self.show_message(TUTORIAL.MESSAGE_MOVE_MATRONMOTHER)
        else:
            super().pickup_character()
    
    def mouse_handler(self, event, mouse_buttons, mouse_movement, mouse_position):
        if self.console_active:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.hide_messages()
            return
        super().mouse_handler(event, mouse_buttons, mouse_movement, mouse_position)
    
    #def activate_only_chars_type(self, type, player):
        #pass
    
        