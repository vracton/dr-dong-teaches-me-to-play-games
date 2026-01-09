from SushiGo.Card import Card

class SushiGoAnthonyMacPlayer():
    def __init__(self, name = None):
        self.name = "Anthony Macintosh"
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
        # Return the index of the card to play from hand (from 0 to len(hand)-1)
        from SushiGo.Card import Card

        # Find this player's already placed/collected cards from visible_cards
        my_placed = []
        try:
            for adapter, placed in visible_cards.items():
                # CPU adapters expose a `.player` attribute that references this player
                if hasattr(adapter, 'player') and adapter.player is self:
                    my_placed = placed
                    break
        except Exception:
            my_placed = []
        # whether chopsticks are available to use (already played earlier)
        chopsticks_available = any(c.type == Card.Type.CHOPSTICKS for c in my_placed)

        # Early game strategy: rounds 1-3
        if current_round is not None and current_round <= 3:
            early_order = [
                Card.Type.SASHIMI,
                Card.Type.WASABI,
                Card.Type.CHOPSTICKS,
                Card.Type.TEMPURA,
                Card.Type.SALMON_NIGIRI,
                Card.Type.SQUID_NIGIRI,
                Card.Type.EGG_NIGIRI,
                Card.Type.DUMPLING,
                Card.Type.SINGLE_MAKI,
                Card.Type.DOUBLE_MAKI,
                Card.Type.TRIPLE_MAKI,
                Card.Type.PUDDING
            ]

            # If chopsticks are available, consider using them first
            if chopsticks_available:
                # helper to find indices of a card type in hand
                def indices_of(t):
                    return [i for i, cc in enumerate(hand) if cc.type == t]

                # If two tempura in hand, use chopsticks to play both
                temp_indices = indices_of(Card.Type.TEMPURA)
                if len(temp_indices) >= 2:
                    return (temp_indices[0], temp_indices[1])

                # If 1 sashimi placed and 2 in hand, use chopsticks to play two sashimi
                sashimi_indices = indices_of(Card.Type.SASHIMI)
                placed_sashimi = sum(1 for c in my_placed if c.type == Card.Type.SASHIMI)
                if placed_sashimi == 1 and len(sashimi_indices) >= 2:
                    return (sashimi_indices[0], sashimi_indices[1])

                # If two of the top three early priorities are in hand, play them both
                top3 = early_order[0:3]
                found = []
                for t in top3:
                    for idx in indices_of(t):
                        if idx not in found:
                            found.append(idx)
                        if len(found) >= 2:
                            return (found[0], found[1])

            # choose the highest-priority card available in hand
            for typ in early_order:
                for i, c in enumerate(hand):
                    if c.type == typ:
                        return i
            # fallback: play first card
            return 0

        # Late game (rounds 4-7): many conditional adjustments
        # Count placed cards
        placed_counts = {}
        for c in my_placed:
            placed_counts[c.type] = placed_counts.get(c.type, 0) + 1

        sashimi_placed = placed_counts.get(Card.Type.SASHIMI, 0)
        wasabi_placed = placed_counts.get(Card.Type.WASABI, 0)
        chopsticks_placed = placed_counts.get(Card.Type.CHOPSTICKS, 0)
        tempura_placed = placed_counts.get(Card.Type.TEMPURA, 0)
        dumpling_placed = placed_counts.get(Card.Type.DUMPLING, 0)

        # Precompute counts in hand
        hand_counts = {}
        for c in hand:
            hand_counts[c.type] = hand_counts.get(c.type, 0) + 1

        # If chopsticks are available in late game, attempt two-card plays first
        if chopsticks_placed >= 1:
            def indices_of(t):
                return [i for i, cc in enumerate(hand) if cc.type == t]

            # Two tempura -> play both
            temp_indices = indices_of(Card.Type.TEMPURA)
            if len(temp_indices) >= 2:
                return (temp_indices[0], temp_indices[1])

            # If 1 sashimi placed and 2 in hand, use chopsticks to play two sashimi
            sashimi_indices = indices_of(Card.Type.SASHIMI)
            if sashimi_placed == 1 and len(sashimi_indices) >= 2:
                return (sashimi_indices[0], sashimi_indices[1])

            # If two of our top three priorities (by original mapping) are in hand, play them
            late_top3 = list(self.priorities.keys())[0:3]
            found = []
            for t in late_top3:
                for idx in indices_of(t):
                    if idx not in found:
                        found.append(idx)
                    if len(found) >= 2:
                        return (found[0], found[1])

        best_index = 0
        best_score = -1e9

        for i, card in enumerate(hand):
            score = 0

            # If we already have 3+ dumplings placed, prioritize dumplings very highly
            if dumpling_placed >= 3:
                if card.type == Card.Type.DUMPLING:
                    score += 100
                else:
                    score -= 5

            # If two or more sashimi already placed, raise sashimi priority a lot
            if sashimi_placed >= 2:
                if card.type == Card.Type.SASHIMI:
                    score += 90

            # If we placed a wasabi earlier, prioritize squid and salmon nigiri
            if wasabi_placed >= 1:
                if card.type == Card.Type.SQUID_NIGIRI:
                    score += 40
                elif card.type == Card.Type.SALMON_NIGIRI:
                    score += 35

            # If we have 1 sashimi placed and chopsticks placed, prioritize completing sashimi
            if sashimi_placed >= 1 and chopsticks_placed >= 1:
                if card.type == Card.Type.SASHIMI:
                    score += 50

            # Prioritize tempura if we already have any tempura placed (trying to make pairs)
            if tempura_placed >= 1 and card.type == Card.Type.TEMPURA:
                score += 30

            # If we have wasabi or chopsticks still in hand (not placed), make them lower priority
            if card.type in (Card.Type.WASABI, Card.Type.CHOPSTICKS):
                # deprioritize playing them late unless they are needed
                score -= 20

            # Maki is lowest priority in late game
            if card.type in (Card.Type.SINGLE_MAKI, Card.Type.DOUBLE_MAKI, Card.Type.TRIPLE_MAKI):
                score -= 15

            # If we have a wasabi placed and there is a squid or salmon in hand, boost their priority
            if wasabi_placed >= 1 and card.type in (Card.Type.SQUID_NIGIRI, Card.Type.SALMON_NIGIRI):
                score += 10

            # Two sashimi in hand together completion check
            if card.type == Card.Type.SASHIMI:
                # if we have two sashimi in hand already, and 1 placed, elevate
                if hand_counts.get(Card.Type.SASHIMI, 0) >= 2:
                    score += 20

            # If we already have many dumplings placed, or can reach thresholds, bump dumpling
            if card.type == Card.Type.DUMPLING:
                if dumpling_placed >= 2:
                    score += 45
                elif hand_counts.get(Card.Type.DUMPLING, 0) >= 2:
                    score += 15

            # Pudding becomes important later if none of the above apply
            if card.type == Card.Type.PUDDING:
                score += 5

            # Default small base values to break ties sensibly
            if card.type == Card.Type.SQUID_NIGIRI:
                score += 8
            elif card.type == Card.Type.SALMON_NIGIRI:
                score += 6
            elif card.type == Card.Type.EGG_NIGIRI:
                score += 4
            elif card.type == Card.Type.TEMPURA:
                score += 7
            elif card.type == Card.Type.SASHIMI:
                score += 9
            elif card.type == Card.Type.WASABI:
                score += 2
            elif card.type == Card.Type.CHOPSTICKS:
                score += 1
            elif card.type == Card.Type.SINGLE_MAKI:
                score += 0
            elif card.type == Card.Type.DOUBLE_MAKI:
                score += 0
            elif card.type == Card.Type.TRIPLE_MAKI:
                score -= 2

            # Tie-breaker: prefer cards with higher explicit priority in our original mapping
            # lower numeric priority value means earlier preference; invert for scoring
            if card.type in self.priorities:
                score += (20 - self.priorities[card.type]) * 0.1

            # Advanced heuristic augmentations (non-overlapping layer)
            # remaining turns approximated by hand size
            remaining_turns = len(hand)
            # marginal expected-value heuristic
            mv = self._marginal_value(card, hand_counts, placed_counts, remaining_turns)
            score += mv

            # urgency multiplier for near-complete sets
            urgency = self._urgency_multiplier(card.type, remaining_turns)
            score *= urgency

            # dead-card penalty
            dead_pen = self._dead_card_penalty(card, hand_counts, placed_counts, remaining_turns)
            score -= dead_pen

            # wasabi efficiency control
            score += self._wasabi_efficiency(card, hand_counts, placed_counts, remaining_turns)

            # chopsticks recovery timing: penalize playing chopsticks too late
            score += self._chopsticks_timing_score(card, remaining_turns)

            # pudding posture adjustments
            score += self._pudding_posture_score(card, placed_counts, visible_cards)

            # deterministic tie-breakers encoded in small increments
            score += self._tie_breaker_bonus(card, hand_counts)

            if score > best_score:
                best_score = score
                best_index = i

        return best_index

    # ----------------------------- Advanced Heuristics -----------------------------
    def _marginal_value(self, card, hand_counts, placed_counts, remaining_turns):
        # Estimate marginal gain from playing this card now (heuristic only)
        from SushiGo.Card import Card
        val = 0
        # Immediate scoring pieces
        if card.type == Card.Type.SQUID_NIGIRI:
            val += 3
        elif card.type == Card.Type.SALMON_NIGIRI:
            val += 2
        elif card.type == Card.Type.EGG_NIGIRI:
            val += 1

        # Tempura and sashimi give value when completing sets
        if card.type == Card.Type.TEMPURA:
            have = placed_counts.get(Card.Type.TEMPURA, 0) + hand_counts.get(Card.Type.TEMPURA, 0)
            # marginal if pairs likely
            if have >= 2:
                val += 5
            else:
                val += 1
        if card.type == Card.Type.SASHIMI:
            have = placed_counts.get(Card.Type.SASHIMI, 0) + hand_counts.get(Card.Type.SASHIMI, 0)
            if have >= 3:
                val += 10
            elif have == 2:
                # one away
                val += 4
            else:
                val += 1

        # Dumplings: marginal value grows with count
        if card.type == Card.Type.DUMPLING:
            cur = placed_counts.get(Card.Type.DUMPLING, 0)
            add = hand_counts.get(Card.Type.DUMPLING, 0)
            # marginal contribution approximated
            if cur + add >= 5:
                val += 6
            elif cur + add >= 3:
                val += 3
            else:
                val += 1

        # Maki provides icons; treat as small immediate value
        if card.type in (Card.Type.SINGLE_MAKI, Card.Type.DOUBLE_MAKI, Card.Type.TRIPLE_MAKI):
            if card.type == Card.Type.SINGLE_MAKI:
                val += 1
            elif card.type == Card.Type.DOUBLE_MAKI:
                val += 2
            else:
                val += 3

        # Wasabi has conditional value; baseline small
        if card.type == Card.Type.WASABI:
            val += 0.5

        # Pudding endgame potential
        if card.type == Card.Type.PUDDING:
            # small immediate expected marginal value during round
            val += 1

        return val

    def _urgency_multiplier(self, card_type, remaining_turns):
        # Increase urgency for near-complete sets as remaining turns shrink
        # remaining_turns is small -> multiplier grows
        mult = 1.0
        # If very few turns left, upweight completion-sensitive cards
        if remaining_turns <= 2:
            # very urgent
            if card_type == Card.Type.SASHIMI:
                mult = 1.6
            elif card_type == Card.Type.TEMPURA:
                mult = 1.5
            elif card_type == Card.Type.DUMPLING:
                mult = 1.4
        elif remaining_turns <= 4:
            if card_type == Card.Type.SASHIMI:
                mult = 1.3
            elif card_type == Card.Type.TEMPURA:
                mult = 1.2
        return mult

    def _dead_card_penalty(self, card, hand_counts, placed_counts, remaining_turns):
        # Penalize cards unlikely to ever score
        from SushiGo.Card import Card
        penalty = 0
        # Tempura needs 2
        if card.type == Card.Type.TEMPURA:
            needed = 2
            possible = placed_counts.get(Card.Type.TEMPURA, 0) + hand_counts.get(Card.Type.TEMPURA, 0)
            # if even with all remaining turns we can't reach a pair, penalize
            if possible < needed and remaining_turns < (needed - possible + 1):
                penalty += 5

        # Sashimi needs 3
        if card.type == Card.Type.SASHIMI:
            needed = 3
            possible = placed_counts.get(Card.Type.SASHIMI, 0) + hand_counts.get(Card.Type.SASHIMI, 0)
            if possible < needed and remaining_turns < (needed - possible + 1):
                penalty += 7

        # Dumplings late that cannot reach thresholds
        if card.type == Card.Type.DUMPLING:
            possible = placed_counts.get(Card.Type.DUMPLING, 0) + hand_counts.get(Card.Type.DUMPLING, 0)
            if possible < 2 and remaining_turns <= 1:
                penalty += 3

        # Wasabi without nigiri opportunity
        if card.type == Card.Type.WASABI:
            nigiri_in_hand = hand_counts.get(Card.Type.SALMON_NIGIRI, 0) + hand_counts.get(Card.Type.SQUID_NIGIRI, 0) + hand_counts.get(Card.Type.EGG_NIGIRI, 0)
            if nigiri_in_hand == 0 and remaining_turns <= 2:
                penalty += 6

        return penalty

    def _wasabi_efficiency(self, card, hand_counts, placed_counts, remaining_turns):
        # Reduce value for wasabi overcommit and when nigiri unlikely
        from SushiGo.Card import Card
        bonus = 0
        if card.type == Card.Type.WASABI:
            # If multiple wasabi already placed, devalue additional wasabi
            if placed_counts.get(Card.Type.WASABI, 0) >= 1:
                bonus -= 3
            # If few nigiri remain in hand and few turns, devalue
            nigiri_left = hand_counts.get(Card.Type.SALMON_NIGIRI, 0) + hand_counts.get(Card.Type.SQUID_NIGIRI, 0) + hand_counts.get(Card.Type.EGG_NIGIRI, 0)
            if nigiri_left == 0 and remaining_turns <= 2:
                bonus -= 4
        # If card is a nigiri and a wasabi is already placed, boost slightly but moderate if many wasabi
        if card.type in (Card.Type.SALMON_NIGIRI, Card.Type.SQUID_NIGIRI, Card.Type.EGG_NIGIRI):
            if placed_counts.get(Card.Type.WASABI, 0) >= 1:
                if placed_counts.get(Card.Type.WASABI, 0) > 1:
                    bonus += 1
                else:
                    bonus += 3
        return bonus

    def _chopsticks_timing_score(self, card, remaining_turns):
        # Prefer to play chopsticks earlier (so they can be used), but deprioritize in final turns
        score = 0
        from SushiGo.Card import Card
        if card.type == Card.Type.CHOPSTICKS:
            if remaining_turns >= 4:
                score += 3
            elif remaining_turns <= 2:
                score -= 6
            else:
                score -= 1
        return score

    def _pudding_posture_score(self, card, placed_counts, visible_cards):
        # Adjust pudding priority based on relative pudding counts
        from SushiGo.Card import Card
        score = 0
        my_pud = placed_counts.get(Card.Type.PUDDING, 0)
        # compute opponents' puddings from visible_cards
        opp_max = 0
        opp_min = None
        try:
            for adapter, placed in visible_cards.items():
                if hasattr(adapter, 'player') and adapter.player is self:
                    continue
                p = sum(1 for c in placed if c.type == Card.Type.PUDDING)
                if p > opp_max:
                    opp_max = p
                if opp_min is None or p < opp_min:
                    opp_min = p
        except Exception:
            opp_max = 0
            opp_min = None

        if card.type == Card.Type.PUDDING:
            # If we are already ahead on puddings, reduce urgency
            if my_pud > opp_max:
                score -= 3
            # If we are behind or risk last place on puddings, increase priority
            if my_pud < (opp_min or 0):
                score += 6
            # Otherwise small boost late in game
            score += 1
        return score

    def _tie_breaker_bonus(self, card, hand_counts):
        # Deterministic tie-breaker bonuses: prefer low-variance, flexible cards
        bonus = 0
        from SushiGo.Card import Card
        # variance rank: dumpling(hi), sashimi/ tempura(med), nigiri/ maki(low)
        if card.type == Card.Type.DUMPLING:
            bonus -= 1
        elif card.type in (Card.Type.SASHIMI, Card.Type.TEMPURA):
            bonus += 0
        elif card.type in (Card.Type.SQUID_NIGIRI, Card.Type.SALMON_NIGIRI, Card.Type.EGG_NIGIRI):
            bonus += 1
        elif card.type in (Card.Type.SINGLE_MAKI, Card.Type.DOUBLE_MAKI, Card.Type.TRIPLE_MAKI):
            bonus += 1

        # prefer preserving unique combos: if playing this card would remove a unique finishing piece, subtract
        if hand_counts.get(card.type, 0) == 1:
            bonus -= 0.2

        # stable deterministic small tiebreaker by card type ordering
        bonus += (hash(card.type) % 5) * 0.01
        return bonus

