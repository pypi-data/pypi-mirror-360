import inspect

from numpy import source


class InspectLearn():
  def __init__(self) -> None:
    pass

  def log_function_name(self,):
    """实际应用
    在实际应用中，这种方法可以用于日志记录、调试和错误处理，帮助你动态获取函数名称以提供更有用的输出信息。
    在这个示例中，log_function_name 函数可以在任何其他函数中调用，以动态地获取并记录当前函数的名称。

    Returns:
        _type_: _description_
    """
    current_frame = inspect.currentframe()
    caller_frame = inspect.getouterframes(current_frame, 2)
    function_name = caller_frame[1][3]
    return function_name

  def log_function_name_example(self,):
    print(f"正在执行的函数名: {self.log_function_name()}")

  def getsource(self, func):
    """获得函数的源代码

    Args:
        func (_type_): _description_

    Returns:
        _type_: _description_
    """
    source_code = inspect.getsource(func)
    return source_code
