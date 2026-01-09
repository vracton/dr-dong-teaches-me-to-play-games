from GameEngine import GameEngine
from RandomPlayer import RandomPlayer
from TiePlayer import TiePlayer

# from SuperTicTacToe.SuperTicTacToeBoard import SuperTicTacToeBoard
# from SuperTicTacToe.SuperTicTacToeHumanPlayer import SuperTicTacToeHumanPlayer
# from SuperTicTacToe.SuperTicTacToeYOURNAMEPlayer import SuperTicTacToeYOURNAMEPlayer

from SushiGo.SushiGoBoard import SushiGoBoard
from SushiGo.SushiGoHumanPlayer import SushiGoHumanPlayer
from SushiGo.SushiGoCPUPlayerAdapter import SushiGoCPUPlayerAdapter
from SushiGo.SushiGoKanchiSahooPlayerOld import SushiGoKanchiSahooPlayerOld
from SushiGo.SushiGoKanchiSahooPlayer import SushiGoKanchiSahooPlayer
from SushiGo.SushiGoMihirBenjaminDeenPlayer import SushiGoMihirBenjaminDeenPlayer
from SushiGo.SushiGoAnthonyMacPlayer import SushiGoAnthonyMacPlayer
from SushiGo.SushiGoAidanandRoyPlayer import SushiGoAidanandRoyPlayer
from SushiGo.SushiGoVishnuHarishPlayer import SushiGoVishnuHarishPlayer
from SushiGo.SushiGoArunPlayer import SushiGoArunPlayer
from SushiGo.SushiGoYOURNAMEPlayer import SushiGoYOURNAMEPlayer
from SushiGo.Card import Card

all_players = []

def set_seeds():
    scores = run_game(all_players)

    run_many_times(all_players, 10)
    # sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))

    # for item in sorted_scores.items():
    #     print(f"Player {item[0].name}: {item[1]} points")

def run_many_times(players, nTimes, output = True):
    score_count = {player: 0 for player in players}
    for i in range(nTimes):
        scores = run_game(players, output)
        sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
        counter = len(players)
        for item in sorted_scores.items():
            score_count[item[0]] += counter
            counter -= 1
            
    score_count = dict(sorted(score_count.items(), key=lambda item: item[1], reverse=True))
    for player in score_count:
        print(f"Player {player.name}: {score_count[player]} total points over {nTimes} games")

def run_game(players, print = True):
    board = SushiGoBoard(players)
    board.output = print

    engine = GameEngine(board)

    engine.run(True)
    #print(f"Winner: {winner.name}")
    scores = board.scoreBoard()
    return scores

def default_run(output = True):
    player1 = RandomPlayer("Random bot 4")
    player2 = RandomPlayer("Random bot 1")
    player3 = RandomPlayer("Random bot 2")
    player4 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer())
    #player4 = SushiGoHumanPlayer("Atharv")
    player5 = RandomPlayer("Random bot 3")

    scores = run_game([player1, player2, player3, player4, player5], output)

    for player in scores:
        print(f"Player {player.name}: {scores[player]} points")

