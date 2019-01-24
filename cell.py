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
from polygons import Circle
from logger import Logger as LOG

@functools.total_ordering
class Cell(Circle):
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
        params['overlay'] = False
        super().__init__("cell_"+str(real_index), position, size, canvas_size, **params)
        self.pos    = grid_position
        self.index  = real_index
        self.chars  = pygame.sprite.GroupSingle()
        Cell.generate(self)

    @staticmethod
    def generate(self):
        self.add_text_sprite(self.id+"_text", str(self.pos[0])+"-"+str(self.pos[1]), text_size=tuple(x*0.75 for x in self.rect.size))

    def draw(self, surface):
        """Draws the Cell on the surface, with the index blitted on top (already done in self.image).
        If the cell is in the active state, an overlay of a random RGB color is also blitted.
        Args:
            surface (:obj: pygame.Surface): Surface in which to draw the Cell."""
        super().draw(surface)
        if self.active:
            pygame.draw.circle(surface, UtilityBox.random_rgb_color(), self.rect.center, self.rect.height//2)

    def add_char(self, character):
        """Args:
            character (:obj: Character):    Character to add to the Cell when it arrives."""
        if not self.chars.has(character):
            self.chars.add(character)

    def set_hover(self, hover):
        super().set_hover(hover)
        if self.chars.sprite and self.chars.sprite.active:
            self.chars.sprite.set_hover(hover)

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

    def has_char(self):
        return self.chars.sprite if self.chars.sprite else False

    def has_enemy(self, who_asking):
        """Checks if there is an enemy in the Cell (If a character is of a different player of who is asking).
        Used to convert to path object.
        Args:
            who_asking (str):   The player who is asking this information.
        Returns:
            (boolean):  True if there is at least one enemy in the Cell."""
        for character in self.chars.sprites():
            if character.get_master() != who_asking: return True
        return False

    def has_ally(self, who_asking):
        """Checks if there is an ally in the Cell (If a character is of the same player of who is asking).
        Used to convert to path object.
        Args:
            who_asking (str):   The player who is asking this information.
        Returns:
            (boolean):  True if there is at least one ally in the Cell."""
        for character in self.chars:
            if character.get_master() == who_asking: return True
        return False

    def is_empty(self):
        return True if not self.chars.sprite else False

    def empty_cell(self):
        self.chars.empty()

    def kill_char(self):
        sprite = self.chars.sprite
        self.chars.empty()
        return sprite

    def to_path(self, who_asking):
        """Convers this Cell to a corresponding Path object that has the same info as this Cell (In a more static fashion).
        Args:
            who_asking (str):   The player who is requesting this casting.
        Returns:
            (:obj: Path):   A Path object with the same info as this Cell."""
        return Path(self.pos, self.has_ally(who_asking), self.has_enemy(who_asking), self.index)
    
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

class QuadrantCell(object):
    def __init__(self, cell):
        self.cell = cell
        self.center_level = 0
        self.border_level = 0

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

    def __init__(self, id_, level_size, *cells):
        """Quadrant constructor.
        Args:
            id (int):   Numerical ID of this quadrant.
            *cells (:obj: Cell):    All the cells belonging to this quadrant that have to be sorted out. Separated by commas."""
        self.id     = id_
        self.cells  = []
        self.borders = {}
        self.centers = {}
        #interval to return pseudo cells (exterior-border-center, and shit like that)
        self.index  = None
        self.lvl    = None
        Quadrant.generate(self, level_size, *cells)
        

    @staticmethod
    def generate(self, level_size, *cells):
        for cell in cells:
            self.cells.append(QuadrantCell(cell))
        self.index, self.lvl = self.get_intervals(level_size, *self.cells)
        self.sort_cells_but_good(level_size, *self.cells)
        for cell in self.cells:
            try:
                self.borders[cell.border_level].append(cell)
            except KeyError:
                self.borders[cell.border_level] = [cell]
            try:
                self.centers[cell.center_level].append(cell)
            except KeyError:
                self.centers[cell.center_level] = [cell]
        self.print_state()

    def print_state(self):
        LOG.log('debug', 'Quadrant id: ', self.id, ', with the intervals: lvl ', self.lvl, ', index', self.index,\
                        '\nAll cells: ',\
                        tuple(str(cell.cell.pos)+', center_level: '+str(cell.center_level)+', border_level: '+ str(cell.border_level)+'\n'\
                        for cell in self.cells),\
                        '---------------------------------')

    def get_random_cell(self, border_level=None, center_level=None):
        """Gets a random cell from the quadrant, returns it and deletes it.
        Args:
            zone (string, default=None):    Zone from where to get the Cell. Kinda like a restriction or to specify.
                                            Options: center, border, None.
        Returns:
            (None||:obj: Cell): A cell of the requested zone as the input says so. 
                                None if the input cant be recognized.
        """
        if center_level:
            #Parsing center level
            center_levels = (min(x for x in self.centers.keys()), max(x for x in self.centers.keys()))
            level = center_levels[0] if center_level < center_levels[0]\
            else center_levels[1] if center_level > center_levels[1] else center_level
            #Returning the cell
            cell = random.choice(self.centers[level])
        elif border_level:
            #parsing border level
            border_levels = (min(x for x in self.borders.keys()), max(x for x in self.borders.keys()))
            level = border_levels[0] if border_level < border_levels[0]\
            else border_levels[1] if border_level > border_levels[1] else border_level
            #Returning the cell
            cell = random.choice(self.centers[level])
        else:
            cell = random.choice(self.cells)
        self.delete_cells(cell)
        return cell.cell

    def delete_cells(self, *cells):
        for cell in cells:
            self.cells.remove(cell)
            self.borders[cell.border_level].remove(cell)
            self.centers[cell.center_level].remove(cell)

    def get_intervals(self, level_size, *cells):
        """After analyzing all the Cells, gets the intervals for max and min levels, and max/min indexes
        of all the Cells in the quadrant.
        Args:
            *cells (:obj: Cell):    All the cells that belong to this quadrant. Separated by commas.
        Returns:
            (tuple: tuple, tuple):  Both intervals in a (minimum, maximum) schema."""
        offset = level_size//8
        indexes, levels = tuple([(cell.cell.get_index()+offset)%level_size for cell in cells]), tuple([cell.cell.get_level() for cell in cells])
        return (min(indexes), max(indexes)), (min(levels), max(levels))


    def sort_cells_but_good(self, level_size, *cells):
        while True:
            for cell in cells:
                cell.border_level += 1
            indexes, lvls = self.get_intervals(level_size, *cells)
            center_cells = self.sort_cells(level_size, lvls, indexes, *cells)
            for cell in center_cells:
                cell.center_level += 1
            cells = center_cells
            if len(cells) is 0:
                break

    def sort_cells(self, level_size, lvl_interval, index_interval, *cells):
        """Sort all the input cells and separates them in center or border. Also adds them to the belonging Group.
        The Cells have their references duplicated, since they are added to the general Cell groupm, ando to border or center.
        Args:
            *cells (:obj: Cell):    All the cells that belong to this quadrant. Separated by commas."""
        center = []
        offset = level_size//8
        for cell in cells:
            #if cell.get_level() < self.lvl[1] and cell.get_level() > self.lvl[0]\ #This makes the outside-cells border too (altho correct, we dont want that)
            if cell.cell.get_level() > lvl_interval[0]\
            and (cell.cell.get_index()+offset)%level_size < index_interval[1]\
            and (cell.cell.get_index()+offset)%level_size > index_interval[0]:
                center.append(cell)
        return center