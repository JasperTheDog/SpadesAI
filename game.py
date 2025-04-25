from player import Player, PlayerType
from deck import Deck
from util import get_valid_int_input, card_to_rank, card_to_suit
from states import create_game_state
import argparse
import random

class SpadesGame:
    def __init__(self, num_manual, num_random, num_agents_min_max, num_agents_expectimax, num_agents_mcts, num_rounds, skip_rounds_below=0, text_disable=False):
        self.round = num_rounds
        self.num_players = num_manual + num_random + num_agents_min_max + num_agents_expectimax + num_agents_mcts
        self.players = [
            Player(
            f"Player {i}",
            PlayerType.MANUAL if i < num_manual else
            PlayerType.RANDOM if i < num_manual + num_random else
            PlayerType.MAXN if i < num_manual + num_random + num_agents_min_max else
            PlayerType.EXPECTIMAX if i < num_manual + num_random + num_agents_min_max + num_agents_expectimax else
            PlayerType.MCTS,
            i
            )
            for i in range(self.num_players)
        ]
        random.shuffle(self.players)
        self.deck = Deck()
        self.trump_suit = 'S'

        # Round specific
        self.cards_played_round = set()
        self.trump_broken_round = False
        self.dealer_index = 0
        self.starting_player_index = 1

        # Options
        self.skip_rounds_below = skip_rounds_below
        self.text_disable = text_disable

    def reset_round(self):
        self.cards_played_round = set()
        self.trump_broken_round = False
        self.dealer_index = (self.dealer_index + 1) % self.num_players
        self.deck.reset()

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
        if not self.text_disable:
            print(f"{winner.name} wins the trick")
        return winner_index

    ## Phases

    def bidding_phase(self):
        if not self.text_disable:
            print()
            print("-" * 25 + " Starting bidding phase " + "-" * 25)
        total_bid = 0
        total_bids = 0
        for i in range(self.num_players):
            player_index = (self.dealer_index + 1 + i) % self.num_players
            player = self.players[player_index]
            if player.type == PlayerType.MANUAL:
                if not self.text_disable:
                    self.print_board(show_hands=True)
                    print(f"{player.name} is bidding")
            bid = player.getAI().bid(self.players[player_index].hand, total_bid, total_bids, self.num_players, self.round)
            player.set_bid_amount(bid)
            total_bid += bid
            total_bids += 1
            if not self.text_disable:
                print(f"{player.name} bids {bid}")
        if not self.text_disable:
            print("-" * 25 + " Ending bidding phase " + "-" * 25)


    def play_trick(self, starting_player_index):
        if not self.text_disable:
            print()
            print("*" * 25 + " Starting trick " + "*" * 25)
        trick = [None] * self.num_players
        for i in range(self.num_players):
            player_index = (starting_player_index + i) % self.num_players
            player = self.players[player_index]
            if player.type == PlayerType.MANUAL:
                if not self.text_disable:
                    self.print_board(show_hands=True, tricks=trick)
                    print(f"{player.name} is playing")
            game_state = create_game_state(self, trick, player_index, self.trump_broken_round)
            card = player.getAI().play(game_state)
            player.hand.remove(card)
            trick[player_index] = card
            self.cards_played_round.add(card)
            if not self.text_disable:
                print(f"{player.name} plays {card}")

        winner_index = self.score_trick(trick, starting_player_index)
        if not self.text_disable:
            print("*" * 25 + " Ending trick " + "*" * 25)
        return winner_index

    def play_round(self):
        if not self.text_disable:
            print()
            print("$" * 25 + " Starting round " + str(self.round) + " " + "$" * 25)
            for player in self.players:
                print(f"{player.name} has {player.total_score} points")
        num_cards = self.round
        self.deal_cards(num_cards)
        self.bidding_phase()

        for _ in range(num_cards):
            if not self.text_disable:
                self.print_board(show_hands=True)
            self.starting_player_index = self.play_trick(self.starting_player_index)

        if not self.text_disable:
            self.print_board()
        self.reset_round()
        if not text_disable:
            print("$" * 25 + " Ending round " + str(self.round) + " " + "$" * 25)
    
    def score_round(self):
        for player in self.players:
            trick_amount = player.trick_amount
            str = f"{player.name} bid {player.bid_amount} and won {trick_amount}"
            if trick_amount == player.bid_amount:
                score = player.bid_amount + 10
            else:
                score = -1 * player.bid_amount
            player.total_score += score
            player.reset_for_new_round()
            if not self.text_disable:
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
            trick_amount = str(player.trick_amount)
            print(f"{player.name} ({player.type.value}) Hand: {hand_str: <30} Bid: {bid_str: <5} Tricks: {trick_amount: <5} Played: {trick_str}")
        print("#" * 35 + " Board Bottom " + "#" * 35)
        print()


    def play_game(self):
        while self.round > self.skip_rounds_below:
            if not self.text_disable:
                self.print_board()
            self.play_round()
            self.score_round()
            self.round -= 1

        winner = max(self.players, key=lambda player: player.total_score)
        print("Final Scores:")
        for player in self.players:
            print(f"{player.name}: {player.total_score} points")
        print(f"The winner is {winner.name} with {winner.total_score} points")
        sorted_players = sorted(self.players, key=lambda player: player.total_score, reverse=True)
        return sorted_players

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play a game of Spades.")
    parser.add_argument("-m", "--manual", type=int, default=0, help="Number of manual players (0-4).")
    parser.add_argument("-r", "--random", type=int, default=0, help="Number of AI agents (Random) (0-4).")
    parser.add_argument("-x", "--maxn", type=int, default=0, help="Number of AI agents (MaxN) (0-4).")
    parser.add_argument("-e", "--expectimax", type=int, default=0, help="Number of AI agents (Expectimax) (0-4).")
    parser.add_argument("-mcts", "--montecarlo", type=int, default=0, help="Number of AI agents (Monte Carlo Tree Search) (0-4).")
    parser.add_argument("-n", "--rounds", type=int, default=10, help="Number of rounds (1-100).")
    parser.add_argument("-s", "--sim", type=int, default=None, help="Simulation mode (1-1000).")
    parser.add_argument("-d", "--disable-text", action="store_true", help="Disable text output.")
    args = parser.parse_args()

    num_manual_players = args.manual
    num_agents_rand = args.random
    num_agents_max_n = args.maxn
    num_agents_expectimax = args.expectimax
    num_agents_mcts = args.montecarlo
    text_disable = args.disable_text
    total_players = num_manual_players + num_agents_rand + num_agents_max_n + num_agents_expectimax + num_agents_mcts
    num_rounds = args.rounds 

    if args.sim:
        stats = []
        for _ in range(args.sim):
            print("Game:", _ + 1)
            game = SpadesGame(num_manual_players, num_agents_rand, num_agents_max_n, num_agents_expectimax, num_agents_mcts , num_rounds, 0, text_disable)
            sorted_score_players = game.play_game()
            single_game_stats = {player.id: (i + 1, player.total_score) for i, player in enumerate(sorted_score_players)}
            stats.append(single_game_stats)
        print("Simulation results:")
        aggregated_stats = {}
        for game_stats in stats:
            for player_id, (standing, score) in game_stats.items():
                if player_id not in aggregated_stats:
                    aggregated_stats[player_id] = {"total_standing": 0, "total_score": 0, "games_played": 0}
                aggregated_stats[player_id]["total_standing"] += standing
                aggregated_stats[player_id]["total_score"] += score
                aggregated_stats[player_id]["games_played"] += 1

        for player_id, data in aggregated_stats.items():
            avg_standing = data["total_standing"] / data["games_played"]
            avg_score = data["total_score"] / data["games_played"]
            print(f"Player {player_id}: Average Standing: {avg_standing:.2f}, Average Score: {avg_score:.2f}")

    else:
        game = SpadesGame(num_manual_players, num_agents_rand, num_agents_max_n,num_agents_expectimax , num_agents_mcts, num_rounds, 0, text_disable)
        game.play_game()