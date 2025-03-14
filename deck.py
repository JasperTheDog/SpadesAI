import random

class Deck:
    SUITS = ['S', 'H', 'D', 'C']
    RANKS = [str(n) for n in range(2, 11)] + ['J', 'Q', 'K', 'A']

    def __init__(self):
        self.reset()

    def reset(self):
        self.cards = [f"{rank}{suit}" for suit in self.SUITS for rank in self.RANKS]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, count: int):
        return [self.cards.pop() for _ in range(min(count, len(self.cards)))]
