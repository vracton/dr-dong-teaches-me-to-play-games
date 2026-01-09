from SushiGo.Card import Card

class SushiGoArunPlayer():
    def __init__(self, name=None):
        self.name = "Your Name Here"
        if name:
            self.name = name

        # Lower number = higher priority
        self.priorities = {
            Card.Type.SASHIMI: 1,
            Card.Type.TEMPURA: 2,
            Card.Type.SQUID_NIGIRI: 3,
            Card.Type.SALMON_NIGIRI: 4,
            Card.Type.DUMPLING: 5,
            Card.Type.TRIPLE_MAKI: 6,
            Card.Type.DOUBLE_MAKI: 7,
            Card.Type.SINGLE_MAKI: 8,
            Card.Type.WASABI: 9,
            Card.Type.EGG_NIGIRI: 10,
            Card.Type.CHOPSTICKS: 11,
            Card.Type.PUDDING: 12
        }

    def choose_move(self, hand, visible_cards, current_round):
        # Count what we already have played
        played = []
        for player_cards in visible_cards.values():
            played.extend(player_cards)

        sashimi_count = sum(1 for c in played if c.type == Card.Type.SASHIMI)
        has_wasabi = any(c.type == Card.Type.WASABI for c in played)

        best_index = 0

        for i in range(len(hand)):
            card = hand[i]
            best_card = hand[best_index]

            # Rule 1: If we already have 2 sashimi, force the 3rd
            if sashimi_count == 2 and card.type == Card.Type.SASHIMI:
                return i

            # Rule 2: If we have wasabi, prefer nigiri
            if has_wasabi and card.type in [
                Card.Type.SQUID_NIGIRI,
                Card.Type.SALMON_NIGIRI,
                Card.Type.EGG_NIGIRI
            ]:
                return i

            # Rule 3: Avoid chopsticks late
            if current_round == 3 and card.type == Card.Type.CHOPSTICKS:
                continue

            # Default: priority comparison
            if self.priorities[card.type] < self.priorities[best_card.type]:
                best_index = i

        return best_index
