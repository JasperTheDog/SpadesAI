from ai import RandomAi, ManualAi
from enum import Enum

class PlayerType(Enum):
    MANUAL = "Manual"
    RANDOM = "Random"
    SEARCH = "Search"
class Player:
    def __init__(self, name, type):
        self.name = name
        self.hand = []
        self.bid_amount = None
        self.trick_amount = None
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
        if self.trick_amount is None:
            self.trick_amount = 0
        self.trick_amount += 1

    def update_total_score(self, score):
        self.total_score += score

    def reset_for_new_round(self):
        self.hand = []
        self.bid_amount = None
        self.trick_amount = None

    def getAI(self):
        if self.type == PlayerType.RANDOM:
            return RandomAi()
        elif self.type == PlayerType.MANUAL:
            return ManualAi()
        else:
            return RandomAi()
        