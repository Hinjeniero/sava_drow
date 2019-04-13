#import keras
import math
class ComputerPlayer(object):
    def __init__(self):
        self.ia_mode = None #alpha-beta-pruning | null-move | full blown IA with keras
    
    def generate_possible_movements(self):
        pass

    def generate_action(self, current_map):
        pass

    def generate_alpha_beta(self, initial_map, depth, max_nodes, all_cells, current_player, all_players):
        all_paths = {}
        #TODO INPUT DATA: {cells: char/None/False}
        #TODO FIRST POSSIBLE DESTINIES WITH CHAR
        destiny = self.minimax(mapmpampa, all_paths, [], 1, 5, True, -math.inf, math.inf)

    def minimax(map_situation, all_paths, path, depth, max_depth, isMaximizingPlayer, alpha, beta):
        if depth is max_depth:  #TODO where to appen dthe next cell in path?
            value = sum(char.value for char in map_situation.values if char)
            all_paths[path] = value
            return value

        if isMaximizingPlayer :
            bestVal = -math.inf 
            for movement in self.generate_movements():
                value = minimax(node, all_paths, path, depth+1, max_depth, False, alpha, beta)
                bestVal = max(bestVal, value) 
                alpha = max(alpha, bestVal)
                if beta <= alpha:
                    break
            return bestVal

        else :
            bestVal = math.inf  
            for movement in self.generate_movements():
                value = minimax(node, all_paths, path, depth+1, max_depth, True, alpha, beta)
                bestVal = min(bestVal, value) 
                beta = min(beta, bestVal)
                if beta <= alpha:
                    break
            return bestVal

    def generate_movements(self):
        pass

    def generate_nodes(self, char):
        pass