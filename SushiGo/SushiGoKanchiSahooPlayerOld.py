from collections import Counter, defaultdict

from SushiGo.Card import Card


class SushiGoKanchiSahooPlayerOld:
    def __init__(self, name=None):
        self.name = name or "Kanchi + Sahoo"
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

        # early and late game priorities (etc. u dont want chopsticks when theres 2 cards left for example, or first tempura that late)
        priorities = (
            self._early_priorities if current_round < 3 else self._late_priorities
        )
        played = (
            visible_cards.get(player_adapter, [])
            if visible_cards and player_adapter
            else []
        )

        # these events will change the priority of certain cards if they are active, so we keep track of them
        has_chopsticks = any(card.type == Card.Type.CHOPSTICKS for card in played)
        tempura_count = sum(1 for card in played if card.type == Card.Type.TEMPURA)
        chopsticks_count = sum(
            1 for card in played if card.type == Card.Type.CHOPSTICKS
        )

        # this finds the best combo to use with chopsticks if we get it on the first two turns
        # i doubt getting chopsticks later is very worth it, but changing the threshold to 4 could possibly have some merit
        if has_chopsticks and len(hand) >= 2 and chopsticks_count == 1:
            combo = self._find_best_combo(hand)
            if combo:
                return combo

        # greedy algorithm for determining our score based on the priorities we defined and certain events to boost priority
        best_index = 0
        best_score = -float("inf")
        for i, card in enumerate(hand):
            score = priorities.get(card.type, 0)

            # we realllly love tempura (2 cards for 5 pts, pretty simple), but having only one is cooked
            # so we boost the priority of it if we already have one, and then after we get it, destroy priority
            if card.type == Card.Type.TEMPURA:
                if tempura_count == 0:
                    score += 200
                elif tempura_count == 1:
                    score += 250
                else:
                    score -= 300

            # double chopsticks is not smth we wanna try rn, so destroy chopstick priority if we get one
            if card.type == Card.Type.CHOPSTICKS and chopsticks_count > 0:
                score -= 1000

            # if we got a wasabi down, put a squid or salmon nigiri down as a bonus. egg prob isn't worth it most the time, 
            # so we don't include that here. however this may need changing.
            has_wasabi = any(c.type == Card.Type.WASABI for c in played)
            if has_wasabi:
                if card.type == Card.Type.SQUID_NIGIRI:
                    score += 50
                elif card.type == Card.Type.SALMON_NIGIRI:
                    score += 30

            # boost pudding in last card of each round because we dont want to fall behind then
            if current_round == 3 and len(hand) <= 2 and card.type == Card.Type.PUDDING:
                score += 30

            if score > best_score:
                best_score = score
                best_index = i

        return best_index

    def _find_best_combo(self, hand):
        # we have defined a couple of good combos to use with chopsticks above in self.combo_priority (like double tempura, wasabi + nigiri)
        # if there is no good combo available, then this returns None as in we don't have a good chposticks move
        # above, this runs every move as a check, so until we get a good combo, chopsticks aren't used
        # this is another greedy search with linear runtime so shouldn't take that long too

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


# gpt fixed some errors
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
