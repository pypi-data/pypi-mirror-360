import shutil

import joblib
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans as _Kmeans
import os
from .AI import transforms, Models
from tqdm import tqdm
from PIL import Image
import torch
import torch.nn as nn
from collections import defaultdict


class KMeans:

    def __init__(self, n_cluster=5, random_state=42):
        self.n_cluster = n_cluster
        self.random_state = random_state
        self.kmeans = _Kmeans(n_clusters=self.n_cluster, random_state=self.random_state)
        self.labels = None

    def fit(self, features):
        self.kmeans.fit(features)
        self.labels = self.kmeans.labels_


class LeftHalfCrop:
    def __call__(self, img):
        width, height = img.size
        left_half = img.crop((0, 0, width // 2, height))
        return left_half


class RightHalfCrop:
    def __call__(self, img):
        width, height = img.size
        right_half = img.crop((width // 2, 0, width, height))
        return right_half


class ModelKMeans(KMeans):

    def __init__(self, data_dir=None, model=None, n_cluster=100, random_state=42, device=None, transform=None, image_paths=None):
        super(ModelKMeans, self).__init__(n_cluster=n_cluster, random_state=random_state)
        if device is None:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        if model is None:
            model = Models.resnet18(pretrained=True)
        self.device = device
        model = nn.Sequential(*list(model.children())[:-1])
        model.eval()
        self.model = model.to(device)
        if image_paths is None:
            image_paths = [os.path.join(data_dir, img) for img in os.listdir(data_dir) if
                           img.endswith('.jpg') or img.endswith('.png') or img.endswith('.webp')]
        self.image_paths = image_paths
        if transform is None:
            transforms.Compose([
                # transforms.Resize(256),
                RightHalfCrop(),
                transforms.Resize(256),
                # transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
        self.transform = transform
        features = []
        self.length = len(self.image_paths)

        for img_path in tqdm(image_paths, total=self.length, desc='Epoch'):
            img = Image.open(img_path)#.convert("RGB")
            transform_img = self.transform(img)
            img_tensor = transform_img.unsqueeze(0)
            # self.get_image(transform_img)

            with torch.no_grad():
                img_tensor = img_tensor.to(self.device)
                feature = model(img_tensor)
                features.append(feature.cpu().squeeze().numpy())

        self.features = np.array(features)

    def fit(self, *args):
        super().fit(self.features)
        self.store_dict()

    def show(self):
        for img_path, label in zip(self.image_paths, self.labels):
            print(f"Image: {img_path} - Cluster: {label}")

    def store_dict(self):
        images_by_cluster = defaultdict(list)
        for img_path, label in tqdm(zip(self.image_paths, self.kmeans.labels_),
                                    total=self.length, desc='Loading the images in to memory'):
            images_by_cluster[label].append(img_path)
        self.images_by_cluster = images_by_cluster
        return images_by_cluster

    def save(self, filename=None):
        images_by_cluster = defaultdict(list)
        for img_path, label in tqdm(zip(self.image_paths, self.kmeans.labels_),
                                    total=self.length, desc='Loading the images in to memory'):
            images_by_cluster[label].append(img_path)

        if filename is None:
            filename = "clustered_images"
        output_dir = filename
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for i in range(0, self.n_cluster):
            cluster_dir = os.path.join(output_dir, f"Cluster_{i}")
            if not os.path.exists(cluster_dir):
                os.makedirs(cluster_dir)

        for label, img_paths in tqdm(images_by_cluster.items(),
                                     total=len(images_by_cluster.keys()), desc='Saving images'):
            cluster_dir = os.path.join(output_dir, f"Cluster_{label}")

            for img_path in img_paths:
                # img = Image.open(img_path)
                img_name = os.path.basename(img_path)
                shutil.copy2(img_path, os.path.join(cluster_dir, img_name))
                # img.save(os.path.join(cluster_dir, img_name))

        print(f"Finish Saving")

    def get_image(self, transformed_img):
        unnormalize = transforms.Normalize(
            mean=[-0.485 / 0.229, -0.456 / 0.224, -0.406 / 0.225],
            std=[1 / 0.229, 1 / 0.224, 1 / 0.225]
        )

        transformed_img = unnormalize(transformed_img)

        np_img = transformed_img.permute(1, 2, 0).numpy()

        np_img = np.clip(np_img * 255, 0, 255).astype(np.uint8)

        plt.imshow(np_img)
        plt.axis('off')
        plt.show()

    def show_cluster(self):
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        reduced_features = pca.fit_transform(self.features)

        plt.figure(figsize=(10, 8))
        for i in range(self.n_cluster):
            cluster_points = reduced_features[self.labels == i]
            plt.scatter(cluster_points[:, 0], cluster_points[:, 1], label=f'Cluster {i}')

        plt.title('K-Means Clustering of Images')
        plt.xlabel('PCA Component 1')
        plt.ylabel('PCA Component 2')
        plt.legend()
        plt.show()

    def predict(self, new_image_paths):
        if not hasattr(self.kmeans, 'cluster_centers_'):
            raise ValueError("KMeans model has not been fitted yet. Call fit() before predict().")

        new_features = []
        for img_path in tqdm(new_image_paths, total=len(new_image_paths), desc='Predicting Images'):
            try:
                img = Image.open(img_path).convert("RGB")
                transform_img = self.transform(img)
                img_tensor = transform_img.unsqueeze(0)

                with torch.no_grad():
                    img_tensor = img_tensor.to(self.device)
                    feature = self.model(img_tensor)
                    new_features.append(feature.cpu().squeeze().numpy())
            except Exception as e:
                print(f"Warning: Could not process image {img_path} for prediction. Error: {e}")
                pass

        if not new_features:
            print("No valid new images could be processed for prediction.")
            return np.array([])

        new_features_np = np.array(new_features)
        if new_features_np.ndim == 1:
            new_features_np = new_features_np.reshape(1, -1)
        cluster_predictions = self.kmeans.predict(new_features_np)
        return cluster_predictions

    def save_model(self, filepath="kmeans_model.joblib"):
        if not hasattr(self.kmeans, 'cluster_centers_'):
            print("KMeans model has not been fitted yet. Call fit()")
            return
        try:
            joblib.dump(self.kmeans, filepath)
            print(f"Saved KMeans model: {filepath}")
        except Exception:
            pass

    def load_model(self, filepath="kmeans_model.joblib"):
        try:
            self.kmeans = joblib.load(filepath)
            self.n_cluster = self.n_clusters
            if hasattr(self.kmeans, 'labels_'):
                self.labels = self.kmeans.labels_
            else:
                self.labels = None

            if self.features is not None and self.features.size > 0:
                if hasattr(self.kmeans, 'cluster_centers_'):
                    try:
                        self.labels = self.kmeans.predict(self.features)
                        if hasattr(self, 'image_paths') and self.image_paths and len(self.image_paths) == len(
                                self.labels):
                            self.store_dict()
                    except Exception:
                        self.labels = None
                else:
                    self.labels = None


        except Exception:
            pass

