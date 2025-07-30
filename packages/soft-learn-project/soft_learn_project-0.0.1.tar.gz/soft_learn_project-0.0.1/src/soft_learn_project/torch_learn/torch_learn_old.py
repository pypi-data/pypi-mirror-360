# 在 PyTorch中，torch.Tensor是存储和变换数据的主要工具。
# 如果你之前用过NumPy，你会发现Tensor和NumPy的多维数组非常类似。然而，Tensor提供GPU计算和自动求梯度等更多功能，这些使 Tensor 这一数据类型更加适合深度学习.
# Tensor的结构操作包括：创建张量，查看属性，修改形状，指定设备，数据转换， 索引切片，广播机制，元素操作，归并操作；
# Tensor的数学运算包括：标量运算，向量运算，矩阵操作，比较操作;

# 张量可以看成多维数组，下面用 Python 的numpy来定义张量。
"""
import numpy as np

# 0维张量 ()
x0 = np.array(28)
# 1维张量 (3,)
x1 = np.array([1, 2, 3])
# 2维张量 (2, 3)
x2 = np.array([[1, 2, 3], [4, 5, 6]])
# 3维张量 (3, 3, 4)
x3 = np.array([[[1, 4, 7, 3], [2, 5, 8, 5], [3, 6, 9, 4]],
               [[1, 2, 3, 4], [4, 5, 6, 3], [7, 8, 9, 5]],
               [[9, 8, 7, 5], [6, 5, 4, 4], [3, 2, 1, 3]]])
# 4维张量 (2, 5, 4, 3)
x4 = np.ones((2, 5, 4, 3))
"""

# 安装 pip3 install torch

# 使用
# import matplotlib_inline.backend_inline
# import torch

# print(torch.__version__)

# 创建tensor
# 数据表：2 维，形状 = (样本数，特征数)
# 序列类：3 维，形状 = (样本数，步长，特征数)
# 图像类：4 维，形状 = (样本数，宽，高，通道数)
# 视屏类：5 维，形状 = (样本数，帧数，宽，高，通道数)
# 机器学习，尤其深度学习，需要大量的数据，因此样本数肯定占一个维度，惯例我们把它称为维度 1。这样机器学习要处理的张量至少从 2 维开始。
"""
# （0维张量）
# torch.tensor与torch.Tensor的区别
x = torch.tensor(2)
print(x, x.shape, x.type())
# tensor(2) torch.Size([]) torch.LongTensor
y = torch.Tensor(2)
print(y, y.shape, y.type())
# tensor([0., 0.]) torch.Size([2]) torch.FloatTensor
# """

# 1维度张量
"""
x = torch.tensor([5.5, 3])
print(x, x.shape, x.type())
# """
# 2维向量
"""
torch.manual_seed(20211013)
x = torch.rand([4, 3])
print(x, x.shape, x.type())
x = torch.zeros([4, 3], dtype=torch.long)  # 构造一个矩阵全为 0，而且数据类型是 long.
print(x)
# """

"""
x = torch.tensor([5.5, 3])
x = x.new_ones([4, 3])  # 基于已经存在的 tensor，创建一个 tensor， 返回的tensor默认具有相同的 torch.dtype和torch.device
print(x, x.type())
x = torch.rand_like(x, dtype=torch.float)  # 重置数据类型
# """

# 获取它的维度等属性信息：
"""
# tensor.shape，tensor.size(): 返回张量的形状；
# tensor.ndim：查看张量的维度；
# tensor.dtype，tensor.type()：查看张量的数据类型；
# tensor.is_cuda：查看张量是否在GPU上；
# tensor.grad：查看张量的梯度；
# tensor.requires_grad：查看张量是否可微.
torch.manual_seed(20211013)
x = torch.rand([4, 3])
print("形状: ", x.shape, x.size())
print("维度: ", x.ndim)
print("类型: ", x.dtype, x.type())
print("cuda: ", x.is_cuda)
print("梯度: ", x.grad)
print("是否可微: ", x.requires_grad)
# """

