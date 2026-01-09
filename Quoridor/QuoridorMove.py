from enum import Enum
from Move import Move

class QuoridorMoveType(Enum):
    MOVE = 0
    FENCE = 1

class QuoridorMove(object):
    """
    One move in Quoridor
    """

    def move_pawn(new_coord, player):
        move = QuoridorMove()
        move.type = QuoridorMoveType.MOVE
        move.coord = new_coord
        move.player = player
        return move

    def add_fence(fence, player):
        move = QuoridorMove()
        move.type = QuoridorMoveType.FENCE
        move.coord = fence.first
        move.is_horizontal = fence.is_horizontal
        move.player = player
        return move

    def execute(self, board):
        if self.type == QuoridorMoveType.MOVE:
            board.move_pawn(self.player, self.coord)
        elif self.type == QuoridorMoveType.FENCE:
            board.add_fence(self.player, self.coord, self.is_horizontal)
        else:
            raise Exception("Impossible move!")

    def __eq__(self, other):
        try:
            if self.type != other.type:
                return False
            if self.type == QuoridorMoveType.MOVE:
                return self.coord == other.coord and self.player == other.player
            elif self.type == QuoridorMoveType.FENCE:
                return self.coord == other.coord and self.player == other.player and self.is_horizontal == other.is_horizontal
            return False
        except Exception:
            return False
