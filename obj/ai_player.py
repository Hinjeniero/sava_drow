"""--------------------------------------------
ai_player module. Contains the classes and methods to support
computer controlled game movements, depending on the algorithms chosen.
Have the following classes:
    PersistantNumber
    ComputerPlayer
--------------------------------------------"""

__all__ = ['PersistantNumber', 'ComputerPlayer']
__version__ = '0.2'
__author__ = 'David Flaity Pardo'

#Python libraries
import math
import time
import random
import collections

#Selfmade libraries
from obj.players import Player
from obj.utilities.decorators import time_it
from obj.paths import PathAppraiser

class PersistantNumber(object): #To avoid the copying of classes
    """PersistantNumber class. Contains an int that its persistant, that is, that holds the reference
    to the instance of it when it goes through methods. A glorified int that you can use as a 
    modificable input parameter in methods.
    Attributes:
        number (int):   The number itself."""
    def __init__(self, initial_number=0):
        """PersistantNumber constructor.
        Args:
            initial_number (int, default=0):    The number itself."""
        self.number = initial_number

class ComputerPlayer(Player):
    """ComputerPlayer class. Inherits from Player.
    Its purpose is #to_pass_butter. Just kidding, its to simulate the movements of a player
    without the intervention of an actual one. A CPU player.
    It holds various board parameters needed to check and see what movement/action to perform.
    The possibilities vary between simple algorithms, like random or half-random movements, to full heuristics to get a more
    'intelligent' like behaviour.
    Attributes:
        ai_mode (String):   Algorithm or method used to return the next movement of this player.
        distances (:obj: numpy.Matrix): Distances matrix of the current board.
        graph (:obj: numpy.Matrix): Matrix of enabled/directly connected paths of the current board.
        circum_size (int):  Length of each circumference of the current board.
        adaptative_max_depth (boolean): Flag to activate the adaptative reduction of the max depth search (According to the time limitation)
                                        or deactivate it. If True, the max depth of the search algorithms will be reducted by 1 until it can be completed
                                        below the timeout assigned.
        max_depth (int):    Current maximum depth to search in the tree algorithms.
        timeout_count (int):    Counter of the times that the timeout has been exceeded.
    """
    def __init__(self, graph, distances, level_size, name, order, sprite_size, canvas_size, ai_mode='random', infoboard=None, obj_uuid=None,\
                avatar=None, max_depth=5, adaptative_max_depth=True,  **character_params):
        """ComputerPlayer constructor.
        Args:
            distances (:obj: numpy.Matrix): Distances matrix of the current board.
            graph (:obj: numpy.Matrix): Matrix of enabled/directly connected paths of the current board.
            level_size (int):   Length of each circumference of the board that this player will be in.
            name (str): Name of the player.
            order (int):    Order of turn. A numerical identifier, if you prefer.
            sprite_size (:tuple: int, int): Size of the image of the characters. In pixels.
            canvas_size (:tuple: int, int): Resolution of the screen. In pixels.
            ai_mode (String):    Algorithm or method that will be used in each movement of this player.
            infoboard (:obj: Infoboard, default=None):  Infoboard of the player. It's shown through the game.
            obj_uuid (int, default=None):   Unique id of this player. If it's not supplied, it will be generated later.
            avatar (String):    Path of the folder with the desired avatars images. One will be picked at random for this player.
            max_depth(int): Current maximum depth to search in the tree algorithms.
            adaptative_max_depth (boolean): Flag to indicate if the max_depth attribute is adaptative to the current situation and timeout.
            **character_params (:dict:):    Contains the more specific parameters to create the characters.
                                            Ammount of each type of char, name of their actions, and their folder paths.
        """
        name = name+'(CPU)'
        super().__init__(name, order, sprite_size, canvas_size, infoboard=infoboard, obj_uuid=obj_uuid, empty=False, avatar=avatar, **character_params)
        self.human = False
        self.ai_mode = ai_mode #alpha-beta-pruning | null-move | full blown IA with keras
        self.distances = distances 
        self.graph = graph
        self.circum_size = level_size
        self.adaptative_max_depth = adaptative_max_depth
        self.max_depth = max_depth
        self.timeout_count = 0

    def increate_timeout_count(self):
        """Increases the counter of timeouts breached. Restarts it (and does whatever action) if the limit has been hit."""
        self.timeout_count += 1
        if self.adaptative_max_depth and self.timeout_count is 5:
            self.timeout_count = 5
            self.max_depth -= 1 if self.max_depth > 1 else 0   #Else we substract 0

    def generate_fitnesses(self, all_cells, current_player, paths_graph, distances, current_map, level_size):
        """Generates all the fitnesses (scores) for each movement possible for the input player, in the current board, in the input situation.
        Args:
            all_cells (Dict->int:Character):    Structure that have all the cells that currently have a char in them. The key of each element 
                                                if the index of the cell, and the value is the Character that resides in that cell.
            current_player (int):   Unique identifier of the current player.
            paths_graph (:obj: numpy.Matrix):   Matrix of enabled/directly connected paths of the current board.
            distances (:obj: numpy.Matrix): Distances matrix of the current board.
            current_map (Dict->int:Path):   Path objects that describe each current cell for a specific player.
                                            (Says if there is a char, if it's an enemy or an ally...)
            level_size (int):   Length of each circumference of the board that this player will be in.
        Returns:
            (List->Tuple->(int, int), int): A list of tuples, each tuple containing the movement itself in the first position(another tuple),
                                            and the score for this movement in the second position
        """
        all_fitnesses = []
        for start_index, char in all_cells.items():
            if char.owner_uuid == current_player:
                destinations = [path[-1] for path in char.get_paths(paths_graph, distances, current_map, start_index, level_size)]
                fitnesses = PathAppraiser.rate_movements(start_index, destinations, paths_graph, distances, current_map, all_cells, level_size)
                for destiny, score in fitnesses.items():
                    all_fitnesses.append(((start_index, destiny), score))   #Append a tuple ((start, destiny), fitness_eval_of_movm)
        return all_fitnesses

    #TODO FOR NOW USING -1 AS BOARD HASH, CHANGE THAT. SAME WITH STATE HASH
    def get_movement(self, current_map, board_cells, my_player, all_players, max_nodes=100):
        """Gets as an input the current state of the board, and based on the current ai mode, returns what it undestands to be
        the best course of action (The best next movement).
        Args:
            current_map (Dict->int:Path):   Path objects that describe each current cell for a specific player.
                                            (Says if there is a char, if it's an enemy or an ally...)
            board_cells (Iterable->Cell):   The updated cell objects that form the board. The iterable with them will usually be 
                                            a List or a pygame.sprite.Group.
            my_player (int):    Unique identifier of the current player.
            all_players (List->int):    List with all the players unique identifiers(uuid).
            max_nodes (int):    Limit to the expansion of the tree searchs. Unused right now.
        Returns:
            (Tuple->int, int):  The best movement calculated by the underlying algorithm. (source, destiny).
        """
        all_cells = {cell.get_real_index(): cell.get_char() for cell in board_cells if cell.has_char()}
        fitnesses = self.generate_fitnesses(all_cells, my_player, self.graph, self.distances, current_map, self.circum_size)
        if 'random' in self.ai_mode:
            if 'half' in self.ai_mode:
                return self.generate_random_movement(fitnesses, somewhat_random=True)
            return self.generate_random_movement(fitnesses, totally_random=True)
        if 'fitness' in self.ai_mode:
            return self.generate_random_movement(fitnesses)
        #The other methods need the all_cells structure  
        if 'alpha' in self.ai_mode:
            if 'order' in self.ai_mode:
                return self.generate_alpha_beta(max_nodes, all_cells, current_map, my_player, all_players, ordering=True)    
            return self.generate_alpha_beta(max_nodes, all_cells, current_map, my_player, all_players)
        if 'monte' in self.ai_mode:
            return MonteCarloSearch.monte_carlo_tree_search(self.graph, self.distances, self.circum_size, -1, all_cells, current_map, my_player, all_players)
            
    def generate_random_movement(self, fitnesses, totally_random=False, somewhat_random=False):
        """Algorithm to return a next movement based in randomness and the score at which are rated the different possible moves.
        Have 3 modes:
            Totally random: A movement will be chosen from the possible ones at random.
            Partially random: Will use a random, but the weights of each decission will be based on the score.
            Pure fitnesses: Will take only the move with the highest score. If more than one share the highest, a random one will be chosen.
        Args:
            fitnesses: A list of tuples, each tuple containing the movement itself in the first position(another tuple),
                    and the score for this movement in the second position
            totally_random (boolean):   Flag that is True if the mode of the algorithm is totally random.
            somewhat_random (boolean):  Flag that is True if the mode of the algorithm is partially random.
        Returns:
            (Tuple->int, int):  A movement calculated by the underlying algorithm. (source, destiny).
        """
        if totally_random:
            return random.choice(fitnesses)[0]
        fitnesses.sort(key=lambda tup: tup[1], reverse=True)
        if somewhat_random:
            return random.choices(fitnesses, weights=list(score[1] for score in fitnesses))[0]
        else:
            only_best_movements = list(score[0] for score in fitnesses if score[1] == fitnesses[0][1])  #IF the score is the same as the best elements inn the ordered list
            return random.choice(only_best_movements)

    @time_it
    def generate_alpha_beta(self, max_nodes, all_cells, current_map, my_player_uuid, all_players, timeout=10.0, ordering=False):
        """Heuristic that uses the alpha-beta pruning to explore the game tree, reaching until the self.max_depth attribute, and
        returning the evaluation of the board at that point. Then uses that value to cut off game tree branches that, obviously, would have
        never ocurred in a normal gameplay.
        Args:
            max_nodes (int):    Limit to the expansion of the tree searchs. Unused right now.
            all_cells (Dict->int:Character):    Structure that have all the cells that currently have a char in them. The key of each element 
                                                if the index of the cell, and the value is the Character that resides in that cell.
            current_map (Dict->int:Path):   Path objects that describe each current cell for a specific player.
                                            (Says if there is a char, if it's an enemy or an ally...)
            my_player_uuid (int):   Unique identifier of the current player.
            all_players (List->int):    List with all the players unique identifiers(uuid).
            timeout (float):    Limit of time, in seconds, that this method has to explore the game tree before forcibly returning.
            ordering (boolean): True if we want to order the possible destinies in each iteration. More pruning, but less iterations.
        Returns:
            (Tuple->int, int):  The best movement calculated in the execution until the end (source, destiny).
        """
        my_player_index = next((i for i in range(0, len(all_players)) if all_players[i] == my_player_uuid))
        all_paths = {}
        start = time.time()
        pruned = PersistantNumber()
        self.minimax(my_player_index, my_player_index, all_players, all_cells, current_map, all_paths, [], 0, True, -math.inf, math.inf, start, timeout, pruned, ordering)
        if time.time()-start > timeout: #If we reached the timeout...
            self.increate_timeout_count()
        print("The number of paths tested by alpha beta is "+str(len(all_paths.keys())), " with a max depth setting of "+str(self.max_depth)+", in a time of "+str(time.time()-start)+" seconds.")
        print("The number of pruned branches is "+str(pruned.number))
        rated_movements = [((dest[0], dest[1]), score) for dest, score in all_paths.items()]
        rated_movements.sort(key=lambda dest:dest[1], reverse=True)
        return rated_movements[0][0]    #Returning only the movement, we have no use for the score

    @staticmethod
    def generate_movements(paths_graph, all_distances, circum_size, all_cells, current_map, current_player, my_turn=True, ordering=False):
        """Generates and returns all the possible movements in a board state for a specific player and his characters.
        Args:
            paths_graph (:obj: numpy.Matrix):   Matrix of enabled/directly connected paths of the current board.
            all_distances (:obj: numpy.Matrix): Distances matrix of the current board.
            circum_size (int):  Length of each circumference of the board that this player will be in
            all_cells (Dict->int:Character):    Structure that have all the cells that currently have a char in them. The key of each element 
                                                if the index of the cell, and the value is the Character that resides in that cell.
            current_map (Dict->int:Path):   Path objects that describe each current cell for a specific player.
                                            (Says if there is a char, if it's an enemy or an ally...)
            current_player (int):   Unique identifier of the current player.
            my_turn (boolean, default=True):  Flag that says if its the turn of the current player or not. Useless right now, most likely a vestige.
            ordering (boolean, default=False): True if we want to order the possible destinies in each iteration, using the fitnesses.
        Returns:
            (Dict->int, Tuple->ints):   Each key of the dict, is the index of the source cell, and each value, is a tuple containing all
                                        the possible destiny cells from that source cell.
        """
        destinies = []
        for cell_index, char_inside_cell in all_cells.items():
            this_index_destinations = []
            if char_inside_cell.owner_uuid == current_player and my_turn\
            or char_inside_cell.owner_uuid != current_player and not my_turn:
                paths = char_inside_cell.get_paths(paths_graph, all_distances, current_map, cell_index, circum_size)
                if paths:
                    if ordering:  #If there are paths
                        this_index_destinations = [path[-1] for path in paths]  #All destinies
                        fitnesses = PathAppraiser.rate_movements_lite(cell_index, this_index_destinations, paths_graph, current_map, all_cells, circum_size)
                        destinies.extend([(cell_index, dest, score) for dest, score in fitnesses.items()])   #(source_cell, dest_cell, score_movement)
                        destinies.sort(key=lambda movement: movement[-1], reverse=True)  #Order by decrecient fitnesses
                    else:
                        destinies.extend([(cell_index, path[-1]) for path in paths])                          #(source_cell, dest_cell)
        return tuple(destinies) 

    def minimax(self, my_player_index, current_player_index, all_players, all_cells, current_map, all_paths, path, depth, isMaximizingPlayer, alpha, beta, start_time, timeout, pruned, ordering):
        """Recursive algorithm. It's the core of the alpha-beta pruning AI, Exploring, expanding and cutting off branchs of the game tree. It is based in the MiniMax algorithm.
        In a 2 player game, the algorithm goes switching right between maximizinf and minimizing mode. In a 4 player game, stays in minimazing for a bit more before returning to 
        maximizing.
        Args:
            my_player_index (int):  Index of my player uuid in the list that hold all the uuids.
            current_player_index (int): Index of the player uuid that currently holds the turn, in the all_player list.
            all_players (List->int):    List with all the players unique identifiers(uuid).
            all_cells (Dict->int:Character):    Structure that have all the cells that currently have a char in them. The key of each element 
                                                if the index of the cell, and the value is the Character that resides in that cell.
                                                Will be simulated and changed for other players as the algorithm explores the tree, and changed back when finished.
            current_map (Dict->int:Path):   Path objects that describe each current cell for a specific player. 
                                            Will be simulated and changed for other players as the algorithm explores the tree, and changed back when finished.
            all_paths (Dict->Tuple:float):  Have all the paths that the algorithm has found until now (All the expansions until the max_depth/timeout), with the value that
                                            moving until that board game state returned. Each key is the path in a tuple, and each float is the score.
            path (List->ints):  Current expanding path. Will be converted to a tuple and analyzed when it reaches the max depth/timeout.
            isMaximizingPlayer (boolean):   Flag that says if the algorithm is in a maximizing step (True) or it isn't (False).
            alpha (float):  Current alpha value. Used for pruning.
            beta (float):   Current beta value. Used for pruning.
            start_time (float): Timestamp of the moment at which the method started. Used to check if we are out of time already.
            timeout (float):    Limit of time, in seconds, that this method has to explore the game tree before forcibly returning.
            pruned (:obj: PersistantNumber): Number of branches that have been cut off in the execution.
            ordering (boolean): True if we want to order the possible destinies in each iteration. More pruning, but less iterations.
        """
        if depth is self.max_depth or (time.time()-start_time > timeout):   #TODO or board.end_game is true!
            value = sum(char.value for char in all_cells.values() if char.owner_uuid == all_players[my_player_index])\
                    /sum(char.value for char in all_cells.values() if char.owner_uuid != all_players[my_player_index])   #My chars left minus his chars left
            all_paths[tuple(path)] = value  #This could also do it using only the first movm as key,since its the only one we are interested in. THe rest are garbage, who did those mvnmsnts? no idea
            #del path[0] #Lets get that index out of here
            return value
        if isMaximizingPlayer:
            bestVal = -math.inf 
            #generate_movements returns a dict with the scheme: {cell_index_source: (all destinies)}
            #for source_index, destinies in ComputerPlayer.generate_movements(self.graph, self.distances, self.circum_size, all_cells, current_map, all_players[current_player_index], ordering=ordering).items():
            for movement in ComputerPlayer.generate_movements(self.graph, self.distances, self.circum_size, all_cells, current_map, all_players[current_player_index], ordering=ordering):
                source_index = movement[0]
                if not path:    #First movement, this, we are interested in
                    path.append(source_index)
                dest_index = movement[1]
                #for dest_index in movements[1]:
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
                        #minimax(self, my_player_index, current_player_index, all_players, all_cells, current_map, all_paths, path, depth, isMaximizingPlayer, alpha, beta, start_time, timeout, pruned, ordering):
                value = self.minimax(my_player_index, current_player_index, all_players, all_cells, current_map, all_paths, path, depth+1, False, alpha, beta, start_time, timeout, pruned, ordering)
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
                if len(path) is 1:  #If we have another source here
                    del path[0]
                #end of restoration
                bestVal = max(bestVal, value) 
                alpha = max(alpha, value)
                if beta <= value:   #Pruning
                    pruned.number += 1
                    return bestVal
            return bestVal
        else:   #Minimizing player
            bestVal = math.inf  
            #for source_index, destinies in ComputerPlayer.generate_movements(self.graph, self.distances, self.circum_size, all_cells, current_map, all_players[current_player_index], False, ordering=ordering).items():
            for movement in ComputerPlayer.generate_movements(self.graph, self.distances, self.circum_size, all_cells, current_map, all_players[current_player_index], ordering=ordering):
                source_index = movement[0]
                dest_index = movement[1]
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
                value = self.minimax(my_player_index, current_player_index, all_players, all_cells, current_map, all_paths, path, depth+1, isMaximizingPlayer, alpha, beta, start_time, timeout, pruned, ordering)
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
        """Static method that changes the current_map structure to be able to simulate the turn of the next player.
        Auxiliar method of alpha-beta. Unused right now.
        Args:
            current_player_index (int): Index of the player uuid that currently holds the turn, in the all_player list.
            my_player_index (int):  Index of my player uuid in the list that hold all the uuids.
            all_players (List->int):    List with all the players unique identifiers(uuid).
            current_map (Dict->int:Path):   Path objects that describe each current cell for a specific player. 
        Returns:
            (int): The index of the new current player (In the all_players list)."""
        current_player_index = current_player_index+1 if current_player_index < (len(all_players)-1) else 0
        if isMaximizingPlayer and current_player_index == my_player_index or not isMaximizingPlayer and current_player_index != my_player_index:
            isMaximizingPlayer = not isMaximizingPlayer
            ComputerPlayer.reverse_map(current_map)
        return current_player_index

    @staticmethod
    def reverse_map(current_map):
        """Reverses enemies and allies in the current_map structure. Useful in simulations.
        If both were False they keep being False.
        Args:
            current_map (Dict->int:Path):   Path objects that describe each current cell for a specific player."""
        for path_obj in current_map.values():
            if path_obj.ally or path_obj.enemy: #If there is a char in it
                path_obj.ally = not path_obj.ally
                path_obj.enemy = not path_obj.enemy #Reversing indeed. Its just that.

    @staticmethod
    def change_map(current_map, all_cells, new_player_uuid):
        """Changes the current_map structure to match another player (the enemies and allies and such).
        Args:
            current_map (Dict->int:Path):   Path objects that describe each current cell for a specific player.
            new_player_uuid (int):  The uuid of the player that the current_map must match."""
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
    """Class Node. Core class that is pretty much essential for the MonteCarlo heuristic to work properly.
    Each instance of this class represents a Node/leaf in the game tree. Each node has information about the board state
    that it holds.
    Attributes:
        parent (:obj:Node): Direct parent of this node. The one that 'created' you when expanding itself.
        previous_movement (Tuple->int, int):    Movement that led to this node. Useful when returning it in the root method of the montecarlo.
        paths_graph (:obj: numpy.Matrix):   Matrix of enabled/directly connected paths of the current board.
        distances (:obj: numpy.Matrix): Distances matrix of the current board.
        circum_size (int):   Length of each circumference of the board that this player will be in.
        board_hash (int):   Hash produced by the current board_state. Useful when indexing/saving.
        board_state (Dict->int:Character):  Structure that have all the cells that currently have a char in them. The key of each element 
                                    if the index of the cell, and the value is the Character that resides in that cell.
        map_state (Dict->int:Path):   Path objects that describe each current cell for a specific player.
                                        (Says if there is a char, if it's an enemy or an ally...)
        children (List->Nodes): All the nodes that have direct descendency of this one when expanded. Like the 'sons' of this node.
        visited (boolean):  Flag that says if this node have been visited.
        total_n (int):  Times that this Node have been selected for rollout/been visited.
        total_value (float):    Total value that the simulations that have this node in their 'game path' returned.
    """
    def __init__(self, parent, paths_graph, distances, circum_size, board_hash, board_state, map_state, previous_movement):
        """Node constructor.
        Args:
            parent (:obj:Node): Direct parent of this node. The one that 'created' you when expanding itself.
            paths_graph (:obj: numpy.Matrix):   Matrix of enabled/directly connected paths of the current board.
            distances (:obj: numpy.Matrix): Distances matrix of the current board.
            circum_size (int):   Length of each circumference of the board that this player will be in.
            board_hash (int):   Hash produced by the current board_state. Useful when indexing/saving.
            board_state (Dict->int:Character):  Structure that have all the cells that currently have a char in them. The key of each element 
                                        if the index of the cell, and the value is the Character that resides in that cell.
            map_state (Dict->int:Path):   Path objects that describe each current cell for a specific player.
                                            (Says if there is a char, if it's an enemy or an ally...) 
            previous_movement (Tuple->int, int):    Movement that led to this node. Useful when returning it in the root method of the montecarlo.       
        """
        self.parent = parent
        self.previous_movement = previous_movement 
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
        """Expands this node, effectively creating as many nodes or states as movements are possible from the board state of this node.
        If its already expanded, does nothing. Also, once donde, delete the attribute map_state of the node calling this method, since it won't
        be useful anymore (to save memory).
        Creates and adds all the children of this node to the self.children attribute.
        Args:
            current_player (int):   UUID of the player that holds the turn in this node."""
        if not self.children:   #If it's empty, we expand it. (Add the result boards to the children)
            #for source_index, destinies in ComputerPlayer.generate_movements(self.paths_graph, self.distances, self.circum_size, self.board_state, self.map_state, current_player).items():
            for movements in ComputerPlayer.generate_movements(self.paths_graph, self.distances, self.circum_size, self.board_state, self.map_state, current_player):
                source_index = movements[0]
                dest_index = movements[1]
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
        """Calculates the (upper confidence bound applied to trees) value of this node.
        Args:
            exploration_const (float, default=1):   Constant that makes the exploration part of the algorithm higher or lower.
        Returns:
            (float):    Current UBCTV of this node."""
        if self.total_n == 0: 
            return math.inf
        return (self.total_value/self.total_n)+(exploration_const*(math.sqrt(math.log(self.parent.total_n)/self.total_n))) #Upper Confidence bound applied to trees

    def at_end_game(self):
        """Checks if the board game has reached and end. Does this by checking all the essential pieces left, and checking if they belong to more
        than one player. (If there are only essential pieces from a player left)
        Returns:
            (boolean):  True if the board state is final, this means, the game is over. False otherwise."""
        all_essential_pieces = []
        for char in self.board_state.values():
            if char.essential:
                all_essential_pieces.append(char)
        return False if any(char.owner_uuid != all_essential_pieces[0].owner_uuid for char in all_essential_pieces) else True

    def board_evaluation(self, player):
        """Calculates a score for the current board, taking into account the input player.
        The higher the total value char of the input player is, the higher the score.
        Args:
            player (int):   UUID of the player for whom the scoring of the board will be processed.
        Returns:
            (float):    Score of the board state of this node."""
        my_total_char_value = sum(char.value for char in self.board_state.values() if char.owner_uuid == player)
        try:
            return (my_total_char_value/sum(char.value for char in self.board_state.values() if char.owner_uuid != player))*my_total_char_value
        except ZeroDivisionError:   #No enemies left, so the sum would be zero
             return my_total_char_value*my_total_char_value

