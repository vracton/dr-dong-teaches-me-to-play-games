from ThirtyOne.ThirtyOneMove import ThirtyOneDrawChoiceMove
from ThirtyOne.ThirtyOneMove import ThirtyOneDiscardMove
from ThirtyOne.Card import Card

def card_value(card: Card) -> int:
    if card.rank in [Card.Rank.JACK, Card.Rank.QUEEN, Card.Rank.KING]:
        return 10
    elif card.rank == Card.Rank.ACE:
        return 11
    else:
        return card.rank.value

def suit_value(cards: list[Card]) -> dict[Card.Suit, int]:
    values = {
        Card.Suit.HEARTS: 0,
        Card.Suit.DIAMONDS: 0,
        Card.Suit.CLUBS: 0,
        Card.Suit.SPADES: 0,
    }
    
    for card in cards:
        values[card.suit] += card_value(card)

    return values

def get_num_faces(cards: list[Card], suit: Card.Suit) -> int:
    count = 0
    for card in cards:
        if card.suit == suit and card.rank in [Card.Rank.JACK, Card.Rank.QUEEN, Card.Rank.KING, Card.Rank.ACE]:
            count += 1
    return count

def get_max_suit(cards: list[Card]) -> Card.Suit:
    values = suit_value(cards)
    face_counts = {suit: 0 for suit in values}
    for card in cards:
        if card.rank in [Card.Rank.JACK, Card.Rank.QUEEN, Card.Rank.KING, Card.Rank.ACE]:
            face_counts[card.suit] += 1
    max_suit = max(values, key=lambda suit: (face_counts[suit], values[suit]))
    return max_suit

# gets the suits in your hand by order (highest -> lowest)
def get_hand_suits_by_value(cards: list[Card]) -> list[Card.Suit]:
    values = suit_value(cards)
    face_counts = {suit: get_num_faces(cards, suit) for suit in values}
    sorted_suits = sorted(
        (suit for suit, val in values.items() if val > 0),
        key=lambda suit: (face_counts[suit], values[suit]),
        reverse=True,
    )
    return sorted_suits

def get_max_suit_value(cards: list[Card]) -> int:
    values = suit_value(cards)
    return values[get_max_suit(cards)]

def get_num_face_in_suit(cards: list[Card], suit: Card.Suit) -> int:
    count = 0
    for card in cards:
        if card.suit == suit and card.rank in [Card.Rank.JACK, Card.Rank.QUEEN, Card.Rank.KING, Card.Rank.ACE]:
            count += 1
    return count

def get_face_cards(cards):
    face_cards = []
    for card in cards: 
        if card.rank in [Card.Rank.JACK, Card.Rank.QUEEN, Card.Rank.KING, Card.Rank.ACE]:
            face_cards.append(card)
            
    return face_cards
        
        
class ThirtyOnePlayer():
    def __init__(self):
        super().__init__()
        self.name = "Kanchi + Sahoo"
        self.turns = 0

    def choose_draw_move(self, cards: list[Card], top_discard, move_storage):
        self.turns += 1
        # Example strategy: always draw from the deck
        # print("----------------choosing draw move------------------")
        suit = get_max_suit(cards)
        
        cur_max_val = get_max_suit_value(cards)
    
        if self.turns <= 3:
            if cur_max_val >= 20:
                # print(cur_max_val)
                return ThirtyOneDrawChoiceMove.Choice.KNOCK
            

        if cur_max_val >= 26:
            # print(cur_max_val)
            return ThirtyOneDrawChoiceMove.Choice.KNOCK
        
        if get_face_cards(cards):
            if top_discard.SUIT == suit:
                cur_suit_values = get_hand_suits_by_value(cards)
                print(cur_suit_values)
                return ThirtyOneDrawChoiceMove.Choice.DRAW_FROM_DISCARD
            else:
                return ThirtyOneDrawChoiceMove.Choice.DRAW_FROM_DECK

        return ThirtyOneDrawChoiceMove.Choice.DRAW_FROM_DECK

    def choose_discard_move(self, cards, top_discard, move_storage):
        # print('kanchi is discarding')
        
        # discard the lowest value card of the lowest value suit or troll if you have 2 face cards
        sorted_suits = get_hand_suits_by_value(cards)
        lowest_suit = sorted_suits[-1]

        cards_of_lowest_suit = [card for card in cards if card.suit == lowest_suit]
        cards_of_lowest_suit.sort(key=card_value)

        card_to_discard = cards_of_lowest_suit[0]
        return card_to_discard