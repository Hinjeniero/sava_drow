from obj.board import Board
from obj.utilities.decorators import run_async
from settings import NETWORK
#from external.Mastermind import MastermindServerTCP, MastermindClientTCP
#from external.Mastermind._mm_errors import *   #This one doesnt catch the exception for some fuckin reasoni
from external.Mastermind import *   #I dont like this one a bit, since it has to import everything
from obj.board_server import Server
import threading, traceback

class NetworkBoard(Board):
    def __init__(self, id_, event_id, end_event_id, resolution, host=False, server=None, **params):
        if host:
            super().__init__(id_, event_id, end_event_id, resolution, **params)
        else:
            super().__init__(id_, event_id, end_event_id, empty=True, **params) #To generate the environment later
        self.client = None
        self.server = server
        self.my_player = None
        self.waiting_for_event = False
        self.queue = [] #This is the queue of received actions
        NetworkBoard.generate(self, host)

    @staticmethod
    def generate(self, host, **params):
        self.client = MastermindClientTCP(NETWORK.CLIENT_TIMEOUT_CONNECT, NETWORK.CLIENT_TIMEOUT_RECEIVE)
        try:
            if host:
                print("IM THE HOST YES")
                self.server.start(NETWORK.SERVER_IP, NETWORK.SERVER_PORT)
                self.client.connect(NETWORK.CLIENT_LOCAL_IP, NETWORK.SERVER_PORT)
            else:
                print("Im a normal client")
                #self.client.connect(NETWORK.CLIENT_IP, NETWORK.SERVER_PORT)
                self.client.connect(NETWORK.CLIENT_LOCAL_IP, NETWORK.SERVER_PORT)   #Testing in local machine
            print("Client connected!")  #If you are not the host
            self.send_handshake(host)
        except MastermindError: #If there was an error connecting
            raise Exception("MASTERMINDERROR BRO")

    @run_async
    def receive_worker(self):
        while True:
            try:
                data = self.client.receive(True)
                self.response_handler(data)
            except MastermindErrorClient:   #Timeout!
                continue
            except Exception:
                break
    
    def response_handler(self, response):
        print("YESSE")

    def get_board_params(self):
        """Chisels down the entire parameters to get just the one that all the clients must share."""
        params = {'inter_path_frequency'  : self.params['inter_path_frequency'],
                'circles_per_lvl'       : self.params['circles_per_lvl'],
                'max_levels'            : self.params['max_levels'] ,
                'center_cell'           : self.params['center_cell'],
                'quadrants_overlap' : self.params['quadrants_overlap']}
        return params

    def get_char_params(self):
        """Chisels down the entire params to get the one that cliens must share."""
        return True

    def send_data(self, sent_data, compression=None):
        """Blocking call to the server. (if run_async as decorator can be not blocking, just a subthread blocked)"""
        self.client.send(sent_data, compression=compression)
        reply = self.client.receive(True)
        return reply

    def send_data_async(self, sent_data, compression=None):
        """Blocking call to the server. (if run_async as decorator can be not blocking, just a subthread blocked)"""
        self.client.send(sent_data, compression=compression)

    def request_data(self, command, compression=None):
        self.client.send({command:True}, compression=compression)
        reply = self.client.receive(True)
        return reply

    def request_data_async(self, command, compression=None):
        self.client.send({command:False}, compression=compression)

    def ALL_PLAYERS_LOADED(self):
        super().ALL_PLAYERS_LOADED()
        if (self.loaded_players is self.total_players):
            players = self.send_data({'players': True}) #Send the uuid, order, and name.    #DO THIS ASYNC
            reply = self.send_data({'positions_and_shit': True})

    def send_handshake(self, host):
        if host:
            reply = self.send_data({'host': True})
            self.send_data_async({'params': self.get_board_params()})
        else:
            params = self.request_data('params')
            self.params.update(params)
            self.generate_environment()
            players_ammount = self.request_data({'players': True}) #TO get the number of players
            for _ in range(0, players_ammount['players']):
                print("ADDING PLAYER")  #CREATE WITH EMPTY = TRUE
            reply = self.request_data({'positions': True})
        reply = self.send_data({'ready': True})
        print("FINAL REPLY, WE ARE IN BUSINESS ")

    #This to be a queue that is checked once in every frame? Or a thread to be checked and results saved in a queue when ready?
    def send_update(self, data):
        reply = self.client.send_data({'update': True})
        print(str(reply))
    
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
