"""--------------------------------------------
cell module. Contains the Cell object (basic unit of the game),
and the Quadrant object (Organization of Cells on the board). 
Have the following classes, inheriting represented by tabs:
    Cell
    Quadrant
--------------------------------------------"""

__all__ = ['Cell', 'Quadrant']
__version__ = '1.0'
__author__ = 'David Flaity Pardo'

import functools
import pygame
import random
from settings import PATHS
from obj.paths import Path
from obj.sprite import Sprite, MultiSprite
from obj.polygons import Circle
from obj.utilities.decorators import run_async_not_pooled
from obj.utilities.surface_loader import ResizedSurface
from obj.utilities.utility_box import UtilityBox
from obj.utilities.logger import Logger as LOG

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
    def __init__(self, grid_position, real_index, position, size, canvas_size, angle=0, **params):
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
        self.text_pos = None
        self.fitness_active = False
        self.current_fitness = -1
        self.def_overlay = self.overlay
        self.fitnesses_sprites = {} #In a (overlay, text) schema
        self.index  = real_index
        self.chars  = pygame.sprite.GroupSingle()
        self.promotion = False
        self.owner  = None
        self.angle = angle
        Cell.generate(self)

    @staticmethod
    def generate(self):
        """Generate method, called in the constructor. Renders the cell text."""
        self.text_pos = str(self.text_parser())
        #self.add_text_sprite(self.id+"_text", str(self.index), text_size=tuple(x*0.75 for x in self.rect.size))    #This line when testing, easier to spot mistakes in paths and shit.
        self.add_text_sprite(self.id+"_text", self.text_pos, text_size=tuple(x*0.75 for x in self.rect.size))

    def text_parser(self):
        """Returns the matching alphabetic scheme according to our real_index attribute"""
        result_text = ''
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        my_level_index = self.pos[0]
        if my_level_index > len(alphabet):  #Won't be in a position higher than 26^2
            result_text += alphabet[my_level_index//len(alphabet)]
            my_level_index %= len(alphabet)
        result_text += alphabet[my_level_index]
        result_text += '-'+str(self.pos[-1])
        return result_text

    @run_async_not_pooled
    def show_fitness_value(self, fitness_value):
        """Shows with a small dialog the fitness value of this cell in this turn.
        Non blocking method."""
        try:
            self.set_fitness_value(fitness_value)
            self.fitness_active = True
        except pygame.error:
            LOG.log('warning', 'Couldnt modify the cell ', self.index)

    @run_async_not_pooled
    def hide_fitness_value(self):
        """Hides the small dialog with the fitness value of this cell in this turn.
        Non blocking method."""
        try:
            self.fitness_active = False
            self.overlay = self.def_overlay   #Value -1 holds the default overlay
            self.current_fitness = -1
        except pygame.error:
            LOG.log('warning', 'Couldnt modify the cell ', self.index)

    def draw(self, surface, offset=None):
        """Draws the sprite over a surface. Draws the overlay too if use_overlay is True.
        Args:
            surface (:obj: pygame.Surface): Surface to draw the Sprite. It's usually the display.
            offset (Container: int, int, default=None): Offset in pixels to be taken into account when drawing.
        """
        super().draw(surface, offset=offset)
        try:
            if self.fitness_active:
                self.fitnesses_sprites[self.current_fitness][1].draw(surface, offset=offset)
        except KeyError:
            pass

    def set_canvas_size(self, canvas_size):
        """Set a new resolution for the container element (Can be the screen itself). 
        Updates self.real_rect and self.resolution.
        Args:
            canvas_size (Tuple-> int,int): Resolution to set.
        """
        super().set_canvas_size(canvas_size)
        self.fitnesses_sprites = {} #Garbage collector, do your job!

    def set_fitness_value(self, fitness_value):
        self.current_fitness = fitness_value
        try:
            self.fitnesses_sprites[fitness_value]
        except KeyError:
            color_value = 255*fitness_value
            overlay_color = (2*(255-color_value), 2*color_value, 0.3*color_value, 0)    #This because otherwise the gradient of colors is ugly
            overlay_color = tuple(min(x, 255) for x in overlay_color) #Clipping vlaues back to 1
            overlay = Sprite.generate_overlay(self.image, overlay_color)
            value_sprite = MultiSprite('value', (0, 0), (int(self.rect.width*1.2), self.rect.height//2), self.rect.size, texture=PATHS.BROWN_SLIDER, keep_aspect_ratio=False)
            self.add_sprite(value_sprite, add_to_sprite_list=False)   #We only do this to add the absolute position and that shit
            value_sprite.add_text_sprite('fuckinvalue', round(fitness_value, 4))
            #value_sprite.set_center(self.center)
            self.fitnesses_sprites[fitness_value] = (overlay, value_sprite)
        self.overlay = self.fitnesses_sprites[fitness_value][0]

    def parse_text(self, text): #TODO CONVERT NUYMEBRS TO LETTERS AND ALL THAT SHIT
        pass

    def add_border(self, image_path):
        border = Circle('border'+str(self.index), (0, 0), self.rect.size, self.rect.size, texture=image_path)
        self.add_sprite(border)

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

    def get_char(self):
        return self.has_char()

    def has_char(self):
        return self.chars.sprite if self.chars.sprite else False

    def open_access(self, who_asking):
        return False if (self.has_ally(who_asking) or (self.has_enemy(who_asking) and not self.chars.sprite.can_die))\
        else True

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
        return Path(self.pos, self.has_ally(who_asking), self.has_enemy(who_asking), self.open_access(who_asking), self.index)
    
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
        self.bifurcation  = False

    def cell_to_str(self):
        return 'border_level: '+str(self.border_level)

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

    def __init__(self, id_, level_size, interpath_freq, *cells):
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
        Quadrant.generate(self, level_size, interpath_freq, *cells)

    @staticmethod
    def generate(self, level_size, interpath_freq, *cells):
        for cell in cells:
            self.cells.append(QuadrantCell(cell))
        self.index, self.lvl = self.get_intervals(level_size, *self.cells)
        self.sort_cells_but_good(level_size, *self.cells)
        for cell in self.cells:
            if (cell.cell.get_index()+1)%interpath_freq == 0:
                cell.bifurcation = True
            try:
                self.borders[cell.border_level].append(cell)
            except KeyError:
                self.borders[cell.border_level] = [cell]
            try:
                self.centers[cell.center_level].append(cell)
            except KeyError:
                self.centers[cell.center_level] = [cell]
            if cell.center_level > 0:
                cell.cell.promotion = True
        #self.print_state()

    @staticmethod
    def delete_overlapping_cells(*quadrants):
        for quadrant in quadrants:
            for cell in quadrant.cells:
                overlaps = False
                for other_quadrant in quadrants:
                    if quadrant is not other_quadrant:
                        for other_cell in other_quadrant.cells:
                            if cell.cell.get_real_index() == other_cell.cell.get_real_index():
                                overlaps = True
                                other_quadrant.delete_cells(other_cell)
                                break
                if overlaps:
                    quadrant.delete_cells(cell)

    def max_border_lvl(self):
        return max(x for x in self.borders.keys())

    def max_center_lvl(self):
        return max(x for x in self.centers.keys())

    def print_state(self):
        LOG.log('debug', 'Quadrant id: ', self.id, ', with the intervals: lvl ', self.lvl, ', index', self.index,\
                        '\nAll cells: ',\
                        tuple(str(cell.cell.pos)+', center_level: '+str(cell.center_level)+\
                        ', border_level: '+ str(cell.border_level)+\
                        ', bifurcation: '+str(cell.bifurcation)+'\n'\
                        for cell in self.cells),\
                        '---------------------------------')

    def parse_level(self, border_level=None, center_level=None):
        if center_level:
            center_levels = (min(x for x in self.centers.keys()), max(x for x in self.centers.keys()))
            level = center_levels[0] if center_level < center_levels[0]\
            else center_levels[1] if center_level > center_levels[1] else center_level
            return level
        elif border_level:
            border_levels = (min(x for x in self.borders.keys()), max(x for x in self.borders.keys()))
            level = border_levels[0] if border_level < border_levels[0]\
            else border_levels[1] if border_level > border_levels[1] else border_level
            return level

    def get_cell(self, border_level=None, center_level=None, random_cell=True):
        """Gets a random cell from the quadrant, returns it and deletes it.
        Args:
            zone (string, default=None):    Zone from where to get the Cell. Kinda like a restriction or to specify.
                                            Options: center, border, None.
        Returns:
            (None||:obj: Cell): A cell of the requested zone as the input says so. 
                                None if the input cant be recognized.
        """
        choosable_pool = []
        #Too low and too high levels get parsed here
        center_level = self.parse_level(center_level=center_level)
        border_level = self.parse_level(border_level=border_level)
        bifurcations = True    
        while len(choosable_pool) is 0:
            if center_level:
                choosable_pool.extend((cell for cell in self.centers[center_level] if cell.bifurcation == bifurcations))
                if not bifurcations:
                    center_level -= 1
                    if center_level < 0:
                        break
            elif border_level:
                choosable_pool.extend((cell for cell in self.borders[border_level] if cell.bifurcation == bifurcations))
                if not bifurcations:
                    border_level -= 1
                    if border_level < 0:
                        break
            else:
                break
            bifurcations = not bifurcations
        if len(choosable_pool) is 0:            #If its 0 even after all that
            choosable_pool.extend(self.cells)   #Lets just get whatever cell is still available 
        #And now we can choose
        if random_cell:
            cell = random.choice(choosable_pool)
        else:
            choosable_pool.sort(key=lambda cell: cell.cell.get_level(), reverse=True)
            cell = choosable_pool[0]    #The first one after sorting
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
        if any(index is level_size-1 for index in indexes):    #We are in the last quadrant, the one which connects to the start again
            indexes = tuple(level_size if index is 0 else index for index in indexes)
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