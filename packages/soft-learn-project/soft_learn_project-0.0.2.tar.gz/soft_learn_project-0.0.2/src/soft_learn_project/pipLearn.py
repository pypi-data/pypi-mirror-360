
class PipLearn():
  def __init__(self) -> None:
    # 用法
    """
    https://packaging.python.org/en/latest/tutorials/installing-packages/

    pip cache purge  # 清理 pip 缓存的命令：
    pip list #列表
    pip -V # 查看版本
    pip show numpy #查看numpy信息 查看numpy 安装了没
    pip install pip_search 
    pip_search numpy # 以后搜索这样用 
    pip install --upgrade pip #pip 自身更新
    pip freeze #显示本地安装包的详细信息
    pip --help
    pip install numpy #安装包  # -i https://pypi.tuna.tsinghua.edu.cn/simple 参数指明从清华源下载
    s = 'pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ py4vasp'
    pip install -U numpy #更新包
    pip uninstall numpy #卸载包
    """
    # 通过文件安装
    print('pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ py4vasp')
    pass

  def install(self):
    """
    如果未安装 pip，则首先尝试从标准库中启动安装：
      python -m ensurepip --upgrade  # 安装加升级 pip 到 Python 自带的 pip 版本（注意不是 PyPI 上的最新版）；
      --
      python3 -m ensurepip --default-pip  # 明确安装 pip，但不升级现有 pip
      python3 -m pip install --upgrade pip  # 升级到最新版本的pip 

    """
    pass

  def install_package(self):
    """
      从本地 src 安装 开发模式 ，即以这种方式安装项目，使其看起来已安装，但仍然可以从 src 目录进行编辑。
        python3 -m pip install -e <path>
      安装特定的源代码压缩包。
        python3 -m pip install ./downloads/SomeProject-1.0.4.tar.gz
      安装“额外包” Extras 是包的可选“变体”，可能包括额外的依赖项，从而启用包的额外功能。如果您知道某个包发布了额外功能，可以在 pip 安装命令中包含它：
        python3 -m pip install 'SomePackage[PDF]'
      从版本控制系统安装包: 这回git clone + pip install  # 最好还是先自己克隆 再 pip install -e .
        python3 -m pip install -e SomeProject @ git+https://git.repo/some_pkg.git          # from git
        python3 -m pip install -e SomeProject @ git+https://git.repo/some_pkg.git@feature  # from a branch
        python3 -m pip install -e SomeProject @ svn+svn://svn.repo/some_pkg/trunk/         # from svn
      从替代索引安装
        python3 -m pip install --index-url http://my.package.repo/simple/ SomeProject
      在安装时搜索额外的索引，除了 PyPI
        python3 -m pip install --extra-index-url http://my.package.repo/simple SomeProject
    """

  def pip_source(self):
    """设置源 
    编辑或创建文件 ~/.pip/pip.conf
    [global]
    index-url = https://pypi.tuna.tsinghua.edu.cn/simple
    """
    s1 = 'https://pypi.mirrors.ustc.edu.cn/simple/'
    s2 = 'https://mirror.baidu.com/pypi/simple/'
    s3 = 'https://pypi.tuna.tsinghua.edu.cn/simple'
    s4 = 'https://mirrors.aliyun.com/pypi/simple/'
    s5 = 'https://pypi.douban.com/simple/'
    s6 = 'https://mirrors.huaweicloud.com/repository/pypi/simple/'
    s_list = [s1, s2, s3, s4, s5, s6]
    for s in s_list:
      print(s)

  def install_by_txt(self,):
    # 把要安装的包写入requirements.txt
    """
    matplotlib==2.2.2
    numpy==1.14.2
    """
    # 然后安装
    'pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple'
    pass

  def install_whl(self,):
    url = 'https://www.lfd.uci.edu/~gohlke/pythonlibs/'  # python 安装包的一个合集网址
    'pip3 install *.whl'  # 下载后直接安装
