from ai import RandomAi, ManualAi, MaxNAi, ExpectimaxAi, MCTSAi
from enum import Enum

class PlayerType(Enum):
    MANUAL = "Manual"
    RANDOM = "Random"
    MAXN = "MaxN"
    EXPECTIMAX = "Expectimax"
    MCTS = "MCTS"
class Player:
    def __init__(self, name, type, id):
        self.id = id
        self.name = name
        self.hand = []
        self.bid_amount = None
        self.trick_amount = 0
        self.total_score = 0
        self.type = type

    def add_card_to_hand(self, card):
        self.hand.append(card)

    def add_cards_to_hand(self, cards):
        self.hand.extend(cards)

    def remove_card_from_hand(self, card):
        self.hand.remove(card)
    
    def remove_card_from_hand_by_index(self, index):
        self.hand.pop(index)

    def set_bid_amount(self, bid):
        self.bid_amount = bid

    def increment_trick_amount(self):
        self.trick_amount += 1

    def update_total_score(self, score):
        self.total_score += score

    def reset_for_new_round(self):
        self.hand = []
        self.bid_amount = None
        self.trick_amount = 0

    def getAI(self):
        if self.type == PlayerType.RANDOM:
            return RandomAi()
        elif self.type == PlayerType.MANUAL:
            return ManualAi()
        elif self.type == PlayerType.MAXN:
            return MaxNAi()
        elif self.type == PlayerType.EXPECTIMAX:
            return ExpectimaxAi()
        elif self.type == PlayerType.MCTS:
            return MCTSAi()
        else:
            return RandomAi()
        