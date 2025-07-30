import glob
import os
import itertools
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
    def __init__(self, n_classes, channels, img_size, latent_dim, code_dim):
        super(Generator, self).__init__()
        input_dim = latent_dim + n_classes + code_dim

        self.init_size = img_size // 4  # Initial size before upsampling
        self.l1 = nn.Sequential(nn.Linear(input_dim, 128 * self.init_size ** 2))

        self.conv_blocks = nn.Sequential(
            nn.BatchNorm2d(128),
            nn.Upsample(scale_factor=2),
            nn.Conv2d(128, 128, 3, stride=1, padding=1),
            nn.BatchNorm2d(128, 0.8),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Upsample(scale_factor=2),
            nn.Conv2d(128, 64, 3, stride=1, padding=1),
            nn.BatchNorm2d(64, 0.8),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(64, channels, 3, stride=1, padding=1),
            nn.Tanh(),
        )

    def forward(self, noise, labels, code):
        gen_input = torch.cat((noise, labels, code), -1)
        out = self.l1(gen_input)
        out = out.view(out.shape[0], 128, self.init_size, self.init_size)
        img = self.conv_blocks(out)
        return img


class Discriminator(nn.Module):
    def __init__(self, n_classes, channels, img_size, code_dim):
        super(Discriminator, self).__init__()

        def discriminator_block(in_filters, out_filters, bn=True):
            """Returns layers of each discriminator block"""
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

        # The height and width of downsampled image
        ds_size = img_size // 2 ** 4

        # Output layers
        self.adv_layer = nn.Sequential(nn.Linear(128 * ds_size ** 2, 1))
        self.aux_layer = nn.Sequential(nn.Linear(128 * ds_size ** 2, n_classes), nn.Softmax())
        self.latent_layer = nn.Sequential(nn.Linear(128 * ds_size ** 2, code_dim))

    def forward(self, img):
        out = self.conv_blocks(img)
        out = out.view(out.shape[0], -1)
        validity = self.adv_layer(out)
        label = self.aux_layer(out)
        latent_code = self.latent_layer(out)

        return validity, label, latent_code

def weights_init_normal(m):
    classname = m.__class__.__name__
    if classname.find("Conv") != -1:
        torch.nn.init.normal_(m.weight.data, 0.0, 0.02)
    elif classname.find("BatchNorm") != -1:
        torch.nn.init.normal_(m.weight.data, 1.0, 0.02)
        torch.nn.init.constant_(m.bias.data, 0.0)

