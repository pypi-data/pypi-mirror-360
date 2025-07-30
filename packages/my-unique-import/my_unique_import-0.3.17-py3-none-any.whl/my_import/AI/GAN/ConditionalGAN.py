import glob
import os
import itertools
import re
from collections import defaultdict

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.utils import save_image

from my_import.AI.AI import Trainer, MyDataLoader
from tqdm import tqdm
import numpy as np
from torch.autograd import Variable

from my_import.AI.GAN import baseGANTrainer


class Generator(nn.Module):
    def __init__(self, n_classes, img_size, latent_dim):
        super(Generator, self).__init__()

        self.label_emb = nn.Embedding(n_classes, n_classes)
        self.img_size = img_size

        def block(in_feat, out_feat, normalize=True):
            layers = [nn.Linear(in_feat, out_feat)]
            if normalize:
                layers.append(nn.BatchNorm1d(out_feat, 0.8))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return layers

        self.model = nn.Sequential(
            *block(latent_dim + n_classes, 128, normalize=False),
            *block(128, 256),
            *block(256, 512),
            *block(512, 1024),
            nn.Linear(1024, int(np.prod(img_size))),
            nn.Tanh()
        )

    def forward(self, noise, labels):
        # Concatenate label embedding and image to produce input
        gen_input = torch.cat((self.label_emb(labels), noise), -1)
        img = self.model(gen_input)
        img = img.view(img.size(0), *self.img_size)
        return img


class Discriminator(nn.Module):
    def __init__(self, n_classes, img_size):
        super(Discriminator, self).__init__()

        self.label_embedding = nn.Embedding(n_classes, n_classes)

        self.model = nn.Sequential(
            nn.Linear(n_classes + int(np.prod(img_size)), 512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, 512),
            nn.Dropout(0.4),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, 512),
            nn.Dropout(0.4),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, 1),
        )

    def forward(self, img, labels):
        # Concatenate label embedding and image to produce input
        d_in = torch.cat((img.view(img.size(0), -1), self.label_embedding(labels)), -1)
        validity = self.model(d_in)
        return validity


