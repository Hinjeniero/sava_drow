#import keras
import math
import random
from obj.players import Player
from obj.utilities.decorators import time_it
class ComputerPlayer(Player):
    def __init__(self, graph, distances, level_size, name, order, sprite_size, canvas_size, ia_mode='random', infoboard=None, obj_uuid=None, avatar=None, **character_params):
        super().__init__(name, order, sprite_size, canvas_size, infoboard=infoboard, obj_uuid=obj_uuid, empty=False, avatar=avatar, **character_params)
        self.human = False
        self.ia_mode = ia_mode #alpha-beta-pruning | null-move | full blown IA with keras
        self.distances = distances 
        self.graph = graph
        self.circum_size = level_size

    def get_movement(self, fitnesses, current_map, all_cells, my_player, all_players, max_depth=5, max_nodes=100):
        #Fitnesses list of tuples like so: ((start, destiny), fitness_eval_of_movm)
        if 'random' in self.ia_mode:
            if 'half' in self.ia_mode:
                return self.generate_random_movement(fitnesses, somewhat_random=True)
            return self.generate_random_movement(fitnesses, totally_random=True)
        elif 'fitness' in self.ia_mode:
            return self.generate_random_movement(fitnesses)
        elif 'alpha' in self.ia_mode:
            if 'order' in self.ia_mode:
                return self.generate_alpha_beta_ordered(fitnesses, max_depth, max_nodes, all_cells, current_map, my_player, all_players)    
            return self.generate_alpha_beta(max_depth, max_nodes, all_cells, current_map, my_player, all_players)
        elif 'neural' in self.ia_mode:
            pass
            
    def generate_random_movement(self, fitnesses, totally_random=False, somewhat_random=False):
        if totally_random:
            return random.choice(fitnesses)[0]
        fitnesses.sort(key=lambda tup: tup[1], reverse=True)
        if somewhat_random:
            return random.choices(fitnesses, weights=list(score[1] for score in fitnesses))[0]
        else:
            only_best_movements = list(score[0] for score in fitnesses if score[1] == fitnesses[0][1])  #IF the score is the same as the best elements inn the ordered list
            return random.choice(only_best_movements)

    @time_it
    def generate_alpha_beta_ordered(self, fitnesses, max_depth, max_nodes, all_cells, current_map, current_player, all_players):   #TODO ADD ORDERING OF DESTINIES BY FITNESSES
        all_paths = {}
        #cells_with_char IS DONE LIKE THIS: A DICT WITH ONLY THE CELLS WITH A CHAR IN IT!!{INDEX: CHAR}
        cells_with_char = {cell.get_real_index(): cell.get_char() for cell in all_cells if cell.has_char()} #Creating the dict as written below
        self.minimax(current_player, cells_with_char, current_map, all_paths, [], 0, max_depth, True, -math.inf, math.inf)
        rated_movements = [(dest[0], score) for dest, score in all_paths.items()]  #TODO MAKE THIS PROPERLY, dest[0] is most likely not the way to go, we have to create a movement (source, dest) or something here
        rated_movements.sort(key=lambda dest:dest[1], reversed=True)
        print("FINAL MOVEMENTS RATED BY ALPHA BETA "+str(rated_movements))
        return rated_movements[0]

    @time_it
    def generate_alpha_beta(self, max_depth, max_nodes, all_cells, current_map, current_player, all_players):
        all_paths = {}
        #cells_with_char IS DONE LIKE THIS: A DICT WITH ONLY THE CELLS WITH A CHAR IN IT!!{INDEX: CHAR}
        cells_with_char = {cell.get_real_index(): cell.get_char() for cell in all_cells if cell.has_char()} #Creating the dict as written below
        self.minimax(current_player, cells_with_char, current_map, all_paths, [], 0, max_depth, True, -math.inf, math.inf)
        rated_movements = [(dest[0], score) for dest, score in all_paths.items()]  #TODO MAKE THIS PROPERLY, dest[0] is most likely not the way to go, we have to create a movement (source, dest) or something here
        rated_movements.sort(key=lambda dest:dest[1], reversed=True)
        print("FINAL MOVEMENTS RATED BY ALPHA BETA "+str(rated_movements))
        return rated_movements[0]

    def generate_movements(self, all_cells, current_map, my_player, my_turn=True):
        destinies = {}  #TODO current_map is paths? NO ITS NOT!
        for cell, char_inside_cell in all_cells.items():
            if char_inside_cell.owner_uuid == my_player and my_turn\
            or char_inside_cell.owner_uuid != my_player and not my_turn:
                source = cell.get_real_index()
                paths = char_inside_cell.get_paths(self.graph, self.distances, current_map, cell, self.circum_size)
                destinies[source] = tuple(path[-1] for path in paths)
        return destinies    #Return {char: (dest1,  dest2...), char2:...}

    def minimax(self, my_player, all_cells, current_map, all_paths, path, depth, max_depth, isMaximizingPlayer, alpha, beta):   #TODO MUST MODIFY CURRENT MAP TO GET DESTINIES OF ENEMY PLAYER!!
        #map_situation is: {cellindex:char/False}
        if depth is max_depth:
            value = sum(char.value for char in all_cells.values if char.owner_uuid == my_player)\
                    -sum(char.value for char in all_cells.values if char.owner_uuid != my_player)   #My chars left minus his chars left
            all_paths[path.copy()] = value  #This could also do it using only the first movm as key,since its the only one we are interested in.
            return value

        if isMaximizingPlayer:
            bestVal = -math.inf 
            #generat4e-movemtns returns a dict weith the scheme: {cell_index_source: (all destinies)}
            for source_index, destinies in self.generate_movements(all_cells, current_map, my_player).items():
                for dest_index in destinies:
                    #SIMULATE MOVEMENT
                    char_moving = all_cells[source_index]   #Starting to save variables to restore later
                    char_ded = all_cells[dest_index] if dest_index in all_cells else None
                    had_enemy = current_map[source_index].enemy
                    #Start simulating
                    current_map[source_index].ally = False
                    current_map[dest_index].ally = True
                    current_map[dest_index].enemy = False   #Simulation in current_map correct
                    del all_cells[source_index]
                    all_cells[dest_index] = char_moving     #Simulation in all_cells correct
                    path.append(dest_index)
                    #Going deeper
                    value = self.minimax(my_player, all_cells, current_map, all_paths, path, depth+1, max_depth, False, alpha, beta)
                    #UNDO SIMULATION
                    current_map[source_index].ally = True
                    current_map[dest_index].ally = False
                    current_map[dest_index].enemy = had_enemy               #Restoration in current_map correct
                    all_cells[source_index] = char_moving                   #Restoration in all_cells correct
                    if not char_ded:    del all_cells[dest_index]           #If the cell we moved to didn't had an enemy
                    else:               all_cells[dest_index] = char_ded
                    del path[-1]
                    #end of restoration
                    bestVal = max(bestVal, value) 
                    alpha = max(alpha, bestVal)
                    if beta <= alpha:
                        return bestVal
        else:
            bestVal = math.inf  
            for source_index, destinies in self.generate_movements(all_cells, current_map, my_player, False).items():
                for dest_index in destinies:
                    #Inversion of current_map
                    #SIMULATE MOVEMENT
                    char_moving = all_cells[source_index]   #Starting to save variables to restore later
                    char_ded = all_cells[dest_index] if dest_index in all_cells else None
                    had_enemy = current_map[source_index].enemy
                    #Start simulating
                    current_map[source_index].ally = False
                    current_map[dest_index].ally = True
                    current_map[dest_index].enemy = False   #Simulation in current_map correct
                    del all_cells[source_index]
                    all_cells[dest_index] = char_moving     #Simulation in all_cells correct
                    path.append(dest_index)
                    #Going deeper                    
                    value = self.minimax(my_player, all_cells, current_map, all_paths, path, depth+1, max_depth, True, alpha, beta)
                    #UNDO SIMULATION
                    current_map[source_index].ally = True
                    current_map[dest_index].ally = False
                    current_map[dest_index].enemy = had_enemy               #Restoration in current_map correct
                    all_cells[source_index] = char_moving                   #Restoration in all_cells correct
                    if not char_ded:    del all_cells[dest_index]           #If the cell we moved to didn't had an enemy
                    else:               all_cells[dest_index] = char_ded
                    del path[-1]
                    #end of restoration
                    #Re-Inversion of current_map
                    bestVal = min(bestVal, value) 
                    beta = min(beta, bestVal)
                    if beta <= alpha:
                        return bestVal