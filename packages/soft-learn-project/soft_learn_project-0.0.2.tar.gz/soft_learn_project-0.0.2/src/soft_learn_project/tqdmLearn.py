import tqdm
import time


class TqdmLearn():
  def __init__(self) -> None:
    """tqdm = "taqaddum"（阿拉伯语中的“进展”）
    也可理解为：“快速的进度条（progress bar）”
    ---
    如果你经常跑 for 循环，或者做训练任务，它是个非常「提气质」的小工具 ✨
    """
    pass

  def install(self):
    """ conda install tqdm
    """
    pass

  def example1(self):
    # 示例 1：为循环添加进度条
    for i in tqdm.tqdm(range(100)):
      time.sleep(0.02)  # 模拟耗时操作

  def exmaple2(self):
    # 示例 2：手动控制进度
    progress_bar = tqdm.tqdm(total=1000)  # 设置总步数
    for i in range(100):
      time.sleep(0.1)
      progress_bar.update(10)      # 每步更新10个单位
    progress_bar.close()

  def exmaple_2(self):
    from tqdm import tqdm
    import pandas as pd

    tqdm.pandas()  # 激活
    # df['result'] = df['value'].progress_apply(my_function)

    return
