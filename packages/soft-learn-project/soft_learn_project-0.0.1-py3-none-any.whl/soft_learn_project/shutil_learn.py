class ShutilLearn():
  def __init__(self) -> None:
    # shutil 模块 shutil可以简单地理解为sh + util，shell工具的意思。shutil模块是对os模块的补充，主要针对文件的拷贝、删除、移动、压缩和解压操作。
    """
    shutil.move('test.py', 'name')  # 移动文件（目录）， 如果文件存在会发生错误
    shutil.copy('../os_learn.py', 'test1.py')  # 复制
    shutil.rmtree('name')  # 只能删除目录，目录可以非空, 删除非空文件夹需要使用shutil模块
    shutil.copytree("olddir", "newdir")  # 复制文件夹.olddir和newdir都只能是目录，且newdir必须不存在
    os.system('mkdir test')  # :运行shell命令, os.system('mkdir test')
    """
    pass

  def e(self):

    pass
