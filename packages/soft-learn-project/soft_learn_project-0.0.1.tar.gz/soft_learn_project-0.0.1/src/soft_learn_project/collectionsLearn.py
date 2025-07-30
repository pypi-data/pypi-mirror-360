

from collections.abc import Iterable


class Features():
  def __init__(self) -> None:
    pass

  def is_iterable(obj):
    """可以使用 collections.abc 模块中的 Iterable 抽象基类来检验一个变量是否是可迭代的。

    Args:
        obj (_type_): _description_

    Returns:
        _type_: _description_
    """
    return isinstance(obj, Iterable)


if __name__ == '__main__':
  # 示例用法
  print(Features().is_iterable([1, 2, 3]))  # True
  print(Features().is_iterable("hello"))    # True
  print(Features().is_iterable(42))         # False
  print(Features().is_iterable({'a': 1, 'b': 2}))  # True
