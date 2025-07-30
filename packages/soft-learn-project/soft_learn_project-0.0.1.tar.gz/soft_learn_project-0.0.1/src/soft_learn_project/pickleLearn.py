import pickle


class PickleLearn():
  def __init__(self) -> None:
    """把内存中的数据变为可存储或传输的过程称为序列化 pickling
   python 提供了pickle 函数用于序列化, 把变量内容从新读到内存里称为反序列化unpickling
    """
    pass

  def dump_pyobj(self, pyobj, fname='data_pyobj'):
    """dumps方法可以把任意对象序列化成bytes, 然后把bytes写入到 file-like object 中

    Args:
        pyobj (_type_): _description_
        fname (str, optional): _description_. Defaults to 'data_pyobj'.
    """
    with open(file=fname, mode="wb") as f:
      pickle.dump(pyobj, f)
    print(f'pyobj 保存为-> {fname}')

  def load_pyobj(self, fname='data_pyobj'):
    """从文件读取 pyobj

    Args:
        fname (str, optional): _description_. Defaults to 'data_pyobj'.

    Returns:
        _type_: _description_
    """

    with open(fname, mode="rb") as f:
      print(f'fobj_name -> {fname}')
      pyobj = pickle.load(f)
    return pyobj

  def example(self, fname='/Users/wangjinlong/my_linux/soft_learn/py_package_learn/pickle_learn/data'):
    a_dict = {"name": "bob", "age": 18, "score": 89}
    self.dump_pyobj(pyobj=a_dict,
                    fname=fname)
    pyobj = self.load_pyobj(fname=fname)
    return pyobj
