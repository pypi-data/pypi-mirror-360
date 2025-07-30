import yaml
import maggma.stores


class PyyamlLearn():
  def __init__(self):
    """home: https://github.com/yaml/pyyaml?tab=readme-ov-file
    Python的全功能YAML处理框架
    docs: https://pyyaml.org/wiki/PyYAMLDocumentation
    """
    pass

  def install(self):
    string = """conda install pyyaml"""
    print(string)
    return None

  def example_load(self):
    """包含一个 文档使用 load 多个使用 load_all
    """
    document = """
      a: 1
      b:
        c: 3
        d: 4
    """
    l = yaml.load(stream=document, Loader=yaml.Loader)
    yaml.load(stream=open('x.yaml', mode='r'),
              Loader=yaml.Loader)
    documents = """
    ---
    name: The Set of Gauntlets 'Pauraegen'
    description: >
        A set of handgear with sparks that crackle
        across its knuckleguards.
    ---
    name: The Set of Gauntlets 'Paurnen'
    description: >
      A set of gauntlets that gives off a foul,
      acrid odour yet remains untarnished.
    """
    for data in yaml.load_all(stream=documents, Loader=yaml.Loader):
      print(data)
    pass

  def load(self, fname='x.yaml'):
    with open(file=fname, mode='r') as f:
      for data in yaml.load_all(stream=f, Loader=yaml.Loader):
        yield data

  def dump(self,
           dict_list,
           fname='xxx/x.yml'):
    with open(file=fname, mode="w") as f:
      yaml.dump_all(documents=dict_list,
                    stream=f)
    return None

  def write_yaml(self, store: maggma.stores.MongoURIStore,
                 fname='xxx/x.yml'):
    """写入到 .yaml 文件

    Args:
        store (_type_): _description_
    """
    self.dump(dict_list=[store.as_dict()], fname=fname)
    # print(f'写入文件:{fname}')
    return None