class CGANTrainer(baseGANTrainer):

    def __init__(self, data_loader: MyDataLoader, generator=None, discriminator=None, device=None,
                 log_dir=None, auto_save=False, writer=None, verbose=0, evaluation_interval=400,
                 mem_threshold=0.9, lr_G=0.0002, lr_D=0.00005, scheduler=None, patience=5, save_interval=10,
                 b1 = 0.5, b2 =0.999, model_save_dir=None,
                 **kwargs):

        super(CGANTrainer, self).__init__(data_loader, generator, discriminator, device,
                                               log_dir, auto_save, writer, verbose, evaluation_interval,
                                               mem_threshold, lr_G, lr_D, scheduler, patience, save_interval, model_save_dir, **kwargs)
        adversarial_loss = torch.nn.MSELoss()
        self.adversarial_loss = adversarial_loss
        n_classes = len(self.data_loader.classes)
        self.n_classes = n_classes
        latent_dim = 100
        img_size = self.data_loader.size[2]
        channels = self.data_loader.size[0]
        if generator is None:
            g = Generator
        else:
            g = generator

        if discriminator is None:
            d = Discriminator
        else:
            d = discriminator

        generator = g(n_classes=n_classes, img_size=(channels, img_size,img_size), latent_dim=latent_dim)
        discriminator = d(n_classes=n_classes, img_size=(channels, img_size,img_size))
        self.generator = generator.to(self.device)
        self.discriminator = discriminator.to(self.device)
        self.b1, self.b2 = b1, b2
        self.latent_dim = latent_dim
        optimizer_G = torch.optim.Adam(self.generator.parameters(), lr=self.lr_G, betas=(self.b1, self.b2))
        optimizer_D = torch.optim.Adam(self.discriminator.parameters(), lr=self.lr_D, betas=(self.b1, self.b2))
        self.optimizer_G = optimizer_G
        self.optimizer_D = optimizer_D
        cuda = True if torch.cuda.is_available() else False
        self.FloatTensor = torch.cuda.FloatTensor if cuda else torch.FloatTensor
        self.LongTensor = torch.cuda.LongTensor if cuda else torch.LongTensor
        self.batch_size = self.data_loader.batch_size
        self.losses = defaultdict(list)


    def train(self, num_epochs):
        if self.verbose == 2:
            self.show()
        # device = self.device
        FloatTensor = self.FloatTensor
        LongTensor = self.LongTensor
        total_epochs = self.epoch + num_epochs
        outer_tqdm = tqdm(range(self.epoch, total_epochs), desc='Epochs', unit='epoch', position=0, leave=False)
        for epoch in outer_tqdm:
            # self.model.train()
            running_g_loss = 0.0
            running_d_loss = 0.0
            inner_tqdm = tqdm(self.data_loader.train_loader, desc=f'Epoch {epoch + 1}/{total_epochs}', unit='batch',
                              position=1, leave=False)
            for i, (data, labels) in enumerate(inner_tqdm):
                batch_size = data.shape[0]

                # Adversarial ground truths
                valid = Variable(FloatTensor(batch_size, 1).fill_(1.0), requires_grad=False)
                fake = Variable(FloatTensor(batch_size, 1).fill_(0.0), requires_grad=False)

                # Configure input
                real_imgs = Variable(data.type(FloatTensor))
                labels = Variable(labels.type(LongTensor))

                # -----------------
                #  Train Generator
                # -----------------

                self.optimizer_G.zero_grad()

                # Sample noise and labels as generator input
                z = Variable(FloatTensor(np.random.normal(0, 1, (batch_size, self.latent_dim))))
                gen_labels = Variable(LongTensor(np.random.randint(0, self.n_classes, batch_size)))

                # Generate a batch of images
                gen_imgs = self.generator(z, gen_labels)

                # Loss measures generator's ability to fool the discriminator
                validity = self.discriminator(gen_imgs, gen_labels)
                g_loss = self.adversarial_loss(validity, valid)

                g_loss.backward()
                self.optimizer_G.step()

                # ---------------------
                #  Train Discriminator
                # ---------------------

                self.optimizer_D.zero_grad()

                # Loss for real images
                validity_real = self.discriminator(real_imgs, labels)
                d_real_loss = self.adversarial_loss(validity_real, valid)

                # Loss for fake images
                validity_fake = self.discriminator(gen_imgs.detach(), gen_labels)
                d_fake_loss = self.adversarial_loss(validity_fake, fake)

                # Total discriminator loss
                d_loss = (d_real_loss + d_fake_loss) / 2

                d_loss.backward()
                self.optimizer_D.step()

                inner_tqdm.set_postfix(D_loss=d_loss.item(), G_loss=g_loss.item())
                running_g_loss += g_loss
                running_d_loss += d_loss
                batches_done = epoch * len(self.data_loader.train_loader) + i
                if batches_done % self.evaluation_interval == 0:
                    self.sample_image(n_row=self.n_classes, batches_done=batches_done)

            # epoch_loss_combined = (running_g_loss + running_d_loss) / (2 * len(self.data_loader.train_loader))
            average_g_loss = running_g_loss / len(self.data_loader.train_loader)
            average_d_loss = running_d_loss / len(self.data_loader.train_loader)

            outer_tqdm.set_postfix(D_loss=average_d_loss.item(), G_loss=average_g_loss.item())  # 更新外部tqdm
            # self.writer.add_scalar('Loss/Training', epoch_loss, epoch)
            # self.writer.add_scalar('Learning Rate', self.get_lr(), epoch)
            self.losses['d_loss'].append((average_d_loss.item(), epoch))
            self.losses['g_loss'].append((average_g_loss.item(), epoch))
            self._auto_save(epoch)
            self._auto_plot_loss(epoch)
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
        loss_save_path = os.path.join(self.model_save_dir, 'loss_history.pth')
        torch.save(self.losses, loss_save_path)


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
                path_to_load_loss = os.path.join(self.model_save_dir, 'loss_history.pth')
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
            path_to_load_loss = os.path.join(self.model_save_dir, 'loss_history.pth')

        else:
            if 'generator' in path:
                path_to_load_gen = path
                path_to_load_disc = path.replace('generator', 'discriminator')
            elif 'discriminator' in path:
                path_to_load_disc = path
                path_to_load_gen = path.replace('discriminator', 'generator')
            elif 'loss_history' in path:
                path_to_load_loss = path
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
        self.losses = torch.load(path_to_load_loss, map_location=self.device)

        print(f'Generator and Discriminator loaded from epoch {epoch}')
        return epoch, loss

    def sample_image(self, n_row, batches_done):
        """Saves a grid of generated digits ranging from 0 to n_classes"""
        # Sample noise
        z = Variable(self.FloatTensor(np.random.normal(0, 1, (n_row ** 2, self.latent_dim))))
        # Get labels ranging from 0 to n_classes for n rows
        labels = np.array([num for _ in range(n_row) for num in range(self.n_classes)])
        labels = Variable(self.LongTensor(labels))
        # print("-------------Generating Images-------------")
        # print("labels:", labels)
        gen_imgs = self.generator(z, labels)
        image_path = os.path.join(self.model_save_dir, 'generated_images')
        os.makedirs(image_path, exist_ok=True)
        save_image(gen_imgs.data, f"{image_path}/%d.png" % batches_done, nrow=n_row, normalize=True)
        # print("-------------Finished Generating Images-------------")

    def to_categorical(self, y, num_columns):
        """Returns one-hot encoded Variable"""
        y_cat = np.zeros((y.shape[0], num_columns))
        y_cat[range(y.shape[0]), y] = 1.0

        return Variable(self.FloatTensor(y_cat))

    def generate_images(self, input_labels, prefix, dir_name=None, new_labels=None):
        if dir_name is None:
            dir_name = "regenerated_images"
        if new_labels is None:
            new_labels = input_labels
        image_path = os.path.join(self.model_save_dir, dir_name)
        os.makedirs(image_path, exist_ok=True)
        start_index = self.get_next_available_filename_index(image_path)
        size = len(input_labels)
        self.generator.eval()
        # Sample noise
        with torch.no_grad():
            for i in range(size):
                label = input_labels[i]
                name_label = new_labels[i]
                image_path_dir = os.path.join(image_path, str(name_label))
                os.makedirs(image_path_dir, exist_ok=True)
                z = Variable(self.FloatTensor(np.random.normal(0, 1, (1, self.latent_dim))))
                # Get labels ranging from 0 to n_classes for n rows
                labels = np.array([label])
                labels = Variable(self.LongTensor(labels))
                # print("-------------Generating Images-------------")
                # print("labels:", labels)
                gen_imgs = self.generator(z, labels)
                current_filename_index = start_index + i
                save_path = os.path.join(image_path_dir, f"{prefix}_{current_filename_index}.png")
                save_image(gen_imgs.data, save_path, nrow=1, normalize=True)
        self.generator.train()

    def get_next_available_filename_index(self, image_path_dir):
        max_i = -1
        if os.path.exists(image_path_dir):
            for filename in os.listdir(image_path_dir):
                if filename.endswith(".png"):
                    match = re.match(r"(\d+)\.png$", filename)
                    if match:
                        try:
                            current_i = int(match.group(1))
                            if current_i > max_i:
                                max_i = current_i
                        except ValueError:
                            pass
        return max_i + 1