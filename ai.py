import random
from player import Player
from states import GameState
from util import playable_cards

class AiAgent:
    def play(self, state: GameState):
        raise NotImplementedError("This method should be overridden by subclasses")
    def manual():
        return False

class RandomAi(AiAgent):
    def play(self, state: GameState):
        playable = playable_cards(state)
        if len(playable) > 0:
            return random.choice(playable)
        else:
            print("No playable cards")
            return None        
        
class ManualAi(AiAgent):
    def play(self, state: GameState):
        print("Your hand: ", state.player_hands[state.curr_player_index])
        card = input("Play a card: ")
        while card not in state.player_hands[state.curr_player_index]:
            print("Invalid card. Please try again.")
            card = input("Play a card: ")
        return card

    def manual():
        return True