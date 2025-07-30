import copy


class CopyLearn():
  def __init__(self) -> None:
    """为什么有赋值还要copy呢？当有一个需求是要把一个数据放到我的程序里进行修改操作，但是还要保持原始数据不变。这个时候就需要copy模块

    官方解释：与C语言不同,Python中的赋值语句不复制对象，它们在目标和对象之间建立索引。对于可变项目或可变项目的集合，有时需要一个副本，以便可以更改一个副本而不更改其他副本。该模块提供通用的浅层和深层copy操作。

    https://www.bilibili.com/video/BV1gB4y197dm/?spm_id_from=333.337.search-card.all.click&vd_source=5ec84b7f759de5474190c5f84b86a564
    """
    pass

  def assingment(self):
    a = [11, 22]
    b = a  # 这个不叫复制, 这个称之为增加指向,
    print(id(a), id(b))
    a.append(33)  # 修改a后 b也变

  def shallow_copy(self):
    a = [11, 22]
    b = [33, 44]
    c = [a, b]
    d = copy.copy(c)  # 浅拷贝是复制c, 对于c里面的可变对象,  只是增加了指向
    print(id(c), id(d))  # c,d 地址不同
    print(id(c[0]), id(d[0]))  # 地址相同
    # 对于元组不执行copy
    a = (1, 2)
    b = copy.copy(a)
    print(id(a), id(b))  # 地址相同
    pass

  def deep_copy(self):
    a = [11, 22]
    b = [33, 44]
    c = [a, b]
    d = copy.deepcopy(c)  # 深拷贝, 会复制c列表以及c列表里面的嵌套列表
    print(id(c), id(d))  # c,d 地址不同, 一定是复制了一份c 然后用d指向
    print(id(c[0]), id(d[0]))  # 地址也相同
    a.append(555)
    print(c, d)  # 结果不同
    pass

  def example(self):
    a = [11, 22]
    b = [33, 44]
    c = [a, b]
    d = copy.copy(c)
    e = copy.deepcopy(c)
    c.append([55, 66])
