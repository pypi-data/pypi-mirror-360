
import dataclasses


class DataclassesLearn():
  def __init__(self):
    """* dataclasses 是 Python 标准库中的一个模块，从 Python 3.7 开始引入，旨在简化创建和管理类的过程。它提供了一个装饰器 @dataclass，可以自动为类生成常用的特殊方法，例如 __init__()、__repr__()、__eq__() 等，从而减少样板代码（boilerplate code）的书写。
    * 主要功能
    - 简化类定义 使用 @dataclass 装饰器时，只需定义类的属性，Python 会自动生成初始化方法 __init__()，不需要手动编写。
    - 支持比较和排序 @dataclass 可以自动生成比较方法（如 __eq__, __lt__ 等），以便于对象之间的比较。
    - 默认值和字段管理 通过 field() 可以控制字段的默认值、是否可比较等特性。
    - 可变和不可变类 可以通过参数 frozen=True 将类设为不可变
    ---
    * dataclasses 是一个非常实用的模块，尤其适合需要定义大量简单类的场景。它以简洁的语法提供了强大的功能，是现代 Python 编程中的重要工具之一。
    """
    pass

  def example_1(self):
    """简化类定义 使用 @dataclass 装饰器时，只需定义类的属性，Python 会自动生成初始化方法 __init__()，不需要手动编写。
    - __init__()、__repr__()
    """
    @dataclasses.dataclass
    class Person:
      name: str
      age: int
      city: str = "Unknown"  # 默认值

    # 创建实例
    p1 = Person(name="Alice", age=30)
    print(p1)  # 输出：Person(name='Alice', age=30, city='Unknown')
    # 2. 自动生成的比较方法
    p2 = Person(name="Alice", age=30)
    p3 = Person(name="Bob", age=25)
    print(p1 == p2)  # 输出：True
    print(p1 == p3)  # 输出：False

  def example_2(self):
    @dataclasses.dataclass
    class Product:
      name: str
      price: float
      discount: float = dataclasses.field(
          default=0.0, repr=False, )  # 不在 __repr__ 中显示

    p = Product(name="Laptop", price=999.99)
    print(p)  # 输出：Product(name='Laptop', price=999.99)

  def example_3(self):
    """
    @dataclass 装饰器接受以下参数：
    init：是否自动生成 __init__ 方法，默认 True。
    repr：是否自动生成 __repr__ 方法，默认 True。
    eq：是否自动生成 __eq__ 方法，默认 True。
    order：是否生成排序方法（__lt__, __le__, __gt__, __ge__），默认 False。
    unsafe_hash：是否生成 __hash__ 方法，默认 False。
    frozen：是否使实例变为不可变，默认 False。
    """
    @dataclasses.dataclass(frozen=True)
    class Point:
      x: int
      y: int

    p = Point(1, 2)
    # p.x = 10  # 会报错：dataclasses.FrozenInstanceError
