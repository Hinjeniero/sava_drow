import threading
import traceback
import time
import uuid
from obj.board import Board
from obj.utilities.decorators import run_async
from obj.utilities.logger import Logger as LOG
from settings import NETWORK
#from external.Mastermind import MastermindServerTCP, MastermindClientTCP
#from external.Mastermind._mm_errors import *   #This one doesnt catch the exception for some fuckin reasoni
from external.Mastermind import *   #I dont like this one a bit, since it has to import everything
from obj.board_server import Server

class NetworkBoard(Board):
    def __init__(self, id_, event_id, end_event_id, resolution, host=False, server=None, **params):
        if host:
            super().__init__(id_, event_id, end_event_id, resolution, **params)
        else:
            super().__init__(id_, event_id, end_event_id, resolution, empty=True, **params) #To generate the environment later
        self.uuid = uuid.uuid1().int    #Using this if crashing would led to more conns than players
        self.ip = None
        self.port = None
        self.client = None
        self.client_lock = threading.Lock()
        self.server = server
        self.my_player = None
        self.waiting_for_event = False
        self.queue = [] #This is the queue of received actions
        self.conditions = {}    #Used if client and not host.
        self.reconnect = True
        NetworkBoard.generate(self, host)

    @staticmethod
    def generate(self, host, **params):
        self.port = NETWORK.SERVER_PORT
        self.client = MastermindClientTCP(NETWORK.CLIENT_TIMEOUT_CONNECT, NETWORK.CLIENT_TIMEOUT_RECEIVE)
        try:
            if host:
                print("IM THE HOST YES")
                self.server.start(NETWORK.SERVER_IP, NETWORK.SERVER_PORT)
                self.ip = NETWORK.CLIENT_LOCAL_IP
            else:
                print("Im a normal client")
                self.loaded=False
                self.conditions['board_done'] = threading.Condition()
                self.conditions['players_ammount_done'] = threading.Condition()
                self.conditions['players_data_done'] = threading.Condition()
                '''for cond in self.conditions.values():
                    cond.acquire()'''
                self.ip = NETWORK.CLIENT_LOCAL_IP   #Testing rn
                #self.ip = NETWORK.CLIENT_IP
            self.connect()
            self.keep_alive() #Creating thread
            self.send_handshake(host)
        except MastermindError: #If there was an error connecting
            LOG.log('ERROR', traceback.format_exc())

    def send_handshake(self, host):
        self.send_data({'host': host, 'id': self.uuid})
        if host:
            self.send_data_async({'params': self.get_board_params()})
        else:
            self.request_data_async('params')
            self.request_data_async('players')          #To get the number of players
            self.request_data_async('players_data')     #To get the data of the players
            self.request_data_async('character_data')  #To get the data of the characters

    def connect(self):
        if self.ip and self.port:
            self.client_lock.acquire()
            self.client.disconnect()
            self.client.connect(self.ip, self.port)
            self.client_lock.release()
            print("Client connected!")

    ####A THREAD
    @run_async
    def keep_alive(self, compression=None): #Also works as a keep-alive-connection. How to kill this thread later on...
        while True:
            try:
                self.request_data_async('keep-alive')   #Response will be handled in the receiving thread
                time.sleep(1)
            except MastermindErrorClient:   #If disconnectes from server
                if self.reconnect:
                    self.connect()
                    self.send_data({'id': self.uuid}, compression=compression)
                else:
                    break
    ####ANOTHER THREAD
    @run_async
    def receive_worker(self):
        while True:
            try:
                data = self.client.receive(True)
                self.response_handler(data)
            except MastermindErrorClient:   #Timeout/disconnection
                if self.reconnect:
                    self.connect()
                else:
                    break
    
    def response_handler(self, response):
        if not self.server: #If im not host
            if 'params' in response:
                self.params.update(self.params['params'])
                self.generate_mapping()
                self.generate_environment()
            elif 'players' in response:
                self.conditions['board_done'].wait_for(self.generated)
                for i in range (0, 4, 4//response['players']):
                    self.create_player('null', i, (200, 200), empty=True)  #The name will be overwritten later on
            elif 'players_data' in response:
                self.conditions['board_done'].wait_for(self.generated)
                self.conditions['players_ammount_done'].wait_for(self.started)
                for player in self.players: #Once per player
                    if response['players_data']['data']['order'] is player.order:
                        player.uuid = response['players_data']['uuid']
                        player.name = response['players_data']['name']
                        break
                self.loaded=True
            elif 'character_data' in response:
                self.conditions['board_done'].wait_for(self.generated)
                self.conditions['players_ammount_done'].wait_for(self.started)
                self.conditions['players_data_done'].wait_for(self.loaded)
                print("CHARS ARE HERE")
                print(response) #THIS SHOULD BE CHARACTERS
                #SET CHARACTERS.
        #HANDLING OF NORMAL RESPONSES DURING THE GAME
    #####END OF THREAD


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
        if self.started:
            if self.server:
                self.send_player_and_chars_data()
                return
            self.request_data_async('chars_data') #To get the chars data AFTER we have created the empty player

    def send_player_and_chars_data(self):
        players = []
        for player in self.players:
            players.append(player.())
        self.send_data_async({'players_data': players})
        characters = []
        for cell in self.cells:
            if cell.has_char():
                characters.append(cell.get_char().(cell.get_real_index()))
        self.send_data_async({'characters_data': characters})











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

    def destroy(self):
        self.reconnect = False
        self.client.disconnect()
        if self.server:
            self.server.accepting_disallow()
            self.server.disconnect_clients()
            self.server.disconnect()