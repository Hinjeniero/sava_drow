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
from obj.animation import ScriptedSprite, Animation, LoopedAnimation
from obj.sprite import AnimatedSprite, TextSprite
from obj.utilities.decorators import time_it, run_async
from obj.utilities.surface_loader import SurfaceLoader, no_size_limit
from settings import PATHS, STRINGS

PYGAME_EVENT = -1
MOVE_KEYWORDS = ('run', )

class AnimationGenerator(object):
    @staticmethod
    def factory(request_id, resolution, time, fps_modes, current_fps):
        animation = None
        request_id = request_id.lower()
        if 'layer' in request_id:
            if 'industrial' in request_id:
                animation = AnimationGenerator.industrial_layered_background(resolution, time, *fps_modes)
            elif 'forest' in request_id:
                animation = AnimationGenerator.forest_layered_background(resolution, time, *fps_modes)
        if 'animated' in request_id:
            if 'waterfall' in request_id:
                if 'cave' in request_id:
                    animation = AnimationGenerator.animated_cave_waterfall_background(resolution, time, *fps_modes)
                else:
                    animation = AnimationGenerator.animated_waterfall_background(resolution, time, *fps_modes)
            elif 'rain' in request_id:
                if 'chin' in request_id:
                    animation = AnimationGenerator.animated_rain_chinese(resolution, time, *fps_modes)
                else:
                    animation = AnimationGenerator.animated_rain_tree(resolution, time, *fps_modes)
        if animation:
            animation.set_fps(current_fps)
        return animation


    @staticmethod
    @time_it
    def animated_tree_platform(resolution):
        tree_sprite = AnimatedSprite('tree', (0, 0), resolution, resolution, sprite_folder=PATHS.ANIMATED_TREE,\
                                    resize_smooth=False)
        tree_sprite.set_position(tuple(x//2 - y//2 for x,y in zip(resolution, tree_sprite.rect.size)))
        return tree_sprite

    @staticmethod
    @time_it
    def industrial_layered_background(resolution, time, *fps):
        return AnimationGenerator.layered_animated_background(resolution, time, fps, PATHS.INDUSTRIAL_LAYERED_BG,\
                                                            'background', 'far', 'front', 'foreground')

    @staticmethod
    @time_it
    def forest_layered_background(resolution, time, *fps):
        return AnimationGenerator.layered_animated_background(resolution, time, fps, PATHS.INDUSTRIAL_LAYERED_BG,\
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
    @time_it
    def animated_waterfall_background(resolution, time, *fps):
        return AnimationGenerator.animated_static_background('waterfall', PATHS.ANIMATED_WATERFALL_BG, resolution, time, *fps)

    @staticmethod
    @time_it
    def animated_cave_waterfall_background(resolution, time, *fps):
        return AnimationGenerator.animated_static_background('waterfall_cave', PATHS.ANIMATED_CAVE_WATERFALL_BG, resolution, time, *fps)

    @staticmethod
    @time_it
    def animated_rain_tree(resolution, time, *fps):
        return AnimationGenerator.animated_static_background('spirit_tree', PATHS.ANIMATED_RAIN_TREE_BG, resolution, time, *fps)
    
    @staticmethod
    @time_it
    def animated_rain_chinese(resolution, time, *fps):
        return AnimationGenerator.animated_static_background('chinese_chon_hon', PATHS.ANIMATED_RAIN_CHINESE_BG, resolution, time, *fps)
    
    ####NORMAL ANIMATIONS FORM HERE ON
    @staticmethod
    def explosions_bottom(resolution, *fps, bottom_offset=0.00, init_ratio=0.05):
        animation = LoopedAnimation('MICHAEL BAY')
        folder = PATHS.EXPLOSIONS
        index = 1
        ratio = init_ratio
        for explosion_type in PATHS.ALL_EXPLOSIONS:
            size = tuple(ratio*x for x in resolution)
            sprite = ScriptedSprite('explasion_'+str(index), (0, 0), size, resolution, fps[0], fps, sprite_folder=folder,\
                                    keywords=(explosion_type,), animation_delay=5)
            x = index*(resolution[0]*0.8)//len(PATHS.ALL_EXPLOSIONS)
            position = (x, (resolution[1]*(1-bottom_offset))-sprite.rect.height)
            sprite.set_position(position)
            sprite.add_movement(position, position, 1)
            animation.add_sprite(sprite, 0, 1)
            index += 1
            ratio += init_ratio
        return animation

    @staticmethod
    def explosions_deccelerating_bottom(resolution, *fps, bottom_offset=0.00, size=0.20):
        animation = LoopedAnimation('EXPLOSIUNS')
        folder = PATHS.EXPLOSIONS
        size = tuple(size*x for x in resolution)
        index = 1
        for explosion_type in PATHS.ALL_EXPLOSIONS:
            sprite = ScriptedSprite('explasion_'+str(index), (0, 0), size, resolution, fps[0], fps, sprite_folder=folder,\
                                    animation_delay=2*index)
            x = index*(resolution[0]*0.8)//len(PATHS.ALL_EXPLOSIONS)
            position = (x, (resolution[1]*(1-bottom_offset))-sprite.rect.height)
            sprite.set_position(position)
            sprite.add_movement(position, position, 1)
            animation.add_sprite(sprite, 0, 1)
            index += 1
        return animation

    @staticmethod
    @time_it
    def characters_crossing_screen(resolution, *fps, ammount=5, time_interval=(4, 10)):
        animation = AnimationGenerator.sprite_crossing_screen(resolution, random.randint(time_interval[0],\
                                                            time_interval[1]), random.choice(PATHS.CHARS), *fps)
        ratio_size = 0.10
        size = tuple(res * ratio_size for res in resolution)
        for _ in range(0, ammount-1):
            sprite = ScriptedSprite(random.choice(STRINGS.SPRITE_NAMES), (0, 0), size, resolution, fps[0], fps,\
                                    sprite_folder=random.choice(PATHS.CHARS), keywords=MOVE_KEYWORDS)
            init_pos = (-sprite.rect.width, resolution[1]-sprite.rect.height)
            end_pos = (resolution[0], resolution[1]-sprite.rect.height)
            time = time_interval[0]+(random.random()*(time_interval[1]-time_interval[0]))
            sprite.add_movement(init_pos, end_pos, time)
            animation.add_sprite(sprite, 0, time)
        return animation 

    @staticmethod
    def pawn_crossing_screen(resolution, time, *fps):
        return AnimationGenerator.sprite_crossing_screen(resolution, time, PATHS.PAWN, *fps)

    @staticmethod
    def warrior_crossing_screen(resolution, time, *fps):
        return AnimationGenerator.sprite_crossing_screen(resolution, time, PATHS.WARRIOR, *fps)

    @staticmethod
    def wizard_crossing_screen(resolution, time, *fps):
        return AnimationGenerator.sprite_crossing_screen(resolution, time, PATHS.WIZARD, *fps)

    @staticmethod
    def priestess_crossing_screen(resolution, time, *fps):
        return AnimationGenerator.sprite_crossing_screen(resolution, time, PATHS.PRIESTESS, *fps)

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
                                                            time_interval[1]), random.choice(PATHS.CHARS), *fps,
                                                            start_pos=start_pos, end_pos=end_pos)
        return animation

    @staticmethod
    def bounce_sprite(resolution, start_pos, end_pos, time, fps_modes, folder, *keywords):
        pass

    @staticmethod
    def floating_logo(resolution, text, start_pos, end_pos, size, time, fps_modes, folder, keywords=None): #TODO DO THE ANIMATED_CHARACTER TEXT ON TOP DRAWING
        animation = AnimationGenerator.floating_sprite(resolution, start_pos, end_pos, size, time, fps_modes, folder, keywords=keywords)
        text = TextSprite('text', start_pos, size, resolution, text, resize_mode='fill')
        sprite = ScriptedSprite('door', start_pos, size, resolution, fps_modes[0], fps_modes, sprite_folder=folder, keywords=keywords)
        init_pos = tuple((x*pos)-y//2 for x, pos, y in zip(resolution, start_pos, sprite.rect.size))
        end_pos = tuple((x*pos)-y//2 for x, pos, y in zip(resolution, end_pos, sprite.rect.size))
        sprite.add_movement(init_pos, end_pos, time)
        sprite.add_movement(end_pos, init_pos, time)
        animation = LoopedAnimation('Floating sprite')
        animation.add_sprite(sprite, 0, time, 0)

    @staticmethod
    def floating_sprite(resolution, start_pos, end_pos, size, time, fps_modes, folder, keywords=None):
        sprite = ScriptedSprite('door', start_pos, size, resolution, fps_modes[0], fps_modes, sprite_folder=folder, keywords=keywords)
        init_pos = tuple((x*pos)-y//2 for x, pos, y in zip(resolution, start_pos, sprite.rect.size))
        end_pos = tuple((x*pos)-y//2 for x, pos, y in zip(resolution, end_pos, sprite.rect.size))
        sprite.add_movement(init_pos, end_pos, time)
        sprite.add_movement(end_pos, init_pos, time)
        animation = LoopedAnimation('Floating sprite')
        animation.add_sprite(sprite, 0, time, 0)
        return animation

    @staticmethod
    @time_it
    def sprite_teleporting_screen(resolution, time, folder, *fps, start_pos=0.20, end_pos=0.80):
        if not isinstance(fps, tuple):
            fps = fps,
        ratio_size = 0.20
        size = tuple(res * ratio_size for res in resolution)
        #Sprites
        start_door = ScriptedSprite('door', (0, 0), size, resolution, fps[0], fps, sprite_folder=PATHS.DOOR, animation_delay=2)
        end_door = ScriptedSprite('door', (0, 0), size, resolution, fps[0], fps, sprite_folder=PATHS.DOOR, animation_delay=2)
        sprite = ScriptedSprite('sans', (0, 0), size, resolution, fps[0], fps, sprite_folder=PATHS.SANS, animation_delay=2)
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