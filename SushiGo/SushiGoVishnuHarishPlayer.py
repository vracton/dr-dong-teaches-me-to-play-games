from SushiGo.Card import Card

class SushiGoVishnuHarishPlayer():
    def __init__(self, name = None):
        self.name = "Horosh n Voshno"
        self.playedCards = []
        if name:
            self.name = name
        self.priorities = {
            Card.Type.TRIPLE_MAKI: 1,
            Card.Type.PUDDING: 2,
            Card.Type.WASABI: 3,
            Card.Type.SQUID_NIGIRI: 4,
            Card.Type.SASHIMI: 5,
            Card.Type.DUMPLING: 6,
            Card.Type.TEMPURA: 7,
            Card.Type.SALMON_NIGIRI: 8,
            Card.Type.DOUBLE_MAKI: 9,
            Card.Type.SINGLE_MAKI: 10,
            Card.Type.EGG_NIGIRI: 11,
            Card.Type.CHOPSTICKS: 12
        }
        self.priorities = {k: v for k, v in sorted(self.priorities.items(), key=lambda item: item[1])}

    def choose_move(self, hand, visible_cards, current_round):

        if len(hand) == 7:
            # remove all the cards from played cards except pudding types
            self.playedCards = [card for card in self.playedCards if card.type == Card.Type.PUDDING]
            self.priorities = {
                Card.Type.TRIPLE_MAKI: 1,
                Card.Type.PUDDING: 2,
                Card.Type.WASABI: 3,
                Card.Type.SQUID_NIGIRI: 4,
                Card.Type.SASHIMI: 5,
                Card.Type.DUMPLING: 6,
                Card.Type.TEMPURA: 7,
                Card.Type.SALMON_NIGIRI: 8,
                Card.Type.DOUBLE_MAKI: 9,
                Card.Type.SINGLE_MAKI: 10,
                Card.Type.EGG_NIGIRI: 11,
                Card.Type.CHOPSTICKS: 12
            }
                    
        # Return the index of the card to play from hand (from 0 to len(hand)-1)
        #return 0  # Example: always play the first card in hand
        
        # if there is a sashimi in hand and two sashimi in my pile, play the sashimi immediately
        if any(card.type == Card.Type.SASHIMI for card in hand):
            sashimi_count = sum(1 for card in self.playedCards if card.type == Card.Type.SASHIMI)
            if sashimi_count == 2:
                for i in range(len(hand)):
                    if hand[i].type == Card.Type.SASHIMI:
                        self.playedCards.append(hand[i])
                        return i
        # if there is one tempura on the pile and another in hand, play the tempura immediately
        if any(card.type == Card.Type.TEMPURA for card in hand):
            tempura_count = sum(1 for card in self.playedCards if card.type == Card.Type.TEMPURA)
            if tempura_count == 1:
                for i in range(len(hand)):
                    if hand[i].type == Card.Type.TEMPURA:
                        self.playedCards.append(hand[i])
                        return i
        # if there is a wasabi in pile and nigiri other than egg nigiri in hand, play the nigiri
        if any(card.type == Card.Type.WASABI for card in self.playedCards):
            for i in range(len(hand)):
                if hand[i].type in [Card.Type.SALMON_NIGIRI, Card.Type.SQUID_NIGIRI]:
                    self.playedCards.append(hand[i])
                    return i
        # for every dumpling in pile, increase priority of dumplings in hand by 1
        dumpling_count = sum(1 for card in self.playedCards if card.type == Card.Type.DUMPLING)
        if dumpling_count > 0:
            self.priorities[Card.Type.DUMPLING] -= dumpling_count

        # if current round > 5, decrease priority of the sashimi cards by 3 and tempura cards by 2
        if current_round > 5:
            self.priorities[Card.Type.SASHIMI] -= 3
            self.priorities[Card.Type.TEMPURA] -= 2

        best_card_index = 0
        for i in range(len(hand)):
            if self.priorities[hand[i].type] < self.priorities[hand[best_card_index].type]:
                best_card_index = i

        self.playedCards.append(hand[best_card_index])
        
        return best_card_index

