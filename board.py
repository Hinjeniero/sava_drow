import pygame, math, numpy, os
from utility_box import UtilityBox
from pygame.locals import *
import gradients #Gradients in polygons
import ptext #Gradients in text
from polygons import *

pygame.init()
small_circles_size = 0.75 #1 is 100%
screen = pygame.display.set_mode((1024, 768)) #Needs to be a tuple of two components

class player():
    def __init__(self):
        self.id = 0
        self.characters=[]

class character():
    def __init__(self):
        self.position=-1
        self.surface=None

class Board:
    game_folder = os.path.dirname(__file__)
    img_folder = os.path.join(game_folder, 'img')
    sounds_folder = os.path.join(game_folder, 'sounds')

    __default_config = {'background_path': None,
                        'circles_per_lvl': 16,
                        'max_levels': 4,
                        'soundtheme_path': sounds_folder+'\gametheme.mp3',
                        'soundeffect_path': sounds_folder+'\click.ogg',
                        'font': None,
                        'max_font':200,
    }

    def __init__(self, id, resolution, *characters, **params):
        #Basic info saved
        self.id             = id
        self.resolution     = resolution
        self.config         = Board.__default_config.copy()
        self.config.update(params)

        #Graphic elements
        self.cells          = pygame.sprite.Group()
        self.paths          = pygame.sprite.Group()
        self.active_cell    = pygame.sprite.GroupSingle()
        self.characters     = pygame.sprite.OrderedUpdates()
        self.platform       = None
        self.background     = UtilityBox.load_background(resolution, self.config['background_path'])

        #Music & sounds
        #self.game_theme = pygame.mixer.music.load(self.config['soundtheme_path'])
        #self.click_sound = pygame.mixer.Sound(file=self.config['soundeffect_path'])
        #self.click_sound.set_volume(1)

        for character in characters:
            self.characters.add(character)

        self.generate_object()

    def generate_object(self):
        self.platform = Rectangle((int(self.resolution[0]*0.05), int(self.resolution[1]*0.05)), (int(self.resolution[0]*0.75), int(self.resolution[1]*0.75)))
        self.generate_cells()
        self.generate_paths()

    def generate_cells(self, radius_mult=0.3):
        ratio   = self.platform.rect.width//(2*self.config['max_levels'])
        radius  = 0
        for i in range (0, self.config['max_levels']):                                  #1 is the internal lvl, we will go externally
            radius  += ratio
            if i is 0:  self.cells.add(*self.generate_circles(radius, self.platform.rect.center, radius//6, 4, initial_offset=0.25*math.pi))
            else:       self.cells.add(*self.generate_circles(radius, self.platform.rect.center, radius//6, self.config['circles_per_lvl']))
    
    #TODO could pass params in this function if we want coloured circles
    def generate_circles(self, radius, center, circle_radius, circle_number, initial_offset=0):
        circles = []
        two_pi  = 2*math.pi    
        angle   = initial_offset*(math.pi/180) if initial_offset > two_pi else initial_offset
        distance= two_pi/circle_number
        while angle < two_pi:
            position    = (center[0]+(radius*math.sin(angle))-circle_radius, center[1]+(radius*math.cos(angle))-circle_radius)  
            angle       += distance
            circles.append(Circle(position, (circle_radius*2, circle_radius*2)))
        return circles

    def generate_paths(self):
        ratio = self.platform.rect.width//self.config['max_levels']
        radius = ratio//2
        for i in range (0, self.config['max_levels']): #Dont want a circle in the first lvl
            colorkey = (0, 0, 0)
            out_circle = Circle((self.platform.rect.centerx-radius, self.platform.rect.centery-radius),(radius*2, radius*2), surf_color=colorkey, border_size=3, use_gradient=False)
            out_circle.image.set_colorkey(colorkey)
            out_circle.update_mask()
            self.paths.add(out_circle)
            radius+=ratio//2

    def draw(self, surface, hitboxes=False):
        surface.blit(self.background, (0,0))                                                                            #Draws background
        surface.blit(self.platform.image, self.platform.rect)                                                           #Draws board
        self.paths.draw(surface)                                                                                        #Draws paths between cells
        self.cells.draw(surface)                                                                                        #Draws cells    
        active_sprite = self.active_cell.sprite
        if active_sprite is not None:
            center = (active_sprite.rect.x+active_sprite.rect.width//2, active_sprite.rect.y+active_sprite.rect.height//2)  
            pygame.draw.circle(surface, UtilityBox.random_rgb_color(), center, active_sprite.rect.height//2)             #Draws an overlay on the active cell
        self.characters.draw(surface)                                                                                    #Draws the characters
        if hitboxes:    
            for sprite in self.cells.sprites(): 
                UtilityBox.draw_hitbox(surface, sprite)
        
    def event_handler(self, event, keys_pressed, mouse_buttons_pressed, mouse_movement=False, mouse_pos=(0, 0)):
        if event.type == pygame.KEYDOWN:                    self.keyboard_handler(keys_pressed)
        if mouse_movement or any(mouse_buttons_pressed):    self.mouse_handler(event, mouse_buttons_pressed, mouse_movement, mouse_pos)  

    #Does all the shit related to the mouse hovering an option
    def mouse_handler(self, event, mouse_buttons, mouse_movement, mouse_position):
        #if event.type == pygame.MOUSEBUTTONDOWN:
            #if mouse_buttons[0]:    self.active_sprite.sprite.hitbox_action('first_mouse_button', value=mouse_position)
            #elif mouse_buttons[2]:  self.active_sprite.sprite.hitbox_action('secondary_mouse_button', value=mouse_position)
        if mouse_movement: 
            colliding_sprite = pygame.sprite.spritecollideany(UtilityBox.get_mouse_sprite(mouse_position), self.cells.sprites(), collided=pygame.sprite.collide_circle)
            if colliding_sprite is not None:    
                self.active_cell.add(colliding_sprite)

            test = pygame.sprite.spritecollideany(UtilityBox.get_mouse_sprite(mouse_position), self.paths.sprites(), collided=pygame.sprite.collide_mask)
            if test is not None:
                print(test.radius)

    #TODO KEYBOARD DOES NOT CHANGE ACTIVE CELL, BUT ACTIVE CHARACTER. ACTIVE CELL CHANGE ONLY BY MOUSE
    def keyboard_handler(self, keys_pressed):
        if keys_pressed[pygame.K_DOWN]:         pass
        if keys_pressed[pygame.K_UP]:           pass
        if keys_pressed[pygame.K_LEFT]:         pass
        if keys_pressed[pygame.K_RIGHT]:        pass
        if keys_pressed[pygame.K_KP_ENTER]\
            or keys_pressed[pygame.K_SPACE]:    pass

#List of (ids, text)
if __name__ == "__main__":
    #Variables
    resolution = (1024, 1024)
    pygame.init()
    screen = pygame.display.set_mode(resolution)
    pygame.mouse.set_visible(True)
    clock = pygame.time.Clock()
    timeout = 20

    #Create Board
    game = Board("testboard", resolution)    

    #Start the test
    loop = True
    while loop:
        clock.tick(144)
        game.draw(screen)       #Drawing the sprite group
        fnt = pygame.font.Font(None, 60)
        frames = fnt.render(str(int(clock.get_fps())), True, pygame.Color('white'))
        screen.blit(frames, (50, 150))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:       loop = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:    loop = False
            elif event.type >= pygame.USEREVENT:
                print("Received event number "+str(event.type)+", with value "+str(event.value))
            if loop:            #If not exit yet                        
                game.event_handler(event, pygame.key.get_pressed(), pygame.mouse.get_pressed(),\
                                    mouse_movement=(pygame.mouse.get_rel() != (0,0)), mouse_pos=pygame.mouse.get_pos())
        pygame.display.update() #Updating the screen