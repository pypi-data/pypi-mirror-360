import monty
import monty.serialization
import monty.io
import monty.json
import monty.math


class MontyLearn():
  def __init__(self):
    """https://github.com/materialsvirtuallab/monty

    """
    pass

  def install(self):
    string = """pip install monty
    conda install monty
    """
    print(string)
    return None

  def dumpfn(self,
             data={"name": "Alice", "age": 30,
                   "hobbies": ["reading", "cycling"]},
             fname_json="data.json",
             ):
    """将数据保存为 JSON 或者 yaml 文件

    Args:
        data (dict, optional): _description_. Defaults to {"name": "Alice", "age": 30, "hobbies": ["reading", "cycling"]}.

    Returns:
        _type_: _description_
    """
    monty.serialization.dumpfn(data, fn=fname_json)
    print(f'文件保存在-> {fname_json}')
    return None

  def loadfn(self, fname_json="data.json"):
    """ 从文件中读取数据

    Args:
        fname_json (str, optional): _description_. Defaults to "data.json".

    Returns:
        _type_: _description_
    """

    data = monty.serialization.loadfn(fn=fname_json)
    return data

  def example_serialization(self):
    """1. JSON/YAML 的序列化与反序列化
    """

    data = {"name": "Alice", "age": 30, "hobbies": ["reading", "cycling"]}

    # 将数据保存为 JSON 文件
    monty.serialization.dumpfn(data, "data.json")

    # 从文件中读取数据
    loaded_data = monty.serialization.loadfn("data.json")
    print(loaded_data)

    return None

  def example_MSONable(self):
    """Monty 提供了 MSONable 类，允许对象被序列化为 JSON 或 YAML。
    """
    from monty.json import MSONable

    class Person(MSONable):
      def __init__(self, name, age):
        self.name = name
        self.age = age

    # 创建对象并序列化
    person = Person(name="Bob", age=25)
    person_json = person.as_dict()
    print(person_json)
    return None

  def example_zopen(self):
    """使用 Monty 的 zopen 读取压缩文件或远程资源：
    """
    from monty.io import zopen
    with zopen("example.txt.gz", "rt") as f:
      for line in f:
        print(line.strip())

  def example_utils(self):
    """有一些 科学计算工具
    """
    from monty.math import gcd
    print(gcd(48, 18))  # 输出最大公约数：6
    return None
