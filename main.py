from GameEngine import GameEngine
from RandomPlayer import RandomPlayer
from TiePlayer import TiePlayer

# from SuperTicTacToe.SuperTicTacToeBoard import SuperTicTacToeBoard
# from SuperTicTacToe.SuperTicTacToeHumanPlayer import SuperTicTacToeHumanPlayer
# from SuperTicTacToe.SuperTicTacToeYOURNAMEPlayer import SuperTicTacToeYOURNAMEPlayer

from SushiGo.SushiGoBoard import SushiGoBoard
from SushiGo.SushiGoHumanPlayer import SushiGoHumanPlayer
from SushiGo.SushiGoCPUPlayerAdapter import SushiGoCPUPlayerAdapter
from SushiGo.SushiGoYOURNAMEPlayer import SushiGoYOURNAMEPlayer
from SushiGo.SushiGoRLPlayer import SushiGoRLPlayer
from SushiGo.SushiGoKanchiSahooPlayer import SushiGoKanchiSahooPlayer
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
    player1 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer("Tempura"))
    player1.player.priorities[Card.Type.SASHIMI] = 0
    player1.player.priorities[Card.Type.WASABI] = 1
    player1.player.priorities[Card.Type.SQUID_NIGIRI] = 2
    player1.player.priorities[Card.Type.PUDDING] = 3
    player1.player.priorities[Card.Type.TRIPLE_MAKI] = 4
    player1.player.priorities[Card.Type.DOUBLE_MAKI] = 5
    player1.player.priorities[Card.Type.TEMPURA] = 6
    player1.player.priorities[Card.Type.SALMON_NIGIRI] = 7
    player1.player.priorities[Card.Type.DUMPLING] = 8
    player1.player.priorities[Card.Type.EGG_NIGIRI] = 9
    player1.player.priorities[Card.Type.CHOPSTICKS] = 10
    player1.player.priorities[Card.Type.SINGLE_MAKI] = 11

    player2 = SushiGoCPUPlayerAdapter(SushiGoKanchiSahooPlayer())

    player3 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer("Palantir"))
    player3.player.priorities[Card.Type.SQUID_NIGIRI] = 0
    player3.player.priorities[Card.Type.DUMPLING] = 1
    player3.player.priorities[Card.Type.SALMON_NIGIRI] = 2
    player3.player.priorities[Card.Type.WASABI] = 3
    player3.player.priorities[Card.Type.PUDDING] = 4
    player3.player.priorities[Card.Type.TRIPLE_MAKI] = 5
    player3.player.priorities[Card.Type.TEMPURA] = 6
    player3.player.priorities[Card.Type.SASHIMI] = 7
    player3.player.priorities[Card.Type.SINGLE_MAKI] = 8
    player3.player.priorities[Card.Type.DOUBLE_MAKI] = 9
    player3.player.priorities[Card.Type.EGG_NIGIRI] = 10
    player3.player.priorities[Card.Type.CHOPSTICKS] = 11
    
    # Load trained RL player
    rl = SushiGoRLPlayer()
    rl.load("SushiGo/rl_qtable.pkl")  # Load trained Q-table
    rl.training = False  # Disable exploration
    rl.epsilon = 0.0     # Pure exploitation
    player4 = SushiGoCPUPlayerAdapter(rl)
    
    player5 = RandomPlayer("Random bot 3")

    scores = run_game([player1, player2, player3, player4, player5], output)

    # Check if RL won
    rl_score = scores[player4]
    max_score = max(scores.values())
    won = rl_score == max_score
    
    if output:
        for player in scores:
            print(f"Player {player.name}: {scores[player]} points")
    
    return won, rl_score

def run_tests(output = True):
    player1 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer("Sashimi"))
    player1.player.priorities[Card.Type.SASHIMI] = 0
    player2 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer("Dumpling"))
    player2.player.priorities[Card.Type.DUMPLING] = 0
    player3 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer("Tempura"))
    player3.player.priorities[Card.Type.TEMPURA] = 0
    
    # Load trained RL player
    rl = SushiGoRLPlayer()
    rl.load("SushiGo/rl_qtable.pkl")
    rl.training = False
    rl.epsilon = 0.0
    player4 = SushiGoCPUPlayerAdapter(rl)
    
    player5 = RandomPlayer("Random bot")

    players = [player1, player2, player3, player4, player5]

    scores = run_many_times(players, 100, output)

