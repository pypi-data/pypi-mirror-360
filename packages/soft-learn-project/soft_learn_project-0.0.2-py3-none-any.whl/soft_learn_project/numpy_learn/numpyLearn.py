import numpy as np


class NumpyLearn():
  def __init__(self) -> None:
    """NumPy (numerical python)针对数组运算提供大量的数学函数库, 主要用于数组计算，包含
    一个强大的N维数组对象 ndarray: n - dimention array N维数组
    整合 C/C++/Fortran 代码的工具
    线性代数、傅里叶变换、随机数生成等功能
    """
    pass

  def set_printoptions(self):
    """可以通过使用 numpy 中的 set_printoptions 函数来控制数组打印时显示的精度。对于你的数组，如果你希望显示两位有效数字，可以设置如下：
    suppress = True 会防止大数以科学计数法显示。
    注意，这只是影响数组的打印格式，而不修改数组本身的值。如果你想要修改数组中的数值精度，可以使用 round 函数
    np.set_printoptions(precision=2, suppress=True)
    """
    pass

  def install(self):
    string = """ numpy的安装
    默认已经安装在anaconda 所建立的环境了,
    如果没有, 则安装: conda install numpy 
    """
    print(string)
    return None

  def notes(self):
    """
    # 需要注意和理解的地方
    np.random.seed(22)
    arr = np.random.randint(0, 10, size=(3, 2))

    for a in arr:
      a[:] = np.array([0, 0])  # 这种方式不会创建新的对象, 会修改arr的值
      # a = np.array([0,0]) # 这种方式会创建新的数组对象, 不会修改arr的值
    print(arr)

    # np.all 和np.any 的用法
    a = np.array([1, 2, 4])
    b = np.array([1, 2, 3])
    print(a == b)
    print(np.all(a == b))  # 有一个假则返回假
    print(np.any(a == b))  # 有一个真则返回真
    print(np.all([1, 2, np.nan]))
    print(np.all([3, 0, 0]))

    # 我临时的
    a_list = list(range(5))
    a_array = np.array(range(5))
    print(a_list, a_array)  # 从外观上能看出列表元素之间有逗号，而数组元素之间是空格
    m = np.linspace(0, 11, 12).reshape(3, 4)
    print(m, type(m))
    n = m[1:3, 2:4]
    print(n, type(n))

    b_matrix = np.matrix([[1, 2], [3, 4]])  # np中的矩阵对象，已经不推荐使用了，推荐的是数组类型的对象
    b_asarray = np.asarray(b_matrix)
    print(b_matrix, type(b_matrix), '\n', b_asarray, type(b_asarray))

    # 创建数组 np.array()
    a = np.array([2.0, 3.0, 4.0])  # 使用 array()函数创建ndarray n 维数组
    # print(a)
    c = np.array([[1.0, 2.0], [3.0, 4.0]])  # 二维数组
    d = np.array([[1, 2], [3, 4]], dtype=complex)  # dytpe指定数组元素的数据类型
    # print(d)
    arr = np.array(['apple', 'banana', 'cherry'])
    # print(arr.dtype)  # 获取数组对象的数据类型
    # a = np.array([1, 2, 3, 4, 5], ndmin=5) # ndmin指定创建数组的最小维度
    # 在此数组中，最里面的维度（第 5 个 dim）有 4 个元素，第 4 个 dim 有 1 个元素作为向量，
    # 第 3 个 dim 具有 1 个元素是与向量的矩阵，第 2 个 dim 有 1 个元素是 3D 数组，而第 1 个 dim 有 1 个元素，该元素是 4D 数组。
    m = np.array(range(10), dtype=float)  # 使用迭代器创建 ndarray

    y_ndarray = np.linspace(-1, 2,5, dtype=float)  # 创建一个等差数列数组，起点为-1，终点为2，取5个点, 默认50个点
    print(y_ndarray)
    print(np.around(y_ndarray, decimals=1))
    # np.around(y, decimals=2)  # numpy 指定浮点数的小数位数
    # 数组的属性 查看属性而不是调用方法

    # a = np.random.randint(10, size=(2, 2, 3))
    a = np.array(
        [[7, 2, 3],
        [8, 9, 6]], dtype=float)
    print(a)

    print(a.shape)  # 数组的维度，对于矩阵，返回元组(m,n) m 行 n 列
    print(a.size)  # 数组元素的总个数，相当于 .shape 中 n*m 的值

    print(a.ndim)  # 秩，即轴的数量或维度的数量
    # print(a.dtype)  # ndarray 对象的元素类型
    # print(a.itemsize)  # ndarray 对象中每个元素的大小，以字节为单位
    print(a.flags)  # ndarray 对象的内存信息
    # print(a.real)  # ndarray元素的实部  # a.imag	元素的虚部

    # 数据类型修改  astype()
    arr = np.array([[1.1, 2.1, 3.1],
                    [22.3, 53, 21]]
                  )
    # print(arr.dtype)
    # print(arr.astype(int).dtype)  # 使用 astype() 方法转换数据类型并返回新数组, 或者 newarr = arr.astype('i')
    print(arr.tobytes())  # 序列化到本地, 变成字节，然后就可以写入到本地了 print(newarr.tostring()) 方法被丢弃

    # 索引，切片
    a = np.arange(0, 10, 1) ** 2
    # print(a)
    # print(a[2:4])  # 索引从0开始，
    # print(a[0:6:2])  # 或者print(a[:6:2], 从开始到第6个索引，每隔一个元素（步长=2）赋值
    # a[-1] = 100  # 赋值, -1表示最后一个索引
    # print(a)
    # a[1:4] = 100  # 批量赋值
    # print(a)
    print(a[::-1])  # 将a逆序输出，a本身未发生改变
    b = [np.sqrt(i) for i in a]  # 通过遍历赋值
    arr = np.arange(0, 20).reshape((4, 5))
    print(arr)
    # print(arr[:, -1])  # 取最后一列
    # print(arr[0:3, 2])
    # print(a > 2)  # 关系判断给出逻辑值
    # print(a[a > 2])  # 数组过滤, 根据逻辑值找到符合条件的

    # 迭代遍历
    arr = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
    for x in np.nditer(arr): # 使用 nditer()
        print(x)

    # for idx, x in np.ndenumerate(arr): # 使用 ndenumerate() 进行枚举迭代
    #     print(idx, x)

    # for x in arr:  # 获取 n 维数组的值，需要迭代n次
    #     for y in x:
    #         for z in y:
    #             print(z)


    # 数组的常用函数
    # 生成数组的方法
    # print(np.ones((2, 3, 4), dtype=np.int16))  # 2页，3行，4列，全1，指定数据类型
    # print(np.zeros((2, 3, 4)))  # 2页，3行，4列，全0
    # print(np.empty((2, 3)))  # 值取决于内存

    # 随机数
    print(np.random.uniform(low=0, high=10, size=[3,4]))

    # print(np.random.rand(3, 4))  # 返回 0 到 1 之间的随机浮点数。rand(),rand(3,3)
    # print(np.random.randn(2, 4))  # 返回满足标准正态分布的随机数 # 3 + 2.5 * np.random.randn(2, 4)
    # print(np.random.randint(0, 10, size=10))  # 返回整数随机数，size可指定大小 size=(3,4)
    # print(np.random.choice(x, size=(2, 3)))  # 从向量x中随机返回其中一个值。取多次可组成矩阵，size指定矩阵大小

    # 形状操作  方法：shape, reshape, transpose, resize， ravel, squeeze
    np.random.seed(22)
    a: np.ndarray = np.floor(10 * np.random.random((3, 4)))
    print(a)
    # print(a.reshape(4,3))  # 只是改变形状，不改变维度, 或者a.reshape(4,-1)， a.reshape(1,-1) # 还是二维数组
    # print(a.reshape(-1)) # 可以展平数组(将多维数组转换为 1D 数组) 或者用a.ravel()， 形状改变变成一维。
    print(a.transpose())  # 输出a的转置 或者：print(a.T)
    # print(a.reshape(2, 6))  # 或者 print(a.reshape(2, -1))  不改变数组a
    # a.resize((2, 4))  # 直接修改原数组, 无返回值 不能print(a.resize((2,4)))
    # print(a)

    # squeeze 函数：从数组的形状中删除单维度条目，即把shape中为1的维度去掉
    # 用法：numpy.squeeze(a,axis = None)
    #  2）axis用于指定需要删除的维度，但是指定的维度必须为单维度，否则将会报错；
    #  3）axis的取值可为None 或 int 或 tuple of ints, 可选。若axis为空，则删除所有单维度的条目；
    #  4）返回值：数组
    #  5) 不会修改原数组；
    z = np.array([[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]])
    print(z, z.shape)
    z_new = z.squeeze(axis=None)  # z_new = np.squeeze(z, axis=None) # 从数组的形状中删除单维度条目，即把shape中为1的维度去掉
    print(z_new, z_new.shape)

    # 数组的分析与处理方法： sum(), min(), max(), sort(), lexsort(), cumsum(), cumprod() 等
    a = np.array([[6, 5, 45], [3, 18, 9]])  # 2行2列
    print(a)
    print(np.sort(a, axis=1))  # 用函数排序
    a.sort(axis=1)  # 用方法排序，直接修改a的内容，无返回值
    print(a)
    # print(np.sum(a, 0))  # 矩阵行求和1，列求和0,默认全部求和,或者b.sum(0)  cumsum(1) 累加和
    # print(np.min(a, axis=0))  # max(),min() # axis = 0: 按列计算，axis = 1: 按行计算
    # print(np.average(a))
    # print(np.std(a))  # 标准差
    # print(np.var(a))  # 方差

    nm = ('raju', 'anil', 'ravi', 'amar')
    dv = ('f.y.', 's.y.', 's.y.', 'f.y.')
    ind = np.lexsort((dv, nm))  # numpy.lexsort() 用于对多个序列进行排序。把它想象成对电子表格进行排序，每一列代表一个序列，排序时优先照顾靠后的列。
    print(ind)  # 排序的索引
    print([nm[i] + ", " + dv[i] for i in ind])  # 根据索引来获取排序后的数据

    # 副本和视图 a.copy() a.view()
    a = np.array([1, 2, 3, 4, 5])
    b = a.copy()  # b是a的副本，改变a不会影响b
    c = a.view()  # c是a的视图，改变a会影响c
    a[0] = 61
    print(a)
    print(b)
    print(c)

    # 数组的连接concatenate() 堆栈stack() 拆分split()
    # 按照行合并
    arr1 = np.array([[1, 2, 3], [3, 4, 9]])  # 2X3
    arr2 = np.array([[5, 6]])  # 1X2
    arr3 = arr2.transpose() # 转置后 2X1
    arr = np.concatenate((arr1, arr3), axis=1)  # 按照行合并
    print(arr)

    # 按照列合并
    arr1 = np.array([[1, 2, 3], [3, 4, 9]])  # 2X3
    arr2 = np.array([[5, 6, 7]])  # 1X3
    arr = np.concatenate((arr1, arr2), axis=0)
    print(arr)

    # 展平合并
    arr = np.concatenate((arr1, arr2), axis=None)  
    print(arr)

    # 拆分
    # a, b = np.split(arr, 2)  # 拆分成两个数组,可以加入axis=0,1参数,必须等量拆分 还有hsplit() vsplit()
    # print(a, b)
    # a, b, c, d = np.array_split(arr, 4, axis=1)  # 可以不等量拆
    # print(a, b, c, d)

    # 不等量拆分
    arr = np.array([[1, 2, 3], [3, 4, 9],[1,31,1],[1,9,88]])
    a,b,c = np.split(arr,indices_or_sections=[1,3,],axis=0) # 分成三个数组, 0:1,1:3,3:三个

    # 数组元素的添加与删除  concatenate 能够实现append 的功能
    # arr1: np.ndarray = np.array([[1, 2, 3], [3, 4, 9]])  # 2X3
    # print(np.append(arr1, [[555, 7, 9]], axis=0))
    # append	将值添加到数组末尾
    # insert	沿指定轴将值插入到指定下标之前
    # delete	删掉某个轴的子数组，并返回删除后的新数组
    # unique	查找数组内的唯一元素
    a = np.array([[1, 2, 3], [4, 5, 6]])
    print(a)
    print(np.insert(a, 3, [11, 12]))
    print(np.insert(a, 1, 12, axis=0))  # 沿轴 0 广播
    print('*'* 40)
    print(a)
    print(np.delete(a, 2))
    data_array = np.delete(data_array,obj=[1],axis=1)  # 按照列杀出某一列或者多列
    # print(np.delete(a, 1, axis=1))

    a = np.array([5, 2, 6, 2, 7, 5, 6, 8, 2, 9])
    print(a)
    print(np.unique(a))  # 去除数组中的重复元素
    u, indices = np.unique(a, return_counts=True)
    print(u)
    print(indices)  # 返回去重元素的重复数量

    # 数组的去重
    a = np.array([[5, 2, 6], [2, 7, 5], [6, 8, 2]])
    print(a)
    # print(np.unique(a))
    # 或者拍扁再去重
    print(a.flatten())
    print(set(a.flatten()))

    # 字符串函数
    print(np.char.center('Runoob', 20, fillchar='*'))
    print(np.char.capitalize('runoob'))
    print(np.char.title('i like runoob'))
    print(np.char.lower(['RUNOOB', 'GOOGLE']))
    print(np.char.split('i like runoob?'))
    print(np.char.split('www.runoob.com', sep='.'))
    print(np.char.join([':', '-'], ['runoob', 'google']))
    print(np.char.replace('i like runoob', 'oo', 'cc'))

    # np.char.split 函数和split 方法一样，单返回的数据类型不同
    print("-" * 50)
    arr = np.char.split('i like runoob?', sep=" ")
    print(arr, type(arr))
    x_str = "i like runoob?"
    x_list = x_str.split(" ")
    print(x_list, type(x_list))

    # 基本运算  数值运算，关系运算，逻辑运算
    a = np.array([[1, 2], [3, 4]]) 
    b = np.array([[3, 2], [4, 9]])
    # print(a + b)  # n维数组能够直接相加  # 或者 print(np.add(a, b))
    # print(np.exp(a))  # 指数
    print(np.power(a, b))

    a = np.array([[0, 0, 0],
                  [10, 10, 10],
                  [20, 20, 20],
                  [30, 30, 30]])
    b = np.array([1, 2, 3])  # 当运算中的 2 个数组的形状不同时，numpy 将自动触发广播机制
    # print(a + b)
    # print(a.swapaxes(1, 0))

    a = np.array([[1, 2], [3, 4]])
    b = np.array([[11, 12], [13, 14]])
    print(np.inner(a,a))  # 两个数组的内积
    print(np.dot(a, b))  # 两个数组的点积，即元素对应相乘。 # 或者a.dot(b) # 矩阵相乘
    print(np.vdot(a, b))  # 两个向量的点积。 如果参数是多维数组，它会被展开。
    print(np.matmul(a, b))  # 矩阵乘法

    # NumPy 线性代数  NumPy 提供了线性代数函数库 linalg，该库包含了线性代数所需的所有功能
    print(np.linalg.inv(a))  # 计算矩阵的乘法逆矩阵
    print(np.linalg.det(a))  # 计算矩阵的行列式
    # numpy.linalg.solve()  # 求解线性矩阵方程 函数给出了矩阵形式的线性方程的解。

    #  NumPy IO  Numpy 可以读写磁盘上的文本数据或二进制数据。
    # NumPy 为 ndarray 对象引入了一个简单的文件格式：npy。
    # load() 和 save() 函数是读写文件数组数据的两个主要函数，默认情况下，数组是以未压缩的原始二进制格式保存在扩展名为 .npy 的文件中。
    a = np.array([1, 2, 3, 4, 5])
    np.save('outfile.npy', a)  # 保存到 outfile.npy 文件上，如果文件路径末尾没有扩展名 .npy，该扩展名会被自动加上
    b = np.load('outfile.npy')
    # print(b)

    # loadtxt() 和 savetxt() 函数 处理文本文件(.txt 等)  # 保存时用的是fmt格式参数，读取时用的是dtype数据类型，特别是对于有字符有数值的文本
    b = np.array(range(0, 12), dtype=int).reshape(3, 4)
    # print(b)
    np.savetxt("out.txt", b, fmt="%d", delimiter=',')  # 改为保存为整数，以逗号分隔
    b = np.loadtxt("out.txt", delimiter=",", dtype="str")  # load 时也要指定为逗号分隔
    print('*' * 40)
    print(b)

    # savez() 函数用于将多个数组写入文件，默认情况下，数组是以未压缩的原始二进制格式保存在扩展名为 .npz 的文件中。
    a = np.array([[1, 2, 3], [4, 5, 6]])
    b = np.arange(0, 1.0, 0.1)
    c = np.sin(b)
    np.savez("runoob.npz", a, b, sin_array=c)  # c 使用了关键字参数 sin_array
    r = np.load("runoob.npz")
    print('*' * 40)
    print(r.files)  # 查看各个数组名称
    print(r["arr_0"])  # 数组 a
    print(r["arr_1"])  # 数组 b
    print(r["sin_array"])  # 数组 c

    # numpy.histogram() 函数是数据的频率分布的图形表示。 水平尺寸相等的矩形对应于类间隔，称为 bin，变量 hist 对应于频率。
    # numpy.histogram()函数将输入数组和 bin 作为两个参数。 bin 数组中的连续元素用作每个 bin 的边界。
    a = np.array([22, 87, 5, 43, 56, 73, 55, 54, 11, 20, 51, 5, 79, 31, 27])
    hist, bins = np.histogram(a, bins=[0, 20, 40, 60, 80, 100], density=True)
    print(hist)  # 对应频次
    print(bins)  # 对应间隔
    """
    pass

  def search_三元(self):
    # --搜索数组， where() extract() 三元运算符 np.where
    np.random.seed(24)
    arr = np.random.randint(0, 10, 5)
    print(arr)
    print(np.where(arr < 3))  # 返回输入数组中满足给定条件的元素的索引。
    print(np.extract(arr < 3, arr))  # 返回满条件的元素。
    # ind = np.extract((a > 0) & (a < 0.5),b).argmin()  # 找到满足a中条件的，b的最小值的位置

    # e.g.
    a = np.arange(100, 110)
    b = np.arange(10, 20)
    a_part = a[a > 106]
    a_part
    b[np.where(a > 106)]
    np.where(a > 106, 1, a/5)  # 满足条件为1，否则a/5
    # print(np.where(stock_change > 0.5, 1, 0))

    # ### 3.4.3 np.where（三元运算符）
    # 判断前四个股票前四天的涨跌幅 大于0的置为1，否则为0
    np.random.seed(22)
    stock_change = np.round(np.random.normal(loc=0, scale=1, size=[4, 4]), 2)
    print(stock_change)
    print(np.where(stock_change > 0.5, 1, 0))

  def logical(self):
    # ### 3.4.1 逻辑运算
    np.random.seed(22)
    stock_change = np.random.normal(loc=0, scale=1, size=(8, 10))
    print(stock_change)

    # 复合逻辑运算 np.logical_and(), np.logical_or() 等
    np.random.seed(22)
    stock_change = np.round(np.random.normal(loc=0, scale=1, size=[4, 6]), 2)
    temp = stock_change[:4, :4]
    # print(temp)
    # print(np.logical_and(temp > 0.5, temp < 1))

    # 判断前四个股票前四天的涨跌幅 大于0.5并且小于1的，换为1，否则为0
    print(np.where(np.logical_and(temp > 0.5, temp < 1), 1, 0))
    print(np.where((temp > 0.5) & (temp < 1), 1, 0))  # 也能够实现上面的判断
    # 判断前四个股票前四天的涨跌幅 大于0.5或者小于-0.5的，换为1，否则为0
    print(np.where(np.logical_or(temp > 0.5, temp < -0.5), 11, 3))

  def statistics(self):
    # 统计运算 : sum(), min(), max(), sort(), lexsort(), cumsum(), cumprod() 等
    # 两种方式，1. np.函数名,  2. ndarray.方法
    # 股票涨跌幅统计运算   一行表示一支股票，每一列表示天数
    np.random.seed(22)
    stock_change = np.round(np.random.normal(loc=0, scale=1, size=[4, 6]), 2)
    temp = stock_change[:4, :4]
    # 前四只股票前四天的最大涨幅
    print(temp)  # shape: (4, 4) 0  1

  def judge(self):
    # 逻辑判断, 如果涨跌幅大于0.5就标记为True 否则为False
    print(stock_change > 0.5)

    stock_change[stock_change > 0.5] = 1.1  # 给满足条件的位置赋值
    print(stock_change)

    # 通用判断函数 np.all np.any
    # 判断stock_change[0:2, 0:5]是否全是上涨的
    np.random.seed(22)
    stock_change = np.round(np.random.normal(loc=0, scale=1, size=[4, 6]), 2)
    print(stock_change)
    print(stock_change[0:2, 0:5] > 0)

    print(np.all(stock_change[0:2, 0:5] > 0))

    # 判断前5只股票这段期间是否有上涨的
    print(np.any(stock_change[:5, :] > 0))

    # print(temp.max(axis=0))
    # print(np.max(temp, axis=-1))
    # print(np.argmax(temp, axis=-1))  # 给出最大值的位置

  def polyfit(self, x_arr=np.array([1, 2, 3, 4, 5, 6, 7, 8, 9]),
              y_arr=np.array([1, 4, 9, 16, 25, 36, 49, 64, 81]),
              degree=2,  # 选择多项式的次数
              num=100,
              ):
    """二次多项式有三个系数: a*x**2 + b*x + c 

    Args:
        x_arr (_type_, optional): _description_. Defaults to np.array([1, 2, 3, 4, 5, 6, 7, 8, 9]).
        y_arr (_type_, optional): _description_. Defaults to np.array([1, 4, 9, 16, 25, 36, 49, 64, 81]).
        degree (int, optional): _description_. Defaults to 2.

    Returns:  x_fit, y_fit
        _type_: _description_
    """
    # 多项式拟合
    coefficients = np.polyfit(x_arr, y_arr, degree)

    # 生成拟合曲线
    poly = np.poly1d(coefficients)
    x_fit = np.linspace(min(x_arr), max(x_arr), num=num)  # 用更多点来绘制平滑的拟合曲线
    y_fit = poly(x_fit)
    return x_fit, y_fit

  def zsgc_增删改查(self):
    string = """ numpy 的基础操作
    import numpy as np 
    arr1 =np.arange(5)
    arr2 =np.arange(6,11)
    # print(arr1)
    arr3 = arr1 + arr2 
    arr3
    arr3 = np.append(arr1, arr2) # 增 
    arr3 = np.append(arr3, [101,102]) 
    arr3[:10] # 删
    arr3[3] = 201 # 改
    arr3[3] # 查
    arr3
    """
    print(string)
    return None

  def get_unit_vector(self, vector_arr):
    vector_arr_unit = vector_arr/np.linalg.norm(vector_arr)
    return vector_arr_unit

  def get_theta(vec1, vec2):
    """
    计算两个矢量之间的夹角, vec1,vec2是两个矢量
    @return: 返回弧度和角度
    """
    # 两个矢量点乘
    vec1_dot_vec2 = np.dot(vec1, vec2)
    # 计算两个矢量的模
    mod_vec1 = np.sqrt(np.sum(np.square(vec1)))
    mod_vec2 = np.sqrt(np.sum(np.square(vec2)))
    # 根据公式计算夹角的余弦
    cos_theta = vec1_dot_vec2/(mod_vec1*mod_vec2)
    # 计算角度
    theta_radian = np.arccos(cos_theta)  # 弧度
    theta_degree = np.arccos(cos_theta) / np.pi * 180
    return theta_radian, theta_degree
