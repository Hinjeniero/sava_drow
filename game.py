import pygame, os, threading, sys
from pygame.locals import *
from pygame.key import *
from screen import Screen
from board import Board
from menu import Menu
from ui_element import *
from colors import *
from paths import IMG_FOLDER
from decorators import run_async
from exceptions import *
from logger import Logger as LOG

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
        LOG.log('INFO', "----Initial Pygame parameters----")
        LOG.log('INFO', "FPS: ", params['fps'])
        LOG.log('INFO', "RESOLUTION: ", params['display'].get_size())
        return params

    def change_pygame_var(self, command, value):
        LOG.log('DEBUG', "Requested change of pygame params: ", command, "->", value)
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
        LOG.log('DEBUG', "Changed resolution to ", resolution)

    def event_handler(self, events):
        all_keys            = pygame.key.get_pressed()          #Get all the pressed keyboard keys
        all_mouse_buttons   = pygame.mouse.get_pressed()        #Get all the pressed mouse buttons
        mouse_pos           = pygame.mouse.get_pos()            #Get the current mouse position
        mouse_mvnt          = (pygame.mouse.get_rel() != (0,0)) #True if get_rel returns non zero vaalues

        for event in events:
            if event.type == pygame.QUIT:               return False
            elif event.type == pygame.KEYDOWN   \
                and event.key == pygame.K_ESCAPE:       self.esc_handler()
            #elif event.type == pygame.KEYDOWN:          self.__keyboard_handler(event, keys_pressed)
            elif event.type >= pygame.USEREVENT:        self.user_command_handler(event.type, event.command, event.value)
            self.__current_screen.event_handler(event, all_keys, all_mouse_buttons, mouse_movement=mouse_mvnt, mouse_pos=mouse_pos)
        return True

    def esc_handler(self):
        LOG.log('DEBUG', "Pressed esc in ", self.__current_screen.id)
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
        LOG.log('DEBUG', "Requested change of screen to ", keywords)
        count = 0
        for i in range(0, len(self.screens)):
            matches = len([0 for j in keywords if j in self.screens[i].id])
            if matches > count:   
                self.__current_screen = self.screens[i]
                count = matches
        if count is 0:  raise ScreenNotFoundException("A screen with those keywords wasn't found")
        else:           LOG.log('DEBUG', "Changed to  ", self.__current_screen.id)
 
    def user_command_handler(self, eventid, command, value):
        ''' Ou shit the user command handler, good luck m8
        USEREVENT when MENUS:           Change in settings
        UESREVENT+1 when MENUS:         Change of screen
        USEREVENT+2 when BOARD:         Action in them
        USEREVENT+3 when NOTIFICATIONS: popups and shit
        '''
        if eventid < pygame.USEREVENT:      return False
        elif eventid is pygame.USEREVENT:   self.change_pygame_var(command, value)
        elif eventid is pygame.USEREVENT+1: self.change_screen(*command.split('_'))
        elif eventid is pygame.USEREVENT+2: pass    #Board actions
        elif eventid is pygame.USEREVENT+3: pass    #Dialog actions
        elif eventid is pygame.USEREVENT+4: pass    #Dunno, errors?

    def start(self):
        LOG.log('INFO', "GAME STARTING!")
        try:
            loop = True
            while loop:
                self.__current_screen.draw(self.pygame_params['display'], clock=self.pygame_params['clock'])
                loop = self.event_handler(pygame.event.get())
            sys.exit()
        except Exception as exc:
            LOG.exception(exc)

