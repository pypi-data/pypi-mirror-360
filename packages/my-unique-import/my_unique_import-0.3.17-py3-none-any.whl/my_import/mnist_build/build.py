import random

from matplotlib import pyplot as plt

from my_import.prob import BernoulliSampler, UniformSampler
import pandas as pd
import numpy as np
import torch
from torchvision import datasets
from torchvision.transforms import ToTensor


size = 1000
U_D = UniformSampler(0, 10, dtype=int).sample(size)
D = U_D
C = BernoulliSampler(0.95-0.1*U_D).sample(size)
U_1 = BernoulliSampler(0.8).sample(size)
U_2 = BernoulliSampler(0.9).sample(size)
U_3 = BernoulliSampler(0.75).sample(size)
indicator = (U_D >= 5).astype(int)
B = (indicator ^ U_1) | ((C ^ U_2) & U_3)
df = pd.DataFrame({
    'D': U_D,
    'C': C,
    'B': B,
    # 'U_1': U_1, # 也可以加入中间变量进行检查
    # 'U_2': U_2,
    # 'U_3': U_3,
})

iter = zip(D,C,B)
print(iter)
train_data = datasets.MNIST(
    root = './data',
    train = True,
    transform = ToTensor(),
    download = True,
)
mnist_by_digit = {i: [] for i in range(10)}

# 遍历整个数据集，将图像存入对应的列表
for image_tensor, label in train_data:
    # 将 tensor 转为 numpy 数组 (28, 28)，像素范围 [0, 255]
    numpy_image = (image_tensor.squeeze().numpy() * 255).astype(np.uint8)
    mnist_by_digit[label].append(numpy_image)

print("预处理完成！")
for i in range(10):
    print(f"数字 '{i}' 包含 {len(mnist_by_digit[i])} 张图像。")

def edit_image(original_image, C, B):
    new_image = np.zeros((28, 28, 3), dtype=np.uint8)
    if C == 0:
        new_image[original_image > 0] = (0, 255, 0)
    elif C == 1:
        new_image[original_image > 0] = (255, 0, 0)
    if B == 1:
        new_image[0:3, :] = (0, 0, 255)
    return new_image


for d, c, b in iter:
    print(d, c, b)
    candidate_images = mnist_by_digit[d]
    original_image = random.choice(candidate_images)
    new_image = edit_image(original_image, c, b)
    plt.figure(figsize=(8, 4))
    plt.subplot(1, 2, 1)
    plt.title(f"Randomly Chosen 'd={d}'")
    plt.imshow(original_image, cmap='gray')
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.title(f"New Image (c={c}, b={b})")
    plt.imshow(new_image)
    plt.axis('off')

    plt.tight_layout()
    plt.show()


