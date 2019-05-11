#import keras
import math
import time
import random
from obj.players import Player
from obj.utilities.decorators import time_it
from obj.paths import PathAppraiser

class PersistantNumber(object): #To avoid the copying of classes
    def __init__(self, initial_number=0):
        self.number = initial_number

class ComputerPlayer(Player):
    def __init__(self, graph, distances, level_size, name, order, sprite_size, canvas_size, ia_mode='random', infoboard=None, obj_uuid=None,\
                avatar=None, max_depth=5, adaptative_max_depth=True,  **character_params):
        super().__init__(name, order, sprite_size, canvas_size, infoboard=infoboard, obj_uuid=obj_uuid, empty=False, avatar=avatar, **character_params)
        self.human = False
        self.ia_mode = ia_mode #alpha-beta-pruning | null-move | full blown IA with keras
        self.distances = distances 
        self.graph = graph
        self.circum_size = level_size
        self.adaptative_max_depth = adaptative_max_depth
        self.max_depth = max_depth
        self.timeout_count = 0

    def increate_timeout_count(self):
        self.timeout_count += 1
        if self.adaptative_max_depth and self.timeout_count is 5:
            self.timeout_count = 5
            self.max_depth -= 1 if self.max_depth > 1 else 0   #Else we substract 0

    def generate_fitnesses(self, all_cells, current_player, paths_graph, distances, current_map, level_size):
        all_fitnesses = []
        for start_index, char in all_cells.items():
            if char.owner_uuid == current_player:
                destinations = [path[-1] for path in char.get_paths(paths_graph, distances, current_map, start_index, level_size)]
                fitnesses = PathAppraiser.rate_movements(start_index, destinations, paths_graph, distances, current_map, all_cells, level_size)
            for destiny, score in fitnesses.items():
                all_fitnesses.append(((start_index, destiny), score))   #Append a tuple ((start, destiny), fitness_eval_of_movm)
        return all_fitnesses

    def get_movement(self, current_map, board_cells, my_player, all_players, max_nodes=100): #TODO FOR NOW USING -1 AS BOARD HASH, CHANGE THAT. SAME WITH STATE HASH
        #Fitnesses list of tuples like so: ((start, destiny), fitness_eval_of_movm)
        all_cells = {cell.get_real_index(): cell.get_char() for cell in board_cells if cell.has_char()}
        fitnesses = self.generate_fitnesses(all_cells, my_player, self.graph, self.distances, current_map, self.circum_size)
        if 'random' in self.ia_mode:
            if 'half' in self.ia_mode:
                return self.generate_random_movement(fitnesses, somewhat_random=True)
            return self.generate_random_movement(fitnesses, totally_random=True)
        if 'fitness' in self.ia_mode:
            return self.generate_random_movement(fitnesses)
        #The other methods need the all_cells structure  
        if 'alpha' in self.ia_mode:
            if 'order' in self.ia_mode:
                return self.generate_alpha_beta_ordered(fitnesses, max_nodes, all_cells, current_map, my_player, all_players)    
            return self.generate_alpha_beta(max_nodes, all_cells, current_map, my_player, all_players)
        if 'monte' in self.ia_mode:
            return MonteCarloSearch.monte_carlo_tree_search(self.graph, self.distances, self.circum_size, -1, all_cells, current_map, my_player, all_players)
            
    def generate_random_movement(self, fitnesses, totally_random=False, somewhat_random=False):
        print("RANDOM METHOD")
        if totally_random:
            return random.choice(fitnesses)[0]
        fitnesses.sort(key=lambda tup: tup[1], reverse=True)
        if somewhat_random:
            return random.choices(fitnesses, weights=list(score[1] for score in fitnesses))[0]
        else:
            only_best_movements = list(score[0] for score in fitnesses if score[1] == fitnesses[0][1])  #IF the score is the same as the best elements inn the ordered list
            return random.choice(only_best_movements)

    #ALL PLAYERS IS NOTHING BUT  A LIST OF THE UUIDS OF ALL THE PLAYERS!!
    @time_it
    def generate_alpha_beta_ordered(self, fitnesses, max_nodes, all_cells, current_map, my_player_uuid, all_players, timeout=10):   #TODO ADD ORDERING OF DESTINIES BY FITNESSES
        my_player_index = next((i for i in range(0, len(all_players)) if all_players[i] == my_player_uuid))
        all_paths = {}
        #cells_with_char IS DONE LIKE THIS: A DICT WITH ONLY THE CELLS WITH A CHAR IN IT!!{INDEX: CHAR}
        start = time.time()
        pruned = PersistantNumber()
        self.minimax(my_player_index, my_player_index, all_players, all_cells, current_map, all_paths, [], 0, True, -math.inf, math.inf, start, timeout, pruned)
        print("The number of paths tested by alpha beta is "+str(len(all_paths.keys())), " with a max depth setting of "+str(self.max_depth)+", in a time of "+str(time.time()-start)+" seconds.")
        rated_movements = [((dest[0], dest[1]), score) for dest, score in all_paths.items()]
        rated_movements.sort(key=lambda dest:dest[1], reverse=True)
        print("FINAL MOVEMENTS RATED BY ALPHA BETA "+str(rated_movements))
        return rated_movements[0][0]    #Returning only the movement, we have no use for the score

    @time_it
    def generate_alpha_beta(self, max_nodes, all_cells, current_map, my_player_uuid, all_players, timeout=10):
        print("BETA METHOD")
        my_player_index = next((i for i in range(0, len(all_players)) if all_players[i] == my_player_uuid))
        all_paths = {}
        #cells_with_char IS DONE LIKE THIS: A DICT WITH ONLY THE CELLS WITH A CHAR IN IT!!{INDEX: CHAR}
        start = time.time()
        pruned = PersistantNumber()
        self.minimax(my_player_index, my_player_index, all_players, all_cells, current_map, all_paths, [], 0, True, -math.inf, math.inf, start, timeout, pruned)
        if time.time()-start > timeout: #If we reached the timeout...
            self.increate_timeout_count()
        print("The number of paths tested by alpha beta is "+str(len(all_paths.keys())), " with a max depth setting of "+str(self.max_depth)+", in a time of "+str(time.time()-start)+" seconds.")
        print("The number of pruned branches is "+str(pruned.number))
        rated_movements = [((dest[0], dest[1]), score) for dest, score in all_paths.items()]
        rated_movements.sort(key=lambda dest:dest[1], reverse=True)
        return rated_movements[0][0]    #Returning only the movement, we have no use for the score

    @staticmethod
    def generate_movements(path_graph, all_distances, circum_size, all_cells, current_map, current_player, my_turn=True):
        destinies = {}
        for cell_index, char_inside_cell in all_cells.items():
            if char_inside_cell.owner_uuid == current_player and my_turn\
            or char_inside_cell.owner_uuid != current_player and not my_turn:
                paths = char_inside_cell.get_paths(path_graph, all_distances, current_map, cell_index, circum_size)
                destinies[cell_index] = tuple(path[-1] for path in paths)
        return destinies    #Return {char: (dest1,  dest2...), char2:...}

    def minimax(self, my_player_index, current_player_index, all_players, all_cells, current_map, all_paths, path, depth, isMaximizingPlayer, alpha, beta, start_time, timeout, pruned):
        #map_situation is: {cellindex:char/False}
        if depth is self.max_depth or (time.time()-start_time > timeout):
            value = sum(char.value for char in all_cells.values() if char.owner_uuid == all_players[my_player_index])\
                    /sum(char.value for char in all_cells.values() if char.owner_uuid != all_players[my_player_index])   #My chars left minus his chars left
            all_paths[tuple(path)] = value  #This could also do it using only the first movm as key,since its the only one we are interested in. THe rest are garbage, who did those mvnmsnts? no idea
            return value

        if isMaximizingPlayer:
            bestVal = -math.inf 
            #generat4e-movemtns returns a dict weith the scheme: {cell_index_source: (all destinies)}
            for source_index, destinies in ComputerPlayer.generate_movements(self.graph, self.distances, self.circum_size, all_cells, current_map, all_players[current_player_index]).items():
                if not path:    #First movement, this, we are interested in
                    path.append(source_index)
                for dest_index in destinies:
                    #SIMULATE MOVEMENT
                    char_moving = all_cells[source_index]   #Starting to save variables to restore later
                    char_ded = all_cells[dest_index] if dest_index in all_cells else None
                    had_enemy = current_map[source_index].enemy
                    #Start simulating
                    current_map[source_index].ally = False
                    current_map[source_index].access = True
                    current_map[dest_index].ally = True
                    current_map[dest_index].enemy = False   #Simulation in current_map correct
                    current_map[source_index].access = False
                    del all_cells[source_index]
                    all_cells[dest_index] = char_moving     #Simulation in all_cells correct
                    path.append(dest_index)
                    #Going deeper
                    #NEW CURRENT PLAYER
                    current_player_index = current_player_index+1 if current_player_index < (len(all_players)-1) else 0
                    ComputerPlayer.change_map(current_map, all_cells, all_players[current_player_index])
                    #RECURSIVE EXECUTION
                    value = self.minimax(my_player_index, current_player_index, all_players, all_cells, current_map, all_paths, path, depth+1, False, alpha, beta, start_time, timeout, pruned)
                    #UNDO SIMULATION
                    current_map[source_index].ally = True
                    current_map[source_index].access = False
                    current_map[dest_index].ally = False
                    current_map[dest_index].enemy = had_enemy               #Restoration in current_map correct
                    current_map[dest_index].update_accessibility(char_moving)
                    all_cells[source_index] = char_moving                   #Restoration in all_cells correct
                    if not char_ded:    del all_cells[dest_index]           #If the cell we moved to didn't had an enemy
                    else:               all_cells[dest_index] = char_ded
                    del path[-1]
                    #end of restoration
                    bestVal = max(bestVal, value) 
                    alpha = max(alpha, value)
                    if beta <= value:   #Pruning
                        pruned.number += 1
                        return bestVal
                #print("·ppath "+str(path))
                if len(path) is 1:
                    del path[-1]
            return bestVal
        else:   #Minimizing player
            bestVal = math.inf  
            for source_index, destinies in ComputerPlayer.generate_movements(self.graph, self.distances, self.circum_size, all_cells, current_map, all_players[current_player_index], False).items():
                for dest_index in destinies:
                    #SIMULATE MOVEMENT
                    char_moving = all_cells[source_index]   #Starting to save variables to restore later
                    char_ded = all_cells[dest_index] if dest_index in all_cells else None
                    had_enemy = current_map[source_index].enemy
                    #Start simulating
                    current_map[source_index].ally = False
                    current_map[source_index].access = True
                    current_map[dest_index].ally = True
                    current_map[dest_index].enemy = False   #Simulation in current_map correct
                    current_map[source_index].access = False
                    del all_cells[source_index]
                    all_cells[dest_index] = char_moving     #Simulation in all_cells correct
                    path.append(dest_index)
                    #Going deeper     
                    #NEW CURRENT PLAYER
                    current_player_index = current_player_index+1 if current_player_index < (len(all_players)-1) else 0
                    ComputerPlayer.change_map(current_map, all_cells, all_players[current_player_index])
                    if current_player_index == my_player_index: #Checking this cuz it could have more than 2 players
                        isMaximizingPlayer = not isMaximizingPlayer
                    value = self.minimax(my_player_index, current_player_index, all_players, all_cells, current_map, all_paths, path, depth+1, isMaximizingPlayer, alpha, beta, start_time, timeout, pruned)
                    #UNDO SIMULATION
                    current_map[source_index].ally = True
                    current_map[source_index].access = False
                    current_map[dest_index].ally = False
                    current_map[dest_index].enemy = had_enemy               #Restoration in current_map correct
                    current_map[dest_index].update_accessibility(char_moving)
                    all_cells[source_index] = char_moving                   #Restoration in all_cells correct
                    if not char_ded:    del all_cells[dest_index]           #If the cell we moved to didn't had an enemy
                    else:               all_cells[dest_index] = char_ded
                    del path[-1]
                    #end of restoration
                    bestVal = min(bestVal, value) 
                    beta = min(beta, value)
                    if beta <= alpha:   #Pruning
                        pruned.number += 1
                        return bestVal
            return bestVal

    @staticmethod
    def change_to_next_player(current_player_index, my_player_index, all_players, current_map):
        current_player_index = current_player_index+1 if current_player_index < (len(all_players)-1) else 0
        if isMaximizingPlayer and current_player_index == my_player_index or not isMaximizingPlayer and current_player_index != my_player_index:
            isMaximizingPlayer = not isMaximizingPlayer
            ComputerPlayer.reverse_map(current_map)
        return current_player_index

    @staticmethod
    def reverse_map(current_map):
        """Reverses enemies and allies in the current map structure. Useful in simulations.
        A current map follows a scheme: {cell_index: path object}"""
        for path_obj in current_map.values():
            if path_obj.ally or path_obj.enemy: #If there is a char in it
                path_obj.ally = not path_obj.ally
                path_obj.enemy = not path_obj.enemy #Reversing indeed. Its just that.

    @staticmethod
    def change_map(current_map, all_cells, new_player_uuid):
        """Changes the current_map so its accurate when describing enemies and allies
        A current map follows a scheme: {cell_index: path object}"""
        for cell_index, char in all_cells.items():  #The only cells in tthe keys of this structure are the ones with characters
            if char.owner_uuid == new_player_uuid:
                current_map[cell_index].ally = True
                current_map[cell_index].enemy = False
            else:
                current_map[cell_index].ally = False
                current_map[cell_index].enemy = True
            current_map[cell_index].update_accessibility(char)

