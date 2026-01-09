from GameEngine import GameEngine
from RandomPlayer import RandomPlayer
from TiePlayer import TiePlayer

from Quoridor.QuoridorBoard import QuoridorBoard
from Quoridor.QuoridorHumanPlayer import QuoridorHumanPlayer
from Quoridor.QuoridorYOURNAMEPlayer import QuoridorYOURNAMEPlayer

def run_game(players, print = True):
    board = QuoridorBoard(players)
    board.output = print

    engine = GameEngine(board)

    engine.run(True)
    #print(f"Winner: {winner.name}")
    scores = board.scoreBoard()
    return scores

def default_run(output = True):
    player1 = QuoridorHumanPlayer("Dr. Dong")
    player2 = RandomPlayer("Random bot 1")
    player3 = RandomPlayer("Random bot 2")
    player4 = QuoridorYOURNAMEPlayer()

    scores = run_game([player1, player2], output)

    for player in scores:
        print(f"Player {player.name}: {scores[player]} points")

def run_quoridor():
    default_run()