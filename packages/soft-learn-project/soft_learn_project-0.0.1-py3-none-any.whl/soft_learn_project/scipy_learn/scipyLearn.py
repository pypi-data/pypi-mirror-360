import scipy.integrate
import scipy.interpolate
from scipy.optimize import curve_fit
from scipy.stats import binom, hypergeom
import matplotlib.pyplot as plt
from scipy import optimize
import scipy
from scipy import constants  # scipy 的常量模块
import scipy.optimize
import numpy as np
import scipy.stats
from py_package_learn.functools_learn import functoolsLearn


class Learn():
  def __init__(self) -> None:
    """# python在科学计算领域有三个非常受欢迎库，numpy、SciPy、matplotlib。numpy是一个高性能的多维数组的计算库，SciPy是构建在numpy的基础之上的，它提供了许多的操作numpy的数组的函数。
    # SciPy是一款方便、易于使用、专为科学和工程设计的python工具包，它包括了统计、优化、整合以及线性代数模块、傅里叶变换、信号和图像图例，常微分方差的求解等，
    # 下面就简单的介绍一下SciPy在图像处理方面的应用，如果专业做图像处理当然还是建议使用opencv。

    # 教程： https://docs.scipy.org/doc/scipy/tutorial/index.html
    SciPy 是一个开源的 Python 算法库和数学工具包。
    SciPy 包含的模块有最优化、线性代数、积分、插值、特殊函数、快速傅里叶变换、信号处理和图像处理、常微分方程求解和其他科学与工程中常用的计算。

    print(scipy.__version__)  # 查看 scipy 库的版本号
    print(dir(constants))
    print(constants.g)  # 查看重力加速度
    print(constants.zero_Celsius)
    """
    pass

  def install(self):
    """安装
    python3 -m pip install -U scipy
    """
    pass

  def deal_array(self):
      # SciPy Matlab 数组   scipy.io 模块提供了很多函数来处理 Matlab 的数组。
    # savemat() 方法可以导出 Matlab 格式的数据。
    """
    arr = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9,])
    # 导出  dict - 包含数据的字典。 # 保存了一个名为 "arr.mat" 的文件。
    sio.savemat('arr.mat', {"vec": arr})
    # 导入 Matlab 格式数据, 不加这个参数导入的数据多了一个维度
    mydata = sio.loadmat('arr.mat', squeeze_me=True)
    print(mydata)
    print(mydata['vec'])
    # """
    pass


