import argparse
import os
import random

from GameEngine import GameEngine
from RandomPlayer import RandomPlayer
from SushiGo.SushiGoBoard import SushiGoBoard
from SushiGo.SushiGoCPUPlayerAdapter import SushiGoCPUPlayerAdapter
from SushiGo.SushiGoRLPlayer import SushiGoRLPlayer
from SushiGo.SushiGoYOURNAMEPlayer import SushiGoYOURNAMEPlayer
from SushiGo.SushiGoKanchiSahooPlayer import SushiGoKanchiSahooPlayer
from SushiGo.Card import Card


def create_priority_opponents():
    """Create the same priority-based opponents used in main.py"""
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
    
    return [player1, player2, player3]


def run_one_game_with_training(board: SushiGoBoard, rl_adapter: SushiGoCPUPlayerAdapter, rl: SushiGoRLPlayer, output: bool = False):
    """Run a single game, applying shaping rewards after every card reveal.

    This gives ~21 reward signals per game (one per turn) instead of just 3
    (one per round), making credit assignment much easier.
    """
    board.output = output

    # Track the RL player's played cards to detect new cards after reveals
    prev_rl_cards = list(board.played_cards.get(rl_adapter, []))

    while not board.getGameEnded():
        # Check if a reveal just happened (cards_to_be_played is empty for all)
        was_pending = any(len(board.cards_to_be_played.get(p, [])) > 0 for p in board.players)

        try:
            move = board.getNextMove()
        except Exception:
            move = random.choice(board.getPossibleMoves())
        if not board.checkIsValid(move):
            move = random.choice(board.getPossibleMoves())

        board = board.doMove(move)

        # After doMove, check if cards were just revealed (transition from pending -> not pending)
        is_pending = any(len(board.cards_to_be_played.get(p, [])) > 0 for p in board.players)

        if was_pending and not is_pending:
            # Cards just revealed! Compute shaping reward for RL player
            new_rl_cards = list(board.played_cards.get(rl_adapter, []))
            shaping = rl.compute_shaping_reward(prev_rl_cards, new_rl_cards)
            rl.observe_reward(shaping)
            prev_rl_cards = new_rl_cards

    return board


def run_one_game(players, output: bool = False):
    board = SushiGoBoard(players)
    board.output = output
    engine = GameEngine(board)
    engine.run(visualize=False)
    return board


