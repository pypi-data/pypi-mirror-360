import matplotlib.pyplot as plt
import sympy
import numpy
import sympy as sp


class SympyLearn():
  def __init__(self) -> None:
    sympy.init_printing(use_unicode=True)  # 指定结果用unicode字符打印出来。
    # 设置字体, 用以显示中文
    from py_package_learn.matplotlib_learn import matplotlibLearn
    matplotlibLearn.Features().fonts_sets(font_sans_serif='SongTi SC')
    pass

  def install(self):
    string = """安装:
    conda install sympy
    """
    pass

  def define_symbols(self):
    # 定义符号变量 sympy.symbols()
    m = sympy.Symbol("m")  # 只能定义一个，没啥用
    # 定义多个变量
    x, y, z = sympy.symbols('x,y,z')
    m, n, p = sympy.var("m,n,p")
    # 向量
    var_x = sympy.symbols("x_1:5")
    print(var_x[0])
    # 数学符合补充
    # 虚数单位i
    sympy.I
    # 自然对数底 e
    sympy.E
    # 无穷大
    sympy.oo
    # 求n次方根
    sympy.root(8, 3)
    # 求对数
    sympy.log(1024, 2)
    # 求阶乘
    sympy.factorial(4)
    pass

  def subs(self):
    x, y, z = sympy.symbols("x,y,z")
    expr: sympy.Expr = sympy.exp(sympy.cos(x)) + 1
    # 替换: subs()方法
    expr.subs(x, 0)

    expr = x**3 + 4*x*y - z
    expr.subs([(x, 2), (y, 4), (z, 5)])

    # 变量替换
    t = sympy.symbols("t")
    exp_1 = sympy.exp(t) + 1
    exp_2 = sympy.cos(x)
    exp_1.subs(t, exp_2)

  def sympify(self):
    x = sympy.symbols('x')
    # 字符串转化为表达式 sympy.sympify()
    str_expr = "x**2 + 2*x +1"
    expr = sympy.sympify(str_expr)
    # expr = sympy.simplify(str_expr) # 都可以？
    num = expr.subs(x, 2)
    num
    # 要获取表达式的字符串形式，则使用str(expr)
    str(expr)
    expr = sympy.Integral(sympy.sqrt(1/x), x)
    str(expr)
    sympy.srepr(expr)
    # 将SymPy表达式转换为可进行数值计算的表达式
    # 最简单方法是使用lambdify函数
    a = numpy.arange(10)
    expr = sympy.sin(x)
    f = sympy.lambdify(x, expr, modules="numpy")
    f(a)
    # 使用subs flag将替换传递给evalf更有效，数值上更稳定，它需要一个符号字典：点对（ point pairs）
    expr.evalf(n=15, subs={x: 2.4})  # 可以指定精度
    expr.subs(x, 2.4)  # 不能指定精度

    # 计算机二进制计算的误差
    # sympy.evalf(chop=True)
    expr = sympy.sin(1)**2 + sympy.cos(1)**2 - 1
    expr.evalf(chop=True)  # 通过将chop设置为True来自行删除小于所需精度的舍入误差

    pass

  def simplify(self):
    # 注意区别
    # * sympy.simplify()  #化简
    # * sympy.sympify() # 转换字符串
    x, y, z = sympy.symbols("x,y,z")
    expr = (x**3 + x**2 - x - 1)/(x**2 + 2*x + 1)
    sympy.simplify(expr)
    # 将字符表达式转换为LaTeX代码
    expr = sympy.Integral(sympy.cos(x)**2, (x, 0, sympy.pi))
    sympy.latex(expr)
    # 构造有理数
    sympy.Rational(1, 2)

    # 有理分式部分分式分解 aprt()
    expr = (x**3 - x**2 + 2*x + 1)/(x**2+x)
    expr.apart()

  def expand(self, expr,):
    """ 它会尝试将一个数学表达式展开成它的最简形式或标准形式，比如乘法展开、三角函数展开、多项式展开等。
    a, b = sympy.symbols('a,b')
    expr = sympy.cos(a+b)
    """
    result = sympy.expand(e=expr, trig=True, log=True,)
    return result

  def plot(self):
    x = sympy.symbols('x')
    expr = -sympy.sqrt(x)
    p = sympy.plot(expr, (x, 0, 10),
                   title='中文标题',
                   xlabel="X轴标签",
                   label='my legend',
                   size=(4, 3),  # 设置大小
                   legend=True)
    #  保存图形
    # p.save('x.pdf')

    #
    a, b, c, x, y, z = sympy.symbols('a,b,c,x,y,z')
    p = sympy.plot((x**2, (x, -6, 6)), (x, (x, -5, 5)), legend=True)
    sympy.plot(x, x**2, x**3, (x, -5, 5), )
    #
    x = sympy.symbols('x')
    p1 = sympy.plot(sympy.sin(x), (x, -5, 5),
                    show=False, label='1/v'
                    )
    p2 = sympy.plot(2*sympy.sin(x), (x, -5, 5),
                    show=False, label='2/V'
                    )
    p1.extend(p2)  # 将两个图形对象合并

    # 显示图例
    p1.legend = True

    p1.show()

    return p

  def plot_implicit(self):
    # 隐函数绘图
    x, y, z = sympy.symbols('x,y,z')
    p = sympy.plot_implicit(x**2 + y**2 - 4)
    return p

  def solve_eq(self, expr_list, **var):
    result = sp.solve(expr_list, **var)
    return result

  def cubic_spline_sum_expr(self, number_of_sum):
    """求和表达式

    Args:
        number_of_sum (_type_): _description_

    Returns: expr_sum
        _type_: _description_
    """
    k = sp.symbols('k')
    A = sp.IndexedBase(label='A')
    R = sp.IndexedBase(label='R')
    r = sp.symbols('r')
    expr = A[k]*(R[k] - r)**3 * sp.Heaviside(arg=R[k] - r, H0=1)
    expr_sum = sp.Sum(expr, (k, 0, number_of_sum-1))
    return expr_sum

  def cubic_spline_value(self, r_values_array, A_values_array, R_values_array):
    """表达式求值

    Args:
        r_values_array (_type_): _description_
        A_values_array (_type_): _description_
        R_values_array (_type_): _description_

    Returns:
        _type_: _description_
    """
    number_of_sum = len(A_values_array)
    expr = self.cubic_spline_sum_expr(number_of_sum=number_of_sum)
    expr_func = sp.lambdify(args=['r', 'A', 'R'], expr=expr, modules='numpy')
    values_array = expr_func(r_values_array, A_values_array, R_values_array)
    return values_array

  def notes_symble_var(self):
    # 定义符号变量 sympy.symbols()

    import sympy
    sympy.init_printing(use_unicode=True)  # 指定结果用unicode字符打印出来。

    m = sympy.Symbol("m")  # 只能定义一个，没啥用
    m

    t = sympy.symbols("t")

    t

    # 定义多个变量
    m, n, p = sympy.var("m,n,p")
    m, n, p

    # 定义多个变量
    x, y, z = sympy.symbols("x,y,z")

    x, y

    alpha = sympy.symbols("alpha")

    alpha

    var_x = sympy.symbols("x_1:5")

    var_x[0]

    var_x

    # ## 数学符合补充

    # 虚数单位i
    sympy.I

    # 自然对数低e
    sympy.E

    # 无穷大
    sympy.oo

    # 求n次方根
    sympy.root(8, 3)

    # 求对数
    sympy.log(1024, 2)

    # 求阶乘
    sympy.factorial(4)

    # # 替换操作

    # ## 符号表达式

    import sympy

    x, y, z = sympy.symbols("x,y,z")
    expr = sympy.exp(sympy.cos(x)) + 1
    expr

    # ## 替换: subs()方法

    expr.subs(x, 0)

    t = sympy.symbols("t")
    exp_1 = sympy.exp(t) + 1
    exp_2 = sympy.cos(x)

    exp_1.subs(t, exp_2)

    expr = x**3 + 4*x*y - z
    expr.subs([(x, 2), (y, 4), (z, 5)])

    expr.subs([(x, 2), (y, 4), ])

    # ## 字符串转化为表达式 sympy.sympify()

    import sympy

    str_expr = "x**2 + 2*x +1"
    expr = sympy.sympify(str_expr)
    expr = sympy.simplify(str_expr)
    expr
    # expr

    x = sympy.symbols("x")

    num = expr.subs(x, 2)
    num

    type(num)

    # ## 要获取表达式的字符串形式，则使用str(expr)

    expr

    str(expr)

    x = sympy.symbols('x')
    expr = sympy.Integral(sympy.sqrt(1/x), x)
    expr

    str(expr)

    sympy.srepr(expr)

    # ## 将SymPy表达式转换为可进行数值计算的表达式
    # 最简单方法是使用lambdify函数

    import numpy as np

    import numpy
    a = numpy.arange(10)
    expr = sympy.sin(x)
    f = sympy.lambdify(x, expr, modules="numpy")
    f(a)

    # ## 为数值指定精度 使用evalf()方法
    # 要将数值表达式求值为浮点数

    sympy.sqrt(8).evalf(n=15)

    expr = sympy.cos(2*x)
    expr

    # 使用subs flag将替换传递给evalf更有效，数值上更稳定，它需要一个符号字典：点对（ point pairs）
    expr.evalf(n=15, subs={x: 2.4})  # 可以指定精度

    expr.subs(x, 2.4)  # 不能指定精度

    # ## 计算机二进制计算的误差
    # evalf(chop=True) 通过将chop设置为True来自行删除小于所需精度的舍入误差
    # 0.1+0.2

    expr = sympy.sin(1)**2 + sympy.cos(1)**2 - 1
    expr.evalf()

    expr.evalf(chop=True)

    expr = sympy.sympify("0.1+0.2")
    expr.evalf(chop=True)

    # 注意区别
    # * sympy.simplify()  # 简化计算
    # * sympy.sympify() # 转换字符串

    x, y, z = sympy.symbols("x,y,z")

    expr = (x**3 + x**2 - x - 1)/(x**2 + 2*x + 1)

    sympy.simplify(expr)

    # 简化结果不明确
    sympy.simplify("x**2+2*x +1")

    # ### 因式分解 factor()

    sympy.factor(x**2 - 5*x + 6)

    sympy.factor(x**3 - y**3)

    sympy.factor_list(x**3 - y**3)

    # ### 多项式展开 expand()  展开成多项式

    sympy.expand((x-2)*(x-3))

    # ### 合并同类项 collect()
    # 与coeff()方法搭配使用，给出某一项的系数
    expr = x**3 - x**2*z + 2 * x**2 + x*y - 3
    expr.collect(x)
    sympy.collect(expr, x)
    sympy.collect(expr, x).coeff(x, 2)
    expr.coeff(x, 2)

    # ### 有理分式化简 cancel()
    expr = (x**2 + 2*x + 1)/(x**2+x)
    expr.cancel()

    sympy.cancel(expr)

    expr.simplify()

    # ### 有理分式部分分式分解 aprt()
    expr = (x**3 - x**2 + 2*x + 1)/(x**2+x)
    expr.apart()

    # ### 反三角函数  前面加a

    expr = sympy.acos(x)
    expr

    # ### 利用三角恒等式化简 trigsimp() 利用三角恒等式展开expand_trig()
    expr = sympy.sin(x)**2 + sympy.cos(x)**2
    sympy.trigsimp(expr)  # 对于这个表达式sympy.simplify() 就是利用了trigsimp()方法化简的
    sympy.expand_trig(sympy.cos(8*x))

    # ### 幂函数化简 powsimp() 与展开expand_power_exp(), 指数函数expand_power_base()

    x, y = sympy.symbols("x,y")
    a, b = sympy.symbols("a,b")

    expr = x**a * y**a
    expr

    sympy.powsimp(expr)

    # 或者指定参数强制化简
    x, y = sympy.symbols("x,y")
    a, b = sympy.symbols("a,b")
    expr = x**a * y**a
    sympy.powsimp(expr, force=True)

    # 需要指定条件才能化简
    x, y = sympy.symbols("x,y", positive=True)
    a, b = sympy.symbols("a,b", real=True)
    expr = x**a * y**a
    sympy.powsimp(expr)

    sympy.expand_power_base((x*y)**a, force=True)

    # 公式
    x, y = sympy.symbols("x,y")
    a, b = sympy.symbols("a,b")
    expr = (x**a)**b
    sympy.powdenest(expr)

    sympy.powdenest(expr, force=True)

    # # 将字符表达式转换为LaTeX代码

    expr = sympy.Integral(sympy.cos(x)**2, (x, 0, sympy.pi))
    sympy.latex(expr)

    # # 检验是否相等

    import sympy
    x, y, z = sympy.symbols("x,y,z")

    # 通过在随机点上对两个表达式进行数值求值来检验它们是否相等。
    a = sympy.cos(x)**2 - sympy.sin(x)**2
    b = sympy.cos(2*x)
    a.equals(b)

    # 构造有理数
    sympy.Rational(1, 2)

  def notes_solve_eq(self):

    sympy.init_printing(use_unicode=True)  # 指定结果用unicode字符打印出来。

    # # 方程求解
    # ## 建立方程

    x, y, z = sympy.symbols('x y z')

    equation = sympy.Eq(x**2, 2)
    equation

    # ## 解方程

    sympy.solve(equation, x)  # 可以是方程

    sympy.solve(x**2-2, x)  # 可以是=0的表达式

    sympy.solveset(sympy.sin(x)-1, x, domain=sympy.S.Reals)

    sympy.solveset(sympy.sin(x)-1, x)

    sympy.solve(sympy.sin(x)-1, x)

    # ## 解方程组
    # 总结，只需要记住solve就行，方程，方程组，线性，非线性都可以解, 对于方程solveset()能求出解的集合

    # ### 方程式形式

    x, y, z = sympy.symbols('x y z')
    sympy.linsolve([x+y+z-1, x+y+2*z-3], (x, y, z))

    x, y, z = sympy.symbols('x y z')
    sympy.solve([x+y+z-1, x+y+2*z-3, x-z**3-4], (x, y, z))

    # ### 增广矩阵形式

    sympy.Matrix([[1, 1, 1, 1], [1, 1, 2, 3]])

    sympy.linsolve(sympy.Matrix([[1, 1, 1, 1], [1, 1, 2, 3]]), (x, y, z))

    # ### $Ax=b$形式

    M = sympy.Matrix([[1, 1, 1, 1], [1, 1, 2, 3]])
    M

    A = M[:, :-1]
    b = M[:, -1]
    system = A, b
    system

    sympy.linsolve(system, x, y, z)

    sympy.linsolve(M, (x, y, z))

    # ### 非线性方程

    sympy.nonlinsolve([x*y - 1, x-2*y], (x, y))

    # nonlinsolve不能很好地求解具有三角函数的方程组。
    sympy.solve([x*y - 1, x-2*y], (x, y))

    sympy.solve([sympy.sin(x+y), sympy.cos(x-y)], [x, y])

    sympy.solveset(x*sympy.exp(x)-1, x)

    # 利用nsolve求解数值解
    from sympy import symbols, Eq, nsolve
    x, y = symbols('x y')
    eqs = [Eq(x ** 2 / 4 + y ** 2, 1),
           Eq((x - 0.2) ** 2 - y, 3)]

    X0 = [3, 4]
    print(nsolve(eqs, [x, y], X0))

    # 利用nsolve求解数值解
    from sympy import symbols, Eq, nsolve
    x, y = symbols('x y')
    eqs = [Eq(x ** 2 / 4 + y ** 2, 1),
           Eq((x - 0.2) ** 2 - y, 3)]

    X0 = [3, 4]
    sympy.solve(eqs, [x, y])

    # ## 求解微分方程：$y'' - y = e^t$
    #

    # ### 两种创建函数的方法

    # 通过将cls=function传递给symbols函数来创建未定义的函数。
    f, g = sympy.symbols('f g', cls=sympy.Function)
    f, type(f)
    t = sympy.symbols('t')
    f(x), f(t), f

    y = sympy.Function("y")  # 或者用这种方式
    y, type(y)

    y(t)

    f(x).diff(x)  # f(x)的未估值导数：

    # ### 解微分方程

    t = sympy.symbols("t")
    y = sympy.Function("y")

    # 创建微分方程
    diffeq = sympy.Eq(y(t).diff(t, t) - y(t), sympy.exp(t))
    diffeq

    sympy.dsolve(diffeq, y(t))

    sympy.solve(diffeq, y(t))  # 不是想要的结果

    sympy.dsolve(f(t).diff(t, 2) - 2*f(t).diff(t) + f(t) - sympy.sin(t), f(t))

    sympy.dsolve(sympy.Eq(f(t).diff(t, 2) - 2 *
                          f(t).diff(t) + f(t), sympy.sin(t)), f(t))

    f = sympy.Function('f')
    eq = sympy.Eq(f(t).diff(t, 2) - 2 * f(t).diff(t) + f(t), sympy.sin(t))
    eq

    sympy.dsolve(eq, f(t))

    # ## 求矩阵 $\begin{pmatrix} 1&2\\2&2\end{pmatrix}$特征值

    expr = sympy.Matrix([[1, 2], [2, 2]])
    expr

    expr.eigenvals()

    # # 求和  $\displaystyle \sum_{n=1}^{100}2n$

    import sympy
    # 定义变量
    n = sympy.Symbol('n')
    f = 2*n

    # 前面参数放函数，后面放变量的变化范围
    s = sympy.summation(f, (n, 1, 100))
    s

    # # 解带有求和式的方程  $\displaystyle \sum_{i=1}^{5} x^2+10x = 15$

    # 解释一下，i可以看做是循环变量，就是x自己加五次
    # 先定义变量，再写出方程
    x = sympy.Symbol('x')
    i = sympy.Symbol('i')
    f = sympy.summation(x*2, (i, 1, 5))+10*x-15
    result = sympy.solve(f, x)
    result

    # ## 求和方程的应用

    import sympy
    x, i, n = sympy.symbols("x,i,n")
    a = sympy.IndexedBase("a")
    expr = a[i]*x**3
    # expr_sum = sympy.summation(expr,(i,0,4)) # 直接求和相当于下面使用.doit()之后的结果
    expr_sum = sympy.Sum(expr, (i, 0, 4)).doit()  # doit()注意变成求和的长形式
    expr_sum_diff = expr_sum.diff(x, 1)
    expr_sum_diff

    expr_sum

    # 代入索引值
    # 方法1，先把表达式变成函数再代入值
    expr_sum_diff_func = sympy.lambdify([x, a], expr_sum_diff, modules="numpy")
    A = [1, 2, 3, 4, 5]  # a1=1,a2=2, ...
    expr_sum_diff_func(3, A)

    # 方法2，现代入值再把表达式变成函数
    # expr_sum_diff = expr_sum_diff.subs(dict(zip(a,A)))
    expr_sum_diff = expr_sum_diff.evalf(subs=dict(zip(a, A)))  # 要注意是字典形式
    # 变成函数
    expr_sum_diff_func = sympy.lambdify(x, expr_sum_diff, modules="numpy")
    expr_sum_diff_func(3.5)

    # ## 分段函数

    # r1,rc 分别为内截断和外截断

    def get_S_expr():
      A, B, C = sp.symbols('A,B,C')
      r = sp.symbols('r')
      r_1 = sp.symbols('r_1')
      r_c = sp.symbols('r_c')
      S_expr1 = C
      S_expr2 = A/3 * (r - r_1)**3 + B/4 * (r - r_1)**4 + C
      S_expr = sp.Piecewise((S_expr1, r < r_1), (S_expr2, True))
      return S_expr

    get_S_expr()

    A, B, C = sp.symbols('A,B,C')
    r = sp.symbols('r')
    r_1 = sp.symbols('r_1')
    r_c = sp.symbols('r_c')
    sp.Piecewise((C, r < r_1), (A+B, sp.And(r_1 < r, r < r_c)))

    sp.Piecewise((C, r < r_1), (A+B, r < r_c))

    pass

  def notes_tyler(self):
    # 泰勒公式: 把复杂的函数转换成简答的函数，方法就是泰勒展开 复杂函数 $\to$ 多项式表示的函数
    # $f(x) = \displaystyle\sum_{n=0}^{n} \frac{f^{(n)} (x_0)}{n!} (x-x_0)^n$
    # 这种转换只在$x_0$ 及其附近的一个小区间有效
    x, y, z = sympy.symbols("x,y,z")
    expr = sympy.exp(sympy.sin(x))
    n_2 = sympy.series(expr, x, x0=0, n=3)  # 2阶展开
    n_2.removeO()  # 去掉高阶
    n_4 = expr.series(x, 0, 5)
    n_6 = expr.series(x, 0, 7)

    # 画图展示
    def figure_taylor():
      import matplotlib.pyplot as plt
      import numpy as np
      # %matplotlib widget
      x = np.arange(-2, 2, 0.01)
      n2 = 1 + x + x**2/2
      n4 = -x**4/8 + x**2/2 + x + 1
      n6 = eval(str(n_6.removeO()))
      fig, ax = plt.subplots()
      ax.plot(x, np.exp(np.sin(x)), color="r", label="original")
      ax.plot(x, n2, label="n_2")
      ax.plot(x, n4, label="n_4")
      ax.plot(x, n6, label="n_6")
      ax.hlines(y=0, xmin=-2, xmax=2, color="k", alpha=1)
      ax.vlines(0, ymin=-1, ymax=5, color="k", alpha=1)
      ax.legend()
      plt.show()

    n = 3
    print(sympy.diff(expr, x, n).subs(x, 0))
    print(sympy.diff(n_2.removeO(), x, n).subs(x, 0))
    print(sympy.diff(n_4.removeO(), x, n).subs(x, 0))
    print(sympy.diff(n_6.removeO(), x, n).subs(x, 0))

    expr.taylor_term(5, x)

  def notes_微积分(self):
    # ## 求导函数 diff()
    # * diff(expr, x) 表达式对x求导
    # * 连续求导 diff(expr,x,x) 或者diff(expr,x,2)
    # * 多元连续求导 diff(expr,x,2 y,3,z,5)
    x, y, z = sympy.symbols("x,y,z")
    expr = sympy.sin(x)
    sympy.diff(expr, x, 2)
    expr.diff(x, 2)

    # 创建求导公式 sympy.Derivative(), 求解 doit()方法
    expr = sympy.Derivative(sympy.sin(x*y), x)
    expr.doit()

    #
    m, n, a, b = sympy.symbols("m,n,a,b")
    expr = (a*x + b)**m
    expr.diff((x, n))

    expr = sympy.Derivative(sympy.sin(x*y), (x, n))

    # 数值微分的python实现
    import numpy as np

    def diff1_c(f, x, h):  # 中心差分
      """
      (1) 从截断误差的角度——步长越小，计算结果越精确
      (2) 从舍入误差的角度——步长不宜过小
      当步长 h 非常小，f(x+h) 和 f(x−h) 的值非常接近，直接相减可能会造成有效数字的损失
      原文链接：https://blog.csdn.net/xfijun/article/details/108422317
      """
      return (f(x+h)-f(x-h))/(2*h)

    def func(x):
      return np.sin(x)

    # 在 pi/3处的数值微分值
    func_diff_value = diff1_c(func, np.pi/3, 1e-6)
    print(f"数值微分的值为-->{func_diff_value})")

    # 对比符号微分的值
    import sympy
    x = sympy.symbols("x")
    expr = sympy.sin(x)
    # 微分的表达式
    expr_diff = sympy.diff(expr, x, 1)
    # 在 pi/3处的值
    expr_diff_value = expr_diff.evalf(subs={x: sympy.pi/3}, chop=True, n=5)
    print(f"符号微分在pi/3处的值为-->{expr_diff_value}")

    # ## 积分学
    # * 不定积分，定积分，多重积分 integrate()

    # 不定积分
    sympy.integrate(sympy.cos(x), x)
    # 定积分
    sympy.integrate(sympy.cos(x), (x, 0.5, 1))  # 传递一个元组
    sympy.integrate(sympy.exp(-x), (x, 0, "+oo"))
    sympy.integrate(sympy.exp(-x**2 - y**2),
                    (x, "-oo", "+oo"), (y, "-oo", "oo"))
    sympy.integrate(x**x, x)
    # 定义积分表达式 Integral  计算doit()
    expr = sympy.Integral(sympy.log(x)**2)
    expr.doit()

  def notes_求极限(self):
    x, y, z = sympy.symbols("x,y,z")
    # 求极限值
    sympy.limit(sympy.sin(x)/x, x, 0)  # 可以用 +oo, -oo 表示无穷

    # 定义未求值的函数 Limit()
    expr = sympy.Limit(sympy.sin(x)/x, x, 0)
    # 求值 doit()
    expr.doit()

    # 求左右极限
    sympy.limit(1/x, x, 0, "+")
    sympy.limit(1/x, x, 0, "-")

  def notes_画图(self):
    # 创建一个符号变量
    x = sp.symbols('x')
    # 创建一个表达式
    expr = x**2
    # 使用sympy.plot绘制图形，设置标题和标签
    p = sp.plot(expr, (x, -5, 5),    # 该命令就可以显示图形了
                title='中文标题',
                xlabel='X轴标签',
                ylabel='Y轴标签',
                size=(4, 3),  # 设置大小
                )

    x, y, z = sympy.symbols("x,y,z")

    # %matplotlib widget

    x = sympy.symbols('x')
    p = sympy.plot(-sympy.sqrt(x), (x, 0, 10), xlabel="time",
                   label='my legend',
                   legend=True)
    # plt.show()

    p.get_segments()

    # 隐函数绘图
    sympy.plot_implicit(x**2 + y**2 - 4)

    x = sympy.symbols('x')
    p1 = sympy.plot(sympy.log(x),
                    # label='log(x)',
                    legend=True)
    a, b, c, x, y, z = sympy.symbols('a,b,c,x,y,z')

    sympy.plot((x**2, (x, -6, 6)), (x, (x, -5, 5)), legend=True)

    sympy.plot(x, x**2, x**3, (x, -5, 5), )

    x = sympy.symbols('x')
    p1 = sp.plot(sp.sin(x), (x, -5, 5),
                 show=False, label='1/v'
                 )
    p2 = sp.plot(2*sp.sin(x), (x, -5, 5),
                 show=False, label='2/V'
                 )
    p1.extend(p2)  # 将两个图形对象合并

    # 显示图例
    p1.legend = True
    p1.show()

  def notes_矩阵(self):
    # 生成矩阵，使用Matrix对象
    sympy.Matrix([[1, -1], [3, 4], [0, 2]])

    # 为了便于生成列向量，单独一个元素列表被认为是列向量
    sympy.Matrix([1, 2, 3])
    # 生成矩阵的函数
    sympy.zeros(3, 4)
    sympy.ones(2, 3)
    sympy.diag([1, 2, 3])
    sympy.diag(1, 2, 3)
    # ## 矩阵的操作
    M = sympy.Matrix([[1, 2, 3], [3, 2, 1]])
    N = sympy.Matrix([0, 1, 1])
    M, N

    M*N
    # 属性
    M.shape
    # ### 访问行和列
    # 若要获取矩阵的单个行或列，请使用row或col。例如，M.row(0)将获取第一行。M.col(-1)将获取最后一列。
    #
    M.row(0)
    M.col(-1)
    M.col(-1).row(0)
    # ###  删除和插入行和列

    # 要删除行或列，请使用row_del或r col_del。这些操作将修改矩阵。
    M.col_del(1)
    M.row_del(0)
    # 插入行和列
    M = M.row_insert(0, sympy.Matrix([[4, 5]]))
    M.col_insert(2, sympy.Matrix([1, 2]))
    # 运算
    M**(-1)
    # 转置
    M.transpose()  # 或者M.T
    # 矩阵的行列式
    M.det()
    # 将矩阵转换为简化的阶梯形式, rref(),返回第一个元素是简化的行梯队形式，第二个元素是主元的列索引。
    M.rref()
    # 找到矩阵的零空间，请使用nullspace
    m = sympy.Matrix([[1, 2, 3, 0, 0], [4, 10, 0, 0, 1]])
    m.nullspace()

    # 特征值、特征向量和对角化（Eigenvalues, Eigenvectors, and Diagonalization）
    # 要求矩阵的特征值，请使用eigenvals。eigenvals返回一个字典：{特征值：代数重数}
    M.eigenvals()
