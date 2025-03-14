from player import Player, PlayerType
from deck import Deck
from util import get_valid_int_input, create_game_state, card_to_rank, card_to_suit

class SpadesGame:
    def __init__(self, num_manual, num_random, num_serach, num_rounds):
        self.round = num_rounds
        self.num_players = num_manual + num_random + num_serach
        self.players = [Player(f"Player {i}", PlayerType.MANUAL if i < num_manual else PlayerType.RANDOM if i < num_manual + num_random else PlayerType.SEARCH) for i in range(self.num_players)]
        self.deck = Deck()
        self.trump_suit = 'S'

        # Round specific
        self.cards_played_round = set()
        self.trump_broken_round = False
        self.dealer_index = 0
        self.starting_player_index = 1

    def reset_round(self):
        self.cards_played_round = set()
        self.trump_broken_round = False
        self.dealer_index = self.dealer_index + 1 % self.num_players

    def deal_cards(self, num_cards):
        self.deck.shuffle()
        for player in self.players:
            player.hand = self.deck.deal(num_cards)
    
    def score_trick(self, trick, starting_player_index):
        starting_card = trick[starting_player_index]
        starting_rank = card_to_rank(starting_card)

        winning_suit = card_to_suit(starting_card)
        winner_index = starting_player_index
        winning_rank = starting_rank

        for i in range(len(trick) - 1):
            player_index = (starting_player_index + i + 1) % self.num_players
            card = trick[player_index]
            card_rank = card_to_rank(card)
            card_suit = card_to_suit(card)

            if card_suit == self.trump_suit:
                if winning_suit != self.trump_suit or card_rank > winning_rank:
                    winner_index = player_index
                    winning_suit = self.trump_suit
                    winning_rank = card_rank
            elif card_suit == winning_suit and card_rank > winning_rank:
                winner_index = player_index
                winning_rank = card_rank
        winner = self.players[winner_index]
        winner.increment_trick_amount()
        print(f"{winner.name} wins the trick")
        return winner_index

    ## Phases

    def bidding_phase(self):
        print()
        print("-" * 25 + " Starting bidding phase " + "-" * 25)
        total_bid = 0
        total_bids = 0
        for i in range(self.num_players):
            player_index = (self.dealer_index + 1 + i) % self.num_players
            player = self.players[player_index]
            if player.type == PlayerType.MANUAL:
                self.print_board(show_hands=True)
                print(f"{player.name} is bidding")
            bid = player.getAI().bid(total_bid, total_bids, self.num_players, self.round)
            player.set_bid_amount(bid)
            total_bid += bid
            total_bids += 1
            print(f"{player.name} bids {bid}")
        print("-" * 25 + " Ending bidding phase " + "-" * 25)


    def play_trick(self, starting_player_index):
        print()
        print("*" * 25 + " Starting trick " + "*" * 25)
        trick = [None] * self.num_players
        for i in range(self.num_players):
            player_index = (starting_player_index + i) % self.num_players
            player = self.players[player_index]
            if player.type == PlayerType.MANUAL:
                self.print_board(show_hands=True, tricks=trick)
                print(f"{player.name} is playing")
            game_state = create_game_state(self, trick, player_index, self.trump_broken_round)
            card = player.getAI().play(game_state)
            player.hand.remove(card)
            trick[player_index] = card
            self.cards_played_round.add(card)
            print(f"{player.name} plays {card}")

        winner_index = self.score_trick(trick, starting_player_index)
        print("*" * 25 + " Ending trick " + "*" * 25)
        return winner_index

    def play_round(self):
        print("$" * 25 + " Starting round " + str(self.round) + " " + "$" * 25)
        for player in self.players:
            print(f"{player.name} has {player.total_score} points")
        num_cards = self.round
        self.deal_cards(num_cards)
        self.bidding_phase()

        for _ in range(num_cards):
            self.print_board(show_hands=True)
            self.starting_player_index = self.play_trick(self.starting_player_index)

        self.print_board()
        self.reset_round()
        print("$" * 25 + " Ending round " + str(self.round) + " " + "$" * 25)
    
    def score_round(self):
        for player in self.players:
            trick_amount = player.trick_amount if player.trick_amount is not None else 0
            str = f"{player.name} bid {player.bid_amount} and won {trick_amount}"
            if trick_amount == player.bid_amount:
                score = player.bid_amount + 10
            else:
                score = -1 * player.bid_amount
            player.total_score += score
            player.reset_for_new_round()
            print(f"{str} scoring {score} points")
    
    def print_board(self, show_hands=False, tricks=None):
        print()
        print("#" * 35 + " Board Top    " + "#" * 35)
        for i, player in enumerate(self.players):
            if show_hands or i == 0:
                hand_str = ' '.join(str(card) for card in player.hand)
            else:
                hand_str = ' '.join('*' for _ in player.hand)
            
            trick_str = '____' if tricks is None or tricks[i] is None else str(tricks[i])
            bid_str = '____' if player.bid_amount is None else str(player.bid_amount)
            trick_amount = '0' if player.trick_amount is None else str(player.trick_amount)
            print(f"{player.name} ({player.type.value}) Hand: {hand_str: <30} Bid: {bid_str: <5} Tricks: {trick_amount: <5} Played: {trick_str}")
        print("#" * 35 + " Board Bottom " + "#" * 35)
        print()


    def play_game(self):
        while self.round > 0:
            self.print_board()
            self.play_round()
            self.score_round()
            self.round -= 1

        winner = max(self.players, key=lambda player: player.total_score)
        print("Final Scores:")
        for player in self.players:
            print(f"{player.name}: {player.total_score} points")
        print(f"The winner is {winner.name} with {winner.total_score} points")

if __name__ == "__main__":
    num_manual_players = get_valid_int_input("Enter the number of manual players: ", 0, 4)
    num_agents_rand = get_valid_int_input("Enter the number of AI agents (Random): ", 1, 4)
    #num_agents_search = get_valid_int_input("Enter the number of AI agents (Search): ", 0, 4)
    num_agents_search = 0
    num_rounds = get_valid_int_input("Enter the number of rounds: ", 1, 100)
    game = SpadesGame(num_manual_players, num_agents_rand, num_agents_search,
                      num_rounds)
    game.play_game()