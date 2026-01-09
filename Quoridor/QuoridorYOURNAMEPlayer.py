from collections import deque
from random import Random

from Player import Player
from Quoridor.QuoridorMove import QuoridorMove


class QuoridorYOURNAMEPlayer(Player):
    def __init__(self):
        super().__init__("DijkstraWallPlayer")
        self.random = Random()

    def getMove(self, board):
        our_index = board.findIndex(self)
        our_distance = self._shortest_distance(board, our_index)
        opponent_distances = self._collect_opponent_distances(board, our_index)

        # Get best moves
        best_pawn_move, best_pawn_distance = self._evaluate_pawn_moves(board, our_index)
        best_fence, fence_delay = self._evaluate_best_fence(
            board, our_index, opponent_distances
        )

        # Place walls only if they meaningfully slow opponent and we have moves left
        walls_placed = len(board.all_fences())
        if (
            best_fence
            and fence_delay > 0
            and walls_placed < 8
            and board.fences[our_index] > 1
        ):
            return best_fence

        # Otherwise move forward
        if best_pawn_move:
            return best_pawn_move

        # Fallback
        legal_moves = board.get_legal_moves_for_player(self)
        if legal_moves:
            return self.random.choice(legal_moves)

        legal_fences = board.get_legal_fences(self)
        if legal_fences:
            return self.random.choice(legal_fences)

        return None

    def _evaluate_pawn_moves(self, board, our_index):
        """Find move that gets us closest to goal"""
        legal_moves = board.get_legal_moves_for_player(self)
        if not legal_moves:
            return None, float("inf")

        best_move = None
        best_distance = float("inf")

        for move in legal_moves:
            sim_board = board.clone()
            move.execute(sim_board)
            distance = self._shortest_distance(sim_board, our_index)
            if distance < best_distance:
                best_distance = distance
                best_move = move

        return best_move, best_distance

    def _evaluate_best_fence(self, board, our_index, opponent_distances):
        """Find fence that delays opponent most without hurting us"""
        if board.fences[our_index] == 0:
            return None, 0

        legal_fences = board.get_legal_fences(self)
        if not legal_fences:
            return None, 0

        best_fence = None
        best_delay = 0
        our_pos = board.pawns[our_index]
        our_distance = self._shortest_distance(board, our_index)

        for fence_move in legal_fences:
            # Skip walls behind us
            if self._is_behind(fence_move.coord, our_pos, our_index, board):
                continue

            sim_board = board.clone()
            fence_move.execute(sim_board)

            # Check if it hurts us significantly
            our_after = self._shortest_distance(sim_board, our_index)
            if our_after > our_distance + 1:
                continue

            # Check how much it delays the closest opponent
            max_delay = 0
            for opponent_idx in opponent_distances:
                before = opponent_distances[opponent_idx]
                after = self._shortest_distance(sim_board, opponent_idx)
                if after > before:
                    max_delay = max(max_delay, after - before)

            if max_delay > best_delay:
                best_delay = max_delay
                best_fence = fence_move

        return best_fence, best_delay

    def _collect_opponent_distances(self, board, our_index):
        distances = {}
        for idx in range(len(board.players)):
            if idx != our_index:
                distances[idx] = self._shortest_distance(board, idx)
        return distances

    def _is_behind(self, pos, our_pos, our_index, board):
        """Check if position is behind us"""
        if our_index == 0:
            return pos.y < our_pos.y
        elif our_index == 1 and len(board.pawns) == 2:
            return pos.y > our_pos.y
        elif our_index == 1 and len(board.pawns) == 4:
            return pos.x < our_pos.x
        elif our_index == 2:
            return pos.y > our_pos.y
        elif our_index == 3:
            return pos.x > our_pos.x
        return False

    def _shortest_distance(self, board, player_index):
        """BFS to find shortest path to goal"""
        start = board.pawns[player_index]
        target_check = board.get_target(player_index)
        visited = {start}
        queue = deque([(start, 0)])

        while queue:
            coord, distance = queue.popleft()
            if target_check(coord):
                return distance

            for neighbor in board.get_legal_move_positions(coord):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, distance + 1))

        return float("inf")
