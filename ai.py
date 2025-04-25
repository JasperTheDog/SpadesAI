import random
import time
from states import GameState, playable_cards
from util import get_valid_int_input, get_valid_input
from mcts import MCTSNode

NUM_SAMPLES = 500  # number of playouts per action
MADE_BID = 10

class AiAgent:
    def play(self, state: GameState):
        raise NotImplementedError("This method should be overridden by subclasses")
    def manual(self):
        return False
    # def bid(self, total_bid, total_bids, num_players, round):
    #     bid = (round - total_bid) // (num_players - total_bids)
    #     if total_bids == round - 1 and total_bid + bid == round:
    #         bid -= 1
    #     return bid
    def bid(self, hand, total_bid, total_bids, num_players, round_num):
        trump_suit = 'S'

        high_cards = sum(1 for c in hand if c[0] in ['A', 'K', 'Q', 'J'])
        trump_count = sum(1 for c in hand if c[1] == trump_suit)
        strong_trumps = sum(1 for c in hand if c[1] == trump_suit and c[0] in ['A', 'K', 'Q', 'J'])
        # Calculate the ratio of each suit in the hand
        suit_counts = {suit: sum(1 for c in hand if c[1] == suit) for suit in ['S', 'H', 'D', 'C']}
        total_cards = len(hand)
        non_high_cards_low_suit_ratio = sum(
            1 for suit, count in suit_counts.items() if count / total_cards < 0.2
            for c in hand if c[1] == suit and c[0] in ['8', '9', '10']
        )

        # Heuristic: Estimate bid based on combined power
        score = 0
        score += 1 * strong_trumps  # strong trumps likely win tricks
        score += 0.6 * (trump_count - strong_trumps)  # weak trumps are worth less
        score += 0.4 * (high_cards - strong_trumps)  # non-trump high cards
        score += .5 * non_high_cards_low_suit_ratio  # non-high cards in low-suit
        
        # print("Score:", score)

        estimated_bid = round(score)

        # Clamp to round range
        estimated_bid = max(0, min(estimated_bid, round_num))

        # Enforce the “no perfect bid sum” rule
        allowed_bids = [bid for bid in range(round_num + 1)
                        if (total_bids < num_players - 1 or total_bid + bid != round_num)]

        # Pick closest allowed bid
        if estimated_bid in allowed_bids:
            return estimated_bid
        else:
            return min(allowed_bids, key=lambda x: abs(x - estimated_bid))


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
        player_hand = state.player_hands[state.curr_player_index]
        playable = playable_cards(state)
        print(f"Your hand: {player_hand}")
        print(f"Playable cards: {playable}")
        card_index = get_valid_int_input(f"Play a card (0-indexed): ", 0, len(playable) - 1)
        card = playable[card_index]
        return card

    def manual(self):
        return True
    
    def bid(self, hand, total_bid, total_bids, num_players, round):
        allowed_bids = [bid for bid in range(round + 1) if (total_bid + bid != round or total_bids != num_players - 1)]
        str_allowed_bids = ', '.join(map(str, allowed_bids))
        print(f"Allowed bids: {str_allowed_bids}")
        string_list = [str(bid) for bid in allowed_bids]
        bid = get_valid_input(f"Enter your bid: ", string_list)
        return int(bid)
    

class MaxNAi(AiAgent):
    def __init__(self, depth=5):
        self.depth = depth
    
    def evaluationFunction(self, gameState: GameState):
        pass
    
    def utility(self, gameState: GameState):
        utilities = []
        for i in range(gameState.getNumPlayers()):
            if gameState.tricks_won[i] == gameState.bids[i]:
                utilities.append(MADE_BID)  # Utility of 1 if the player met their bid
            else:
                distance = abs(gameState.tricks_won[i] - gameState.bids[i])
                utilities.append(-1 * distance)  # Utility decreases by -1 per trick away from bid
        return tuple(utilities)

        
    def play(self, state: GameState):
        my_index = state.curr_player_index

        def maxn(gameState, agentIndex, currMaxUtilSum = [0] * state.getNumPlayers()):
            assert(agentIndex == gameState.curr_player_index)
            # Terminal node
            if len(gameState.player_hands[agentIndex]) == 0:
                return self.utility(gameState)

            nextAgent = (agentIndex + 1) % gameState.getNumPlayers()
            best_util = None
            best_action = None

            for action in gameState.getLegalActions():
                successor = gameState.generateSuccessor(action)
                utilities = maxn(successor, nextAgent)

                if best_util is None or utilities[agentIndex] > best_util[agentIndex]:
                    best_util = utilities
                    best_action = action

            if agentIndex == my_index:
                return best_util
            else:
                return best_util

        # Root call: pick best action based on our utility
        legal_actions = state.getLegalActions()
        best_score = float('-inf')
        best_action = None

        for action in legal_actions:
            successor = state.generateSuccessor(action)
            utilities = maxn(successor, (my_index + 1) % state.getNumPlayers())
            print("Action:", action, "Utilities:", utilities)
            if utilities[my_index] > best_score:
                best_score = utilities[my_index]
                best_action = action

        return best_action
    
    def manual(self):
        return False
    

