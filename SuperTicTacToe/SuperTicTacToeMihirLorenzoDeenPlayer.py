from MinimaxPlayer import MinimaxPlayer
from SuperTicTacToe.SuperTicTacToeMove import SuperTicTacToeMove
import random

MINIMAX_DEPTH = 4 # Do not change this

class SuperTicTacToeMihirLorenzoDeenPlayer(MinimaxPlayer):
    def __init__(self):
        super().__init__("Mihir Lorenzo & Deen ", MINIMAX_DEPTH)

    def scoreBoard(self, board, player):
        """
        Strategic heuristic function for Ultimate Tic-Tac-Toe.
        Returns a value between -1 and 1 indicating how good the board is for the given player.
        """
        opponent = board.players[0] if board.players[1] == player else board.players[1]
        
        # Check if game is over
        winner = board.getGameEnded()
        if winner == player:
            return 1.0
        elif winner == opponent:
            return -1.0
        
        score = 0.0
        
        # 1. Master board evaluation (most important)
        master_score = self._evaluate_master_board(board, player, opponent)
        score += master_score * 0.5  # Weight: 50%
        
        # 2. Sub-board control and threats
        sub_board_score = self._evaluate_sub_boards(board, player, opponent)
        score += sub_board_score * 0.3  # Weight: 30%
        
        # 3. Positional advantage (center control)
        positional_score = self._evaluate_positional_advantage(board, player, opponent)
        score += positional_score * 0.1  # Weight: 10%
        
        # 4. Forcing move advantage (controlling where opponent must play)
        forcing_score = self._evaluate_forcing_moves(board, player, opponent)
        score += forcing_score * 0.1  # Weight: 10%
        
        # Normalize to [-1, 1] range
        return max(-1.0, min(1.0, score))
    
    def _evaluate_master_board(self, board, player, opponent):
        """Evaluate the master board for wins, threats, and control."""
        master = board.master_board
        score = 0.0
        
        # Count wins
        player_wins = sum(1 for row in master.board for cell in row if cell == player)
        opponent_wins = sum(1 for row in master.board for cell in row if cell == opponent)
        score += (player_wins - opponent_wins) * 0.2
        
        # Evaluate threats (two in a row with empty third)
        player_threats = self._count_threats(master, player)
        opponent_threats = self._count_threats(master, opponent)
        score += (player_threats - opponent_threats) * 0.15
        
        return score
    
    def _evaluate_sub_boards(self, board, player, opponent):
        """Evaluate all sub-boards for control and threats."""
        score = 0.0
        
        for i in range(3):
            for j in range(3):
                sub_board = board.sub_boards[i][j]
                
                # If sub-board is won, it's already counted in master board
                if sub_board.winner == player:
                    continue
                elif sub_board.winner == opponent:
                    continue
                
                # Evaluate threats in this sub-board
                player_threats = self._count_threats(sub_board, player)
                opponent_threats = self._count_threats(sub_board, opponent)
                
                # Weight by position (center is more valuable)
                position_weight = 1.0
                if i == 1 and j == 1:  # Center sub-board
                    position_weight = 1.5
                elif (i + j) % 2 == 0:  # Corner sub-boards
                    position_weight = 1.2
                
                score += (player_threats - opponent_threats) * 0.05 * position_weight
                
                # Count pieces (more pieces = more control)
                player_pieces = sum(1 for row in sub_board.board for cell in row if cell == player)
                opponent_pieces = sum(1 for row in sub_board.board for cell in row if cell == opponent)
                score += (player_pieces - opponent_pieces) * 0.02 * position_weight
        
        return score
    
    def _evaluate_positional_advantage(self, board, player, opponent):
        """Evaluate positional advantages like center control."""
        score = 0.0
        
        # Center sub-board control
        center_board = board.sub_boards[1][1]
        if center_board.winner == player:
            score += 0.3
        elif center_board.winner == opponent:
            score -= 0.3
        else:
            # Check center position within center sub-board
            if center_board.board[1][1] == player:
                score += 0.1
            elif center_board.board[1][1] == opponent:
                score -= 0.1
        
        return score
    
    def _evaluate_forcing_moves(self, board, player, opponent):
        """Evaluate advantage from controlling where opponent must play."""
        score = 0.0
        
        # If we control the current board, opponent is forced to play there
        if board.current_board is not None:
            boardx, boardy = board.get_indices(board.current_board)
            sub_board = board.sub_boards[boardx][boardy]
            
            # If it's our turn and we're forcing opponent into a bad position
            if board.current_player == player:
                # Check if the forced board is advantageous for us
                player_threats = self._count_threats(sub_board, player)
                opponent_threats = self._count_threats(sub_board, opponent)
                if player_threats > opponent_threats:
                    score += 0.1
                elif opponent_threats > player_threats:
                    score -= 0.1
        
        return score
    
    def _count_threats(self, board_obj, player):
        """Count the number of two-in-a-row threats for a player on a board."""
        threats = 0
        board = board_obj.board
        
        # Check rows
        for row in range(3):
            player_count = sum(1 for col in range(3) if board[row][col] == player)
            empty_count = sum(1 for col in range(3) if board[row][col] is None)
            if player_count == 2 and empty_count == 1:
                threats += 1
        
        # Check columns
        for col in range(3):
            player_count = sum(1 for row in range(3) if board[row][col] == player)
            empty_count = sum(1 for row in range(3) if board[row][col] is None)
            if player_count == 2 and empty_count == 1:
                threats += 1
        
        # Check main diagonal
        player_count = sum(1 for i in range(3) if board[i][i] == player)
        empty_count = sum(1 for i in range(3) if board[i][i] is None)
        if player_count == 2 and empty_count == 1:
            threats += 1
        
        # Check anti-diagonal
        player_count = sum(1 for i in range(3) if board[i][2-i] == player)
        empty_count = sum(1 for i in range(3) if board[i][2-i] is None)
        if player_count == 2 and empty_count == 1:
            threats += 1
        
        return threats

