import pygame 
from pygame.locals import *
from pygame.key import *
from board import Board
from menu import Menu

class Setting:
    def __init__(self, UI_Element=None):
        self.graphics = UI_Element #Not really an ui element, a subclass of this one

class Button_setting(Setting):
    def __init__(self, UI_Element=None, set_of_values=[]):
        super().__init__(UI_Element)
        self.values = set_of_values
        self.index = 0

        #For the sake of writing short code
    def get_value(self):
        return self.values[self.index]

    def hitbox_action(self, mouse_buttons, mouse_pos):
        if mouse_buttons[1]: #This is a tuple, the first one is the left button. Right button was clicked
            self.dec_index()
        else: #left or center button were pressed
            self.inc_index()

    def inc_index(self):
        self.index += 1
        if self.index >= len(self.values):
            self.index = 0

    def dec_index(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.values)-1

class Slider_setting(Setting):
    def __init__(self, UI_Element=None, value=1):
        super().__init__(UI_Element)
        self.value = value

    def get_value(self):
        return self.value

    def hitbox_action(self, mouse_buttons, mouse_pos):
        pass
        #TODO check slider and values of the mouse and shit

class game():
    def __init__(self, mouse_visible=True, fps=60, title="Game", ):
        self.init_pygame_modules(mouse_visible, title)
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.menus = {}
        self.boards = {}
        self.showing_menu = None
        
        self.showing_board = None

        self.settings=[]

        self.desk = 0 #The id matches with the menu or the board, whatever is up to drawing
        self.turn = -1

        self.players=[]
    
    def add_menu(self, id_menu, menu):
        self.menus[id_menu] = menu
        self.showing_menu = menu

    def add_board(self, id_board, board):
        self.boards[id_board] = board
        self.showing_board = board

    def init_pygame_modules(self, mouse_visible, title):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.mouse.set_visible(mouse_visible)
        pygame.display.set_caption(title)

    def draw(self):
        if self.desk is 0:
            self.showing_menu.draw()
        elif self.desk is 1:
            self.showing_board.draw()

    def event_handler(self, events, keys_pressed, mouse_movement=False, mouse_pos=(0, 0)):
        if self.desk is 0:
            self.showing_menu.event_handler(events, keys_pressed, mouse_movement=mouse_movement, mouse_pos=mouse_pos)
        elif self.desk is 1:
            self.showing_menu.event_handler(events, keys_pressed, mouse_movement=mouse_movement, mouse_pos=mouse_pos)
            
    def start(self):
        loop = True
        while loop:
            self.clock.tick(self.fps)
            self.draw()
            if pygame.mouse.get_rel() != (0,0): #If there is mouse movement
                loop = self.event_handler(pygame.event.get(), pygame.key.get_pressed(), mouse_movement=True, mouse_pos=pygame.mouse.get_pos())
            else:
                loop = self.event_handler(pygame.event.get(), pygame.key.get_pressed())

#List of (ids, text)
if __name__ == "__main__":
    resolutions = Setting(options=[(800, 600), (1024, 768), (1280, 720), (1366, 768), (160, 120), (320, 240), (640, 480)])
    number_lvls = Setting(options=[1, 2, 3, 4, 5, 6])

    options=[("start_game", "Start game"), ("resolution", "Resolution"), ("settings", "Settings"), ("options", "Options")]
    settings={"resolution" : resolutions}

    menu = Menu("main_menu", options, settings, background_path='background.jpg', logo_path="logo.jpg")
    game = game()
    game.start()



