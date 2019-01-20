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
from sprite import AnimatedSprite
from paths import IMG_FOLDER
from decorators import time_it
from surface_loader import SurfaceLoader, no_size_limit

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
MOVE_KEYWORDS = ('run', )

class AnimationGenerator(object):
    @staticmethod
    def animated_tree_platform(resolution):
        tree_sprite = AnimatedSprite('tree', (0, 0), resolution, resolution, sprite_folder=IMG_FOLDER+'\\Tree',\
                                    resize_smooth=False)
        tree_sprite.set_position(tuple(x//2 - y//2 for x,y in zip(resolution, tree_sprite.rect.size)))
        return tree_sprite

    @staticmethod
    def industrial_layered_background(resolution, time, *fps):
        return AnimationGenerator.layered_animated_background(resolution, time, fps, IMG_FOLDER+'\\Industrial',\
                                                            'background', 'far', 'front', 'foreground')

    @staticmethod
    @no_size_limit
    def layered_animated_background(resolution, time, fps_modes, folder, background_keyword, *layers_keywords, mode='fit'):
        animation = LoopedAnimation('Layered animated background bro')
        AnimationGenerator.add_background(animation, resolution, fps_modes, folder, background_keyword)
        time_ratio = len(layers_keywords)
        layer_index = 1
        initial_out_of_screen   = tuple(-x for x in resolution)
        #Adding first layer, the background
        for layer_kw in layers_keywords:
            layer_time = time*time_ratio
            layer_sprited = ScriptedSprite('layered_sprite', initial_out_of_screen, resolution, resolution, fps_modes[0], fps_modes,\
                                        sprite_folder=folder, keywords=(layer_kw,), resize_smooth=False, resize_mode=mode)
            layer_sprited_copy = layer_sprited.copy()
            init_pos = (-resolution[0], resolution[1]-layer_sprited.rect.height)
            end_pos = (resolution[0], resolution[1]-layer_sprited.rect.height)
            layer_sprited.add_movement(init_pos, end_pos, layer_time)
            layer_sprited_copy.add_movement(init_pos, end_pos, layer_time)
            animation.add_sprite(layer_sprited, 0, layer_time, layer_index)
            animation.add_sprite(layer_sprited_copy, 0.5*layer_time, 1.5*layer_time, layer_index)
            time_ratio -= 1
            layer_index += 1
        return animation

    @staticmethod
    def add_background(animation, resolution, fps_modes, folder, background_keyword):
        background = ScriptedSprite('layered_sprite', (0, 0), resolution, resolution, fps_modes[0], fps_modes,\
                                    sprite_folder=folder, keywords=(background_keyword,), resize_mode='fill', resize_smooth=False)
        background.add_movement((0, 0), (0, 0), 1)
        animation.add_sprite(background, 0, 1, 0) #TODO this generic method to have the sprite still, convert to a method                           

    @staticmethod
    @no_size_limit
    def animated_static_background(id_, folder, resolution, time, *fps):
        animation = LoopedAnimation(id_+' bro')
        waterfall = ScriptedSprite(id_, (0, 0), resolution, resolution, fps[0], fps, sprite_folder=folder,\
                                    resize_mode='fill', resize_smooth=False, animation_delay=5)
        waterfall.add_movement((0, 0), (0, 0), 1)
        animation.add_sprite(waterfall, 0, time)
        return animation

    @staticmethod
    def animated_waterfall_background(resolution, time, *fps):
        return AnimationGenerator.animated_static_background('waterfall', IMG_FOLDER+'\\Waterfall', resolution, time, *fps)

    @staticmethod
    def animated_cave_waterfall_background(resolution, time, *fps):
        return AnimationGenerator.animated_static_background('waterfall_cave', IMG_FOLDER+'\\Waterfall_dark', resolution, time, *fps)

    @staticmethod
    def animated_rain_tree(resolution, time, *fps):
        return AnimationGenerator.animated_static_background('spirit_tree', IMG_FOLDER+'\\Rain_tree', resolution, time, *fps)
    
    @staticmethod
    def animated_rain_chinese(resolution, time, *fps):
        return AnimationGenerator.animated_static_background('chinese_chon_hon', IMG_FOLDER+'\\Rain_chinese', resolution, time, *fps)

    @staticmethod
    @time_it
    def characters_crossing_screen(resolution, *fps, ammount=5, time_interval=(4, 10)):
        animation = AnimationGenerator.sprite_crossing_screen(resolution, random.randint(time_interval[0],\
                                                            time_interval[1]), random.choice(SPRITE_PATHS), *fps)
        ratio_size = 0.10
        size = tuple(res * ratio_size for res in resolution)
        for _ in range(0, ammount-1):
            sprite = ScriptedSprite(random.choice(SPRITE_NAMES), (0, 0), size, resolution, fps[0], fps,\
                                    sprite_folder=random.choice(SPRITE_PATHS), keywords=MOVE_KEYWORDS)
            init_pos = (-sprite.rect.width, resolution[1]-sprite.rect.height)
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
        init_pos = (-sprite.rect.width, resolution[1]-sprite.rect.height)
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
        end_door = ScriptedSprite('door', (0, 0), size, resolution, fps[0], fps, sprite_folder=DOOR_PATH, animation_delay=1)
        sprite = ScriptedSprite('sans', (0, 0), size, resolution, fps[0], fps, sprite_folder=IMG_FOLDER+'\\sans_hd', animation_delay=1)
        #params
        init_pos = ((start_pos*resolution[0]), resolution[1]-sprite.rect.height)
        end_pos = ((end_pos*resolution[0])-(end_door.rect.width//2), resolution[1]-sprite.rect.height)
        start_door.add_movement(init_pos, init_pos, time)
        end_door.add_movement(end_pos, end_pos, time)
        sprite.add_movement(init_pos, end_pos, time)
        #Creating animation
        animation = LoopedAnimation('Crossing screen bro')
        animation.add_sprite(start_door, 0, time, 0)
        animation.add_sprite(end_door, 0, time, 0)
        animation.add_sprite(sprite, 0, time, 1)
        return animation  