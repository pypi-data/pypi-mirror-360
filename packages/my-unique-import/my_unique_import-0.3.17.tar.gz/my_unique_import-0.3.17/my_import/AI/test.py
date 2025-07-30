import numpy as np
import torch
from torch import nn, optim
from torch.utils.data import DataLoader, TensorDataset
import random
from matplotlib import pyplot as plt

seed = 0
np.random.seed(seed)
torch.manual_seed(seed)
random.seed(seed)
torch.cuda.manual_seed(seed)
torch.cuda.manual_seed_all(seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

# Number of samples
N = 1000
epochs = 100

# Noise levels
sigma_noise_x1 = 10  # Low noise in X for task 1
sigma_noise_z1 = 0.1# High noise in Z for task 1
sigma_noise_x2 = 0.1  # High noise in X for task 2
sigma_noise_z2 = 10  # Low noise in Z for task 2
sigma_epsilon = 0.1  # Noise in Y


def generate_data(variable, noise_level):
    pass


def split_data(variable, Y, batch_size=64):
    N = len(Y)
    test_size = int(0.2 * N)
    indices = np.random.permutation(N)
    test_indices = indices[:test_size]
    train_indices = indices[test_size:]
    train_data = []
    test_data = []
    for i in variable:
        train_data.append(i[train_indices])
        test_data.append(i[test_indices])
    Y_train = Y[train_indices]
    Y_test = Y[test_indices]
    if len(variable) == 1:
        train_loader = DataLoader(TensorDataset(torch.tensor(train_data[0], dtype=torch.float32),
                                                 torch.tensor(Y_train, dtype=torch.float32)),
                                       batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(TensorDataset(torch.tensor(test_data[0], dtype=torch.float32),
                                                torch.tensor(Y_test, dtype=torch.float32)),
                                      batch_size=batch_size, shuffle=False)
        return train_loader, test_loader
    else:

        train_dataset = TensorDataset(torch.tensor(np.hstack(train_data), dtype=torch.float32),
                                      torch.tensor(Y_train, dtype=torch.float32))
        test_dataset = TensorDataset(torch.tensor(np.hstack(test_data), dtype=torch.float32),
                                     torch.tensor(Y_test, dtype=torch.float32))
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    return train_loader, test_loader

def display(trainers, labels=None):
    if labels is None:
        labels = [f'Task {i.name} Trainer' for i in trainers]
    for i, label in zip(trainers, labels):
        plt.plot(i.loggers, label=label)
    plt.legend()
    plt.show()


# Generate data for task 1
 # Noisy X with low noise

Z1_true = np.random.randn(N, 1)
noise_z1 = np.random.normal(0, sigma_noise_z1, (N, 1))
Z1 = Z1_true + noise_z1  # Noisy Z with high noise
X1_true = np.sin(Z1_true)
noise_x1 = np.random.normal(0, sigma_noise_x1, (N, 1))
X1 = X1_true + noise_x1

epsilon1 = np.random.normal(0, sigma_epsilon, (N, 1))
Y1 = X1_true + epsilon1 + Z1_true

# Generate data for task 2 # Noisy X with high noise

Z2_true = np.random.randn(N, 1)
noise_z2 = np.random.normal(0, sigma_noise_z2, (N, 1))
Z2 = Z2_true + noise_z2  # Noisy Z with low noise
X2_true = np.sin(Z2_true)
noise_x2 = np.random.normal(0, sigma_noise_x2, (N, 1))
X2 = X2_true + noise_x2

epsilon2 = np.random.normal(0, sigma_epsilon, (N, 1))
Y2 = Z2_true + epsilon2 + X2_true
test_size = int(0.2 * N)
indices = np.random.permutation(N)
batch_size = 32
task1_train_loader, task1_test_loader = split_data([X1, Z1], Y1)
task2_train_loader, task2_test_loader = split_data([X2, Z2], Y2)
task2_new_train_loader, task2_new_test_loader = split_data([Z2], X2)

# class LinearModel(nn.Module):
#     def __init__(self, input_dim, output_dim):
#         super(LinearModel, self).__init__()
#         self.w = nn.Parameter(torch.randn(input_dim, output_dim))
#         self.b = nn.Parameter(torch.zeros(output_dim))
#
#     def forward(self, x, params=None):
#         if params is None:
#             params = {'w': self.w, 'b': self.b}
#         return x @ params['w'] + params['b']
class LinearModel(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(LinearModel, self).__init__()
        self.linear = nn.Linear(input_dim, output_dim)

    def forward(self, x):
        return self.linear(x)

class NonlinearNN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(NonlinearNN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, output_dim)
        )

    def forward(self, x):
        return self.network(x)

# Ordinary train method
class OrdinaryTrainer:
    def __init__(self, model=None, lr=0.01, epochs=1000, device=None, name=None, input_shape=None, output_shape=None):
        if model is None:
            model = NonlinearNN(input_shape, output_shape)
        if device is None:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"model is using device: {device}")
        self.device = device
        self.model = model.to(device)
        self.lr = lr
        self.epochs = epochs
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.loss_fn = nn.MSELoss()
        self.loggers = []
        if name is None:
            name = 'Ordinary'
        self.name = name

    def train(self, train_loader):
        for epoch in range(self.epochs):
            total_loss = 0.0
            for X_batch, Y_batch in train_loader:
                X_batch, Y_batch = X_batch.to(self.device), Y_batch.to(self.device)
                self.optimizer.zero_grad()
                Y_pred = self.model(X_batch)
                loss = self.loss_fn(Y_pred, Y_batch)
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item() * X_batch.size(0)
            avg_loss = total_loss / len(train_loader.dataset)
            self.loggers.append(avg_loss)
            if (epoch + 1) % 100 == 0:
                print(f"Epoch {epoch + 1}/{self.epochs}, Loss: {avg_loss:.4f}")

    def test(self, test_loader):
        self.model.eval()
        total_loss = 0.0
        with torch.no_grad():
            for X_batch, Y_batch in test_loader:
                X_batch, Y_batch = X_batch.to(self.device), Y_batch.to(self.device)
                Y_pred = self.model(X_batch)
                loss = self.loss_fn(Y_pred, Y_batch)
                total_loss += loss.item() * X_batch.size(0)
        avg_loss = total_loss / len(test_loader.dataset)
        return avg_loss

    def predict(self, X):
        self.model.eval()
        torch.tensor(X)
        with torch.no_grad():
            X = X.to(self.device)
            Y_pred = self.model(X)
            return Y_pred.cpu().numpy()


sigma_low_noise = 0.1  # Low noise level for X and Z

# Generate data for new task (low noise X, Z)
 # Low noise X

Z_low_true = np.random.randn(N, 1)
noise_z_low = np.random.normal(0, sigma_low_noise, (N, 1))
Z_low = Z_low_true + noise_z_low  # Low noise Z
X_low_true = np.sin(Z_low_true)
noise_x_low = np.random.normal(0, sigma_low_noise, (N, 1))
X_low = X_low_true + noise_x_low

epsilon_low = np.random.normal(0, sigma_epsilon, (N, 1))
Y_low = X_low_true + epsilon_low + Z_low_true  # Y depends on true X and Z with low noise

# Split low-noise data into train and test sets
test_indices_low = indices[:test_size]
train_indices_low = indices[test_size:]

X_low_train = X_low[train_indices_low]
Z_low_train = Z_low[train_indices_low]
Y_low_train = Y_low[train_indices_low]

X_low_test = X_low[test_indices_low]
Z_low_test = Z_low[test_indices_low]
Y_low_test = Y_low[test_indices_low]

task_low_train_dataset = TensorDataset(torch.tensor(np.hstack([X_low_train, Z_low_train]), dtype=torch.float32),
                                       torch.tensor(Y_low_train, dtype=torch.float32))
task_low_test_dataset = TensorDataset(torch.tensor(np.hstack([X_low_test, Z_low_test]), dtype=torch.float32),
                                      torch.tensor(Y_low_test, dtype=torch.float32))
task_low_train_loader = DataLoader(task_low_train_dataset, batch_size=batch_size, shuffle=True)
task_low_test_loader = DataLoader(task_low_test_dataset, batch_size=batch_size, shuffle=False)

# linear_model = LinearModel()
p_y_xz = OrdinaryTrainer(lr=0.01, epochs=epochs, device=torch.device('cpu'), input_shape=2, output_shape=1)
p_y_xz.train(task1_train_loader)
p_x_z = OrdinaryTrainer(lr=0.01, epochs=epochs, device=torch.device('cpu'), input_shape=1, output_shape=1)
p_x_z.train(task2_new_train_loader)
p_y_xz.test(task_low_train_loader)
p_x_z.test(task2_new_test_loader)

index = 1
example_batch = next(iter(task_low_test_loader))

# 提取输入数据和对应标签
if isinstance(example_batch, dict):
    inputs = example_batch['input']  # 假设数据中输入的键为 'input'
    labels = example_batch['label']  # 假设标签的键为 'label'
else:
    inputs, labels = example_batch  # 如果返回的不是字典，通常是 (inputs, labels) 的形式

# 取出第一个样本和标签
example_input = inputs
example_label = labels

# 打印样本和标签
print("Example input:", example_input)
print("Example X:", example_input[:, :1])
print("Example Z:", example_input[:, 1:])
print("Example label:", example_label)


# 打印或测试这个样本
print("Selected example:", example_input)
# print(X_low_test[index], Z_low_test[index], Y_low_test[index])
ygivenxz =p_y_xz.predict(example_input)
xgivenz = p_x_z.predict(example_input[:, 1:])
print("Selected PY|XZ:", ygivenxz)
print("Selected PX|Z:", xgivenz)
print("True label example:", example_label)
size = batch_size

pred = torch.sum(torch.tensor(ygivenxz) * torch.tensor(xgivenz) * torch.tensor(example_input[:, 1:])) / torch.tensor(example_input[:, :1])
print("Predictions:", pred)
