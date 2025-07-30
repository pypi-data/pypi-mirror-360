import torch
import torch.nn as nn
import torch.nn.functional as F
from .AI import Trainer, MyDataLoader
from tqdm import tqdm


class _DiffusionModel(nn.Module):
    def __init__(self, base_model, image_size):
        super(_DiffusionModel, self).__init__()
        self.base_model = base_model
        self.image_size = image_size

        feature_map_dim = image_size // 8
        if feature_map_dim < 1:
            feature_map_dim = 1

        self.latent_channels = 128

        num_features = self.base_model.fc.in_features
        self.base_model.fc = nn.Linear(num_features, feature_map_dim * feature_map_dim * self.latent_channels)

        def get_deconv_output_padding(input_dim, output_dim, kernel_size, stride, padding):
            return output_dim - ((input_dim - 1) * stride - 2 * padding + kernel_size)

        h_in_deconv1 = feature_map_dim
        h_out_deconv1 = h_in_deconv1 * 2
        op1 = get_deconv_output_padding(h_in_deconv1, h_out_deconv1, 4, 2, 1)
        self.deconv1 = nn.ConvTranspose2d(self.latent_channels, 64, kernel_size=4, stride=2, padding=1,
                                          output_padding=op1)

        h_in_deconv2 = h_out_deconv1
        h_out_deconv2 = h_in_deconv2 * 2
        op2 = get_deconv_output_padding(h_in_deconv2, h_out_deconv2, 4, 2, 1)
        self.deconv2 = nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1, output_padding=op2)

        h_in_deconv3 = h_out_deconv2
        h_out_deconv3 = h_in_deconv3 * 2
        op3 = get_deconv_output_padding(h_in_deconv3, h_out_deconv3, 4, 2, 1)
        self.deconv3 = nn.ConvTranspose2d(32, 3, kernel_size=4, stride=2, padding=1, output_padding=op3)

        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.base_model(x)

        feature_map_dim = self.image_size // 8
        if feature_map_dim < 1:
            feature_map_dim = 1

        x = x.view(x.size(0), self.latent_channels, feature_map_dim, feature_map_dim)

        x = self.relu(self.deconv1(x))
        x = self.relu(self.deconv2(x))
        x = self.deconv3(x)

        if x.shape[2] != self.image_size or x.shape[3] != self.image_size:
            x = F.interpolate(x, size=(self.image_size, self.image_size), mode='bilinear', align_corners=False)

        return x

# class _DiffusionModel(nn.Module):
#     def __init__(self, base_model, image_size):
#         super(_DiffusionModel, self).__init__()
#         self.base_model = base_model
#         self.image_size = image_size
#         num_features = self.base_model.fc.in_features
#         self.base_model.fc = nn.Linear(num_features, image_size // 8 * image_size // 8 * 128)
#
#         self.deconv1 = nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1)
#         self.deconv2 = nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1)
#         self.deconv3 = nn.ConvTranspose2d(32, 3, kernel_size=4, stride=2, padding=1)
#
#         self.relu = nn.ReLU()
#
#     def forward(self, x):
#         x = self.base_model(x)
#         x = x.view(x.size(0), 128, self.image_size // 8, self.image_size // 8)
#         x = self.relu(self.deconv1(x))
#         x = self.relu(self.deconv2(x))
#         x = self.deconv3(x)
#         return x


class DiffusionModel:

    @staticmethod
    def diffusion(model, image_size, device):
        return _DiffusionModel(model, image_size).to(device)


class DiffusionTrainer(Trainer):

    def __init__(self, model: nn.Module, data_loader: MyDataLoader, criterion=None, optimizer=None, device=None,
                 auto_classifer=False, log_dir=None, is_model_graph=True, auto_save=False, writer=None,
                 verbose=0, evaluation_interval=10, mem_threshold=0.9, lr=0.005, scheduler=None, save_interval=10,
                 **kwargs):
        if criterion is None:
            criterion = nn.MSELoss()

        super(DiffusionTrainer, self).__init__(model, data_loader, criterion, optimizer, device, auto_classifer,
                                               log_dir, is_model_graph, auto_save, writer, verbose, evaluation_interval,
                                               mem_threshold, lr, scheduler, save_interval, **kwargs)

    def train(self, num_epochs):
        device = self.device
        for epoch in tqdm(range(num_epochs)):
            self.model.train()
            running_loss = 0.0
            for images, _ in tqdm(self.data_loader.train_loader, desc=f'Epoch {epoch + 1}/{num_epochs}',
                                  unit='batch'):
                images = images.to(device)
                noisy_images = images + torch.randn_like(images) * 0.1
                self.optimizer.zero_grad()
                outputs = self.model(noisy_images)
                loss = self.criterion(outputs, images)
                loss.backward()
                self.optimizer.step()
                running_loss += loss.item() * images.size(0)

            mem_allocated = torch.cuda.memory_allocated(device)
            mem_reserved = torch.cuda.memory_reserved(device)
            if mem_allocated / mem_reserved > self.mem_threshold:
                print("The memory allocation is close to the maximum, So Ending the train")
                return

            epoch_loss = running_loss / len(self.data_loader.train_loader)
            print(f'Epoch [{self.epoch + 1}/{num_epochs}], Loss: {epoch_loss:.4f}')
            self.writer.add_scalar('Loss/Training', epoch_loss, epoch)
            self.writer.add_scalar('Learning Rate', self.get_lr(), epoch)
            self.epoch = epoch
            self._auto_save(epoch)
            if epoch % self.evaluation_interval == 0 and epoch != 0:
                average_loss = self.evaluate()
                self.writer.add_scalar('Loss/Validation', average_loss, epoch)
                early_stop = self._early_stop(average_loss=average_loss, epoch=epoch)
                if early_stop == -1:
                    return

            if self.scheduler is not None:
                self.scheduler.step()
    # def train(self, num_epochs):
    #     super().train(num_epochs)

    def train_method(self, data, labels):
        images = data.to(self.device)
        # tqdm.write(f'images size {images.size(0)}')
        noisy_images = images + torch.randn_like(images) * 0.1
        outputs = self.model(noisy_images)
        loss = self.criterion(outputs, images)
        return loss

    def loss_value(self, loss):
        return loss.item() * self.data_loader.batch_size

    def evaluate(self, data_loader=None, phase='Validation'):
        if data_loader is None:
            data_loader = self.data_loader.val_loader
        self.model.eval()
        running_loss = 0.0
        with torch.no_grad():
            for images, _ in tqdm(data_loader, desc='Evaluating', unit='batch'):
                images = images.to(self.device)
                noisy_images = images + torch.randn_like(images) * 0.1
                outputs = self.model(noisy_images)
                loss = self.criterion(outputs, images)
                running_loss += loss.item() * images.size(0)

        average_loss = running_loss / len(data_loader)
        print(f'{phase} Loss: {average_loss:.4f}')
        return average_loss

    def test(self):
        return self.evaluate(self.data_loader.test_loader, phase='Test')

    def _predict(self, *args, **kwargs):
        self.model.eval()
        with torch.no_grad():
            res = self.model(*args, **kwargs)
        return res

    def predict(self, data, *args, **kwargs):
        return self._predict(data.to(self.device))
