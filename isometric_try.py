import pygame, math, numpy
from pygame.locals import *

pygame.init()
resolution = (800, 600)
pygame.mouse.set_visible(True)
clock = pygame.time.Clock()
fps = 60
screen = pygame.display.set_mode(resolution)

background = pygame.Surface(resolution)
background.fill((0,0,0))

border_rect = (100, 100)
option_surf = pygame.Surface(border_rect)
pygame.draw.rect(option_surf, (0, 0, 255), (0,0)+border_rect, 0) #Tuple of 4 components

border_rect_2 = (100, 100)
option_surf_2 = pygame.Surface(border_rect_2)
pygame.draw.rect(option_surf_2, (0, 0, 255), (0,0)+border_rect_2, 5) #Tuple of 4 components

position = [100, 100]
loop = True
stop = False
angle = 0
while loop:
    clock.tick(fps)
    screen.fill((0,0,0))

    screen.blit(background, (0,0))
    screen.blit(pygame.transform.rotate(option_surf, angle), position)
    screen.blit(pygame.transform.rotate(option_surf_2, angle), [x*3 for x in position])
    if not stop:
        angle+=1
    #position = [x+20 for x in position]  
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loop=False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                loop = False
            else:
                all_keys = pygame.key.get_pressed() #Getting all keys pressed in that frame
                if all_keys[pygame.K_SPACE]:
                    if not stop:
                        stop = True
                    else:
                        stop = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pass
    if pygame.mouse.get_rel() != (0,0): #If there is mouse movement
        pass
    pygame.display.update() 
