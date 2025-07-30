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
from torch.autograd import grad as torch_grad
import torch.nn.functional as F
from itertools import chain as ichain


class Reshape(nn.Module):
    """
    Class for performing a reshape as a layer in a sequential model.
    """

    def __init__(self, shape=[]):
        super(Reshape, self).__init__()
        self.shape = shape

    def forward(self, x):
        return x.view(x.size(0), *self.shape)

    def extra_repr(self):
        # (Optional)Set the extra information about this module. You can test
        # it by printing an object of this class.
        return 'shape={}'.format(
            self.shape
        )


class Generator_CNN(nn.Module):
    """
    CNN to model the generator of a ClusterGAN
    Input is a vector from representation space of dimension z_dim
    output is a vector from image space of dimension X_dim
    """

    # Architecture : FC1024_BR-FC7x7x128_BR-(64)4dc2s_BR-(1)4dc2s_S
    def __init__(self, latent_dim, n_c, x_shape, verbose=False):
        super(Generator_CNN, self).__init__()

        self.name = 'generator'
        self.latent_dim = latent_dim
        self.n_c = n_c
        self.x_shape = x_shape
        self.ishape = (128, 7, 7)
        self.iels = int(np.prod(self.ishape))
        self.verbose = verbose

        self.model = nn.Sequential(
            # Fully connected layers
            torch.nn.Linear(self.latent_dim + self.n_c, 1024),
            nn.BatchNorm1d(1024),
            # torch.nn.ReLU(True),
            nn.LeakyReLU(0.2, inplace=True),
            torch.nn.Linear(1024, self.iels),
            nn.BatchNorm1d(self.iels),
            # torch.nn.ReLU(True),
            nn.LeakyReLU(0.2, inplace=True),

            # Reshape to 128 x (7x7)
            Reshape(self.ishape),

            # Upconvolution layers
            nn.ConvTranspose2d(128, 64, 4, stride=2, padding=1, bias=True),
            nn.BatchNorm2d(64),
            # torch.nn.ReLU(True),
            nn.LeakyReLU(0.2, inplace=True),

            nn.ConvTranspose2d(64, self.x_shape[0], 4, stride=2, padding=1, bias=True),
            nn.Sigmoid()
        )

        initialize_weights(self)

        if self.verbose:
            print("Setting up {}...\n".format(self.name))
            print(self.model)

    def forward(self, zn, zc):
        z = torch.cat((zn, zc), 1)
        # z = z.unsqueeze(2).unsqueeze(3)
        x_gen = self.model(z)
        # Reshape for output
        x_gen = x_gen.view(x_gen.size(0), *self.x_shape)
        return x_gen


def initialize_weights(net):
    for m in net.modules():
        if isinstance(m, nn.Conv2d):
            m.weight.data.normal_(0, 0.02)
            m.bias.data.zero_()
        elif isinstance(m, nn.ConvTranspose2d):
            m.weight.data.normal_(0, 0.02)
            m.bias.data.zero_()
        elif isinstance(m, nn.Linear):
            m.weight.data.normal_(0, 0.02)
            m.bias.data.zero_()


def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        m.weight.data.normal_(0.0, 0.02)
    elif classname.find('BatchNorm') != -1:
        m.weight.data.normal_(1.0, 0.02)
        m.bias.data.fill_(0)


