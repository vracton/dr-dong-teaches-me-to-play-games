import os
import pickle
import random
from collections import Counter

from SushiGo.Card import Card


class SushiGoRLPlayer:
	"""A lightweight RL agent for Sushi Go.

	Class-level name allows adapters to read a default name from the type when
	the class itself (not an instance) is passed.

	Interface expectation (via SushiGoCPUPlayerAdapter):
	  - choose_move(hand, visible_cards, current_round, me=None) -> index in `hand`

	Learning strategy:
	  - Episodic update (Monte-Carlo style): after a full game, update Q(s,a)
		toward the final score obtained by this player.
	"""

	name = "RL Player"

	def __init__(
		self,
		name: str | None = None,
		alpha: float = 0.05,
		epsilon: float = 0.2,
		epsilon_min: float = 0.02,
		epsilon_decay: float = 0.999,
		seed: int | None = None,
	):
		self.name = name or self.name
		self.alpha = float(alpha)
		self.epsilon = float(epsilon)
		self.epsilon_min = float(epsilon_min)
		self.epsilon_decay = float(epsilon_decay)

		self._rng = random.Random(seed)
		self._q: dict[tuple, dict[int, float]] = {}
		self._since_last_reward: list[tuple[tuple, int]] = []  # (state, action_type_value)
		self.training = True

	# ------------------------- Public API -------------------------

	def start_episode(self) -> None:
		self._since_last_reward = []

	def observe_reward(self, reward: float) -> None:
		"""Apply a reward to the actions taken since the last reward event.

		In Sushi Go, scores typically change at the end of a round (and at final pudding).
		This provides a much denser signal than only using final score.
		"""
		if not self.training:
			return
		if not self._since_last_reward:
			return

		for state, action in self._since_last_reward:
			q_sa = self._q.get(state, {}).get(action, 0.0)
			updated = q_sa + self.alpha * (float(reward) - q_sa)
			self._q.setdefault(state, {})[action] = updated

		self._since_last_reward = []

	def compute_shaping_reward(self, old_cards: list, new_cards: list) -> float:
		"""Compute immediate reward for cards just played.

		This gives a dense signal after every turn based on the actual
		point value or expected value of what was just added.
		"""
		old_counts = Counter(c.type for c in old_cards)
		new_counts = Counter(c.type for c in new_cards)

		reward = 0.0

		# --- Tempura: +5 for completing a pair ---
		old_tempura_pairs = old_counts.get(Card.Type.TEMPURA, 0) // 2
		new_tempura_pairs = new_counts.get(Card.Type.TEMPURA, 0) // 2
		reward += (new_tempura_pairs - old_tempura_pairs) * 5.0

		# --- Sashimi: +10 for completing a triple ---
		old_sashimi_triples = old_counts.get(Card.Type.SASHIMI, 0) // 3
		new_sashimi_triples = new_counts.get(Card.Type.SASHIMI, 0) // 3
		reward += (new_sashimi_triples - old_sashimi_triples) * 10.0

		# --- Dumplings: marginal value (1->3->6->10->15) ---
		dumpling_values = [0, 1, 3, 6, 10, 15]
		old_dump = min(5, old_counts.get(Card.Type.DUMPLING, 0))
		new_dump = min(5, new_counts.get(Card.Type.DUMPLING, 0))
		reward += float(dumpling_values[new_dump] - dumpling_values[old_dump])

		# --- Nigiri: base value, 3x if wasabi waiting ---
		nigiri_types = [
			(Card.Type.EGG_NIGIRI, 1),
			(Card.Type.SALMON_NIGIRI, 2),
			(Card.Type.SQUID_NIGIRI, 3),
		]
		# Count unpaired wasabi before this play
		old_wasabi = old_counts.get(Card.Type.WASABI, 0)
		old_nigiri_total = sum(old_counts.get(t, 0) for t, _ in nigiri_types)
		unpaired_wasabi = max(0, old_wasabi - old_nigiri_total)

		for ntype, val in nigiri_types:
			added = new_counts.get(ntype, 0) - old_counts.get(ntype, 0)
			if added > 0:
				# Apply wasabi multiplier to as many as possible
				wasabi_applied = min(added, unpaired_wasabi)
				reward += wasabi_applied * val * 3.0
				unpaired_wasabi -= wasabi_applied
				reward += (added - wasabi_applied) * float(val)

		# --- Wasabi: expected future value (~2-3 points if paired) ---
		added_wasabi = new_counts.get(Card.Type.WASABI, 0) - old_counts.get(Card.Type.WASABI, 0)
		reward += added_wasabi * 2.0

		# --- Maki: competitive, scale by icon count ---
		for mtype, icons in [
			(Card.Type.SINGLE_MAKI, 1),
			(Card.Type.DOUBLE_MAKI, 2),
			(Card.Type.TRIPLE_MAKI, 3),
		]:
			added = new_counts.get(mtype, 0) - old_counts.get(mtype, 0)
			reward += added * icons * 0.5  # scaled since competitive

		# --- Pudding: end-game value, rough expected benefit ---
		added_pudding = new_counts.get(Card.Type.PUDDING, 0) - old_counts.get(Card.Type.PUDDING, 0)
		reward += added_pudding * 1.5

		# --- Chopsticks: optionality value ---
		added_chopsticks = new_counts.get(Card.Type.CHOPSTICKS, 0) - old_counts.get(Card.Type.CHOPSTICKS, 0)
		reward += added_chopsticks * 1.0

		return reward

	def end_episode(self, reward: float | None = None) -> None:
		if not self.training:
			return

		# Optional final flush (e.g. if training uses only end-of-game reward)
		if reward is not None:
			self.observe_reward(float(reward))

		# Decay epsilon once per episode
		self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

	def save(self, path: str) -> None:
		os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
		payload = {
			"q": self._q,
			"alpha": self.alpha,
			"epsilon": self.epsilon,
			"epsilon_min": self.epsilon_min,
			"epsilon_decay": self.epsilon_decay,
			"name": self.name,
		}
		with open(path, "wb") as f:
			pickle.dump(payload, f)

	def load(self, path: str) -> None:
		with open(path, "rb") as f:
			payload = pickle.load(f)
		self._q = payload.get("q", {})
		self.alpha = float(payload.get("alpha", self.alpha))
		self.epsilon = float(payload.get("epsilon", self.epsilon))
		self.epsilon_min = float(payload.get("epsilon_min", self.epsilon_min))
		self.epsilon_decay = float(payload.get("epsilon_decay", self.epsilon_decay))
		self.name = payload.get("name", self.name)

	def choose_move(self, hand, visible_cards, current_round, me=None, board=None):
		"""Return the index (0..len(hand)-1) of the card to play."""
		if not hand:
			raise ValueError("Hand is empty; cannot choose a move.")

		state = self._encode_state(hand, visible_cards, current_round, me=me)
		
		# Actions are card types present in hand.
		available_actions = sorted({card.type.value for card in hand})
		action = self._select_action(state, available_actions)

		# Convert chosen card type to an index in hand.
		candidate_indices = [i for i, card in enumerate(hand) if card.type.value == action]
		chosen_index = self._rng.choice(candidate_indices)

		if self.training:
			self._since_last_reward.append((state, action))
		
		return chosen_index

	# ------------------------- Internals -------------------------

	def _select_action(self, state: tuple, available_actions: list[int]) -> int:
		# Epsilon-greedy
		if self.training and self._rng.random() < self.epsilon:
			return self._rng.choice(available_actions)

		# State-aware priorities that adjust based on game situation
		# Unpack state: (can_complete_tempura, can_complete_sashimi, can_use_wasabi, 
		#                best_nigiri, dumpling_bucket, has_dumpling, hand_size_bucket)
		can_complete_tempura, can_complete_sashimi, can_use_wasabi, best_nigiri, dumpling_bucket, has_dumpling, hand_size_bucket = state
		
		# Dynamic priority calculation
		priorities = {}
		
		for a in available_actions:
			card_type = Card.Type(a)
			
			# Base values (expected points)
			if card_type == Card.Type.SQUID_NIGIRI:
				val = 9.0 if can_use_wasabi else 3.0
			elif card_type == Card.Type.SALMON_NIGIRI:
				val = 6.0 if can_use_wasabi else 2.0
			elif card_type == Card.Type.EGG_NIGIRI:
				val = 3.0 if can_use_wasabi else 1.0
			elif card_type == Card.Type.WASABI:
				val = 4.0 if best_nigiri > 0 else 2.0  # More valuable if nigiri in hand
			elif card_type == Card.Type.TEMPURA:
				val = 5.0 if can_complete_tempura else 2.0  # Complete pair = 5pts
			elif card_type == Card.Type.SASHIMI:
				val = 5.0 if can_complete_sashimi else 2.5  # Sashimi is risky
			elif card_type == Card.Type.DUMPLING:
				# Marginal value: 1->2->3->4->5
				marginal = [1, 2, 3, 4, 5][min(dumpling_bucket, 4)]
				val = float(marginal)
			elif card_type == Card.Type.TRIPLE_MAKI:
				val = 2.5  # ~half of 6pts for winning
			elif card_type == Card.Type.DOUBLE_MAKI:
				val = 1.5
			elif card_type == Card.Type.SINGLE_MAKI:
				val = 0.5
			elif card_type == Card.Type.PUDDING:
				val = 2.0  # Long-term value
			elif card_type == Card.Type.CHOPSTICKS:
				val = 1.0 if hand_size_bucket == 2 else 0.5  # Better early
			else:
				val = 0.0
			
			# Add learned Q-value adjustment
			q_state = self._q.get(state, {})
			q_adjustment = q_state.get(a, 0.0) * 0.5  # Scale down Q influence
			
			priorities[a] = val + q_adjustment
		
		# Pick highest priority action
		best_action = max(available_actions, key=lambda a: priorities.get(a, 0))
		return best_action

	def _encode_state(self, hand, visible_cards, current_round: int, me=None) -> tuple:
		"""State encoding focused on combo completion opportunities.
		
		Key insight: the most valuable decisions are about completing combos.
		We encode whether each combo-completing opportunity exists.
		"""
		hand_counts = Counter(card.type for card in hand)

		my_cards = []
		if me is not None and visible_cards is not None and me in visible_cards:
			my_cards = visible_cards[me]

		my_counts = Counter(card.type for card in my_cards)

		# --- Combo completion opportunities (high value decisions) ---
		# Can complete tempura pair? (have 1 played + 1 in hand)
		can_complete_tempura = 1 if (my_counts.get(Card.Type.TEMPURA, 0) % 2 == 1 and 
									  hand_counts.get(Card.Type.TEMPURA, 0) > 0) else 0
		
		# Can complete sashimi triple?
		sashimi_needed = 3 - (my_counts.get(Card.Type.SASHIMI, 0) % 3)
		can_complete_sashimi = 1 if (sashimi_needed <= hand_counts.get(Card.Type.SASHIMI, 0) and
									  sashimi_needed <= 3) else 0
		
		# Have wasabi waiting + nigiri available?
		nigiri_count = sum(my_counts.get(t, 0) for t in [Card.Type.SALMON_NIGIRI, Card.Type.SQUID_NIGIRI, Card.Type.EGG_NIGIRI])
		has_unpaired_wasabi = my_counts.get(Card.Type.WASABI, 0) > nigiri_count
		has_nigiri_in_hand = any(hand_counts.get(t, 0) > 0 for t in [Card.Type.SALMON_NIGIRI, Card.Type.SQUID_NIGIRI, Card.Type.EGG_NIGIRI])
		can_use_wasabi = 1 if (has_unpaired_wasabi and has_nigiri_in_hand) else 0
		
		# Best nigiri available (for wasabi decision)
		best_nigiri = 0
		if hand_counts.get(Card.Type.SQUID_NIGIRI, 0) > 0:
			best_nigiri = 3
		elif hand_counts.get(Card.Type.SALMON_NIGIRI, 0) > 0:
			best_nigiri = 2
		elif hand_counts.get(Card.Type.EGG_NIGIRI, 0) > 0:
			best_nigiri = 1

		# Dumpling count (marginal value changes)
		dumpling_bucket = min(3, my_counts.get(Card.Type.DUMPLING, 0))
		has_dumpling_in_hand = 1 if hand_counts.get(Card.Type.DUMPLING, 0) > 0 else 0
		
		# Hand size (early = can start combos, late = must complete or take points)
		hand_size_bucket = 0 if len(hand) <= 2 else (1 if len(hand) <= 4 else 2)

		return (
			can_complete_tempura,
			can_complete_sashimi,
			can_use_wasabi,
			best_nigiri,
			dumpling_bucket,
			has_dumpling_in_hand,
			hand_size_bucket,
		)

