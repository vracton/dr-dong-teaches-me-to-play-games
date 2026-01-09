from SushiGo.Card import Card

class SushiGoAidanandRoyPlayer():
    def __init__(self, name=None):
        self.name = "Aidan and Roy"
        if name:
            self.name = name
        self.priorities = {
            Card.Type.TEMPURA: 1,
            Card.Type.SASHIMI: 2,
            Card.Type.DUMPLING: 3,
            Card.Type.SINGLE_MAKI: 4,
            Card.Type.DOUBLE_MAKI: 5,
            Card.Type.TRIPLE_MAKI: 6,
            Card.Type.SALMON_NIGIRI: 7,
            Card.Type.SQUID_NIGIRI: 8,
            Card.Type.EGG_NIGIRI: 9,
            Card.Type.PUDDING: 10,
            Card.Type.WASABI: 11,
            Card.Type.CHOPSTICKS: 12
        }
        self.priorities = {k: v for k, v in sorted(self.priorities.items(), key=lambda item: item[1])}

    def choose_move(self, hand, visible_cards, current_round):
        my_cards = []
        others_cards = []
        
        for p, cards in visible_cards.items():
            if hasattr(p, 'player') and p.player == self:
                my_cards = cards
            else:
                others_cards.append(cards)
                
        if my_cards is None:
            my_cards = []

        best_idx = 0
        best_val = -float('inf')
        
        for i, card in enumerate(hand):
            val = self.evaluate_card(card, my_cards, others_cards, current_round)
            if val > best_val:
                best_val = val
                best_idx = i
                
        return best_idx

    def evaluate_card(self, card, my_cards, others_cards, current_round):
        score = 0
        score += self.get_immediate_score(card, my_cards)
        score += self.get_strategic_score(card, my_cards, others_cards, current_round)
        score += self.get_blocking_score(card, others_cards)
        return score

    def get_immediate_score(self, card, my_cards):
        if card.type == Card.Type.TEMPURA:
            count = sum(1 for c in my_cards if c.type == Card.Type.TEMPURA)
            if count % 2 == 1: return 5 # Completes a pair
            return 0
            
        if card.type == Card.Type.SASHIMI:
            count = sum(1 for c in my_cards if c.type == Card.Type.SASHIMI)
            if count % 3 == 2: return 10 # Completes a trio
            return 0
            
        if card.type == Card.Type.DUMPLING:
            count = sum(1 for c in my_cards if c.type == Card.Type.DUMPLING)
            if count == 0: return 1
            if count == 1: return 3
            if count == 2: return 6
            if count == 3: return 10
            if count >= 4: return 15
            return 0
            
        if card.type in [Card.Type.EGG_NIGIRI, Card.Type.SALMON_NIGIRI, Card.Type.SQUID_NIGIRI]:
            wasabis = sum(1 for c in my_cards if c.type == Card.Type.WASABI)
            nigiris = sum(1 for c in my_cards if c.type in [Card.Type.EGG_NIGIRI, Card.Type.SALMON_NIGIRI, Card.Type.SQUID_NIGIRI])
            
            open_wasabi = max(0, wasabis - nigiris) 
            
            base = 0
            if card.type == Card.Type.EGG_NIGIRI: base = 1
            if card.type == Card.Type.SALMON_NIGIRI: base = 2
            if card.type == Card.Type.SQUID_NIGIRI: base = 3
            
            if open_wasabi > 0: return base * 3
            return base
            
        return 0

    def get_strategic_score(self, card, my_cards, others_cards, current_round):
        val = 0
        
        if card.type == Card.Type.TEMPURA:
            count = sum(1 for c in my_cards if c.type == Card.Type.TEMPURA)
            if count % 2 == 0: val = 1.5 
        
        if card.type == Card.Type.SASHIMI:
            count = sum(1 for c in my_cards if c.type == Card.Type.SASHIMI)
            rem = count % 3
            if rem == 0: val = 1.0 # Start
            elif rem == 1: val = 3.0 # Continue (closer to 10)

        if card.type == Card.Type.WASABI:
            val = 3.5 
            
        if card.type == Card.Type.PUDDING:
            my_pudding = sum(1 for c in my_cards if c.type == Card.Type.PUDDING)
            
            min_opp = 0
            max_opp = 0
            if others_cards:
                 counts = [sum(1 for c in hand if c.type == Card.Type.PUDDING) for hand in others_cards]
                 min_opp = min(counts)
                 max_opp = max(counts)
            
            if my_pudding <= min_opp: val = 4.0 
            elif my_pudding >= max_opp: val = 2.5
            else: val = 1.0
            
            if current_round == 3: val *= 1.5
            
        if card.type in [Card.Type.SINGLE_MAKI, Card.Type.DOUBLE_MAKI, Card.Type.TRIPLE_MAKI]:
            maki_points = 1
            if card.type == Card.Type.DOUBLE_MAKI: maki_points = 2
            if card.type == Card.Type.TRIPLE_MAKI: maki_points = 3
            
            my_total = self.calc_maki(my_cards)
            
            if not others_cards:
                val = maki_points * 1.0
            else:
                max_opp = max(self.calc_maki(h) for h in others_cards)
                
                if my_total <= max_opp + 3:
                    val = maki_points * 1.5
                else:
                    val = maki_points * 0.5
            
        if card.type == Card.Type.CHOPSTICKS:
            val = -10.0 
            
        return val
        
    def get_blocking_score(self, card, others_cards):
        block_val = 0
        for opp_hand in others_cards:
            gain = self.get_immediate_score(card, opp_hand)
            
            if gain >= 5:
                block_val = max(block_val, gain * 0.3)
                
        return block_val

    def calc_maki(self, cards):
        s = 0
        for c in cards:
            if c.type == Card.Type.SINGLE_MAKI: s += 1
            elif c.type == Card.Type.DOUBLE_MAKI: s += 2
            elif c.type == Card.Type.TRIPLE_MAKI: s += 3
        return s

