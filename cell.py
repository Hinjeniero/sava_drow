import functools, pygame, random
from paths import Path

@functools.total_ordering
class Cell(pygame.sprite.Sprite):
    def __init__(self, circle, grid_position, real_index):
        super().__init__()
        self.image  = circle.image
        self.rect   = circle.rect
        self.center = circle.center
        self.pos    = grid_position
        self.index  = real_index
        self.chars  = pygame.sprite.Group()

    def add_char(self, character):
        self.chars.add(character)

    def get_level(self):
        return self.pos[0]
    
    def get_index(self):
        return self.pos[1]

    def has_enemy(self, who_asking):
        for character in self.chars.sprites():
            if character.get_master() != who_asking: return True
        return False

    def has_ally(self, who_asking):
        for character in self.chars:
            if character.get_master() == who_asking: return True
        return False

    def to_path(self, who_asking):
        return Path(self.pos, self.has_enemy(who_asking), self.has_ally(who_asking), self.index)
    
    def __str__(self): #TODO provisional method
        return "[Cell "+str(self.pos)+" | Chars: "+str(len(self.chars))+"]"

    def __lt__(self, cell):
        return self.pos[0]<cell.pos[0] if self.pos[0] != cell.pos[0] else self.pos[1]<cell.pos[1]

    def __le__(self, cell):
        return True if self.pos[0]<cell.pos[0] else True if self.pos[1]<cell.pos[1] else self.__eq__(cell)

    def __gt__(self, cell):
        return self.pos[0]>cell.pos[0] if self.pos[0] != cell.pos[0] else self.pos[1]>cell.pos[1]
    
    def __ge__(self, cell):
        return True if self.pos[0]>cell.pos[0] else True if self.pos[1]>cell.pos[1] else self.__eq__(cell)
    
    def __eq__(self, cell):
        return all(mine == his for mine, his in zip (self.pos, cell.pos))

    def __hash__(self):
        return hash(self.pos)

class Quadrant(object):
    def __init__(self, id_, *cells):
        self.id     = id_
        self.center = pygame.sprite.Group()
        self.border = pygame.sprite.Group()
        self.lvl    = (0, 0)        #interval to return pseudo cells (exterior-border-center, and shit like that)
        self.index  = (0, 0)
        self.get_intervals()
        self.sort_cells()

    def get_cell(self):
        pass

    def get_random_cell(self):
        pass

    def get_intervals(self, *cells):
        indexes, levels = tuple([cell.get_index() for cell in cells]), tuple([cell.get_level() for cell in cells])
        self.lvl, self.index = (min(indexes), max(indexes)), (min(levels), max(levels))

    def sort_cells(self, *cells):
        for cell in cells:  self.__sort_cell(cell, *cells)
    
    def __sort_cell(self, cell, *cells):
        less_lvl, more_lvl, less_index, more_index = False, False, False, False
        for other_cell in cells:
            if all(less_lvl, more_lvl, less_index, more_index): 
                self.center.add(cell)
                return
            elif other_cell is not cell:
                if other_cell.get_level() < cell.get_level():   less_lvl    = True
                elif other_cell.get_level() > cell.get_level(): more_lvl    = True
                if other_cell.get_index() < cell.get_index():   less_index  = True
                elif other_cell.get_index() > cell.get_index(): more_index  = True
        self.border.add(cell)
                        
