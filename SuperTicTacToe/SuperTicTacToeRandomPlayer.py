from MinimaxPlayer import MinimaxPlayer
from SuperTicTacToe.SuperTicTacToeMove import SuperTicTacToeMove
import random

MINIMAX_DEPTH = 4 # Do not change this

class SuperTicTacToeRandomPlayer(MinimaxPlayer):
    def __init__(self):
        super().__init__("random", MINIMAX_DEPTH)

    def scoreBoard(self, board, player):
        return random.uniform(-1, 1)

