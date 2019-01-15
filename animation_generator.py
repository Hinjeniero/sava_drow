"""--------------------------------------------
animation_generator module. Contains classes to generate
generic useful animations
Have the following classes:
    AnimationGenerator
--------------------------------------------"""

__all__ = ['AnimationGenerator']
__version__ = '0.1'
__author__ = 'David Flaity Pardo'

#Python libraries
import pygame
import random
#Selfmade libraries
from animation import ScriptedSprite, LoopedAnimation
from paths import IMG_FOLDER
from decorators import time_it

"""Global variables, read_only:
    PYGAME_EVENT:
    SPRITE_PATHS:
    SPRITE_NAMES:
    MOVE_KEYWORDS:
"""
PYGAME_EVENT = pygame.USEREVENT+6
SPRITE_PATHS = (IMG_FOLDER+'\\Pawn', IMG_FOLDER+'\\Warrior', IMG_FOLDER+'\\Wizard',
                IMG_FOLDER+'\\Priestess')
DOOR_PATH = (IMG_FOLDER+'\\Portal')
SPRITE_NAMES = ('Manolo', 'Eustaquio', 'Zimamamio')
MOVE_KEYWORDS = ('walk', )

class AnimationGenerator(object):
    @staticmethod
    @time_it
    def characters_crossing_screen(resolution, *fps, ammount=1, time_interval=(4, 10)):
        animation = AnimationGenerator.sprite_crossing_screen(resolution, random.randint(time_interval[0],\
                                                            time_interval[1]), random.choice(SPRITE_PATHS), *fps)
        ratio_size = 0.10
        size = tuple(res * ratio_size for res in resolution)
        for _ in range(0, ammount-1):
            sprite = ScriptedSprite(random.choice(SPRITE_NAMES), (0, 0), size, resolution, fps[0], fps,\
                                    sprite_folder=random.choice(SPRITE_PATHS), keywords=MOVE_KEYWORDS)
            init_pos = (0, resolution[1]-sprite.rect.height)
            end_pos = (resolution[0], resolution[1]-sprite.rect.height)
            time = time_interval[0]+(random.random()*(time_interval[1]-time_interval[0]))
            sprite.add_movement(init_pos, end_pos, time)
            animation.add_sprite(sprite, 0, time)
        return animation

    @staticmethod
    def pawn_crossing_screen(resolution, time, *fps):
        return AnimationGenerator.sprite_crossing_screen(resolution, time, IMG_FOLDER+'\\Pawn', *fps)

    @staticmethod
    def warrior_crossing_screen(resolution, time, *fps):
        return AnimationGenerator.sprite_crossing_screen(resolution, time, IMG_FOLDER+'\\Warrior', *fps)

    @staticmethod
    def wizard_crossing_screen(resolution, time, *fps):
        return AnimationGenerator.sprite_crossing_screen(resolution, time, IMG_FOLDER+'\\Wizard', *fps)

    @staticmethod
    def priestess_crossing_screen(resolution, time, *fps):
        return AnimationGenerator.sprite_crossing_screen(resolution, time, IMG_FOLDER+'\\Priestess', *fps)

    @staticmethod
    def sprite_crossing_screen(resolution, time, folder, *fps):
        if not isinstance(fps, tuple):
            fps = fps,
        ratio_size = 0.10
        size = tuple(res * ratio_size for res in resolution)
        sprite = ScriptedSprite('sprite_crossing', (0, 0), size, resolution, fps[0], fps, sprite_folder=folder, keywords=MOVE_KEYWORDS)
        init_pos = (0, resolution[1]-sprite.rect.height)
        end_pos = (resolution[0], resolution[1]-sprite.rect.height)
        sprite.add_movement(init_pos, end_pos, time)
        animation = LoopedAnimation('Crossing screen bro')
        animation.add_sprite(sprite, 0, time)
        return animation

    @staticmethod
    def character_teleporting_screen(resolution, *fps, ammount=10, time_interval=(4, 10), start_pos=0.20, end_pos=0.80):
        animation = AnimationGenerator.sprite_teleporting_screen(resolution, random.randint(time_interval[0],\
                                                            time_interval[1]), random.choice(SPRITE_PATHS), *fps,
                                                            start_pos=start_pos, end_pos=end_pos)
        return animation

    @staticmethod
    def sprite_teleporting_screen(resolution, time, folder, *fps, start_pos=0.20, end_pos=0.80):
        if not isinstance(fps, tuple):
            fps = fps,
        ratio_size = 0.20
        size = tuple(res * ratio_size for res in resolution)
        #Sprites
        start_door = ScriptedSprite('door', (0, 0), size, resolution, fps[0], fps, sprite_folder=DOOR_PATH, animation_delay=1)
        end_door = ScriptedSprite(  'door', (0, 0), size, resolution, fps[0], fps, sprite_folder=DOOR_PATH, animation_delay=1)
        sprite = ScriptedSprite('sans', (0, 0), size, resolution, fps[0], fps, sprite_folder=IMG_FOLDER+'\\sans_hd', animation_delay=1)
        #params
        init_pos = (start_pos*resolution[0], resolution[1]-sprite.rect.height)
        end_pos = (end_pos*resolution[0], resolution[1]-sprite.rect.height)
        start_door.add_movement(init_pos, init_pos, time)
        end_door.add_movement(end_pos, end_pos, time)
        #--
        #init_pos = (init_pos[0]+start_door.rect.width//3, init_pos[1])
        #end_pos = (end_pos[0]-end_door.rect.width//3, init_pos[1])
        sprite.add_movement(init_pos, end_pos, time)
        #Creating animation
        animation = LoopedAnimation('Crossing screen bro')
        animation.add_sprite(start_door, 0, time)
        animation.add_sprite(end_door, 0, time)
        animation.add_sprite(sprite, 0, time)
        return animation  