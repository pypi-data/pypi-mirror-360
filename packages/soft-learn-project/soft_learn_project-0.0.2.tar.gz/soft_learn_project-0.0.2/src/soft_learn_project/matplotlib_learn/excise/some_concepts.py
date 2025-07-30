# 什么是后端？
# 为了支持所有这些用例，matplotlib可以针对不同的输出，这些功能中的每一个都称为后端；
# “前端”是面向用户的代码，即绘图代码，而“后端”则在幕后完成了所有繁重的工作来生成数字。
# 有两种后端：用户界面后端（用于pygtk、wxpython、tkinter、qt4或macosx；也称为“交互后端”）和硬拷贝后端以生成图像文件（png、svg、pdf、ps；也称为“非交互后端”）。

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['path.simplify_threshold'] = 1.0

# Setup, and create the data to plot
y = np.random.rand(100000)
y[50000:] *= 2
y[np.geomspace(10, 50000, 400).astype(int)] = -1
mpl.rcParams['path.simplify'] = True

mpl.rcParams['agg.path.chunksize'] = 0
plt.plot(y)
plt.show()

mpl.rcParams['agg.path.chunksize'] = 10000
plt.plot(y)
plt.show()
