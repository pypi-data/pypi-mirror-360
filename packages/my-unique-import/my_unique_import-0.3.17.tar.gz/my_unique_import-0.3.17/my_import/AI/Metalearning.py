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
sigma_noise_x1 = 0.1  # Low noise in X for task 1
sigma_noise_z1 = 10.0  # High noise in Z for task 1
sigma_noise_x2 = 10.0  # High noise in X for task 2
sigma_noise_z2 = 0.1  # Low noise in Z for task 2
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

# Split data into train and test sets
test_size = int(0.2 * N)
indices = np.random.permutation(N)

# Task 1
# test_indices_t1 = indices[:test_size]
# train_indices_t1 = indices[test_size:]
#
# X1_train = X1[train_indices_t1]
# Z1_train = Z1[train_indices_t1]
# Y1_train = Y1[train_indices_t1]
#
# X1_test = X1[test_indices_t1]
# Z1_test = Z1[test_indices_t1]
# Y1_test = Y1[test_indices_t1]
#
# # Task 2
# test_indices_t2 = indices[:test_size]
# train_indices_t2 = indices[test_size:]
#
# X2_train = X2[train_indices_t2]
# Z2_train = Z2[train_indices_t2]
# Y2_train = Y2[train_indices_t2]
#
# X2_test = X2[test_indices_t2]
# Z2_test = Z2[test_indices_t2]
# Y2_test = Y2[test_indices_t2]

# Create TensorDatasets and DataLoaders
batch_size = 32

# Task 1
# task1_train_dataset = TensorDataset(torch.tensor(np.hstack([X1_train, Z1_train]), dtype=torch.float32),
#                                     torch.tensor(Y1_train, dtype=torch.float32))
# task1_test_dataset = TensorDataset(torch.tensor(np.hstack([X1_test, Z1_test]), dtype=torch.float32),
#                                    torch.tensor(Y1_test, dtype=torch.float32))
# task1_train_loader = DataLoader(task1_train_dataset, batch_size=batch_size, shuffle=True)
# task1_test_loader = DataLoader(task1_test_dataset, batch_size=batch_size, shuffle=False)
task1_train_loader, task1_test_loader = split_data([X1, Z1], Y1)
# Task 2
# task2_train_dataset = TensorDataset(torch.tensor(np.hstack([X2_train, Z2_train]), dtype=torch.float32),
#                                     torch.tensor(Y2_train, dtype=torch.float32))
# task2_test_dataset = TensorDataset(torch.tensor(np.hstack([X2_test, Z2_test]), dtype=torch.float32),
#                                    torch.tensor(Y2_test, dtype=torch.float32))
# task2_train_loader = DataLoader(task2_train_dataset, batch_size=batch_size, shuffle=True)
# task2_test_loader = DataLoader(task2_test_dataset, batch_size=batch_size, shuffle=False)
task2_train_loader, task2_test_loader = split_data([X2, Z2], Y2)


# Define the model with parameterized inputs
class LinearModel(nn.Module):
    def __init__(self):
        super(LinearModel, self).__init__()
        self.w = nn.Parameter(torch.randn(2, 1))
        self.b = nn.Parameter(torch.zeros(1))

    def forward(self, x, params=None):
        if params is None:
            params = {'w': self.w, 'b': self.b}
        return x @ params['w'] + params['b']


