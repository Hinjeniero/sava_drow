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
from animation import ScriptedSprite, Animation, LoopedAnimation
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
    def industrial_moving_background(resolution, time, *fps):
        animation       = Animation('Moving background bro', -1, -1)
        #Loading
        background      = ScriptedSprite('sprite_crossing', (0, 0), resolution, resolution, fps[0], fps,\
                                        sprite_folder=IMG_FOLDER+'\\Industrial', keywords=('background',)) 
        far_buildings_1 = ScriptedSprite('start_far_buildings', (0, 0), resolution, resolution, fps[0], fps,\
                                        sprite_folder=IMG_FOLDER+'\\Industrial', keywords=('far',))
        far_buildings_2 = ScriptedSprite('end_far_buildings', (0, 0), resolution, resolution, fps[0], fps,\
                                        sprite_folder=IMG_FOLDER+'\\Industrial', keywords=('far',))
        buildings_1     = ScriptedSprite('start_buildings', (0, 0), resolution, resolution, fps[0], fps,\
                                        sprite_folder=IMG_FOLDER+'\\Industrial', keywords=('front',))
        buildings_2     = ScriptedSprite('end_buildings', (0, 0), resolution, resolution, fps[0], fps,\
                                        sprite_folder=IMG_FOLDER+'\\Industrial', keywords=('front',))
        foreground_1    = ScriptedSprite('start_foreground', (0, 0), resolution, resolution, fps[0], fps,\
                                        sprite_folder=IMG_FOLDER+'\\Industrial', keywords=('foreground',))
        foreground_2    = ScriptedSprite('end_foreground', (0, 0), resolution, resolution, fps[0], fps,\
                                        sprite_folder=IMG_FOLDER+'\\Industrial', keywords=('foreground',))
        #Params
        init_pos = (-resolution[0], resolution[1])
        end_pos  = (resolution[0], resolution[1])
        far_init_pos = (init_pos[0], init_pos[1]-far_buildings_1.rect.height) 
        far_end_pos = (end_pos[0], end_pos[1]-far_buildings_1.rect.height) 
        build_init_pos = (init_pos[0], init_pos[1]-buildings_1.rect.height)
        build_end_pos = (end_pos[0], end_pos[1]-buildings_1.rect.height)
        fore_init_pos = (init_pos[0], init_pos[1]-foreground_1.rect.height)
        fore_end_pos = (end_pos[0], end_pos[1]-foreground_1.rect.height)
        print("FAR "+str(far_init_pos))
        print("BUILD "+str(build_init_pos))
        print("FORE "+str(fore_init_pos))
        print("SIZE FAR "+str(far_buildings_1.rect.size))
        print("SIZE BILD "+str(buildings_1.rect.size))
        print("SIZE FORE "+str(foreground_1.rect.size))
        #Timers
        building_time = time*2
        far_building_time = time*3
        foreground_time = time
        #Animating
        background.add_movement((0, 0), (0, 0), 1)
        far_buildings_1.add_movement(far_init_pos, far_end_pos, far_building_time)  #TODO make a copy of this.
        far_buildings_2.add_movement(far_init_pos, far_end_pos, far_building_time)
        buildings_1.add_movement(build_init_pos, build_end_pos, building_time)
        buildings_2.add_movement(build_init_pos, build_end_pos, building_time)
        foreground_1.add_movement(fore_init_pos, fore_end_pos, foreground_time)
        foreground_2.add_movement(fore_init_pos, fore_end_pos, foreground_time)
        #Adding to animation
        animation.add_sprite(background, 0, time)
        animation.add_sprite(far_buildings_1, 0, far_building_time)
        animation.add_sprite(far_buildings_2, 0.5*far_building_time, 1.5*far_building_time)
        animation.add_sprite(buildings_1, 0, building_time)
        animation.add_sprite(buildings_2, 0.5*building_time, 1.5*building_time)
        animation.add_sprite(foreground_1, 0, foreground_time)
        animation.add_sprite(foreground_2, 0.5*foreground_time, 1.5*foreground_time) #How to not repeat this shit
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
        init_pos = ((start_pos*resolution[0]), resolution[1]-sprite.rect.height)
        end_pos = ((end_pos*resolution[0])-(end_door.rect.width//2), resolution[1]-sprite.rect.height)
        start_door.add_movement(init_pos, init_pos, time)
        end_door.add_movement(end_pos, end_pos, time)
        sprite.add_movement(init_pos, end_pos, time)
        #Creating animation
        animation = LoopedAnimation('Crossing screen bro')
        animation.add_sprite(start_door, 0, time)
        animation.add_sprite(end_door, 0, time)
        animation.add_sprite(sprite, 0, time)
        return animation  