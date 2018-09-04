import pygame
import os
from pygame.locals import *
from pygame.key import *
from board import Board
from menu import Menu
from setting import Setting


class game():
    __event_id_counter = 1
    game_folder = os.path.dirname(__file__)
    img_folder = os.path.join(game_folder, 'img')
    sounds_folder = os.path.join(game_folder, 'sounds')

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

    def event_handler(self, events):
        all_keys =          pygame.key.get_pressed()        #Get all the pressed keyboard keys
        all_mouse_buttons = pygame.mouse.get_pressed()      #Get all the pressed mouse buttons
        mouse_pos=pygame.mouse.get_pos()                    #Get the current mouse position
        mouse_mvnt = (pygame.mouse.get_rel() != (0,0))      #True if get_rel returns non zero vaalues

        for event in events:
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                else:
                    if self.desk is 0:
                        self.showing_menu.event_handler(event, all_keys, all_mouse_buttons, mouse_movement=mouse_mvnt, mouse_pos=mouse_pos)
                    elif self.desk is 1:
                        self.showing_menu.event_handler(event, all_keys, all_mouse_buttons, mouse_movement=mouse_mvnt, mouse_pos=mouse_pos)
            
    def user_event_handler(self, event):
        pass

    def start(self):
        loop = True
        while loop:
            self.clock.tick(self.fps)
            self.draw()
            loop = self.event_handler(pygame.event.get())

#List of (ids, text)
if __name__ == "__main__":
    resolutions = Setting(options=[(800, 600), (1024, 768), (1280, 720), (1366, 768), (160, 120), (320, 240), (640, 480)])
    number_lvls = Setting(options=[1, 2, 3, 4, 5, 6])

    options=[("start_game", "Start game"), ("resolution", "Resolution"), ("settings", "Settings"), ("options", "Options")]
    settings={"resolution" : resolutions}

    menu = Menu("main_menu", options, settings, background_path='background.jpg', logo_path="logo.jpg")
    game = game()
    game.start()



