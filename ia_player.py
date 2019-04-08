import tensorflow
import keras

class ComputerPlayer(object):
    def __init__(self):
        self.ia_mode = None #alpha-beta-pruning | null-move | full blown IA with keras
    
    def generate_movement(self, current_map):
        pass