# MAML class with proper inner loop updates
class MAML:
    def __init__(self, model=None, meta_lr=0.01, inner_lr=0.01, inner_steps=1, meta_epochs=1000, batch_size=32,
                 device=None, name=None):
        if device is None:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        if model is None:
            model = LinearModel()
        self.device = device
        self.meta_lr = meta_lr
        self.inner_lr = inner_lr
        self.inner_steps = inner_steps
        self.meta_epochs = meta_epochs
        self.batch_size = batch_size
        self.model = model.to(device)
        self.meta_optimizer = optim.Adam(self.model.parameters(), lr=meta_lr)
        self.loss_fn = nn.MSELoss()
        if name is None:
            name = 'MAML'
        self.name = name

    def train(self, tasks, meta_epochs):
        inner_lr = self.inner_lr
        inner_steps = self.inner_steps
        num_tasks = len(tasks)
        meta_optimizer = self.meta_optimizer
        meta_model = self.model
        loss_fn = self.loss_fn
        device = self.device

        for epoch in range(meta_epochs):
            # Initialize meta-loss
            meta_loss = 0.0

            # For each task
            for task_loader in tasks:
                # Get a batch from the task
                X_batch, Y_batch = next(iter(task_loader))
                X_batch = X_batch.to(device)
                Y_batch = Y_batch.to(device)

                # Clone the initial parameters
                params = {'w': meta_model.w, 'b': meta_model.b}

                # Inner loop
                for _ in range(inner_steps):
                    Y_pred = meta_model(X_batch, params=params)
                    loss = loss_fn(Y_pred, Y_batch)
                    grads = torch.autograd.grad(loss, params.values(), create_graph=True)
                    params = {name: param - inner_lr * grad for (name, param), grad in zip(params.items(), grads)}

                # Compute loss with updated parameters
                Y_pred = meta_model(X_batch, params=params)
                loss = loss_fn(Y_pred, Y_batch)
                meta_loss += loss

            # Meta-update
            meta_loss /= num_tasks
            meta_optimizer.zero_grad()
            meta_loss.backward()
            meta_optimizer.step()

            if (epoch + 1) % 100 == 0:
                print(f"Epoch {epoch + 1}/{meta_epochs}, Meta Loss: {meta_loss.item():.4f}")

    def test(self, test_loader, inner_steps=1, inner_lr=0.01):
        """
        Test the MAML-trained model on a new task.

        Args:
            test_loader (DataLoader): DataLoader for the test task.
            inner_steps (int): Number of inner loop adaptation steps.
            inner_lr (float): Learning rate for inner loop updates.
        """
        meta_model = self.model
        loss_fn = nn.MSELoss()

        # Clone the initial parameters
        params = {'w': meta_model.w.clone(), 'b': meta_model.b.clone()}

        # Adaptation phase (inner loop)
        for step in range(inner_steps):
            for X_batch, Y_batch in test_loader:
                X_batch, Y_batch = X_batch.to(self.device), Y_batch.to(self.device)
                Y_pred = meta_model(X_batch, params=params)
                loss = loss_fn(Y_pred, Y_batch)
                grads = torch.autograd.grad(loss, params.values())
                params = {name: param - inner_lr * grad for (name, param), grad in zip(params.items(), grads)}

        # Evaluation phase
        total_loss = 0.0
        total_samples = 0
        with torch.no_grad():
            for X_batch, Y_batch in test_loader:
                X_batch, Y_batch = X_batch.to(self.device), Y_batch.to(self.device)
                Y_pred = meta_model(X_batch, params=params)
                loss = loss_fn(Y_pred, Y_batch)
                batch_size = X_batch.size(0)
                total_loss += loss.item() * batch_size
                total_samples += batch_size
        avg_loss = total_loss / total_samples
        return avg_loss


# Instantiate and train the MAML model
tasks_train_loaders = [task1_train_loader, task2_train_loader]  #[task1_train_loader, task2_train_loader]
maml = MAML(device=torch.device('cpu'))
print(f"Model is using device: {maml.device}")
maml.train(tasks_train_loaders, meta_epochs=1000)

# Test the MAML model on Task 1
test_loss_t1_maml = maml.test(task1_test_loader, inner_steps=5, inner_lr=0.01)
print(f"\nTest Loss on Task 1 after adaptation (MAML): {test_loss_t1_maml:.4f}")

# Test the MAML model on Task 2
test_loss_t2_maml = maml.test(task2_test_loader, inner_steps=5, inner_lr=0.01)
print(f"Test Loss on Task 2 after adaptation (MAML): {test_loss_t2_maml:.4f}")


# Ordinary train method
class OrdinaryTrainer:
    def __init__(self, model=None, lr=0.01, epochs=1000, device=None, name=None):
        if model is None:
            model = LinearModel()
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


# Train and test the ordinary model on Task 1
print("\nTraining Ordinary Model on Task 1")
ordinary_model_t1 = LinearModel()
ordinary_trainer_t1 = OrdinaryTrainer(model=ordinary_model_t1, lr=0.01, epochs=epochs, device=torch.device('cpu'))
test_loss_t1_ordinary_without_train = ordinary_trainer_t1.test(task1_test_loader)
ordinary_trainer_t1.train(task1_train_loader)
test_loss_t1_ordinary = ordinary_trainer_t1.test(task1_test_loader)
print(f"Test Loss on Task 1 (Ordinary Method): {test_loss_t1_ordinary:.4f}")

# Train and test the ordinary model on Task 2
print("\nTraining Ordinary Model on Task 2")
ordinary_model_t2 = LinearModel()
ordinary_trainer_t2 = OrdinaryTrainer(model=ordinary_model_t2, lr=0.01, epochs=epochs, device=torch.device('cpu'))
test_loss_t2_ordinary_without_train = ordinary_trainer_t2.test(task2_test_loader)
ordinary_trainer_t2.train(task2_train_loader)
test_loss_t2_ordinary = ordinary_trainer_t2.test(task2_test_loader)
print(f"Test Loss on Task 2 (Ordinary Method): {test_loss_t2_ordinary:.4f}")
print("-----------Conclusion-----------")
print(f"Test Loss on Task 1 after adaptation (MAML): {test_loss_t1_maml:.4f}")
print(f"Test Loss on Task 2 after adaptation (MAML): {test_loss_t2_maml:.4f}")
print(f"Test Loss on Task 1 (Ordinary Method): {test_loss_t1_ordinary:.4f}")
print(f"Test Loss on Task 2 (Ordinary Method): {test_loss_t2_ordinary:.4f}")
print(f"Test Loss on Task 1 without train: {test_loss_t1_ordinary_without_train:.4f}")
print(f"Test Loss on Task 2 without train: {test_loss_t2_ordinary_without_train:.4f}")
ordinary_trainer_t3 = OrdinaryTrainer(model=maml.model, lr=0.01, epochs=epochs, device=torch.device('cpu'))
ordinary_trainer_t3.train(task1_train_loader)
test_loss_t3_ordinary = ordinary_trainer_t3.test(task1_test_loader)
print(f"Test Loss on Task 1 (MAML Trained on Task 1): {test_loss_t3_ordinary:.4f}")
md2 = LinearModel()
md2.load_state_dict(maml.model.state_dict())
ordinary_trainer_t4 = OrdinaryTrainer(model=md2, lr=0.01, epochs=epochs, device=torch.device('cpu'))
ordinary_trainer_t4.train(task2_train_loader)
test_loss_t4_ordinary = ordinary_trainer_t4.test(task2_test_loader)
print(f"Test Loss on Task 2 (MAML Trained on Task 2): {test_loss_t4_ordinary:.4f}")
plt.plot(ordinary_trainer_t2.loggers, label='Ordinary Trainer')
plt.plot(ordinary_trainer_t4.loggers, label='MAML Trainer')
plt.legend()

