#import keras
import math
import random
from obj.players import Player
class ComputerPlayer(Player):
    def __init__(self, graph, distances, level_size, name, order, sprite_size, canvas_size, ia_mode='random', infoboard=None, obj_uuid=None, avatar=None, **character_params):
        super().__init__(name, order, sprite_size, canvas_size, infoboard=infoboard, obj_uuid=obj_uuid, empty=False, avatar=avatar, **character_params)
        self.human = False
        self.ia_mode = ia_mode #alpha-beta-pruning | null-move | full blown IA with keras
        self.distances = distances 
        self.graph = graph
        self.circum_size = level_size

    def get_movement(self, fitnesses, current_map, all_cells): #Fitnesses list of tuples like so: ((start, destiny), fitness_eval_of_movm)
        if 'random' in self.ia_mode:
            if 'half' in self.ia_mode:
                return self.generate_random_movement(fitnesses, somewhat_random=True)
            return self.generate_random_movement(fitnesses, totally_random=True)
        elif 'fitness' in self.ia_mode:
            return self.generate_random_movement(fitnesses)
        elif 'alpha' in self.ia_mode:
            return self.generate_alpha_beta(fitnesses, current_map, all_cells)
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

    def generate_alpha_beta(self, initial_map, depth, max_nodes, all_cells, current_player, all_players):
        all_values = {}
        destiny = self.minimax(initial_map, [], 0, 5, True, -math.inf, math.inf)

    def generate_movements(self, current_map, player):
        destinies = {}  #TODO current_map is paths? NO ITS NOT!
        for cell, char_inside_cell in current_map.items():
            if char_inside_cell and char_inside_cell.owner_uuid == player:
                source = cell.get_real_index()
                paths = char_inside_cell.get_paths(self.graph, self.distances, current_map, cell, self.circum_size)
                destinies[source] = tuple(path[-1] for path in paths)
        return destinies    #Return {char: (dest1,  dest2...), char2:...}

    def minimax(self, my_player, enemy_player, map_situation, all_paths, path, depth, max_depth, isMaximizingPlayer, alpha, beta):
        #map_situation is: {cellindex:char/False}
        if depth is max_depth:
            value = sum(char.value for char in map_situation.values if char)
            all_paths[path] = value
            return value

        if isMaximizingPlayer:
            bestVal = -math.inf 
            for char, destinies in self.generate_movements(map_situation, my_player).items():
                for destiny in destinies:
                    #SIMULATE MOVEMENT
                    value = self.minimax(my_player, enemy_player, map_situation, all_paths, path, depth+1, max_depth, False, alpha, beta)
                    #UNDO SIMULATION
                    bestVal = max(bestVal, value) 
                    alpha = max(alpha, bestVal)
                    if beta <= alpha:
                        return bestVal
        else:
            bestVal = math.inf  
            for char, destinies in self.generate_movements(map_situation, enemy_player).items():
                for destiny in destinies:
                    #SIMULATE MOVEMENT
                    value = self.minimax(my_player, enemy_player, map_situation, all_paths, path, depth+1, max_depth, True, alpha, beta)
                    #UNDO SIMULATION
                    bestVal = min(bestVal, value) 
                    beta = min(beta, bestVal)
                    if beta <= alpha:
                        return bestVal