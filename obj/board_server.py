import threading
from obj.utilities.decorators import run_async
from settings import NETWORK
from external.Mastermind import *

class Server(MastermindServerTCP):
    def __init__(self, number_of_players):
        MastermindServerTCP.__init__(self, NETWORK.SERVER_REFRESH_TIME, NETWORK.SERVER_CONNECTION_REFRESH, NETWORK.SERVER_CONNECTION_TIMEOUT)
        self.host = None    #COnnection object. This is another client, but its the host. I dunno if this will be useful yet.
        self.clients = []   #Connections objects (Includes host)
        self.total_players = number_of_players
        self.players_ready = 0
        self.current_map = None
        self.queue = []
        self.lock = threading.Lock()

    def add_to_queue(self, command):
        self.lock.acquire()
        self.queue.append(command)
        self.lock.release()

    def get_from_queue(self):
        self.lock.acquire()
        element = self.queue[0]
        del self.queue[0]
        self.lock.release()
        return element
        
    def send_updates(self):
        while len(self.queue) > 0:
            command = self.get_from_queue()
            for client in self.clients: #Connections
                self.callback_client_handle(client, command)

    def send_start_info(self):
        for conn in self.clients:
            self.callback_client_handle(conn, 'player')

    def callback_client_handle(self, connection_object, data):
        reply = None
        if 'host' in data:
            if not self.host:
                self.host = connection_object
            else:
                reply = 'There is already a host. No hacking pls.'
        if 'params' in data and not self.board_params:
            if connection_object is self.host:
                self.add_to_queue(data)
            else:
                reply = True #Returns the params of the board
        if 'start' in data or 'ready' in data:  #IN THIS ONE WAIT FOR ALL OF THEM TO BE ONLINE
            self.players_ready += 1
            if self.players_ready < self.total_players:
                return  #So the clients stay blocked until we reply with an ACK
        if 'player' in data: #At start
            if connection_object is self.host:
                pass #Saves the player info
            else:
                pass #Saves the player info(name and shit), and replies the final board. reply=board
        if 'update' in data:
            reply = 'UPDATE' #reply = changes, Sends the info of the board to the whatever client requested it. (If there is new actions)
        if 'move_char' in data:
            reply = 'MOVE' #Save the info of the char.
        if 'menu' in data:
            pass #Changing screens, sohuld check what to do
        if not reply:   #If it wanst a request but a push of data
            reply = 'ACK'
        #print("Echo server got: \""+str(data)+"\"")
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