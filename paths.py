import os, functools

GAME_FOLDER = os.path.dirname(__file__)
IMG_FOLDER = os.path.join(GAME_FOLDER, 'img')
SOUND_FOLDER = os.path.join(GAME_FOLDER, 'sounds')
@functools.total_ordering
class Path(object):
    def __init__(self, grid_pos, ally, enemy):
        self.pos = grid_pos
        self.ally = ally
        self.enemy = enemy
    
    def has_enemy(self):
        return self.enemy
        
    def has_ally(self):
        return self.ally

    def __lt__(self, path):
        return self.pos[0]<path.pos[0] if self.pos[0] != path.pos[0] else self.pos[1]<path.pos[1]

    def __le__(self, path):
        return True if self.pos[0]<path.pos[0] else True if self.pos[1]<path.pos[1] else self.__eq__(path)

    def __gt__(self, path):
        return self.pos[0]>path.pos[0] if self.pos[0] != path.pos[0] else self.pos[1]>path.pos[1]
    
    def __ge__(self, path):
        return True if self.pos[0]>path.pos[0] else True if self.pos[1]>path.pos[1] else self.__eq__(path)
    
    def __eq__(self, path):
        return all(mine == his for mine, his in zip (self.pos, path.pos))