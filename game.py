import pygame 
from pygame.locals import *
from pygame.key import *
from board import Board
from menu import Menu

class game():
    def __init__(self, mouse_visible=True, fps=60, title="Game"):
        self.init_pygame_modules(mouse_visible, title)
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.menus = {}
        self.boards = {}
        self.showing_menu = None
        self.showing_board = None

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
        pygame.display.set_caption(gameTitle)

    def start(self):
        loop = True
        while loop:
            self.clock.tick(self.fps)
            self.draw()
            if pygame.mouse.get_rel() != (0,0): #If there is mouse movement
                loop = self.event_handler(pygame.event.get(), pygame.key.get_pressed(), mouse_movement=True, mouse_pos=pygame.mouse.get_pos())
            else:
                loop = self.event_handler(pygame.event.get(), pygame.key.get_pressed())





game = game()
game.start