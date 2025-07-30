import numpy as np
from .Game import Game


class TicTacToe(Game):
    def __init__(self, board=None, start_player=1):
        if board is None:
            board = np.zeros((3, 3, 3), dtype=int)
        self.board = board
        self.current_player = 1
        self.start_player = start_player

    def reset(self, start_player=1):
        self.board = np.zeros((3, 3, 3), dtype=int)
        self.current_player = start_player
        self.start_player = start_player
        return self.board

    def get_legal_actions(self):
        return [(i, j) for i in range(3) for j in range(3) if self.board[0, i, j] == 0]

    def step(self, action):
        if self.board[0, action[0], action[1]] != 0:
            raise ValueError("Invalid action")
        self.board[0, action[0], action[1]] = 1
        self.board[self.current_player, action[0], action[1]] = 1
        winner = self.check_winner()
        reward = 0
        if winner == self.start_player:
            reward = 10
        elif winner == 3 - self.start_player:
            reward = -10
        elif winner == -1:
            reward = 5
        # elif winner == 0 and self.current_player == 1:
        #     reward = -1
        # elif winner == 0 and self.current_player == 2:
        #     reward = +1
        done = len(self.get_legal_actions()) == 0 or winner != 0
        self.current_player = 3 - self.current_player
        return self.board.copy(), reward, done, winner

    def check_winner(self):
        for i in range(3):
            if np.all(self.board[self.current_player, i, :] == 1):
                return self.current_player
            if np.all(self.board[self.current_player, :, i] == 1):
                return self.current_player
        if np.all(np.diag(self.board[self.current_player, :, :]) == 1):
            return self.current_player
        if np.all(np.diag(np.fliplr(self.board[self.current_player, :, :])) == 1):
            return self.current_player
        if np.all(self.board[0, :, :] == 1):
            return -1
        return 0

    def __repr__(self):
        return self.board.__repr__()

    def state(self):
        return self.board.copy()

    def __copy__(self):
        return TicTacToe(self.board.copy())

    def copy(self):
        return self.__copy__()

    def transfer_action(self, action):
        return action[0] * 3 + action[1]
