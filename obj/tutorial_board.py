"""--------------------------------------------
tutorial_board module. Contains a board subclass with messags and a mock game.
Have the following classes.
    TutorialBoard
--------------------------------------------"""

#Python libraries
import pygame

#Selfmade libraries
from strings import TUTORIAL
from obj.board import Board
from obj.utilities.utility_box import UtilityBox
from obj.utilities.decorators import run_async

class TutorialBoard(Board):
    """TutorialBoard class. Inherits from Board.
    Each instance of this class contains a board which is specialized in showing a player his way around the different actions.
    Due to this, it only has 2 players, and far less characters than in a normal game.
    Also, messages will be shown, triggered by some player actions.
    It takes the messages to show from the Settings.py file.
    Attributes:
        msgs_shown (Dict-hash:String):  Structure with all the messages that will be used and shown through the tutorial.
    """
    def __init__(self, id_, event_id, end_event_id, resolution, **params):
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

    @run_async
    def show_message(self, msg):
        """Shows on the tutorial board the input message. This will also block any actions until it is dismissed (by an action).
        It will only show the message, if it is contained in the msgs_shown structure. 
        This means that unless a message is written beforehand in the Settings.py file, it won't be shown, even calling this method.
        Also, each message can be shown only once.
        Args:   
            msg (String):   Message to show"""
        try:
            if not self.msgs_shown[hash(msg)]:  #If it haven't been shown yet.
                self.console_active = True
                self.msgs_shown[hash(msg)] = True
                self.LOG_ON_SCREEN(msg,  msg_size=(0.60, 0.90), text_lines=UtilityBox.line_number(msg))
        except KeyError:    #the fuck msg are you trying to show
            pass
    
    def hide_messages(self):
        """Hides the console with the whatever messages it has and cleans it. Kinda like dismissing the console."""
        self.console_active = False
        self.overlay_console.clear_msgs()

    def ALL_PLAYERS_LOADED(self):
        """ Checks if all of the board players have been created and loaded succesfully."""
        super().ALL_PLAYERS_LOADED()
        if self.started:
            self.hide_messages()

    def pickup_character(self):
        """Checks if a subtype of character has been picked up before, and if it hasn't, a 
        helping tutorial message is shown on the screen, describing the character's behaviour and how it moves.
        If its not the first time, the pick up method is called normally."""
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
        """Checks if a cell has been set as active before, and if it hasn't, a 
        helping tutorial message is shown on the screen.
        If its not the first time, the set active cell method is called normally."""
        super().set_active_cell(cell)
        self.show_message(TUTORIAL.MESSAGE_HOVER_CELL)

    def mouse_handler(self, event, mouse_buttons, mouse_movement, mouse_position):
        """Handles any mouse related pygame event. This allows for user interaction with the object.
        This overloaded one only has as an added feature, that it hides the console upon a mouse click, which
        doesn't happen in a normal board.
        Args:
            event (:obj: pygame.event): Event received from the pygame queue.
            mouse_buttons (List->boolean):  List with 3 positions regarding the 3 normal buttons on a mouse.
                                            Each will be True if that button was pressed.
            mouse_movement( boolean, default=False):    True if there was mouse movement since the last call.
            mouse_position (:tuple: int, int, default=(0,0)):   Current mouse position. In pixels.
        """
        if mouse_movement and not self.msgs_shown[hash(TUTORIAL.MESSAGE_BOARD)]:
            self.show_message(TUTORIAL.MESSAGE_BOARD)
            return
        if self.console_active:
            if event.type == pygame.MOUSEBUTTONDOWN:    #IF DICE: Do shit. Go activating and deactivating the spritse in the order that we want thhe player to play them.
                self.hide_messages()
            return
        super().mouse_handler(event, mouse_buttons, mouse_movement, mouse_position)

    def shuffle(self):
        """Shuffles and throws the board's infoboard's dice. Shows a message explaining it if it's the first time."""
        if not self.msgs_shown[hash(TUTORIAL.MESSAGE_DICE)]:
            self.show_message(TUTORIAL.MESSAGE_DICE)
            return
        super().shuffle()

    def activate_only_chars_type(self, type, player):
        """More or less the steps that we want the noob player to take (The order I mean)"""
        pass
    
        