class Optimize(metaclass=functoolsLearn.AutoDecorateMeta):
  """使用 scipy.optimize 中的方法进行优化
  1. 需要建立 cost 或者称为目标函数
  2. 建立边界条件
  """

  def __init__(self) -> None:
    """SciPy 优化器 optimize 模块提供了常用的最优化算法函数实现，我们可以直接调用这些函数完成我们的优化问题，比如查找函数的最小值或方程的根等。
    使用 scipy.optimize 中的方法进行优化
    1. 需要建立 cost 或者称为目标函数
    2. 建立边界条件

    """
    self.optimize_method = [
        'minimize', 'differential_evolution', 'dual_annealing', 'basinhopping']
    pass

  def get_data(self, df_surface, xdata_name=['energy_list', 'temperature_list'], ydata_name='variance_list'):
    import torch
    # 获取数据
    xdata = torch.tensor(df_surface[xdata_name].values).float()
    ydata = torch.tensor(df_surface[ydata_name].values).float().reshape(-1, )
    return xdata, ydata

  def get_residual_cost(self, pars, xdata, ydata, label='cost'):

    def func(xdata, pars):
      # 定义拟合函数的形式
      import torch
      x, y = torch.split(xdata, 1, dim=1)
      a, b, c, d, m, n, p = pars
      z = (a / (1 + torch.exp(-b * (x - c))) + d) * (m * torch.exp(n * y) + p)
      return z.reshape(-1, )

    ydata_predict = func(xdata, pars)
    residual = (ydata - ydata_predict) / ydata
    if label == 'residual':
      return residual
    elif label == 'cost':
      cost = (residual**2).sum() / len(residual)
      return np.array(cost)

  def get_bounds(self, pars, ratio=0.2):
    # 设置优化参数的边界, 许多优化方法都必须提供边界
    # [v - abs(v) * ratio for v in pars]
    bounds_left = pars - abs(pars * ratio)
    # [v + abs(v) * ratio for v in pars]
    bounds_right = pars + abs(pars * ratio)
    # bounds = zip(bounds_left, bounds_right)
    bounds = optimize.Bounds(
        lb=bounds_left, ub=bounds_right, keep_feasible=False)
    return bounds

  def optimizefit(self, objective_function, pars, args_tuple, bounds, optimize_method='differential_evolution'):
    """_summary_

    Args:
        objective_function (_type_): _description_
        pars (_type_): _description_
        args_tuple (_type_): _description_
        bounds (_type_): _description_
        optimize_method (str, optional): _description_. Defaults to 'differential_evolution'.

    Returns: result
        _type_: _description_
    """
    if optimize_method == 'minimize':
      result = optimize.minimize(
          fun=objective_function, x0=pars, args=args_tuple, bounds=bounds)
    elif optimize_method == 'differential_evolution':
      result = optimize.differential_evolution(
          func=objective_function,
          bounds=bounds,
          args=args_tuple,
          updating='immediate',
          # x0=pars
      )
    elif optimize_method == 'dual_annealing':
      result = optimize.dual_annealing(func=objective_function,
                                       bounds=bounds,  # 必须要提供
                                       no_local_search=False,
                                       minimizer_kwargs={'tol': 1e-11,
                                                         'method': 'L-BFGS-B',  # 'BFGS',
                                                         #  'options': {'maxiter': 10,
                                                         #              'disp': False,
                                                         #              },
                                                         },
                                       x0=pars,
                                       args=args_tuple,
                                       )
    elif optimize_method == 'basinhopping':
      result = optimize.basinhopping(
          func=objective_function,
          x0=pars,
          #  niter=50,
          minimizer_kwargs={
              "method": "L-BFGS-B",
              'args': args_tuple,
              'bounds': bounds,  # 可以不要, 不设置边界可能会导致S为0,从而势文件出现nan
          },
          stepsize=0.5,
      )
    else:
      raise Exception('optimize_method 参数名错误!')
    # result.fun, result.x, result.success
    return result

  def example(self, ):
    import torch
    pars = torch.tensor([9.6857e+01, 1.4246e-01, 6.3954e+01, -
                        4.3065e-02, 2.1943e+02, -2.6635e-03, 9.1935e+01])
    bounds = self.get_bounds(pars, ratio=4)
    xdata, ydata = self.get_data()
    args_tuple = (xdata, ydata)

    result = self.optimizefit(objective_function=self.get_residual_cost,
                              pars=pars,
                              args_tuple=args_tuple,
                              bounds=bounds,
                              optimize_method='differential_evolution')
    return result

  def curve_fit_1D(self,
                   x_arr=np.array([1, 2, 3, 4, 5, 6, 7, 8, 9]),
                   y_arr=np.array([1, 4, 9, 16, 25, 36, 49, 64, 81]),
                   func=None
                   ):
    """有空参阅from sci_research import function_fit

    Args:
        x_arr (_type_, optional): _description_. Defaults to np.array([1, 2, 3, 4, 5, 6, 7, 8, 9]).
        y_arr (_type_, optional): _description_. Defaults to np.array([1, 4, 9, 16, 25, 36, 49, 64, 81]).

    Returns:
        _type_: _description_
    """

    # 定义拟合函数形式，这里是二次函数
    if func is None:
      def func(x, a, b, c):
        return a * x**2 + b * x + c

    # 使用curve_fit进行拟合
    popt, pcov = scipy.optimize.curve_fit(func, x_arr, y_arr)

    # 输出拟合参数
    print(f'Fitted parameters: {popt}')
    # 生成拟合曲线
    x_fit = np.linspace(min(x_arr), max(x_arr), 100)
    y_fit = func(x_fit, *popt)
    return x_fit, y_fit

  def curve_fit_2D(self, features,
                   target,
                   model=None):
    """
    通过给定函数拟合, 使用curve_fit, 用最小二乘的方式去逼近拟合, 求出函数的各项系数

    Args:
        x_data (_type_): _description_
        y_data (_type_): _description_
        z_data (_type_): _description_

    Returns: popt
        _type_: _description_
    """

    # 定义一个具有两个自变量的模型函数
    if model is None:
      def model(features, a, b, c, d, e):
        x, y = features
        return a * x**2 + b * y**2 + c*x + d*y + e
    else:
      model = model
    # 使用 curve_fit 拟合数据
    popt, pcov = scipy.optimize.curve_fit(
        f=model, xdata=features, ydata=target)
    print(f'拟合参数为{popt}')
    return popt

  def curve_fit_2D_example(self,):

    # 定义一个具有两个自变量的模型函数
    def model(features, a, b, c, d, e):
      x, y = features
      return a * x**2 + b * y**2 + c*x + d*y + e

    # 生成一些示例数据, x_data,y_data 不要具有线性关系否则出问题
    x_data = np.random.uniform(0, 10, 100)
    y_data = np.random.uniform(10, 20, 100)
    z_data = model((x_data, y_data), 1.0, 2.0, 3.0, 4, 5)
    # 加入噪声
    z_data = z_data + 0.1 * np.random.normal(size=x_data.size)
    popt = self.curve_fit_2D(features=[x_data, y_data],
                             target=z_data,
                             model=model)

    # 输出拟合参数
    print("拟合参数:", popt)

    pass

  def root(self):
    """查找 x + cos(x) 方程的根:
    """
    def eqn(x):
      return x + np.cos(x)

    myroot = optimize.root(eqn, 0)  # fun - 表示方程的函数。x0 - 根的初始猜测。
    print(myroot.x)  # 查看根
    # print(myroot)  # 查看更多信息
    return

  def minimize_modu(self):
    # 最小化函数  scipy.optimize.minimize() 函数来最小化函数。
    # minimize() 函接受以下几个参数： fun - 要优化的函数 x0 - 初始猜测值  method - 要使用的方法名称，值可以是：'CG'，'BFGS'... callback - 每次优化迭代后调用的函数。 options - 定义其他参数的字典：
    # 详细解释查看scipy_learn.ipynb
    """
    def eqn(x):
        return x ** 2 + x + 2

    mymin = optimize.minimize(eqn, 0)  # , method='BFGS')
    print(mymin)
    # """
    pass

  def calcu_reduced_chi(self, x, y, fit_func):
    """计算缩减卡方值
    作用: 检验的拟合质量, reduced_chi越小拟合函数越好

    Args:
        x (_type_): _description_
        y (_type_): _description_
        fit_func (_type_): _description_

    Returns:
        _type_: _description_
    """

    # 将模型拟合到数据
    popt, _ = optimize.curve_fit(fit_func, x, y)
    # 计算残差
    Observe = y
    Expect = fit_func(x, *popt)
    residuals = Observe - Expect
    # 计算卡方值
    chi_squared = np.sum(residuals**2/Expect)
    # 计算拟合的自由度（DOF）：
    dof = len(x) - len(popt)
    # 规约卡方（Reduced Chi-Squared
    # 计算缩减卡方值
    reduced_chi_squared = chi_squared / dof
    data = {'chi_squared': chi_squared,
            'dof': dof,
            'reduced_chi_squared': reduced_chi_squared}
    return data


