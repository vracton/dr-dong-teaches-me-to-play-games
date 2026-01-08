from MinimaxPlayer import MinimaxPlayer
from SuperTicTacToe.SuperTicTacToeMove import SuperTicTacToeMove
from SuperTicTacToe.SingleTicTacToeBoard import SingleTicTacToeBoard
from SuperTicTacToe.SuperTicTacToeBoard import SuperTicTacToeBoard
from Player import Player
import random

def singleBoardScore(board: SingleTicTacToeBoard, player: Player) -> float:
    def f(n):
        if n == 0:
            return 0.0
        elif n == 1:
            return 0.2
        elif n == 2:
            return 0.4
        elif n == 3:
            return 1000.0
        return 0

    score = 0

    # rows
    for i in range(3):
        numInRow = 0
        for j in range(3):
            if board.board[i][j] == player:
                numInRow += 1
            elif board.board[i][j] is not None:
                numInRow = 0
                break
        score += f(numInRow)

    # cols
    for j in range(3):
        numInCol = 0
        for i in range(3):
            if board.board[i][j] == player:
                numInCol += 1
            elif board.board[i][j] is not None:
                numInCol = 0
                break
        score += f(numInCol)

    # diagonals
    numInDiag = 0
    for i in range(3):
        if board.board[i][i] == player:
            numInDiag += 1
        elif board.board[i][i] is not None:
            numInDiag = 0
            break
    score += f(numInDiag)
    
    numinAntiDiag = 0
    for i in range(3):
        if board.board[i][2 - i] == player:
            numinAntiDiag += 1
        elif board.board[i][2 - i] is not None:
            numinAntiDiag = 0
            break
    score += f(numinAntiDiag)

    return score / 8.0;


def opponentOf(board: SuperTicTacToeBoard, player: Player) -> Player:
    for p in board.players:
        if p != player:
            return p
    return player


MINIMAX_DEPTH = 4 # Do not change this

class SuperTicTacToeYOURNAMEPlayer(MinimaxPlayer):
    def __init__(self):
        super().__init__("Kanchi + Sahoo", MINIMAX_DEPTH)

    def scoreBoard(self, board, player):
        opponent = opponentOf(board, player)
        total_score = 0

        # calculate local boards (9 sub-boards)
        local_score = 0
        counted = 0
        for i in range(3):
            for j in range(3):
                singleBoard = board.sub_boards[i][j]
                if singleBoard.winner is not None or singleBoard.is_full:
                    continue
                local_score += (singleBoardScore(singleBoard, player) - singleBoardScore(singleBoard, opponent))
                counted += 1;
        
        if counted > 0:
            local_score /= counted

        # big board (1 master board)
        macro_score = (singleBoardScore(board.master_board, player) - singleBoardScore(board.master_board, opponent))

        # emphasize the current sub-board, if any
        current_score = 0
        if board.current_board is not None and board.current_board.winner is None and not board.current_board.is_full:
            current_score = (singleBoardScore(board.current_board, player) - singleBoardScore(board.current_board, opponent))

        total_score = (0.50 * local_score) + (0.40 * macro_score) + (0.10 * current_score)
        
        return total_score
