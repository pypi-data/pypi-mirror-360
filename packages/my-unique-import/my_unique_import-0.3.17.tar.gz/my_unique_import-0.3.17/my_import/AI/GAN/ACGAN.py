import glob
import os

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
    def __init__(self, n_classes, latent_dim, img_size, channels):
        super(Generator, self).__init__()

        self.label_emb = nn.Embedding(n_classes, latent_dim)

        self.init_size = img_size // 4  # Initial size before upsampling
        self.l1 = nn.Sequential(nn.Linear(latent_dim, 128 * self.init_size ** 2))

        self.conv_blocks = nn.Sequential(
            nn.BatchNorm2d(128),
            nn.Upsample(scale_factor=2), # 1: init_size -> init_size * 2
            nn.Conv2d(128, 128, 3, stride=1, padding=1),
            nn.BatchNorm2d(128, 0.8),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Upsample(scale_factor=2), # 2: init_size * 2 -> init_size * 4
            nn.Conv2d(128, 64, 3, stride=1, padding=1),
            nn.BatchNorm2d(64, 0.8),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(64, channels, 3, stride=1, padding=1),
            nn.Tanh(),
        )

    def forward(self, noise, labels):
        gen_input = torch.mul(self.label_emb(labels), noise)
        out = self.l1(gen_input)
        out = out.view(out.shape[0], 128, self.init_size, self.init_size)
        img = self.conv_blocks(out)
        return img


class Discriminator(nn.Module):
    def __init__(self, n_classes, channels, img_size):
        super(Discriminator, self).__init__()
        self.img_size = img_size
        self.channels = channels

        def discriminator_block(in_filters, out_filters, bn=True):
            block = [nn.Conv2d(in_filters, out_filters, 3, 2, 1), nn.LeakyReLU(0.2, inplace=True), nn.Dropout2d(0.25)]
            if bn:
                block.append(nn.BatchNorm2d(out_filters, 0.8))
            return block

        self.conv_blocks = nn.Sequential(
            *discriminator_block(channels, 16, bn=False),
            *discriminator_block(16, 32),
            *discriminator_block(32, 64),
            *discriminator_block(64, 128),
        )

        # Dynamic calculation of flattened feature dimension
        dummy_input = torch.randn(1, channels, img_size, img_size)

        with torch.no_grad():
            output_feature_map = self.conv_blocks(dummy_input)  # Changed from self.model to self.conv_blocks
            self.flattened_feature_dim = output_feature_map.view(1, -1).size(1)

        # Output layers
        self.adv_layer = nn.Sequential(nn.Linear(self.flattened_feature_dim, 1), nn.Sigmoid())
        self.aux_layer = nn.Sequential(nn.Linear(self.flattened_feature_dim, n_classes),
                                       nn.Softmax(dim=1))  # Added dim=1 for Softmax

    def forward(self, img):
        out = self.conv_blocks(img)
        out = out.view(out.shape[0], -1)

        validity = self.adv_layer(out)
        label = self.aux_layer(out)

        return validity, label

def weights_init_normal(m):
    classname = m.__class__.__name__
    if classname.find("Conv") != -1:
        torch.nn.init.normal_(m.weight.data, 0.0, 0.02)
    elif classname.find("BatchNorm2d") != -1:
        torch.nn.init.normal_(m.weight.data, 1.0, 0.02)
        torch.nn.init.constant_(m.bias.data, 0.0)

