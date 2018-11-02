import pygame, os
from pygame.locals import *
from pygame.key import *
from screen import Screen
from board import Board
from menu import Menu
from ui_element import *
from colors import *
from paths import *
from players import *
from exceptions import *
CHANGES_WERE_MADE = False

def init_pygame_modules (mouse_visible, resolution, title):
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.mouse.set_visible(mouse_visible)
    pygame.display.set_caption(title)
    pygame.display.set_mode(resolution)

class Game(object):
    def __init__(self, *screens, resolution=(1280, 720), mouse_visible=True, title="Game"):
        self.pygame_params      = self.generate_pygame_vars(resolution=resolution)
        self.screens            = []
        self.players            = [] 
        if len(screens) > 0:    self.add_elements(*screens) 
        else:                   raise NoScreensException("A game needs at least a screen to work")
        
        #Helpful but unnecesary attributes, only for the sake of clean code
        self.__current_screen   = self.screens[0]

    def add_elements(self, *elements):
        for element in elements:
            if isinstance(element, Screen): self.screens.append(element)
            else:                           raise InvalidGameElementException("Can't add an element of type "+str(type(element)))

    def generate_pygame_vars(self, resolution=(1280, 720)):
        params                  = {}
        params['fps']           = 60
        params['clock']         = pygame.time.Clock()
        params['clock'].tick(params['fps'])
        params['display']       = pygame.display.get_surface()
        if resolution is not params['display'].get_size(): 
            params['display']   = pygame.display.set_mode(resolution)
        return params

    def change_pygame_var(self, command, value):
        global CHANGES_WERE_MADE
        CHANGES_WERE_MADE   = True
        cmd                 = command.lower()
        if len(cmd) <= 0:           raise EmptyCommandException("Received an empty command string")
        elif 'fps' in cmd:          self.pygame_params['clock'].tick(value)
        elif 'resolution' in cmd:   self.__set_resolution(value)
        elif 'music' in cmd:        pass
        elif 'sound' in cmd:        pass
    
    def __set_resolution(self, resolution):
        self.pygame_params['display'] = pygame.display.set_mode(resolution)
        for screen in self.screens:     screen.update_resolution(resolution)

    def event_handler(self, events):
        all_keys            = pygame.key.get_pressed()          #Get all the pressed keyboard keys
        all_mouse_buttons   = pygame.mouse.get_pressed()        #Get all the pressed mouse buttons
        mouse_pos           = pygame.mouse.get_pos()            #Get the current mouse position
        mouse_mvnt          = (pygame.mouse.get_rel() != (0,0)) #True if get_rel returns non zero vaalues

        for event in events:
            self.__current_screen.event_handler(event, all_keys, all_mouse_buttons, mouse_movement=mouse_mvnt, mouse_pos=mouse_pos)
            if event.type == pygame.QUIT:               return False
            elif event.type == pygame.KEYDOWN   \
                and event.key == pygame.K_ESCAPE:       self.esc_handler()
            #elif event.type == pygame.KEYDOWN:          self.__keyboard_handler(event, keys_pressed)
            elif event.type >= pygame.USEREVENT:        self.user_command_handler(event.type, event.command, event.value)
        return True

    def esc_handler(self):
        id_screen = self.__current_screen.id.lower()
        if 'main' in id_screen and 'menu' in id_screen: self.__esc_main_menu()
        elif 'menu' in id_screen:                       self.__esc_menu()
        elif 'board' in id_screen:                      self.__esc_board()

    def __esc_board(self):
        self.change_screen("main", "menu")

    def __esc_menu(self):
        if CHANGES_WERE_MADE:   self.change_screen("main", "menu")
        else:                   self.change_screen("main", "menu")

    def __esc_main_menu(self):
        if self.__current_screen.have_dialog() and not self.__current_screen.dialog_is_active():        self.__current_screen.show_dialog()   
        elif self.__current_screen.have_dialog() and self.__current_screen.dialog_is_active():  self.__current_screen.hide_dialog()  

    def change_screen(self, *keywords):
        count = 0
        for i in range(0, len(self.screens)):
            matches = len([0 for j in keywords if j in self.screens[i].id])
            if matches > count:   
                self.__current_screen = self.screens[i]
                count = matches
        if count is 0:  raise ScreenNotFoundException("A screen with those keywords wasn't found")
 
    def user_command_handler(self, eventid, command, value):
        ''' Ou shit the user command handler, good luck m8
        USEREVENT when MENUS:           Change in settings
        UESREVENT+1 when MENUS:         Change of screen
        USEREVENT+2 when BOARD:         Action in them
        USEREVENT+3 when NOTIFICATIONS: popups and shit
        '''
        if eventid < pygame.USEREVENT:      return False
        elif eventid is pygame.USEREVENT:   self.change_pygame_var(command, value)
        elif eventid is pygame.USEREVENT+1: self.change_screen(*command.split('_'))   #TODO change_screen methood is not prepared to filter bad keywords
        elif eventid is pygame.USEREVENT+2: pass
        elif eventid is pygame.USEREVENT+3: pass
        elif eventid is pygame.USEREVENT+4: pass
            
    def start(self):
        loop = True
        print("GAME STARTING")
        while loop:
            self.__current_screen.draw(self.pygame_params['display'], clock=self.pygame_params['clock'])
            loop = self.event_handler(pygame.event.get())

