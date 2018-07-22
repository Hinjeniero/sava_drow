import pygame, math, numpy
from pygame.locals import *
import gradients #Gradients in polygons
import ptext #Gradients in text
from polygons import Circle, Rectangle

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
    def __init__(self, fps=60, resolution=(1024, 768), background_path=None, circles_per_lvl=16, lvls=4):
        self.fps = fps
        self.bg_path = background_path
        self.background = self.load_background(resolution, self.bg_path)
        self.clock = pygame.time.Clock()

        self.elements = {}
        self.circles_per_lvl = circles_per_lvl
        self.lvl_inception = lvls

        self.board = Rectangle(resolution[0]*0.05, resolution[1]*0.05, resolution[0]*0.75, resolution[1]*0.9, color=(0, 255, 0)) 
        self.board_texture = pygame.transform.scale(pygame.image.load('wood.png'), self.board.size)
        self.platform = Circle(self.board.pos[0]+self.board.size[0]/2, self.board.pos[1]+self.board.size[1]/2, resolution[0]/2.5 , color=(0,0,0), width=2) 
        self.active_circle = (0, 0)

        dim = int((self.platform.radius*math.pi)/circles_per_lvl)+1
        self.distance_table = self.create_distances_table(dim) #LUT to store the euclidean distances. Useful in the circles hitbox checking

    def create_distances_table(self, dimensions):
        matrix = numpy.empty([dimensions+1, dimensions+1])
        x = 0
        for i in range (0, dimensions+1):
            for j in range (x, dimensions+1):
                euclidean = math.sqrt(i*i + j*j)
                matrix[i][j] = euclidean
                matrix[j][i] = euclidean
            x+=1
        return matrix


    def calculate_circles(self, radius_mult=0.3):
        double_pi = 2*math.pi
        step = (double_pi)/self.circles_per_lvl
        angle = double_pi/8 #In the first iteration we want it like this, since we only want 4 circles
        ratio = self.platform.radius/(self.lvl_inception+1)
        big_radius = 0

        for i in range (0, self.lvl_inception): #1 is the internal lvl, we will go externally
            big_radius+=ratio
            circumference = big_radius*math.pi #circumference = rad*pi
            self.elements[i]=[] #Initiating list
            while angle < double_pi: #2*pi rads= 360º
                x_pos = self.platform.pos[0]+big_radius*math.cos(angle)
                y_pos = self.platform.pos[1]+big_radius*math.sin(angle)
                small_radius = radius_mult*circumference/self.circles_per_lvl #Crescent circles
                if small_radius < ratio*radius_mult:
                    small_radius=ratio*radius_mult
                circ_surface = gradients.radial(int(small_radius), (0, 0, 0, 255), (255, 255, 255, 100))
                circ = Circle(x_pos, y_pos, small_radius, surface=circ_surface)
                self.elements[i].append(circ)
                if i is not 0: #First circle, only 4 small ones.
                    angle += step                   
                else:
                    angle += double_pi/4
            angle=0

    def load_background(self, size, background_path=None):
        if background_path is None:
            bg_surf = gradients.vertical(size, (255, 255, 255, 255), (50, 50, 50, 255)) #Gradient from white to grey-ish
        else:
            bg_surf = pygame.transform.scale(pygame.image.load(background_path), size)
        return bg_surf

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        pygame.draw.rect(surface, self.board.color, (self.board.pos, self.board.size), self.board.width)
        surface.blit(self.board_texture, self.board.pos)
        ratio = self.platform.radius/(self.lvl_inception+1)
        radius = 2*ratio
        for i in range (0, self.lvl_inception-1): #Dont want a circle in the first lvl
            pygame.draw.circle(surface, self.platform.color, self.platform.pos, int(radius), 3) #Drawing big circle
            radius+=ratio
        for lvl, list_of_circles in self.elements.items():
            index = 0
            for circle in list_of_circles:
                pygame.draw.circle(surface, (0,0,0,255), circle.pos, circle.radius+2)
                if circle.surface is not None:
                    if lvl is self.active_circle[0] and index is self.active_circle[1]:
                        pass
                    else:
                        surface.blit(circle.surface, circle.surface_pos)
                    #x = circle.surface.get_size()
                    #rect = pygame.Rect(circle.pos+x)
                    #pygame.draw.rect(surface, (255, 0, 0), rect, 2)
                index+=1
        pygame.display.update() #We could use flip too since in here we are not specifying any part of the screen
    
    #Does all the shit related to the mouse hovering an option
    def mouse_collider(self, mouse_position):
        for lvl, list_of_circles in self.elements.items():
            index = 0
            for circle in list_of_circles:
                try:
                    pos_difference = tuple(abs(circle_axis_coord-mouse_axis_coord) for circle_axis_coord,mouse_axis_coord in zip(mouse_position, circle.pos))
                    if self.distance_table[pos_difference[0]][pos_difference[1]] < circle.radius:
                        return (lvl, index)
                except IndexError: #Its way too far away from this hitbox
                    pass
                index+=1
        return self.active_circle #No option is selected, we leave whatever was active

    def event_handler(self, events, keys_pressed, mouse_movement=False, mouse_pos=(0, 0)):
        for event in events:
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        if mouse_movement:
            self.active_circle = self.mouse_collider(mouse_pos)
        return True

    def run(self):
        self.calculate_circles()
        loop = True
        while loop:
            self.clock.tick(self.fps)
            self.draw(screen)
            if pygame.mouse.get_rel() != (0,0): #If there is mouse movement
                loop = self.event_handler(pygame.event.get(), pygame.key.get_pressed(), mouse_movement=True, mouse_pos=pygame.mouse.get_pos())
            else:
                loop = self.event_handler(pygame.event.get(), pygame.key.get_pressed())

if __name__ == "__main__":
    game = Board()
    game.run()