class Stats():
  def __init__(self) -> None:
    pass

  def distribution_binom(self,
                         n_trials=20,  # 试验次数
                         p_success=0.5,  # 每次成功的概率
                         ):
    """每次实验是独立的, 每次成功的概率为 p, 失败为1-p, n 次实验出现k 次的概率为
    P(X=k)=C_n^k * p^k * (1-p)^(n-k)

    Args:
        n_trials (int, optional): _description_. Defaults to 20.

    Returns:
        _type_: _description_
    """

    # 生成二项分布和超几何分布的样本数据
    x_binom = np.arange(0, n_trials+1)
    y_binom = scipy.stats.binom.pmf(x_binom, n_trials, p_success)

    # 画图
    plt.figure(figsize=(10, 5))
    # 画二项分布
    plt.bar(x_binom, y_binom, color='blue', alpha=0.7)
    plt.title(f'Binomial Distribution (n={n_trials}, p={p_success:.2f})')
    plt.xlabel('Number of Successes')
    plt.ylabel('Probability')
    plt.grid(True)

    return y_binom

  def distribution_hypergeom(self, N_population=500,  # 总体大小
                             M_success=100,  # 次品数量
                             n_sample=15,  # 抽样次数
                             ):
    """N件产品, M件次品, 从中抽取n件产品(不放回地抽样), 次品为x件的概率
    P(x) = C_m^x * C_{N-M}^{n-x} / C_N^n

    X ~ H(N,M,n) # 读作 X服从 参数为N,M,n的超几何分布
    # 设置参数
    N_population = 500  # 总体大小
    M_success = 10  # 次品数量
    n_sample = 15  # 抽样次数

    Args:
        N_population (int, optional): _description_. Defaults to 500.
    """

    # 生成超几何分布的样本数据
    x_hypergeom = np.arange(0, n_sample)
    # N件产品, M 件次品, 从中抽取n 件样本, 次品 数量为 x_hypergeom 的概率
    y_hypergeom = scipy.stats.hypergeom.pmf(
        x_hypergeom, N_population, M_success, n_sample)

    # 画图
    plt.figure(figsize=(10, 5))
    # 画超几何分布
    plt.bar(x_hypergeom, y_hypergeom, color='green', alpha=0.7)
    plt.title(
        f'Hypergeometric Distribution (N={N_population}, M={M_success}, n={n_sample})')
    plt.xlabel('Number of Successes in Sample')
    plt.ylabel('Probability')
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    return y_hypergeom

  def distribution_multinomial(self, N=4, M=2):
    """多项式分布函数  举例: N 个小球 等概率放在M个格子里面
    M=2 时 就是二项式分布

    Returns:
        _type_: _description_
    """

    # 生成每个盒子放置小球的概率，这里假设是均匀分布
    # M = 5 时, [1/M] * M= [0.2, 0.2, 0.2, 0.2, 0.2]
    probabilities = [1/M] * M
    # 生成多项式分布的随机变量
    rv = scipy.stats.multinomial(N, probabilities)
    # 生成随机样本，表示每个盒子放置的小球数量
    ball_counts = rv.rvs()

    print("每个盒子放置的小球数量:", ball_counts)
    pass