#List of (ids, text)
if __name__ == "__main__":
    resolutions = ((640, 480), (800, 600), (1024, 768), (1280, 720), (1366, 768))
    res = resolutions[3]
    init_pygame_modules(True, res, 'Sava Drow')
    #Create elements, main menu buttons
    buttonStart         = UIElement.factory("start_game_go_main_board", pygame.USEREVENT+1, (10, 100), (800, 100), res, None, text="Start game", start_gradient = GREEN, end_gradient=BLACK)
    buttonRes           = UIElement.factory("change_resolution_screen_display", pygame.USEREVENT, (10, 300), (800, 100), res, resolutions, text="Resolution", text_centering=1)
    buttonSoundMenu     = UIElement.factory("go_menu_sound_music", pygame.USEREVENT+1, (10, 500), (800, 100), res, None, text="Music menu")
    #Exit dialog and its buttons
    acceptButton        = UIElement.factory("accept_notification", pygame.USEREVENT+2, (0, 0), (200, 50), (600, 400), None, text="ACCEPT")
    cancelButton        = UIElement.factory("accept_notification", pygame.USEREVENT+2, (0, 0), (200, 50), (600, 400), None, text="CANCEL")
    exitDialog          = UIElement.factory("exit_main_menu_notification", pygame.USEREVENT+2, (0, 0), (600, 400), res, None, acceptButton, cancelButton, text="Exit this shit?")

    #Sliders of the music and sound menu
    sliderMenuMusic     = UIElement.factory("change_menu_music_volume", pygame.USEREVENT, (10, 110), (800, 100), res, (0.75), text="Menu music volume", slider_type=0,\
                        start_gradient = RED, end_gradient=BLACK, slider_start_color = RED, slider_end_color = WHITE)
    sliderMenuSounds    = UIElement.factory("change_menu_sound_volume", pygame.USEREVENT, (10, 310), (800, 100), res, (0.75), text="Menu sounds volume", slider_type=0)
    sliderBoardMusic    = UIElement.factory("change_board_music_volume", pygame.USEREVENT, (10, 510), (800, 100), res, (0.75), text="Board music volume")
    sliderBoardSounds   = UIElement.factory("change_board_sound_volume", pygame.USEREVENT, (10, 710), (800, 100), res, (0.75), text="Board sounds volume")

    #Create Menu and board
    main_menu = Menu("main_menu", pygame.USEREVENT, res, (True, 0), buttonStart, buttonRes, buttonSoundMenu, dialog=exitDialog, background_path = IMG_FOLDER+'\\background.jpg')
    sound_menu = Menu("menu_volume_sound_music", pygame.USEREVENT+1, res, (True, 0), sliderMenuMusic, sliderMenuSounds, sliderBoardMusic, sliderBoardSounds)

    player_1    = Player("Zippotudo", {"pawn":1, "warrior":1, "wizard":1, "priestess":0}, (100, 100))

    main_board = Board("main_board", pygame.USEREVENT+7, res, background_path = IMG_FOLDER+'\\board_2.jpg')
    main_board.add_players(player_1)
    #TODO EACH PLAYERS GETS HIS INFOBOARD
    game = Game(main_menu, sound_menu, main_board, title="Sava Drow", resolution=res)
    game.start()

