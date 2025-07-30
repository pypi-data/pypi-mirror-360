import glob
import os
from my_import.AI.AI import Trainer, MyDataLoader # 假设 Trainer 和 MyDataLoader 路径正确
from torchvision.utils import save_image
from .baseVAE import BaseVAE
import torch.nn as nn
import torch.nn.functional as F
import torch
from tqdm import tqdm



class BetaVAE(BaseVAE):

    num_iter = 0 # Global static variable to keep track of iterations

    def __init__(self,
                 in_channels: int,
                 latent_dim = 100,
                 hidden_dims = None,
                 beta: int = 4,
                 gamma:float = 1000.,
                 max_capacity: int = 25,
                 Capacity_max_iter: int = 1e5,
                 loss_type:str = 'B',
                 **kwargs) -> None:
        super(BetaVAE, self).__init__()

        self.latent_dim = latent_dim
        self.beta = beta
        self.gamma = gamma
        self.loss_type = loss_type
        self.C_max = torch.Tensor([max_capacity])
        self.C_stop_iter = Capacity_max_iter

        modules = []
        if hidden_dims is None:
            hidden_dims = [32, 64, 128, 256, 512]

        # Build Encoder
        for h_dim in hidden_dims:
            modules.append(
                nn.Sequential(
                    nn.Conv2d(in_channels, out_channels=h_dim,
                              kernel_size= 3, stride= 2, padding  = 1),
                    nn.BatchNorm2d(h_dim),
                    nn.LeakyReLU())
            )
            in_channels = h_dim

        self.encoder = nn.Sequential(*modules)
        self.fc_mu = nn.Linear(hidden_dims[-1]*4, latent_dim)
        self.fc_var = nn.Linear(hidden_dims[-1]*4, latent_dim)
        # self.fc_mu = nn.Linear(hidden_dims[-1], latent_dim)
        # self.fc_var = nn.Linear(hidden_dims[-1], latent_dim)


        # Build Decoder
        modules = []

        self.decoder_input = nn.Linear(latent_dim, hidden_dims[-1] * 4)

        hidden_dims.reverse()

        for i in range(len(hidden_dims) - 1):
            modules.append(
                nn.Sequential(
                    nn.ConvTranspose2d(hidden_dims[i],
                                       hidden_dims[i + 1],
                                       kernel_size=3,
                                       stride = 2,
                                       padding=1,
                                       output_padding=1),
                    nn.BatchNorm2d(hidden_dims[i + 1]),
                    nn.LeakyReLU())
            )



        self.decoder = nn.Sequential(*modules)

        self.final_layer = nn.Sequential(
                            nn.ConvTranspose2d(hidden_dims[-1],
                                               hidden_dims[-1],
                                               kernel_size=3,
                                               stride=2,
                                               padding=1,
                                               output_padding=1),
                            nn.BatchNorm2d(hidden_dims[-1]),
                            nn.LeakyReLU(),
                            nn.Conv2d(hidden_dims[-1], out_channels= 3,
                                      kernel_size= 3, padding= 1),
                            nn.Tanh())

    def encode(self, input):
        """
        Encodes the input by passing through the encoder network
        and returns the latent codes.
        :param input: (Tensor) Input tensor to encoder [N x C x H x W]
        :return: (Tensor) List of latent codes
        """
        result = self.encoder(input)
        result = torch.flatten(result, start_dim=1)

        # Split the result into mu and var components
        # of the latent Gaussian distribution
        mu = self.fc_mu(result)
        log_var = self.fc_var(result)

        return [mu, log_var]

    def decode(self, z):
        result = self.decoder_input(z)
        result = result.view(-1, 512, 2, 2)
        result = self.decoder(result)
        result = self.final_layer(result)
        return result

    def reparameterize(self, mu, logvar):
        """
        Will a single z be enough ti compute the expectation
        for the loss??
        :param mu: (Tensor) Mean of the latent Gaussian
        :param logvar: (Tensor) Standard deviation of the latent Gaussian
        :return:
        """
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return eps * std + mu

    def forward(self, input, **kwargs):
        mu, log_var = self.encode(input)
        z = self.reparameterize(mu, log_var)
        return  [self.decode(z), input, mu, log_var]

    def loss_function(self,
                      *args,
                      **kwargs) -> dict:
        self.num_iter += 1
        recons = args[0]
        input = args[1]
        mu = args[2]
        log_var = args[3]
        kld_weight = kwargs['M_N']  # Account for the minibatch samples from the dataset

        recons_loss =F.mse_loss(recons, input)

        kld_loss = torch.mean(-0.5 * torch.sum(1 + log_var - mu ** 2 - log_var.exp(), dim = 1), dim = 0)

        if self.loss_type == 'H': # https://openreview.net/forum?id=Sy2fzU9gl
            loss = recons_loss + self.beta * kld_weight * kld_loss
        elif self.loss_type == 'B': # https://arxiv.org/pdf/1804.03599.pdf
            self.C_max = self.C_max.to(input.device)
            C = torch.clamp(self.C_max/self.C_stop_iter * self.num_iter, 0, self.C_max.data[0])
            loss = recons_loss + self.gamma * kld_weight* (kld_loss - C).abs()
        else:
            raise ValueError('Undefined loss type.')

        return {'loss': loss, 'Reconstruction_Loss':recons_loss, 'KLD':kld_loss}

    def sample(self,
               num_samples:int,
               current_device: int, **kwargs):
        """
        Samples from the latent space and return the corresponding
        image space map.
        :param num_samples: (Int) Number of samples
        :param current_device: (Int) Device to run the model
        :return: (Tensor)
        """
        z = torch.randn(num_samples,
                        self.latent_dim)

        z = z.to(current_device)

        samples = self.decode(z)
        return samples

    def generate(self, x, **kwargs):
        """
        Given an input image x, returns the reconstructed image
        :param x: (Tensor) [B x C x H x W]
        :return: (Tensor) [B x C x H x W]
        """

        return self.forward(x)[0]


