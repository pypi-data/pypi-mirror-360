import pathlib


class PathlibLearn():
  def __init__(self):
    pass

  def get_relative_path(self,
                        path_absolute='/xxx/yyy/',
                        dir_reference='reference_dir'
                        ):
    """将绝对路径转换为相对路径, ln -s 建立软连接的时候会很有用
    * 直接用 osLearn 模块就行了
    """
    import os
    # 定义绝对路径和参考目录
    absolute_path = pathlib.Path(path_absolute)
    reference_dir = pathlib.Path(dir_reference)
    # 转换为相对路径
    relative_path = pathlib.Path(os.path.relpath(absolute_path, reference_dir))
    # 这样不行
    # relative_path = absolute_path.relative_to(reference_dir)
    return relative_path
