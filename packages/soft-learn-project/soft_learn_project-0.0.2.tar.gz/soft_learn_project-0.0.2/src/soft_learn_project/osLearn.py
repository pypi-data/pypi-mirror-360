import time
import os  # 建议使用 "import os" 风格而非 "from os import *"。这样可以保证随操作系统不同而有所变化的 os.open() 不会覆盖内置函数 open()。


class OsLearn():
  def __init__(self) -> None:
    """
    https://docs.python.org/zh-cn/3.9/library/os.html#random-numbers
    os 本模块提供了一种使用与操作系统相关的功能的便捷式途径。 如果你只是想读写一个文件，请参阅 open()，
    如果你想操作文件路径，请参阅 os.path 模块，如果你想读取通过命令行给出的所有文件中的所有行，请参阅 fileinput 模块。
    为了创建临时文件和目录，请参阅 tempfile 模块，对于高级文件和目录处理，请参阅 shutil 模块。
    在使用 os 这样的大型模块时内置的 dir() 和 help() 函数非常有用:
    print(dir(os))
    help(os)

    # 常用函数
    os.exit():终止当前进程
    os.sep:取代操作系统特定的路径分隔符
    os.name:指示你正在使用的工作平台。比如对于Windows，它是'nt'，而对于Linux/Unix用户，它是'posix'。
    os.getcwd:得到当前工作目录，即当前python脚本工作的目录路径。
    os.chdir(dirname):改变工作目录到dirname
    os.getenv() 和os.putenv:分别用来读取和设置环境变量
    os.listdir():返回指定目录下的所有文件和目录名
    os.remove(file):删除一个文件
    os.stat（file）:获得文件属性
    os.sep #:取代操作系统特定的路径分隔符
    os.linesep:给出当前平台的行终止符。例如，Windows使用'\r\n'，Linux使用'\n'而Mac使用'\r'
    os.name # 使用的工作平台。比如对于Windows，它是'nt'，而对于Linux/Unix用户，它是'posix'。
    os.mkdir(name)  # 创建目录
    os.rmdir(name)  # 删除空目录
    os.curdir:返回当前目录（'.'）
    os.rename("oldname","newname")  重命名文件（目录）.文件或目录都是使用这条命令
    os.removedirs（r“c：\python”）:删除多个目录

    #  其他一些命令
    os.path.exists(name):判断是否存在文件或目录name
    os.path.split()  # 返回一个路径的目录名和文件名
    os.path.isfile()
    os.path.isdir()分别检验给出的路径是一个目录还是文件
    os.path.getsize(name):或得文件大小，如果name是目录返回0L
    os.path.abspath(name):获得绝对路径
    os.path.isabs():判断是否为绝对路径
    os.path.normpath(path):规范path字符串形式
    os.path.split(name):分割文件名与目录（事实上，如果你完全使用目录，它也会将最后一个目录作为文件名而分离，同时它不会判断文件或目录是否存在）
    os.path.splitext():分离文件名和扩展名
    os.path.join(path,name):连接目录与文件名或目录
    os.path.basename(path):返回文件名
    os.path.dirname(path):返回文件路径
    """
    pass

  def dir_operation(self):
    def change_permissions(path):
      # 递归更改文件和目录的权限
      for root, dirs, files in os.walk(path):
        for dir in dirs:
          dir_path = os.path.join(root, dir)
          os.chmod(dir_path, 0o744)
        for file in files:
          file_path = os.path.join(root, file)
          os.chmod(file_path, 0o744)
    # os.walk() 返回 dirpath, dirnames, filenames, 很好用
    # 目录操作
    """
    shutil.copyfile("oldfile","newfile")　　复制文件:oldfile和newfile都只能是文件
    shutil.copy("oldfile","newfile")  oldfile只能是文件夹，newfile可以是文件，也可以是目标目录
    shutil.copytree("olddir","newdir")  复制文件夹.olddir和newdir都只能是目录，且newdir必须不存在
    shutil.rmtree("dir")  空目录、有内容的目录都可以删
    """
    pass

  def file_operation(self, fname='os_learn.py'):
    # 修改为可执行权限，修改文件权限和时间戳
    os.chmod("tt.py", mode=0o744)
    # 获取绝对路径
    path1 = os.path.abspath(fname)
    print(f'当前的绝对路径为{path1}')
    # 获取文件所在目录
    os.path.dirname(path1)
    # 获取路径的 最后一个名字 可以是文件也可以是目录
    fname = os.path.basename(path1)
    # 分离文件名的前缀和后缀
    prefix, sufix = os.path.splitext(path1)
    print(f'文件的前缀和后缀为{prefix} 和 {sufix}')

    # 获得文件属性
    st = os.stat(fname)
    # time of most recent access 最近的访问时间,只要打开这个文件就算是访问
    time_float = st.st_atime   # 是个时间浮点数
    # os.path.getatime('os_learn.ipynb') # 或者这样
    time_float = st.st_mtime  # 文件的内容被修改的时间
    time_float = st.st_ctime  # 创建时间  或者用 os.path.getctime('os_pa.py')
    time_str = time.ctime(time_float)

    print(f'文件的创建时间为{time_str}')
    pass

  def get_file_size(self, fname='xx/yy'):
    fsize = os.path.getsize(fname)/1e+6  # MB
    return fsize

  def run_cmd_learn(self,):
    # 执行python脚本或者终端命令
    # method 1
    order_str = 'python hello_word.py'
    with os.popen(order_str, 'r') as f:  # 获取执行python脚本执行的结果
      res = f.read()  # res接受返回结果
    # method 2
    # 在调用os.system()时，会直接将传进来的Python脚本输出内容打印在控制台，而返回结果为0或1，0代表success，1表示failed
    res = os.system(order_str)
    print(res)

    # 执行python 命令
    command_line_str = "python -c 'print(\"Hello, World!\")'"
    with os.popen(command_line_str, 'r') as f:  # 获取执行python脚本执行的结果
      res = f.read()  # res接受返回结果
    print(res)

  def run_cmd_popen(self, cmd='python hello_word.py'):
    """* 执行python脚本或者终端命令
    # 最好是使用subprocess 包
    """

    with os.popen(cmd=cmd, mode='r') as f:  # 获取执行python脚本执行的结果
      # res = f.readlines()  # res接受返回结果
      res = f.read()  # res接受返回结果
    return res

  def run_cmd_system(self, cmd='python hello_word.py'):
    """* 执行终端命令
    # 最好是使用subprocess 包
    """

    # 在调用os.system()时，会直接将传进来的Python脚本输出内容打印在控制台，而返回结果为0或1，0代表success，1表示failed
    res = os.system(command=cmd)
    return res

  def get_home_variabble(self,):
    # 获得 家目录变量
    os.environ['HOME']
    os.path.expandvars('$HOME')
    os.path.expanduser('~')
    pass

  def set_envvar(self,):
    # 设置变量
    # 在python环境中执行
    path_lmpbin = os.popen('which vasp_std').read().strip()
    path_lmpbin = '/Users/wangjinlong/opt/anaconda3/envs/lammps/bin/lmp_mpi'
    os.environ['ASE_LAMMPSRUN_COMMAND'] = f'mpiexec --np 4 {path_lmpbin}'
    result = os.system('echo $ASE_LAMMPSRUN_COMMAND')
    result = os.popen('echo $ASE_LAMMPSRUN_COMMAND').read().strip()
    pass

  def get_relative_path(self,
                        absolute_path='/Users/wangjinlong/Documents/project/file.txt',
                        reference_dir='/Users/wangjinlong/Documents',):
    """根据参考路径获得绝对路径的相对路径
    """
    # 转换为相对路径
    relative_path = os.path.relpath(absolute_path, reference_dir)
    return relative_path
