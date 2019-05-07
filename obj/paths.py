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
import math
from obj.utilities.logger import Logger as LOG
from obj.utilities.synch_dict import Dictionary
from obj.utilities.decorators import time_it

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
    def __init__(self, grid_pos, ally, enemy, access, real_index):
        self.pos    = grid_pos
        self.index  = real_index
        self.ally   = ally
        self.enemy  = enemy
        self.access = access
    
    def is_empty(self):
        """Returns:
            (boolean):  True if there are not characters in this index."""
        return True if not self.ally and not self.enemy else False

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

    def accessible(self):
        return self.access

    def copy(self):
        return Path(self.pos, self.ally, self.enemy, self.access, self.index)

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
    #@time_it
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
        #print("RESTRICIONS DIST IS "+str(restrictions.dist))  TODO delete
        destinations    = {}
        length          = len(graph[0]) #Want to know how many indexes the map has
        if restrictions.dist is 1:          #No need to check much, only if the immediate path exists
            for x in range(0, length):      
                for y in range(x, length):
                    if x is y:        continue                    #Same cell, no movmnt
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
        '''for key, item in destinations.items():
            LOG.log("debug", key, " -> ", item, '\n\n')'''
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
    #@time_it
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
        #LOG.log('DEBUG', "Number of iterations searching paths of distance ",restrictions.dist," -> ",iterations)
        return solutions

