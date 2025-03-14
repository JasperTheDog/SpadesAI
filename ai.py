import random
from states import GameState
from util import playable_cards, get_valid_int_input, get_valid_input
class AiAgent:
    def play(self, state: GameState):
        raise NotImplementedError("This method should be overridden by subclasses")
    def manual(self):
        return False
    def bid(self, total_bid, total_bids, num_players, round):
        raise NotImplementedError("This method should be overridden by subclasses")

class RandomAi(AiAgent):
    def play(self, state: GameState):
        playable = playable_cards(state)
        if len(playable) > 0:
            return random.choice(playable)
        else:
            print("No playable cards")
            return None

    def bid(self, total_bid, total_bids, num_players, round):
        bid = (round - total_bid) // (num_players - total_bids)
        if total_bids == round - 1 and total_bid + bid == round:
            bid -= 1
        return bid
class ManualAi(AiAgent):
    def play(self, state: GameState):
        player_hand = state.player_hands[state.curr_player_index]
        print(f"Your hand: {player_hand}")
        card_index = get_valid_int_input(f"Play a card (0-indexed): ", 0, len(player_hand) - 1)
        card = player_hand[card_index]
        return card

    def manual(self):
        return True
    
    def bid(self, total_bid, total_bids, num_players, round):
        allowed_bids = [bid for bid in range(round + 1) if (total_bid + bid != round or total_bids != num_players - 1)]
        str_allowed_bids = ', '.join(map(str, allowed_bids))
        print(f"Allowed bids: {str_allowed_bids}")
        string_list = [str(bid) for bid in allowed_bids]
        bid = get_valid_input(f"Enter your bid: ", string_list)
        return int(bid)