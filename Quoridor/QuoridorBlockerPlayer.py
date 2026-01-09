from Player import Player
from Quoridor.QuoridorMove import QuoridorMove
from collections import deque
import random


class QuoridorBlockerPlayer(Player):
    def __init__(self, name="Blocker"):
        super().__init__(name)

    def shortest_path_length(self, board, player_index):
        start = board.pawns[player_index]
        target_test = board.get_target(player_index)
        q = deque([(start, 0)])
        visited = {start}
        while q:
            node, dist = q.popleft()
            if target_test(node):
                return dist
            for neigh in board.get_legal_move_positions(node):
                if neigh not in visited:
                    visited.add(neigh)
                    q.append((neigh, dist + 1))
        return None

    def choose_centered_next_step(self, board, player_index):
        # Returns a Coordinate for the next pawn move preferring center when tied
        start = board.pawns[player_index]
        neighbors = board.get_legal_move_positions(start)
        if not neighbors:
            return None

        best_dist = None
        best_neighbors = []
        for neigh in neighbors:
            cloned = board.clone()
            cloned.pawns[player_index] = neigh
            d = self.shortest_path_length(cloned, player_index)
            d_val = float('inf') if d is None else d
            if best_dist is None or d_val < best_dist:
                best_dist = d_val
                best_neighbors = [neigh]
            elif d_val == best_dist:
                best_neighbors.append(neigh)

        # If multiple neighbors tie on distance, choose the one closest to center (4,4)
        if len(best_neighbors) == 1:
            return best_neighbors[0]
        center_x, center_y = 4, 4
        def center_dist(c):
            return abs(c.x - center_x) + abs(c.y - center_y)

        best_neighbors.sort(key=center_dist)
        return best_neighbors[0]

    def getMove(self, board):
        # If we have no fences left, move using shortest-path (Dijkstra/BFS)
        if board.fences[board.findIndex(self)] == 0:
            # Move pawn along its shortest path
            my_index = board.findIndex(self)
            start = board.pawns[my_index]
            parents = {start: None}
            q = deque([start])
            target_test = board.get_target(my_index)
            found = None
            while q:
                node = q.popleft()
                if target_test(node):
                    found = node
                    break
                for neigh in board.get_legal_move_positions(node):
                    if neigh not in parents:
                        parents[neigh] = node
                        q.append(neigh)

            if found is not None:
                # Prefer next step that keeps us centered when multiple equal routes exist
                next_step = self.choose_centered_next_step(board, my_index)
                if next_step is not None:
                    return QuoridorMove.move_pawn(next_step, self)

            # final fallback
            possible = board.getPossibleMoves()
            return random.choice(possible) if possible else None

        # Evaluate fences by total shortest-path increase for all other players (maximize total distance)
        my_index = board.findIndex(self)

        # Compute original total distance for all players except self
        original_total = 0
        for i in range(len(board.pawns)):
            if i == my_index:
                continue
            d = self.shortest_path_length(board, i)
            if d is None:
                d = float('inf')
            original_total += d

        legal_fences = board.get_legal_fences(self)
        best_moves = []
        best_total = original_total

        MIN_GAIN = 3

        for fence_move in legal_fences:
            cloned = board.clone()
            cloned.doMove(fence_move)
            new_total = 0
            for i in range(len(cloned.pawns)):
                if i == my_index:
                    continue
                d = self.shortest_path_length(cloned, i)
                if d is None:
                    d = float('inf')
                new_total += d

            if new_total > best_total:
                best_total = new_total
                best_moves = [fence_move]
            elif new_total == best_total:
                best_moves.append(fence_move)

        best_gain = best_total - original_total

        # Only place a wall if it improves total distances by at least MIN_GAIN
        if best_moves and best_gain >= MIN_GAIN:
            return random.choice(best_moves)

        # Evaluate whether an opponent (the Dijkstra player) can place a fence
        # that would increase their shortest-path by more than our best fence
        opp_index = None
        for i, p in enumerate(board.players):
            if p != self and hasattr(p, 'name') and p.name == "DijkstraPlayer":
                opp_index = i
                break

        if opp_index is not None:
            orig_opp_dist = self.shortest_path_length(board, opp_index)
            orig_opp_val = float('inf') if orig_opp_dist is None else orig_opp_dist

            opp_legal = board.get_legal_fences(board.players[opp_index])
            opp_best_gain = 0
            opp_best_moves = []
            for opp_move in opp_legal:
                cloned = board.clone()
                cloned.doMove(opp_move)
                new_dist = self.shortest_path_length(cloned, opp_index)
                new_val = float('inf') if new_dist is None else new_dist
                gain = new_val - orig_opp_val
                if gain > opp_best_gain:
                    opp_best_gain = gain
                    opp_best_moves = [opp_move]
                elif gain == opp_best_gain:
                    opp_best_moves.append(opp_move)

            blocker_gain = best_total - original_total

            if opp_best_gain > blocker_gain and opp_best_moves:
                # Try to find our fence placements that would make the opponent's best moves illegal
                blocking_candidates = []
                for my_move in legal_fences:
                    cloned = board.clone()
                    cloned.doMove(my_move)
                    opp_after = cloned.get_legal_fences(board.players[opp_index])
                    # if any of opp_best_moves is missing from opp_after then my_move blocks it
                    blocks = False
                    for opp_move in opp_best_moves:
                        still_available = False
                        for m in opp_after:
                            try:
                                if m.coord == opp_move.coord and getattr(m, 'is_horizontal', False) == getattr(opp_move, 'is_horizontal', False):
                                    still_available = True
                                    break
                            except Exception:
                                continue
                        if not still_available:
                            blocks = True
                            break
                    if blocks:
                        blocking_candidates.append(my_move)

                if blocking_candidates:
                    # choose blocking candidate that also gives us best total increase
                    best_block = None
                    best_block_total = best_total
                    for my_move in blocking_candidates:
                        cloned = board.clone()
                        cloned.doMove(my_move)
                        new_total = 0
                        for i in range(len(cloned.pawns)):
                            if i == my_index:
                                continue
                            d = self.shortest_path_length(cloned, i)
                            if d is None:
                                d = float('inf')
                            new_total += d
                        if new_total > best_block_total:
                            best_block_total = new_total
                            best_block = my_move
                    if best_block:
                        return best_block
                    return random.choice(blocking_candidates)

        # No beneficial fence found: fallback to moving pawn along its shortest path
        # Reuse a simple BFS pathfinder to move pawn one step towards its goal
        my_index = board.findIndex(self)
        start = board.pawns[my_index]
        parents = {start: None}
        q = deque([start])
        target_test = board.get_target(my_index)
        found = None
        while q:
            node = q.popleft()
            if target_test(node):
                found = node
                break
            for neigh in board.get_legal_move_positions(node):
                if neigh not in parents:
                    parents[neigh] = node
                    q.append(neigh)

        if found is not None:
            # prefer centered next step when multiple equal routes
            next_step = self.choose_centered_next_step(board, my_index)
            if next_step is not None:
                return QuoridorMove.move_pawn(next_step, self)

        # Final fallback: any legal move
        possible = board.getPossibleMoves()
        return random.choice(possible) if possible else None