# 常见的构造Tensor的函数：

# 函数	功能
# Tensor(*sizes)	基础构造函数。 直接从参数构建一个张量，支持List，Numpy数组。
# tensor(data)	类似于np.array
# ones(*sizes)	指定shape，生成元素全1的数据。
# zeros(*sizes)	指定shape，生成元素全0的数据。
# eye(*sizes)	对角为1，其余为0。指定（行列）数，创建二维单位Tensor。
# arange(s,e,step)	从s到e，步长为step生成一个序列张量。
# linspace(s,e,steps)	从s到e，均匀分成step份。
# logspace(s,e,steps)	从10^s 到 10^e，均匀分成steps份。
# rand/randn(*sizes)	生成[0,1]均匀分布和标准正态分布数据。
# normal(mean,std)/uniform(from,to)	正态分布/均匀分布
# randperm(m)	随机排列

# ---------
# 操作

# 一些加法操作：
"""
torch.manual_seed(20211013)
x = torch.rand([4, 3])
y = torch.ones([4, 3])
print(x + y)  # 方式1
print(torch.add(x, y))  # 方式2
result = torch.empty([4, 3])  # 方式3 提供一个输出 tensor 作为参数
torch.add(x, y, out=result)
print(result)
y.add_(x)  # 方式4 in-place
print(y)
# """

# 索引操作：（类似于numpy)
"""
torch.manual_seed(20211013)
x = torch.rand([4, 3])
print(x[:, 1])  # 取第二列
# """

# 改变大小：如果你想改变一个 tensor 的大小或者形状，你可以使用 torch.view：
"""
x = torch.randn([4, 4])
y = x.view(16)  # 注意 view() 返回的新tensor与源tensor共享内存（其实是同一个tensor)
z = x.view(-1, 8)  # -1是指这一维的维数由其他维度决定
print(x.size(), y.size(), z.size())

# Pytorch还提供了一 个reshape()可以改变形状，但是此函数并不能保证返回的是其拷贝，所以不推荐使用。推荐先用clone创造一个副本然后再使用view。
# 如果你有一个元素 tensor ，使用 .numpy() 来获得这个 value，即得到Python的标量：
x = torch.randn(1)
print(x)
print(x.item())  # 使用 .numpy() 来获得这个 value，即得到Python的标量：
# """

# 广播机制
# 当对两个形状不同的 Tensor 按元素运算时，可能会触发广播（broadcasting）机制：先适当复制元素使这两个 Tensor 形状相同后再按元素运算.
"""
x = torch.arange(1, 3).view(1, 2)
y = torch.arange(1, 4).view(3, 1)
print(x + y)
# """

# 2.2 自动求导
# PyTorch 中，所有神经网络的核心是autograd包。autograd包为张量上的所有操作提供了自动求导机制.
"""
x = torch.ones([2, 2], requires_grad=True)  # 创建一个张量并设置requires_grad=True用来追踪其计算历史。
print(x)
# """
# 梯度
# 现在开始进行反向传播，因为out是一个标量，因此out.backward()和out.backward(torch.tensor(1.))等价。
# 如果设置它的属性.requires_grad为True，那么它将会追踪对于该张量的所有操作。通过调用.backward()，来自动计算梯度.
"""
x = torch.ones([2, 2], requires_grad=True)
y = x ** 2
z = y * y * 3
out = z.mean()
out.backward()
print(x.grad)
# """

