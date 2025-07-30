import matplotlib
import matplotlib.animation
import mpl_toolkits
import mpl_toolkits.mplot3d
import matplotlib.axis
import matplotlib.colorbar
import matplotlib.figure
from matplotlib.ticker import LinearLocator
import matplotlib.cm
import mpl_toolkits.axes_grid1
import mpl_toolkits.axisartist
import mpl_toolkits
import matplotlib.colors
from matplotlib import figure
from matplotlib.axes import _axes as axes
from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.mplot3d import Axes3D  # 画三维图需要这个命令
from matplotlib import pyplot as plt
import numpy as np
import matplotlib.axes
import pandas as pd


class Learn():
  def __init__(self) -> None:
    """
    [参考网址](https://www.cnblogs.com/xingshansi/p/6777945.html)
    [最重要的还是官方](https://matplotlib.org/2.0.2/mpl_toolkits/mplot3d/tutorial.html#mplot3d-tutorial)
    https://www.bilibili.com/video/av38512783/?p=12&spm_id_from=pageDriver
    """
    pass

  def install(self):
    string = """默认也安装过了
    conda install matplotlib 
    """
    print(string)
    return None

  def example_OO_style(self):
    # OO style绘图 面向对象的绘图风格
    # 面向对象和交互式绘图风格，两种里面选择并坚持其中一种，而不要想两种都很熟，我选择OO style
    x = np.linspace(0, 2, 100)  # Sample data.

    # Note that even in the OO-style, we use `.pyplot.figure` to create the figure.
    fig, ax = plt.subplots()  # Create a figure and an axes.
    ax.plot(x, x, label='linear')  # Plot some data on the axes.
    ax.plot(x, x**2, label='quadratic')  # Plot more data on the axes...
    ax.plot(x, x**3, label='cubic')  # ... and some more.
    ax.set_xlabel('x label')  # Add an x-label to the axes.
    ax.set_ylabel('y label')  # Add a y-label to the axes.
    ax.set_title("Simple Plot")  # Add a title to the axes.
    ax.legend()  # Add a legend.

  def pyplot_style():
    """(pyplot-style) 的绘图风格
    """
    x = np.linspace(0, 2, 100)  # Sample data.
    plt.plot(x, x, label='linear')  # Plot some data on the (implicit) axes.
    plt.plot(x, x**2, label='quadratic')  # etc.
    plt.plot(x, x**3, label='cubic')
    plt.xlabel('x label')
    plt.ylabel('y label')
    plt.title("Simple Plot")
    plt.legend()

  def ticks(self, ax):
    """# 关于刻度的一些设置
    # ax.locator_params('x', nbins=10)  # 设置刻度的密度，x轴的密度为10，数字越大越密集
    # ax.xaxis.set_major_formatter(plt.NullFormatter())  # 隐藏x轴的刻度标签
    # ax.xaxis.set_major_locator(plt.NullLocator())  # 隐藏x轴的刻度和标签
    # axi.xaxis.set_major_locator(plt.MaxNLocator(3))  # 自定义刻度数量为3
    # ax.xaxis.set_major_locator(plt.MultipleLocator(np.pi / 2))  # 设置主刻度的位置
    # ax.xaxis.set_minor_locator(plt.MultipleLocator(np.pi / 4))  # 设置次刻度的位置

    # 刻度格式生成器与定位器小结
    定位器类	描述
    NullLocator	无刻度
    FixedLocator	刻度位置固定
    IndexLocator	用索引作为定位器（如 x = range(len(y))）
    LinearLocator	从 min 到 max 均匀分布刻度
    LogLocator	从 min 到 max 按对数分布刻度
    MultipleLocator	刻度和范围都是基数（base）的倍数
    MaxNLocator	为最大刻度找到最优位置
    AutoLocator	（默认）以 MaxNLocator 进行简单配置
    AutoMinorLocator	次要刻度的定位器
    格式生成器类	描述
    NullFormatter	刻度上无标签
    IndexFormatter	将一组标签设置为字符串
    FixedFormatter	手动为刻度设置标签
    FuncFormatter	用自定义函数设置标签
    FormatStrFormatter	为每个刻度值设置字符串格式
    ScalarFormatter	（默认）为标量值设置标签
    LogFormatter	对数坐标轴的默认格式生成器


    Args:
        ax (_type_): _description_
    """
    # 设置刻度值
    ax.xaxis.set_major_locator(plt.FixedLocator(np.arange(0, 12, 2)))
    ax.xaxis.set_major_formatter(plt.FixedFormatter(np.arange(0, 0.12, 0.02)))
    ax.yaxis.set_major_locator(plt.FixedLocator(np.arange(0, 12, 2)))
    ax.yaxis.set_major_formatter(plt.FixedFormatter(
        np.round(np.arange(0, 1.2, 0.2), decimals=1)))
    ax.set_xticks(np.arange(0, 12, 2))
    ax.set_xticklabels(np.arange(0, 0.12, 0.02))
    ax.set_yticks(np.arange(0, 12, 2))
    ax.set_yticklabels(np.round(np.arange(0, 1.2, 0.2)))

  def ticks_set2(self):

    pass

  def setp(self):
    """
    ## getp(), setp()的使用方法
    概述
    pyplot模块提供了获取/设置对象属性值的接口。功能类似于Python内置函数getattr和setattr。从源码上来看，get()是getp()的别名，两者是等价的。setp()、getp()的底层实现是基于Python内置函数getattr和setattr。

    getp()函数：获取对象属性
    getp()函数的签名为matplotlib.pyplot.getp(obj, *args, **kwargs)。
    常用参数为：

    obj ：需要查询属性的对象。类型为 Artist对象，即matplotlib所有可见对象。必备参数。
    property：需要查询的属性。类型为字符串或None, 默认值为 None。
    当值为None时，返回对象的所有属性。
    当值为某属性名时，则会返回obj.get_属性名()的值。
    返回值为查询对象的某个属性或为None，此时打印输出全部属性。

    # setp() getp() 设置和获取对象属性  # 以下这两种格式是等价的
    # plt.setp(lines, 'linewidth', 2, 'color', 'r')  # MATLAB style
    # plt.setp(lines, linewidth=2, color='r')  # python style
    #  修改属性的思路：getp()先查看某个对象的属性，然后setp()修改


    ### setp()函数：设置对象属性或属性的取值要求
    setp()函数的签名为matplotlib.pyplot.setp(obj, *args, **kwargs)。
    常用参数为：

    obj ：需要设置属性的对象或对象列表。类型为 Artist对象或 Artist对象列表，即matplotlib所有可见对象。必备参数。
    file ：当查询属性取值要求时输出文件的位置。类文件对象。默认值为 sys.stdout。
    *args、**kwargs：需要设置的属性值。
    setp()函数的调用方式有很多种：

    * 设置一个对象的一个属性。
    ```
    line, = plt.plot([1, 2, 3])
    plt.setp(line, linestyle='--')
    ````
    * 设置多个对象的一个属性。
    ```
    lines = plot([1, 2, 3],[1, 2, 3],[4, 5, 6],[4, 5, 6])
    setp(lines, linestyle='--')
    ```
    * 设置一个对象的多个个属性。
    `setp(line, linewidth=2, color='r')`

    * 输出该属性的取值要求。

    `setp(line, 'linestyle')`
    > 输出为： linestyle: {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}

    * 输出所有可设置的属性及其取值要求。
    setp(line)
    > 输出为： agg_filter: a filter function, ...

    * setp 还支持 MATLAB 式的键值对。
    `setp(lines, 'linewidth', 2, 'color', 'r')`

    ### 总结
    在matplotlib当中，所有可见对象都继承自Artist类，因此，这些对象被称为Artist。

    pyplot模块的setp()、getp/get()等函数底层其实都是调用的Artist类的相关方法。

    属性操作中属性名称可能是一个令人疑惑的地方。
    在matplotlib当中，实际的属性值存储在_开头的属性中，然后对外提供setter 、getter方法调用。

    例如Line2D对象，其颜色属性为_color，对外接口为get_color()、set_color()。通过内置函数dir()即可列出对象的属性。
    """
    x = np.arange(0, 1.0, 0.01)
    # x = np.linspace(0, 7, 20)
    y1 = np.sin(2 * np.pi * x)
    y2 = np.sin(4 * np.pi * x)
    # lines = plt.plot(x, y1, x, y2)  # plt.setp(lines, color='r', marker='o')  # 设置的实例为列表，所有的实例都会被设置为相同的值
    line = plt.plot(x, y1, 'k:', label='sin(x)')
    # plt.setp(line)  # 查看能够被设置的所有属性
    # plt.setp(line, 'linestyle')  # 提供属性名而不提供值，(注意属性值是字符串)这样可以获得属性值的有效参数类型
    hxl = plt.xlabel('时间轴', loc='center')
    plt.gca().set_xlabel('得更快了')
    hleg = plt.legend()
    # print(plt.xticks())
    # plt.setp(hleg.get_texts(), fontsize=20)  # 设置图例的字体大小
    plt.setp(plt.gca().get_legend().get_texts())  # 获取图例的文本句柄
    # plt.gca()函数返回当前的坐标轴(一个matplotlib.axes.Axes的实例)，gcf()函数返回当前视图窗口(一个matplotlib.figure.Figure实例)
    # print(plt.get_fignums())  # 返回图形编号
    # print(plt.get_figlabels())  # Return a list of existing figure labels.
    # print(plt.get_plot_commands())   # 返回所有的绘图命令
    # plt.hlines(0.5,xmin=0, xmax=0.5)  # 增加水平线
    plt.axhline(0.5, 0, 0.5)  # 同上
    plt.pause(3)  # 三秒后关闭图形窗口
    pass

  def setp_example(self):
    # 案例：演示 setp()函数
    line, = plt.plot([2, 1])
    # 利用键值对设置属性
    plt.setp(line, color='b')
    # matlab式键值对
    plt.setp(line, "color", "g")
    # 利用内置哈数setattr设置属性值
    setattr(line, "_color", 'red')
    # 将color属性取值要求输出到标准输出
    plt.setp(line, "color")
    # 将line对象所有属性取值要求输出到标准输出
    plt.setp(line)
    # 设置多个对象的属性
    lines = plt.plot([1, 2, 3], [1, 2, 3], [4, 5, 6], [4, 5, 6])
    plt.setp(lines, linestyle='--')
    # 将获取到的color属性取值要求输出到setp.log中
    with open("setp.log", "a+") as f:
      plt.setp(line, "color", file=f)
    plt.show()

  def interactive_开启交互模式_动图(self,):
    """开启交互模式_动图, 在 py 中运行效果好
    """
    # method 1
    # plt.ion()
    # for i in range(20):
    #   plt.cla()
    #   x = np.linspace(0, 7, 200)
    #   y = np.cos(x - i*0.1)
    #   plt.plot(x, y)
    #   plt.pause(0.05)
    # plt.ioff()
    # plt.show()

    # method2
    # 开启交互模式
    plt.ion()

    # 创建图形窗口
    fig, ax = plt.subplots()

    # 绘制初始图形
    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x)
    line, = ax.plot(x, y)

    # 更新图形
    for i in range(100):
      y = np.sin(x + i/10)
      line.set_ydata(y)
      plt.draw()
      # plt.plot(x,y)
      plt.pause(0.01)

    # 关闭交互模式
    plt.ioff()
    plt.show()

  def spectial_符号(self, ax: matplotlib.axes.Axes):
    """插入希腊字母: 两个美元符号中书写TeX表达式
    """
    s = r"$\alpha$=0.8"
    ax.set_xlabel()
    ax.title(r'导体表面斜入射的合成波: \n' +
             r'$2E_m \sin(kz \cos \theta_i ) \cos(k\sin \theta_i x)$')
    pass

  def get_cmaps(self):
    # 列出所有可用的颜色映射
    cmaps = plt.colormaps()
    return cmaps

  def string_eample(self):
    string = """一些例子
    ---1
    # 面向对象和交互式绘图风格，两种里面选择并坚持其中一种，而不要想两种都很熟，我选择OO style
    x = np.linspace(0, 2, 100)  # Sample data.

    # Note that even in the OO-style, we use `.pyplot.figure` to create the figure.
    fig, ax = plt.subplots()  # Create a figure and an axes.
    ax.plot(x, x, label='linear')  # Plot some data on the axes.
    ax.plot(x, x**2, label='quadratic')  # Plot more data on the axes...
    ax.plot(x, x**3, label='cubic')  # ... and some more.
    ax.set_xlabel('x label')  # Add an x-label to the axes.
    ax.set_ylabel('y label')  # Add a y-label to the axes.
    ax.set_title("Simple Plot")  # Add a title to the axes.
    ax.legend()  # Add a legend.

    ---2
    # 案例：演示 setp()函数
    line, = plt.plot([2, 1])
    # 利用键值对设置属性
    plt.setp(line, color='b')
    # matlab式键值对
    plt.setp(line, "color", "g")
    # 利用内置哈数setattr设置属性值
    setattr(line, "_color", 'red')
    # 将color属性取值要求输出到标准输出
    plt.setp(line, "color")
    # 将line对象所有属性取值要求输出到标准输出
    plt.setp(line)
    # 设置多个对象的属性
    lines = plt.plot([1, 2, 3], [1, 2, 3], [4, 5, 6], [4, 5, 6])
    plt.setp(lines, linestyle='--')
    # 将获取到的color属性取值要求输出到setp.log中
    with open("setp.log", "a+") as f:
      plt.setp(line, "color", file=f)
    plt.show()

    ---3 
    # 1. 准备数据
    np.random.seed(0)
    y1 = np.linspace(0, 1, 100)
    y2 = np.random.randint(1000, 2000, 100)

    # 2. 画图
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.set_xlabel("时间")
    ax.set_ylabel("速度")
    line1, = ax.plot(y1, marker="o", color="k", label="速度")
    ax2 = ax.twinx()  # 添加第二个y轴的方法
    ax2.set_ylabel("受力")
    ax2.set_ylim(0, 3000)
    line2, = ax2.plot(y2, marker="*", color="r", label="受力")
    # ax.legend([line1,line2],["速度","受力"])  # 增加图例的方法 合并图例的方法就是仅使用一个轴的legend()函数。
    # 合并图列
    lns = [*ax.get_lines(), *ax2.get_lines()]
    labs = [l.get_label() for l in lns]
    legend = ax.legend(lns, labs, loc='best', fontsize=16)  # 修改图例字体大小
    plt.show()
    """
    print(string)
    return None