# Sample a random latent space vector
def sample_z(shape=64, latent_dim=10, n_c=10, fix_class=-1, req_grad=False):
    assert (fix_class == -1 or (fix_class >= 0 and fix_class < n_c)), "Requested class %i outside bounds." % fix_class

    Tensor = torch.cuda.FloatTensor

    # Sample noise as generator input, zn
    zn = Variable(Tensor(0.75 * np.random.normal(0, 1, (shape, latent_dim))), requires_grad=req_grad)

    ######### zc, zc_idx variables with grads, and zc to one-hot vector
    # Pure one-hot vector generation
    zc_FT = Tensor(shape, n_c).fill_(0)
    zc_idx = torch.empty(shape, dtype=torch.long)

    if (fix_class == -1):
        zc_idx = zc_idx.random_(n_c).cuda()
        zc_FT = zc_FT.scatter_(1, zc_idx.unsqueeze(1), 1.)
        # zc_idx = torch.empty(shape, dtype=torch.long).random_(n_c).cuda()
        # zc_FT = Tensor(shape, n_c).fill_(0).scatter_(1, zc_idx.unsqueeze(1), 1.)
    else:
        zc_idx[:] = fix_class
        zc_FT[:, fix_class] = 1

        zc_idx = zc_idx.cuda()
        zc_FT = zc_FT.cuda()

    zc = Variable(zc_FT, requires_grad=req_grad)

    ## Gaussian-noisey vector generation
    # zc = Variable(Tensor(np.random.normal(0, 1, (shape, n_c))), requires_grad=req_grad)
    # zc = softmax(zc)
    # zc_idx = torch.argmax(zc, dim=1)

    # Return components of latent space variable
    return zn, zc, zc_idx


def calc_gradient_penalty(netD, real_data, generated_data):
    # GP strength
    LAMBDA = 10

    b_size = real_data.size()[0]

    # Calculate interpolation
    alpha = torch.rand(b_size, 1, 1, 1)
    alpha = alpha.expand_as(real_data)
    alpha = alpha.cuda()

    interpolated = alpha * real_data.data + (1 - alpha) * generated_data.data
    interpolated = Variable(interpolated, requires_grad=True)
    interpolated = interpolated.cuda()

    # Calculate probability of interpolated examples
    prob_interpolated = netD(interpolated)

    # Calculate gradients of probabilities with respect to examples
    gradients = torch_grad(outputs=prob_interpolated, inputs=interpolated,
                           grad_outputs=torch.ones(prob_interpolated.size()).cuda(),
                           create_graph=True, retain_graph=True)[0]

    # Gradients have shape (batch_size, num_channels, img_width, img_height),
    # so flatten to easily take norm per example in batch
    gradients = gradients.view(b_size, -1)

    # Derivatives of the gradient close to 0 can cause problems because of
    # the square root, so manually calculate norm and add epsilon
    gradients_norm = torch.sqrt(torch.sum(gradients ** 2, dim=1) + 1e-12)

    # Return gradient penalty
    return LAMBDA * ((gradients_norm - 1) ** 2).mean()


class Encoder_CNN(nn.Module):
    """
    CNN to model the encoder of a ClusterGAN
    Input is vector X from image space if dimension X_dim
    Output is vector z from representation space of dimension z_dim
    """

    def __init__(self, latent_dim, n_c, verbose=False, channels=3):
        super(Encoder_CNN, self).__init__()

        self.name = 'encoder'
        self.channels = channels
        self.latent_dim = latent_dim
        self.n_c = n_c
        self.cshape = (128, 5, 5)
        self.iels = int(np.prod(self.cshape))
        self.lshape = (self.iels,)
        self.verbose = verbose

        self.model = nn.Sequential(
            # Convolutional layers
            nn.Conv2d(self.channels, 64, 4, stride=2, bias=True),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(64, 128, 4, stride=2, bias=True),
            nn.LeakyReLU(0.2, inplace=True),

            # Flatten
            Reshape(self.lshape),

            # Fully connected layers
            torch.nn.Linear(self.iels, 1024),
            nn.LeakyReLU(0.2, inplace=True),
            torch.nn.Linear(1024, latent_dim + n_c)
        )

        initialize_weights(self)

        if self.verbose:
            print("Setting up {}...\n".format(self.name))
            print(self.model)

    def forward(self, in_feat):
        z_img = self.model(in_feat)
        # Reshape for output
        z = z_img.view(z_img.shape[0], -1)
        # Separate continuous and one-hot components
        zn = z[:, 0:self.latent_dim]
        zc_logits = z[:, self.latent_dim:]
        # Softmax on zc component
        zc = softmax(zc_logits)
        return zn, zc, zc_logits


def tlog(x):
    return torch.log(x + 1e-8)


# Softmax function
def softmax(x):
    return F.softmax(x, dim=1)


# Cross Entropy loss with two vector inputs
def cross_entropy(pred, soft_targets):
    log_softmax_pred = torch.nn.functional.log_softmax(pred, dim=1)
    return torch.mean(torch.sum(- soft_targets * log_softmax_pred, 1))