class ExpectimaxAi(AiAgent):
    def __init__(self, depth=5):
        self.depth = depth
    
    def evaluationFunction(self, gameState: GameState):
        pass
    
    def utility(self, gameState: GameState):
        utilities = []
        for i in range(gameState.getNumPlayers()):
            if gameState.tricks_won[i] == gameState.bids[i]:
                utilities.append(MADE_BID)  # Utility of 1 if the player met their bid
            else:
                distance = abs(gameState.tricks_won[i] - gameState.bids[i])
                utilities.append(-1 * distance)  # Utility decreases by -1 per trick away from bid
        return tuple(utilities)

    def simulate_random_playout(self, gameState: GameState):
        """
        Plays out the rest of the round randomly and returns the terminal state.
        """
        state = gameState.clone()  # Assume you have a deep copy method

        while not state.isTerminal():
            current = state.curr_player_index
            legal = state.getLegalActions()
            random_action = random.choice(legal)
            state = state.generateSuccessor(random_action)

        return state

    def expectimax_maxn(self, gameState: GameState, agentIndex: int, depth: int):
        if gameState.isTerminal():
            return self.utility(gameState)

        nextAgent = (agentIndex + 1) % gameState.getNumPlayers()
        legal_actions = gameState.getLegalActions()
        best_util = None

        for action in legal_actions:
            utilities_list = []

            for _ in range(NUM_SAMPLES):
                sampled_state = gameState.generateSuccessor(action)
                rollout_terminal = self.simulate_random_playout(sampled_state)
                util = self.utility(rollout_terminal)
                utilities_list.append(util)

            avg_utilities = tuple(
                sum(vals) / len(vals) for vals in zip(*utilities_list)
            )

            if best_util is None or avg_utilities[agentIndex] > best_util[agentIndex]:
                best_util = avg_utilities
                best_action = action

        return best_util if agentIndex != gameState.curr_player_index else best_action

    def play(self, state: GameState):
        my_index = state.curr_player_index
        legal_actions = state.getLegalActions()

        best_score = float('-inf')
        best_action = None

        for action in legal_actions:
            expected_utilities = []

            for _ in range(NUM_SAMPLES):
                successor = state.generateSuccessor(action)
                terminal_state = self.simulate_random_playout(successor)
                expected_utilities.append(self.utility(terminal_state))

            avg_utilities = tuple(
                sum(vals) / len(vals) for vals in zip(*expected_utilities)
            )

            # print(f"Action: {action}, Expected utilities: {avg_utilities}")

            if avg_utilities[my_index] > best_score:
                best_score = avg_utilities[my_index]
                best_action = action

        return best_action

class MCTSAi(AiAgent):
    def __init__(self, num_samples=NUM_SAMPLES, time_limit=1.0):
        self.num_samples = num_samples
        self.time_limit = time_limit

    def simulate_random_playout(self, state):
        # Random playout until end of round
        while not state.isTerminal():
            legal = state.getLegalActions()
            action = random.choice(legal)
            state = state.generateSuccessor(action)
        return state

    def mcts(self, root_state, time_limit=5.0):
        root_node = MCTSNode(root_state)
        my_index = root_state.curr_player_index
        start_time = time.time()

        while time.time() - start_time < time_limit:
            node = root_node
            # SELECTION
            while not node.is_terminal() and node.is_fully_expanded():
                node = node.best_child()

            # EXPANSION
            if not node.is_terminal() and node.untried_actions():
                node = node.expand()

            # SIMULATION
            rollout_result = self.simulate_random_playout(node.state)
            tricks = rollout_result.tricks_won[my_index]
            bid = rollout_result.bids[my_index]
            result = 1 if tricks == bid else 0

            # BACKPROPAGATION
            while node is not None:
                node.visits += 1
                node.wins += result
                node = node.parent

        # Choose best action from root
        best = max(root_node.children, key=lambda c: c.visits)
        return best.action
    
    def play(self, state: GameState):
        card = self.mcts(state, self.time_limit)
        print("MCTS action:", card)
        return card