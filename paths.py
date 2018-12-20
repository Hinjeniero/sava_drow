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
    def set_movements(existing_paths, restrictions, cells_per_lvl):
        hash_key = hash(restrictions)
        if not Movements.get_movements(hash_key): #If returns None, doesnt exist
            paths = Path.all_paths_factory(existing_paths, cells_per_lvl, restrictions)
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
    def all_paths_factory(path_exists, cells_per_level, restrictions):
        lvl_size        = cells_per_level
        destinations    = {}
        length          = len(path_exists[0]) #Want to know how many indexes the map has
        if restrictions.dist is 1:          #No need to check much, only if the immediate path exists
            for x in range(0, length):      
                for y in range(x, length):
                    if x is y:              continue                    #Same cell, no movmnt
                    if path_exists[x][y]:
                        try:                destinations[x].append((y, x))   #The list of destinations already exist for this index
                        except KeyError:    destinations[x] = [(y, x)]       #It doesn't, have to create it
                        try:                destinations[y].append((x, y))
                        except KeyError:    destinations[y] = [(x, y)] 
        if restrictions.dist < 2:   #If less that two but not one, infinite distance w/ restrictions
            for x in range(0, length):      
                for y in range(x, length):
                    if x is y:              continue    #Same cell not movmnt
                    if restrictions.only_same_index:    #If the dest cell doesn't abide by this restriction
                        if not path_exists[x][y] or x%lvl_size is not y%lvl_size:
                            continue                    #Next iteration
                    if restrictions.only_same_lvl:      #If the dest cell doesn't abide by this restriction
                        if x//lvl_size is not y//lvl_size:    
                            continue                    #Next iteration
                    #All conditions cleared, its a possible destiny
                    try:                destinations[x].append((y, x))   #The list of destinations already exist for this index
                    except KeyError:    destinations[x] = [(y, x)]       #It doesn't, have to create it
                    try:                destinations[y].append((x, y))
                    except KeyError:    destinations[y] = [(x, y)] 
        else:                       #For complex paths, we need a submethod
            for x in range(0, length):
                destinations[x] = Path.generate_paths(path_exists, x, restrictions)
        return destinations

    @staticmethod
    def generate_paths(path_exists, initial_index, restrictions):
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