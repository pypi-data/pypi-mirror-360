import gzip


class GzipLearn():
  def __init__(self):
    """在 Python 中，读取 .gz 文件非常简单。常用的方法是使用内置的 gzip 模块。以下是一些常见的方式：
    """
    pass

  def open_txt_gz(self, fname='xx.txt.gz'):
    with gzip.open(fname, 'rt') as f:  # 'rt' 表示读取文本模式
      content = f.read()
    return content

  def open_txt_gz_for_large_file(self, fname='xx.txt.gz'):
    # 如果文件太大，不想一次性读取到内存：
    with gzip.open(fname, 'rt') as f:
      for line in f:
        yield line

  def open_bin_gz(self, fname='xx.bin.gz'):
    with gzip.open(fname, 'rb') as f:  # 'rb' 表示读取二进制模式
      content = f.read()
      # print(content)  # 如果是二进制文件，可能会显示乱码
    return content

  def get_df_csv_gz(self, fname='xx.csv.gz'):
    # 读取 .csv.gz 文件为 pandas.DataFrame（常用）
    import pandas as pd
    df = pd.read_csv(fname, compression='gzip')
    return df
