from deprecated import deprecated


class DeprecatedLearn():
  def __init__(self) -> None:
    """@deprecated 是一个常见的装饰器，通常用来标记某个函数、方法或类已被弃用（deprecated），并建议使用其他替代方案。不过 Python 并没有内置的 @deprecated 装饰器，需要通过第三方库或自定义来实现。
    from deprecated import deprecated # 这个就是第三方库
    """
    import warnings
    # 启用 DeprecationWarning
    warnings.simplefilter("always", category=DeprecationWarning)
    pass

  def install(self):
    string = """conda install deprecated
    """
    print(string)
    return None

  # 举个例子
  @deprecated(reason="Use 'new_function' instead.")
  def old_function(self,):
    print("This function is 被弃用.")

  def new_function(self):
    print("This is the new function.")