if __name__ == "__main__":
    # Run multiple games to see win rate for all players
    games = 100
    
    # Track wins per player name
    win_counts = {}
    score_totals = {}
    
    for i in range(games):
        won, score = default_run(output=False)
    
    # Run with tracking
    from collections import defaultdict
    win_counts = defaultdict(int)
    score_totals = defaultdict(list)
    
    for i in range(games):
        # Recreate players for each game to get fresh scores
        player1 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer("Tempura"))
        player1.player.priorities[Card.Type.SASHIMI] = 0
        player1.player.priorities[Card.Type.WASABI] = 1
        player1.player.priorities[Card.Type.SQUID_NIGIRI] = 2
        player1.player.priorities[Card.Type.PUDDING] = 3
        player1.player.priorities[Card.Type.TRIPLE_MAKI] = 4
        player1.player.priorities[Card.Type.DOUBLE_MAKI] = 5
        player1.player.priorities[Card.Type.TEMPURA] = 6
        player1.player.priorities[Card.Type.SALMON_NIGIRI] = 7
        player1.player.priorities[Card.Type.DUMPLING] = 8
        player1.player.priorities[Card.Type.EGG_NIGIRI] = 9
        player1.player.priorities[Card.Type.CHOPSTICKS] = 10
        player1.player.priorities[Card.Type.SINGLE_MAKI] = 11

        player2 = SushiGoCPUPlayerAdapter(SushiGoKanchiSahooPlayer())

        player3 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer("Palantir"))
        player3.player.priorities[Card.Type.SQUID_NIGIRI] = 0
        player3.player.priorities[Card.Type.DUMPLING] = 1
        player3.player.priorities[Card.Type.SALMON_NIGIRI] = 2
        player3.player.priorities[Card.Type.WASABI] = 3
        player3.player.priorities[Card.Type.PUDDING] = 4
        player3.player.priorities[Card.Type.TRIPLE_MAKI] = 5
        player3.player.priorities[Card.Type.TEMPURA] = 6
        player3.player.priorities[Card.Type.SASHIMI] = 7
        player3.player.priorities[Card.Type.SINGLE_MAKI] = 8
        player3.player.priorities[Card.Type.DOUBLE_MAKI] = 9
        player3.player.priorities[Card.Type.EGG_NIGIRI] = 10
        player3.player.priorities[Card.Type.CHOPSTICKS] = 11
        
        rl = SushiGoRLPlayer()
        rl.load("SushiGo/rl_qtable.pkl")
        rl.training = False
        rl.epsilon = 0.0
        player4 = SushiGoCPUPlayerAdapter(rl)
        
        player5 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer("netenyahoo"))
        player5.player.priorities[Card.Type.SQUID_NIGIRI] = 0
        player5.player.priorities[Card.Type.DUMPLING] = 1
        player5.player.priorities[Card.Type.SALMON_NIGIRI] = 2
        player5.player.priorities[Card.Type.TRIPLE_MAKI] = 3
        player5.player.priorities[Card.Type.PUDDING] = 4
        player5.player.priorities[Card.Type.WASABI] = 5
        player5.player.priorities[Card.Type.DOUBLE_MAKI] = 6
        player5.player.priorities[Card.Type.SINGLE_MAKI] = 7
        player5.player.priorities[Card.Type.SASHIMI] = 8
        player5.player.priorities[Card.Type.EGG_NIGIRI] = 9
        player5.player.priorities[Card.Type.TEMPURA] = 10
        player5.player.priorities[Card.Type.CHOPSTICKS] = 11
        
        players = [player1, player2, player3, player4, player5]
        scores = run_game(players, False)
        
        max_score = max(scores.values())
        for player in players:
            name = player.name
            score_totals[name].append(scores[player])
            if scores[player] == max_score:
                win_counts[name] += 1
    
    print(f"\nResults over {games} games:")
    print("-" * 50)
    for name in score_totals:
        avg_score = sum(score_totals[name]) / len(score_totals[name])
        win_rate = win_counts[name] / games * 100
        print(f"{name:15} | Win rate: {win_rate:5.1f}% | Avg score: {avg_score:.1f}")
    print("-" * 50)
    print(f"Random baseline: {100/len(score_totals):.1f}%")