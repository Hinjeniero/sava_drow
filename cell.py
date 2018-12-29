"""--------------------------------------------
cell module. Contains the Cell object (basic unit of the game),
and the Quadrant object (Organization of Cells on the board). 
Have the following classes, inheriting represented by tabs:
    Cell
    Quadrant
--------------------------------------------"""

__all__ = ['Cell', 'Quadrant']
__version__ = '0.2'
__author__ = 'David Flaity Pardo'

import functools
import pygame
import random
from paths import Path
from utility_box import UtilityBox
from sprite import MultiSprite

@functools.total_ordering
class Cell(MultiSprite):
    """Cell class. Inherits from MultiSprite.
    It's the most basic unit of the mapping of a board (Square).
    Has the position on said board and some info, like the characters, 
    and the Sprite of the cell itself (A circle with an overblitted text).
    Attributes:
        pos (:tuple: int, int): Position of the Cell in the board. Follos a (level, index) schema.
        index (int):    Real position of the corresponding Cell. Schema: level*cells_per_lvl+index.
        chars (:obj: pygame.sprite.Group):  The characters that are currently residing on this Cell.
    
    """
    def __init__(self, grid_position, real_index, position, size, canvas_size, **params):
        """Cell constructor.
        Args:
            grid_position (:tuple: int, int):   Position of the Cell in the board. Follos a (level, index) schema.
            real_index (int):   Real position of the corresponding Cell. Schema: level*cells_per_lvl+index.
            position (:tuple: int,int): Position of the Cell in the screen. In pixels.
            size (:tuple: int,int):     Size of the Cell in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display/Screen in which to draw this Cell. In pixels.
            params (:dict:):    Dict of keywords and values as parameters to create the Circle associated.
                                Variety going from fill_color and use_gradient to fill_color."""
        params['shape'] = 'circle'
        super().__init__("cell_"+str(real_index), position, size, canvas_size, **params)
        self.pos    = grid_position
        self.index  = real_index
        self.chars  = pygame.sprite.Group()
        self.add_text_sprite(self.id+"_text", str(self.pos))

    def draw(self, surface):
        """Draws the Cell on the surface, with the index blitted on top (already done in self.image).
        If the cell is in the active state, an overlay of a random RGB color is also blitted.
        Args:
            surface (:obj: pygame.Surface): Surface in which to draw the Cell."""
        super().draw(surface)
        if self.active:
            pygame.draw.circle(surface, UtilityBox.random_rgb_color(), self.rect.center, self.rect.height//2)
            text = self.get_sprite("text")
            surface.blit(text.image, text.rect) # TODO Im almost sure that this shit will be drawn in the topleft corner

    def add_char(self, character):
        """Args:
            character (:obj: Character):    Character to add to the Cell when it arrives."""
        self.chars.add(character)

    def get_level(self):
        """Returns:
            (int):  Level/Circumference of the Cell (Positioning)."""
        return self.pos[0]
    
    def get_index(self):
        """Returns:
            (int):  Index of the Cell (Positioning)."""
        return self.pos[1]

    def get_real_index(self):
        """Returns:
            (int):  Absolute index of the Cell (Positioning) (level*level_size+index)."""
        return self.index

    def has_enemy(self, who_asking):
        """Checks if there is an enemy in the Cell (If a character is of a different player of who is asking).
        Args:
            who_asking (str):   The player who is asking this information.
        Returns:
            (boolean):  True if there is at least one enemy in the Cell."""
        for character in self.chars.sprites():
            if character.get_master() != who_asking: return True
        return False

    def has_ally(self, who_asking):
        """Checks if there is an ally in the Cell (If a character is of the same player of who is asking).
        Args:
            who_asking (str):   The player who is asking this information.
        Returns:
            (boolean):  True if there is at least one ally in the Cell."""
        for character in self.chars:
            if character.get_master() == who_asking: return True
        return False

    def to_path(self, who_asking):
        """Convers this Cell to a corresponding Path object that has the same info as this Cell (In a more static fashion).
        Args:
            who_asking (str):   The player who is requesting this casting.
        Returns:
            (:obj: Path):   A Path object with the same info as this Cell."""
        return Path(self.pos, self.has_enemy(who_asking), self.has_ally(who_asking), self.index)
    
    def __str__(self):
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
    """Quadrant class. Takes care of the organization of the Cells themselves.
    in different zones of the board. Each zone is divided between borders and centre.
    This is useful to follow a standard when dropping the different type of Characters on the board.
    The cells are organized in 4 quadrants (that follow the next scheme with cardinal points):
        quadrant 0 -> From NW to NE
        quadrant 1 -> From NE to SE
        quadrant 2 -> From SE to SW
        quadrant 3 -> From SW to NW.
    The distinction between border cells and center cells is if the existence of other Cells that surround them or not.
    If they are the last line of the quadrant (Contact with the exterior in ANY axis), it's a border. Otherwise, a center.-
    Attributes:
        id (int):   Numerical ID of this quadrant.
        cells (:obj: pygame.sprite.Group):  All the cells belonging to this quadrant.
        center (:obj: pygame.sprite.Group): The cells of this quadrant that are at the center.
        border (:obj: pygame.sprite.Group): The cells of this quadrant that are at the borders.
        lvl (:tuple: int, int): Minimum and maximum levels that the cells of this quadrant posses.
        index (:tuple: int, int):   Minimum and maximum levels that the cells of this quadrant posses.
        """

    def __init__(self, id_, *cells):
        """Quadrant constructor.
        Args:
            id (int):   Numerical ID of this quadrant.
            *cells (:obj: Cell):    All the cells belonging to this quadrant that have to be sorted out. Separated by commas."""
        self.id     = id_
        self.cells  = pygame.sprite.Group()
        self.center = pygame.sprite.Group()
        self.border = pygame.sprite.Group()
        #interval to return pseudo cells (exterior-border-center, and shit like that)
        self.lvl, self.index = self.get_intervals(*cells)
        self.sort_cells(*cells)

    def get_random_cell(self, zone=None):
        """Gets a random cell from the quadrant, returns it and deletes it.
        Args:
            zone (string, default=None):    Zone from where to get the Cell. Kinda like a restriction or to specify.
                                            Options: center, border, None.
        Returns:
            (None||:obj: Cell): A cell of the requested zone as the input says so. 
                                None if the input cant be recognized.
        """
        cell = random.choice(self.cells.sprites()) if not zone or 'Nnne' in zone.lower()\
        else random.choice(self.border.sprites()) if 'bord' in zone.lower()\
        else random.choice(self.center.sprites()) if 'cent' in zone.lower()\
        else None
        self.cells.remove(cell), self.center.remove(cell), self.border.remove(cell)
        return cell

    def get_intervals(self, *cells):
        """After analyzing all the Cells, gets the intervals for max and min levels, and max/min indexes
        of all the Cells in the quadrant.
        Args:
            *cells (:obj: Cell):    All the cells that belong to this quadrant. Separated by commas.
        Returns:
            (tuple: tuple, tuple):  Both intervals in a (minimum, maximum) schema."""
        indexes, levels = tuple([cell.get_index() for cell in cells]), tuple([cell.get_level() for cell in cells])
        return (min(indexes), max(indexes)), (min(levels), max(levels))

    def sort_cells(self, *cells):
        """Sort all the input cells and separates them in center or border. Also adds them to the belonging Group.
        The Cells have their references duplicated, since they are added to the general Cell groupm, ando to border or center.
        Args:
            *cells (:obj: Cell):    All the cells that belong to this quadrant. Separated by commas."""
        for cell in cells:
            self.cells.add(cell)
            if cell.get_level() < self.lvl[1] and cell.get_level() > self.lvl[0]\
            and cell.get_index() < self.index[1] and cell.get_index() > self.index[0]:
                self.center.add(cell)
            else:
                self.border.add(cell)
                        
