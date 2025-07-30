
import json


class JsonLearn():
  def __init__(self) -> None:
    """
    JSON (JavaScript Object Notation) 是一种轻量级的数据交换格式。JSON 文件的文件类型是 .json
    json数据在javaScript 中 称为对象
    其用法参见： ~/my_linux/soft_learn/web-开发/JavaScript_learn/js_learn.html

    Python3 中可以使用 json 模块来对 JSON 数据进行编解码，它包含了两个函数：
    json.dumps()和json.dump() # 分别对字符串和文件中的数据进行编码。把字典变成字符串
    json.loads()和json.load() # 分别对字符串和文件中的数据进行编码。将字符串转换成字典
    内存中的字符串<->字典，文件中的字符串<->字典
    """
    pass

  def dump(self, data_dict, fname='parameters_dict.json',):
    """写入 JSON 数据到文件
    如果你要处理的是文件而不是字符串，你可以使用json.dump()和json.load()来编码和解码JSON数据。
    """

    with open(fname, mode="w", encoding='utf-8') as f:
      json.dump(data_dict, fp=f,
                ensure_ascii=False,  # 显示中文
                indent=4)  # indent 可以使结果变得好看
    print(f'data_dict 写入文件{fname}')

  def load(self, fname,):
    """从文读取数据
    """

    with open(fname, 'r') as f:
      data_dict: dict = json.load(f)  # 读入内存的是字典

    return data_dict

  def dumps(self, data):
    """字典类型转换为 JSON 对象(字符串)

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """

    # 编码成字符串, 注意里面有个参数ensure_ascii 默认是True也就是用ascII编码，要改成False,改为unicode(utf-8)编码
    json_str = json.dumps(data, ensure_ascii=False)
    # print("Python 原始数据：", repr(data))
    # print("JSON 对象：", json_str)

    return json_str

  def loads(self, json_str):
    """将 JSON 对象(字符串)转换为 Python 字典

    Args:
        json_str (_type_): _description_

    Returns:
        _type_: _description_
    """

    data_dict = json.loads(json_str)  # 将字符串转换成字典
    return data_dict