def main():
    parser = argparse.ArgumentParser(description="Train a Sushi Go RL player (episodic tabular learning).")
    parser.add_argument("--episodes", type=int, default=2000)
    parser.add_argument("--opponents", type=int, default=4, help="Number of RandomPlayer opponents (for random mode).")
    parser.add_argument("--mode", type=str, default="selfplay", choices=["random", "selfplay", "priority", "mixed"],
                        help="Training mode: random, selfplay, priority (vs main.py bots), or mixed")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--epsilon", type=float, default=0.2)
    parser.add_argument("--epsilon-min", type=float, default=0.02)
    parser.add_argument("--epsilon-decay", type=float, default=0.999)
    parser.add_argument("--save", type=str, default=os.path.join("SushiGo", "rl_qtable.pkl"))
    parser.add_argument("--load", type=str, default=None)
    parser.add_argument("--report-every", type=int, default=100)
    args = parser.parse_args()

    rl = SushiGoRLPlayer(
        name="RL",
        alpha=args.alpha,
        epsilon=args.epsilon,
        epsilon_min=args.epsilon_min,
        epsilon_decay=args.epsilon_decay,
    )

    if args.load:
        rl.load(args.load)
        # Override epsilon from command line when loading
        rl.epsilon = args.epsilon
        rl.epsilon_min = args.epsilon_min

    rl_adapter = SushiGoCPUPlayerAdapter(rl)

    print(f"Training mode: {args.mode}")
    
    recent_rewards = []
    recent_wins = []
    recent_ranks = []
    for ep in range(1, args.episodes + 1):
        rl.start_episode()

        # Create opponents based on mode
        if args.mode == "random":
            opponents = [RandomPlayer(f"Random {i}") for i in range(args.opponents)]
            players = [rl_adapter, *opponents]
        
        elif args.mode == "selfplay":
            # Self-play: copies of RL + one random
            rl_copies = []
            for i in range(4):
                rl_copy = SushiGoRLPlayer(name=f"RL-copy-{i}")
                rl_copy._q = rl._q
                rl_copy.training = False
                rl_copy.epsilon = 0.05
                rl_copies.append(SushiGoCPUPlayerAdapter(rl_copy))
            players = [rl_adapter, *rl_copies]
        
        elif args.mode == "priority":
            # Train against the priority bots from main.py
            priority_bots = create_priority_opponents()
            players = [rl_adapter, *priority_bots, RandomPlayer("Random")]
        
        elif args.mode == "mixed":
            # Mix of self-play and priority bots
            if ep % 2 == 0:
                priority_bots = create_priority_opponents()
                players = [rl_adapter, *priority_bots, RandomPlayer("Random")]
            else:
                rl_copies = []
                for i in range(3):
                    rl_copy = SushiGoRLPlayer(name=f"RL-copy-{i}")
                    rl_copy._q = rl._q
                    rl_copy.training = False
                    rl_copy.epsilon = 0.05
                    rl_copies.append(SushiGoCPUPlayerAdapter(rl_copy))
                players = [rl_adapter, *rl_copies, RandomPlayer("Random")]



        board = SushiGoBoard(players)
        board = run_one_game_with_training(board, rl_adapter, rl, output=False)
        scores = board.scoreBoard()

        # End-of-episode bookkeeping (epsilon decay). Rewards were already applied as deltas.
        rl.end_episode()

        # Track score, wins, and rank
        reward = float(scores[rl_adapter])
        recent_rewards.append(reward)
        
        sorted_scores = sorted(scores.values(), reverse=True)
        rl_score = scores[rl_adapter]
        rank = sorted_scores.index(rl_score) + 1
        recent_ranks.append(rank)
        recent_wins.append(1 if rank == 1 else 0)
        
        if len(recent_rewards) > args.report_every:
            recent_rewards.pop(0)
            recent_wins.pop(0)
            recent_ranks.pop(0)

        if ep % args.report_every == 0:
            avg = sum(recent_rewards) / max(1, len(recent_rewards))
            win_rate = sum(recent_wins) / max(1, len(recent_wins)) * 100
            avg_rank = sum(recent_ranks) / max(1, len(recent_ranks))
            print(f"Episode {ep}/{args.episodes} | score: {avg:.1f} | win%: {win_rate:.1f}% | rank: {avg_rank:.2f} | eps: {rl.epsilon:.3f}")

    rl.save(args.save)
    print(f"Saved Q-table to {args.save}")

    # Quick eval run (no learning) - run multiple games for reliable stats
    rl.training = False
    rl.epsilon = 0.0
    
    eval_wins = 0
    eval_scores = []
    eval_games = 100
    print(f"\nRunning {eval_games} evaluation games...")
    for _ in range(eval_games):
        board = run_one_game([rl_adapter, *[RandomPlayer(f"Random {i}") for i in range(args.opponents)]], output=False)
        scores = board.scoreBoard()
        rl_score = scores[rl_adapter]
        eval_scores.append(rl_score)
        max_score = max(scores.values())
        if rl_score == max_score:
            eval_wins += 1
    
    avg_eval_score = sum(eval_scores) / len(eval_scores)
    eval_win_rate = eval_wins / eval_games * 100
    print(f"Eval results over {eval_games} games:")
    print(f"  Avg score: {avg_eval_score:.1f}")
    print(f"  Win rate: {eval_win_rate:.1f}%")
    print(f"  (Random baseline win rate: {100/(args.opponents+1):.1f}%)")


if __name__ == "__main__":
    main()
