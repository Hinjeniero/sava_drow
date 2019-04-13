"""--------------------------------------------
tutorial_board module. Contains a board subclass with messags and a mock game.
Have the following classes.
    TutorialBoard
--------------------------------------------"""
from obj.board import Board


class TutorialBoard(Board):
    """TutorialBoard class. Inherits from Board.
    Adds threads to handle received data, and sending of data on important steps of the game.
    This allows to communication between NetworkBoards, making possible to hold a game between different
    programs/computers over a LAN connection.
    Contains a keep_alive subthread, whose only purpose is to maintain the connection with the server operative,
    and a receive_worker subtread, that is listening to the server and handling thoe responses. Both of those work on an infinite loop.
    Attributes:
        uuid (int): Identifier of this NetworkBoard/Client.
        ip (str):   IP address of the server to connect to.
        port (int): PORT of the server to connect to.
        connected (:obj: threading.Event):  Flag to block the threads in the case of a disconnection, and unblock them later.
        client (:obj:niodsaidsa):   Our connection object that will be used to communicate with the server. 
        client_lock (:obj: threading.Lock): Lock to make the access to the client thread-safe.
        server (:obj: BoardServer): Server object. Only the host contains it to start it, otherwise is None.
        my_player (int):Uuid of the player that we will be controlling on the board.
        my_turn(boolean):   True if is the turn of my player, False otherwise.
        flags (dict):   Dict of threading.Event objects that block threads when they try to make an action that needs a not ready yet asset.
        reconnect (boolean):    True if to reconnect after losing connection, False otherwise.
    """

    def __init__(self, id_, event_id, end_event_id, resolution, obj_uuid=None, **params):
        """NetworkBoard constructor. Autogenerates the UUID.
        Args:
            id_ (str):  Identifier of the Screen.
            event_id (int): Identifier of the Screen event.
            end_event_id (int): Event that signals the end of the game in this board.
            resolution (:tuple: int,int):   Size of the Screen. In pixels.
            host (boolean, default=False):  True if this Board is the host, False otherwhise.
            server (:obj: BoardServer, default=None):   Server to connect all the clients. Essential if host is True.
            **params (:dict:):  Dict of keywords and values as parameters to create the Screen.
                                platform_proportion, platform_alignment, inter_path_frequency, circles_per_lvl,\
                                max_levels, path_color, path_width.
        """
        params['loading_screen_text'] = ''
        super().__init__(id_, event_id, end_event_id, resolution, empty=True, **params) #To generate the environment later
        self.messages = []