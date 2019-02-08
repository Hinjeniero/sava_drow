"""--------------------------------------------
network_board module. Contains a board subclass capable of communicate with
other boards through sockets.
Have the following classes.
    NetworkBoard
--------------------------------------------"""

#Python full fledged libraries
import threading
import traceback
import time
import uuid
import random
#External libraries
#from external.Mastermind import MastermindServerTCP, MastermindClientTCP
#from external.Mastermind._mm_errors import *   #This one doesnt catch the exception for some fuckin reasoni
from external.Mastermind import *   #I dont like this one a bit, since it has to import everything
from obj.board_server import Server
#Selfmade libraries
from settings import NETWORK
from obj.board import Board
from obj.players import Character
from obj.utilities.decorators import run_async
from obj.utilities.logger import Logger as LOG

class NetworkBoard(Board):
    """NetworkBoard class. Inherits from Board.
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
        flags (dict):   Dict of threading.Event objects that block threads when they try to make an action that needs a not ready yet asset.
        reconnect (boolean):    True if to reconnect after losing connection, False otherwise.
    """

    def __init__(self, id_, event_id, end_event_id, resolution, host=False, server=None, **params):
        """NetworkBoard constructor. Autogenerates the UUID.
        Args:
            id_ (str):  Identifier of the Screen.
            event_id (int): Identifier of the Screen event.
            resolution (:tuple: int,int):   Size of the Screen. In pixels.
            host (boolean, default=False):  True if this Board is the host, False otherwhise.
            server (:obj: BoardServer, default=None):   Server to connect all the clients. Essential if host is True.
            **params (:dict:):  Dict of keywords and values as parameters to create the Screen.
                                platform_proportion, platform_alignment, inter_path_frequency, circles_per_lvl,\
                                max_levels, path_color, path_width.
        """
        if host:
            super().__init__(id_, event_id, end_event_id, resolution, **params)
        else:
            super().__init__(id_, event_id, end_event_id, resolution, empty=True, **params) #To generate the environment later
        self.uuid = uuid.uuid1().int    #Using this if crashing would led to more conns than players
        self.ip = None
        self.port = None
        self.connected = threading.Event()
        self.client = None
        self.client_lock = threading.Lock()
        self.server = server
        self.my_player = None
        self.my_turn = False
        self.flags = {}     #Used if client and not host.
        self.reconnect = True
        NetworkBoard.generate(self, host)

    @staticmethod
    def generate(self, host):
        """This method sets the adequate ip, checking if this object is the host or not.
        Initiates the client, and makes it connect to the server.
        Also makes that distinction to start the server, or to set the flags needed to receive information from the host.
        Logs errors if those are of type MastermindError.
        Args:
            self (:obj: NetworkBoard):  NetworkBoard object calling this method
            host (boolean): True if this board is the host, False otherwise."""
        self.port = NETWORK.SERVER_PORT
        self.client = MastermindClientTCP(NETWORK.CLIENT_TIMEOUT_CONNECT, NETWORK.CLIENT_TIMEOUT_RECEIVE)
        try:
            if host:
                self.server.start(NETWORK.SERVER_IP, NETWORK.SERVER_PORT)
                self.ip = NETWORK.CLIENT_LOCAL_IP
            else:
                self.flags["board_done"] = threading.Event()
                self.flags["players_ammount_done"] = threading.Event()
                self.flags["players_data_done"] = threading.Event()
                self.ip = NETWORK.CLIENT_LOCAL_IP   #Testing rn
                #self.ip = NETWORK.CLIENT_IP
            self.connect()
            self.keep_alive() #Creating thread
            self.receive_worker()
            self.send_handshake(host)
        except MastermindError: #If there was an error connecting
            LOG.log("ERROR", traceback.format_exc())

    def send_handshake(self, host):
        """"Sends the first request to the server, with our ID and a host boolean.
        If this is the host, will send the parameters for the board creation.
        Otherwise, will ask for those parameters, along with other essential data like
        the generated players data, the ammount of players, or the generated characters data (like dropping cell).
        ARgs:"""
        self.send_data({"host": host, "id": self.uuid})
        if host:
            self.send_data_async({"params": self.get_board_params()})
        else:
            self.request_data_async("params")
            self.request_data_async("players")          #To get the number of players
            self.request_data_async("players_data")     #To get the data of the players
            self.request_data_async("characters_data")  #To get the data of the characters
        self.send_data_async({"dice": random.randint(1, 6), "id":self.uuid})    #Sending dice result for the player assignments

    def connect(self):   #TODO SEND ID IN CONNECT?
        """Connects the client to the server if the ip and port are available."""
        if self.ip and self.port:
            self.client_lock.acquire()
            self.client.disconnect()
            self.client.connect(self.ip, self.port)
            self.client_lock.release()
            LOG.log('info', 'Client ', self.uuid, ' connected to the server in the address ',\
                    self.ip, ':', self.port)

    @run_async
    def keep_alive(self):
        """SubThread that sends 'keep-alive' requests to the server in an infinite loop, to keep the connection, well, alive.
        Sends a request per second. It's a busy loop, using sleep. Not the best approach, but it works"""
        while True:
            try:
                self.request_data_async("keep-alive")   #Response will be handled in the receiving thread
                time.sleep(1)
            except MastermindErrorClient:               #If disconnectes from server
                if self.reconnect:
                    self.connect()  #TODO USE A FLAG TO SET THE CONNECTED STATE, TO BLOCK WHEN NOT CONNECTED.
                else:
                    break

    @run_async
    def receive_worker(self):
        """Subthread that is listening to the server in an infinite loop. Uses a blocking receiving call to avoid a busy loop.
        If it receives a response, it redirects it to the response_handler method. Also calls connect if the connections is lost."""
        while True:
            try:
                data = self.client.receive(True)
                self.response_handler(data)
            except MastermindErrorClient:   #Timeout/disconnection
                if self.reconnect:
                    self.connect()
                else:
                    break
            except ValueError:
                LOG.log('warning', 'RECEIVE_WORKER: There was a problem receiving the packet in the sockets, retrying...')
                LOG.log('warning', 'Mockingly: iNvAliD litERaL for iNt() with BASe 10: b\"{\"')
    
    @run_async
    def response_handler(self, response):
        """Handler of the received responses from the server. Accepts responses in the JSON schema.
        It decides what to do judging by the existance of different keys in the JSON form received.
        This runs on a subthread because some of the received responses require actions that can only
        be put on motion after some requirements are fulfilled. Thus, it can block on some of the flags.
        Args:
            response (dict):JSON schema. Contains the various replies of the server."""
        if "params" in response and not self.server:    #REQUESTING THE BOARD GENERATION PARAMETERS
            self.params.update(response["params"])
            self.generate_mapping()
            self.generate_environment()
            self.flags["board_done"].set()
        elif "players" in response and not self.server:
            self.flags["board_done"].wait()
            for i in range (0, 4, 4//response["players"]):
                self.create_player("null", i, None, empty=True)  #The name will be overwritten later on
        elif "players_data" in response and not self.server:
            self.flags["board_done"].wait()
            self.flags["players_ammount_done"].wait()
            for received_player in response["players_data"]:
                for player in self.players: #Once per player
                    if received_player["order"] is player.order:
                        player.uuid = received_player["uuid"]
                        player.name = received_player["name"]
                        break
            self.flags["players_data_done"].set()
        elif "characters_data" in response and not self.server:
            self.flags["board_done"].wait()
            self.flags["players_ammount_done"].wait()
            self.flags["players_data_done"].wait()
            for character in response['characters_data']:
                char = None
                for player in self.players:
                    if character['player'] == player.uuid:
                        size = self.cells.sprites()[0].rect.size
                        constructor = Character.get_constructor_by_key(character['type'])
                        sprite_folder = Character.get_sprite_folder_by_key(character['type'])
                        char = constructor(player.name, player.uuid, character['id'], (0, 0), size,\
                                            self.resolution, sprite_folder, uuid=character['uuid'])
                        if player.uuid == self.my_player:
                            char.set_active(True)
                        player.characters.add(char)
                if char:
                    cell = self.get_cell_by_real_index(character['cell'])
                    cell.add_char(char)
                    char.set_cell(cell)
                    self.characters.add(char)
            for player in self.players:
                player.update()
            self.send_ready()
        elif "start" in response:
            pass
        elif "player_id" in response:
            self.my_player = response['player_id']
        elif "success" in response: #This one needs no action
            pass
        elif "move_char" in response:   #Moving around drag_char by other players.
            for char in self.characters:
                if char.uuid == response['uuid']:
                    char.rect.center = tuple(x*self.resolution for x in response['center'])
                    break 
        elif "drop_char" in response:   #Dropping the opponent char somewhere.
            for char in self.characters:
                if char.uuid == response['character']:
                    cell = self.get_cell_by_real_index(response['cell'])
                    char.set_cell(cell)             #Positioning the char
                    if not cell.is_empty():
                        self.kill_character(cell)   #Killing char if there is one 
                    cell.add_char(char)
        elif "next_turn" in response:    #Next turn with the player that should play it
            if response['player'] is not self.my_player:  #If the last play wasn't me
                self.next_player_turn()
                if self.current_player.uuid == self.my_player:
                    self.my_turn = True
        else:
            LOG.log('info', 'Unexpected response: ', response)

    def get_board_params(self):
        """Chisels down the entire parameters to get just the ones that all the clients must share."""
        params = {"inter_path_frequency"  : self.params["inter_path_frequency"],
                "circles_per_lvl"       : self.params["circles_per_lvl"],
                "max_levels"            : self.params["max_levels"] ,
                "center_cell"           : self.params["center_cell"],
                "quadrants_overlap" : self.params["quadrants_overlap"]}
        return params

    def send_data(self, data_to_send, compression=None):
        """Sends data to the server with a blocking call that waits for a reply.
        Args:
            data_to_send (dict):    Data to send to the server (in a JSON schema).
            compression (int, default=None):    Level of compression of the data when sending it.
        Returns:
            (dict): Reply of the server. Usually a Success=True, or an ACK=True."""
        while True:
            try:
                self.client.send(data_to_send, compression=compression)
                reply = self.client.receive(True)
                return reply
            except ValueError:
                LOG.log('warning', 'SEND_DATA: There was a problem receiving the packet in the sockets, retrying...')
                LOG.log('warning', 'Mockingly: iNvAliD litERaL for iNt() with BASe 10: b\"{\"')

    def send_data_async(self, data_to_send, compression=None):
        """Sends data to the server with a non-blocking call and exits without waiting for a reply.
        Args:
            data_to_send (dict):    Data to send to the server (in a JSON schema).
            compression (int, default=None):    Level of compression of the data when sending it."""
        self.client.send(data_to_send, compression=compression)

    def request_data(self, command, compression=None):
        """Requests data to the server with a blocking call that waits for a reply.
        Args:
            command (str):  Data requested of the server.
            compression (int, default=None):    Level of compression of the request petition.
        Returns:
            (dict): Reply of the server. Success=True if the data couldn't be provided now, or the data itself."""
        while True:
            try:
                self.client.send({command: True}, compression=compression)
                reply = self.client.receive(True)
                return reply
            except ValueError:
                LOG.log('warning', 'REQUEST_DATA: There was a problem receiving the packet in the sockets, retrying...')
                LOG.log('warning', 'Mockingly: iNvAliD litERaL for iNt() with BASe 10: b\"{\"')

    def request_data_async(self, command, compression=None):
        """Requests data to the server with a non-blocking call and exits without waiting for a reply.
        Args:
            command (str):  Data requested of the server.
            compression (int, default=None):    Level of compression of the request petition."""
        self.client.send({command: True}, compression=compression)

    def ALL_PLAYERS_LOADED(self):
        """"Sets the flag started to True when all the players are loaded.
        In the host, after creating the players and characters like in the normal board, it sends
            the data of all of them to the server.
        In the non-host clients, when the mock-empty-players are created, we unblock the threads waiting to assign
            attributes to the players and characters to the board."""
        super().ALL_PLAYERS_LOADED()
        if self.started:
            if self.server:
                self.send_player_and_chars_data()
                return
            else:
                self.flags["players_ammount_done"].set()

    def send_player_and_chars_data(self):
        """"Sends all the players and the characters info to the server, 
        for it to be broadcasted to the clients when requested. 
        Executed just on the host."""
        players = []
        for player in self.players:
            players.append(player.json())
        self.send_data_async({"players_data": players})
        chars = []
        for cell in self.cells:
            char = cell.get_char()
            if char:
                chars.append(char.json(cell.get_real_index()))
        self.send_data_async({"characters_data": chars})
        self.send_ready()

    def send_ready(self):
        self.send_data_async({'ready': True})

    #TODO CONTINUE HEEEERE
    def send_update(self, data):
        reply = self.client.send_data({"update": True})
        print(str(reply))
    
    def mouse_handler(self, event, mouse_movement, mouse_position):
        super().mouse_handler(event, mouse_movement, mouse_position)
        if mouse_movement:
            if self.drag_char:
                self.client.send_data_async({}) #TODO Send drag_char position

    def pickup_character(self):
        if self.my_turn:
            super().pickup_character()
        else:
            super().pickup_character(get_dests=False)

    def drop_character(self):
        if self.my_turn:
            super().drop_character()
            self.send_data_async({'drop_character': True, 'character': self.drag_char.sprite.uuid,\
                                'cell':self.active_cell.sprite.get_real_index()})
        else:
            self.client.send_data_async({}) #TODO Send drag_char position

    def next_player_turn(self):
        super().next_player_turn()
        if self.my_turn:
            self.my_turn = False
            self.send_data_async({"end_turn": True, "player": self.my_player})

    def destroy(self):
        self.reconnect = False
        self.client.disconnect()
        if self.server:
            self.server.accepting_disallow()
            self.server.disconnect_clients()
            self.server.disconnect()