# 2.3 并行计算简介
# 在利用PyTorch做深度学习的过程中，可能会遇到数据量较大无法在单块GPU上完成，或者需要提升计算速度的场景，这时就需要用到并行计算。本节让我们来简单地了解一下并行计算的基本概念和主要实现方式，具体的内容会在课程的第二部分详细介绍。
# 2.3.1 为什么要做并行计算
# 我们学习PyTorch的目的就是可以编写我们自己的框架，来完成特定的任务。可以说，在深度学习时代，GPU的出现让我们可以训练的更快，更好。所以，如何充分利用GPU的性能来提高我们模型学习的效果，这一技能是我们必须要学习的。这一节，我们主要讲的就是PyTorch的并行计算。PyTorch可以在编写完模型之后，让多个GPU来参与训练。
# 2.3.2 CUDA是个啥
# CUDA是我们使用GPU的提供商——NVIDIA提供的GPU并行计算框架。对于GPU本身的编程，使用的是CUDA语言来实现的。在PyTorch使用 CUDA则表示要开始要求我们的模型或者数据开始使用GPU了。
# 在编写程序中，当我们使用了 cuda() 时，其功能是让我们的模型或者数据迁移到GPU当中，通过GPU开始计算。


# --------------------------------------------------
# 深度学习的一个小例子
# 线性回归从零开始实现 原文链接：https://blog.csdn.net/qq_37402392/article/details/120254894

# 我们使用线性回归模型真实权重 w = [ 2 , − 3.4 ] T w=[2, -3.4]^{T} w=[2,−3.4]
# T 和偏差 b = 4.2 b=4.2 b=4.2，以及一个随机噪声项 ε来生成标签.
# y=Xw+b+ε
# 其中噪声项 ε 服从均值为0、标准差为0.01的正态分布。噪声代表了数据集中无意义的干扰。下面，让我们生成数据集。

import matplotlib.pyplot as plt
import random
num_inputs = 2  # 输入数目
num_examples = 1000  # 样本数目
true_w = [2, -3.4]  # 权重w的真实值
true_b = 4.2  # 偏差b的真实值
features = torch.randn(num_examples, num_inputs, dtype=torch.float32)  # 输入特征
labels = true_w[0] * features[:, 0] + \
    true_w[1] * features[:, 1] + true_b  # 标签数据
labels += torch.tensor(np.random.normal(0, 0.01, size=labels.size()),
                       dtype=torch.float32)  # 引入噪声

# print(labels)
print(features.numpy())

# 通过生成第二个特征 features[:, 1] 和标签 labels 的散点图，可以更直观地观察两者间的线性关系.


def use_svg_display():
  # 用矢量图显示
  matplotlib_inline.backend_inline.set_matplotlib_formats('svg')


def set_figsize(figsize=(3.5, 2.5)):
  use_svg_display()
  # 设置图的尺寸
  plt.rcParams['figure.figsize'] = figsize


set_figsize()
# 加分号只显示图
plt.scatter(features[:, 1].numpy(), labels.numpy(), 1)
# plt.show()


# 2.2.2 读取数据集
# 在训练模型的时候，我们需要遍历数据集并不断读取小批量数据样本。这里我们定义一个函数：它 每次返回 batch_size（批量大小）个随机样本的特征和标签.
def data_iter(batch_size, features, labels):
  # 获取特征数量
  num_examples = len(features)
  # 获取所有的索引
  indices = list(range(num_examples))
  # 样本的读取顺序是随机的
  random.shuffle(indices)
  for i in range(0, num_examples, batch_size):
    # 最后一次可能不足一个batch，所以使用min
    j = torch.LongTensor(indices[i: min(i + batch_size,
                                        num_examples)])
    # index_select函数根据索引返回对应元素
    yield features.index_select(0, j), labels.index_select(0, j)


# 让我们读取第一个小批量数据样本并打印。每个批量的特征形状为(10, 2)，分别对应批量大小和输 入个数；标签形状为批量大小.
batch_size = 10
for X, y in data_iter(batch_size, features, labels):
  print(X, y)
  # 只读取第一个
  break