class Discriminator_CNN(nn.Module):
    """
    CNN to model the discriminator of a ClusterGAN
    Input is tuple (X,z) of an image vector and its corresponding
    representation z vector. For example, if X comes from the dataset, corresponding
    z is Encoder(X), and if z is sampled from representation space, X is Generator(z)
    Output is a 1-dimensional value
    """

    # Architecture : (64)4c2s-(128)4c2s_BL-FC1024_BL-FC1_S
    def __init__(self, wass_metric=False, verbose=False, channels=3):
        super(Discriminator_CNN, self).__init__()

        self.name = 'discriminator'
        self.channels = channels
        self.cshape = (128, 5, 5)
        self.iels = int(np.prod(self.cshape))
        self.lshape = (self.iels,)
        self.wass = wass_metric
        self.verbose = verbose

        self.model = nn.Sequential(
            # Convolutional layers
            nn.Conv2d(self.channels, 64, 4, stride=2, bias=True),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(64, 128, 4, stride=2, bias=True),
            nn.LeakyReLU(0.2, inplace=True),

            # Flatten
            Reshape(self.lshape),

            # Fully connected layers
            torch.nn.Linear(self.iels, 1024),
            nn.LeakyReLU(0.2, inplace=True),
            torch.nn.Linear(1024, 1),
        )

        # If NOT using Wasserstein metric, final Sigmoid
        if (not self.wass):
            self.model = nn.Sequential(self.model, torch.nn.Sigmoid())

        initialize_weights(self)

        if self.verbose:
            print("Setting up {}...\n".format(self.name))
            print(self.model)

    def forward(self, img):
        # Get output
        validity = self.model(img)
        return validity