class VAETrainer(Trainer):
    def __init__(self, vae_model: nn.Module, data_loader: MyDataLoader, criterion=None, optimizer=None, device=None,
                 log_dir=None, is_model_graph=True, auto_save=False, writer=None,
                 verbose=0, evaluation_interval=10, mem_threshold=0.9, lr=0.0002, scheduler=None, save_interval=400,
                 **kwargs):

        super(VAETrainer, self).__init__(vae_model, data_loader, criterion, optimizer, device,
                                               False, log_dir, is_model_graph, auto_save, writer, verbose, evaluation_interval,
                                               mem_threshold, lr, scheduler, save_interval, **kwargs)

        self.model = vae_model.to(self.device)

        if optimizer is None:
            self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        else:
            self.optimizer = optimizer

        self.batch_size = self.data_loader.batch_size

    def train(self, num_epochs):
        if self.verbose == 2:
            self.show()
        device = self.device
        total_epochs = self.epoch + num_epochs

        outer_tqdm = tqdm(range(self.epoch, total_epochs), desc='Epochs', unit='epoch', position=0, leave=False)
        for epoch in outer_tqdm:
            self.model.train()
            running_loss = 0.0
            running_reconstruction_loss = 0.0
            running_kld_loss = 0.0

            inner_tqdm = tqdm(self.data_loader.train_loader, desc=f'Epoch {epoch + 1}/{total_epochs}', unit='batch',
                              position=1, leave=False)
            for i, (data, labels) in enumerate(inner_tqdm):
                real_imgs = data.to(device)

                self.optimizer.zero_grad()

                recons, input_img, mu, log_var = self.model(real_imgs)

                dataset_size = len(self.data_loader.train_loader.dataset)
                kld_weight = self.batch_size / dataset_size

                loss_dict = self.model.loss_function(recons, input_img, mu, log_var, M_N = kld_weight)
                total_loss = loss_dict['loss']

                total_loss.backward()
                self.optimizer.step()

                running_loss += total_loss.item()
                recons_loss = loss_dict['Reconstruction_Loss']
                kld_loss = loss_dict['KLD']

                inner_tqdm.set_postfix(Loss=total_loss.item(),
                                        Recon_Loss=recons_loss.item(),
                                        KLD_Loss=kld_loss.item())
                running_reconstruction_loss += recons_loss.item()
                running_kld_loss += kld_loss.item()

                batches_done = epoch * len(self.data_loader.train_loader) + i
                if batches_done % self.save_interval == 0:
                    self.sample_vae_images(n_row=10, batches_done=batches_done)

            avg_epoch_loss = running_loss / len(self.data_loader.train_loader)
            avg_reconstruction_loss = running_reconstruction_loss / len(self.data_loader.train_loader)
            avg_kld_loss = running_kld_loss / len(self.data_loader.train_loader)
            outer_tqdm.set_postfix(Epoch_Loss=avg_epoch_loss, avg_recon_loss = avg_reconstruction_loss, avg_kld_loss=avg_kld_loss)

            self.scheduler_step()

        self.epoch += num_epochs
            # self._auto_save(self.epoch)

    def sample_vae_images(self, n_row, batches_done):
        samples = self.model.sample(num_samples=n_row**2, current_device=self.device)

        image_path = os.path.join(self.model_save_dir, 'vae_generated_images')
        os.makedirs(image_path, exist_ok=True)
        save_image(samples.data, f"{image_path}/%d.png" % batches_done, nrow=n_row, normalize=True)

    def save_model(self, path=None, epoch=None):
        if epoch is None:
            epoch = self.epoch
        if path is None:
            vae_path = os.path.join(self.model_save_dir, f'vae_epoch_{epoch:02d}.pth')
            best_vae_path = os.path.join(self.model_save_dir, 'best_vae.pth')
        else:
            vae_path = f"{path}_vae.pth"
            best_vae_path = os.path.join(os.path.dirname(path), 'best_vae.pth')
        os.makedirs(os.path.dirname(vae_path), exist_ok=True)

        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, vae_path)
        print(f'VAE model saved at epoch {epoch} to {vae_path}')

    def load_model(self, path=None):
        if path is None:
            vae_files = glob.glob(os.path.join(self.model_save_dir, 'vae_epoch_*.pth'))

            def extract_epoch(filename):
                try:
                    return int(os.path.basename(filename).split('_')[-1].split('.')[0])
                except (IndexError, ValueError):
                    return -1

            valid_vae_files = [f for f in vae_files if extract_epoch(f) != -1]

            if not valid_vae_files:
                best_vae_path = os.path.join(self.model_save_dir, 'best_vae.pth')
                if os.path.exists(best_vae_path):
                    print(f"No epoch checkpoints found. Loading best VAE model from {best_vae_path}")
                    checkpoint = torch.load(best_vae_path, map_location=self.device)
                    self.model.load_state_dict(checkpoint)
                    self.model.to(self.device)
                    return 0, 0.0
                else:
                    raise FileNotFoundError("No valid VAE checkpoints found (nor best VAE model).")

            path_to_load_vae = max(valid_vae_files, key=extract_epoch)
            epoch_to_load = extract_epoch(path_to_load_vae)
            print(f'Loading VAE model from epoch {epoch_to_load} from {path_to_load_vae}')

        else:
            path_to_load_vae = path
            if not os.path.exists(path_to_load_vae):
                raise FileNotFoundError(f"Specified VAE checkpoint file not found: {path_to_load_vae}")
            print(f'Loading VAE model from {path_to_load_vae}')

        checkpoint = torch.load(path_to_load_vae, map_location=self.device)

        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

        epoch = checkpoint.get('epoch', 0)
        loss = checkpoint.get('loss', 0.0)

        self.model.to(self.device)

        print(f'VAE model loaded from epoch {epoch}')
        self.epoch = epoch
        return epoch, loss