class InfoGANTrainer(baseGANTrainer):

    def __init__(self, data_loader: MyDataLoader, generator=None, discriminator=None, device=None,
                 log_dir=None, auto_save=False, writer=None, verbose=0, evaluation_interval=10,
                 mem_threshold=0.9, lr=0.0002, scheduler=None, save_interval=400,
                 b1 = 0.5, b2 =0.999,
                 **kwargs):

        super(InfoGANTrainer, self).__init__(data_loader, generator, discriminator, device,
                                               log_dir, auto_save, writer, verbose, evaluation_interval,
                                               mem_threshold, lr, scheduler, save_interval, **kwargs)
        adversarial_loss = torch.nn.MSELoss()
        categorical_loss = torch.nn.CrossEntropyLoss()
        continuous_loss = torch.nn.MSELoss()
        self.adversarial_loss = adversarial_loss
        self.categorical_loss = categorical_loss
        self.continuous_loss = continuous_loss
        n_classes = len(self.data_loader.classes)
        self.n_classes = n_classes
        latent_dim = 100
        img_size = self.data_loader.size[2]
        channels = self.data_loader.size[0]
        code_dim = 2
        self.code_dim = code_dim

        generator = Generator(n_classes=n_classes, channels=channels, img_size=img_size, latent_dim=latent_dim, code_dim=code_dim)
        discriminator = Discriminator(n_classes=n_classes, channels=channels, img_size=img_size, code_dim=code_dim)
        generator.apply(weights_init_normal)
        discriminator.apply(weights_init_normal)
        self.generator = generator.to(self.device)
        self.discriminator = discriminator.to(self.device)
        self.b1, self.b2 = b1, b2
        self.latent_dim = latent_dim
        optimizer_G = torch.optim.Adam(self.generator.parameters(), lr=self.lr, betas=(self.b1, self.b2))
        optimizer_D = torch.optim.Adam(self.discriminator.parameters(), lr=self.lr, betas=(self.b1, self.b2))
        optimizer_info = torch.optim.Adam(
            itertools.chain(generator.parameters(), discriminator.parameters()), lr=self.lr, betas=(self.b1, self.b2)
        )
        self.optimizer_G = optimizer_G
        self.optimizer_D = optimizer_D
        self.optimizer_info = optimizer_info
        cuda = True if torch.cuda.is_available() else False
        self.FloatTensor = torch.cuda.FloatTensor if cuda else torch.FloatTensor
        self.LongTensor = torch.cuda.LongTensor if cuda else torch.LongTensor
        self.batch_size = self.data_loader.batch_size
        self.lambda_cat = 1
        self.lambda_con = 0.1


    def train(self, num_epochs):
        if self.verbose == 2:
            self.show()
        device = self.device
        FloatTensor = self.FloatTensor
        LongTensor = self.LongTensor
        total_epochs = self.epoch + num_epochs
        outer_tqdm = tqdm(range(self.epoch, total_epochs), desc='Epochs', unit='epoch', position=0, leave=False)
        for epoch in outer_tqdm:
            running_g_loss = 0.0
            running_d_loss = 0.0
            running_info_loss = 0.0
            inner_tqdm = tqdm(self.data_loader.train_loader, desc=f'Epoch {epoch + 1}/{total_epochs}', unit='batch',
                              position=1, leave=False)
            for i, (data, labels) in enumerate(inner_tqdm):
                batch_size = data.shape[0]

                # Adversarial ground truths
                valid = Variable(FloatTensor(batch_size, 1).fill_(1.0), requires_grad=False)
                fake = Variable(FloatTensor(batch_size, 1).fill_(0.0), requires_grad=False)

                # Configure input
                real_imgs = Variable(data.type(FloatTensor))
                labels = self.to_categorical(labels.numpy(), num_columns=self.n_classes)

                # -----------------
                #  Train Generator
                # -----------------

                self.optimizer_G.zero_grad()

                # Sample noise and labels as generator input
                z = Variable(FloatTensor(np.random.normal(0, 1, (batch_size, self.latent_dim))))
                label_input = self.to_categorical(np.random.randint(0, self.n_classes, batch_size), num_columns=self.n_classes)
                code_input = Variable(FloatTensor(np.random.uniform(-1, 1, (batch_size, self.code_dim))))

                # Generate a batch of images
                gen_imgs = self.generator(z, label_input, code_input)

                # Loss measures generator's ability to fool the discriminator
                validity, _, _ = self.discriminator(gen_imgs)
                g_loss = self.adversarial_loss(validity, valid)

                g_loss.backward()
                self.optimizer_G.step()

                # ---------------------
                #  Train Discriminator
                # ---------------------

                self.optimizer_D.zero_grad()

                # Loss for real images
                real_pred, _, _ = self.discriminator(real_imgs)
                d_real_loss = self.adversarial_loss(real_pred, valid)

                # Loss for fake images
                fake_pred, _, _ = self.discriminator(gen_imgs.detach())
                d_fake_loss = self.adversarial_loss(fake_pred, fake)

                # Total discriminator loss
                d_loss = (d_real_loss + d_fake_loss) / 2

                d_loss.backward()
                self.optimizer_D.step()

                # ------------------
                # Information Loss
                # ------------------

                self.optimizer_info.zero_grad()

                # Sample labels
                sampled_labels = np.random.randint(0, self.n_classes, batch_size)

                # Ground truth labels
                gt_labels = Variable(LongTensor(sampled_labels), requires_grad=False)

                # Sample noise, labels and code as generator input
                z = Variable(FloatTensor(np.random.normal(0, 1, (batch_size, self.latent_dim))))
                label_input = self.to_categorical(sampled_labels, num_columns=self.n_classes)
                code_input = Variable(FloatTensor(np.random.uniform(-1, 1, (batch_size, self.code_dim))))

                gen_imgs = self.generator(z, label_input, code_input)
                _, pred_label, pred_code = self.discriminator(gen_imgs)

                info_loss = self.lambda_cat * self.categorical_loss(pred_label, gt_labels) + self.lambda_con * self.continuous_loss(
                    pred_code, code_input
                )

                info_loss.backward()
                self.optimizer_info.step()


                inner_tqdm.set_postfix(D_loss=d_loss.item(), G_loss=g_loss.item(), info_loss=info_loss.item())
                running_g_loss += g_loss
                running_d_loss += d_loss
                running_info_loss += info_loss
                batches_done = epoch * len(self.data_loader.train_loader) + i
                if batches_done % self.save_interval == 0:
                    self.sample_image(n_row=10, batches_done=batches_done)

            # epoch_loss_combined = (running_g_loss + running_d_loss) / (2 * len(self.data_loader.train_loader))
            average_g_loss = running_g_loss / len(self.data_loader.train_loader)
            average_d_loss = running_d_loss / len(self.data_loader.train_loader)
            average_info_loss = running_info_loss / len(self.data_loader.train_loader)
            outer_tqdm.set_postfix(D_loss=average_d_loss.item(), G_loss=average_g_loss.item(), info_loss=average_info_loss.item())  # 更新外部tqdm
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
        # Static sample
        static_z = Variable(self.FloatTensor(np.zeros((self.n_classes ** 2, self.latent_dim))))
        static_label = self.to_categorical(
            np.array([num for _ in range(self.n_classes) for num in range(self.n_classes)]), num_columns=self.n_classes
        )
        static_code = Variable(self.FloatTensor(np.zeros((self.n_classes ** 2, self.code_dim))))
        z = Variable(self.FloatTensor(np.random.normal(0, 1, (n_row ** 2, self.latent_dim))))
        static_sample = self.generator(z, static_label, static_code)
        image_path = os.path.join(self.model_save_dir, 'generated_images')
        os.makedirs(image_path, exist_ok=True)
        os.makedirs(os.path.join(image_path, 'static'), exist_ok=True)
        os.makedirs(os.path.join(image_path, 'varying_c1'), exist_ok=True)
        os.makedirs(os.path.join(image_path, 'varying_c2'), exist_ok=True)

        save_image(static_sample.data, f"{image_path}/static/%d.png" % batches_done, nrow=n_row, normalize=True)

        # Get varied c1 and c2
        zeros = np.zeros((n_row ** 2, 1))
        c_varied = np.repeat(np.linspace(-1, 1, n_row)[:, np.newaxis], n_row, 0)
        c1 = Variable(self.FloatTensor(np.concatenate((c_varied, zeros), -1)))
        c2 = Variable(self.FloatTensor(np.concatenate((zeros, c_varied), -1)))
        sample1 = self.generator(static_z, static_label, c1)
        sample2 = self.generator(static_z, static_label, c2)
        save_image(sample1.data, f"{image_path}/varying_c1/%d.png" % batches_done, nrow=n_row, normalize=True)
        save_image(sample2.data, f"{image_path}/varying_c2/%d.png" % batches_done, nrow=n_row, normalize=True)

    def to_categorical(self, y, num_columns):
        """Returns one-hot encoded Variable"""
        y_cat = np.zeros((y.shape[0], num_columns))
        y_cat[range(y.shape[0]), y] = 1.0

        return Variable(self.FloatTensor(y_cat))