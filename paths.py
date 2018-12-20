import os, functools
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
        print("KEYS OF THIS SHIT "+str(Movements.MOVEMENTS.dict.keys()))
        hash_key = hash(restrictions)
        if not Movements.get_movements(hash_key): #If returns None, doesnt exist
            paths = Path.all_paths_factory(existing_paths, distances, cells_per_lvl, restrictions)
            Movements.MOVEMENTS.add_item(hash_key, paths)

class Restrictions(object):
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
        lvl_size        = cells_per_level
        destinations    = {}
        length          = len(path_exists[0]) #Want to know how many indexes the map has
        if restrictions.dist is 1:          #No need to check much, only if the immediate path exists
            for x in range(0, length):      
                for y in range(x, length):
                    if x is y:              continue                    #Same cell, no movmnt
                    if path_exists[x][y]:   Path.add_path(x, y, destinations)
        if restrictions.dist < 2:   #If less that two but not one, infinite distance w/ restrictions (CANT HAVE NO RESTRICTIONS)
            for x in range(0, length):      
                for y in range(x, length):
                    if x is y or distances[x][y] < 0:   continue    #Same cell or not direct path, next iteration
                    if Path.check_restrictions(x, y, restrictions, distances, lvl_size):
                        Path.add_path(x, y, destinations)
        else:   #For complex paths, we need a submethod
            for x in range(0, length):
                destinations[x] = Path.generate_paths(path_exists, x, restrictions)
        return destinations

    @staticmethod
    def add_path(init_pos, final_pos, dest_list):
        '''add the path to the destinations. Contains the try-except logic'''
        try:                dest_list[init_pos].append((init_pos, final_pos))   #The list of destinations already exist for this index
        except KeyError:    dest_list[init_pos] = [(init_pos, final_pos)]       #It doesn't, have to create it
        try:                dest_list[final_pos].append((final_pos, init_pos))
        except KeyError:    dest_list[final_pos] = [(final_pos, init_pos)] 
    
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
                solutions.append(path.copy())                       #Add solution
                if len(to_check) > 0:               del path[to_check[-1][1]:]  #Restore path to the last bifurcation
                continue
            #Adding destinations to to_check if there is an existant path with the current index (path last index)
            for dest in range(0, len(path_exists[0])):
                if dest not in path\
                and path_exists[path[-1]][dest]: to_check.append((dest, len(path)))
        LOG.log('DEBUG', "Number of iterations searching paths of distance ",restrictions.dist," -> ",iterations)
        return solutions