from SushiGo.Card import Card
import random

class SushiGoMihirBenjaminDeenPlayer():
    # Card counts in the full deck
    DECK_COUNTS = {
        Card.Type.TEMPURA: 14,
        Card.Type.SASHIMI: 14,
        Card.Type.DUMPLING: 14,
        Card.Type.SINGLE_MAKI: 6,
        Card.Type.DOUBLE_MAKI: 12,
        Card.Type.TRIPLE_MAKI: 8,
        Card.Type.SALMON_NIGIRI: 10,
        Card.Type.SQUID_NIGIRI: 5,
        Card.Type.EGG_NIGIRI: 5,
        Card.Type.PUDDING: 10,
        Card.Type.WASABI: 6,
        Card.Type.CHOPSTICKS: 4
    }
    
    TOTAL_CARDS = sum(DECK_COUNTS.values())  # 108 cards
    
    # Scoring constants
    TEMPURA_PAIR_VALUE = 5
    SASHIMI_TRIPLE_VALUE = 10
    DUMPLING_SCORES = [0, 1, 3, 6, 10, 15]  # Index = count
    NIGIRI_SCORES = {
        Card.Type.EGG_NIGIRI: 1,
        Card.Type.SALMON_NIGIRI: 2,
        Card.Type.SQUID_NIGIRI: 3
    }
    WASABI_MULTIPLIER = 3
    MAKI_FIRST_PLACE = 6
    MAKI_SECOND_PLACE = 3
    PUDDING_BONUS = 6
    PUDDING_PENALTY = 6
    
    # Monte Carlo parameters
    MONTE_CARLO_ITERATIONS = 20
    NUM_PLAYERS = 5
    CARDS_PER_HAND = 7
    
    def __init__(self, name = None):
        self.name = "BenjaminMihirDeen"
        if name:
            self.name = name
        
        # Per-round state tracking
        self.reset_round_state()
        
        # Track seen cards across rounds for probability calculations
        self.seen_cards = {card_type: 0 for card_type in Card.Type}
        self.current_round_tracker = 0
        
        # Backward compatibility: maintain priorities dict (not used by new EV system)
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
    
    def reset_round_state(self):
        """Reset state tracking for a new round"""
        self.tempura_count = 0
        self.sashimi_count = 0
        self.dumpling_count = 0
        self.maki_count = 0
        self.pudding_count = 0
        self.wasabi_available = 0
        self.nigiri_played = []  # Track nigiri for wasabi pairing
    
    def update_state_from_visible(self, visible_cards):
        """Update internal state based on visible played cards
        
        FIX: Use name matching to find our own cards since visible_cards keys are Player objects,
        not SushiGoMihirBenjaminDeenPlayer objects. Track state separately to avoid dependency on dict keys.
        """
        # Reset and recalculate from visible cards
        self.reset_round_state()
        
        # FIX: Find our own cards by matching name (safer than assuming self is a key)
        for player, cards in visible_cards.items():
            # Match by name since adapter wraps us
            if hasattr(player, 'name') and player.name == self.name:
                for card in cards:
                    self._add_card_to_state(card)
                break
    
    def _add_card_to_state(self, card):
        """Helper to add a card to internal state"""
        if card.type == Card.Type.TEMPURA:
            self.tempura_count += 1
        elif card.type == Card.Type.SASHIMI:
            self.sashimi_count += 1
        elif card.type == Card.Type.DUMPLING:
            self.dumpling_count += 1
        elif card.type == Card.Type.SINGLE_MAKI:
            self.maki_count += 1
        elif card.type == Card.Type.DOUBLE_MAKI:
            self.maki_count += 2
        elif card.type == Card.Type.TRIPLE_MAKI:
            self.maki_count += 3
        elif card.type == Card.Type.PUDDING:
            self.pudding_count += 1
        elif card.type == Card.Type.WASABI:
            self.wasabi_available += 1
        elif card.type in [Card.Type.EGG_NIGIRI, Card.Type.SALMON_NIGIRI, Card.Type.SQUID_NIGIRI]:
            if self.wasabi_available > 0:
                self.wasabi_available -= 1
            self.nigiri_played.append(card.type)
    
    def count_visible_cards(self, visible_cards, hand):
        """Count how many of each card type we've seen
        
        FIX: Count visible played cards (all players) and our hand.
        Do NOT double-count - our hand is separate from played cards.
        """
        counts = {card_type: 0 for card_type in Card.Type}
        
        # Count in all visible played cards (all players, including ourselves)
        for player_cards in visible_cards.values():
            for card in player_cards:
                counts[card.type] += 1
        
        # Count in our hand (these are NOT yet played, so they're still "in circulation"
        # but we know about them, so we exclude them from remaining deck estimates)
        for card in hand:
            counts[card.type] += 1
        
        return counts
    
    def estimate_remaining_cards(self, visible_cards, hand, current_round, exclude_card=None):
        """Estimate how many of each card type remain unseen
        
        FIX: Correctly exclude:
        - All visible played cards (from all players)
        - Our current hand (we know these cards)
        - The card we're evaluating (if exclude_card provided)
        - Do NOT subtract opponent hands (they're unknown to us)
        
        Args:
            visible_cards: Dictionary of played cards (keyed by Player objects)
            hand: Our current hand
            current_round: Current round number
            exclude_card: Optional card to exclude from remaining count (for evaluation)
        """
        seen = self.count_visible_cards(visible_cards, hand)
        remaining = {}
        
        for card_type in Card.Type:
            # Start with full deck count
            count = self.DECK_COUNTS[card_type]
            # Subtract cards we've seen (played cards + our hand)
            count -= seen[card_type]
            # If evaluating a specific card, exclude it from remaining pool
            if exclude_card and exclude_card.type == card_type:
                count = max(0, count - 1)
            remaining[card_type] = max(0, count)
        
        return remaining
    
    def calculate_tempura_ev(self, remaining_cards, turns_remaining):
        """Calculate expected value of playing a tempura"""
        current_pairs = self.tempura_count // 2
        new_pairs = (self.tempura_count + 1) // 2
        
        immediate_value = (new_pairs - current_pairs) * self.TEMPURA_PAIR_VALUE
        
        # Probability of completing another pair
        if self.tempura_count % 2 == 0:  # Will have odd count after playing
            # Need one more tempura
            tempura_remaining = remaining_cards[Card.Type.TEMPURA] - 1  # -1 for the one we're playing
            total_remaining = sum(remaining_cards.values()) - 1
            
            if total_remaining > 0 and tempura_remaining > 0:
                # Approximate probability: cards left in round / total cards
                # More sophisticated: hypergeometric distribution approximation
                cards_in_round = turns_remaining * self.NUM_PLAYERS * self.CARDS_PER_HAND
                prob_completion = min(1.0, (tempura_remaining / max(1, total_remaining)) * (turns_remaining / 7.0))
                completion_value = prob_completion * self.TEMPURA_PAIR_VALUE
            else:
                completion_value = 0
        else:
            completion_value = 0
        
        return immediate_value + completion_value
    
    def calculate_sashimi_ev(self, remaining_cards, turns_remaining):
        """Calculate expected value of playing a sashimi"""
        current_triples = self.sashimi_count // 3
        new_triples = (self.sashimi_count + 1) // 3
        
        immediate_value = (new_triples - current_triples) * self.SASHIMI_TRIPLE_VALUE
        
        # Probability of completing another triple
        remainder = (self.sashimi_count + 1) % 3
        if remainder == 0:  # Just completed a triple, no completion value
            completion_value = 0
        else:
            # Need 2 or 1 more sashimi
            needed = 3 - remainder
            sashimi_remaining = remaining_cards[Card.Type.SASHIMI] - 1
            total_remaining = sum(remaining_cards.values()) - 1
            
            if total_remaining > 0 and sashimi_remaining >= needed:
                # Simplified probability calculation
                cards_in_round = turns_remaining * self.NUM_PLAYERS
                prob_completion = min(1.0, (sashimi_remaining / max(1, total_remaining)) * (turns_remaining / 7.0) * needed * 0.3)
                completion_value = prob_completion * self.SASHIMI_TRIPLE_VALUE
            else:
                completion_value = 0
        
        return immediate_value + completion_value
    
    def calculate_dumpling_ev(self, remaining_cards, turns_remaining):
        """Calculate expected value of playing a dumpling (with diminishing returns)"""
        current_score = self.DUMPLING_SCORES[min(self.dumpling_count, 5)]
        new_score = self.DUMPLING_SCORES[min(self.dumpling_count + 1, 5)]
        
        immediate_value = new_score - current_score
        
        # Diminishing returns: each additional dumpling is worth less
        # No completion value needed - dumplings score individually
        
        return immediate_value
    
    def calculate_maki_ev(self, card, visible_cards, remaining_cards, turns_remaining, current_round):
        """Calculate expected value of playing maki based on competitive position
        
        FIX: Make evaluation RELATIVE and competitive, not linear.
        Account for denial value (preventing opponents from winning).
        Estimate opponent trajectories conservatively.
        """
        maki_value = 0
        if card.type == Card.Type.SINGLE_MAKI:
            maki_value = 1
        elif card.type == Card.Type.DOUBLE_MAKI:
            maki_value = 2
        elif card.type == Card.Type.TRIPLE_MAKI:
            maki_value = 3
        
        new_maki_total = self.maki_count + maki_value
        
        # FIX: Estimate opponent maki totals (use name matching)
        opponent_maki = []
        for player, cards in visible_cards.items():
            # Skip our own cards
            if hasattr(player, 'name') and player.name == self.name:
                continue
            player_maki = 0
            for c in cards:
                if c.type == Card.Type.SINGLE_MAKI:
                    player_maki += 1
                elif c.type == Card.Type.DOUBLE_MAKI:
                    player_maki += 2
                elif c.type == Card.Type.TRIPLE_MAKI:
                    player_maki += 3
            opponent_maki.append(player_maki)
        
        # FIX: More sophisticated relative evaluation
        if opponent_maki:
            max_opponent = max(opponent_maki)
            min_opponent = min(opponent_maki)
            
            # Estimate future maki from remaining cards (conservative)
            maki_remaining = (remaining_cards[Card.Type.SINGLE_MAKI] + 
                             remaining_cards[Card.Type.DOUBLE_MAKI] * 2 + 
                             remaining_cards[Card.Type.TRIPLE_MAKI] * 3)
            
            # Conservative estimate: opponents will get some maki
            # Assume they get proportional share of remaining maki
            cards_per_opponent = turns_remaining  # Each opponent gets ~turns_remaining more cards
            total_cards_remaining = sum(remaining_cards.values())
            if total_cards_remaining > 0:
                maki_density = maki_remaining / total_cards_remaining
                estimated_opponent_gain = cards_per_opponent * maki_density * 0.6  # Conservative 60%
            else:
                estimated_opponent_gain = 0
            
            estimated_max = max_opponent + estimated_opponent_gain
            estimated_second = sorted(opponent_maki, reverse=True)[1] if len(opponent_maki) > 1 else max_opponent
            estimated_second += estimated_opponent_gain * 0.8
            
            # Relative positioning evaluation
            if new_maki_total > estimated_max:
                # Strong position for first
                ev = self.MAKI_FIRST_PLACE * 0.75 + self.MAKI_SECOND_PLACE * 0.15
            elif new_maki_total > estimated_second:
                # Good position for second, possible first
                ev = self.MAKI_SECOND_PLACE * 0.65 + self.MAKI_FIRST_PLACE * 0.2
            elif new_maki_total >= estimated_second * 0.85:
                # Competitive for second
                ev = self.MAKI_SECOND_PLACE * 0.4
            else:
                # Denial value: prevent opponents from getting too far ahead
                if new_maki_total < estimated_max * 0.7:
                    ev = -0.5  # Slight penalty for being far behind
                else:
                    ev = 0.5  # Small positive for staying competitive
            
            # Bonus for triple maki (high value, harder to get)
            if card.type == Card.Type.TRIPLE_MAKI:
                ev *= 1.2
        else:
            # No opponent data, assume moderate value
            ev = self.MAKI_FIRST_PLACE * 0.4
        
        return ev
    
    def calculate_nigiri_ev(self, card, remaining_cards):
        """Calculate expected value of playing nigiri
        
        FIX: Strongly prefer pairing with Squid > Salmon > Egg when wasabi available.
        Include probability of future wasabi draws.
        """
        base_value = self.NIGIRI_SCORES[card.type]
        
        # Check if wasabi is available
        if self.wasabi_available > 0:
            # FIX: Strong preference for high-value nigiri with wasabi
            if card.type == Card.Type.SQUID_NIGIRI:
                return base_value * self.WASABI_MULTIPLIER  # 9 points - highest value
            elif card.type == Card.Type.SALMON_NIGIRI:
                return base_value * self.WASABI_MULTIPLIER  # 6 points
            else:  # EGG_NIGIRI
                return base_value * self.WASABI_MULTIPLIER  # 3 points (still good)
        else:
            # Check probability of drawing wasabi in future
            wasabi_remaining = remaining_cards[Card.Type.WASABI]
            total_remaining = sum(remaining_cards.values())
            
            if total_remaining > 0 and wasabi_remaining > 0:
                # FIX: Better probability estimation
                # Probability depends on turns remaining and card density
                prob_wasabi = min(0.4, (wasabi_remaining / max(1, total_remaining)) * 1.5)
                
                # Expected value with wasabi (weighted by probability)
                wasabi_bonus = prob_wasabi * (base_value * (self.WASABI_MULTIPLIER - 1))
                ev = base_value + wasabi_bonus
                
                # FIX: Prefer saving high-value nigiri if wasabi likely
                if card.type == Card.Type.SQUID_NIGIRI and prob_wasabi > 0.2:
                    ev += 1.0  # Bonus for holding high-value nigiri when wasabi likely
            else:
                ev = base_value
        
        return ev
    
    def calculate_pudding_ev(self, visible_cards, current_round, turns_remaining):
        """Calculate expected value of playing pudding
        
        FIX: Rank-based evaluation, not linear.
        Strongly avoid being sole lowest.
        Weight much more heavily in round 3.
        """
        # FIX: Get opponent pudding counts (use name matching)
        opponent_pudding = []
        for player, cards in visible_cards.items():
            # Skip our own cards
            if hasattr(player, 'name') and player.name == self.name:
                continue
            player_pudding = sum(1 for c in cards if c.type == Card.Type.PUDDING)
            opponent_pudding.append(player_pudding)
        
        new_total = self.pudding_count + 1
        
        if current_round < 3:
            # FIX: Early rounds - moderate value, track position
            if opponent_pudding:
                # Rank-based: avoid being lowest
                if new_total <= min(opponent_pudding):
                    return 1.5  # Slight positive to avoid falling behind
                else:
                    return 0.8  # Neutral-positive
            return 1.0
        elif current_round == 3:
            # FIX: Final round - CRITICAL, rank-based evaluation
            if opponent_pudding:
                min_opponent = min(opponent_pudding)
                max_opponent = max(opponent_pudding)
                
                # Count how many are at each level
                tied_lowest = sum(1 for p in opponent_pudding if p == min_opponent)
                tied_highest = sum(1 for p in opponent_pudding if p == max_opponent)
                
                if new_total > max_opponent:
                    # We'd be highest - strong bonus
                    return self.PUDDING_BONUS * 0.9
                elif new_total == max_opponent:
                    # Tied for highest - good, but split bonus
                    return (self.PUDDING_BONUS / (tied_highest + 1)) * 0.85
                elif new_total < min_opponent:
                    # We'd be sole lowest - STRONG penalty
                    return -self.PUDDING_PENALTY * 0.95
                elif new_total == min_opponent:
                    # Tied for lowest - split penalty (better than sole lowest)
                    penalty_per_player = self.PUDDING_PENALTY / (tied_lowest + 1)
                    return -penalty_per_player * 0.9
                else:
                    # Safe middle position - small positive
                    return 2.0
            else:
                # No opponent data - assume positive
                return 3.0
        else:
            return 0.5
    
    def calculate_chopsticks_ev(self, turns_remaining, hand, remaining_cards):
        """Calculate expected value of playing chopsticks
        
        FIX: Value based on future opportunity.
        Increase in value earlier in round.
        Penalized when turns_remaining < 2.
        """
        if turns_remaining < 2:
            return -2.0  # FIX: Strong penalty - too late to be useful
        
        # FIX: Value increases with more turns remaining
        base_value = 1.5
        
        # Early in round = more valuable (more opportunities to use)
        if turns_remaining >= 5:
            base_value = 3.0  # Very valuable early
        elif turns_remaining >= 3:
            base_value = 2.0  # Moderately valuable
        
        # FIX: Estimate future hand quality
        # If many good cards remain, chopsticks more valuable
        high_value_cards = (
            remaining_cards[Card.Type.SQUID_NIGIRI] +
            remaining_cards[Card.Type.SALMON_NIGIRI] +
            remaining_cards[Card.Type.TRIPLE_MAKI] +
            remaining_cards[Card.Type.WASABI]
        )
        total_remaining = sum(remaining_cards.values())
        
        if total_remaining > 0:
            quality_factor = (high_value_cards / total_remaining) * 2.0
            base_value *= (1.0 + quality_factor)
        
        return base_value
    
    def calculate_wasabi_ev(self, remaining_cards, turns_remaining):
        """Calculate expected value of playing wasabi
        
        FIX: Strongly prefer pairing with Squid > Salmon > Egg.
        Include probability of future nigiri draws.
        """
        # FIX: Calculate expected value based on probability of drawing each nigiri type
        total_remaining = sum(remaining_cards.values())
        
        if total_remaining == 0:
            return 0
        
        # Probability of drawing each nigiri type
        prob_squid = remaining_cards[Card.Type.SQUID_NIGIRI] / total_remaining
        prob_salmon = remaining_cards[Card.Type.SALMON_NIGIRI] / total_remaining
        prob_egg = remaining_cards[Card.Type.EGG_NIGIRI] / total_remaining
        
        # Expected value: probability * (wasabi value - base value)
        # Wasabi with squid = 9 (vs 3 base) = +6 bonus
        # Wasabi with salmon = 6 (vs 2 base) = +4 bonus
        # Wasabi with egg = 3 (vs 1 base) = +2 bonus
        
        ev_squid = prob_squid * 6.0
        ev_salmon = prob_salmon * 4.0
        ev_egg = prob_egg * 2.0
        
        # FIX: Weight by turns remaining (more turns = more chances)
        turns_factor = min(1.0, turns_remaining / 5.0)
        
        total_ev = (ev_squid + ev_salmon + ev_egg) * turns_factor
        
        # FIX: Bonus if we already have high-value nigiri in hand (not tracked here, but conservative)
        # This is handled in nigiri evaluation when wasabi is available
        
        return total_ev
    
    def monte_carlo_score(self, card, hand, visible_cards, remaining_cards, current_round, turns_remaining):
        """Perform Monte Carlo simulation to estimate card value"""
        total_score_delta = 0
        
        for _ in range(self.MONTE_CARLO_ITERATIONS):
            # Simulate random completion of round
            score_delta = self._simulate_round_completion(
                card, hand, visible_cards, remaining_cards, current_round, turns_remaining
            )
            total_score_delta += score_delta
        
        return total_score_delta / self.MONTE_CARLO_ITERATIONS
    
    def _simulate_round_completion(self, card, hand, visible_cards, remaining_cards, current_round, turns_remaining):
        """Simulate one random completion of the round
        
        FIX: Monte Carlo as probabilistic opportunity estimation, not literal deck draws.
        Normalize results. Avoid drawing cards already in hand.
        """
        # Simulate our final state if we play this card
        tempura_final = self.tempura_count
        sashimi_final = self.sashimi_count
        dumpling_final = self.dumpling_count
        maki_final = self.maki_count
        pudding_final = self.pudding_count
        wasabi_final = self.wasabi_available
        nigiri_final = list(self.nigiri_played)
        
        # Add the card we're playing
        if card.type == Card.Type.TEMPURA:
            tempura_final += 1
        elif card.type == Card.Type.SASHIMI:
            sashimi_final += 1
        elif card.type == Card.Type.DUMPLING:
            dumpling_final += 1
        elif card.type == Card.Type.SINGLE_MAKI:
            maki_final += 1
        elif card.type == Card.Type.DOUBLE_MAKI:
            maki_final += 2
        elif card.type == Card.Type.TRIPLE_MAKI:
            maki_final += 3
        elif card.type == Card.Type.PUDDING:
            pudding_final += 1
        elif card.type == Card.Type.WASABI:
            wasabi_final += 1
        elif card.type in [Card.Type.EGG_NIGIRI, Card.Type.SALMON_NIGIRI, Card.Type.SQUID_NIGIRI]:
            if wasabi_final > 0:
                wasabi_final -= 1
            nigiri_final.append(card.type)
        
        # FIX: Simulate remaining turns probabilistically
        # Don't literally draw from deck - estimate opportunity
        total_remaining = sum(remaining_cards.values())
        if total_remaining > 0 and turns_remaining > 0:
            # FIX: Create card pool EXCLUDING cards in our hand
            # (We know what's in our hand, so we won't receive those cards)
            card_pool = []
            for card_type, count in remaining_cards.items():
                # Count how many of this type are in our hand (we won't receive these)
                in_hand = sum(1 for c in hand if c.type == card_type)
                available = max(0, count - in_hand)
                card_pool.extend([card_type] * available)
            
            # FIX: Simulate cards we'll receive (probabilistic, not literal)
            cards_to_receive = min(turns_remaining, len(card_pool))
            if cards_to_receive > 0 and len(card_pool) > 0:
                # Sample without replacement (more realistic)
                sample_size = min(cards_to_receive, len(card_pool))
                received_cards = random.sample(card_pool, sample_size)
                
                for received_card in received_cards:
                    if received_card == Card.Type.TEMPURA:
                        tempura_final += 1
                    elif received_card == Card.Type.SASHIMI:
                        sashimi_final += 1
                    elif received_card == Card.Type.DUMPLING:
                        dumpling_final += 1
                    elif received_card == Card.Type.SINGLE_MAKI:
                        maki_final += 1
                    elif received_card == Card.Type.DOUBLE_MAKI:
                        maki_final += 2
                    elif received_card == Card.Type.TRIPLE_MAKI:
                        maki_final += 3
                    elif received_card == Card.Type.PUDDING:
                        pudding_final += 1
                    elif received_card == Card.Type.WASABI:
                        wasabi_final += 1
                    elif received_card in [Card.Type.EGG_NIGIRI, Card.Type.SALMON_NIGIRI, Card.Type.SQUID_NIGIRI]:
                        if wasabi_final > 0:
                            wasabi_final -= 1
                        nigiri_final.append(received_card)
        
        # Calculate final score
        score = 0
        score += (tempura_final // 2) * self.TEMPURA_PAIR_VALUE
        score += (sashimi_final // 3) * self.SASHIMI_TRIPLE_VALUE
        score += self.DUMPLING_SCORES[min(dumpling_final, 5)]
        
        # Score nigiri with wasabi
        for nigiri_type in nigiri_final:
            if nigiri_type in self.NIGIRI_SCORES:
                score += self.NIGIRI_SCORES[nigiri_type]
        
        # FIX: Maki scoring - simplified but reasonable estimate
        score += maki_final * 0.5  # Conservative estimate
        
        # Pudding scoring only matters at game end, handled separately
        
        return score
    
    def score_card(self, card, hand, visible_cards, remaining_cards, current_round, turns_remaining):
        """Main scoring function combining immediate value, completion value, and Monte Carlo"""
        # Calculate heuristic-based expected value
        heuristic_ev = 0
        
        if card.type == Card.Type.TEMPURA:
            heuristic_ev = self.calculate_tempura_ev(remaining_cards, turns_remaining)
        elif card.type == Card.Type.SASHIMI:
            heuristic_ev = self.calculate_sashimi_ev(remaining_cards, turns_remaining)
        elif card.type == Card.Type.DUMPLING:
            heuristic_ev = self.calculate_dumpling_ev(remaining_cards, turns_remaining)
        elif card.type in [Card.Type.SINGLE_MAKI, Card.Type.DOUBLE_MAKI, Card.Type.TRIPLE_MAKI]:
            heuristic_ev = self.calculate_maki_ev(card, visible_cards, remaining_cards, turns_remaining, current_round)
        elif card.type in [Card.Type.EGG_NIGIRI, Card.Type.SALMON_NIGIRI, Card.Type.SQUID_NIGIRI]:
            heuristic_ev = self.calculate_nigiri_ev(card, remaining_cards)
        elif card.type == Card.Type.PUDDING:
            heuristic_ev = self.calculate_pudding_ev(visible_cards, current_round, turns_remaining)
        elif card.type == Card.Type.WASABI:
            heuristic_ev = self.calculate_wasabi_ev(remaining_cards, turns_remaining)
        elif card.type == Card.Type.CHOPSTICKS:
            heuristic_ev = self.calculate_chopsticks_ev(turns_remaining, hand, remaining_cards)
        
        # FIX: Combine with Monte Carlo (weighted combination)
        # Normalize MC results to be on similar scale as heuristic
        mc_weight = 0.25  # 25% Monte Carlo, 75% heuristic (heuristic is more reliable)
        mc_ev = self.monte_carlo_score(card, hand, visible_cards, remaining_cards, current_round, turns_remaining)
        
        # FIX: Normalize MC EV to be on similar scale (MC tends to be higher)
        # Scale factor based on typical score ranges
        mc_normalized = mc_ev * 0.3  # Normalize MC to heuristic scale
        
        final_ev = (1 - mc_weight) * heuristic_ev + mc_weight * mc_normalized
        
        return final_ev

    def choose_move(self, hand, visible_cards, current_round):
        """
        Main decision function: returns index of best card to play
        
        Args:
            hand: List of Card objects in current hand
            visible_cards: Dictionary mapping players to their played cards
            current_round: Current round number (1, 2, or 3)
        """
        # Update state if round changed
        if current_round != self.current_round_tracker:
            self.reset_round_state()
            self.current_round_tracker = current_round
        
        # Update state from visible cards
        self.update_state_from_visible(visible_cards)
        
        # Estimate turns remaining (simplified: assume ~7 turns per round)
        # More accurately: count cards in hand
        turns_remaining = len(hand) - 1  # -1 because we're about to play one
        
        # Score each card in hand
        best_index = 0
        best_score = float('-inf')
        
        for i, card in enumerate(hand):
            # Estimate remaining cards excluding this card (since we're evaluating playing it)
            card_remaining = self.estimate_remaining_cards(visible_cards, hand, current_round, exclude_card=card)
            
            score = self.score_card(card, hand, visible_cards, card_remaining, current_round, turns_remaining)
            
            if score > best_score:
                best_score = score
                best_index = i
        
        # Update state for the card we're about to play
        self._add_card_to_state(hand[best_index])
        
        return best_index