class PathAppraiser(object):
    @staticmethod
    @time_it
    def rate_path(start_pos, possible_destinies, current_map, character):
        pass

    @staticmethod
    #@time_it
    def rate_movement_lite(start_pos, possible_destinies, paths_graph, distances, current_map, all_cells, level_size):
        """Returns a tuple with indexes of the destinies, and a fitness going from 0 to 1. Super light method for fast computing!"""

    @staticmethod
    #@time_it
    def rate_movement(start_pos, possible_destinies, paths_graph, distances, current_map, all_cells, level_size):
        """Returns a tuple with indexes of the destinies, and a fitness going from 0 to 1."""
        fitnesses = {}
        character = next(cell.get_char() for cell in all_cells if cell.get_real_index() == start_pos)
        #TODO Create the algorithm itself, since the helpiung values have been written already
        danger_multiplier = PathAppraiser.get_danger_multiplier(character, all_cells)
        start_danger = PathAppraiser.get_danger_in_position(start_pos, character.owner_uuid, paths_graph, distances, all_cells, level_size)*danger_multiplier
        bait_ratios = {}
        destinies_danger = {}
        kill_values = {}
        for index in possible_destinies:
            destiny_cell = next(cell for cell in all_cells if index == cell.get_real_index())
            kill_values[index] = PathAppraiser.get_kill_value(destiny_cell, character)
            destinies_danger[index] = PathAppraiser.get_danger_in_position(index, character.owner_uuid, paths_graph, distances, all_cells, level_size)
            destinies_danger[index] *= danger_multiplier# if kill_values[index] != 0 else (danger_multiplier*2)

            current_map[start_pos].ally = False #This to get proper paths to this method to get a useful bait result
            bait_ratios[index] = PathAppraiser.get_bait_value(character, index, paths_graph, distances, current_map, all_cells, level_size)
            current_map[start_pos].ally = True
            '''LOG.log('info', '---------------INDEX CELL RESULTS ', index, '-------------')
            LOG.log('info', 'Danger multiplier ', danger_multiplier)
            LOG.log('info', 'Start pos danger ', start_danger," vs destiny danger: ", destinies_danger[index])
            LOG.log('info', 'Bait value ', bait_ratios[index])
            LOG.log('info', 'Kill value ', kill_values[index])
            LOG.log('info', 'Start pos danger ', start_danger," vs destiny danger: ", destinies_danger[index])
            LOG.log('info', "IN TANH VALUES: bait ", math.tanh(bait_ratios[index]), ", danger difference: ", math.tanh(destinies_danger[index]/start_danger), ", kill: ", math.tanh(kill_values[index]))
            print("----------------------------------")'''
            fitness = 0.6*(math.tanh(kill_values[index]))+0.6*(math.tanh(destinies_danger[index]/start_danger))+0.2*(math.tanh(bait_ratios[index]))
            #print("fitness for "+str(index)+" is "+str(fitness))
            fitnesses[index] = min(fitness, 1)
            fitnesses[index] = max(fitness, 0)
        return fitnesses

    @staticmethod
    def invert_map(self, current_map):
        for path_obj in current_map.values():
            if path_obj.has_ally():
                path_obj.enemy = True
                path_obj.ally = False
            elif path_obj.has_enemy():
                path_obj.enemy = False
                path_obj.ally = True

    @staticmethod
    def generate_current_map(all_cells, player):
        """This code is redundant, but oh well"""
        map_for_player = {}
        for cell in all_cells:
            map_for_player[cell.get_real_index()]=cell.to_path(player)
        return map_for_player 

    @staticmethod
    def get_kill_value(destination, my_char):
        if destination.has_char() and (destination.has_char().owner_uuid != my_char.owner_uuid):
            return 1*math.sqrt(destination.has_char().value/my_char.value)
        return 0 

    @staticmethod
    def get_danger_multiplier(my_char, all_cells):
        ratio = 1
        my_type_of_char = 0
        essential_pieces = 0 
        all_value = 0
        for cell in all_cells:
            if cell.has_char() and cell.has_char().owner_uuid == my_char.owner_uuid:
                my_type_of_char += 1 if my_char.get_type() == cell.has_char().get_type() else 0
                essential_pieces += 1 if cell.has_char().essential else 0
                all_value += cell.has_char().value
        ratio *= (my_char.value/my_type_of_char) * (my_char.value/all_value) * (1 if not my_char.essential else my_char.value/essential_pieces if essential_pieces>1 else 999)
        return ratio

    @staticmethod
    def get_danger_in_position(cell_index, player, graph, distances, all_cells, level_size):
        """From 0 to 1. 0 worst case, 1 no danger whatsoever"""
        danger_value = 1
        enemies_ready = 0
        for cell in all_cells:
            if cell.get_char() and cell.get_char().owner_uuid != player:
                enemy_map = PathAppraiser.generate_current_map(all_cells, cell.get_char().owner_uuid)
                enemy_destinies = tuple(path[-1] for path in cell.get_char().get_paths(graph, distances, enemy_map, cell.get_real_index(), level_size))
                if cell_index in enemy_destinies:   #If there is another char of another player that can move here
                    enemies_ready += 1
        return danger_value/(enemies_ready+1)

    @staticmethod
    def get_bait_value(my_char, destination, graph, distances, current_map, all_cells, level_size): #TODO CHECK THIS; NOT WORKIKNG PROPERLY. GOOD WAY TO CHECK THIS IS WITH THYE 2 WIZARDS IN THE CENTER
        bait_value = 1
        vengeful_allies = 0
        baited_enemy_values = []
        has_enemy = current_map[destination].enemy  #So the paths of the allies are correct, as if its an enemy here after killing our bait char.
        current_map[destination].enemy = True       #So the paths of the allies are correct, as if its an enemy here after killing our bait char.
        for cell in all_cells:
            if cell.get_char():
                if cell.get_char().owner_uuid == my_char.owner_uuid:
                    ally_destinies = tuple(path[-1] for path in cell.get_char().get_paths(graph, distances, current_map, cell.get_real_index(), level_size))
                    if destination in ally_destinies:
                        vengeful_allies += 1
                else:
                    enemy_map = PathAppraiser.generate_current_map(all_cells, cell.get_char().owner_uuid)
                    enemy_destinies = tuple(path[-1] for path in cell.get_char().get_paths(graph, distances, enemy_map, cell.get_real_index(), level_size))
                    if destination in enemy_destinies:
                        baited_enemy_values.append(cell.get_char().value)
        current_map[destination].enemy = has_enemy #Restoring the map of paths object
        if vengeful_allies == 0 or len(baited_enemy_values) == 0 or my_char.essential:
            return 0
        bait_value *= (min(baited_enemy_values)/my_char.value)*math.sqrt(vengeful_allies)   #Usually the opponent will use the less valuable piece to kill our bait
        return bait_value