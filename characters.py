import pygame
__all__ = ["Warrior", "Wizard", "Priestess", "Pawn"]

class Character(object):
    def __init__(self):
        sprites = pygame.sprite.Group() #Or a normal list
        self.rect = None
        self.image = None
        self.mask = None
        
    def move(self):
        pass
        if 0: return True #Allowed movm
        if 1: return False #not allowed

    def update(self):
        pass

    def animation_active(self):
        pass

class Warrior(Character):
    def __init__(self):
        pass

class Wizard(Character):
    def __init__(self):
        pass

class Priestess(Character):
    def __init__(self):
        pass

class Pawn(Character):
    def __init__(self):
        pass