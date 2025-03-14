class GameState:
    def __init__(self, player_hands, curr_player_index, cards_played_round, cards_played_trick, trump_broken):
        self.player_hands = player_hands
        self.curr_player_index = curr_player_index
        self.cards_played_round = cards_played_round
        self.cards_played_trick = cards_played_trick
        self.trump_broken = trump_broken

class PlayerState:
    def __init__(self, bid, tricks_won, hand_size, cards=None):
        self.bid = bid
        self.tricks_won = tricks_won
        self.hand_size = hand_size
        self.cards = cards if cards is not None else []