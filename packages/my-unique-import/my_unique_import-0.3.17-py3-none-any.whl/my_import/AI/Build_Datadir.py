import random
import os
import shutil


class DataBuilder:

    def __init__(self, data, seed=42, train_rate=0.8, val_rate=0.1, test_rate=0.1):
        self.seed = seed
        random.shuffle(data)
        self.data = data
        self.train_rate = train_rate
        self.val_rate = val_rate
        self.test_rate = test_rate
        self.length = len(data)
        self.train_size = int(self.train_rate * self.length)
        self.val_size = int(self.length * self.val_rate)
        self.test_size = int(self.length * self.test_rate)

    def build(self, directory):
        train_data = self.data[:self.train_size]
        val_data = self.data[self.train_size:self.train_size + self.val_size]
        test_data = self.data[self.train_size + self.val_size:]
        os.makedirs(directory, exist_ok=True)
        train_path = os.path.join(directory, 'train')
        val_path = os.path.join(directory, 'val')
        test_path = os.path.join(directory, 'test')
        os.makedirs(train_path, exist_ok=True)
        os.makedirs(val_path, exist_ok=True)
        os.makedirs(test_path, exist_ok=True)
        for image_path, label in train_data:
            os.makedirs(os.path.join(train_path, label), exist_ok=True)
            img_name = os.path.basename(image_path)
            shutil.copy2(image_path, os.path.join(train_path, label,img_name))

        for image_path, label in val_data:
            os.makedirs(os.path.join(val_path, label), exist_ok=True)
            img_name = os.path.basename(image_path)
            shutil.copy2(image_path, os.path.join(val_path, label,img_name))

        for image_path, label in test_data:
            os.makedirs(os.path.join(test_path, label), exist_ok=True)
            img_name = os.path.basename(image_path)
            shutil.copy2(image_path, os.path.join(test_path, label,img_name))
