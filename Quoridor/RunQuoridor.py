from GameEngine import GameEngine
from RandomPlayer import RandomPlayer
from TiePlayer import TiePlayer

from Quoridor.QuoridorBoard import QuoridorBoard
from Quoridor.QuoridorHumanPlayer import QuoridorHumanPlayer
from Quoridor.QuoridorYOURNAMEPlayer import QuoridorYOURNAMEPlayer
from Quoridor.QuoridorAggressiveWallPlayer import QuoridorAggressiveWallPlayer
from Quoridor.QuoridorBlockerPlayer import QuoridorBlockerPlayer
from Quoridor.QuoridorSahooPlayer import QuoridorSahooPlayer


def run_game(players, print = True):
    board = QuoridorBoard(players)
    board.output = print

    engine = GameEngine(board)

    engine.run(True)
    #print(f"Winner: {winner.name}")
    scores = board.scoreBoard()
    return scores

def default_run(output = True):
    player1 = QuoridorSahooPlayer()
    player2 = QuoridorAggressiveWallPlayer()
    player3 = RandomPlayer("Random bot 2")
    player4 = QuoridorYOURNAMEPlayer()

    scores = run_game([player2, player1], output)

    for player in scores:
        print(f"Player {player.name}: {scores[player]} points")

def run_quoridor():
    default_run()