#Monte carlo tree search from here on
class Node(object):
    def __init__(self, parent, paths_graph, distances, circum_size, board_hash, board_state, map_state, previous_movement):
        self.parent = parent
        self.previous_movement = previous_movement #Movement that led to this node. Useful when returning it in the root method of the montecarlo
        #Board params - Some of those wont be modified, so its okay to save them as references
        self.paths_graph = paths_graph
        self.distances = distances
        self.circum_size = circum_size
        self.board_hash = board_hash
        #Those 4 settings up there are inherited by the lower nodes
        self.state_hash = None
        self.board_state = board_state#{cell_index: character}
        self.map_state = map_state    #{cell_index: path object}
        self.children = []
        self.visited = False
        self.total_n = 0
        self.total_value = 0

    def expand(self, current_player):
        #print("Expanding")
        if not self.children:   #If it's empty, we expand it. (Add the result boards to the children)
            for source_index, destinies in ComputerPlayer.generate_movements(self.paths_graph, self.distances, self.circum_size, self.board_state, self.map_state, current_player).items():
                for dest_index in destinies:
                    all_cells_node = self.board_state.copy()
                    current_map = {cell_index: path_obj.copy() for cell_index, path_obj in self.map_state.items()}
                    #Start simulating, all_cells
                    all_cells_node[dest_index] = all_cells_node[source_index]
                    del all_cells_node[source_index]
                    #simulating in current_map
                    current_map[source_index].ally = False
                    current_map[source_index].access = True
                    current_map[dest_index].ally = True
                    current_map[dest_index].enemy = False
                    current_map[dest_index].access = False  
                    #CREATES THE CHILDREN
                    self.children.append(Node(self, self.paths_graph, self.distances, self.circum_size, -1, all_cells_node, current_map, (source_index, dest_index)))    #God knows how much this will occupy in memory...
            self.map_state = None   #Have no more need for this data after expanding and getting all the possible movements from this board.
    
    def get_uct_value(self, exploration_const=1):
        if self.total_n == 0: 
            return math.inf
        try:
            return (self.total_value/self.total_n)+(exploration_const*(math.sqrt(math.log(self.parent.total_n)/self.total_n))) #Upper Confidence bound applied to trees
        except ValueError:
            print("parnttotaln is "+str(self.parent.total_n))
            raise ValueError("DICK")

    def at_end_game(self):
        all_essential_pieces = []
        for char in self.board_state.values():
            if char.essential:
                all_essential_pieces.append(char)
        return False if any(char.owner_uuid != all_essential_pieces[0].owner_uuid for char in all_essential_pieces) else True
        #If there are only essential pieces from a player left

    def board_evaluation(self, player):
        my_total_char_value = sum(char.value for char in self.board_state.values() if char.owner_uuid == player)
        try:
            return (my_total_char_value/sum(char.value for char in self.board_state.values() if char.owner_uuid != player))*my_total_char_value
        except ZeroDivisionError:   #No enemies left, so the sum would be zero
             return my_total_char_value*my_total_char_value