class Interpolate():
  def __init__(self) -> None:
    pass

  def interpolate_1d(self):
    # 一维插值
    # from scipy.interpolate import UnivariateSpline, Rbf

    xs = np.arange(0, 10, 1)
    ys = np.sin(xs)  # * np.exp(xs)
    interp_func = scipy.interpolate.interp1d(
        xs, ys, kind='cubic')  # 插值方法： 'linear', 'cubic', 'quintic'
    newarr = interp_func(np.arange(2.1, 5, 0.1))
    print(newarr)

    fig, ax = plt.subplots()
    ax.plot(xs, ys, 'ro:')
    nx = np.arange(2.1, 5, 0.1)
    ny = newarr
    ax.plot(nx, ny, 'k^')
    plt.pause(5)

    pass

  def interpolate_2d(self):
    #  二维插值
    """
    import numpy as np
    from scipy import interpolate
    import pylab as pl
    import matplotlib as mpl


    def func(x, y):
        return (x + y) * np.exp(-5.0 * (x ** 2 + y ** 2))


    # X-Y轴分为15*15的网格
    y,x = np.mgrid[-1:1:5j, -1:1:10j]  # a:b:c c为实数表示间隔,不包含b；c为复数(cj)表示插入点数，包含b
    # 或者用如下三条
    # x = np.linspace(-1, 1, 5)
    # y = np.linspace(-1, 1, 10)
    # x,y = np.meshgrid(x, y)

    fvals = func(x, y)  # 计算每个网格点上的函数值 15*15的值
    print(len(fvals[0]))

    # 三次样条二维插值
    newfunc = interpolate.interp2d(x, y, fvals, kind='cubic')

    # 计算100*100的网格上的插值
    xnew = np.linspace(-1, 1, 100)  # x
    ynew = np.linspace(-1, 1, 100)  # y
    fnew = newfunc(xnew, ynew)  # 仅仅是y值 100*100的值

    # 绘图
    # 为了更明显地比较插值前后的区别，使用关键字参数interpolation='nearest'
    # 关闭imshow()内置的插值运算。
    pl.subplot(121)
    im1 = pl.imshow(fvals, extent=[-1, 1, -1, 1], cmap=mpl.cm.hot,
                    interpolation='nearest', origin="lower")  # pl.cm.jet
    # extent=[-1,1,-1,1]为x,y范围 favals为
    pl.colorbar(im1)

    pl.subplot(122)
    im2 = pl.imshow(fnew, extent=[-1, 1, -1, 1], cmap=mpl.cm.hot,
                    interpolation='nearest', origin="lower")
    pl.colorbar(im2)
    pl.show()
    # """

    # 二维插值的三维展示方法
    """
    import numpy as np
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib as mpl
    from scipy import interpolate
    import matplotlib.cm as cm
    import matplotlib.pyplot as plt


    def func(x, y):
        return (x + y) * np.exp(-5.0 * (x ** 2 + y ** 2))


    # X-Y轴分为20*20的网格
    x = np.linspace(-1, 1, 20)
    y = np.linspace(-1, 1, 20)
    x, y = np.meshgrid(x, y)  # 20*20的网格数据

    fvals = func(x, y)  # 计算每个网格点上的函数值 15*15的值

    fig = plt.figure(figsize=(9, 6))
    # Draw sub-graph1
    ax: Axes3D = plt.subplot(1, 2, 1, projection='3d')
    surf = ax.plot_surface(x, y, fvals, rstride=2, cstride=2,
                           cmap=cm.coolwarm, linewidth=0.5, antialiased=True)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('f(x, y)')
    plt.colorbar(surf, shrink=0.5, aspect=5)  # 标注

    # 二维插值
    newfunc = interpolate.interp2d(x, y, fvals, kind='cubic')  # newfunc为一个函数

    # 计算100*100的网格上的插值
    xnew = np.linspace(-1, 1, 100)  # x
    ynew = np.linspace(-1, 1, 100)  # y
    fnew = newfunc(xnew, ynew)  # 仅仅是y值 100*100的值 np.shape(fnew) is 100*100
    xnew, ynew = np.meshgrid(xnew, ynew)
    ax2 = plt.subplot(1, 2, 2, projection='3d')
    surf2 = ax2.plot_surface(xnew, ynew, fnew, rstride=2, cstride=2,
                             cmap=cm.coolwarm, linewidth=0.5, antialiased=True)
    ax2.set_xlabel('xnew')
    ax2.set_ylabel('ynew')
    ax2.set_zlabel('fnew(x, y)')
    plt.colorbar(surf2, shrink=0.5, aspect=5)  # 标注
    plt.show()
    # """
    pass


class Special():
  def __init__(self) -> None:
    pass

  def special_modu(self):
    """排列和组合
    """
    from scipy import special
    perm = special.perm(4, 2)  # 排列数
    comb = special.comb(4, 2)  # 组合数

    # 将N个气体分子放在两个格子中微观状态数对应的概率
    def comb(N):
      p_array = special.comb(N, range(N+1))/2**N
      return p_array

    plt.plot(comb(100), marker='o')  # 这就是一个二项分布
    pass


class Constants():
  def __init__(self) -> None:
    pass

  def use(self):
    """SciPy 常量模块 constants 提供了许多内置的数学常数
    constants.Boltzmann
    """
    return None


class Features():
  def __init__(self) -> None:
    self.Learn = Learn()
    self.Optimize = Optimize()
    self.Stats = Stats()
    self.Interpolate = Interpolate()
    self.Special = Special()
    self.Constants = Constants()
    pass