def run_tests(output = True):
    # player3 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer("Tempura"))
    # player3.player.priorities[Card.Type.SASHIMI] = 0
    # player3.player.priorities[Card.Type.WASABI] = 1
    # player3.player.priorities[Card.Type.SQUID_NIGIRI] = 2
    # player3.player.priorities[Card.Type.PUDDING] = 3
    # player3.player.priorities[Card.Type.TRIPLE_MAKI] = 4
    # player3.player.priorities[Card.Type.DOUBLE_MAKI] = 5
    # player3.player.priorities[Card.Type.TEMPURA] = 6
    # player3.player.priorities[Card.Type.SALMON_NIGIRI] = 7
    # player3.player.priorities[Card.Type.DUMPLING] = 8
    # player3.player.priorities[Card.Type.EGG_NIGIRI] = 9
    # player3.player.priorities[Card.Type.CHOPSTICKS] = 10
    # player3.player.priorities[Card.Type.SINGLE_MAKI] = 11

    # player4 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer("Pudding"))
    # player4.player.priorities[Card.Type.WASABI] = 0
    # player4.player.priorities[Card.Type.SQUID_NIGIRI] = 1
    # player4.player.priorities[Card.Type.TRIPLE_MAKI] = 2
    # player4.player.priorities[Card.Type.SALMON_NIGIRI] = 3
    # player4.player.priorities[Card.Type.DUMPLING] = 4
    # player4.player.priorities[Card.Type.PUDDING] = 5
    # player4.player.priorities[Card.Type.SINGLE_MAKI] = 6
    # player4.player.priorities[Card.Type.CHOPSTICKS] = 7
    # player4.player.priorities[Card.Type.EGG_NIGIRI] = 8
    # player4.player.priorities[Card.Type.SASHIMI] = 9
    # player4.player.priorities[Card.Type.DOUBLE_MAKI] = 10
    # player4.player.priorities[Card.Type.TEMPURA] = 11

    # player5 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer("Palantir"))
    # player5.player.priorities[Card.Type.SQUID_NIGIRI] = 0
    # player5.player.priorities[Card.Type.DUMPLING] = 1
    # player5.player.priorities[Card.Type.SALMON_NIGIRI] = 2
    # player5.player.priorities[Card.Type.WASABI] = 3
    # player5.player.priorities[Card.Type.PUDDING] = 4
    # player5.player.priorities[Card.Type.TRIPLE_MAKI] = 5
    # player5.player.priorities[Card.Type.TEMPURA] = 6
    # player5.player.priorities[Card.Type.SASHIMI] = 7
    # player5.player.priorities[Card.Type.SINGLE_MAKI] = 8
    # player5.player.priorities[Card.Type.DOUBLE_MAKI] = 9
    # player5.player.priorities[Card.Type.EGG_NIGIRI] = 10
    # player5.player.priorities[Card.Type.CHOPSTICKS] = 11



    # player1 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer("Sashimi"))
    # player1.player.priorities[Card.Type.SASHIMI] = 0
    # player1.player.priorities[Card.Type.PUDDING] = 1
    # player1.player.priorities[Card.Type.SQUID_NIGIRI] = 2
    # player1.player.priorities[Card.Type.EGG_NIGIRI] = 3
    # player1.player.priorities[Card.Type.SALMON_NIGIRI] = 4
    # player1.player.priorities[Card.Type.WASABI] = 5
    # player1.player.priorities[Card.Type.DUMPLING] = 6
    # player1.player.priorities[Card.Type.TRIPLE_MAKI] = 7
    # player1.player.priorities[Card.Type.TEMPURA] = 8
    # player1.player.priorities[Card.Type.SINGLE_MAKI] = 9
    # player1.player.priorities[Card.Type.DOUBLE_MAKI] = 10
    # player1.player.priorities[Card.Type.CHOPSTICKS] = 11

    player1 = SushiGoCPUPlayerAdapter(SushiGoKanchiSahooPlayer("Kanchi + Sahoo"))
    player2 = SushiGoCPUPlayerAdapter(SushiGoArunPlayer("Arun"))
    player3 = SushiGoCPUPlayerAdapter(SushiGoMihirBenjaminDeenPlayer("Mihir + Benjamin + Deen"))
    player4 = SushiGoCPUPlayerAdapter(SushiGoVishnuHarishPlayer("Vishnu + Harish"))
    player5 = SushiGoCPUPlayerAdapter(SushiGoAnthonyMacPlayer("Anthony + Mac"))
    player6 = SushiGoCPUPlayerAdapter(SushiGoAidanandRoyPlayer("Aidan + Roy"))

    players = [player1, player2, player3, player4, player5, player6]

    scores = run_many_times(players, 1000, output)

if __name__ == "__main__":
    #default_run()
    #set_seeds()
    run_tests(True)