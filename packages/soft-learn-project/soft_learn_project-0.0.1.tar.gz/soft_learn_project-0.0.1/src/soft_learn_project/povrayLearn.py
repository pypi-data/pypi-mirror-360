
import os


class PovrayLearn():
  def __init__(self) -> None:
    """ 学习官网: https://www.povray.org/documentation/3.7.0/t2_2.html#t2_2_1
    """
    pass

  def install(self):
    s = "brew install povray"
    pass

  def usage(self):
    # 1. 准备 x.pov 文件
    # 2. $povray +P x.pov
    # 3. 就会在当前目录下生成 x.png
    os.system('povray +P x.pov')
    pass
