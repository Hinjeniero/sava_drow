import threading
from obj.utilities.decorators import run_async
from obj.utilities.synch_dict import Dictionary
from settings import NETWORK
from external.Mastermind import *

class Server(MastermindServerTCP):
    def __init__(self, number_of_players):
        MastermindServerTCP.__init__(self, NETWORK.SERVER_REFRESH_TIME, NETWORK.SERVER_CONNECTION_REFRESH, NETWORK.SERVER_CONNECTION_TIMEOUT)
        self.host = None    #Connection object. This is another client, but its the host. I dunno if this will be useful yet.
        self.total_players = number_of_players
        self.players_ready = 0
        self.current_map = None
        #
        self.clients = Dictionary()   #Connections objects (Includes host)
        self.waiting = []   #Connections waiting for an event to occur. This acts as a barrier
        self.data = Dictionary()
        self.players_data = Dictionary()
        self.chars_data = Dictionary()

    def add_data(self, key, data):
        self.data.add_item(key, data)

    def add_client(self, id_, conn_client):
        self.clients.add_item(id_, conn_client)

    def add_player(self, player):
        self.players_data.add_item(player['uuid'], player['data'])
        print("ADDING")
        print(str(self.players_data.dict))

    def add_char(self, character):
        self.chars_data.add_item(character['uuid'], character['data'])
        print("ADDING CHAR")
        print("Current chars: "+str(len(self.chars_data.keys())))

    def get_data(self, key):
        self.lock.acquire()
        response = {}
        try:
            response[key] = self.get_item(key)
        except KeyError:
            response = {'success': False, 'error': 'The data with the key '+key+' was not found in the server'}
        self.lock.release()
        return response

    def send_updates(self):
        while len(self.queue) > 0:
            command = self.get_from_queue()
            for client in self.clients.values(): #Connections
                self.callback_client_handle(client, command)

    def send_start_info(self):
        for conn in self.clients.values():
            self.callback_client_handle(conn, 'player')

    def broadcast_data(self, list_of_conns, data):
        for conn in list_of_conns:
            self.callback_client_send(conn, data)

    def callback_client_handle(self, connection_object, data):
        reply = None
        for key in data.keys(): #FOLLOWING JSON FORM
            if 'id' in key:
                self.add_client(data['id'], connection_object)
            if 'host' in key:
                if not self.host:
                    self.host = connection_object
                else:
                    reply = {'success': False, 'error': 'There is already an host.'}
            elif 'params' in key and connection_object is self.host:
                if connection_object is self.host:
                    self.add_data('params', data['params'])
                else:
                    reply = self.get_data('params')
            elif 'start' in key or 'ready' in data:  #IN THIS ONE WAIT FOR ALL OF THEM TO BE ONLINE
                self.players_ready += 1
                self.waiting.append(connection_object)
                if self.players_ready >= self.total_players:
                    self.broadcast_data(self.waiting, {'unlock': True})
            elif 'players' in key: #At start
                reply = {'players': self.total_players}
            elif 'player_data' in key:
                self.add_player(data['player_data'])
            elif 'character_data' in key:
                self.add_char(data['character_data'])
            elif 'update' in key:
                reply = 'UPDATE' #reply = changes, Sends the info of the board to the whatever client requested it. (If there is new actions)
            elif 'move_char' in key:
                reply = 'MOVE' #Save the info of the char.
            elif 'menu' in key:
                pass #Changing screens, sohuld check what to do
            if not reply:   #If it wanst a request but a push of data
                reply = {'success': True}
        self.callback_client_send(connection_object, reply)

    @run_async
    def start(self, ip, port):
        self.connect(ip, port) #This connect is way more like a bind to the socket.
        try:
            self.accepting_allow_wait_forever()
        except:                 #Only way to break is with an exception
            pass
        self.accepting_disallow()
        self.disconnect_clients()
        self.disconnect()