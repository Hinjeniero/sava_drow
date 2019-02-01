from obj.board import Board
from obj.utilities.decorators import run_async
from settings import NETWORK
from external.Mastermind import MastermindServerTCP, MastermindClientTCP
from external.Mastermind._mm_errors import *
import threading

class Server(MastermindServerTCP):
    def __init__(self):
        super().__init__(self, NETWORK.SERVER_REFRESH_TIME, NETWORK.SERVER_CONNECTION_REFRESH, NETWORK.SERVER_CONNECTION_TIMEOUT)
        self.lock = threading.Lock()

    @run_async
    def start(self, ip, port):
        self.connect(ip, port) #This connect is way more like a bind to the socket.
        try:
            self.accepting_allow_wait_forever()
        except:
            #Only way to break is with an exception
            pass
        self.accepting_disallow()
        self.disconnect_clients()
        self.disconnect()

class NetworkBoard(Board):
    def __init__(self, id_, event_id, end_event_id, resolution, *players, **params):
        super().__init__(id_, event_id, end_event_id, resolution, *players, **params)
        self.client = None
        self.server = None
        self.actions_queue = []
        NetworkBoard.generate(self)

    @staticmethod
    def generate(self, server): #Check if im the fuckins server or not
        client = MastermindClientTCP(NETWORK.CLIENT_TIMEOUT_CONNECT, NETWORK.CLIENT_TIMEOUT_RECEIVE)
        try:
            print("Client connecting on \""+NETWORK.SERVER_IP+"\", port "+str(NETWORK.SERVER_PORT)+" . . .")
            client.connect(NETWORK.CLIENT_IP, NETWORK.SERVER_PORT)
        except MastermindError:
            print("No server found; starting server!")
            server = Server()
            server.start(NETWORK.SERVER_IP, NETWORK.SERVER_PORT)

            print("Client connecting on \""+NETWORK.CLIENT_LOCAL_IP+"\", port "+str(NETWORK.SERVER_PORT)+" . . .")
            client.connect(NETWORK.CLIENT_LOCAL_IP, NETWORK.SERVER_PORT)
        print("Client connected!")
        self.send_handshake()

    def send_handshake(self):
        self.client.send(["update"], None)
        reply = None
        while reply == None:
            reply = client.receive(False)
        print(reply)

    def send_data(self, data):
        pass

    #This to be a queue that is checked once in every frame? Or a thread to be checked and results saved in a queue when ready?
    def receive_data(self, data):
        pass
    
    def mouse_handler(self, event, mouse_movement, mouse_position):
        super().mouse_handler(event, mouse_movement, mouse_position)
        if mouse_movement:
            pass
            #Send to the other computer the drag char movement, so it can show it in screen.
            #Also, DO NOT allow to drop your chars if its not your turn

    def pickup_character(self):
        if 'its my turn':
            super().pickup_character()
        else:
            'Do whatever you want m8, you can move the char around anyway'

    def drop_character(self):
        if 'its my turn':
            super().pickup_character()

    def update_cells(self, *cells):
        #This changes depending on who you are (The map itself).
        super().update_cells(*cells)
        #Send to other parties the info

    def next_char_turn(self, char):
        super().next_char_turn(char)

    def next_player_turn(self):
        #Check how to work this so we can have you stay quiet but move the chars whle
        self.current_player.turn += 1
        while True:
            self.player_index += 1
            if self.player_index >= len(self.players):
                self.player_index = 0
                self.turn += 1
            if self.players[self.player_index].turn is self.turn:
                self.current_player.pause_characters()
                self.current_player = self.players[self.player_index]
                self.current_player.unpause_characters()
                self.update_map()
                break
