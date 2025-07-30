import glob
import os
import numpy as np
from my_import.AI.AI import MyDataLoader
from torchvision.utils import save_image
from torch.autograd import Variable
from my_import.AI.GAN import baseGANTrainer
import torch.nn as nn
import torch
from tqdm import tqdm


class Generator(nn.Module):
    def __init__(self, latent_dim, img_shape):
        super(Generator, self).__init__()

        def block(in_feat, out_feat, normalize=True):
            layers = [nn.Linear(in_feat, out_feat)]
            if normalize:
                layers.append(nn.BatchNorm1d(out_feat, 0.8))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return layers

        self.model = nn.Sequential(
            *block(latent_dim, 128, normalize=False),
            *block(128, 256),
            *block(256, 512),
            *block(512, 1024),
            nn.Linear(1024, int(np.prod(img_shape))),
            nn.Tanh()
        )
        self.img_shape = img_shape

    def forward(self, z):
        img = self.model(z)
        img = img.view(img.size(0), *self.img_shape)
        return img


class Discriminator(nn.Module):
    def __init__(self, img_shape):
        super(Discriminator, self).__init__()

        self.model = nn.Sequential(
            nn.Linear(int(np.prod(img_shape)), 512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(256, 1),
            nn.Sigmoid(),
        )

    def forward(self, img):
        img_flat = img.view(img.size(0), -1)
        validity = self.model(img_flat)

        return validity


class GANTrainer(baseGANTrainer):

    def __init__(self, data_loader: MyDataLoader, generator=None, discriminator=None, device=None,
                 log_dir=None, auto_save=False, writer=None, verbose=0, evaluation_interval=10,
                 mem_threshold=0.9, lr=0.0002, scheduler=None, save_interval=400,
                 b1 = 0.5, b2 =0.999,
                 **kwargs):

        super(GANTrainer, self).__init__(data_loader, generator, discriminator, device,
                                               log_dir, auto_save, writer, verbose, evaluation_interval,
                                               mem_threshold, lr, scheduler, save_interval, **kwargs)
        adversarial_loss = torch.nn.BCELoss()
        self.adversarial_loss = adversarial_loss
        n_classes = len(self.data_loader.classes)
        self.n_classes = n_classes
        latent_dim = 100
        img_size = self.data_loader.size[2]
        channels = self.data_loader.size[0]
        generator = Generator(latent_dim=latent_dim, img_shape=(channels, img_size, img_size))
        discriminator = Discriminator(img_shape=(channels, img_size, img_size))
        self.generator = generator.to(self.device)
        self.discriminator = discriminator.to(self.device)
        self.b1, self.b2 = b1, b2
        self.latent_dim = latent_dim
        optimizer_G = torch.optim.Adam(self.generator.parameters(), lr=self.lr, betas=(self.b1, self.b2))
        optimizer_D = torch.optim.Adam(self.discriminator.parameters(), lr=self.lr, betas=(self.b1, self.b2))
        self.optimizer_G = optimizer_G
        self.optimizer_D = optimizer_D
        cuda = True if torch.cuda.is_available() else False
        self.Tensor = torch.cuda.FloatTensor if cuda else torch.FloatTensor
        self.batch_size = self.data_loader.batch_size


    def train(self, num_epochs):
        if self.verbose == 2:
            self.show()
        device = self.device
        Tensor = self.Tensor
        total_epochs = self.epoch + num_epochs
        outer_tqdm = tqdm(range(self.epoch, total_epochs), desc='Epochs', unit='epoch', position=0, leave=False)
        for epoch in outer_tqdm:
            running_g_loss = 0.0
            running_d_loss = 0.0
            inner_tqdm = tqdm(self.data_loader.train_loader, desc=f'Epoch {epoch + 1}/{total_epochs}', unit='batch',
                              position=1, leave=False)
            for i, (data, labels) in enumerate(inner_tqdm):
                valid = Variable(Tensor(data.size(0), 1).fill_(1.0), requires_grad=False).to(device)
                fake = Variable(Tensor(data.size(0), 1).fill_(0.0), requires_grad=False).to(device)
                real_imgs = Variable(data.type(Tensor)).to(device)
                self.optimizer_G.zero_grad()

                # Sample noise as generator input
                z = Variable(Tensor(np.random.normal(0, 1, (data.shape[0], self.latent_dim))))

                # Generate a batch of images
                gen_imgs = self.generator(z)

                # Loss measures generator's ability to fool the discriminator
                g_loss = self.adversarial_loss(self.discriminator(gen_imgs), valid)

                g_loss.backward()
                self.optimizer_G.step()

                # ---------------------
                #  Train Discriminator
                # ---------------------

                self.optimizer_D.zero_grad()

                # Measure discriminator's ability to classify real from generated samples
                real_loss = self.adversarial_loss(self.discriminator(real_imgs), valid)
                fake_loss = self.adversarial_loss(self.discriminator(gen_imgs.detach()), fake)
                d_loss = (real_loss + fake_loss) / 2

                d_loss.backward()
                self.optimizer_D.step()
                running_g_loss += g_loss
                running_d_loss += d_loss

                inner_tqdm.set_postfix(D_loss=d_loss.item(), G_loss=g_loss.item())
                batches_done = epoch * len(self.data_loader.train_loader) + i
                if batches_done % self.save_interval == 0:
                    self.sample_image(n_row=10, batches_done=batches_done)

            # epoch_loss_combined = (running_g_loss + running_d_loss) / (2 * len(self.data_loader.train_loader))
            outer_tqdm.set_postfix(D_loss=running_d_loss.item(), G_loss=running_g_loss.item())
            # self.writer.add_scalar('Loss/Training', epoch_loss, epoch)
            # self.writer.add_scalar('Learning Rate', self.get_lr(), epoch)
            # self._auto_save(epoch)
            # if self._evaluation(epoch) == -1:
            #     return

            self.scheduler_step()
        self.epoch += num_epochs


    def _predict(self, *args, **kwargs):
        self.model.eval()
        with torch.no_grad():
            res = self.model(*args, **kwargs)
        return res

    def predict(self, data, *args, **kwargs):
        return self._predict(data.to(self.device))

    def save_model(self, path=None, epoch=None):
        if epoch is None:
            epoch = self.epoch

        if path is None:
            gen_path = os.path.join(self.model_save_dir, f'generator_epoch_{epoch:02d}.pth')
            disc_path = os.path.join(self.model_save_dir, f'discriminator_epoch_{epoch:02d}.pth')
            best_gen_path = os.path.join(self.model_save_dir, 'best_generator.pth')
            best_disc_path = os.path.join(self.model_save_dir, 'best_discriminator.pth')
        else:
            gen_path = f"{path}_generator.pth"
            disc_path = f"{path}_discriminator.pth"
            best_gen_path = os.path.join(os.path.dirname(path), 'best_generator.pth')
            best_disc_path = os.path.join(os.path.dirname(path), 'best_discriminator.pth')
        os.makedirs(os.path.dirname(gen_path), exist_ok=True)

        torch.save({
            'epoch': epoch,
            'model_state_dict': self.generator.state_dict(),
            'optimizer_state_dict': self.optimizer_G.state_dict(),
        }, gen_path)
        print(f'Generator saved at epoch {epoch} to {gen_path}')
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.discriminator.state_dict(),
            'optimizer_state_dict': self.optimizer_D.state_dict(),
        }, disc_path)
        print(f'Discriminator saved at epoch {epoch} to {disc_path}')
        if path == os.path.join(self.model_save_dir, 'best_model.pth'):
            torch.save(self.generator.state_dict(), best_gen_path)
            torch.save(self.discriminator.state_dict(), best_disc_path)
            print(f'Best Generator and Discriminator saved to {best_gen_path} and {best_disc_path}')

    def load_model(self, path=None):
        if path is None:
            gen_files = glob.glob(os.path.join(self.model_save_dir, 'generator_epoch_*.pth'))
            disc_files = glob.glob(os.path.join(self.model_save_dir, 'discriminator_epoch_*.pth'))

            def extract_epoch(filename):
                try:
                    return int(os.path.basename(filename).split('_')[-1].split('.')[0])
                except (IndexError, ValueError):
                    return -1

            valid_gen_files = [f for f in gen_files if extract_epoch(f) != -1]
            valid_disc_files = [f for f in disc_files if extract_epoch(f) != -1]

            if not valid_gen_files or not valid_disc_files:
                best_gen_path = os.path.join(self.model_save_dir, 'best_generator.pth')
                best_disc_path = os.path.join(self.model_save_dir, 'best_discriminator.pth')
                if os.path.exists(best_gen_path) and os.path.exists(best_disc_path):
                    print(f"No epoch checkpoints found. Loading best models from {best_gen_path} and {best_disc_path}")
                    gen_checkpoint = torch.load(best_gen_path, map_location=self.device)
                    disc_checkpoint = torch.load(best_disc_path, map_location=self.device)
                    self.generator.load_state_dict(gen_checkpoint)
                    self.discriminator.load_state_dict(disc_checkpoint)
                    self.generator.to(self.device)
                    self.discriminator.to(self.device)
                    return 0, 0.0
                else:
                    raise FileNotFoundError("No valid generator or discriminator checkpoints found (nor best models).")
            max_gen_file = max(valid_gen_files, key=extract_epoch)
            max_disc_file = max(valid_disc_files, key=extract_epoch)

            gen_epoch = extract_epoch(max_gen_file)
            disc_epoch = extract_epoch(max_disc_file)
            if gen_epoch != disc_epoch:
                print(
                    f"WARNING: Latest generator epoch ({gen_epoch}) does not match latest discriminator epoch ({disc_epoch}). Loading generator from {max_gen_file} and discriminator from {max_disc_file}.")

            path_to_load_gen = max_gen_file
            path_to_load_disc = max_disc_file

        else:
            if 'generator' in path:
                path_to_load_gen = path
                path_to_load_disc = path.replace('generator', 'discriminator')
            elif 'discriminator' in path:
                path_to_load_disc = path
                path_to_load_gen = path.replace('discriminator', 'generator')
            else:
                path_to_load_gen = f"{path}_generator.pth"
                path_to_load_disc = f"{path}_discriminator.pth"
        print(f'Loading Generator from {path_to_load_gen}')
        print(f'Loading Discriminator from {path_to_load_disc}')

        if not os.path.exists(path_to_load_gen) or not os.path.exists(path_to_load_disc):
            raise FileNotFoundError(f"Missing one or both checkpoint files: {path_to_load_gen}, {path_to_load_disc}")

        gen_checkpoint = torch.load(path_to_load_gen, map_location=self.device)
        disc_checkpoint = torch.load(path_to_load_disc, map_location=self.device)

        self.generator.load_state_dict(gen_checkpoint['model_state_dict'])
        self.optimizer_G.load_state_dict(gen_checkpoint['optimizer_state_dict'])

        self.discriminator.load_state_dict(disc_checkpoint['model_state_dict'])
        self.optimizer_D.load_state_dict(disc_checkpoint['optimizer_state_dict'])

        epoch = gen_checkpoint.get('epoch', 0)
        loss = gen_checkpoint.get('loss', 0.0)

        self.generator.to(self.device)
        self.discriminator.to(self.device)

        print(f'Generator and Discriminator loaded from epoch {epoch}')
        return epoch, loss


    def sample_image(self, n_row, batches_done):
        """Saves a grid of generated digits ranging from 0 to n_classes"""
        # Sample noise
        z = Variable(self.Tensor(np.random.normal(0, 1, (n_row ** 2, self.latent_dim))))
        # Get labels ranging from 0 to n_classes for n rows
        gen_imgs = self.generator(z)
        image_path = os.path.join(self.model_save_dir, 'generated_images')
        os.makedirs(image_path, exist_ok=True)
        save_image(gen_imgs.data, f"{image_path}/%d.png" % batches_done, nrow=n_row, normalize=True)

