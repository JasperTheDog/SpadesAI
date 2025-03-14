from states import GameState

def get_valid_input(prompt, valid_inputs):
    while True:
        user_input = input(prompt)
        if user_input in valid_inputs:
            return user_input
        else:
            print("Not a valid input. Please try again.")
    
def get_valid_int_input(prompt, min_val, max_val):
    valid_inputs = {str(i) for i in range(min_val, max_val + 1)}
    return int(get_valid_input(prompt, valid_inputs))


def create_game_state(game, cards_played_trick, current_player_index, trump_broken):
    player_hands = [player.hand for player in game.players] # Note if non-observable, other players hands should be hidden
    return GameState(player_hands, current_player_index, game.cards_played_round, cards_played_trick, trump_broken)

def card_to_rank(card):
    rank_str = card[:-1]
    if rank_str == 'J':
        return 11
    elif rank_str == 'Q':
        return 12
    elif rank_str == 'K':
        return 13
    elif rank_str == 'A':
        return 14
    else:
        return int(rank_str)

def card_to_suit(card):
    return card[-1]

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