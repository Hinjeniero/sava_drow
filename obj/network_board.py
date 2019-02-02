from obj.board import Board
from obj.utilities.decorators import run_async
from settings import NETWORK
#from external.Mastermind import MastermindServerTCP, MastermindClientTCP
#from external.Mastermind._mm_errors import *   #This one doesnt catch the exception for some fuckin reasoni
from external.Mastermind import *   #I dont like this one a bit, since it has to import everything
import threading, traceback

class NetworkBoard(Board):
    def __init__(self, id_, event_id, end_event_id, resolution, players_ammount, *players, **params):
        #super().__init__(id_, event_id, end_event_id, resolution, *players, **params) #To use this when shit is gud
        self.client = None
        self.server = None
        self.my_player = None
        self.queue = [] #This is the queue of received actions
        NetworkBoard.generate(self)

    @staticmethod
    def generate(self): #TODO CHANGE THIS TO SEPARATE TOTALLY CLIENT AND SERVER
        self.client = MastermindClientTCP(NETWORK.CLIENT_TIMEOUT_CONNECT, NETWORK.CLIENT_TIMEOUT_RECEIVE)
        try:
            print("Client connecting on \""+NETWORK.CLIENT_IP+"\", port "+str(NETWORK.SERVER_PORT)+" . . .")
            self.client.connect(NETWORK.CLIENT_IP, NETWORK.SERVER_PORT)
            self.send_handshake()
            #TODO Use received data to generate shit.
        except MastermindError: #If you ARE the host
            print("No server found; starting server!")
            self.server = Server()
            self.server.start(NETWORK.SERVER_IP, NETWORK.SERVER_PORT)
            print("My client connecting locally on \""+NETWORK.CLIENT_LOCAL_IP+"\", port "+str(NETWORK.SERVER_PORT)+" . . .")
            self.client.connect(NETWORK.CLIENT_LOCAL_IP, NETWORK.SERVER_PORT)
            super().__init__(id_, event_id, end_event_id, resolution, *players, **params)
        print("Client connected!")  #If you are not the host

    def send_handshake(self):
        self.client.send(['update'], None)
        reply = None
        print("WAITING FDOR HANDSHAKE")
        reply = self.client.receive(True)
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
            super().drop_character()

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