class CollegePhysicsBookFigures():
  def __init__(self) -> None:
    """书上例题的一些图形
    """
    pass

  def yxcf_有限差分法(self):
    def update_f(f):
      for i in range(1, 4):
        for j in range(1, 4):
          f[i, j] = 1/4 * (f[i-1, j] + f[i+1, j] + f[i, j-1] + f[i, j+1])
      return f

    f = np.zeros(shape=(5, 5))
    f[0, :] = 100
    tol = 1e-4

    f_init = f.copy()
    f_new = update_f(f)
    n = 0
    while np.max(np.abs(f_new - f_ini)) > tol:
      f_ini = f.copy()
      f_new = update_f(f)
      n += 1
    print(f)
    print(n)
    pass

  def ss_色散群速(self):
    omega = 10
    delta_omega = 1
    omega1 = omega + delta_omega
    omega2 = omega - delta_omega

    beta = 10
    delta_beta = 1
    beta1 = beta + delta_beta
    beta2 = beta - delta_beta
    beta3 = beta + 200

    Em = 1
    z = np.linspace(0, 10, 300)
    t = np.linspace(0, 10, 100)
    E1 = Em * np.cos(beta1 * z)
    E2 = Em * np.cos(beta2 * z)
    E3 = Em * np.cos(beta3 * z)

    E = 2*Em * np.cos(delta_beta * z) * np.cos(beta*z)

    plt.figure(figsize=(10, 3))
    ax = plt.subplot(131)
    ax.plot(z, E1, color="r", label="E1")
    ax.plot(z, E2, color="b", label="E2")
    ax.legend(loc=1)
    ax = plt.subplot(132)
    ax.plot(z, E1+E2, color="k", label="E总")
    ax.legend(loc=1)
    ax = plt.subplot(133)
    ax.plot(z, E1 + E2 + E3, color="k", label="E1+E2+E3")
    ax.legend(loc=1)
    plt.show()
    fig = plt.figure()
    ax = plt.subplot(121)
    ax.plot(z, E3, color="r", label="E3")
    ax = plt.subplot(122)
    ax.plot(z, E2+E3, color="k", label="E2+E3")
    ax.legend(loc=1)
    plt.show()

  def p514(self):
    # P154 例题3.6.3 均匀介质圆柱在均匀外场中极化
    x = np.linspace(-4, 4, 100)
    y = np.linspace(-4, 4, 100)
    x, y = np.meshgrid(x, y)
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan(y/x)
    # theta = np.arcsin(y/r)
    a = 1
    E0 = 1
    # 电场
    Ex = E0 + E0 * (a/r)**2 * (np.cos(theta)**2 - np.sin(theta)**2)
    Ey = E0 * (a/r)**2 * (2 * np.cos(theta)*np.sin(theta))
    # 电位
    phi = - E0 * r*np.cos(theta) + 0.5 * E0 * a**2 * r**(-1) * np.cos(theta)
    ax = plt.subplot(111)
    ax.set_aspect(aspect="equal")
    ax.streamplot(x, y, Ex, Ey, density=0.5)
    ax.contour(x, y, phi, [-3, -2, -1, 0.1, 1, 5])

  def fb_方波(self):
    plt.rcParams["font.family"] = ["Heiti TC"]

    def plot_square():
      """
      绘制方波图形
      """
      from scipy import signal
      import matplotlib.pyplot as plt
      t = np.linspace(0, 2, 500, endpoint=False)
      plt.plot(t, signal.square(2 * np.pi * t), 'b')
      plt.ylim(-2, 2)
      plt.grid()
      plt.show()

    def sin_sum():
      """
      几个正弦波的合成
      """
      import numpy as np
      import matplotlib.pyplot as plt

      t = np.linspace(-np.pi, np.pi, 201)
      k = np.arange(1, 19)
      k = 2 * k - 1
      # k = 99
      f = np.zeros_like(t)
      for i in range(len(t)):
        f[i] = np.sum(np.sin(k * t[i]) / k)

      f = (4 / np.pi) * f

      plt.plot(t, f, label="4个正弦波的合成")
      plt.legend()
      plt.pause(3)

    def simple_test():
      """
      几个正弦波的合成
      """
      t = np.linspace(0, 2 * np.pi, 100)
      x1 = np.sin(t)
      x2 = np.sin(3 * t) / 3
      x3 = np.sin(5 * t) / 5
      fig, ax = plt.subplots()
      ax: plt.Axes
      # ax.plot(t,x,label="sin")
      ax.plot(t, x1, '-b', label="sin(t)")
      ax.plot(t, x2, label="sin(3t)")
      ax.plot(t, x3, label="sin(5t)")
      x = x1 + x2 + x3
      ax.plot(t, x, label="sum", color="red")
      ax.legend()
      plt.show()


