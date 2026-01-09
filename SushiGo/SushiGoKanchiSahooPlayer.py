from collections import Counter, defaultdict

from SushiGo.Card import Card


class SushiGoKanchiSahooPlayer:
    def __init__(self, name=None):
        self.name = name or "knach + saho"
        self._early_priorities = {
            Card.Type.CHOPSTICKS: 100,
            Card.Type.WASABI: 95,
            Card.Type.SQUID_NIGIRI: 85,
            Card.Type.TEMPURA: 80,
            Card.Type.DUMPLING: 75,
            Card.Type.PUDDING: 70,
            Card.Type.TRIPLE_MAKI: 65,
            Card.Type.DOUBLE_MAKI: 60,
            Card.Type.SINGLE_MAKI: 55,
            Card.Type.SALMON_NIGIRI: 50,
            Card.Type.SASHIMI: 30,
            Card.Type.EGG_NIGIRI: 25,
        }
        self._late_priorities = {
            Card.Type.SQUID_NIGIRI: 95,
            Card.Type.DUMPLING: 90,
            Card.Type.SALMON_NIGIRI: 85,
            Card.Type.EGG_NIGIRI: 80,
            Card.Type.PUDDING: 75,
            Card.Type.WASABI: 70,
            Card.Type.TRIPLE_MAKI: 65,
            Card.Type.DOUBLE_MAKI: 60,
            Card.Type.SINGLE_MAKI: 55,
            Card.Type.CHOPSTICKS: 50,
            Card.Type.SASHIMI: 20,
        }
        self._combo_priority = [
            (Card.Type.WASABI, Card.Type.SQUID_NIGIRI),
            (Card.Type.TEMPURA, Card.Type.TEMPURA),
            (Card.Type.SQUID_NIGIRI, Card.Type.SQUID_NIGIRI),
            (Card.Type.SQUID_NIGIRI, Card.Type.SALMON_NIGIRI),
            (Card.Type.SASHIMI, Card.Type.SASHIMI),
            (Card.Type.DUMPLING, Card.Type.DUMPLING),
        ]

    def choose_move(self, hand, visible_cards, current_round, player_adapter=None):
        """Select a card or chopstick combo based on simplified strategy."""
        priorities = self._early_priorities if current_round < 3 else self._late_priorities
        played = visible_cards.get(player_adapter, []) if visible_cards and player_adapter else []
        
        # Track game state
        has_chopsticks = any(card.type == Card.Type.CHOPSTICKS for card in played)
        tempura_count = sum(1 for card in played if card.type == Card.Type.TEMPURA)
        chopsticks_count = sum(1 for card in played if card.type == Card.Type.CHOPSTICKS)

        # Try chopstick combo if: have chopsticks played, hand >= 2, only 1 chopsticks played so far
        if has_chopsticks and len(hand) >= 2 and chopsticks_count == 1:
            combo = self._find_best_combo(hand)
            if combo:
                return combo

        # Greedy selection with inline bonuses
        best_index = 0
        best_score = -float("inf")
        for i, card in enumerate(hand):
            score = priorities.get(card.type, 0)
            
            # Tempura: boost 2nd, suppress 3rd+
            if card.type == Card.Type.TEMPURA:
                if tempura_count == 0:
                    score += 200
                elif tempura_count == 1:
                    score += 250
                else:
                    score -= 300
            
            # Block chopsticks after first one
            if card.type == Card.Type.CHOPSTICKS and chopsticks_count > 0:
                score -= 1000
            
            # Wasabi bonus: squid nigiri +50, salmon nigiri +30
            has_wasabi = any(c.type == Card.Type.WASABI for c in played)
            if has_wasabi:
                if card.type == Card.Type.SQUID_NIGIRI:
                    score += 50
                elif card.type == Card.Type.SALMON_NIGIRI:
                    score += 30
            
            # Pudding boost in final round
            if current_round == 3 and len(hand) <= 2 and card.type == Card.Type.PUDDING:
                score += 30
            
            if score > best_score:
                best_score = score
                best_index = i
        
        return best_index

    def _find_best_combo(self, hand):
        """Find best chopstick combo from hand based on combo priority."""
        type_indices = defaultdict(list)
        for idx, card in enumerate(hand):
            type_indices[card.type].append(idx)
        
        for first_type, second_type in self._combo_priority:
            first_list = type_indices.get(first_type, [])
            second_list = type_indices.get(second_type, [])
            
            if first_type == second_type and len(first_list) >= 2:
                return (first_list[0], first_list[1])
            elif first_type != second_type and first_list and second_list:
                return tuple(sorted((first_list[0], second_list[0])))
        
        return None


# Patch CPU adapter to handle chopstick combo returns (tuple format)
try:
    from SushiGo.SushiGoCPUPlayerAdapter import SushiGoCPUPlayerAdapter
    from SushiGo.SushiGoMove import SushiGoMove

    original_getMove = SushiGoCPUPlayerAdapter.getMove

    def patched_getMove(self, board):
        choice = self.player.choose_move(
            board.hands[self],
            board.played_cards,
            board.current_round,
            player_adapter=self,
        )
        if choice is None:
            raise Exception("CPU Player returned None for move.")
        if isinstance(choice, tuple):
            first_idx, second_idx = choice
            return SushiGoMove(
                self,
                board.hands[self][first_idx],
                board.hands[self][second_idx],
            )
        return SushiGoMove(self, board.hands[self][choice])

    SushiGoCPUPlayerAdapter.getMove = patched_getMove
except ImportError:
    pass
