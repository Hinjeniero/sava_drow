"""--------------------------------------------
board_server module. Contains the logic that builds a server
to hold a game between different computers.
Have the following classes.
    BoardServer
--------------------------------------------"""

__all__ = ['BoardServer']
__version__ = '1.0'
__author__ = 'David Flaity Pardo'

#Python full fledged libraries
import pygame
import threading
import uuid
import time
#External libraries
from external.Mastermind import *
#Selfmade libraries
from settings import NETWORK, USEREVENTS
from obj.utilities.ip_parser import IpGetter
from obj.utilities.utility_box import UtilityBox
from obj.utilities.decorators import run_async_not_pooled
from obj.utilities.synch_dict import Dictionary
from obj.utilities.logger import Logger as LOG
from obj.utilities.exceptions import ServiceNotAvailableException

class Server(MastermindServerTCP):
    """"Class Server. Inherits from MastermindServerTCP.
    This server allows to have a match between players on different computers,
    on the same board, with the same players and characters. Also synchronizes the actions between them,
    and communicates with the clients to have all of them in the same time spot, and the same turn, with the same result.
    Classic game server to which the clients can connect.
    Have 2 threads. One in the method Start, and another one in the method petition_worker. More details in those methods.
    Attributes:
        host (:obj:):   Connection object with the host. Useful when acting in different manners on the responses depending on the source.
        total_players (int):Total number of players that will connect to this server. Useful when checking how many player ready, etc.    
        total_chars (int):  Total number of characters that this server will hold. Useful to know when we have received all the characters, etc.
        players_ready (int):Number of players that have already generated the board, players and characters, and are ready. 
        hold_lock (:obj: threading.Condition):  Lock of the list of unattended petitions, making this one thread-safe.
        on_hold_empty (:obj: threading.Event):  Flag that allow the petition_worker thread to enter and get the first petition if the list has items,
                                                but blocks him otherwise until there are items.
        on_hold_resp (list->tuple): List of unanswered petitions. Those are recycled and checked until an adequate response is delivered.
                                    The tuple follow the schema (connection_object, unanswered_petition).
        clients (:obj: Dictionary): Holds the clients's connections (value) with the uuid(key) of each one (In case one reconnects). 
        data (:obj: Dictionary):    Holds data about the board. An identificative string is the key, and the data itself the value.
        players_data (:obj: Dictionary):Holds the current state of the players. The uuid is the key, and the current json of each one the value.
        chars_data (:obj: Dictionary):  Holds all the characters of the board. uuid as the key, and the character info json as the value.
                                        This one is intended to be broadcasted initially to the slave clients, more than updated
                                        in each turn to follow the game.
    """
    
    def __init__(self, number_of_players, private=False, obj_uuid=None):
        """Constructor of the server.
        Args:
            number_of_players(int): Number of players/clients that this server will hold."""
        MastermindServerTCP.__init__(self, NETWORK.SERVER_REFRESH_TIME, NETWORK.SERVER_CONNECTION_REFRESH, NETWORK.SERVER_CONNECTION_TIMEOUT)
        self.uuid = obj_uuid if obj_uuid else uuid.uuid1().int    #Using this if crashing would led to more conns than players
        self.public_ip = None
        self.private_ip = None
        self.private_server = private
        self.host = None    #Connection object. This is another client, but its the host. I dunno if this will be useful yet.
        self.total_players = number_of_players
        self.total_chars = None
        self.players_ready = 0
        self.ready = threading.Event()
        self.barrier = []
        self.barrier_lock = threading.Lock()
        self.hold_lock = threading.Lock()
        self.on_hold_empty= threading.Event()
        self.on_hold_resp = []
        self.on_hold_named = Dictionary(exceptions=True)
        self.clients = Dictionary()   #Connections objects (Includes host)
        self.data = Dictionary(exceptions=True)
        self.players_data = Dictionary(exceptions=True)
        self.chars_data = Dictionary(exceptions=True)
        self.all_players_received = threading.Event()

    def set_chars(self, number_of_chars):
        """Sets the total number of characters that the board will have.
        Args:
        number_of_chars(int):   Total number of characters that the board of this server will have."""
        self.total_chars = number_of_chars

    def add_data(self, key, data):
        """Adds useful data to the server's data dict. Can be retrieved later with a request in json.
        Args:
            key (:obj: any):Key of the data that will be used in the later retrieval.
            data(:obj: any):Data to save."""
        self.data.add_item(key, data)

    def add_client(self, id_, conn_client):
        """Adds an identified client to the server. 
        Args:
            id_ (:obj: any):Identificator of the client. It's his uuid.
            conn_client(:obj: any): Connection object that will be used to communicate with the client. This is kept alive by him, too."""
        if id_ in self.clients.keys():
            self.clients.update_item(id_, conn_client)
            LOG.log('info', 'The client ', id_, ' reconnected!')
            #TODO If this was a reconnection
            #TODO Send ALL the info (ask the host for current situation), with the current board state
            #TODO Send your current player
            #TODO Send who IS the current player
            return {"success": True, "msg": "The client "+str(id_)+" connection object was updated successfully."}
        elif len(self.clients.values()) < self.total_players:
            self.clients.add_item(id_, conn_client)
            if not self.private_server:
                self.update_server()
            return {"success": True, "msg": "The client "+str(id_)+" was added successfully."}
        else:
            return {"success": False, "error": "The server is full."}

    def add_player(self, player):
        """Adds the players data to the server's players dict.
        Args:
            player(:obj: dict/json):JSON containing all the players useful params, including:
                                    uuid(int), order(int), name(str), turn(int), dead(bool)"""
        self.players_data.add_item(player["uuid"], player)

    def add_char(self, character):
        """Adds the characters data to the server's players dict.
        Args:
            character(:obj: dict/json): JSON containing all the character useful params, including:
                                        uuid(int), id(int), player(int), type(str), cell(int)"""
        self.chars_data.add_item(character["uuid"], character)

    def get_data(self, key):
        """Gets data from the data dict in the server. In the case that the provided key doesn't match any data,
        a response is issued with a 'success' = False.
        Args:
            key (:obj: any):  Key or identifier of the data that we want to retrieve.
        Returns:
            (Dict): Returns a dict in JSON format containing the data if it was found, or a success false otherwise."""
        response = {}
        try:
            response[key] = self.data.get_item(key)
        except KeyError:    #This will never raise, since data is
            response = {"success": False, "error": "The data with the key "+key+" was not found in the server"}
        return response

    def register_server(self):
        """Sends this server information to the endpoint holding all the public servers.
        Raises an exception if the endpoint cant be reached."""
        try:
            register_server_endpoint = IpGetter.get_servers_table_dir()+NETWORK.TABLE_SERVERS_ADD_ENDPOINT
        except ServiceNotAvailableException:
            raise ServiceNotAvailableException('The public service with the data of serverss is unreachable.')
        json_petition = {'uuid': self.uuid, 'ip': self.public_ip, 'local_ip': self.private_ip, 'port': str(NETWORK.SERVER_PORT), 'players': 1,\
                        'total_players': self.total_players, 'alias': NETWORK.SERVER_ALIAS, 'timestamp': time.time()}
        response = UtilityBox.do_request(register_server_endpoint, method='POST', data=json_petition, return_success_only=True)
        if not response or not response['success']:
            LOG.log('warning', 'no success when adding the server to the table of servers.')
            raise Exception("no success when adding the server to the table of servers.")

    def update_server(self, **params):
        """Sends this server information to the endpoint holding all the public servers, hoping to update it.
        Called after a new player connects e.g.
        Raises an exception if the endpoint cant be reached."""
        LOG.log('info', 'Updating the server player ammount in the table of servers')
        update_server_endpoint = IpGetter.get_servers_table_dir()+NETWORK.TABLE_SERVERS_UPDATE_ENDPOINT
        json_petition = {'uuid': self.uuid, 'players': len(self.clients.values())}
        json_petition.update(params)
        response = UtilityBox.do_request(update_server_endpoint, method='POST', data=json_petition, return_success_only=True)
        if not response or not response['success']:
            LOG.log('warning', 'no success when updating the server.')
            raise Exception("no success when updating the server.")

    def delete_server(self):
        """Sends a command to delete this server information in the endpoint holding all the public servers.
        Raises an exception if the endpoint cant be reached."""
        LOG.log('info', 'Deleting the server form the public table of servers, max ammount of players reached')
        delete_server_endpoint = IpGetter.get_servers_table_dir()+NETWORK.TABLE_SERVERS_DELETE_ENDPOINT
        response = UtilityBox.do_request(delete_server_endpoint, method='POST', data={'uuid': self.uuid}, return_success_only=True)
        if not response or not response['success']:
            LOG.log('warning', 'no success when deleting the server.')
            raise Exception("no success when deleting the server.")

    def broadcast_data(self, list_of_conns, data, *excluded_conns):
        """Sends the input data to all the input connection, excluding the ones marked as such."""
        for conn in list_of_conns:
            if not any(conn == excluded for excluded in excluded_conns): 
                self.callback_client_send(conn, data)

    @run_async_not_pooled
    def add_to_barrier(self, conn_object, data):
        """Adds a connection with matching data to a barrier structure.
        The response to the data will only be delivered when all the active clients submit it."""
        self.barrier_lock.acquire()
        if len(self.barrier) == 0\
        or all(key in data.keys() for key in self.barrier[0][1].keys()):
            self.barrier.append((conn_object, data))
        if len(self.barrier) >= self.total_players:
            self.group_responses_handler()
            self.barrier.clear()
        self.barrier_lock.release()

    def group_responses_handler(self):  
        """Handles the responses that require all the client to submit the petition."""
        if 'start_dice' in self.barrier[0][1].keys():
            #Tuples - (conn, data(json)), 'dice' in saved json
            self.barrier.sort(key=lambda tuple_: tuple_[1]['start_dice'], reverse=True)
            self.all_players_received.wait()
            players = list(self.players_data.values())
            players.sort(key=lambda player: player['order'])
            for i in range (0, self.total_players):
                self.callback_client_send(self.barrier[i][0], {'player_id': players[i]['uuid']})
                #The players in there should be ordered by 'order' already. Sending uuid.
    
    def hold_petition(self, conn_obj, data):
        """Adds the petition to the on hold queue, since it couldn't be satisfied in the moment."""
        self.hold_lock.acquire()
        desired_data = next((key for key in data.keys() if 'data' in key), None)
        if desired_data:
            try:
                clients_waiting_this_data = self.on_hold_named.get_item(desired_data)
                if conn_obj not in clients_waiting_this_data:
                    clients_waiting_this_data.append(conn_obj)
            except KeyError:
                self.on_hold_named.add_item(desired_data, [conn_obj])
        else:
            self.on_hold_resp.append((conn_obj, data))
        if len(self.on_hold_resp) is not 0:
            self.on_hold_empty.set()
        self.hold_lock.release()

    @run_async_not_pooled
    def petition_worker(self):
        """SubThread witn an infinite loop that checks the list of the server unanswered petitions,
        and issues them again to the client_handle to try again. If they are still not ready, the request/petition
        will be appended at the end of this list again.
        Uses a flag to check if there are items, and a Lock to make the list thread-safe."""
        try:
            while True:
                self.on_hold_empty.wait()
                self.hold_lock.acquire()
                petition = self.on_hold_resp.pop(0)
                if 'end' in petition[1]:
                    raise Exception
                if len(self.on_hold_resp) == 0:
                    self.on_hold_empty.clear()
                self.hold_lock.release()
                self.callback_client_handle(*petition)  #This to unpack the tuple of conn,data
        except:
            LOG.log('info', 'Exception in the petition worker, the server must have disconnected')    #The server disconnected, byebye
            LOG.error_traceback()
    
    def callback_client_handle(self, connection_object, data):
        """Handles the petitions of the clients, be requests or sending of data. Uses JSON forms.
        It decides what to do judging by the existance of different keys in the JSON form received,
        and also depending on the source of the msg.
        If the petition can't be answered in this call of the method, it will be appended to the on_hold_petitions
        for later revisions.
        Always sends a reply to the client.
        Args:
            connection_object (:obj: dadsadas): Connection trhough which the client sent the JSON.
            data (dict):JSON form that contains the request or sending of data."""
        reply = None
        try:
            if "host" in data:
                if data["host"]:
                    if not self.host:
                        self.host = connection_object
                    else:
                        reply = {"success": False, "error": "There is already an host."}
                reply = self.add_client(data["id"], connection_object)
            elif "start_dice" in data:
                LOG.log('info', 'Client ', data['id'], ' rolled a ', data['start_dice'])
                self.add_to_barrier(connection_object, data)
            elif "params" in data:
                if connection_object is self.host:
                    self.add_data("params", data["params"])
                else:
                    reply = self.get_data("params")
            elif "start" in data or "ready" in data:
                self.players_ready += 1
                if self.players_ready >= self.total_players:
                    self.broadcast_data(self.clients.values(), {"start": True})
                    if not self.private_server:
                        self.delete_server()
            elif "players" in data: #At start
                reply = {"players": self.total_players}
            elif "players_data" in data:
                if connection_object == self.host:
                    for player in data["players_data"]:
                        self.add_player(player)
                    self.all_players_received.set()
                    #Sends this to the clients that were waiting
                    clients_waiting_for_players_data = self.on_hold_named.get_item("players_data")
                    reply = {"players_data": self.players_data.values_list()}
                    self.broadcast_data(clients_waiting_for_players_data, reply)

                else:
                    if len(self.players_data.keys()) < self.total_players:
                        raise KeyError
                    LOG.log('info', 'Sending players data to client')
                    reply = {"players_data": self.players_data.values_list()}
            elif "characters_data" in data:
                if connection_object == self.host:
                    for character in data["characters_data"]:
                        self.add_char(character)
                    #Sends this to the clients that were waiting
                    clients_waiting_for_chars_data = self.on_hold_named.get_item("players_data")
                    reply = {"characters_data": self.chars_data.values_list()}
                    self.broadcast_data(clients_waiting_for_chars_data, reply)

                else:
                    if len(self.chars_data.keys()) < self.total_chars:
                        raise KeyError
                    LOG.log('info', 'Sending characters data to client')
                    reply = {"characters_data": self.chars_data.values_list()}
            elif "keepalive" in data or "keep_alive" in data or "keep-alive" in data or "update" in data:
                pass
            elif "disconnect" in data:
                self.broadcast_data(self.clients.values(), {'pause':True, 'msg': 'Game paused because a client disconnected, waiting until his reconnection'}, connection_object)
            else:   #Most messages will have this behaviour, being broadcasted to all clients except the origin
                self.broadcast_data(self.clients.values(), data, connection_object)
                #elif "move_character" in data or "drop_character" in data or "end_turn" in data or "admin" in data or "swap" in data:
                #or "dice_value" in data or "turncoat" in data or "lock_characters" in data
        except (KeyError, IndexError):    #Can't attend this petition right now, most likely due to lack of data.
            LOG.log('info', 'The request ', data, ' cant be achievable right now, holding this petition')
            self.hold_petition(connection_object, data)
        if not reply:
            reply = {"success": True}
        self.callback_client_send(connection_object, reply)

    def initiate(self, ip, port):
        """SubThread that starts the server and listens for clients in the parameters specified.
        The server will listen on the tandem ip_address:port.
        Args:
            ip(str):    IP address of the server. Uses 0.0.0.0 usually.
            port(int):  Port that the server will bind to. It will listen on this one."""
        self.private_ip = IpGetter.get_local_ip(raise_exception=True)
        try:
            self.public_ip = IpGetter.get_public_ip(raise_exception=True)
        except ServiceNotAvailableException:
            pygame.event.post(pygame.event.Event(USEREVENTS.BOARD_USEREVENT, command='no_internet'))
            self.public_ip = NETWORK.LOCAL_IP
        try:
            self.connect(ip, port) #This connect is way more like a bind to the socket.
            LOG.log('info', 'Deploying server in the public ip ', self.public_ip, ':', NETWORK.SERVER_PORT)
        except MastermindErrorSocket:
            pygame.event.post(pygame.event.Event(USEREVENTS.BOARD_USEREVENT, command='server_already_exists'))
            return
        if not self.private_server:
            self.register_server()
        self.start()

    @run_async_not_pooled
    def start(self):
        """SubThread that starts the server and listens for clients in the parameters specified.
        The server will listen on the tandem ip_address:port."""
        try:
            self.petition_worker()
            self.accepting_allow_wait_forever()
        except:                 #Only way to break is with an exception
            LOG.log('info', 'Exiting from the server!')
        self.hold_petition(-1, {'end': True})
        self.accepting_disallow()
        self.disconnect_clients()
        self.disconnect()