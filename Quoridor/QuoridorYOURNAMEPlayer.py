from Player import Player
from Quoridor.QuoridorMove import QuoridorMove
from Quoridor.QuoridorBoard import QuoridorBoard
from Quoridor.Coordinate import Coordinate
from random import Random

import heapq
import itertools

# find the optimal path via A*
def find_path(board: QuoridorBoard, start: Coordinate, goal: Coordinate) -> list[Coordinate]:
    if start == goal:
        return [start]

    def heuristic(a: Coordinate, b: Coordinate) -> int:
        # manhattan distance
        return abs(a.x - b.x) + abs(a.y - b.y)

    open_heap: list[tuple[int, int, Coordinate]] = []
    tie_breaker = itertools.count()

    came_from: dict[Coordinate, Coordinate] = {}
    g_score: dict[Coordinate, int] = {start: 0}
    best_f_score = heuristic(start, goal)
    heapq.heappush(open_heap, (best_f_score, next(tie_breaker), start))

    closed: set[Coordinate] = set()

    while open_heap:
        _, _, current = heapq.heappop(open_heap)

        if current in closed:
            continue
        closed.add(current)

        if current == goal:
            # reconstruct path
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        current_g = g_score[current]
        for neighbor in board.get_legal_move_positions(current):
            if neighbor in closed:
                continue

            tentative_g = current_g + 1
            if tentative_g < g_score.get(neighbor, 1_000_000_000):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_heap, (f, next(tie_breaker), neighbor))

    return []

class QuoridorYOURNAMEPlayer(Player):
    def __init__(self):
        super().__init__("goon") 

    def getMove(self, board):
        # x >, y v
        index = board.findIndex(self)
        coord = board.pawns[index]
        self.name = "crack " + board.players[index + 1 % len(board.players)].name

        # build goals depending on player index
        goals: list[Coordinate] = []
        if index == 0:
            goals = [Coordinate(x, 8) for x in range(9)]
        elif index == 1:
            if len(board.pawns) == 2:
                goals = [Coordinate(x, 0) for x in range(9)]
            else:
                goals = [Coordinate(8, y) for y in range(9)]
        elif index == 2:
            goals = [Coordinate(x, 0) for x in range(9)]
        elif index == 3:
            goals = [Coordinate(0, y) for y in range(9)]

        shortest_path: list[Coordinate] | None = None
        shortest_path_length = 82

        for goal in goals:
            path = find_path(board, coord, goal)
            if not path:
                continue
            if len(path) < shortest_path_length:
                shortest_path = path
                shortest_path_length = len(path)

        if shortest_path is None:
            print("i couldnt find a path :((")
            raise Exception("no path found")

        return QuoridorMove.move_pawn(shortest_path[1], self)