# 2.2.3 初始化模型参数
# 我们将权重初始化成均值为0、标准差为0.01的正态随机数，偏差则初始化成0。不能将所有的权重都初始化为0。
w = torch.tensor(np.random.normal(0, 0.01, (num_inputs, 1)),
                 dtype=torch.float32)  # 均值为0、标准差为0.01的正态随机数
b = torch.zeros(1, dtype=torch.float32)  # 偏差为0

# 之后的模型训练中，需要对这些参数求梯度来迭代参数的值，因此我们要让它们的 requires_grad=True 。
w.requires_grad_(requires_grad=True)
b.requires_grad_(requires_grad=True)
torch.tensor([0.], requires_grad=True)


# 2.2.4
# 定义模型   下面是线性回归的矢量计算表达式的实现。我们使用mm()函数做矩阵乘法。
def linreg(X, w, b):
  '''
  计算线性回归值

  X: 数据
  w: 权重
  b: 偏差
  '''
  return torch.mm(X, w) + b


# 2.2.5 定义损失函数
# 我们使用上一节描述的平方损失来定义线性回归的损失函数。在实现中，我们需要把真实值 y 变形 成预测值 y_hat 的形状。以下函数返回的结果也将和 y_hat 的形状相同。
def squared_loss(y_hat, y):
  '''
  计算平方损失
  '''
  return (y_hat - y.view(y_hat.size())) ** 2 / 2


# 2.2.6
# 定义优化函数
# 以下的sgd函数实现了上一节中介绍的小批量随机梯度下降算法。它通过不断迭代模型参数来优化损失函数。这里自动求梯度模块计算得来的梯度是一个批量样本的梯度和。我们将它除以批量大小来得到平均值。
def sgd(params, lr, batch_size):
  '''
  小批量随机梯度下降

  params: 权重
  lr: 学习率
  batch_size: 批大小
  '''
  for param in params:
    param.data -= lr * param.grad / batch_size


# 在训练中，我们将多次迭代模型参数。在每次迭代中，我们根据当前读取的小批量数据样本（特征 X 和标签 y ），通过调用反向函数 backward 计算小批量随机梯度，并调用优化算法 sgd 迭代模型参 数。由于我们之前设批量大小 batch_size 为10，每个小批量的损失 l 的形状为(10, 1)。回忆一下自动 求梯度一节。由于变量 l 并不是一个标量，所以我们可以调用 .sum() 将其求和得到一个标量，再运行 l.backward() 得到该变量有关模型参数的梯度。注意在每次更新完参数后不要忘了将参数的梯度清零。（如果不清零，PyTorch默认会对梯度进行累加）
# 在一个迭代周期（epoch）中，我们将完整遍历一遍 data_iter 函数，并对训练数据集中所有样本 都使用一次（假设样本数能够被批量大小整除）。这里的迭代周期个数 num_epochs 和学习率 lr 都是超参数，分别设3和0.03。在实践中，大多超参数都需要通过反复试错来不断调节。虽然迭代周期数设得越大，模型可能越有效，但是训练时间可能过长。
lr = 0.03
num_epochs = 3
net = linreg
loss = squared_loss
# 训练模型一共需要num_epochs个迭代周期
for epoch in range(num_epochs):
  # 在每一个迭代周期中，会使用训练集中所有样本一次（假设样本数能够被批量大小整除）。
  # X和y分别是小批量样本的特征和标签
  for X, y in data_iter(batch_size, features, labels):
    # l是有关小批量X和y的损失
    l = loss(net(X, w, b), y).sum()
    # 小批量损失对模型参数求梯度
    l.backward()
    # 使用小批量随机梯度下降迭代模型参数
    sgd([w, b], lr, batch_size)
    # 梯度清零
    w.grad.data.zero_()
    b.grad.data.zero_()
  train_l = loss(net(features, w, b), labels)
  print('epoch %d, loss %f' % (epoch+1, train_l.mean().item()))

  print((true_w, w))
  print((true_b, b))
