
import pandas as pd
import numpy as np
import itertools


class itertoolsLearn():
  def __init__(self) -> None:
    """编程中会用到很多需要迭代的地方，强大的python已经为我们提供了itertools内置库，用来帮助开发人员更便捷的编码。

    前言
    由于itertools是内置库，不需要任何安装，直接import itertools即可。

    作者：转身丶即天涯
    链接：https://www.jianshu.com/p/2ef28b04fcd4
    """
    pass

  def ex1(self):
    # 无限迭代器  默认返回一个从0开始，依次+1的自然数迭代器，如果你不停止，它会一直运行下去。
    c = itertools.count(start=0, step=1)
    for i in c:
      print(i)
      if i >= 10:
        break

  def ex2(self):
    l = [1, 2, 3, 4, 5]
    c = itertools.cycle(l)  # 传入一个可迭代对象，然后无限循环迭代。
    n = 1
    for i in c:
      n += 1
      print(i)
      if n >= 10:
        break

  def ex3(self):
    l = [1, 2, 3, 4, 5]
    # 重复迭代一个对象p_object，如果不指定times，则会迭代无数次。
    c = itertools.repeat(object=l, times=5)
    for i in c:
      print(i)

  def ex4(self):
    # 其他序列也支持(list, tuple, str, set, dict)
    l = [1, 2, 3, 4, 5]
    c = itertools.accumulate(l)  # 返回一些列累计值或者其他二进制函数。

    print(c)

    for i in c:
      print(i)

    d = {'a': 1, 'b': 2, 'c': 3}
    c = itertools.accumulate(d.keys())  # 累加迭代dict的key。
    for i in c:
      print(i)

  def ex5(self):
    # itertools.chain(*iterables)
    # 这个chain()类是非常实用的，参数可以传入任意个数序列，而且只要是序列即可，不限定序列的数据类型。
    # 比如，我想一起迭代list, tuple, str三个序列，实用itertools.chain()轻松实现。
    l = [1, 2, 3, 4, 5]
    t = ['A', 'B', 'C']
    s = 'abcdefg'
    c = itertools.chain(l, t, s)

    for i in c:
      print(i)

  def ex6(self):
    # product('ABCD', repeat=2)                   AA AB AC AD BA BB BC BD CA CB CC CD DA DB DC DD
    # permutations('ABCD', 2)                     AB AC AD BA BC BD CA CB CD DA DB DC
    # combinations('ABCD', 2)                     AB AC AD BC BD CD
    # combinations_with_replacement('ABCD', 2)    AA AB AC AD BB BC BD CC CD DD
    c = itertools.product('ABCD', repeat=3)
    for i in c:
      print("".join(list(i)))

  def combinations(self):
    """从列表中任意选择4个排列 itertools.combinations(df.index, 4)
    """
    # 创建数据
    hot = np.array(['685', '398', '1095', '911', '899', '201'], dtype=int)
    fat = [2, 2, 23, 11, 15, 1]
    data = {'name': ['红烧鱼', '蒜泥黄瓜', '土豆炖鸡块', '香菇青菜', '西红柿鸡蛋', '清炒西兰花'],
            'hot': hot, 'fat': fat}
    df = pd.DataFrame(data)
    # 设置索引
    df = df.set_index(keys='name')

    for com in itertools.combinations(df.index, 4):
      if df.loc[list(com)]['hot'].sum() > 2926 and df.loc[list(com)]['fat'].sum() <= 50:
        print(com)