class ClusterGANTrainer(baseGANTrainer):

    def __init__(self, data_loader: MyDataLoader, generator=None, discriminator=None, encoder=None, device=None,
                 log_dir=None, auto_save=False, writer=None, verbose=0, evaluation_interval=10,
                 mem_threshold=0.9, lr=0.0002, scheduler=None, save_interval=400,
                 b1 = 0.5, b2 =0.999, n_cluster = 10, wass_metric=True, decay = 2.5*1e-5,
                 **kwargs):

        super(ClusterGANTrainer, self).__init__(data_loader, generator, discriminator, device,
                                               log_dir, auto_save, writer, verbose, evaluation_interval,
                                               mem_threshold, lr, scheduler, save_interval, **kwargs)
        # adversarial_loss = torch.nn.BCELoss()
        self.bce_loss = torch.nn.BCELoss()
        self.xe_loss = torch.nn.CrossEntropyLoss()
        self.mse_loss = torch.nn.MSELoss()
        # self.adversarial_loss = adversarial_loss
        n_classes = len(self.data_loader.classes)
        self.n_classes = n_classes
        self.wass_metric = wass_metric
        latent_dim = 100
        img_size = self.data_loader.size[2]
        channels = self.data_loader.size[0]
        self.n_cluster = n_cluster
        x_shape = (channels, img_size, img_size)
        generator = Generator_CNN(latent_dim, n_cluster, x_shape)
        discriminator = Discriminator_CNN(wass_metric=wass_metric, channels=channels)
        encoder = Encoder_CNN(latent_dim=latent_dim, n_c=n_cluster, channels=channels)
        self.encoder = encoder.to(self.device)
        self.generator = generator.to(self.device)
        self.discriminator = discriminator.to(self.device)
        ge_chain = ichain(generator.parameters(),
                          encoder.parameters())
        self.b1, self.b2 = b1, b2
        self.latent_dim = latent_dim
        optimizer_GE = torch.optim.Adam(ge_chain, lr=lr, betas=(self.b1, self.b2), weight_decay=decay)
        optimizer_D = torch.optim.Adam(self.discriminator.parameters(), lr=self.lr, betas=(self.b1, self.b2))
        self.optimizer_GE = optimizer_GE
        self.optimizer_D = optimizer_D
        cuda = True if torch.cuda.is_available() else False
        self.Tensor = torch.cuda.FloatTensor if cuda else torch.FloatTensor
        self.batch_size = self.data_loader.batch_size
        self.betan = 10
        self.betac = 10
        self.imgs_dir = os.path.join(self.data_loader.data_dir, 'images')
        os.makedirs(self.imgs_dir, exist_ok=True)
        testdata = self.data_loader.test_loader
        test_imgs, test_labels = next(iter(testdata))
        test_imgs = Variable(test_imgs.type(self.Tensor))
        self.test_imgs = test_imgs
        self.test_labels = test_labels


    def train(self, num_epochs):
        if self.verbose == 2:
            self.show()
        device = self.device
        Tensor = self.Tensor
        total_epochs = self.epoch + num_epochs
        outer_tqdm = tqdm(range(self.epoch, total_epochs), desc='Epochs', unit='epoch', position=0, leave=False)
        ge_l = []
        d_l = []

        c_zn = []
        c_zc = []
        c_i = []
        for epoch in outer_tqdm:
            # running_g_loss = 0.0
            # running_d_loss = 0.0
            inner_tqdm = tqdm(self.data_loader.train_loader, desc=f'Epoch {epoch + 1}/{total_epochs}', unit='batch',
                              position=1, leave=False)
            for i, (data, labels) in enumerate(inner_tqdm):
                self.generator.train()
                self.encoder.train()
                self.generator.zero_grad()
                self.encoder.zero_grad()
                self.discriminator.zero_grad()
                # valid = Variable(Tensor(data.size(0), 1).fill_(1.0), requires_grad=False).to(device)
                # fake = Variable(Tensor(data.size(0), 1).fill_(0.0), requires_grad=False).to(device)
                real_imgs = Variable(data.type(Tensor)).to(device)
                self.optimizer_GE.zero_grad()

                # Sample noise as generator input
                zn, zc, zc_idx = sample_z(shape=data.shape[0],
                                          latent_dim=self.latent_dim,
                                          n_c=self.n_cluster)

                # Generate a batch of images
                gen_imgs = self.generator(zn, zc).detach()
                D_gen = self.discriminator(gen_imgs)
                D_real = self.discriminator(real_imgs)
                enc_gen_zn, enc_gen_zc, enc_gen_zc_logits = self.encoder(gen_imgs)
                zn_loss = self.mse_loss(enc_gen_zn, zn)
                zc_loss = self.xe_loss(enc_gen_zc_logits, zc_idx)
                if self.wass_metric:
                    # Wasserstein GAN loss
                    ge_loss = torch.mean(D_gen) + self.betan * zn_loss + self.betac * zc_loss
                else:
                    # Vanilla GAN loss
                    valid = Variable(Tensor(gen_imgs.size(0), 1).fill_(1.0), requires_grad=False)
                    v_loss = self.bce_loss(D_gen, valid)
                    ge_loss = v_loss + self.betan * zn_loss + self.betac * zc_loss

                # Loss measures generator's ability to fool the discriminator
                ge_loss.backward(retain_graph=True)
                self.optimizer_GE.step()

                # ---------------------
                #  Train Discriminator
                # ---------------------

                self.optimizer_D.zero_grad()

                # Measure discriminator's ability to classify real from generated samples
                if self.wass_metric:
                    # Gradient penalty term
                    grad_penalty = calc_gradient_penalty(self.discriminator, real_imgs, gen_imgs)

                    # Wasserstein GAN loss w/gradient penalty
                    d_loss = torch.mean(D_real) - torch.mean(D_gen) + grad_penalty

                else:
                    # Vanilla GAN loss
                    fake = Variable(Tensor(gen_imgs.size(0), 1).fill_(0.0), requires_grad=False)
                    real_loss = self.bce_loss(D_real, valid)
                    fake_loss = self.bce_loss(D_gen, fake)
                    d_loss = (real_loss + fake_loss) / 2

                d_loss.backward()
                self.optimizer_D.step()

                # Save training losses
                d_l.append(d_loss.item())
                ge_l.append(ge_loss.item())
                inner_tqdm.set_postfix(D_loss=d_loss.item(), GE_loss=ge_loss.item())

                # Generator in eval mode
            self.generator.eval()
            self.encoder.eval()

            # Set number of examples for cycle calcs
            n_sqrt_samp = 5
            n_samp = n_sqrt_samp * n_sqrt_samp

            ## Cycle through test real -> enc -> gen
            t_imgs, t_label = self.test_imgs.data, self.test_labels
            # r_imgs, i_label = real_imgs.data[:n_samp], itruth_label[:n_samp]
            # Encode sample real instances
            e_tzn, e_tzc, e_tzc_logits = self.encoder(t_imgs)
            # Generate sample instances from encoding
            teg_imgs = self.generator(e_tzn, e_tzc)
            # Calculate cycle reconstruction loss
            img_mse_loss = self.mse_loss(t_imgs, teg_imgs)
            # Save img reco cycle loss
            c_i.append(img_mse_loss.item())

            ## Cycle through randomly sampled encoding -> generator -> encoder
            zn_samp, zc_samp, zc_samp_idx = sample_z(shape=n_samp,
                                                     latent_dim=self.latent_dim,
                                                     n_c=self.n_cluster)
            # Generate sample instances
            gen_imgs_samp = self.generator(zn_samp, zc_samp)
            # Encode sample instances
            zn_e, zc_e, zc_e_logits = self.encoder(gen_imgs_samp)
            # Calculate cycle latent losses
            lat_mse_loss = self.mse_loss(zn_e, zn_samp)
            lat_xe_loss = self.xe_loss(zc_e_logits, zc_samp_idx)
            # lat_xe_loss = cross_entropy(zc_e_logits, zc_samp)
            # Save latent space cycle losses
            c_zn.append(lat_mse_loss.item())
            c_zc.append(lat_xe_loss.item())

            # Save cycled and generated examples!
            r_imgs, i_label = real_imgs.data[:n_samp],labels[:n_samp]
            e_zn, e_zc, e_zc_logits = self.encoder(r_imgs)
            reg_imgs = self.generator(e_zn, e_zc)
            save_image(r_imgs.data[:n_samp],
                       '%s/real_%06i.png' % (self.imgs_dir, epoch),
                       nrow=n_sqrt_samp, normalize=True)
            save_image(reg_imgs.data[:n_samp],
                       '%s/reg_%06i.png' % (self.imgs_dir, epoch),
                       nrow=n_sqrt_samp, normalize=True)
            save_image(gen_imgs_samp.data[:n_samp],
                       '%s/gen_%06i.png' % (self.imgs_dir, epoch),
                       nrow=n_sqrt_samp, normalize=True)

                ## Generate samples for specified classes

                # batches_done = epoch * len(self.data_loader.train_loader) + i
                # if batches_done % self.save_interval == 0:
                #     #self.sample_image(n_row=10, batches_done=batches_done)
                #     self.sample_image(epoch=epoch)
            # epoch_loss_combined = (running_g_loss + running_d_loss) / (2 * len(self.data_loader.train_loader))
            outer_tqdm.set_postfix(img_mse_loss=img_mse_loss.item(), lat_mse_loss=lat_mse_loss.item(), lat_xe_loss=lat_xe_loss.item())
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


    def sample_image(self, epoch=None):
        """Saves a grid of generated digits ranging from 0 to n_classes"""
        # Sample noise
        if epoch is None:
            epoch = self.epoch
        stack_imgs = []
        for idx in range(self.n_cluster):
            # Sample specific class
            zn_samp, zc_samp, zc_samp_idx = sample_z(shape=self.n_cluster,
                                                     latent_dim=self.latent_dim,
                                                     n_c=self.n_cluster,
                                                     fix_class=idx)

            # Generate sample instances
            gen_imgs_samp = self.generator(zn_samp, zc_samp)

            if (len(stack_imgs) == 0):
                stack_imgs = gen_imgs_samp
            else:
                stack_imgs = torch.cat((stack_imgs, gen_imgs_samp), 0)

        # Save class-specified generated examples!
        save_image(stack_imgs,
                   '%s/gen_classes_%06i.png' % (self.imgs_dir, epoch),
                   nrow=self.n_cluster, normalize=True)