#List of (ids, text)
if __name__ == "__main__":
    resolutions = ((1280, 720), (1366, 768), (1600, 900), (640, 480), (800, 600), (1024, 768), (1280, 1024))
    res = resolutions[0]
    init_pygame_modules(True, res, 'Sava Drow')
    #Create elements, main menu buttons (POSITIONS AND SIZES ARE IN PERCENTAGES OF THE CANVAS_SIZE, can use absolute integers too)
    buttonStart         = UIElement.factory("start_game_go_main_board", pygame.USEREVENT+1, (0.05, 0.10), (0.90, 0.20), res, None, text="Start game", texture=IMG_FOLDER+"//button.png")
    buttonParamsMenu    = UIElement.factory("go_menu_params_config",    pygame.USEREVENT+1, (0.05, 0.40), (0.90, 0.20), res, None, text="Parameters", start_gradient = RED, end_gradient=BLACK)
    buttonSoundMenu     = UIElement.factory("go_menu_sound_music",      pygame.USEREVENT+1, (0.05, 0.70), (0.90, 0.20), res, None, text="Music menu", start_gradient = RED, end_gradient=BLACK)
    #buttons of parameters menu
    buttonRes           = UIElement.factory("change_resolution_screen_display", pygame.USEREVENT, (0.05, 0.05), (0.90, 0.10), res, resolutions, text="Resolution",          text_centering=1)
    buttonCountPlayers  = UIElement.factory("change_number_count_players",      pygame.USEREVENT, (0.05, 0.20), (0.90, 0.10), res, (2, 3, 4),   text="Number of players",   text_centering=1)
    buttonNumPawns      = UIElement.factory("change_number_count_pawns",        pygame.USEREVENT, (0.15, 0.35), (0.80, 0.10), res, (4, 8),      text="Number of pawns",     text_centering=1)
    buttonNumWarriors   = UIElement.factory("change_number_count_warriors",     pygame.USEREVENT, (0.15, 0.50), (0.80, 0.10), res, (1, 2, 4),   text="Number of warriors",  text_centering=1)
    buttonNumWizards    = UIElement.factory("change_number_count_wizards",      pygame.USEREVENT, (0.15, 0.65), (0.80, 0.10), res, (1, 2),      text="Number of wizards",   text_centering=1)
    buttonNumPriestess  = UIElement.factory("change_number_count_priestess",    pygame.USEREVENT, (0.15, 0.80), (0.80, 0.10), res, (1, 1),      text="Number of priestess", text_centering=1)
    #Exit dialog and its buttons
    dialog_resolution   = tuple(x//2 for x in res)
    dialog_position     = tuple(x//2-y//2 for x, y in zip(res, dialog_resolution))
    acceptButton        = UIElement.factory("accept_notification",          pygame.USEREVENT+2, (0.00, 0.80), (0.50, 0.20), dialog_resolution, None, text="ACCEPT") #Could do this in realtion with the total canvas size
    cancelButton        = UIElement.factory("cancel_notification",          pygame.USEREVENT+2, (0.50, 0.80), (0.50, 0.20), dialog_resolution, None, text="CANCEL")
    exitDialog          = UIElement.factory("exit_main_menu_notification",  pygame.USEREVENT+2, dialog_position, dialog_resolution, res, None, acceptButton, cancelButton, text="Exit this shit?")
    #Sliders of the music and sound menu
    sliderMenuMusic     = UIElement.factory("change_menu_music_volume", pygame.USEREVENT, (0.05, 0.10), (0.80, 0.15), res, (0.75), text="Menus music volume", slider_type=0,\
                        start_gradient = RED, end_gradient=BLACK, slider_start_color = RED, slider_end_color = WHITE)
    sliderMenuSounds    = UIElement.factory("change_menu_sound_volume", pygame.USEREVENT, (0.05, 0.30), (0.80, 0.15), res, (0.75), text="Menus sound volume", slider_type=1)
    sliderBoardMusic    = UIElement.factory("change_board_music_volume",pygame.USEREVENT, (0.05, 0.50), (0.80, 0.15), res, (0.75), text="Board music volume", slider_type=2)
    sliderBoardSounds   = UIElement.factory("change_board_sound_volume",pygame.USEREVENT, (0.05, 0.70), (0.80, 0.15), res, (0.75), text="Board sound volume", slider_type=0)

    #Create Menu and board
    main_menu   = Menu("main_menu",         pygame.USEREVENT,   res, (True, 0), \
                buttonStart, buttonParamsMenu, buttonSoundMenu, dialog=exitDialog, background_path=IMG_FOLDER+'\\background.jpg')
    sound_menu  = Menu("menu_volume_music", pygame.USEREVENT+1, res, (True, 0), \
                sliderMenuMusic, sliderMenuSounds, sliderBoardMusic, sliderBoardSounds, background_path=IMG_FOLDER+'\\background.jpg')
    params_menu = Menu("menu_params_config",pygame.USEREVENT+1, res, (True, 0), \
                buttonRes, buttonCountPlayers, buttonNumPawns, buttonNumWarriors, buttonNumWizards, buttonNumPriestess, background_path=IMG_FOLDER+'\\background.jpg')

    main_board = Board("main_board", pygame.USEREVENT+7, res, background_path = IMG_FOLDER+'\\board_2.jpg')
    main_board.create_player("Zippotudo", 0, {"pawn":1, "warrior":1, "wizard":1, "priestess":0}, (100, 100))
    
    #TODO EACH PLAYERS GETS HIS INFOBOARD
    game = Game(main_menu, sound_menu, params_menu, main_board, title="Sava Drow", resolution=res)
    game.start()

