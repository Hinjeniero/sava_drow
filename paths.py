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
    MOVEMENTS = Dictionary()
    @staticmethod
    def get_movements(hash_key):
        '''returns None if the hash_key doesnt exist'''
        return Movements.MOVEMENTS.get_item(hash_key)
    
    @staticmethod
    def set_movements(existing_paths, distances, restrictions, cells_per_lvl):
        hash_key = hash(restrictions)
        if not Movements.get_movements(hash_key): #If returns None, doesnt exist
            paths = Path.all_paths_factory(existing_paths, distances, cells_per_lvl, restrictions)
            Movements.MOVEMENTS.add_item(hash_key, paths)

class Restriction(object):
    def __init__(self, max_dist=1, move_along_lvl = False, move_along_index = False):
        self.dist               = max_dist          #Max spaces that a char can move
        self.only_same_lvl      = move_along_lvl    #If only can move along the same level
        self.only_same_index    = move_along_index  #If only can move along the same index

    def __eq__(self, other):
        return self.dist == other.dist\
        and self.only_same_index == other.only_same_index\
        and self.only_same_lvl == other.only_same_lvl

    def __hash__(self):
        return hash((self.dist, self.only_same_lvl, self.only_same_index))

@functools.total_ordering
class Path(object):
    def __init__(self, grid_pos, ally, enemy, real_index):
        self.pos    = grid_pos
        self.index  = real_index
        self.ally   = ally
        self.enemy  = enemy
    
    def get_lvl(self):
        return self.pos[0]
    
    def get_index(self):
        return self.pos[1]

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
        
    @staticmethod
    def all_paths_factory(path_exists, distances, cells_per_level, restrictions):
        '''gets all the paths possible from every cell taking into account some restrictions'''
        print("RESTRICIONS DIST IS "+str(restrictions.dist))
        lvl_size        = cells_per_level
        destinations    = {}
        length          = len(path_exists[0]) #Want to know how many indexes the map has
        if restrictions.dist is 1:          #No need to check much, only if the immediate path exists
            for x in range(0, length):      
                for y in range(x, length):
                    if x is y:              continue                    #Same cell, no movmnt
                    if path_exists[x][y]:   Path.add_path(x, y, path_exists, lvl_size, destinations)
        if restrictions.dist < 2:   #If less that two but not one, infinite distance w/ restrictions (CANT HAVE NO RESTRICTIONS)
            for x in range(0, length):      
                for y in range(x, length):
                    if x is y or distances[x][y] < 0:   continue    #Same cell or not direct path, next iteration
                    if Path.check_restrictions(x, y, restrictions, distances, lvl_size):
                        Path.add_path(x, y, path_exists, lvl_size, destinations)
            
        else:   #For complex linked paths, we need a submethod
            for x in range(0, length):
                destinations[x] = Path.generate_paths(path_exists, x, restrictions)
        for key, item in destinations.items():
            LOG.log("debug", key, " -> ", item, '\n\n')
        return destinations

    @staticmethod
    def add_path(init_pos, final_pos, paths_map, lvl_length, dest_list):
        '''add the path to the destinations. Contains the try-except logic
        Completes the path itself if its needed'''
        paths = Path.complete_route(paths_map, (init_pos, final_pos), lvl_length)   #list of tuples
        for path in paths:      #In case that there are two
            try:                dest_list[init_pos].append(path)   #The list of destinations already exist for this index
            except KeyError:    dest_list[init_pos] = [path]       #It doesn't, have to create it
            path = tuple(x for x in reversed(path))
            try:                dest_list[final_pos].append(path)
            except KeyError:    dest_list[final_pos] = [path] 
    
    @staticmethod
    def check_restrictions(initial_pos, final_pos, restrictions, distances, circles):
        '''Only have to pass on one of the conditions'''
        if restrictions.only_same_lvl and initial_pos//circles is final_pos//circles:
            return True
        if restrictions.only_same_index and initial_pos%circles is final_pos%circles:
            return True
        if restrictions.only_same_index and (initial_pos<circles or final_pos<circles)\
        and distances[initial_pos][final_pos] > 0:
            return True 
        return False

    @staticmethod
    def complete_route(paths_map, incomplete_path, lvl_length):
        if 49 in incomplete_path:
            print("TRYING TI COMPLETE "+str(incomplete_path))
        '''Adds the middle cells for paths that don't have all the steps. Only valid for direct paths'''
        paths = [[]]    #Can contain one or two paths (one way or two-way if its in the same level)
        if paths_map[incomplete_path[-1]][incomplete_path[-2]]: return (incomplete_path),
        #print("COMPLETING PATH "+str(incomplete_path))
        init, end = incomplete_path[-2], incomplete_path[-1]
        if abs(init-end) >= lvl_length: #Not the same level, different ones
            index = max(init, end)
            while index is not min(init, end):
                if index >= lvl_length:
                    paths[0].append(index)
                    index -= lvl_length
                else:
                    index = min(init, end)  #The same as a abreak in this case
            paths[0].append(min(init, end)) #End of this shit
        else: #Its the same level then     
            limit = 4 if init < lvl_length and end < lvl_length else lvl_length #Separating first interior level and the exterior one  
            index = init

            while index is not end:
                paths[0].append(index)
                index = index-(limit-1) if index%lvl_length is limit-1 else index+1
            paths[0].append(end)

            paths.append([])    #two way circle, adding the list for the second 
            while index is not init:    #At this point the index should be end.
                paths[1].append(index)
                index = index-(limit-1) if index%lvl_length is limit-1 else index+1
            paths[1].append(init)

        final_paths = []
        for path in paths:
            if path[0] is not incomplete_path[-2]:  path.reverse()  #In case we did it in the reverse order
            final_paths.append(tuple(path))
        print("RESULT "+str(final_paths))
        print("----------")
        return final_paths

    @staticmethod
    def generate_paths(path_exists, initial_index, restrictions):
        '''complex paths, rough backtracking'''
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
            for dest in range(0, len(path_exists[0])):
                if dest not in path\
                and path_exists[path[-1]][dest]: to_check.append((dest, len(path)))
        LOG.log('DEBUG', "Number of iterations searching paths of distance ",restrictions.dist," -> ",iterations)
        return solutions