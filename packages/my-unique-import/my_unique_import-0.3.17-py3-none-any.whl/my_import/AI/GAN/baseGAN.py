import os
import subprocess

import numpy as np
import torch
from matplotlib import pyplot as plt
from torch.utils.tensorboard import SummaryWriter

from my_import import ClassBuilder
from my_import.AI.AI import MyDataLoader, Trainer


class baseGANTrainer:

    def __init__(self, data_loader: MyDataLoader, generator=None, discriminator=None, device=None,
                 log_dir=None, auto_save=True, writer=None, verbose=0, evaluation_interval=10, mem_threshold=0.9, lr_G=0.01, lr_D=0.01,
                 scheduler=None, patience=5, save_interval=10, model_save_dir=None, **kwargs):
        self.params = ClassBuilder.get_params()

        if device is None:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        if isinstance(data_loader, str):
            data_loader = MyDataLoader(data_loader)
        # if generator is not None:
        #     self.generator = generator.to(self.device)
        # if discriminator is not None:
        #     self.discriminator = discriminator.to(self.device)
        print('Using device: {device}'.format(device=device))
        self.num_classes = len(data_loader.classes)
        self.device = device
        self.verbose = verbose
        self.data_loader = data_loader
        # self.lr = lr
        self.save_interval = save_interval
        if writer is None:
            writer = SummaryWriter(log_dir)
        self.log_dir = log_dir if log_dir is not None else writer.get_logdir()
        self.writer = writer
        self.auto_save = auto_save
        self.epoch = kwargs.get('epoch', 0)
        self.evaluation_interval = evaluation_interval
        self.mem_threshold = mem_threshold
        self.scheduler = scheduler
        self.patience = patience
        self.best_loss = np.inf
        self.early_stop_counter = 0
        if model_save_dir is None:
            model_save_dir = os.path.join(data_loader.data_dir, 'models')
        self.result_dir = os.path.join(data_loader.data_dir, 'result')
        os.makedirs(self.result_dir, exist_ok=True)
        self.model_save_dir = model_save_dir
        self.lr_G= lr_G
        self.lr_D= lr_D


    def scheduler_step(self):
        if self.scheduler is not None:
            self.scheduler.step()

    def _auto_save(self, epoch):
        if Trainer.is_inverval(epoch, self.save_interval):
            save_path = os.path.join(self.model_save_dir, f'model_epoch_{epoch:02d}.pth')
            self.save_model(path=save_path, epoch=epoch)

    def _auto_plot_loss(self, epoch):
        if Trainer.is_inverval(epoch, self.save_interval):
            self.plot_loss(epoch=epoch)

    def close(self):
        self.writer.close()

    def show(self):
        print(self.log_dir)
        subprocess.Popen(['tensorboard', '--logdir', os.path.dirname(self.log_dir)])

        print(f"TensorBoard is running. Open http://localhost:6006/ in your browser.")

    def set_scheduler(self, scheduler, **kwargs):
        self.scheduler = scheduler(self.optimizer, **kwargs)

    def get_lr(self):
        if self.scheduler is None:
            return self.optimizer.param_groups[0]['lr']
        else:
            return self.scheduler.get_last_lr()[0]

    def plot_loss(self, epoch=None):
        self_loss = self.losses
        epochs = sorted(list(set([item[1] for key in self_loss for item in self_loss[key]])))
        plt.figure(figsize=(12, 7))

        for loss_name, loss_data_tuples in self_loss.items():
            current_losses = [item[0] for item in loss_data_tuples]
            plt.plot(epochs, current_losses, label=loss_name.replace('_', ' ').title(), linestyle='-')

        plt.xlabel('Epoch')
        plt.ylabel('Loss Value')
        plt.title('Training Loss Trends Over Epochs')
        plt.legend()
        plt.grid(True)
        if epoch is None:
            epoch = self.epoch

        plot_filename = os.path.join(self.result_dir, f'loss_{epoch}.png')
        plt.savefig(plot_filename)
        print("Saved loss to {}".format(plot_filename))
