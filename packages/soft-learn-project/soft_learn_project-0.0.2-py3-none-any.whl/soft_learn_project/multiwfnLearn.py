import os


class Features():
  def __init__(self) -> None:
    self.env()  # 设置环境
    """ 
    # 视频学习
    http://sobereva.com/video.html

    # 成键分析
    http://sobereva.com/379
    
    # http://sobereva.com/167
    """
    pass

  def install(self):
    """ 官网: http://sobereva.com/multiwfn/
    https://github.com/digital-chemistry-laboratory/multiwfn-mac-build

    # 在mac 环境中而不是conda 环境
    brew install flint 
    $ git clone --branch source_dist https://github.com/digital-chemistry-laboratory/multiwfn-mac-build.git
    $ cd multiwfn-mac-build
    $ cmake -B build
    $ cmake --build build
    $ cp build/multiwfn .
    """
    pass

  def env(self):
    # 修改 PATH 环境变量
    new_path = '/Users/wangjinlong/my_linux/soft_learn/multiwfn_learn/multiwfn-mac-build/build'
    os.environ['PATH'] += ':' + new_path
    return None
  
  def e1(self):
    """命令行方式运行
    # 方式1:
    multiwfn 
    根据提示进行相关的选项例如, 
    xx/1.fch
    9 
    8
    y
    0
    q
    # 方式2:
    建立文件 lbo.txt
    内容如下:
    9
    8
    y
    0
    q
    终端运行
    $ multiwfn 1.fch < lbo.txt  # 或者
    $ multiwfn 1.fch < lbo.txt 2>&1 >/dev/null
    # 方式3:
    echo -e "9\n8\ny\n0\nq" | multiwfn 1.fch 2>&1 >/dev/null
    # 运行后会在当前目录下产生分析文件 bndmat.txt
    """
    pass 
  
  def e2(self):
    """_summary_
    echo -e "17\n1\n1\n2\n-5\n5\n3\n-10\nq" | multiwfn /Users/wangjinlong/my_linux/soft_learn/multiwfn_learn/Multiwfn_3.8_dev_bin_Win64/examples/acrolein.wfn
    """
    # AIM:
    pass 
