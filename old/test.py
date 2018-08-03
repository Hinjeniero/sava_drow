import pygame
from pygame.locals import *

pygame.init()
circles = []

class Circle:
    def __init__(self, posx, posy, radius):
        self.pos = (posx, posy)
        self.radius = radius

class Game:
    def __init__(self, fps=60, resolution=(800,600), gameTitle="game_title", backgroundColor=(255, 255, 255), showCursor=True):
        self.fps = fps
        self.bgColor = backgroundColor #Needs to be a tuple of 3 components
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(resolution) #Needs to be a tuple of two components
        self.background = pygame.Surface(resolution)
        self.background.fill(self.bgColor)
        self.showCursor(show=showCursor)
        pygame.display.set_caption(gameTitle)

    def showCursor(self, show=True):
        pygame.mouse.set_visible(show)

    def drawGradient(self, surface, preGradient = '', userGeneratedGradient = (0,0,0)):
        pass

    def run(self):
        loop = True
        global circles
        while loop:
            self.clock.tick(144)
            x, y = pygame.mouse.get_pos() #Getting cursor coordinates
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop=False
                elif event.type is pygame.MOUSEBUTTONDOWN:
                    circles.append(Circle(x, y, 20))
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        all_keys = pygame.key.get_pressed() #Getting all keys pressed in that frame
                        if all_keys[pygame.K_z] and (all_keys[pygame.K_LCTRL] or all_keys[pygame.K_RCTRL]): #Registering ctrl+z
                            if len(circles) > 0:
                                circles.pop()
                    
            self.screen.fill(self.bgColor)
            for circle in circles:
                pygame.draw.circle(self.screen, (255, 0, 0), circle.pos, circle.radius)
            pygame.draw.circle(self.screen, (255, 0, 0), (x, y), 20)
            pygame.display.update() #We could use flip too since in here we are not specifying any part of the screen
    
game = Game()
game.run()