class MonteCarloSearch(object):
    EXPLORATION_CONSTANT = 1.5
    
    @staticmethod
    def monte_carlo_tree_search(paths_graph, distances, circum_size, board_hash, all_cells, current_map, my_player, all_players, timeout=10): #10 seconds of computational power
        print("MONTE CARLO METHOD")
        my_player_index = next((i for i in range(0, len(all_players)) if all_players[i] == my_player))
        current_player_index = my_player_index
        root_node = Node(None, paths_graph, distances, circum_size, -1, all_cells, current_map, (-1, -1))
        root_node.expand(all_players[current_player_index])
        start = time.time()
        iters = 0
        while (time.time()-start) < timeout:
            #print("Start of ITERATION "+str(iters))
            leaf = MonteCarloSearch.traverse(root_node, all_players[current_player_index])                          #leaf = unvisited node, EXPANSION
            simulation_result = MonteCarloSearch.rollout(leaf, all_players, my_player_index, current_player_index)  #ROLLOUT
            MonteCarloSearch.backpropagate(leaf, simulation_result)                                                 #BACKPROPAGATION
            #CHECKS NEW TURN FOR THE NEW SIMULATION AND ROLLOUT
            current_player_index = current_player_index+1 if current_player_index < (len(all_players)-1) else 0
            ComputerPlayer.change_map(current_map, all_cells, all_players[current_player_index])    #Change current map to be of the next player
            #print("End of ITERATION "+str(iters))
            iters += 1
        print("MonteCarlo method completed "+str(iters)+" iterations of the complete algorithm in "+str(time.time()-start)+" seconds")
        return max((node for node in root_node.children), key=lambda node:node.total_n).previous_movement

    @staticmethod
    def traverse(node, current_player):
        leaf = None
        while not leaf:
            leaf = next((child for child in node.children if child.total_n == 0), None)   #Get the first child unexplored, or the best one
            if not leaf: #If unexplored, gets the one with the best UCT value to expand it and get leafs in the next loop
                node = max((child for child in node.children), key=lambda child:child.get_uct_value(exploration_const=MonteCarloSearch.EXPLORATION_CONSTANT))
                node.expand(current_player)   #If its already expanded, it will not expand any further, so we can leave this line like this
        return leaf

    @staticmethod
    def rollout(node, all_players, my_player_index, current_player_index):
        current_player = current_player_index   #We copy this (basic type) so we don't modify it for the calling method
        #print("STARTED ROLLOUT")
        while not node.at_end_game():
            node = MonteCarloSearch.rollout_policy(node, all_players[current_player])
            current_player = current_player+1 if current_player < (len(all_players)-1) else 0
        #print("REACHED END")
        return node.board_evaluation(all_players[my_player_index])
    
    @staticmethod
    def rollout_policy(node, player_uuid, policy='random'): #TODO THIS RANDOM SHOULD DESTROY MOVEMENTS ALREADY DONE
        if 'rand' in policy:
            #Creating shit
            destinies = []
            all_cells_node = node.board_state.copy()
            map_state = {cell_index: path_obj.copy() for cell_index, path_obj in node.map_state.items()}
            ComputerPlayer.change_map(map_state, all_cells_node, player_uuid)    #Change current map to be of the current player
            loops = 0
            while not destinies:
                loops += 1
                allies = tuple((index, char) for index, char in all_cells_node.items() if char.owner_uuid == player_uuid)
                source_index, moving_char = random.choice(allies)
                destinies = moving_char.get_paths(node.paths_graph, node.distances, map_state, source_index, node.circum_size)   #get_paths rreturns a list of tuples with the complete path in one movemetn.
                """if loops > 50: #Infinite loop
                    print("NOT DESTINIES IN THIS LOOP")
                    print("ALLIES ARE "+str(allies))
                    print("Tried to move "+moving_char.id+" from "+str(source_index))
                    print(all_cells_node)
                    for index, path in map_state.items():
                        print(path)
                    print("---------------------------")
                if loops > 200:
                    assert False"""
            destiny = random.choice(destinies)[-1]
            #print("Char "+moving_char.id+" with the movement "+str(source_index)+" -> "+str(destiny))
            all_cells_node[destiny] = all_cells_node[source_index]
            del all_cells_node[source_index]
            #simulating in current_map
            map_state[source_index].ally = False
            map_state[source_index].access = True   #No one left in here, so you can do it
            map_state[destiny].ally = True
            map_state[destiny].enemy = False
            map_state[destiny].access = False       #An ally here
            child_node = Node(node, node.paths_graph, node.distances, node.circum_size, -1, all_cells_node, map_state, (source_index, destiny))
        return child_node

    @staticmethod
    def backpropagate(node, result):
        while node.parent:  #Loops until we have no parent, the top of the tree 
            node.total_n += 1
            node.total_value += result
            node = node.parent
        node.total_n += 1   #Otherwise the top of the tree node doesn't get stats
        node.total_value += result