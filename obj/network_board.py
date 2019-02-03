from obj.board import Board
from obj.utilities.decorators import run_async
from settings import NETWORK
#from external.Mastermind import MastermindServerTCP, MastermindClientTCP
#from external.Mastermind._mm_errors import *   #This one doesnt catch the exception for some fuckin reasoni
from external.Mastermind import *   #I dont like this one a bit, since it has to import everything
from obj.board_server import Server
import threading, traceback

class NetworkBoard(Board):
    def __init__(self, id_, event_id, end_event_id, resolution, players_ammount, host=False, server=None, **params):
        if host:
            super().__init__(id_, event_id, end_event_id, resolution, **params) #To use this when shit is gud
        self.client = None
        self.server = server
        self.my_player = None
        self.queue = [] #This is the queue of received actions
        NetworkBoard.generate(self, host)

    @staticmethod
    def generate(self, host, **params):
        self.client = MastermindClientTCP(NETWORK.CLIENT_TIMEOUT_CONNECT, NETWORK.CLIENT_TIMEOUT_RECEIVE)
        try:
            if host:
                print("IM HOST YES")
                self.server.start(NETWORK.SERVER_IP, NETWORK.SERVER_PORT)
                self.client.connect(NETWORK.CLIENT_LOCAL_IP, NETWORK.SERVER_PORT)
            else:
                print("Im normal client")
                self.client.connect(NETWORK.CLIENT_IP, NETWORK.SERVER_PORT)
            print("Client connected!")  #If you are not the host
            self.send_handshake(host, **params)
        except MastermindError: #If there was an error connecting
            raise Exception("MASTERMINDERROR BRO")

    def get_board_params(self):
        """Chisels down the entire parameters to get just the one that all the clients must share."""
        '''inter_path_frequency'  : 2,
        'circles_per_lvl'       : 16,
        'max_levels'            : 4,
        'center_cell'           : False,
        ['quadrants_overlap'] = True
        '''
        return True

    def get_char_params(self):
        """Chisels down the entire params to get the one that cliens must share."""
        return True

    def send_data(self, sent_data, compression=None):
        """Blocking call to the server. (if run_async as decorator can be not blocking, just a subthread blocked)"""
        self.client.send(sent_data, compression=compression)
        reply = self.client.receive(True)
        return reply

    def send_handshake(self, host):
        if host:
            reply = self.send_data({'host': True})
            print("Sending host "+reply)
            #Create board
            reply = self.send_data({'params': self.get_board_params()})    #Send those 4 params
            players = self.send_data({'players': True})
            print("How many players: "+reply)
            for _ in range(0, players):
                pass #Create player
            reply = self.send_data({'positions_and_shit': True})
            print(reply)
        else:
            reply = self.send_data({'params': True})
            #super().__init__(id_, event_id, end_event_id, resolution, **params)
            reply = self.send_data({'positions': True})
        reply = self.client.send_data({'ready': True})
        print("FINAL REPLY, WE ARE IN BUSINESS "+str())

    #This to be a queue that is checked once in every frame? Or a thread to be checked and results saved in a queue when ready?
    def send_update(self, data):
        reply = self.client.send_data({'update': True})
        print(reply)
    
    #####FOLLOW HERE; GOING TO DINE NOW
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