class ACGANTrainer(baseGANTrainer):

    def __init__(self, data_loader: MyDataLoader, generator=None, discriminator=None, device=None,
                 log_dir=None, auto_save=False, writer=None, verbose=0, evaluation_interval=10,
                 mem_threshold=0.9, lr=0.0002, scheduler=None, save_interval=400,
                 b1 = 0.5, b2 =0.999,
                 **kwargs):

        super(ACGANTrainer, self).__init__(data_loader, generator, discriminator, device,
                                               log_dir, auto_save, writer, verbose, evaluation_interval,
                                               mem_threshold, lr, scheduler, save_interval, **kwargs)
        adversarial_loss = torch.nn.BCELoss()
        auxiliary_loss = torch.nn.CrossEntropyLoss()
        self.adversarial_loss = adversarial_loss
        self.auxiliary_loss = auxiliary_loss
        n_classes = len(self.data_loader.classes)
        self.n_classes = n_classes
        latent_dim = 100
        img_size = self.data_loader.size[2]
        channels = self.data_loader.size[0]
        generator = Generator(n_classes=n_classes, latent_dim=latent_dim, img_size=img_size, channels=channels)
        discriminator = Discriminator(n_classes=n_classes, channels=channels, img_size=img_size)
        generator.apply(weights_init_normal)
        discriminator.apply(weights_init_normal)
        self.generator = generator.to(self.device)
        self.discriminator = discriminator.to(self.device)
        self.b1, self.b2 = b1, b2
        self.latent_dim = latent_dim
        optimizer_G = torch.optim.Adam(self.generator.parameters(), lr=self.lr, betas=(self.b1, self.b2))
        optimizer_D = torch.optim.Adam(self.discriminator.parameters(), lr=self.lr, betas=(self.b1, self.b2))
        self.optimizer_G = optimizer_G
        self.optimizer_D = optimizer_D
        cuda = True if torch.cuda.is_available() else False
        self.FloatTensor = torch.cuda.FloatTensor if cuda else torch.FloatTensor
        self.LongTensor = torch.cuda.LongTensor if cuda else torch.LongTensor
        self.batch_size = self.data_loader.batch_size


    def train(self, num_epochs):
        if self.verbose == 2:
            self.show()
        device = self.device
        FloatTensor = self.FloatTensor
        LongTensor = self.LongTensor
        total_epochs = self.epoch + num_epochs
        outer_tqdm = tqdm(range(self.epoch, total_epochs), desc='Epochs', unit='epoch', position=0, leave=False)
        for epoch in outer_tqdm:
            running_loss = 0.0
            inner_tqdm = tqdm(self.data_loader.train_loader, desc=f'Epoch {epoch + 1}/{total_epochs}', unit='batch',
                              position=1, leave=False)
            for i, (data, labels) in enumerate(inner_tqdm):
                current_batch_size = data.size(0)
                valid = Variable(FloatTensor(current_batch_size, 1).fill_(1.0), requires_grad=False).to(device)
                fake = Variable(FloatTensor(current_batch_size, 1).fill_(0.0), requires_grad=False).to(device)
                real_imgs = Variable(data.type(FloatTensor)).to(device)
                labels = Variable(labels.type(LongTensor)).to(device)
                self.optimizer_G.zero_grad()

                # Sample noise and labels as generator input
                z = Variable(FloatTensor(np.random.normal(0, 1, (current_batch_size, self.latent_dim)))).to(device)
                gen_labels = Variable(LongTensor(np.random.randint(0, self.n_classes, current_batch_size))).to(device)

                # Generate a batch of images
                gen_imgs = self.generator(z, gen_labels)

                # Loss measures generator's ability to fool the discriminator
                validity, pred_label = self.discriminator(gen_imgs.to(device))
                g_loss = 0.5 * (self.adversarial_loss(validity, valid) + self.auxiliary_loss(pred_label, gen_labels))

                g_loss.backward()
                self.optimizer_G.step()

                # ---------------------
                #  Train Discriminator
                # ---------------------

                self.optimizer_D.zero_grad()

                # Loss for real images
                real_pred, real_aux = self.discriminator(real_imgs)
                d_real_loss = (self.adversarial_loss(real_pred, valid) + self.auxiliary_loss(real_aux, labels)) / 2

                # Loss for fake images
                fake_pred, fake_aux = self.discriminator(gen_imgs.detach())
                d_fake_loss = (self.adversarial_loss(fake_pred, fake) + self.auxiliary_loss(fake_aux, gen_labels)) / 2

                # Total discriminator loss
                d_loss = (d_real_loss + d_fake_loss) / 2

                # Calculate discriminator accuracy
                pred = np.concatenate([real_aux.data.cpu().numpy(), fake_aux.data.cpu().numpy()], axis=0)
                gt = np.concatenate([labels.data.cpu().numpy(), gen_labels.data.cpu().numpy()], axis=0)
                d_acc = np.mean(np.argmax(pred, axis=1) == gt)

                d_loss.backward()
                self.optimizer_D.step()
                inner_tqdm.set_postfix(D_loss=d_loss.item(), D_acc=f"{100 * d_acc:.2f}%", G_loss=g_loss.item())
                batches_done = epoch * len(self.data_loader.train_loader) + i
                if batches_done % self.save_interval == 0:
                    self.sample_image(n_row=10, batches_done=batches_done)

            # epoch_loss_combined = (running_g_loss + running_d_loss) / (2 * len(self.data_loader.train_loader))
            # outer_tqdm.set_postfix(D_loss=d_loss.item(), G_loss=g_loss.item(), D_acc=f"{100 * d_acc:.2f}%")  # 更新外部tqdm
            # self.writer.add_scalar('Loss/Training', epoch_loss, epoch)
            # self.writer.add_scalar('Learning Rate', self.get_lr(), epoch)
            # self._auto_save(epoch)
            # if self._evaluation(epoch) == -1:
            #     return

            self.scheduler_step()
        self.epoch += num_epochs

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
        z = Variable(self.FloatTensor(np.random.normal(0, 1, (n_row ** 2, self.latent_dim))))
        # Get labels ranging from 0 to n_classes for n rows
        labels = np.array([num for _ in range(n_row) for num in range(n_row)])
        labels = Variable(self.LongTensor(labels))
        gen_imgs = self.generator(z, labels)
        image_path = os.path.join(self.model_save_dir, 'generated_images')
        os.makedirs(image_path, exist_ok=True)
        save_image(gen_imgs.data, f"{image_path}/%d.png" % batches_done, nrow=n_row, normalize=True)