"""--------------------------------------------
Colors module. Contains global variables that act as shortcuts
to the most used colors. 
--------------------------------------------"""

import pygame
__version__ = '1.0'
__author__ = 'David Flaity Pardo'

#Global names assigned to pygame default colors. This is actually For the sake of code.
COLORS              = pygame.color.THECOLORS
BLACK               = pygame.Color("black")
WHITE               = pygame.Color("white")
RED                 = pygame.Color("red")
GREEN               = pygame.Color("green")
BLUE                = pygame.Color("blue")
DARKGRAY            = pygame.Color("darkgray")
LIGHTGRAY           = pygame.Color("lightgray")
TRANSPARENT_GRAY    = (128, 128, 128, 128)

CLEAR_RED           = (255, 55, 55, 0)
CLEAR_BLUE          = (55, 55, 255, 0)
CLEAR_GREEN         = (55, 255, 55, 0)
CLEAR_YELLOW        = (255, 255, 55, 0)
CLEAR_PINK          = (255, 55, 255, 0)

COLOR_CHOOSER = {0: CLEAR_RED, 1: CLEAR_GREEN, 2: CLEAR_BLUE, 3: CLEAR_YELLOW, 4: CLEAR_PINK}