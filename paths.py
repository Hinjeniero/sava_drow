"""--------------------------------------------
paths module. Contains classes and objects that take care of all
the path generating, saving and responding to requests of the possible paths for some inputs.
The classes in this module are:
    Movements
    Restriction
    Path
--------------------------------------------"""

__all__ = ['Movements', 'Restriction', 'Path']
__version__ = '0.8'
__author__ = 'David Flaity Pardo'

import os
import functools
from logger import Logger as LOG
from synch_dict import Dictionary

GAME_FOLDER = os.path.dirname(__file__)
IMG_FOLDER = os.path.join(GAME_FOLDER, 'img')
SOUND_FOLDER = os.path.join(GAME_FOLDER, 'sounds')

class Movements(object):
    """Movement class. Only contains static methods. Generates, contains and delivers
    all the possible movements of the map, depending on the Restriction.
    General class Atributes:
        MOVEMENTS (:obj: Dictionary):   Thread-safe dictionary that functions as a LUT table
                                        for all the requested movements with a Restriction. 
                                        Key: hash(Restriction), Item: All the possible movements
                                        dor all the cells with that Restriction in place."""
    MOVEMENTS = Dictionary()
    @staticmethod
    def get_movements(hash_key):
        """ Get the all the possible movements for all the cells, for a Restriction.
        Args:
            hash_key (hash):    Hash key of the Restriction to search.
        Returns:
            (None||:dict:): None if there is no paths saved for that Restriction.
                            A list with all the possible paths if the hash is found."""
        return Movements.MOVEMENTS.get_item(hash_key)
    
    @staticmethod
    def set_movements(graph, distances, level_size, restrictions):
        """Generates all the movements for all the cells based on the input restrictions.
        If they exist already this method does nothing.
        Args:
            graph (:obj: numpy.Matrix:boolean): Graph with all the directly connected cells (distance=1).
            distances (:obj: numpy:int):    Graph of distances between cells connected (without changing direction).
            level_size (int):  Number of cell in one circumference.
            movement_restriction (:obj: Restriction):   The movement restriction to which to set the possible destinies."""
        hash_key = hash(restrictions)
        if not Movements.get_movements(hash_key): #If returns None, doesnt exist
            paths = Path.all_paths_factory(graph, distances, level_size, restrictions)
            Movements.MOVEMENTS.add_item(hash_key, paths)

class Restriction(object):
    """Restriction class. Contains attributes that symbolizes and describe some
    of the restrictions that can exist in a movement. This class is useful for Character,
    and for Path.
    Attributes:
        dist (int): Maximum distance that can be traveled.
        only_same_lvl (boolean):    Movement only allowed along the same circumference.
        only_same_index (boolean):  Movement only allowed between the same index (If there are interpaths).
    """

    def __init__(self, max_dist=1, move_along_lvl=False, move_along_index=False):
        """Restriction constructor. If both booleans are True, movement can be performed in those two ways.
        Args:
            max_dist (int, default=1):  Maximum distance that can be traveled in just one turn.
            move_along_lvl (boolean, default=False):    If only movement to positions OF THE SAME CIRCUMFERENCE
                                                        is allowed.
            move_along_index (boolean, default=False):  If only movement to positions OF THE SAME INDEX
                                                        but DIFFERENT CIRCUMFERENCE is allowed (If a path between exists).
        """
        self.dist               = max_dist
        self.only_same_lvl      = move_along_lvl
        self.only_same_index    = move_along_index

    def __eq__(self, other):
        return self.dist == other.dist\
        and self.only_same_index == other.only_same_index\
        and self.only_same_lvl == other.only_same_lvl

    def __hash__(self):
        return hash((self.dist, self.only_same_lvl, self.only_same_index))

