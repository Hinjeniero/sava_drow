"""--------------------------------------------
network_board module. Contains a board subclass capable of communicate with
other boards through sockets.
Have the following classes.
    NetworkBoard
--------------------------------------------"""

#Python libraries
import threading
import time
import random
import pygame
import uuid
import datetime
import requests #Only used to get the servers when getting all of them from the table of servers

#External libraries
#from external.Mastermind import MastermindServerTCP, MastermindClientTCP
#from external.Mastermind._mm_errors import *   #This one doesnt catch the exception for some fuckin reasoni
from external.Mastermind import *   #I dont like this one a bit, since it has to import everything
#Selfmade libraries
from strings import CONFIG_BOARD_DIALOGS
from settings import NETWORK, MESSAGES
from dialog_generator import DialogGenerator
from obj.sprite import TextSprite
from obj.board_server import Server
from obj.ui_element import ScrollingText
from obj.board import Board
from obj.players import Character
from obj.utilities.utility_box import UtilityBox
from obj.utilities.decorators import run_async_not_pooled
from obj.utilities.logger import Logger as LOG
from obj.utilities.exceptions import ServiceNotAvailableException

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
        ready (boolean)
        overlay_text (:obj:pygame.Surface)
        connected (:obj: threading.Event):  Flag to block the threads in the case of a disconnection, and unblock them later.
        change_turn (:obj: threading.Event):
        next_turn_event (:obj: pygame.Event):
        connection_error_event (:obj: pygame.Event):
        client (:obj:omethingfohisfdhhidffsdsfhidoso):   Our connection object that will be used to communicate with the server. 
        client_lock (:obj: threading.Lock): Lock to make the access to the client thread-safe.
        server (:obj: BoardServer): Server object. Only the host contains it to start it, otherwise is None.
        my_player (int):Uuid of the player that we will be controlling on the board.
        my_turn(boolean):   True if is the turn of my player, False otherwise.
        player_names (Dict->somefshfoisofdhithing:obj:pygame.Surface):
        flags (dict):   Dict of threading.Event objects that block threads when they try to make an action that needs a not ready yet asset.
        reconnect (boolean):    True if to reconnect after losing connection, False otherwise.
    """

    def __init__(self, id_, event_id, end_event_id, resolution, obj_uuid=None, direct_connection=False, host=False, server=None, **params):
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
        if host:
            super().__init__(id_, event_id, end_event_id, resolution, initial_dice_screen=False, **params)
        else:
            super().__init__(id_, event_id, end_event_id, resolution, empty=True, initial_dice_screen=False, **params) #To generate the environment later
        self.uuid = obj_uuid if obj_uuid else uuid.uuid1().int    #Using this if crashing would led to more conns than players
        self.ip = None
        self.port = None
        self.ready = False
        self.overlay_text = None
        self.connected = threading.Event()
        self.change_turn = threading.Event()
        self.next_turn_event = pygame.event.Event(event_id, command='next_turn_network_board')
        self.connection_error_event = pygame.event.Event(event_id, command='connection_error')
        self.client = None
        self.client_lock = threading.Lock()
        self.server = server
        self.my_player = None
        self.my_turn = False
        self.players_names = {}
        self.flags = {}     #Used only if client and not host.
        self.reconnect = True
        NetworkBoard.generate(self, host, direct_connection)

    @staticmethod
    def generate(self, host, direct_connection):
        """This method sets the adequate ip, checking if this object is the host or not.
        Initiates the client, and makes it connect to the server.
        Also makes that distinction to start the server, or to set the flags needed to receive information from the host.
        Logs errors if those are of type MastermindError.
        Args:
            self (:obj: NetworkBoard):  NetworkBoard object calling this method
            host (boolean): True if this board is the host, False otherwise."""
        self.overlay_text = ScrollingText('updates', self.event_id, self.resolution, transparency=180)
        self.client = MastermindClientTCP(NETWORK.CLIENT_TIMEOUT_CONNECT, NETWORK.CLIENT_TIMEOUT_RECEIVE)
        try:
            if host:
                self.server.start(NETWORK.SERVER_IP, NETWORK.SERVER_PORT)
                self.set_ip_port(NETWORK.CLIENT_LOCAL_IP, NETWORK.SERVER_PORT)
            else:
                self.generate_connect_dialog(direct_connection)
                self.flags["ip_port_done"] = threading.Event()
                self.flags["board_done"] = threading.Event()
                self.flags["players_ammount_done"] = threading.Event()
                self.flags["players_data_done"] = threading.Event()
            self.start(host)
        except Exception as exc:
            self.exception_handler(exc)

    def generate_events(self):
        super().generate_events()
        self.events['connection_error'] = pygame.event.Event(self.event_id, command='connection_error')
        self.events['pause_game'] = pygame.event.Event(self.event_id, command='pause_game')  #Sent when anything happens in this client
        self.events['servers_table'] = pygame.event.Event(self.event_id, command='servers_table_unreachable')  #Sent when anything happens in this client

    @run_async_not_pooled
    def generate_connect_dialog(self, direct_connection):
        """Generates the matching essential dialog to get the board started. The dialog depends on if we are doing a direct connection, 
        or checking the public list of servers and picking one. 
        First case, a dialog with the connection ip and port input fields will be generated.
        In the second case, a table showing the current running servers will be made.
        Args:
            direct_connection (boolean):    Flag that mark if we are connecting directly (True), or by choosing one of the public options (False)"""
        #TODO To update this just destroy it and rebuild it or whatever. Take into edxample the update_scoreboard in Board.
        if direct_connection:
            dialog = DialogGenerator.create_input_dialog('ip_port', tuple(x//3 for x in self.resolution), self.resolution,\
                                                        ('ip', 'send_ip', str(NETWORK.CLIENT_IP)), ('port', 'send_port', str(NETWORK.SERVER_PORT)))
        else:
            rows = self.get_all_servers()
            dialog = DialogGenerator.create_table_dialog('server_explorer', 'set_ip_port', (self.resolution[0]//1.3, self.resolution[1]//10),\
                                                        self.resolution, CONFIG_BOARD_DIALOGS.SERVER_TABLE_KEYS, *rows)
        self.dialogs.add(dialog)
        if direct_connection:   self.show_dialog('input')
        else:                   self.show_dialog('table')

    def get_all_servers(self):
        try:
            result = UtilityBox.do_request(NETWORK.TABLE_SERVERS_GET_ALL_ENDPOINT)
            servers = []
            for server in result['data']:
                date = datetime.datetime.fromtimestamp(float(server['timestamp'])).strftime('%m-%d %H:%M')
                data = (server['alias'], server['ip'], server['port'], server['players']+'/'+server['total_players'], date)
                servers.append((data, server['ip']+':'+server['port']))
            return servers
        except Exception:   #The endpoint of table servers couldn't be reached
            self.post_event('servers_table')

    @run_async_not_pooled
    def generate_players_names(self):
        """Creates and adds the texts surfaces that match the different players names. This is done to show in the local client the 
        name of the other clients at the position at where their mouse is. Kind of a gimmick, but it's cool"""
        for player in self.players:
            if player.uuid != self.my_player:   #We dont want our player name over our cursor.
                player_text = TextSprite('sprite_'+player.name, (0, 0), tuple(int(x*0.05) for x in self.resolution), self.resolution, player.name)
                self.players_names[player.uuid] = player_text

    def exception_handler(self, exception):
        """Handles the most common exception of this object methods. Since this is done in a lot of methods, we can save code in this way.
        Does so by getting an input exception, catching it in the method, and checking which type of exception is. 
        Afterwards, it will send an event to the pygame event queue, matching the exception .
        Raise:
            exception (Exception):  Its risen to catch the exception in this method itself, so we can control the exception here."""
        try:
            raise exception
        except (MastermindErrorSocket, MastermindError):   #If there was an error connecting
            LOG.error_traceback()
            self.post_event('connection_error')
        except requests.exceptions.ConnectionError:
            LOG.error_traceback()
            self.post_event('connection_error')
            raise ServiceNotAvailableException("The server that holds the table of open games is down right now.")
        except Exception:
            LOG.error_traceback()
            self.post_event('connection_error')

    @run_async_not_pooled
    def start(self, host):
        """Starts the connection with the server, and initiates the threads that take care of the keep_alive packets, and the
        receiving socket end. The second thread is respondible for the received responses from the server (Usually redirected from other players)."""
        try:
            if not host:
                self.flags["ip_port_done"].wait()
            self.LOG_ON_SCREEN('Trying to connect to the server in ', self.ip, ':', self.port)
            self.connect()
            self.keep_alive() #Creating thread
            self.receive_worker()
            self.send_handshake(host)
        except Exception as exc:
            self.exception_handler(exc)

    def set_ip_port(self, ip=None, port=None):
        """Sets the ip attribute and/or the port attribute, according to the input received.
        If both are received, the flag that signals that we have the essential information to finally connect to the server,
        is set to True.
        Args:
            ip (String, default=None):  Ip of the server to connect to.
            port (Int, default=None):   Port of the server to connect to."""
        if ip:
            self.ip = ip
        if port:
            self.port = port
        if self.ip and self.port:
            try:
                self.flags["ip_port_done"].set()
            except KeyError:
                pass

    def send_handshake(self, host):
        """"Sends the first request to the server, with our user UUID, and a host boolean.
        If this is the host, the method will send the parameters for the board creation.
        Otherwise, will ask for those parameters, along with other essential data, like
        the generated players data, the ammount of players, or the generated characters data (like the dropping cell and such).
        Also, sends the a random throw of a dice to decide the order of the players.
        Args:
            host (boolean): Flag saying if we are the host or not (Just a lowly client)."""
        self.send_data({"host": host, "id": self.uuid})
        if host:
            self.send_data_async({"params": self.get_board_params()})
            self.LOG_ON_SCREEN("sent board creation settings to server")
        else:
            self.request_data_async("params")           #To get the board creation params
            self.request_data_async("players")          #To get the number of players
            self.request_data_async("players_data")     #To get the data of the players
            self.request_data_async("characters_data")  #To get the data of the characters
        dice = random.randint(1, 6)
        self.send_data_async({"start_dice": dice, "id":self.uuid})    #Sending dice result for the player assignments
        self.LOG_ON_SCREEN("rolled a "+str(dice))

    def connect(self):
        """Manages the connection of the client to the server, if the ip and port are available."""
        if self.ip and self.port:
            self.client_lock.acquire()
            self.LOG_ON_SCREEN('Connecting to '+str(self.ip)+' in port '+str(self.port))
            self.client.disconnect()
            self.client.connect(self.ip, self.port)
            self.connected.set()
            self.client_lock.release()
            LOG.log('info', 'Client ', self.uuid, ' connected to the server in the address ',\
                    self.ip, ':', self.port)

    @run_async_not_pooled
    def keep_alive(self):
        """SubThread that sends 'keep-alive' requests to the server in an infinite loop, to keep the connection, well, alive.
        Sends a request per second. It's a busy loop, using sleep. Not the best approach, but well, it works."""
        while True:
            try:
                self.request_data_async("keep-alive")   #Response will be handled in the receiving thread
                time.sleep(1)
            except MastermindErrorClient:               #If disconnected from server
                if self.reconnect:
                    self.connect()
                else:
                    break

    @run_async_not_pooled
    def receive_worker(self):
        """Subthread that is listening to the server in an infinite loop. Uses a blocking receiving call to avoid a busy loop.
        If it receives a response, it redirects it to the response_handler method. Also calls connect if the connections is lost."""
        while True:
            try:
                data = self.client.receive(True)
                self.response_handler(data)
            except MastermindErrorClient:   #Timeout/disconnection
                if self.reconnect:
                    self.connected.wait()
                else:
                    break
            except ValueError:
                LOG.log('warning', 'RECEIVE_WORKER: There was a problem receiving the packet in the sockets, retrying...')
                LOG.log('warning', 'Mockingly: iNvAliD litERaL for iNt() with BASe 10: b\"{\"')
    
    @run_async_not_pooled
    def response_handler(self, response):
        """Handler of the received responses from the server. Accepts responses in the JSON schema.
        It decides what to do judging by the existance of different keys in the JSON form received.
        This runs on a subthread because some of the received responses require actions that can only
        be put on motion after some requirements are fulfilled. Thus, it can block on some of the flags.
        Args:
            response (dict):JSON schema. Contains the various replies of the server."""
        if "params" in response and not self.server:    #REQUESTING THE BOARD GENERATION PARAMETERS
            self.LOG_ON_SCREEN('received the board params, creating board...')
            self.params.update(response["params"])
            self.generate_mapping()
            self.LOG_ON_SCREEN('created map...')
            self.generate_environment()
            self.LOG_ON_SCREEN('created the board...')
            self.flags["board_done"].set()
        elif "players" in response and not self.server:
            self.LOG_ON_SCREEN('received the players number, creating mock players...')
            self.flags["board_done"].wait()
            for i in range (0, 4, 4//response["players"]):
                self.create_player("null", i, None, empty=True)  #The name will be overwritten later on
        elif "players_data" in response and not self.server:
            self.LOG_ON_SCREEN('received the players data, updating players...')
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
                    if cell.promotion:
                        cell.owner = char.owner_uuid
            for player in self.players:
                player.update()
            self.send_ready()
        elif "start" in response:
            self.ready = True
            self.console_active = False
            self.activate_my_characters()
            if self.current_player.uuid == self.my_player:
                self.update_map()
                self.post_event('my_turn')  #This makes the popup saying that is my turn, show.
                self.my_turn = True
        elif "player_id" in response:   #TODO THIS IS POORLY DONE, THE ID SENT IS THE BOARD ONE!!!
            self.my_player = response['player_id']
            LOG.log('info', 'My player is ', self.my_player)
        elif "success" in response: #This one needs no action
            pass
        elif "mouse_position" in response:
            player_text = self.players_names[response['mouse_position']]
            player_text.set_center(response['center'])
        elif "move_character" in response:   #Moving around drag_char by other players.
            char = next(char for char in self.characters if char.uuid == response['move_character'])
            center = tuple(x*y for x,y in zip(self.resolution, response['center']))
            char.set_center(center)
            self.players_names[char.owner_uuid].set_center(center)
        elif "drop_character" in response:
            dest_cell = self.get_cell_by_real_index(response['cell'])
            char = next(char for char in self.characters if char.uuid == response['drop_character'])
            last_cell = self.get_cell_by_real_index(char.current_pos)
            if dest_cell.has_char():
                self.kill_character(dest_cell, char)    #Killing char if there is one 
            char.set_cell(dest_cell)                    #Positioning the char
            dest_cell.add_char(char)
            last_cell.kill_char()                       #Not really killing, just want to empty the last cell
            self.update_cells(last_cell, dest_cell)
            self.change_turn.set()
        elif "end_turn" in response:    #Next turn with the player that should play it
            self.thinking_sprite.sprite.set_visible(False)
            self.change_turn.wait()
            self.next_player_turn()
            self.change_turn.clear()
            self.activate_my_characters()   #Just in case they have been frozen earlier
        elif "swap" in response:
            original_char = next(char for char in self.characters if char.uuid == response['original'])
            player = next(player for player in self.players if player.uuid == original_char.owner_uuid)
            self.swapper.send(original_char)
            self.swapper.send(next(char for char in player.fallen if char.uuid == response['new']))
        elif "dice_value" in response:  #The dice in this board will be updated
            #TODO SHOW NOTIFICATION
            self.dice.sprite.add_throw(response['player'])
        elif "turncoat" in response:    #All characters will be locked down in this turn.
            #They will all be paused only in our screen (Only graphically), the actions of the user client will still reach here.
            self.post_event('turncoat')
            my_player = next(player.uuid == self.my_player for player in self.players)
            my_player.pause_characters()
        elif "cpu_player" in response:  #Its the cpu player turn in host
            self.post_event('cpu')
            self.thinking_sprite.sprite.set_visible(True)
        elif "admin" in response:
            event_id_string = 'admin_on' if response["admin"] else 'admin_off'
            self.post_event(event_id_string)
        elif "pause" in response:   #This will usually happen when another client disconnects.
            self.post_event('pause_game')   #TODO for now, a disconenction will issue a game lost msg.
            #TODO BLOCK MOVEMENTS! And how to make the player updated to the last information??
        else:
            LOG.log('info', 'Unexpected response: ', response)

    def shuffle(self):
        """Method that shuffles the dice. It overloads the superclass method because we 
        only want the dice to shuffle if it's our turn, otherwise do nothing."""
        if self.my_turn:
           super().shuffle() 

    def activate_my_characters(self):
        """Called each turn. Sets the characters that belong to the player of this client to active=True.
        This is done so we can move them around, even if it's not our turn. We still cannot change them of cell if its not, of course."""
        if self.my_player:
            for char in self.characters:
                char.set_state('idle')
                if char.owner_uuid == self.my_player:
                    char.set_active(True)
                else:
                    char.set_active(False)

    def get_board_params(self):
        """Chisels down the entire parameters to get just the ones that all the clients must share.
        Returns:
            (:Dict:):   Dict with the essential parameters for the generation of a board on other clients."""
        params = {"inter_path_frequency"  : self.params["inter_path_frequency"],
                "circles_per_lvl"       : self.params["circles_per_lvl"],
                "max_levels"            : self.params["max_levels"] ,
                "center_cell"           : self.params["center_cell"],
                "quadrants_overlap" : self.params["quadrants_overlap"]}
        return params

    def send_data(self, data_to_send, compression=None):
        """Sends data to the server with a blocking call that waits for a reply.
        Args:
            data_to_send (Dict->Any:Any):   Data to send to the server (in a JSON schema).
            compression (int, default=None):    Level of compression of the data when sending it.
        Returns:
            (Dict->Any:Any):    Reply of the server. Usually a Success=True, or an ACK=True."""
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
            data_to_send (Dict->Any:Any):   Data to send to the server (in a JSON schema).
            compression (int, default=None):    Level of compression of the data when sending it."""
        self.client.send(data_to_send, compression=compression)

    def request_data(self, command, compression=None):
        """Requests data to the server with a blocking call that waits for a reply.
        Args:
            command (String):   Data requested of the server.
            compression (int, default=None):    Level of compression of the request petition.
        Returns:
            (Dict->Any:Any):    Reply of the server. Success=True if the data couldn't be provided now, or the data itself."""
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
            command (String):   Data requested of the server.
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
            self.console_active = True
            if self.server:
                self.send_player_and_chars_data()
                return
            else:
                self.flags["players_ammount_done"].set()

    def send_player_and_chars_data(self):
        """"Sends all the players and the characters info to the server, 
        for it to be broadcasted to the clients when requested. 
        Executed just on the host.
        Also takes care of sending the starting dice value of the cpu controlled players, since
        they were the only ones left to send."""
        players = []
        for player in self.players:
            players.append(player.json())
            if not player.human:    #Sends the starting dice value, so the server can finally return the ordering of players
                self.send_data_async({"start_dice": random.randint(1, 6), "cpu_player": player.uuid, "id":self.uuid})
        self.send_data_async({"players_data": players})
        chars = []
        for cell in self.cells:
            char = cell.get_char()
            if char:
                chars.append(char.json(cell.get_real_index()))
        self.send_data_async({"characters_data": chars})
        self.LOG_ON_SCREEN("sent the characters and players data to the server")
        self.send_ready()

    def send_ready(self):
        """Sends the command 'ready' to the server, signalizing that this client is ready to start the game."""
        self.send_data_async({'ready': True})
        self.LOG_ON_SCREEN("ready, waiting for the other players...")
        self.generate_players_names()
    
    def mouse_handler(self, event, mouse_buttons, mouse_movement, mouse_position):
        """Captures the mouse and handles the events regarding this one. More info in method in superclass.
        In this subclass, if mouse_movement is detected, the character under that movement is broadcasted to the rest of
        the clients.
        Args:
            event (:obj: pygame.event): Event received from the pygame queue.
            mouse_movement(boolean, default=False):    True if there was mouse movement since the last call.
            mouse_position (Tuple->int, int, default=(0,0)):   Current mouse position. In pixels."""
        if self.dialog:
            super().mouse_handler(event, mouse_buttons, mouse_movement, mouse_position)
            return
        if self.ready:
            super().mouse_handler(event, mouse_buttons, mouse_movement, mouse_position)
            if mouse_movement:
                if self.drag_char:
                    center = tuple(x/y for x,y in zip(self.drag_char.sprite.rect.center, self.resolution))
                    self.send_data_async({"move_character":self.drag_char.sprite.uuid, "center": center})
                else:
                    self.send_data_async({"mouse_position": self.my_player, "center": mouse_position})

    def pickup_character(self):
        """Picks up a character, and get the possible destinies if it is our turn. More info in this case in superclass method.
        Otherwise only allows to wiggling around."""
        if self.my_turn:
            super().pickup_character()
        else:
            super().pickup_character(get_dests=False)

    def after_swap(self, orig_char, new_char):
        super().after_swap(orig_char, new_char)
        if orig_char.owner_uuid == self.my_player and new_char.owner_uuid == self.my_player\
        or self.server and not self.current_player.human:    #If this was a local swap and not a received one in response_handler from another player
            self.send_data_async({"swap": True, "original": orig_char.uuid, "new": new_char.uuid})

    def update_character(self, char):
        super().update_character(char)
        self.send_data_async({"character": char.uuid, "update_character": True})

    def drop_character(self):
        """Makes the action of the superclass if my_turn is True. Otherwise, just moves the character to the last cell
        where it was. After this, it broadcast the result to the rest of the clients (sending it to the server)."""
        character = self.drag_char.sprite
        if self.my_turn:
            movement = super().drop_character()
            if movement:
                self.send_data_async({'drop_character': character.uuid, 'cell':self.active_cell.sprite.get_real_index()})
        else:
            self.drag_char.sprite.set_selected(False)
            self.drag_char.sprite.set_hover(False)
            self.drag_char.empty()
            character.set_center(self.last_cell.sprite.center)
            center = tuple(x/y for x,y in zip(character.rect.center, self.resolution))
            self.send_data_async({"move_character": character.uuid, "center": center})

    def next_player_turn(self):
        """Makes the actions needed to advance a turn, and communicates with the server if my_turn is True."""
        super().next_player_turn(use_stop_state=False)
        if self.my_turn or (not self.current_player.human and self.server):
            self.my_turn = False    #If the second condition, this doesn't really matter
            self.send_data_async({"end_turn": True})
        else:
            if self.current_player.uuid == self.my_player:
                self.my_turn = True
                self.post_event('my_turn')

    @run_async_not_pooled
    def do_ai_player_turn(self):
        #do ai turn calls move chjaracter without calling drop character, which is the onw that sends
        #good shit here
        movement_executed = []  #This is written like this so pylint doesn't show an error, actually it doesn't matter, it will be assigned inside thje super method
        thread_doing_the_work = super().do_ai_player_turn(result=movement_executed)
        thread_doing_the_work.wait()
        character = self.get_cell_by_real_index(movement_executed[0]).get_char()
        self.send_data_async({'drop_character': character.uuid, 'cell': movement_executed[-1]})

    def dice_value_result(self, value):
        """To sync the dices across all the clients"""
        super().dice_value_result(value)
        self.send_data_async({"player": self.current_player.uuid, "dice_value": value})
            
    def activate_turncoat_mode(self):
        """This is to avoid conflicts when the other players move their chars around"""
        super().activate_turncoat_mode()
        self.send_data_async({"player": self.current_player.uuid, "turncoat": True, "lock_characters": True})   

    def draw(self, surface):
        try:
            super().draw(surface)
            all(name.draw(surface) for name in self.players_names.values())
            #Special cases from now on
            if self.dialog and self.dialog.visible:
                self.dialog.draw(surface)
        except pygame.error:
            LOG.log(*MESSAGES.LOCKED_SURFACE_EXCEPTION)

    def set_admin_mode(self, admin):
        self.admin_mode = admin
        if self.admin_mode:
            self.send_data_async({"admin": True})
        else:
            self.send_data_async({"admin": False})

    def win(self):
        if any(self.my_player == player.uuid for player in self.players if not player.dead):
            super().win()
        else:
            LOG.log("info", "Tough luck, you lost this battle!")
            self.play_sound('lose')
            self.post_event('lose')
            self.finished = True    #To disregard events except esc and things like that
            self.show_score = True  #To show the infoboard.

    def destroy(self):
        """Sets the flags to signal the end of the threads and disconnects 
        clients, and the server if this networkboard is the host."""
        try:
            self.send_data_async({"disconnect": True, "client": self.uuid})
        except Exception:
            pass
        self.reconnect = False
        self.client.disconnect()
        for flag in self.flags.keys():
            self.flags[flag].set()  #Let those threads crash
        if self.server:
            self.server.accepting_disallow()
            self.server.disconnect_clients()
            self.server.disconnect()