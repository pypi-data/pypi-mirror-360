import functools
import warnings
from functools import wraps


def deprecated(reason=""):
  """自定义 @deprecated 装饰器

  Args:
      reason (str, optional): _description_. Defaults to "".
  """
  def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
      warnings.warn(
          f"{func.__name__} is deprecated: {reason}",
          category=DeprecationWarning,
          stacklevel=2,
      )
      return func(*args, **kwargs)
    return wrapper
  return decorator

# 举例子


@deprecated(reason="Use 'new_function' instead.")
def old_function():
  print("This function is deprecated.")


def new_function():
  print("This is the new function.")


class FunctoolsLearn():
  def __init__(self) -> None:
    pass


class ErrorLoggingDecorator():
  def __init__(self) -> None:
    pass

  def error_logging_decorator(self, func):
    """定义一个修饰器，当被修饰的函数成功执行时不输出任何信息，但如果函数抛出异常，则输出错误信息，包括函数名

    Args:
        func (_type_): _description_

    Raises:
        e: _description_

    Returns:
        _type_: _description_
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      try:
        return func(*args, **kwargs)
      except Exception as e:
        function_name = func.__name__
        # import ase.parallel
        # ase.parallel.parprint()
        print(f"{function_name} 出错".center(50, '*'))
        raise e
    return wrapper


class ExamOneMethod():
  def __init__(self) -> None:
    """对类中的一个方法修饰的例子
    """
    pass

  # 对类中的一个方法进行修饰
  @ErrorLoggingDecorator().error_logging_decorator
  def example_function(self, success=True):
    if not success:
      raise ValueError("An error occurred!")


class AutoDecorateMeta(type):
  """对整个类修饰的例子 创建类时加入: metaclass=AutoDecorateMeta
  目的是类中的某个方法出错时, 会给出出错的函数名

  Args:
      type (_type_): _description_
  """
  def __new__(cls, name, bases, dct):
    for key, value in dct.items():
      if callable(value) and not key.startswith('__'):
        dct[key] = ErrorLoggingDecorator().error_logging_decorator(value)
    return super().__new__(cls, name, bases, dct)


class ExampleClass(metaclass=AutoDecorateMeta):
  def __init__(self) -> None:
    pass

  def method1(self, success=False):
    if not success:
      raise ValueError("An error occurred in method1!")
    print("method1 executed successfully")

  def method2(self, success=True):
    if not success:
      raise ValueError("An error occurred in method2!")
    print("method2 executed successfully")


if __name__ == '__main__':
  # 修饰函数示例
  ExamOneMethod().example_function(success=False)

  # 调用类方法示例
  example = ExampleClass()
  try:
    example.method1(success=True)
    example.method1(success=False)
  except Exception:
    pass

  try:
    example.method2(success=True)
    example.method2(success=False)
  except Exception:
    pass