@functools.total_ordering
class Path(object):
    """Path class. Takes care of all the generating of paths and routes.
    Also, with its attributes, it can be a pretty handy version of Cell, with important info
    that is useful at the time of discarding possible destinies, due to the different Restriction 
    between the Characters.
    Attributes:
        pos (:tuple: int, int): Position of the Cell corresponding to this path. Schema (level, index).
        index (int):    Real position of the corresponding Cell. Schema: level*cells_per_lvl+index.
        ally (boolean): True if there are allies in this Path. (Depends on which player asks).
        enemy (boolean):True if there are enemies in this Path. (Depends on which player asks).
    """
    def __init__(self, grid_pos, ally, enemy, real_index):
        self.pos    = grid_pos
        self.index  = real_index
        self.ally   = ally
        self.enemy  = enemy
    
    def get_lvl(self):
        """Returns:
            (int): Circumference of the corresponding Cell."""
        return self.pos[0]
    
    def get_index(self):
        """Returns:
            (int): Index of the corresponding Cell."""
        return self.pos[1]

    def has_enemy(self):
        """Returns:
            (boolean): True if enemies are here."""
        return self.enemy
        
    def has_ally(self):
        """Returns:
            (boolean): True if allies are here."""
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
        
    @staticmethod
    def all_paths_factory(graph, distances, level_size, restrictions):
        """Generates all the possible paths from every cell, taking into account some restrictions.
        Its a general method that works for pretty much everything. 
        The generation is different if the distance is only 1, if its unlimited BUT with restrictions,
        or if its greater than 1 with no restrictions (Uses another method to do this).
        Args:
            graph (:obj: numpy.Matrix:boolean): Graph with all the directly connected cells (distance=1).
            distances (:obj: numpy:int):    Graph of distances between cells connected (without changing direction).
            level_size (int):  Number of cell in one circumference.
            restrictions (:obj: Restriction):   The movement restriction to which to set the possible destinies.
        Returns:
            (:dict: key=cell.index, item=:list:tuple):  A dict in which for every cell(Key), contains all the possible
                                                        destinies in a list of tuples (Those tuples are the complete paths).
        """
        print("RESTRICIONS DIST IS "+str(restrictions.dist))
        destinations    = {}
        length          = len(graph[0]) #Want to know how many indexes the map has
        if restrictions.dist is 1:          #No need to check much, only if the immediate path exists
            for x in range(0, length):      
                for y in range(x, length):
                    if x is y:              continue                    #Same cell, no movmnt
                    if graph[x][y]:   Path.add_path(x, y, graph, level_size, destinations)
        if restrictions.dist < 2:   #If less that two but not one, infinite distance w/ restrictions (CANT HAVE NO RESTRICTIONS)
            for x in range(0, length):      
                for y in range(x, length):
                    if x is y or distances[x][y] < 0:   continue    #Same cell or not direct path, next iteration
                    if Path.check_restrictions(x, y, restrictions, distances, level_size):
                        Path.add_path(x, y, graph, level_size, destinations)
            
        else:   #For complex linked paths, we need a submethod
            for x in range(0, length):
                destinations[x] = Path.generate_paths(graph, x, restrictions)
        for key, item in destinations.items():
            LOG.log("debug", key, " -> ", item, '\n\n')
        return destinations

    @staticmethod
    def add_path(init_pos, end_pos, paths_map, level_size, dest_list):
        """Adds the path (init_pos, end_pos) to the destinations array that is passed as an argument.
        Completes the path itself if its needed (There are empty steps in the middle of the route).
        Args:
            init_pos (int): Initial index of the route/path (The start).
            end_pos (int): Final index of the route/path (The end)-
            paths_map (:obj: numpy.Matrix:boolean): Graph with all the directly connected cells (distance=1).
            level_size (int):  Number of cell in one circumference.
            dest_list (:dict:):The structure to which to add the path (completed if needed)."""
        paths = Path.complete_route(paths_map, (init_pos, end_pos), level_size)   #list of tuples
        for path in paths:      #In case that there are two
            try:                dest_list[init_pos].append(path)   #The list of destinations already exist for this index
            except KeyError:    dest_list[init_pos] = [path]       #It doesn't, have to create it
            path = tuple(x for x in reversed(path))
            try:                dest_list[end_pos].append(path)
            except KeyError:    dest_list[end_pos] = [path] 
    
    @staticmethod
    def check_restrictions(init_pos, end_pos, restrictions, distances, level_size):
        """Check the input restrictions to check if a movement between two indexes is allowed.
        Only have to pass on one of the conditions of the restriction.
        Args:
            init_pos (int): Initial index of the route/path (The start).
            end_pos (int): Final index of the route/path (The end)-
            restrictions (:obj: Restriction):   The movement restrictions to check.
            distances (:obj: numpy:int):    Graph of distances between cells connected (without changing direction).            
            level_size (int):  Number of cell in one circumference.
        Returns:
            (boolean):  True if the movement between the two input indexes is allowed with the input restrictions.
        """
        if restrictions.only_same_lvl and init_pos//level_size is end_pos//level_size:
            return True
        if restrictions.only_same_index and init_pos%level_size is end_pos%level_size:
            return True
        if restrictions.only_same_index and (init_pos<level_size or end_pos<level_size)\
        and distances[init_pos][end_pos] > 0:   #If this path exists (distance > 0)
            return True 
        return False

    @staticmethod
    def complete_route(graph, incomplete_path, level_size):
        """Adds the middle cells/steps for paths/routes that don't have them/are incomplete. Only valid for direct paths.
        Can also add another route in the opposite way (Being the map a circle, we need a route for each direction).
        Args:
            graph (:obj: numpy.Matrix:boolean): Graph with all the directly connected cells (distance=1).
            incomplete_path (:tuple: int):  Path that needs to fill the middle cells/steps/indexes of a route.
            level_size (int):  Number of cell in one circumference.
        Returns:
            (:tuple:int):   A tuple containing the complete route. Can also have two tuples with the complete route
                            in both directions (map==Circle).
        """
        paths = [[]]    #Can contain one or two paths (one way or two-way if its in the same level)
        if graph[incomplete_path[-1]][incomplete_path[-2]]: return (incomplete_path),
        init, end = incomplete_path[-2], incomplete_path[-1]
        if abs(init-end) >= level_size: #Not the same level, different ones
            index = max(init, end)
            while index is not min(init, end):
                if index >= level_size:
                    paths[0].append(index)
                    index -= level_size
                else:
                    index = min(init, end)  #The same as a abreak in this case
            paths[0].append(min(init, end)) #End of this shit
        else: #Its the same level then     
            limit = 4 if init < level_size and end < level_size else level_size #Separating first interior level and the exterior one  
            index = init

            while index is not end:
                paths[0].append(index)
                index = index-(limit-1) if index%level_size is limit-1 else index+1
            paths[0].append(end)

            paths.append([])    #two way circle, adding the list for the second 
            while index is not init:    #At this point the index should be end.
                paths[1].append(index)
                index = index-(limit-1) if index%level_size is limit-1 else index+1
            paths[1].append(init)

        final_paths = []
        for path in paths:
            if path[0] is not incomplete_path[-2]:  path.reverse()  #In case we did it in the reverse order
            final_paths.append(tuple(path))
        return final_paths

    @staticmethod
    def generate_paths(graph, initial_index, restrictions):
        """Generates all the possible routes from an initial index.
        Uses a backtracking approach, and works for every distance and for linked spaces too.
        Don't take into account any restrictions that are not the max distance.
        Args:
            graph (:obj: numpy.Matrix:boolean): Graph with all the directly connected cells (distance=1).
            init_pos (int): Initial index of the route/path (The start).
            restrictions (:obj: Restriction):   The movement restrictions to check (Only uses max_dist).
        Returns:
            (:list: tuple): List containing all the possible routes that start from the initial_index.
                            Each route is a tuple with all the indexes that form the path.
        """
        max_dist    = restrictions.dist+1
        solutions   = []
        path        = []
        to_check    = [(initial_index, 0)]  #sturcture of (index, step_of_this_index)
        iterations  = 0
        while len(to_check) > 0:
            iterations += 1
            path.append(to_check.pop(-1)[0])
            if len(path) is max_dist:
                solutions.append(tuple(path))                       #Add solution
                if len(to_check) > 0:               del path[to_check[-1][1]:]  #Restore path to the last bifurcation
                continue
            #Adding destinations to to_check if there is an existant path with the current index (path last index)
            for dest in range(0, len(graph[0])):
                if dest not in path\
                and graph[path[-1]][dest]: to_check.append((dest, len(path)))
        LOG.log('DEBUG', "Number of iterations searching paths of distance ",restrictions.dist," -> ",iterations)
        return solutions