plt.show()

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

# Create TensorDatasets and DataLoaders for low noise task
task_low_train_dataset = TensorDataset(torch.tensor(np.hstack([X_low_train, Z_low_train]), dtype=torch.float32),
                                       torch.tensor(Y_low_train, dtype=torch.float32))
task_low_test_dataset = TensorDataset(torch.tensor(np.hstack([X_low_test, Z_low_test]), dtype=torch.float32),
                                      torch.tensor(Y_low_test, dtype=torch.float32))
task_low_train_loader = DataLoader(task_low_train_dataset, batch_size=batch_size, shuffle=True)
task_low_test_loader = DataLoader(task_low_test_dataset, batch_size=batch_size, shuffle=False)

# Train and test with low noise data using Ordinary Method
print("\nTraining Ordinary Model on Low Noise Task")
ordinary_model_low = LinearModel()
ordinary_trainer_low = OrdinaryTrainer(model=ordinary_model_low, lr=0.01, epochs=epochs, device=torch.device('cpu'))
ordinary_trainer_low.train(task_low_train_loader)
test_loss_low_ordinary = ordinary_trainer_low.test(task_low_test_loader)
print(f"Test Loss on Low Noise Task (Ordinary Method): {test_loss_low_ordinary:.4f}")

# Test the MAML model on Low Noise Task
test_loss_low_maml = maml.test(task_low_test_loader, inner_steps=5, inner_lr=0.01)
print(f"Test Loss on Low Noise Task after adaptation (MAML): {test_loss_low_maml:.4f}")
ordinary_trainer_low2 = OrdinaryTrainer(model=maml.model, lr=0.01, epochs=epochs, device=torch.device('cpu'))
ordinary_trainer_low2.train(task_low_train_loader)
test_loss_low_ordinary = ordinary_trainer_low2.test(task_low_test_loader)
print(f"Test Loss on Low Noise Task (MAML Method): {test_loss_low_ordinary:.4f}")
# plt.plot(ordinary_trainer_low.loggers, label='Ordinary Trainer 1')
# plt.plot(ordinary_trainer_low2.loggers, label='MAML Trainer 2')
# plt.legend()
#
# plt.show()
display([ordinary_trainer_low, ordinary_trainer_low2], ['Ordinary Trainer', 'MAML Trainer'])

maml = MAML(device=torch.device('cpu'))
tasks_train_loaders = [task1_train_loader, task2_train_loader, task_low_train_loader]
print(f"Model is using device: {maml.device}")
maml.train(tasks_train_loaders, meta_epochs=1000)
ordinary_trainer_low2 = OrdinaryTrainer(model=maml.model, lr=0.01, epochs=epochs, device=torch.device('cpu'))
ordinary_trainer_low2.train(task2_train_loader)
test_loss_low_ordinary = ordinary_trainer_low2.test(task2_test_loader)
print(f"Test Loss on Low Noise Task (MAML Method): {test_loss_low_ordinary:.4f}")
display([ordinary_trainer_low, ordinary_trainer_low2], ['Ordinary Trainer', 'MAML Trainer'])
linear_model = LinearModel()
p_y_xz = OrdinaryTrainer(model=LinearModel(), lr=0.01, epochs=epochs, device=torch.device('cpu'))
p_y_xz.train(task1_train_loader)
p_x_z = OrdinaryTrainer(model=LinearModel(), lr=0.01, epochs=epochs, device=torch.device('cpu'))
p_x_z.train(task2_train_loader)
p_y_xz.test(task_low_train_loader)
p_x_z.test(task_low_train_loader)

index = 1
example_batch = next(iter(task_low_test_loader))

# 如果是一个 batch，可以取出第一个样本
example = {key: value[0] for key, value in example_batch.items()} if isinstance(example_batch, dict) else example_batch[0]

# 打印或测试这个样本
print("Selected example:", example)
# print(X_low_test[index], Z_low_test[index], Y_low_test[index])
print(p_y_xz.predict(example), p_x_z.predict(example))

