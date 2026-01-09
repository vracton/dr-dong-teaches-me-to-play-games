from Player import Player
from SushiGo.SushiGoMove import SushiGoMove

class SushiGoCPUPlayerAdapter(Player):
    def __init__(self, player):
        super().__init__(player.name)
        self.player = player

    def getMove(self, board):
        # Backward-compatible: players may accept optional `me` and/or `board` parameters.
        hand = board.hands[self]
        visible_cards = board.played_cards
        current_round = board.current_round

        try:
            choice = self.player.choose_move(hand, visible_cards, current_round, me=self, board=board)
        except TypeError:
            try:
                choice = self.player.choose_move(hand, visible_cards, current_round, me=self)
            except TypeError:
                try:
                    choice = self.player.choose_move(hand, visible_cards, current_round, board=board)
                except TypeError:
                    choice = self.player.choose_move(hand, visible_cards, current_round)
        if choice == None:
            raise Exception("CPU Player returned None for move.")
        return SushiGoMove(self, board.hands[self][choice])
