import pygame
import random
import math
from settings import USEREVENTS
from obj.sprite import Sprite, AnimatedSprite
from obj.utilities.colors import LIGHTGRAY
from obj.utilities.decorators import run_async_not_pooled
from obj.utilities.logger import Logger as LOG

class Dice(AnimatedSprite):
    GOLD_VALUE = 6
    MAX_DICE_VALUE = 6
    WEIGHTS = [1 for _ in range(1, MAX_DICE_VALUE)]
    VALUES = [i for i in range(1, MAX_DICE_VALUE)]
    def __init__(self, id_, position, size, canvas_size, shuffle_time=0, rotate_kw='rot', result_kw='res', limit_throws=3, **params):
        """Shuffle time in miliseconds"""
        super().__init__(id_, position, size, canvas_size, **params)
        self.currently_shuffling = False
        self.shuffle_time = shuffle_time
        self.event = pygame.event.Event(USEREVENTS.BOARD_USEREVENT, command='dice', value=None, id=id_)
        self.shuffling_event = pygame.event.Event(USEREVENTS.BOARD_USEREVENT, command='shuffling', value=None, id=id_)
        self.throws = {}    #Here are all the players and their throws
        self.current_player = None
        self.turns = 0
        self.max_throws = limit_throws+1
        self.rotate_kw = rotate_kw
        self.result_kw = result_kw
        self.current_result = 1
        self.overlay = None

    @run_async_not_pooled
    def shuffle(self):
        if self.throws[self.current_player] < self.max_throws:
            if not self.locked:
                self.currently_shuffling = True
                if not self.shuffle_time:   pygame.time.set_timer(USEREVENTS.BOARD_USEREVENT, 100)
                else:                       pygame.time.set_timer(USEREVENTS.BOARD_USEREVENT, self.shuffle_time//len(self.surfaces))
            else:
                self.reactivating_dice()
        else:
            LOG.log('info', 'You spent your ammount of throws, you rolled enough already, dont you think?')

    def hitbox_action(self, *pr, **kw): #This is only used for the initial dices
        pygame.event.post(self.shuffling_event)
        self.shuffle()

    def add_turn(self, next_player):
        self.turns += 1
        self.current_player = next_player
        try:
            self.throws[self.current_player]
        except KeyError:
            self.throws[self.current_player] = 1
        self.deactivating_dice(value=self.current_result)

    def reactivating_dice(self):
        self.locked = False
        self.set_enabled(True)

    def deactivating_dice(self, value=1):
        for i in range(0, len(self.names)):
            if self.result_kw in self.names[i] and str(value) in self.names[i]:
                self.animation_index = i
                self.image = self.surfaces[i]
                break
        self.overlay = Sprite.generate_overlay(self.surfaces[self.animation_index], LIGHTGRAY)
        self.locked = True
        self.set_enabled(False)

    def increase_animation_delay(self):
        self.next_frame_time += 1
        if self.next_frame_time >= len(self.surfaces):  #End of animation
            self.next_frame_time = self.params['animation_delay']
            pygame.time.set_timer(USEREVENTS.BOARD_USEREVENT, 0)    #Disabling this timer
            self.throw()

    def animation_frame(self):
        """Changes the current showing surface (changing the index) to the next one."""
        if (self.hover and self.enabled) or self.currently_shuffling:   #If hovering over it
            while not self.locked:  #Acts as a while True, and doesnt get caught up in it when the animation frame is not flowing due to self.locked being True
                super().animation_frame()
                if self.rotate_kw in self.names[self.animation_index]:
                    break

    def get_random_value(self):
        weights = Dice.WEIGHTS.copy()
        x = math.log10(self.turns/(self.throws[self.current_player]*3))
        weights[-1] += math.tanh(x)
        weights[-1] = max(0.3, weights[-1])
        #print("Pos of getting a 6 is "+str(weights[-1]))
        return random.choices(Dice.VALUES, weights)[0]

    def throw(self):
        self.add_throw(self.current_player)
        self.current_result = self.get_random_value()
        self.event.value = self.current_result
        pygame.event.post(self.event)
        LOG.log('info', "You rolled a ", self.current_result)
        self.currently_shuffling = False
        self.deactivating_dice(value=self.current_result)
    
    def add_throw(self, player_uuid):
        self.throws[player_uuid] += 1