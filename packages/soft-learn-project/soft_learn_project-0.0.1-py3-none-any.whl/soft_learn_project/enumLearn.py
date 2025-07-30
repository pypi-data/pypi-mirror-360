from enum import Enum


class enumLearn():
  def __init__(self):
    """* enum 是 Python 中的一个标准库模块，用于创建枚举（Enum）。枚举是一种数据类型，表示一组固定的常量值。每个枚举值都有一个名字和一个值，可以通过名字或值来引用它们。枚举可以使代码更具可读性和可维护性，因为它为常量提供了有意义的名字，而不是直接使用硬编码的数字或字符串。
    * 使用 enum 的基本概念
    - 定义枚举类： 你可以通过继承 enum.Enum 来定义一个枚举类。
    - 访问枚举成员： 枚举类的成员可以通过类名访问，也可以通过值访问。
    * 枚举的特点
    - 名字和值： 每个枚举成员都有一个名字（如 PENDING）和一个值（如 1）。
    - 不可变性： 枚举类一旦定义，其成员是不可改变的。
    - 成员比较： 枚举成员之间可以进行比较（如 == 或 is）。
    * 为什么使用 enum？
    - 提高代码可读性： 使用有意义的名称而不是数字或字符串常量。
    - 避免错误： 枚举值是唯一的，防止使用错误的常量值。
    - 支持自动化迭代： 枚举类允许你轻松迭代其成员。
    * 常见用法
    - 实现状态机： 枚举经常用于表示不同的状态、事件、类型等。
    - 替代常量： 枚举可以代替传统的常量值，使代码更具可读性。
    """
    pass

  def e(self):
    pass
# 定义枚举类


class Status(Enum):
  PENDING = 1
  IN_PROGRESS = 2
  COMPLETED = 3


# 访问枚举成员
print(Status.PENDING)          # 输出：Status.PENDING
print(Status.PENDING.name)     # 输出：PENDING
print(Status.PENDING.value)    # 输出：1

# 使用枚举值
print(Status(1))               # 输出：Status.PENDING