class TwoDimension():
  def __init__(self) -> None:
    pass

  def add_vlines(self, ax: matplotlib.axes.Axes,
                 x=0, color='k', linestyles=':'):
    """加入垂直虚线
    """

    bottom, top = ax.get_ylim()
    ax.vlines(x=x, ymin=bottom, ymax=top,
              linestyles=linestyles, colors=color)
    return ax

  def add_hlines(self, ax: matplotlib.axes.Axes,
                 y=0, color='k',
                 linestyles='-',):
    """加入水平线
    """

    left, right = ax.get_xlim()
    ax.hlines(y=y, xmin=left, xmax=right,
              linestyles=linestyles, colors=color)
    return ax

  def add_vlines_hlines(self, ax: matplotlib.axes.Axes,
                        x=0, y=0, color='k'):
    """加入水平线和垂直虚线

    Args:
        ax (matplotlib.axes.Axes): _description_
        x (int, optional): _description_. Defaults to 0.
        y (int, optional): _description_. Defaults to 0.
        color (str, optional): _description_. Defaults to 'k'.

    Returns:
        _type_: _description_
    """

    bottom, top = ax.get_ylim()
    ax.vlines(x=x, ymin=bottom, ymax=top, linestyles=':',
              colors=color)
    left, right = ax.get_xlim()
    ax.hlines(y=y, xmin=left, xmax=right, linestyles='-',
              colors=color)
    return ax

  def plot_line(self, x, y,
                fig=None,
                ax=None,
                marker='o', linestyle='-', color='red',
                xlabel='时间 (s)',
                ylabel='距离 (m)',
                ):
    if fig is None:
      fig = plt.figure()
    if ax is None:
      ax = fig.add_subplot()
    ax.plot(x, y,
            marker=marker,
            linestyle=linestyle,
            color=color)
    ax.set_xlabel(xlabel=xlabel)
    ax.set_ylabel(ylabel=ylabel)
    return fig, ax

  def double_y_axies_example(self,):
    """画双y轴图的方法

    Returns:
        _type_: _description_
    """
    # 1. 准备数据
    np.random.seed(0)
    y1 = np.linspace(0, 1, 100)
    y2 = np.random.randint(1000, 2000, 100)

    # 2. 画图
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.set_xlabel("时间")
    ax.set_ylabel("速度")
    line1, = ax.plot(y1, marker="o", color="k", label="速度")
    ax2 = ax.twinx()  # 添加第二个y轴的方法
    ax2.set_ylabel("受力")
    ax2.set_ylim(0, 3000)
    line2, = ax2.plot(y2, marker="*", color="r", label="受力")
    # ax.legend([line1,line2],["速度","受力"])  # 增加图例的方法 合并图例的方法就是仅使用一个轴的legend()函数。
    # 合并图列
    lns = [*ax.get_lines(), *ax2.get_lines()]
    labs = [l.get_label() for l in lns]
    # loc 字符串选项或整数选项
    # "best"：自动选择最合适的位置（默认值） 0
    # "upper right"：右上角 1
    # "upper left"：左上角 2
    # "lower left"：左下角 3
    # "lower right"：右下角 4
    # "right"：右侧 5
    # "center left"：左侧中间 6
    # "center right"：右侧中间 7
    # "lower center"：底部中间 8
    # "upper center"：顶部中间 9
    # "center"：中心 10
    legend = ax.legend(lns, labs, loc='best', fontsize=16)  # 修改图例字体大小
    # plt.show()
    return None

  def double_y_axies(self, x, y1, y2,
                     x_label=None,
                     ax_y1label=None,
                     ax_y2label=None,
                     line_y1label=None,
                     line_y2label=None,
                     lable_fontdict=None,
                     y1_lim=None,
                     y2_lim=None,
                     markersize=2,
                     is_save=False,
                     fname='tmp.pdf',
                     fig=None,
                     ax=None,
                     ):
    """画双y轴图的方法
    lable_fontdict = {
    'family': 'serif',
    'style': 'italic',
    'weight': 'bold',
    'size': 14,
    'color': 'blue'
      }
    """

    if fig is None:
      fig = plt.figure()
      ax = fig.add_subplot()
    ax.set_xlabel(x_label, fontdict=lable_fontdict)
    ax.set_ylabel(ax_y1label, fontdict=lable_fontdict)
    line1, = ax.plot(x, y1, marker="o", color="k",
                     label=line_y1label, markersize=markersize, alpha=0.5)
    ax2 = ax.twinx()  # 添加第二个y轴的方法
    ax2.set_ylabel(ax_y2label, fontdict=lable_fontdict)
    ax2.set_ylim(0, y2.max()*1.5)
    line2, = ax2.plot(x, y2, marker="*", color="r",
                      label=line_y2label, markersize=markersize, alpha=0.5)
    # ax.legend([line1,line2],["速度","受力"])  # 增加图例的方法 合并图例的方法就是仅使用一个轴的legend()函数。
    # 合并图列
    lns = [*ax.get_lines(), *ax2.get_lines()]
    labs = [l.get_label() for l in lns]
    legend = ax.legend(lns, labs, loc=0)  # 修改图例字体大小 fontsize=16
    ax.set_ylim(y1_lim)
    ax2.set_ylim(y2_lim)
    if is_save:
      fig.savefig(fname=fname,)
      print(f'图片保存为 -> {fname}')

    return fig, ax

  def plot_df(self, df: pd.DataFrame,
              x='vacuum_thick', y='energy',
              marker='o', linestyle='-',
              ylabel='energy',
              xlabel='Vacuum Thick',
              save=False,
              fname='xxx/dos.pdf',
              ax=None,
              fig=None,
              **kwargs,):
    """直接 使用 df 绘图

    Args:
        df (pd.DataFrame): _description_
        x (str, optional): _description_. Defaults to 'vacuum_thick'.
        y (str, optional): _description_. Defaults to 'energy'.
        marker (str, optional): _description_. Defaults to 'o'.
        linestyle (str, optional): _description_. Defaults to '-'.
        ylabel (str, optional): _description_. Defaults to 'energy'.
        xlabel (str, optional): _description_. Defaults to 'Vacuum Thick'.
        save (bool, optional): _description_. Defaults to False.
        fname (str, optional): _description_. Defaults to 'dos.pdf'.
        ax (_type_, optional): _description_. Defaults to None.
        fig (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    if ax is None:
      fig = plt.figure()
      ax = fig.add_subplot()

    ax = df.plot(x=x, y=y,
                 marker=marker,
                 linestyle=linestyle,
                 xlabel=xlabel,
                 ylabel=ylabel,
                 ax=ax,
                 fig=fig,
                 **kwargs,
                 )
    fig = ax.figure
    if save:
      fig.savefig(fname=fname, bbox_inches='tight',)

    return fig, ax

  def plot_df_dos(self, df_dos: pd.DataFrame,
                  name_column_x='energies',
                  name_column_y_list=None,
                  index_column_y_list=[-2, -1],
                  name_line_label_list=None,
                  linestyle_list=None,
                  line_color_list=None,
                  xlim_list=None,
                  ylim_list=None,
                  save=False,
                  fname='dos.pdf',
                  alpha=0.7,
                  fig=None,
                  ax=None,
                  legend_loc='best'):
    """selection: None表示total dos, or 'p(O)','C(p),O(p)','1(p)', 'total(O)','O(total),P(up),S(down)','O(total),P(total), total(P(d)),total(P(p))

    # 给定 name_column_y_list 才会正确显示

    Args:
        df_dos (_type_): _description_
        name_column_x (str, optional): _description_. Defaults to 'energies'.
        name_column_y_list (list, optional): _description_. Defaults to ['O_s', 'O_p'].
        save (bool, optional): _description_. Defaults to False.
        xlim_list (list, optional): _description_. Defaults to [None, None].
        ylim_list (list, optional): _description_. Defaults to [None, None].
        fname (str, optional): _description_. Defaults to 'dos.pdf'.
        alpha (float, optional): _description_. Defaults to 0.7.

    Returns:
        _type_: _description_
    """

    if fig is None and ax is None:
      fig = plt.figure()
      ax = fig.add_subplot()

    if name_column_y_list is None:
      name_column_y_list = df_dos.columns.values[index_column_y_list]
    if name_line_label_list is None:
      name_line_label_list = name_column_y_list
    if line_color_list is None:
      line_color_list = [None]*len(name_column_y_list)
    if linestyle_list is None:
      linestyle_list = [None]*len(name_column_y_list)
    for column, label, color, linstyle in zip(name_column_y_list, name_line_label_list, line_color_list, linestyle_list):
      ax.plot(df_dos[name_column_x], df_dos[column],  label=label,
              color=color, alpha=alpha, linestyle=linstyle)
    ax.set_xlabel('Energy (eV)')
    ax.set_ylabel('DOS (1/eV)')
    if xlim_list is not None:
      ax.set_xlim(left=xlim_list[0], right=xlim_list[1])
    if ylim_list is not None:
      ax.set_ylim(bottom=ylim_list[0], top=ylim_list[1])
    ax.legend(loc=legend_loc)
    # ax.set_ylim(bottom=0)
    # 加入水平线和垂直虚线
    # ax = self.add_vlines_hlines(ax)
    ax = self.add_vlines(ax=ax, x=0,
                         linestyles=':')

    if save:
      fig.savefig(fname=fname, bbox_inches='tight',)
      print(f'文件保存为-> {fname}')
    return fig, ax

  def lines_example(self):
    # fig4 = plt.figure('f2', figsize=(5, 5))  # 图形窗口的名字  可以设置图形窗口的大小
    fig = plt.figure()
    ax = fig.add_subplot()
    n = 20
    x = np.linspace(0, 10, n)  # linspace(-pi, pi, 256,endpoint=True) #保留终点
    y = np.sin(x)

    ax.set_xlabel("x轴", loc='left')
    ax.set_ylabel('|E|', rotation=90)  # 可以旋转ylabel
    ax.set_title("Matplotlib 演示")  # 增加标题
    ax.plot(x, y, linestyle='dotted', color='red', linewidth=1,
            marker='p', markersize=4, mec='black', label='正弦')
    # 还可以通过RGB元组设置颜色：color=(0.1, 0.5, 0.7)
    # 在一个注释中，需要考虑两点：参数xy代表了注释点在哪里，xytext代表了注释文本在哪里。这两个参数都是(a,b)的元组。
    ax.annotate('max value',  # 文本注释
                xy=(1.7, 1),  # 被注释的点的坐标
                xytext=(4, 0.8),  # xytext：注释文本的位置相对于被注释的点的偏移。

                arrowprops=dict(facecolor='black', shrink=0.02),
                # arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
                )
    z = np.cos(x)
    # https://matplotlib.org/2.0.2/api/pyplot_api.html  网页中查找绘图参数
    ax.plot(x, z, label='cos余弦')  # 绘制多条曲线,增加一条plot即可
    # 画网格线,help(matplotlib.pyplot.grid)  # 透明度alpha=0.5
    ax.grid(visible=True, which='major',
            axis='both', alpha=0.5, linestyle="--")
    ax.legend(loc='best',
              # loc用于调整图例的位置可以help(legend)参考，如legend('upper right'), fontsize字体大小, 由于plot中已经加入label关键词，故可以直接加入图例
              fontsize=16)
    # ax.legend(("a","b","c"),loc="center") # plt.legend(("a","b"))还可以这样来设置图例
    # plt.xlim(-pi,pi);ylim(-1,1) #设置取值范围
    # plt.axis([xmin,xmax,ymin,ymax])
    ax.set_xticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi], [r'$-\pi$',
                                                              r'$-\pi/2$', r'$0$', r'$+\pi/2$', r'$+\pi$'])  # latex 公式
    ax.set_yticks([-1, 0, +1], [r'$-1$', r'$0$', r'$+1$'])  # 设置自定义刻度, 与下面两条等价
    # ax.set_xticks([0, 1, 2])
    # ax.set_xticklabels([0, 2, 10])
    # ax.xaxis.set_major_locator(plt.FixedLocator([0, 1, 2]))
    # ax.xaxis.set_major_formatter(plt.FixedFormatter([0, 2, 10]))
    ax.text(0, 0, 'wjl', fontsize=20, alpha=0.5)  # 自定义文本和透明度
    # 保存图片, bbox_inches="tight": 删除空白区域填充, dpi=72:# 以分辨率 72 来保存图片
    # fig.savefig("sin.pdf", bbox_inches='tight', dpi=72)
    ax: Axes3D = plt.gca()
    ax.set_aspect(1)  # 使x,y轴的单位长度相等
    fig: figure.Figure = plt.gcf()
    # fig.set_size_inches(2, 6)  # 设置图形窗口的大小，英寸
    # plt.pause(10)  # 10秒后关闭图形窗口
    pass

  def line2_example(self):
    # 生成数据
    x = np.array([1, 2, 3, 4, 5])
    y = np.array([10, 20, 15, 25, 30])

    # 创建图形和坐标轴对象
    fig, ax = plt.subplots()

    # 绘制折线图
    ax.plot(x, y)

    # 设置X轴刻度位置和标签
    labels = ['A', 'B', 'C', 'D', 'E']
    ax.set_xticks(x)  # 设置刻度位置
    ax.set_xticklabels(labels)  # 设置刻度标签

    # 显示图形
    plt.show()

  def vlines(self):
    """_summary_
    """
    ax: plt.Axes
    # ，你可以使用 ax.get_ylim() 来获取当前 y 轴的范围：
    ymin, ymax = ax.get_ylim()
    # 在 x=0 处绘制垂直线
    ax.vlines(x=0, ymin=ymin, ymax=ymax, colors='r', linestyles='dashed')

    ax.vlines(x=[20, 100], ymin=-2, ymax=2, linestyles='dashed',
              colors='red')  # 画垂线，在x=20，和x=100处,
    # 画垂线，如果要绘制多个点（例如20和100），则必须调用函数两次。它实际上并没有像vlines（）那样让我们指定线型，
    ax.axvline(20, 0.8, 0.5, color='red')
    pass

  def scatter(self, x, y, z,
              marker='o',
              cmap='coolwarm',
              s=300,
              xlabel='X axis',
              ylabel='Y axis',
              alpha=0.8,
              fig=None,
              ax=None,
              is_colorbar=True):
    """绘制散点图

    Args:
        x (_type_): _description_
        y (_type_): _description_
        z (_type_): _description_
        cmap (str, optional): _description_. Defaults to 'coolwarm'.
        s (int, optional): _description_. Defaults to 300.
        xlabel (str, optional): _description_. Defaults to 'X axis'.
        ylabel (str, optional): _description_. Defaults to 'Y axis'.

    Returns: fig,ax 
        _type_: _description_
    """

    if fig is None:
      fig = plt.figure()
      ax = fig.add_subplot()

    # c设置颜色, alpha设置透明度,cmap='rainbow','hot','coolwarm','Greys'
    sc = ax.scatter(x, y, c=z, cmap=cmap, s=s, alpha=alpha, marker=marker)
    # 添加颜色条
    # colorbar:matplotlib.colorbar.Colorbar
    if is_colorbar:
      colorbar = fig.colorbar(mappable=sc, ax=ax)
      colorbar.set_label(label='Color Scale')

    # 添加标签
    ax.set_xlabel(xlabel=xlabel)
    ax.set_ylabel(ylabel=ylabel)
    # ax.title('Scatter plot with color representing Z values')
    # 显示图像
    # fig.show()
    return fig, ax

  def scatter_example(self):
    data = {'a': np.arange(50),
            'b': np.arange(50) + 10 * np.random.randn(50),
            'c': np.random.randint(0, 50, 50),
            'd': np.abs(np.random.randn(50)) * 100}
    # 如果这里提供data关键字参数，则可以使用与这些变量对应的字符串生成绘图。
    cb = plt.scatter('a', 'b', c='c', s='d', data=data)
    plt.colorbar(cb)
    plt.xlabel('entry a')
    plt.ylabel('entry b')
    plt.show()

  def bar(self, x, xlabels, height, width=0.5):
    fig = plt.figure(dpi=300)
    ax = fig.add_subplot()
    ax.bar(x, height=height, width=width,)
    ax.set_xticks(ticks=x, labels=xlabels, rotation=90)
    return fig, ax

  def bar_example(self):
    movie_name = ['雷神3：诸神黄昏', '正义联盟', '东方快车谋杀案', '寻梦环游记',
                  '全球风暴', '降魔传', '追捕', '七十七天', '密战', '狂兽', '其它']
    # 横坐标
    x = range(len(movie_name))
    # 票房数据
    y = [73853, 57767, 22354, 15969, 14839,
         8725, 8716, 8318, 7916, 6764, 52222]

    # 1.创建画布
    fig = plt.figure(figsize=(5, 2), dpi=100)
    ax = fig.add_subplot()
    # 2.绘制柱状图
    ax.bar(x, y, width=0.5, color=[
        'b', 'r', 'g', 'y', 'c', 'm', 'y', 'k', 'c', 'g', 'b'])
    # 2.1b修改x轴的刻度显示
    ax.set_xticks(x, movie_name)

    # 2.2 添加网格显示
    ax.grid(linestyle="--", alpha=0.5)

    # 2.3 添加标题
    ax.set_title("电影票房收入对比")
    # 3.显示图像
    plt.show()

  def histo(self):
    # numpy.histogram()函数将输入数组和 bin 作为两个参数。 bin 数组中的连续元素用作每个 bin 的边界。
    a = np.array([22, 87, 5, 43, 56, 73, 55, 54, 11, 20, 51, 5, 79, 31, 27])
    hist, bins = np.histogram(a, bins=[0, 20, 40, 60, 80, 100], density=True)

    # plt() 函数将包含数据和 bin 数组的数组作为参数，并转换为直方图。
    a = np.array([22, 87, 5, 43, 56, 73, 55, 54, 11, 20, 51, 5, 79, 31, 27])
    plt.hist(a, bins=bins, density=True)
    plt.title("histogram")

  def histo2(self):
    def normfun(x, mu, sigma):
      pdf = np.exp(-((x - mu) ** 2) / (2 * sigma ** 2)) / \
          (sigma * np.sqrt(2 * np.pi))
      return pdf
    length = np.random.normal(loc=10, scale=2, size=10000)

    plt.figure()
    # 绘制数据集的直方图
    plt.hist(length, bins=21, rwidth=0.9, density=True)
    plt.title('Length distribution')
    plt.xlabel('Length')
    plt.ylabel('Probability')

    # 猜测是正态分布，然后画出正态曲线
    mean = length.mean()  # 获得数据集的平均值
    std = length.std()   # 获得数据集的标准差
    # 设定X轴：前两个数字是X轴的起止范围，第三个数字表示步长
    # 步长设定得越小，画出来的正态分布曲线越平滑
    x = np.arange(2, 18, 0.01)
    # 设定Y轴，载入刚才定义的正态分布函数
    y = normfun(x, mean, std)
    # 绘制数据集的正态分布曲线
    plt.plot(x, y)

  def imshow(self, data=np.random.rand(10, 10),
             xticks=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
             yticks=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
             xlabel='X Axis Label',
             ylabel='Y Axis Label',
             label_colorbar='colorbar name',
             xtick_rotation=90,
             save=False,
             fname='imshow.pdf',
             ):
    """矩阵色图
    """

    # 创建图像和轴对象
    fig, ax = plt.subplots()
    # 使用 imshow 绘制图像
    cax = ax.imshow(data, cmap='coolwarm', interpolation='nearest')

    # 设置 x 轴的刻度和标签
    ax: mpl_toolkits.mplot3d.Axes3D
    ax.set_xticks(np.arange(len(xticks)))
    ax.set_xticklabels(xticks, rotation=xtick_rotation)

    # 设置 y 轴的刻度和标签
    ax.set_yticks(np.arange(len(yticks)))
    ax.set_yticklabels(yticks)

    # 设置轴标签
    ax.set_xlabel(xlabel=xlabel)
    ax.set_ylabel(ylabel=ylabel)

    # 添加颜色条
    colorbar = fig.colorbar(cax)
    colorbar.set_label(label=label_colorbar)
    # 显示图像
    # plt.show()
    if save:
      fig.savefig(fname=fname)
    return fig, ax

  def imshow_example(self):
    """矩阵色图
    """

    # 创建示例数据
    data = np.random.rand(10, 10)

    # 创建图像和轴对象
    fig, ax1 = plt.subplots()
    # 使用 imshow 绘制图像
    cax = ax1.imshow(data, cmap='coolwarm', interpolation='nearest')

    # 设置 x 和 y 轴的刻度和标签
    x_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    y_labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

    # 设置 x 轴的刻度和标签
    ax1: mpl_toolkits.mplot3d.Axes3D
    ax1.set_xticks(np.arange(len(x_labels)))
    ax1.set_xticklabels(x_labels)

    # 设置 y 轴的刻度和标签
    ax1.set_yticks(np.arange(len(y_labels)))
    ax1.set_yticklabels(y_labels)

    # 设置轴标签
    ax1.set_xlabel('X Axis Label')
    ax1.set_ylabel('Y Axis Label')

    # 添加颜色条
    fig.colorbar(cax)
    # 显示图像
    return fig

  def matshow(self):

    row_names = ['A', 'B', 'C',
                 'D']

    column_names = ['a', 'b', 'c', 'd']
    np.random.seed(22)
    data = np.random.randint(1, 100, (4, 4))
    df = pd.DataFrame(data, columns=column_names, index=row_names)

    fig: plt.Figure = plt.figure()
    ax: plt.Axes = fig.add_subplot(111)

    cax = ax.matshow(data, interpolation='nearest',
                     cmap='jet')  # 画矩阵色图  cmap='rainbow'
    fig.colorbar(cax)  # 颜色条

    tick_spacing = 1
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))  # 有问题暂时搞不定
    # ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    # ax.xaxis.set_major_locator(plt.MultipleLocator(tick_spacing))  # ? 不懂啊

    # ax.set_xticklabels([''] + list(df.columns))
    # ax.set_yticklabels([''] + list(df.index))
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels('abcd')

    plt.show()

  def pie(self):
    # 饼图
    y = np.array([35, 25, 25, 15])
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.pie(y,
           labels=['A', 'B', 'C', 'D'],  # 设置饼图标签
           colors=["#d5695d", "#5d8ca8", "#65a479", "#a564c9"],  # 设置饼图颜色
           explode=(0, 0.2, 0, 0),  # 第二部分突出显示，值越大，距离中心越远
           autopct='%.2f%%',  # 格式化输出百分比
           )
    ax.set_title("RUNOOB Pie Test")
    plt.show()
    pass

  def insert_fig(self):
    # 嵌入图
    plt.axes([0.1, 0.1, .8, .8])
    x = np.arange(0.1, 0.8, 0.05)
    y = np.sin(x)
    plt.plot(x, y, color='red', linestyle='-', marker='p')
    plt.xticks([])
    plt.yticks([])
    plt.text(0.6, 0.6, 'axes([0.1,0.1,.8,.8])',
             ha='center', va='center', size=20, alpha=.5)
    plt.axes([0.49, 0.15, .3, .3])
    z = np.cos(x)
    plt.plot(x, z, 'r-s')
    plt.xticks([]), plt.yticks([])
    plt.text(0.5, 0.5, 'axes([0.2,0.2,.3,.3])',
             ha='center', va='center', size=16, alpha=.5)
    # plt.savefig("../figures/axes.png",dpi=64)
    pass

  def contourf(self):
    def f(x, y):
      return (1 - x / 2 + x ** 5 + y ** 3) * np.exp(-x ** 2 - y ** 2)

    # 设置网格和数据
    n = 256
    x = np.linspace(-3, 3, n)
    y = np.linspace(-3, 3, n)
    X, Y = np.meshgrid(x, y)

    # 创建一个新的图形
    fig = plt.figure()

    # 添加子图
    ax = fig.add_subplot(111)

    # 绘制等高线填充图，直接在这里设置 colormap
    contourf = ax.contourf(X, Y, f(X, Y), 8, alpha=.75, cmap='jet')

    # 显示颜色条
    fig.colorbar(contourf, ax=ax)

    # 绘制等高线
    contour = ax.contour(X, Y, f(X, Y), 8, colors='black')

    # 设置标题
    ax.set_title('导体表面斜入射的合成波: \n' +
                 # latex 公式
                 r'$2E_m \sin(kz \cos \theta_i ) \cos(k\sin \theta_i x)$')

    # 显示图形
    plt.show()
    return None

  def plot_str_label(self,
                     x='Substrate',
                     y='E$_f$',
                     linelabel='x',
                     marker='o',
                     xlabel='Substrats',
                     ylabel='E$_f$ (eV)',
                     fig=None,
                     ax=None,):
    if fig is None:
      fig = plt.figure()
      ax = fig.add_subplot()

    ax.plot(x, y, label=linelabel, marker=marker)
    # 设置图形的标签和标题
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()

    # 设置 x 轴标签的角度
    plt.xticks(rotation=45, ha='right')
    return fig, ax


class ThreeDimension():
  def __init__(self) -> None:
    """三维图在jupyter中 需要这个  %matplotlib widget  以及安装 conda install ipympl 才可以看旋转结构
    ---
    fig = plt.figure(figsize=(5, 10))  
    ax1 = fig.add_subplot(3, 1, 1)
    assert isinstance(ax1, axes.Axes)  # 由于上一条命令ide并没有真正的运行，所以不知道fig, ax1的对象类型，所以没有补全提示，通过这个声明就可以了
    或者
    ax1 = fig.add_subplot()  # type:axes.Axes
    """
    pass

  def line3d(self):
    n = 30
    x = np.linspace(0, 10, n)
    y = x
    z = np.exp(-y) * np.cos(x)
    # plt.axes(projection='3d'); plt.plot(x, y, z, 'rs-')  # 或者这样
    ax1: Axes3D = plt.axes(projection='3d')
    # ax1.plot(x, y, z)  # ax1.plot3D(x, y, z)
    ax1.set_zlabel('ZZ')
    ax1.set_xlabel('XX')
    ax1.set_ylabel('Y')
    plt.show()
    pass

  def plot_wireframe(self):
    fig = plt.figure()
    ax: Axes3D = fig.add_subplot(111, projection='3d')
    # Grab some test data.
    X, Y, Z = axes3d.get_test_data(0.05)

    # X,Y,Z：输入数据, rstride:行步长, cstride:列步长, rcount:行数上限, ccount:列数上限
    ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)
    plt.show()

  def plot_surface3(self):
    # Make data.
    X = np.arange(-5, 5, 0.25)
    Y = np.arange(-5, 5, 0.25)
    X, Y = np.meshgrid(X, Y)
    R = np.sqrt(X**2 + Y**2)
    Z = np.sin(R)

    fig = plt.figure()
    ax: Axes3D = fig.add_subplot(projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap=matplotlib.cm.coolwarm,
                           linewidth=0, antialiased=False)

    # Customize the z axis.
    ax.set_zlim(-1.01, 1.01)
    ax.zaxis.set_major_locator(plt.LinearLocator(3))
    ax.zaxis.set_major_formatter(plt.FormatStrFormatter('%.02f'))

    # Add a color bar which maps values to colors.
    fig.colorbar(surf, shrink=0.5, aspect=5)

    plt.show()

  def plot_surface4(self):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    # Make data.
    X = np.arange(-5, 5, 0.25)
    xlen = len(X)
    Y = np.arange(-5, 5, 0.25)
    ylen = len(Y)
    X, Y = np.meshgrid(X, Y)
    R = np.sqrt(X**2 + Y**2)
    Z = np.sin(R)

    # Create an empty array of strings with the same shape as the meshgrid, and
    # populate it with two colors in a checkerboard pattern.
    colortuple = ('y', 'b')
    colors = np.empty(X.shape, dtype=str)
    for y in range(ylen):
      for x in range(xlen):
        colors[x, y] = colortuple[(x + y) % len(colortuple)]

    # Plot the surface with face colors taken from the array we made.
    surf = ax.plot_surface(X, Y, Z, facecolors=colors, linewidth=0)

    # Customize the z axis.
    ax.set_zlim(-1, 1)
    ax.w_zaxis.set_major_locator(LinearLocator(6))

    plt.show()
    pass

  def plot_surface(self):
    n = 30
    x = np.linspace(0, 10, n)
    y = x
    X, Y = np.meshgrid(x, y)
    E_tm = 1
    alpha = 1
    k_tx = 1.5
    Z = E_tm * np.exp(-alpha * Y) * np.cos(k_tx * X)
    ax1: Axes3D = plt.axes(projection='3d')
    ax1.plot_surface(X, Y, Z, cmap='jet')
    ax1.contour(X, Y, Z, zdir='z', offset=0, cmap="rainbow")  # 生成z方向投影，投到x-y平面
    ax1.set_xlabel('x轴 (传播方向)')
    ax1.set_ylabel('z')
    ax1.set_zlabel('电场')
    ax1.view_init(60, 35)  # 可以设置视角
    plt.savefig('bmb-表面波.pdf', bbox_inches='tight')
    plt.show()
    pass

  def surface2(self):
    # 定义坐标轴
    fig = plt.figure()
    ax4: mpl_toolkits.mplot3d.Axes3D = fig.add_subplot(projection='3d')

    # 生成三维数据
    xx = np.arange(-5, 5, 0.1)
    yy = np.arange(-5, 5, 0.1)
    X, Y = np.meshgrid(xx, yy)
    Z = np.sin(np.sqrt(X ** 2 + Y ** 2))
    # 作图
    ax4.plot_surface(X, Y, Z, alpha=0.99, cmap='winter')  # 生成表面， alpha 用于控制透明度
    ax4.contour(X, Y, Z, zdir='z', offset=-3,
                cmap="rainbow")  # 生成z方向投影，投到x-y平面
    # ax4.contour(X,Y,Z, zdir='x', offset=-6,cmap="rainbow")  #生成x方向投影，投到y-z平面
    # ax4.contour(X,Y,Z, zdir='y', offset=6,cmap="rainbow")   #生成y方向投影，投到x-z平面
    # 生成y方向投影填充，投到x-z平面，contourf()函数
    ax4.contourf(X, Y, Z, zdir='y', offset=6, cmap="rainbow")
    # 设定显示范围
    ax4.set_xlabel('X')
    ax4.set_xlim(-6, 4)  # 拉开坐标轴范围显示投影
    ax4.set_ylabel('Y')
    ax4.set_ylim(-4, 6)
    ax4.set_zlabel('Z')
    ax4.set_zlim(-3, 3)
    plt.show()
    pass

  def surface_sphere(self):
    # Make data
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = 10 * np.outer(np.cos(u), np.sin(v))
    y = 10 * np.outer(np.sin(u), np.sin(v))
    z = 10 * np.outer(np.ones(np.size(u)), np.cos(v))

    fig = plt.figure()
    ax: Axes3D = fig.add_subplot(111, projection='3d')
    ax.plot_surface(x, y, z, color='b')
    plt.show()
    return

  def bar3d(self, x, y, z,
            dx=None, dy=None,
            color=None,
            xlabel='X axis',
            ylabel='Y axis',
            zlabel='Z axis',
            alpha=1,
            fig=None,
            ax=None,
            save=False,
            fname='bar3d.pdf',
            ):
    """
    x = np.arange(9)*10
    dx = x.max()/x.__len__()
    y = np.arange(9)/10
    dy = y.max()/y.__len__()
    x = x -dx/2
    y = y - dy/2 
    z = np.random.randint(100,200,9)

    Args:
        x (_type_): _description_
        y (_type_): _description_
        z (_type_): _description_
        dx (_type_, optional): _description_. Defaults to None.
        dy (_type_, optional): _description_. Defaults to None.
    """

    if dx is None:
      dx = x.max()/(x.__len__()*1.5)
      dy = y.max()/(y.__len__()*1.5)
    if fig is None:
      fig = plt.figure()
      ax: mpl_toolkits.mplot3d.Axes3D = fig.add_subplot(
          1, 1, 1, projection='3d')  # 或者(111，projection='3d')
    ax.bar3d(x, y, z=0, dx=dx, dy=dy, dz=z, alpha=alpha,
             color=color)
    ax.set_xlabel(xlabel=xlabel)
    ax.set_ylabel(ylabel=ylabel)
    ax.set_zlabel(zlabel=zlabel, rotation=90)

    # 加入文本
    # for x,y,z,index in zip(x_arr,y_arr,z_arr,index_arr):
    #   ax.text3D(x=x,y=y,z=z,s=index, fontdict={'color':'red'})

    # 使用 plt.tight_layout() 或 fig.subplots_adjust() 来自动调整子图参数，使标签不重叠。
    fig.tight_layout()
    # fig.subplots_adjust()
    if save:
      fig.savefig(fname=fname,
                  # bbox_inches='tight',
                  pad_inches=0.35,)
      print(f'fig 存储到-> {fname}')
    return fig, ax

  def bar3d_example(self):
    """
    # 创建二维数据的三维柱状图 : 演示二维数据的柱状图作为三维条形图。  # 官网中文网址： https://www.osgeo.cn/matplotlib/gallery/mplot3d/hist3d.html
    # plt.bar(x,y,width=2,align="center") # 数据，柱子宽度，对齐
    """

    np.random.seed(22)
    # x,y = np.random.rand(2,100) * 4
    x = (np.random.rand(1, 100) * 4)[0]
    y = (np.random.rand(1, 100) * 6)[0]
    hist, xedges, yedges = np.histogram2d(
        x, y, bins=[4, 6], range=[[0, 4], [0, 6]])

    # Construct arrays for the anchor positions of the 16 bars.
    xpos, ypos = np.meshgrid(
        xedges[:-1] + 0.25, yedges[:-1] + 0.25, indexing="ij")
    xpos = xpos.ravel()
    ypos = ypos.ravel()
    zpos = 0

    # Construct arrays with the dimensions for the 16 bars.
    dx = dy = 0.5 * np.ones_like(zpos)
    dz = hist.ravel()

    fig = plt.figure()
    ax: Axes3D = fig.add_subplot(
        1, 1, 1, projection='3d')  # 或者(111，projection='3d')
    ax.bar3d(xpos, ypos, zpos, dx, dy, dz=dz,)
    ax.set_xlabel('X')
    ax.set_ylabel("Y")
    ax.set_zlabel('z')

  def scatter3D(self, x, y, z,
                c=None,
                s=30,
                xlabel='X axis',
                ylabel='Y axis',
                alpha=0.5,
                fig=None,
                ax=None):
    if fig is None:
      fig = plt.figure()
      ax: mpl_toolkits.mplot3d.Axes3D = fig.add_subplot(
          1, 1, 1, projection='3d')

    if c is None:
      c = z
      cmap = 'coolwarm'
    else:
      cmap = None
    sc = ax.scatter3D(xs=x, ys=y, zs=z, s=s, c=c, cmap=cmap,
                      alpha=alpha)

    if cmap is None:
      pass
    else:
      # 添加颜色条
      # colorbar:matplotlib.colorbar.Colorbar
      colorbar = fig.colorbar(mappable=sc, ax=ax)
      colorbar.set_label(label='Color Scale')

    # 添加标签
    ax.set_xlabel(xlabel=xlabel)
    ax.set_ylabel(ylabel=ylabel)
    return fig, ax


class Animate():
  def __init__(self) -> None:
    """jupyter 需要这个  %matplotlib widget  以及安装 conda install ipympl 
    """
    pass

  def funcAnimation(self, fname='z.gif', save=False):
    fig = plt.figure()
    ax = fig.add_subplot()
    # ax.set_xlim(0, np.pi*2)
    # ax.set_ylim(-1.1, 1.1)
    # ax.set_xlabel("时间 (s)")
    # ax.set_ylabel("振幅 (m)")

    x = np.arange(0, 2*np.pi, 0.01)
    line, = ax.plot(x, np.sin(x))  # 注意逗号，这表示返回的是一个元组

    # 定义更新函数
    def update(frame):
      line.set_ydata(np.sin(x + frame / 10.0))  # 更新线条的 y 数据
      return line,  # 注意逗号，这表示返回的是一个元组

    # 创建动画对象 这里frames参数是一个可迭代对象，程序执行时，会依次取出该对象中的元素，然后传递给update函数。
    ani = matplotlib.animation.FuncAnimation(fig, func=update,
                                             frames=np.arange(0, 200), interval=20, blit=True,)
    if save:
      # ani.save('sine_wave.gif', writer='imagemagick', fps=50)
      ani.save(filename=fname)

  def example2(self, fname='z.gif', save=False):
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.set_xlim(0, np.pi*2)
    ax.set_ylim(-1, 1.1)
    ax.set_xlabel("时间 (s)")
    ax.set_ylabel("振幅 (m)")
    x = []
    y = []
    line, = ax.plot(x, y)

    def update(n):
      x.append(n)
      y.append(np.sin(n))
      ax.plot(x, y, color='k')

    # 这里frames参数是一个可迭代对象，程序执行时，会依次取出该对象中的元素，然后传递给update函数。
    ani = matplotlib.animation.FuncAnimation(
        fig=fig, func=update, frames=np.arange(
            0, np.pi * 2, 0.1), repeat=False, interval=100)
    # interval 的单位是毫秒
    if save:
      ani.save(filename=fname)
    return None

  def ex3(self, fname='z.gif', save=False):
    fig, ax = plt.subplots()  # 创建画布和绘图区
    x = np.arange(0, 2 * np.pi, 0.01)  # 生成X轴坐标序列
    line1, = ax.plot(x, np.sin(x))  # 获取折线图对象，逗号不可少，如果没有逗号，得到的是元组
    line2, = ax.plot(x, np.cos(x))  # 获取折线图对象，逗号不可少

    def update(n):  # 动态更新函数
      line1.set_ydata(np.sin(x + n / 10.0))  # 改变线条y的坐标值
      line2.set_ydata(np.cos(x + n / 10.0))  # 改变线条y的坐标值

    # 这里frames参数是一个整数100，此时，程序会自动生成一个range(100)的可迭代对象，然后依次取出每一个数，将其传递给update函数。
    ani = matplotlib.animation.FuncAnimation(
        fig=fig, func=update, frames=100,
        interval=50, blit=False, repeat=False,
    )  # 创建动画效果
    if save:
      ani.save(fname)
    return ani

  def ex4(self,
          xlabel="Iteration",
          ylabel="Cost",
          fname="fit_process.gif",
          save=False,
          ):

    a = np.arange(1, 10)
    b = np.random.randint(1, 100, size=a.size)

    fig, ax = plt.subplots(figsize=(5, 4))
    ax: plt.Axes
    ax.set_xlabel(xlabel=xlabel)
    ax.set_ylabel(ylabel=ylabel)
    x = []
    y = []

    def update(n, a, b):  # 带多个参数
      x.append(a[n])
      y.append(b[n])
      ax.plot(x, y, color='k', marker='*', linestyle='-')

    ani = matplotlib.animation.FuncAnimation(
        fig=fig, func=update, fargs=(a, b), frames=a.size, repeat=False, interval=100)
    if save:
      ani.save(fname)

  def example_animate3D(self, fname='z.gif', save=False):
    fig: plt.Figure = plt.figure()
    ax: mpl_toolkits.mplot3d.Axes3D = fig.add_subplot(
        projection="3d")  # type: plt.mplot3d.Axes3D
    ax.set_xlim(-1, 1)
    ax.set_ylim(-2.1, 2.1)
    ax.set_zlim3d(-5, 5)
    # line = ax.plot3D([], [], [], "ro")
    frames = 100

    x_list = []  # 画出已经出现的点

    def update(frame):  # 这里的frame 就是animation.FuncAnimation参数中frames中的一个，frames可以是整数表示range(frames)
        # x_list = [] # 只画一个点
      step = np.pi * 2 / frames * frame
      x_list.append(step)
      # x_list = list(np.arange(100))
      x_array = np.array(x_list)
      y_array = x_array
      z_array = x_array * np.cos(x_array) + np.abs(np.sin(y_array))
      line = ax.plot3D(np.cos(x_array), np.sin(y_array), z_array, "ro")
      return line  # 这里搞不懂为什么需要返回这个

    anim = matplotlib.animation.FuncAnimation(fig=fig, func=update, frames=frames, init_func=None,
                                              interval=20, blit=True, repeat=False)
    if save:
      anim.save(fname)
    return anim

  def example_Ipython(self):
    r"""
    %matplotlib inline
    """
    import IPython.display

    # fig, ax = plt.subplots(2, 1, figsize=(6, 6), sharex='all',
    #                       gridspec_kw={'hspace': 0, 'wspace': 0})
    fig, ax = plt.subplots()

    def write_frame(x, y):
      ax.plot(x, y, color="b", marker='o')
      IPython.display.clear_output(wait=True)
      IPython.display.display(fig)

    t = []
    x = []
    y = []
    for i in np.linspace(0, 2*np.pi, 50):
      plt.pause(0.1)
      t.append(i)
      x = np.sin(t)
      write_frame(t, x)
    pass


class Features():
  def __init__(self, font_size=12) -> None:
    """figsize 的默认值为(6.4, 4.8)
    """
    self.color_list = ['black', 'red', 'blue', 'orange', 'green',
                       'darkviolet', 'olive', 'plum',  'violet',
                       'darksalmon', 'lightskyblue', 'palevioletred', 'navy', 'deeppink', 'powderblue',
                       'yellowgreen', 'orangered', 'yellow',]
    self.fonts_sets(font_size=font_size)
    self. Learn = Learn()
    self.TwoDimension = TwoDimension()
    self.ThreeDimension = ThreeDimension()
    self.Animate = Animate()
    self.matplotlib = matplotlib
    self.CollegePhysicsBookFigures = CollegePhysicsBookFigures()
    pass

  def fonts_sets(self,
                 font_family='sans-serif',  # 无衬线字体
                 font_sans_serif='HeiTi TC',
                 font_size=12,  # 全局字体
                 ):
    """
    'font.size': 14：全局字体大小设为 14，所以 medium 将对应 14，其他相对大小（large、x-large 等）会根据此值调整。

    字体知识
    在Matplotlib中，font.family 用于指定字体的家族或类型，它可以接受不同的值，来选择不同的字体家族。以下是一些常见的 font.family 值：

    "serif"：衬线字体（有装饰线的字体），通常用于正文文本。常见的如下:
        Times New Roman: 这是一个广泛使用的 Serif 字体，通常在Windows系统上预安装，用于印刷和出版。
        Georgia: 一种在Web设计和打印中广泛使用的 Serif 字体，拥有清晰的设计。
        Garamond: 这是一种古老的 Serif 字体家族，有多个变种，常用于书籍排版。
        Baskerville: Baskerville 是另一个常见的 Serif 字体，以其高质量的打印效果而闻名。
    "sans-serif"：无衬线字体（无装饰线的字体），通常用于标签、标题等元素。常见的如下:
        Helvetica (Arial): Helvetica 是一种广泛使用的 Sans-serif 字体，Arial 是 Windows 上的类似替代字体。它们都具有现代、清晰的设计，适用于各种应用。
        Verdana: Verdana 是一种专门设计用于屏幕显示的 Sans-serif 字体，非常易于阅读，特别是在小字号下。
        Calibri: Calibri 是微软 Office 套件的默认字体之一，具有现代感和清晰的设计。
        Arial: Arial 与 Helvetica 非常相似，是 Windows 上的常见字体选择，用于各种文档。
        Gill Sans: Gill Sans 是一种古典的 Sans-serif 字体，广泛用于标志和品牌设计。
    "monospace"：等宽字体，所有字符都具有相同的宽度。常用的如下:
        Courier New: 这是一个常见的等宽字体，通常在Windows系统上预安装。它的字母和符号都有相同的宽度。
        Consolas: 这也是一种Windows系统上常见的等宽字体，它在程序员和开发人员中非常受欢迎。
        Monaco: 这是苹果 macOS 操作系统上的默认等宽字体，也常用于编程。
        Inconsolata: 一个免费的开源等宽字体，设计用于提供清晰的编程体验。
        DejaVu Sans Mono: 一个开源的等宽字体，包含了广泛的Unicode字符。
        Menlo: 一个苹果 macOS 系统上的等宽字体，也用于编程。
    "cursive"：草书字体，具有手写风格的字体。
    "fantasy"：奇幻字体，具有装饰性的字体。

    # 添加中文支持 'Arial Unicode MS', 'Songti SC', 'Heiti TC','Source Han Sans SC'
    plt.rcParams['font.family'] = 'Arial Unicode MS'

    --- 
    import matplotlib.font_manager
    # 查看可用字体
    # print([f.name for f in matplotlib.font_manager.fontManager.ttflist])

    # 设置字体
    plt.rcParams['font.family'] = 'monospace'  # 先设置字体族
    plt.rcParams['font.monospace'] = 'Courier New'  # 再设置字体族中的字体

    # 设置宋体
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['axes.unicode_minus'] = False
    # plt.rcParams['font.serif'] = ['Songti SC',
    #                               '/System/Library/Fonts/Supplemental/Songti.ttc']
    plt.rcParams['font.serif'] = 'Songti SC'  # STFangsong # STSong
    # 设置黑体
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'HeiTi TC'

    # plt.rcParams['font.family'] = 'Arial Unicode MS'

    ---
    * 常见的字符串值：
    "xx-small"：非常小的字体
    "x-small"：较小的字体
    "small"：小字体
    "medium"：中等字体（通常是默认字体大小）
    "large"：大字体
    "x-large"：更大的字体
    "xx-large"：非常大的字体
    """

    # 设置字体
    pars_font = {'font.family': font_family,
                 'font.sans-serif': font_sans_serif,
                 'axes.unicode_minus': False,  # 去掉使用中文时的警告
                 # "figure.figsize": (6.4, 4.8), # 默认值
                 "savefig.bbox": "tight",  # 使图形的外面的白色边框尽可能小
                 }
    plt.rcParams.update(pars_font)

    # 字体大小的全局设置
    # 字体大小
    params_fontsize = {'font.size': font_size,      # 全局字体大小
                       'figure.titlesize': 'x-large',  # 图的标题字体
                       'axes.titlesize': 'large',  # 16 坐标轴标题字体
                       'axes.labelsize': 'medium',  # 14 坐标轴标签字体
                       'legend.fontsize': 'medium',  # 14 图例字体
                       'xtick.labelsize': 'medium',  # 12 X轴刻度字体
                       'ytick.labelsize': 'medium',  # 12 Y轴刻度字体
                       }

    plt.rcParams.update(params_fontsize)
    pass

  def paras_set_separately(self,
                           tick_labelsize=16,
                           legend_fontsize=16,
                           axes_labelsize=18,
                           axes_titlesize=18,
                           figure_titlesize=20,
                           ):
    """单独设置图形参数时的设置
    ---
    图例标题的理解, 画出下面的图就明白了
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    mpl.rcParams['legend.title_fontsize'] = 20
    plt.plot([0, 1], [0, 1], label='Line A')
    plt.plot([0, 1], [1, 0], label='Line B') # 图例
    legend = plt.legend(title="Legend Title") # 图例标题
    plt.show()
    """
    # 坐标轴标签字体大小
    matplotlib.rcParams['axes.labelsize'] = axes_labelsize
    # 坐标轴刻度字体大小
    matplotlib.rcParams['xtick.labelsize'] = tick_labelsize
    matplotlib.rcParams['ytick.labelsize'] = tick_labelsize
    # 图例相关
    matplotlib.rcParams['legend.fontsize'] = legend_fontsize
    matplotlib.rcParams['legend.title_fontsize'] = legend_fontsize
    # 标题相关
    matplotlib.rcParams['figure.titlesize'] = figure_titlesize
    matplotlib.rcParams['axes.titlesize'] = axes_titlesize

    return None

  def get_color(self, name_cmap='rainbow', n_resample=10,
                alpha=0.5, color_idx=1, to_hex=True):
    """colormap 色图的设置, 从色图中选择10种颜色, 并控制透明度 alpha=0.3
    """
    import matplotlib
    import matplotlib.colors
    colors = matplotlib.colormaps.get_cmap(
        name_cmap).resampled(n_resample)  # 获得色图并映射为10种
    # 选取第一种颜色 包含透明度
    color = colors(color_idx, alpha=alpha)
    color_16 = matplotlib.colors.to_hex(keep_alpha=True, c=color)
    # 测试
    # plt.plot(0, 1, marker='o', markersize=20, color=color)

    return color_16 if to_hex else color

  def get_color_list(self, num_color=10,
                     alpha=0.5,
                     name_cmap='rainbow',
                     to_hex=True):
    """从 cmap: rainbow 获取10 种颜色
    """
    color_list = [self.get_color(
        name_cmap=name_cmap, n_resample=num_color, alpha=alpha,
        color_idx=i, to_hex=to_hex) for i in range(num_color)]
    return color_list

  def savefig(self, fig: matplotlib.figure.Figure,
              fname='xxx.pdf',
              pad_inches=None,  # 0.35,
              ):
    """* 对于 png 可以如下设置
      - fig.savefig(f'cohp.png', dpi=500, bbox_inches="tight", transparent=True)

    Args:
        fig (matplotlib.figure.Figure): _description_
        save (_type_): _description_
        fname (_type_): _description_
        pad_inches (float, optional): _description_. Defaults to 0.35.
    """

    fig.savefig(fname=fname,
                bbox_inches='tight',
                pad_inches=pad_inches)
    # 对于 png 可以如下设置
    # fig.savefig(f'cohp.png', dpi=500, bbox_inches="tight", transparent=True)

    print(f'fig 存储到-> {fname}')
    return None

  def annotate_sets(self, ax: matplotlib.axes.Axes):
    """可以将文本加在右上角

    Args:
        ax (matplotlib.axes.Axes): _description_
    """
    fig = plt.figure()
    ax = fig.add_subplot()

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    ax.annotate(text=f'-ICOHP:',
                xy=(xlim[1], ylim[1]),  # 右上角坐标
                xytext=(-10, -50),      # 向左下方偏移10个单位
                textcoords='offset points',  # 使用偏移量作为坐标系统 单位是点数（points），1 个点等于 1/72 英寸（约 0.353 毫米）。
                ha='right',             # 水平右对齐
                va='bottom',               # 垂直顶部对齐
                color='gray',
                )
    ax.annotate(text=f'icoph的值:',
                xy=(xlim[1], ylim[1]),  # 右上角坐标
                xytext=(-10, -50),      # 向左下方偏移10个单位
                textcoords='offset points',  # 使用偏移量作为坐标系统 单位是点数（points），1 个点等于 1/72 英寸（约 0.353 毫米）。
                ha='right',             # 水平右对齐
                va='top',               # 垂直顶部对齐
                color='gray',
                )
    return ax

  def example_show(self):
    """_summary_
    """
    # %matplotlib widget
    from soft_learn_project.matplotlib_learn import matplotlibLearn
    import importlib
    importlib.reload(matplotlibLearn)

    matplotlibLearn.Features().TwoDimension.lines_example()
    matplotlibLearn.Features().TwoDimension.imshow_example()
    matplotlibLearn.Features().TwoDimension.bar_example()
    matplotlibLearn.Features().TwoDimension.pie()
    matplotlibLearn.Features().TwoDimension.histo2()
    matplotlibLearn.Features().TwoDimension.insert_fig()
    matplotlibLearn.Features().TwoDimension.contourf()
    matplotlibLearn.Features().ThreeDimension.surface2()
    matplotlibLearn.Features().ThreeDimension.bar3d_example()
    matplotlibLearn.Features().Animate.example2()
    matplotlibLearn.Features().Animate.example_animate3D()
