from board import Board

class NetworkBoard(Board):
    def __init__(self, id_, event_id, end_event_id, resolution, *players, **params):
        super().__init__(id_, event_id, end_event_id, resolution, *players, **params)
        print("Yes.")