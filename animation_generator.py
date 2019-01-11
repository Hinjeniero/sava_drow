from animation import ScriptedSprite, Animation
from paths import IMG_FOLDER
import pygame

class AnimationGenerator(object):

    @staticmethod
    def pawn_crossing_screen(resolution, time, *fps):
        if not isinstance(fps, tuple):
            fps = fps,
        ratio_size = 0.10
        init_pos = (0, int(resolution[1]*(1-ratio_size)))
        size = tuple(res * ratio_size for res in resolution)
        pawn = ScriptedSprite('pawn_crossing', init_pos, size, resolution, fps[0], fps, sprite_folder=IMG_FOLDER+'\\Pawn', animation_delay=5)
        pawn.add_movement(init_pos, (resolution), time)
        animation = Animation('Crossing screen bro', pygame.USEREVENT+6)
        animation.add_sprite(pawn)
        return animation