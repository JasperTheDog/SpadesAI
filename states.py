from util import card_to_suit, card_to_rank
class GameState:
    def __init__(self, round, player_hands, curr_player_index, cards_played_round, cards_played_trick, trump_broken, bids, tricks_won):
        self.round = round
        self.player_hands = player_hands
        self.curr_player_index = curr_player_index
        self.cards_played_round = cards_played_round
        self.cards_played_trick = cards_played_trick
        self.trump_broken = trump_broken
        self.bids = bids
        self.tricks_won = tricks_won
    
    def getNumPlayers(self):
        return len(self.player_hands)

    def getLegalActions(self):
        playable = playable_cards(self)
        if len(playable) > 0:
            return playable
        else:
            return []
    
    def generateSuccessor(self, cardPlayed):
        new_player_hands = [hand[:] for hand in self.player_hands]
        new_player_hands[self.curr_player_index].remove(cardPlayed)
        new_cards_played_round = self.cards_played_round.copy()
        new_cards_played_trick = self.cards_played_trick[:]
        new_cards_played_round.add(cardPlayed)
        new_cards_played_trick[self.curr_player_index] = cardPlayed
        new_tricks_won = self.tricks_won[:]
        if None not in new_cards_played_trick:
            winner_index = self.score_trick(new_cards_played_trick, self.curr_player_index)
            new_tricks_won[winner_index] += 1
            new_cards_played_trick = [None] * len(self.player_hands)

        
        return GameState(
            self.round,
            new_player_hands,
            (self.curr_player_index + 1) % len(self.player_hands),
            new_cards_played_round,
            new_cards_played_trick,
            self.trump_broken or (card_to_suit(cardPlayed) == 'S'),
            self.bids,
            new_tricks_won
        )
    
    def score_trick(self, trick, starting_player_index):
        starting_card = trick[starting_player_index]
        starting_rank = card_to_rank(starting_card)

        winning_suit = card_to_suit(starting_card)
        winner_index = starting_player_index
        winning_rank = starting_rank

        for i in range(len(trick) - 1):
            player_index = (starting_player_index + i + 1) % len(self.player_hands)
            card = trick[player_index]
            card_rank = card_to_rank(card)
            card_suit = card_to_suit(card)

            if card_suit == 'S':
                if winning_suit != 'S' or card_rank > winning_rank:
                    winner_index = player_index
                    winning_suit = 'S'
                    winning_rank = card_rank
            elif card_suit == winning_suit and card_rank > winning_rank:
                winner_index = player_index
                winning_rank = card_rank
        return winner_index


class PlayerState:
    def __init__(self, bid, tricks_won, hand_size, cards=None):
        self.bid = bid
        self.tricks_won = tricks_won
        self.hand_size = hand_size
        self.cards = cards if cards is not None else []


def create_game_state(game, cards_played_trick, current_player_index, trump_broken):
    player_hands = [player.hand for player in game.players] # Note if non-observable, other players hands should be hidden
    player_bids = [player.bid_amount for player in game.players]
    player_tricks_won = [player.trick_amount for player in game.players]
    return GameState(game.round, player_hands, current_player_index, game.cards_played_round, cards_played_trick, trump_broken, player_bids, player_tricks_won)

def playable_cards(gameState: GameState):
    player_hand = gameState.player_hands[gameState.curr_player_index]
    
    if player_hand is None:
        all_cards = {f"{rank}{suit}" for rank in '23456789TJQKA' for suit in 'CDHS'}
        played_cards = set(gameState.cards_played_round + gameState.cards_played_trick)
        card_pool = list(all_cards - played_cards)
    else:
        card_pool = player_hand

    # print(f"Current player index: {gameState.curr_player_index}")
    # print(f"Player hand: {player_hand}")
    # print(f"Card pool: {card_pool}")
    # print(f"Cards played round: {gameState.cards_played_round}")
    # print(f"Cards played trick: {gameState.cards_played_trick}")
    # print(f"Trump broken: {gameState.trump_broken}")
    if all(card is None for card in gameState.cards_played_trick):
        all_spades = all(card_to_suit(card) == 'S' for card in card_pool)
        if not gameState.trump_broken and not all_spades:
            card_pool = [card for card in card_pool if card_to_suit(card) != 'S']
        return card_pool
    else:
        num_non_none = sum([1 for card in gameState.cards_played_trick if card is not None])
        start_index = (gameState.curr_player_index - num_non_none) % len(gameState.player_hands)
        lead_suit = card_to_suit(gameState.cards_played_trick[start_index])
        playable = [card for card in card_pool if card_to_suit(card) == lead_suit]
        if len(playable) == 0:
            return card_pool
        else:
            return playable
