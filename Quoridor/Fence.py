from collections import namedtuple
from Quoridor.Coordinate import Coordinate
from Quoridor.QuoridorMove import QuoridorMove

class Fence:
    def __init__(self, first, is_horizontal):
        self.first = first
        self.is_horizontal = is_horizontal

    def __eq__(self, other):
        return self.first == other.first and self.is_horizontal == other.is_horizontal

    def __hash__(self):
        return hash((self.first, self.is_horizontal))

    # See if you can move from current to final without hitting this wall
    def test_move(self, current, final):
        if self.is_horizontal:
            if (current.y == self.first.y - 1 and final.y == self.first.y) or (final.y == self.first.y - 1 and current.y == self.first.y):
                if current.x == self.first.x or current.x == self.first.x + 1:
                    return False
                else:
                    return True
            else:
                return True
        else:
            if (current.x == self.first.x - 1 and final.x == self.first.x) or (final.x == self.first.x - 1 and current.x == self.first.x):
                if current.y == self.first.y or current.y == self.first.y + 1:
                    return False
                else:
                    return True
            else:
                return True

    # Find which moves are blocked by this fence
    def forbidden_moves(self):
        if self.is_horizontal:
            return [(Coordinate(self.first.x, self.first.y), Coordinate(self.first.x, self.first.y - 1)),
                    (Coordinate(self.first.x, self.first.y - 1), Coordinate(self.first.x, self.first.y)),
                    (Coordinate(self.first.x + 1, self.first.y), Coordinate(self.first.x + 1, self.first.y - 1)),
                    (Coordinate(self.first.x + 1, self.first.y - 1), Coordinate(self.first.x + 1, self.first.y))]
        else:
            return [(Coordinate(self.first.x, self.first.y), Coordinate(self.first.x - 1, self.first.y)),
                    (Coordinate(self.first.x - 1, self.first.y), Coordinate(self.first.x, self.first.y)),
                    (Coordinate(self.first.x, self.first.y + 1), Coordinate(self.first.x - 1, self.first.y + 1)),
                    (Coordinate(self.first.x - 1, self.first.y + 1), Coordinate(self.first.x, self.first.y + 1))]

    # Check for conflicts between two fences
    def check_conflict(self, other):
        if self.is_horizontal == other.is_horizontal:
            return self.check_overlap(other)
        else:
            return self.check_crossing(other)

    # Check for overlaps between two fences, given that the two have the same orientation
    def check_overlap(self, other):
        if self.is_horizontal:
            return self.first.y == other.first.y and abs(self.first.x - other.first.x) < 2
        else:
            return self.first.x == other.first.x and abs(self.first.y - other.first.y) < 2

    # Check for crossings between two fences, given that the two have opposite orientation
    def check_crossing(self, other):
        if self.is_horizontal:
            return self.first.x + 1 == other.first.x and other.first.y + 1 == self.first.y
        else:
            return other.first.x + 1 == self.first.x and self.first.y + 1 == other.first.y