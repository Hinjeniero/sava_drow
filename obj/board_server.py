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
        self.total_chars = None
        self.players_ready = 0
        self.current_map = None

        self.hold_lock = threading.Lock()
        self.on_hold_resp = []
        self.clients = Dictionary()   #Connections objects (Includes host)
        self.waiting = []   #Connections waiting for an event to occur. This acts as a barrier
        self.data = Dictionary(exceptions=True)
        self.players_data = Dictionary(exceptions=True)
        self.chars_data = Dictionary(exceptions=True)

    def set_chars(self, number_of_chars):
        self.total_chars = number_of_chars

    def add_data(self, key, data):
        self.data.add_item(key, data)

    def add_client(self, id_, conn_client):
        self.clients.add_item(id_, conn_client)

    def add_player(self, player):
        self.players_data.add_item(player["uuid"], player)
        """print("ADDING")
        print(str(self.players_data.dict))"""

    def add_char(self, character):
        self.chars_data.add_item(character["uuid"], character)
        """print("ADDING CHAR")
        print("Current chars: "+str(len(self.chars_data.keys())))"""

    def get_data(self, key):
        response = {}
        try:
            response[key] = self.data.get_item(key)
        except KeyError:    #This will never raise, since data is
            response = {"success": False, "error": "The data with the key "+key+" was not found in the server"}
        return response

    def send_updates(self):
        while len(self.queue) > 0:
            command = self.get_from_queue()
            for client in self.clients.values(): #Connections
                self.callback_client_handle(client, command)

    def broadcast_data(self, list_of_conns, data):
        for conn in list_of_conns:
            self.callback_client_send(conn, data)

    @run_async
    def petition_worker(self):
        self.hold_lock.acquire()
        petition = self.on_hold_resp.pop(0)
        self.hold_lock.release()
        self.callback_client_handle(*petition)  #This to unpack the tuple of conn,data

    def callback_client_handle(self, connection_object, data):
        reply = None
        try:
            if "host" in data:   #This is a handshake
                if data["host"]:
                    if not self.host:
                        self.host = connection_object
                    else:
                        reply = {"success": False, "error": "There is already an host."}
                self.add_client(data["id"], connection_object)
            elif "params" in data:
                print("A CLIENT REQUESTED PARAMS")
                if connection_object is self.host:
                    self.add_data("params", data["params"])
                else:
                    reply = self.get_data("params")
            elif "start" in data or "ready" in data:  #IN THIS ONE WAIT FOR ALL OF THEM TO BE ONLINE
                self.players_ready += 1
                self.waiting.append(connection_object)
                if self.players_ready >= self.total_players:
                    self.broadcast_data(self.waiting, {"unlock": True})
            elif "players" in data: #At start
                reply = {"players": self.total_players}
            elif "players_data" in data:
                if connection_object == self.host:
                    for player in data["players_data"]:
                        self.add_player(player)
                else:
                    print("A CLIENT REQUESTED PLAYERS DATA")
                    if len(self.players_data.keys()) < self.total_players:
                        raise KeyError
                    reply = {"players_data": self.players_data.values_list()}
            elif "characters_data" in data:
                if connection_object == self.host:
                    for character in data["characters_data"]:
                        self.add_char(character)
                else:
                    print("A CLIENT REQUESTED CHARS DATA")
                    if len(self.chars_data.keys()) < self.total_chars:
                        raise KeyError
                    reply = {"characters_data": self.chars_data.values_list()}
            elif "update" in data:
                reply = "UPDATE" #reply = changes, Sends the info of the board to the whatever client requested it. (If there is new actions)
            elif "move_char" in data:
                reply = "MOVE" #Save the info of the char.
            elif "menu" in data:
                pass #Changing screens, sohuld check what to do
        except KeyError:    #Can"t attend this petition right now.
            self.hold_lock.acquire()
            print("HOLDING "+str(data))
            self.on_hold_resp.append((connection_object, data))
            self.hold_lock.release()
        if reply:
            print("SERVER REPLIED WITH "+str(reply))
        if not reply:   #If it wanst a request but a push of data
            reply = {"success": True}
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