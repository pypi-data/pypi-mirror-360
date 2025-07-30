import subprocess
import os
import glob
import pandas as pd
import re


class SubprocessLearn():
  def __init__(self):
    """
      总结
      subprocess.run()：推荐使用，功能强大，适用于大部分需求。
      os.system()：适用于非常简单的命令执行，只关心退出码时。
      os.popen()：适用于需要读取命令输出并进行进一步处理的简单场景，但不如 subprocess.run() 灵活。
      --- 
      subprocess.run() 是最推荐的方式，适用于大多数复杂的命令执行场景，能够捕获输出和错误，并提供更多的灵活性。
      subprocess.call() 适用于简单的命令执行，只关心退出码，不需要捕获输出。
      subprocess.check_output() 用于执行命令并捕获输出，适用于需要标准输出的场景，并且可以自动处理错误（通过抛出异常）。
    """
    pass

  def sim_example(self):
    # 执行一个简单的命令，比如 `ls`
    result = subprocess.run(['ls', '-l'], capture_output=True, text=True)
    # 输出命令的标准输出
    print('标准输出:', result.stdout)

    # 输出命令的标准错误
    print('标准错误:', result.stderr)

    # 获取命令的返回码
    print('返回码:', result.returncode)
    pass

  def CLI_cmd(self, directory, args=['ls', '-l']):
    result = subprocess.run(args=args,
                            cwd=directory,
                            env=os.environ,  # 确保环境变量正确传递
                            capture_output=True,
                            text=True,
                            # check=True,
                            )
    # print(result.stdout)
    return result

  def CLI_popen(self, directory, args=['ls', '-l']):
    """支持实时输出读取
    什么时候用 subprocess.run()？
    你只想执行一个简单的命令，不关心中间过程，只要最后的输出。
    不需要与子进程实时交互。
    💡 什么时候用 subprocess.Popen()？
    你想要 实时显示子进程输出。
    需要与子进程进行交互（比如发送输入、读取输出等）。
    要求更大的控制和自定义行为。
    """
    process = subprocess.Popen(args=args,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True,  # 确保输出是字符串而不是字节
                               cwd=directory,
                               env=os.environ,  # 确保环境变量正确传递
                               bufsize=1,  # 行缓冲，适合文本
                               universal_newlines=True,
                               )

    # 实时读取输出
    while True:
      output = process.stdout.readline()
      if output == '' and process.poll() is not None:
        break
      if output:
        print(output.strip())  # 实时打印输出行

    # 如果你想查看错误信息，也可以实时读取 stderr
    error_output = process.stderr.read()
    if error_output:
      print("Error:", error_output)
    return None

  def CLI_cmd_example(self, directory, fname_pbs):
    # 2. 提交任务
    result = subprocess.run(args=['sbatch', fname_pbs],
                            cwd=directory,
                            env=os.environ,  # 确保环境变量正确传递
                            capture_output=True,
                            text=True,
                            # check=True,
                            )
    print(result.stdout)

  def notes_关于压缩(self):
    """
      # 方案一 gzip 
      gzip 是单文件压缩工具，只能压缩单个文件（如 file.txt → file.txt.gz）。
      将目录打包为 .tar.gz（等价于 .tgz）：
      tar -czvf dir.tar.gz dir/  # 压缩
      -c：创建归档
      -z：用gzip压缩
      -v：显示进度（可选）
      -f：指定文件名
      tar -xzvf dir.tar.gz  # 解压到当前目录
      # 方案二：用 zip（兼容Windows）
      zip -r dir.zip dir/  # 压缩目录
      unzip dir.zip # 解压命令
    """
    pass

  def gzip_dir(self, directory):
    """压缩目录"""
    self.CLI_popen(
        directory=directory,
        args=['gzip', '-r', directory]
    )
    return None

  def gunzip_dir(self, directory):
    self.CLI_popen(directory=directory,
                   args=['gunzip', '-rf', directory]
                   )
    return None

  def gzip_file(self,
                directory='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/BN_codoping_sub/B_N3_Gra/O_B_N3_graphene',
                filename_key_list=['OUTCAR', 'vasprun.xml',
                                   'vaspout.h5', 'PROCAR', 'DOSCAR'],
                ):
    """压缩文件
    """
    for dirpath, dirnames, filenames in os.walk(top=directory):
      for filename in filenames:
        if filename in filename_key_list:
          fname = os.path.join(dirpath, filename)
          self.CLI_popen(
              directory=dirpath,
              args=['gzip', fname]
          )
    return None

  def gunzip_file(self,
                  directory='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/BN_codoping_sub/B_N3_Gra/O_B_N3_graphene',
                  fname_key_list=['png.gz', 'pdf.gz'],
                  ):
    for dirpath, dirnames, filenames in os.walk(top=directory):
      for filename in filenames:
        for fname_key in fname_key_list:
          if fname_key in filename:
            fname = os.path.join(dirpath, filename)
            self.CLI_popen(
                directory=dirpath,
                args=['gunzip', '-f', fname]
            )
    return None
