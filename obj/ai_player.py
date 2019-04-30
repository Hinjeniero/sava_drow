#import keras
import math
import time
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

    @staticmethod
    def generate_movements(all_cells, current_map, my_player, my_turn=True):
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
            for source_index, destinies in ComputerPlayer.generate_movements(all_cells, current_map, my_player).items():
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
            for source_index, destinies in ComputerPlayer.generate_movements(all_cells, current_map, my_player, False).items():
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

    @staticmethod
    def reverse_map(self, current_map):
        """Reverses enemies and allies in the current map structure. Useful in simulations.
        A current map follows a scheme: {cell_index: path object}"""
        for path_obj in current_map.values():
            if path_obj.ally or path_obj.enemy: #If there is a char in it
                path_obj.ally = not path_obj.ally
                path_obj.enemy = not path_obj.enemy #Reversing indeed. Its just that.

#Monte carlo tree search from here on
class Node(object):
    def __init__(self, parent, board_hash, board_state, map_state):
        self.parent = parent
        self.board_hash = board_hash
        self.state_hash = None
        self.board_state = board_state  #{cell_index: character}
        self.map_state = map_state      #{cell_index: path object}
        self.children = []
        self.visited = False
        self.total_n = 0
        self.total_value = 0

    def expand(self, all_cells, current_map, my_turn):
        if not self.children:   #If it's empty, we expand it. (Add the result boards to the children)   #TODO CHECK PLAYERS TO REVERSE AND THAT SHIT
            #SIMULATE MOVEMENT
            for source_index, destinies in ComputerPlayer.generate_movements(all_cells, current_map, my_player, False).items():
                for dest_index in destinies:
                    #TODO COPY STRUCTURES! cafeul, onlyshallow copy
                    #char_moving = all_cells[source_index]   #Starting to save variables to restore later
                    #char_ded = all_cells[dest_index] if dest_index in all_cells else None
                    #had_enemy = current_map[source_index].enemy
                    #Start simulating
                    del all_cells[source_index] 
                    all_cells[dest_index] = all_cells[source_index]
                    #----
                    had_enemy = current_map[source_index].enemy
                    current_map[source_index].ally = False
                    current_map[dest_index].ally = True
                    current_map[dest_index].enemy = False
                    #CREATES THE CHILDREN
                    self.children.append(Node(self, -1, all_cells, current_map))    #God knows how much this will occupy in memory...
                    #Return current map to the way it was
                    current_map[source_index].ally = True
                    current_map[dest_index].ally = False
                    current_map[dest_index].enemy = had_enemy               #Restoration in current_map correct
    
    def get_uct_value(self, exploration_const=1):
        if self.total_n == 0: 
            return math.inf
        return (self.total_value/self.total_n)+(exploration_const*(math.sqrt(math.log(self.parent.total_n)/self.total_n))) #Upper Confidence bound applied to trees

    def at_end_game(self):
        all_essential_pieces = []
        for char in self.board_state:
            if char.essential:
                all_essential_pieces.append(char)
        return False if any(char.owner_uuid != all_essential_pieces[0].owner_uuid for char in all_essential_pieces) else True
        #If there are only essential pieces from a player left

    def board_evaluation(self, player):
        my_total_char_value = sum(char.value for char in self.board_state if char.owner_uuid == player.uuid)
        return (my_total_char_value/sum(char.value for char in self.board_state if char.owner_uuid != player.uuid))*my_total_char_value

class MonteCarloSearch(object):
    EXPLORATION_CONSTANT = 1.5
    
    @staticmethod
    def monte_carlo_tree_search(board_hash, root_node, all_cells, current_map, my_player, timeout=10): #10 seconds of computational power
        start = time.time()
        while (time.time-start) < timeout:
            leaf = MonteCarloSearch.traverse(root_node)   #leaf = unvisited node 
            simulation_result = MonteCarloSearch.rollout(leaf, all_cells, current_map, my_player)
            MonteCarloSearch.backpropagate(leaf, simulation_result)
        return max((node for node in root_node.children), key=lambda node:node.total_n) #TODO check how to return the movement itself

    @staticmethod
    def traverse(node):
        leaf = None
        while not leaf:
            leaf = next((child for child in node.children if child.total_n == 0), None)   #Get the first child unexplored, or the best one
            if not leaf: #If unexplored, gets the one with the best UCT value to expand it and get leafs in the next loop
                node = max((child for child in node.children), key=lambda child:child.get_uct_value(exploration_const=MonteCarloSearch.EXPLORATION_CONSTANT))
                node.expand()   #If its already expanded, it will not expand any further, so we can leave this line like this
        return leaf if leaf else node   #Check if endgame or what is this. TODO Check this line

    @staticmethod
    def rollout(node, all_cells, current_map, my_player):
        #Gotta copy those structures for the simulations to not affect the original ones
        while not node.at_end_game():
            node = MonteCarloSearch.rollout_policy(node)
        return node.board_evaluation()
    
    @staticmethod
    def rollout_policy(node, policy='random'):
        if 'rand' in policy:
            pass    #Gonna choose random anyway
        return random.choice(node.children)

    @staticmethod
    def backpropagate(node, result):
        while node.parent:  #Loops until we have no parent, the top of the tree 
            node.total_n += 1
            node.total_value += result
            node = node.parent