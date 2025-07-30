import math
import random
from TTT import TicTacToe
import numpy as np


class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.value = 0

    def is_fully_expanded(self, legal_actions):
        return len(self.children) == len(legal_actions)

    def best_child(self, c_param=1.4):
        choices_weights = [
            (child.value / child.visits) + c_param * math.sqrt((2 * math.log(self.visits) / child.visits))
            for child in self.children
        ]
        return self.children[np.argmax(choices_weights)]

    def add_child(self, state, action):
        child = Node(state, self, action)
        self.children.append(child)
        return child


class MCTS:
    def __init__(self, game, n_iter=1000):
        self.game = game
        self.n_iter = n_iter


    def choice_action(self):
        legal_actions = self.game.get_legal_actions()
        action = random.choice(legal_actions)
        return action
    def search(self, initial_state):
        root = Node(initial_state)
        for _ in range(self.n_iter):
            node = self.tree_policy(root)
            reward = self.default_policy(node.state)
            self.backup(node, reward)
        return root.best_child(c_param=0)

    def tree_policy(self, node):
        while not self.is_terminal(node.state):
            legal_actions = self.game.get_legal_actions()
            if not node.is_fully_expanded(legal_actions):
                return self.expand(node, legal_actions)
            else:
                node = node.best_child()
        return node

    def expand(self, node, legal_actions):
        action = random.choice([a for a in legal_actions if a not in [child.action for child in node.children]])
        next_state, _, _ = self.game.step(action)
        return node.add_child(next_state, action)

    def default_policy(self, state):
        self.game.board = state.copy()
        current_player = self.game.current_player
        reward = 0
        while not self.is_terminal(self.game.board):
            action = self.choice_action()
            state, reward, done, _ = self.game.step(action)
            if done:
                break
        return reward if self.game.current_player != current_player else -reward

    def backup(self, node, reward):
        while node is not None:
            node.visits += 1
            node.value += reward
            node = node.parent

    def is_terminal(self, state):
        self.game.board = state
        return self.game.check_winner() != 0 or len(self.game.get_legal_actions()) == 0


# Example usage
if __name__ == '__main__':
    game = TicTacToe()
    initial_state = game.reset()
    mcts = MCTS(game, n_iter=1000)
    best_action_node = mcts.search(initial_state)
    print("Best action:", best_action_node.action)