class MonteCarloSearch(object):
    """MonteCarloSearch class. Holds all the static methods and steps needed to perform a MonteCarlo heuristic.
    This heuristic have, in short, 4 steps:
        EXPANSION:  A node is selected (and expanded if needed) to check the immediate possible movements.
        TRAVERSION: From the possible nodes, one is chosen.
        SIMULATION/ROLLOUT: From that chosen node, the board simulates all the players movements until it reaches an end state.
        BACKPROPAGATION:    The game takes the score of that final state board, and propagates it back all the way to the root node.
    General class attributes:
        EXPLORATION_CONSTANT (float, default=1.5):  Constant used in the uct algorithm of the nodes. The higher the value, the higher the exploration in the tree.
    """
    EXPLORATION_CONSTANT = 1.5
    @staticmethod
    def monte_carlo_tree_search(paths_graph, distances, circum_size, board_hash, all_cells, current_map, my_player, all_players, timeout=10): #10 seconds of computational power
        my_player_index = next((i for i in range(0, len(all_players)) if all_players[i] == my_player))
        current_player_index = my_player_index
        root_node = Node(None, paths_graph, distances, circum_size, -1, all_cells, current_map, (-1, -1))
        root_node.expand(all_players[current_player_index])
        start = time.time()
        iters = 0
        while (time.time()-start) < timeout:
            leaf = MonteCarloSearch.traverse(root_node, all_players[current_player_index])                          #leaf = unvisited node, EXPANSION
            simulation_result = MonteCarloSearch.rollout(leaf, all_players, my_player_index, current_player_index)  #ROLLOUT
            MonteCarloSearch.backpropagate(leaf, simulation_result)                                                 #BACKPROPAGATION
            #CHECKS NEW TURN FOR THE NEW SIMULATION AND ROLLOUT
            current_player_index = current_player_index+1 if current_player_index < (len(all_players)-1) else 0
            ComputerPlayer.change_map(current_map, all_cells, all_players[current_player_index])    #Change current map to be of the next player
            iters += 1
        print("MonteCarlo method completed "+str(iters)+" iterations of the complete algorithm in "+str(time.time()-start)+" seconds")
        return max((node for node in root_node.children), key=lambda node:node.total_n).previous_movement

    @staticmethod
    def traverse(node, current_player):
        """This method does the traverse part of the MonteCarlo heuristic.
        First, gets a node. If this node has an unexplored son, chose this one. Otherwise, gets the son with the highest UCT value, 
        and expands this one. Then it gets one of the last expanded node children.
        Args:
            current_player (int):   uuid of the player that has the turn in this step.
        Returns
            (:obj:Node):    The final chosen node to do rollout/simulate from."""
        leaf = None
        while not leaf:
            leaf = next((child for child in node.children if child.total_n == 0), None)   #Get the first child unexplored, or the best one
            if not leaf: #If unexplored, gets the one with the best UCT value to expand it and get leafs in the next loop
                node = max((child for child in node.children), key=lambda child:child.get_uct_value(exploration_const=MonteCarloSearch.EXPLORATION_CONSTANT))
                node.expand(current_player)   #If its already expanded, it will not expand any further, so we can leave this line like this
        return leaf

    @staticmethod
    def rollout(node, all_players, my_player_index, current_player_index):
        """Simulates movements across the players in the board until it reaches an end state. Then it returns the value of this end state.
        The movements are chosen according to the policy of the method. Normally random.
        Args:
            all_players (List->int):    List with all the players unique identifiers(uuid).
            current_player_index (int): Index of the player uuid that currently holds the turn, in the all_player list.
            my_player_index (int):  Index of my player uuid in the list that hold all the uuids.
        Returns:
            (float):    The value of the end board that we have reached through simulation (value for my player)."""            
        current_player = current_player_index   #We copy this (basic type) so we don't modify it for the calling method
        while not node.at_end_game():
            node = MonteCarloSearch.rollout_policy(node, all_players[current_player])
            current_player = current_player+1 if current_player < (len(all_players)-1) else 0
        return node.board_evaluation(all_players[my_player_index])
    
    @staticmethod
    def rollout_policy(node, player_uuid, policy='random'): #TODO THIS RANDOM SHOULD DESTROY MOVEMENTS ALREADY DONE
        """This method choose the next step in the simulation, according to the configured policy.
        Args:
            player_uuid (int):  uuid of the player that holds the turn. The resulting possible movements will be generated
                                according to this player. Then one will be chosen.
            policy (String, default='random'):  Policy to follow to choose the steps in the simulation.
        Returns:
            (:obj:Node):    The chosen node (next step)."""
        if 'rand' in policy:
            #Creating structures
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
            destiny = random.choice(destinies)[-1]
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
        """Backpropagates the result input through all the parents, all the way to the top of the tree.
        Also increases the n value of those nodes in 1. UCT things.
        Args:
            result (float): Result to propagate.
        """
        while node.parent:  #Loops until we have no parent, the top of the tree 
            node.total_n += 1
            node.total_value += result
            node = node.parent
        node.total_n += 1   #Otherwise the top of the tree node doesn't get stats
        node.total_value += result