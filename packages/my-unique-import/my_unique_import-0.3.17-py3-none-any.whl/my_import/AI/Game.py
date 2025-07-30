import numpy as np
from abc import ABC, abstractmethod
import random


class Game(ABC):
    choice = random.choice

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def get_legal_actions(self):
        pass

    @abstractmethod
    def step(self, action):
        pass

    @abstractmethod
    def check_winner(self):
        pass

    def simulate(self):
        states, rewards, next_states, actions, dones = [], [], [], [], []

        while self.check_winner() == 0:
            states.append(self.state())
            actions = self.get_legal_actions()
            action = self.choice(actions)
            board, reward, done = self.step(action)
            rewards.append(reward)
            next_states.append(board)
            actions.append(action)
            dones.append(done)

        return states, actions, rewards, next_states, dones

    @abstractmethod
    def state(self):
        pass

    @abstractmethod
    def transfer_action(self):
        pass

# class Gomoku(Game):
#
#     def __init__(self, board_size=19, win_length=5):
#         super().__init__()
#         return
#
#
# if __name__ == '__main__':
#     game = Gomoku()
