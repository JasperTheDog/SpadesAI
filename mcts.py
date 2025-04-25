import math
from collections import defaultdict

class MCTSNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self._untried_actions = state.getLegalActions().copy()
        self.children = []
        self.visits = 0
        self.wins = 0  # Number of times tricks_won == bid

    def untried_actions(self):
        return self._untried_actions

    def q(self):
        return self.wins

    def n(self):
        return self.visits

    def ucb1(self, c=1.4):
        if self.n() == 0:
            return float('inf')
        return self.q() / self.n() + c * math.sqrt(math.log(self.parent.n() + 1) / self.n())

    def best_child(self, c=1.4):
        return max(self.children, key=lambda child: child.ucb1(c))

    def expand(self):
        # self.print_state()
        action = self._untried_actions.pop()
        # print(f"Expanding node with action: {action}")
        next_state = self.state.generateSuccessor(action)
        child_node = MCTSNode(next_state, parent=self, action=action)
        self.children.append(child_node)
        return child_node

    def is_fully_expanded(self):
        return len(self._untried_actions) == 0

    def is_terminal(self):
        return len(self.state.player_hands[self.state.curr_player_index]) == 0
    
    def print_state(self):
        print(f"Current player index: {self.state.curr_player_index}")
        print(f"Player hand: {self.state.player_hands}")
        print(f"Cards played round: {self.state.cards_played_round}")
        print(f"Cards played trick: {self.state.cards_played_trick}")
        print(f"Trump broken: {self.state.trump_broken}")
        print(f"Untried actions: {self._untried_actions}")
