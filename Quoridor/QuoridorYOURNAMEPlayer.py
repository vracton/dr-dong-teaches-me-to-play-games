from collections import deque
from random import Random

from Player import Player
from Quoridor.QuoridorMove import QuoridorMove


class QuoridorYOURNAMEPlayer(Player):
    def __init__(self):
        super().__init__("Kanchi + Sahoo")
        self.random = Random()

    def getMove(self, board):
        our_index = board.findIndex(self)
        our_distance = self._shortest_distance(board, our_index)
        opponent_distances = self._collect_opponent_distances(board, our_index)

        # Check if we're prone to being blocked (count available paths)
        our_path_count = self._count_shortest_paths(board, our_index)
        vulnerable = our_path_count <= 2

        walls_placed = len(board.all_fences())
        our_walls_left = board.fences[our_index]

        # Calculate game phase: 0.0 = start, 1.0 = late game
        # Defensive priority increases over time
        game_phase = min(1.0, walls_placed / 12.0)

        # Get best moves
        best_pawn_move, best_pawn_distance = self._evaluate_pawn_moves(board, our_index)
        best_fence, fence_gain = self._evaluate_best_fence(
            board, our_index, opponent_distances
        )

        # Strategy from strategy.txt:
        # 1. Early game (first couple moves): Aggressive walls for tempo, maximize enemy time
        if walls_placed < 3 and best_fence and fence_gain >= 2:
            return best_fence

        # 2. Check if vulnerable to being blocked - priority increases with game phase
        # If we have 2 exits and prone to blocking, place defensive wall
        if vulnerable and game_phase > 0.3:
            defensive_wall = self._find_defensive_wall(board, our_index)
            if defensive_wall:
                return defensive_wall

        # 3. Mid-game: prioritize movement over walls (tempo), only wall if highly beneficial
        if game_phase < 0.7 and best_fence and fence_gain >= 4:
            return best_fence

        # 4. Late game: sparse defensive walls only when absolutely necessary
        if game_phase >= 0.7 and vulnerable and best_fence and fence_gain >= 2:
            return best_fence

        # Always prefer moving forward (tempo priority from strategy.txt)
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
        """Find fence that maximizes total opponent distance - full optimization near enemy"""
        if board.fences[our_index] == 0:
            return None, 0

        legal_fences = board.get_legal_fences(self)
        if not legal_fences:
            return None, 0

        # Calculate original total distance for all opponents
        original_total = sum(opponent_distances.values())

        best_fence = None
        best_new_total = original_total
        best_gain = 0

        for fence_move in legal_fences:
            sim_board = board.clone()
            fence_move.execute(sim_board)

            # Calculate new total distance for all opponents after this fence
            new_total = 0
            for opponent_idx in opponent_distances:
                after = self._shortest_distance(sim_board, opponent_idx)
                if after == float("inf"):
                    after = 999  # Treat infinity as very large but not infinite
                new_total += after

            gain = new_total - original_total

            if new_total > best_new_total:
                best_new_total = new_total
                best_fence = fence_move
                best_gain = gain

        return best_fence, best_gain

    def _find_defensive_wall(self, board, our_index):
        """Find defensive wall that blocks the longer exit when we have 2 paths"""
        if board.fences[our_index] == 0:
            return None

        # Get all paths to goal
        paths = self._find_multiple_paths(board, our_index, max_paths=3)

        # If we don't have exactly 2 distinct paths, no defensive wall needed
        if len(paths) != 2:
            return None

        # Identify the longer path
        path_lengths = [(i, len(path)) for i, path in enumerate(paths)]
        path_lengths.sort(key=lambda x: x[1], reverse=True)
        longer_path_idx = path_lengths[0][0]
        longer_path = paths[longer_path_idx]

        # Try to find a fence that blocks the longer path without blocking the shorter one
        legal_fences = board.get_legal_fences(self)
        our_distance = self._shortest_distance(board, our_index)

        for fence_move in legal_fences:
            sim_board = board.clone()
            fence_move.execute(sim_board)

            # Check if this fence significantly increases our distance (blocks a path)
            new_distance = self._shortest_distance(sim_board, our_index)

            # We want a fence that increases our distance slightly (blocks long path)
            # but not too much (keeps short path open)
            if new_distance == our_distance + 1:
                # This likely blocked the longer path while keeping shorter one
                return fence_move

        return None

    def _find_multiple_paths(self, board, player_index, max_paths=3):
        """Find multiple distinct shortest paths to goal"""
        start = board.pawns[player_index]
        target_check = board.get_target(player_index)

        # Find shortest distance first
        min_dist = self._shortest_distance(board, player_index)
        if min_dist == float("inf"):
            return []

        # BFS to find all paths at shortest distance
        paths = []
        queue = deque([(start, [start])])

        while queue and len(paths) < max_paths:
            coord, path = queue.popleft()

            if len(path) - 1 > min_dist:
                continue

            if target_check(coord):
                if len(path) - 1 == min_dist:
                    paths.append(path)
                continue

            for neighbor in board.get_legal_move_positions(coord):
                if neighbor not in path:
                    queue.append((neighbor, path + [neighbor]))

        return paths

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

    def _count_shortest_paths(self, board, player_index):
        """Count number of shortest paths to goal using BFS"""
        start = board.pawns[player_index]
        target_check = board.get_target(player_index)
        visited = set()
        queue = deque([(start, 0)])
        path_counts = {start: 1}
        min_distance = float("inf")
        total_paths = 0

        while queue:
            coord, distance = queue.popleft()
            if coord in visited:
                continue
            visited.add(coord)

            if target_check(coord):
                if distance < min_distance:
                    min_distance = distance
                    total_paths = path_counts[coord]
                elif distance == min_distance:
                    total_paths += path_counts[coord]
                continue

            for neighbor in board.get_legal_move_positions(coord):
                if neighbor not in visited:
                    if neighbor not in path_counts:
                        path_counts[neighbor] = 0
                        queue.append((neighbor, distance + 1))
                    if distance + 1 <= min_distance or min_distance == float("inf"):
                        path_counts[neighbor] += path_counts[coord]

        return total_paths if total_paths > 0 else 1
