import numpy as np
import matplotlib.pyplot as plt
import random
import torch
from torch.nn import functional as F
import pandas as pd


class Neuro_net(torch.nn.Module):
  """搭建神经网络"""

  def __init__(self):
    super(Neuro_net, self).__init__()  # 继承__init__功能
    self.hidden_layer1 = torch.nn.Linear(2, 64)
    self.hidden_layer2 = torch.nn.Linear(64, 64)
    self.output_layer = torch.nn.Linear(64, 1)

  def forward(self, x):
    x = self.hidden_layer1(x)
    x = F.relu(x)
    c = x
    for i in range(3):
      x = self.hidden_layer2(x)
      x = F.relu(x)

    pridect_y = self.output_layer(x)
    return pridect_y


class TorchLearn():
  def __init__(self) -> None:
    # 安装

    pass

  def example(sef):
    # 1. 获取数据
    df = pd.read_csv(
        "/Users/wangjinlong/my_server/my/fuzz_melt/2022-4-20/df.csv", index_col=0)
    df_new = pd.read_csv(
        "/Users/wangjinlong/my_server/my/fuzz_melt/2022-4-20/df_new.csv", index_col=0)

    print(df_new.head())
    feature = df_new.values[:, 0:2]
    target = df_new.values[:, 2]

    x_data = feature
    y_data = target.reshape(-1, 1)
    print(x_data.shape, y_data.shape)

    # 2.建立模型
    net = Neuro_net()
    # optimizer 优化
    optimizer = torch.optim.ASGD(net.parameters(), lr=0.01)
    # loss funaction
    loss_funaction = torch.nn.MSELoss()
    epoch = 501
    x_data = torch.tensor(x_data, dtype=torch.float32)
    y_data = torch.tensor(y_data, dtype=torch.float32)

    # 3. 训练
    for step in range(epoch):
      pridect_y = net(x_data)  # 喂入训练数据 得到预测的y值
      loss = loss_funaction(pridect_y, y_data)  # 计算损失

      optimizer.zero_grad()  # 为下一次训练清除上一步残余更新参数
      loss.backward()  # 误差反向传播，计算梯度
      optimizer.step()  # 将参数更新值施加到 net 的 parameters 上

      if step % 100 == 0:
        print("已训练{}步 | loss：{}.".format(step, loss))
    exit()

    # 3. 训练
    plt.ion()
    for step in range(epoch):
      pridect_y = net(x_data)  # 喂入训练数据 得到预测的y值
      loss = loss_funaction(pridect_y, y_data)  # 计算损失

      optimizer.zero_grad()  # 为下一次训练清除上一步残余更新参数
      loss.backward()  # 误差反向传播，计算梯度
      optimizer.step()  # 将参数更新值施加到 net 的 parameters 上

      if step % 100 == 0:
        print("已训练{}步 | loss：{}.".format(step, loss))
        plt.cla()
        ax = plt.subplot(111, projection='3d')
        ax.scatter(x_data[:, 0], x_data[:, 1], y_data, c='g')
        ax.scatter(x_data[:, 0], x_data[:, 1], pridect_y.data.numpy(), c='r')
        plt.pause(0.1)

    plt.ioff()
    plt.show()
    pass
