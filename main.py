from GameEngine import GameEngine
from RandomPlayer import RandomPlayer
from ThirtyOne.ThirtyOnePlayer import ThirtyOnePlayer
from TiePlayer import TiePlayer

from ThirtyOne.ThirtyOneCPUPlayerAdapter import ThirtyOneCPUPlayerAdapter
from ThirtyOne.ThirtyOneHumanPlayer import ThirtyOneHumanPlayer
from ThirtyOne.ThirtyOneBoard import ThirtyOneBoard

#player1 = ThirtyOneHumanPlayer("Dr. Dong")
player1 = ThirtyOneCPUPlayerAdapter(ThirtyOnePlayer())
player2 = ThirtyOneCPUPlayerAdapter(ThirtyOnePlayer())
player3 = ThirtyOneCPUPlayerAdapter(ThirtyOnePlayer())

board = ThirtyOneBoard([player1, player2, player3])

engine = GameEngine(board)

winner = engine.run(True)

print("\n Final scores:")
scores = board.scoreBoard()
for player in scores:
    print(f"Player {player.name}: {scores[player]} points")

if isinstance(winner, TiePlayer):
    print("The game was a tie between " + winner.players.__str__())
else:
    print (f"The winner is player {winner.name}")
