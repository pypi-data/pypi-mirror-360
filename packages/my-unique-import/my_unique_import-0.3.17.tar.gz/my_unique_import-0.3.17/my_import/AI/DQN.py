import os
import random
from collections import deque
import numpy as np
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm
from .AI import Models, Optimizer
import torch
import copy


class DQN:

    def __init__(self, game=None, q_network=None, target_network=None, optimizer=None, replay=None, criterion=None,
                 lr=1e-5, gamma=0.995, target_update=50, batch_size=64, epsilon_start=1.0, epsilon_end=0.01,
                 epsilon_decay=0.995, capacity = 10000,
                 log_dir=None, writer=None, device=None, num_classes=9, epoch=0
                 ):
        if replay is None:
            replay = MemoryReplay(capacity=capacity)
        if q_network is None:
            q_network = Models.resnet18()
            num_ftrs = q_network.fc.in_features
            q_network.fc = torch.nn.Linear(num_ftrs, num_classes)
        if target_network is None:
            target_network = Models.resnet18()
            num_ftrs = target_network.fc.in_features
            target_network.fc = torch.nn.Linear(num_ftrs, num_classes)
        if optimizer is None:
            optimizer = Optimizer.Adam(q_network.parameters(), lr=lr)
        if criterion is None:
            criterion = torch.nn.MSELoss()
        if device is None:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.lr = lr
        self.gamma = gamma
        self.game = game
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.target_update = target_update
        self.batch_size = batch_size
        self.replay = replay
        self.q_network = q_network.to(device)
        self.target_network = target_network.to(device)
        self.target_network.eval()
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device
        self.epoch = epoch
        if writer is None:
            writer = SummaryWriter(log_dir)
        self.writer = writer
        self.log_dir = log_dir if log_dir is not None else writer.get_logdir()
        self.epsilon = epsilon_start

    def prefill_replay_buffer(self, prefill_steps):
        state = self.game.reset()
        for _ in range(prefill_steps):
            action = random.choice(self.game.get_legal_actions())
            next_state, reward, done, _ = self.game.step(action)
            next_state = np.array(next_state)
            action = self.game.transfer_action(action)
            self.replay.push(state, action, reward, next_state, done)
            state = next_state if not done else self.game.reset()

    def train(self, episodes):
        device = self.device
        epsilon = self.epsilon
        self.q_network.train()
        for episode in tqdm(range(episodes), desc="Training Episodes"):
            start_player = 1 if random.random() < 0.5 else 2
            state = self.game.reset(start_player=start_player)
            state = np.array(state)
            total_reward = 0

            for t in range(200):
                if random.random() < epsilon:
                    action = random.choice(self.game.get_legal_actions())
                else:
                    with torch.no_grad():
                        board = torch.FloatTensor(state)
                        board = board.unsqueeze(0).to(device)
                        self.q_network.eval()
                        action_values = self.q_network(board).squeeze(0)
                        legal_actions_pos = self.game.get_legal_actions()
                        legal_actions = [self.game.transfer_action(action) for action in legal_actions_pos]
                        arg = torch.argmax if self.game.current_player == start_player else torch.argmin
                        action = legal_actions_pos[arg(action_values[legal_actions]).item()]
                        self.q_network.train()

                next_state, reward, done, _ = self.game.step(action)
                next_state = np.array(next_state)
                action = self.game.transfer_action(action)
                self.replay.push(state, action, reward, next_state, done)

                state = next_state
                total_reward += reward

                if len(self.replay) >= self.batch_size:
                    states, actions, rewards, next_states, dones = self.replay.sample(self.batch_size)

                    states = torch.FloatTensor(states).reshape(self.batch_size, 3, 3, 3).to(device)
                    actions = torch.LongTensor(actions).unsqueeze(1).to(device)
                    rewards = torch.FloatTensor(rewards).to(device)
                    next_states = torch.FloatTensor(next_states).reshape(self.batch_size, 3, 3, 3).to(device)
                    dones = torch.FloatTensor(dones).to(device)

                    q_values = self.q_network(states).gather(1, actions).squeeze()
                    next_q_values = self.target_network(next_states).max(1)[0]
                    target_q_values = rewards + self.gamma * next_q_values * (1 - dones)

                    loss = self.criterion(q_values, target_q_values.detach())
                    self.optimizer.zero_grad()
                    loss.backward()

                    # 梯度裁剪
                    torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), max_norm=0.5)
                    self.optimizer.step()

                    self.writer.add_scalar('Reward', total_reward, self.epoch + episode)
                    self.writer.add_scalar('Epsilon', epsilon, self.epoch + episode)
                    self.writer.add_scalar('Loss', loss.item(), self.epoch + episode)

                if done:
                    break

            epsilon = max(self.epsilon_end, self.epsilon_decay * epsilon)

            if episode % self.target_update == 0:
                self.target_network.load_state_dict(self.q_network.state_dict())

                print(f"Episode {episode}, Total Reward: {total_reward}, Epsilon: {epsilon:.2f}")

        self.epoch += episodes
        self.writer.close()

    def test_model(self, episodes=10):
        device = self.device
        self.q_network.eval()
        total_rewards = []

        for episode in range(episodes):
            state = self.game.reset()
            state = np.array(state)
            total_reward = 0

            while True:
                with torch.no_grad():
                    board = torch.FloatTensor(state)
                    board = board.unsqueeze(0).to(device)
                    action_values = self.q_network(board).squeeze(0)
                    legal_actions_pos = self.game.get_legal_actions()
                    legal_actions = [self.game.transfer_action(action) for action in legal_actions_pos]
                    arg = torch.argmax if self.game.current_player == 1 else torch.argmin

                    action = legal_actions_pos[arg(action_values[legal_actions]).item()]

                next_state, reward, done, winner = self.game.step(action)
                next_state = np.array(next_state)
                state = next_state
                total_reward += reward

                if done:
                    break

            total_rewards.append(total_reward)
            print(f"Test Episode {episode + 1}, Total Reward: {total_reward}, Winner: {winner}")

        avg_reward = np.mean(total_rewards)
        print(f"Average Total Reward over {episodes} episodes: {avg_reward}")

    def save(self, path):
        if '.pth' in path:
            return self._save_config(path)
        os.makedirs(path, exist_ok=True)
        return self._save_config(os.path.join(path, 'dqn.pth'))

    def _save_config(self, path):
        try:
            torch.save({'game': self.game, 'q_network': self.q_network, 'target_network': self.target_network,
                        'epoch': self.epoch, 'optimizer': self.optimizer, 'criterion': self.criterion, 'lr': self.lr,
                        'gamma': self.gamma, 'device': self.device, 'log_dir': self.log_dir, 'replay': self.replay,
                        'target_update': self.target_update, 'batch_size': self.batch_size,
                        'epsilon_start': self.epsilon,
                        'epsilon_end': self.epsilon_end, 'epsilon_decay': self.epsilon_decay
                        },
                       path)
            print('Saved model configuration successfully')
            return True
        except Exception as e:
            print(f'Error saving model configuration: {str(e)}')
            return False

    @staticmethod
    def load(path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"No checkpoint found at '{path}'")
        params = torch.load(os.path.join(path, 'dqn.pth'))
        return DQN(**params)


class SAC:

    def __init__(self, model, game, replay=None):
        self.model = model
        self.game = game
        if replay is None:
            replay = MemoryReplay()
        self.replay = replay

        pass

    def get_data(self):
        for i in range(200):
            res = self.game.simulate()
            self.replay.push_list(*res)
            self.game.reset()


class MemoryReplay:
    def __init__(self, capacity=10000):
        self.capacity = capacity
        self.memory = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        experience = (state, action, reward, next_state, done)
        self.memory.append(experience)

    def push_list(self, states, actions, rewards, next_states, dones):
        for state, action, reward, next_state, done in zip(states, actions, rewards, next_states, dones):
            self.push(state, action, reward, next_state, done)

    def sample(self, batch_size):
        experiences = random.sample(self.memory, batch_size)

        states, actions, rewards, next_states, dones = zip(*experiences)

        return (np.array(states),
                np.array(actions),
                np.array(rewards, dtype=np.float32),
                np.array(next_states),
                np.array(dones, dtype=np.uint8))

    def __len__(self):
        return len(self.memory)

    def size(self):
        return self.__len__()
