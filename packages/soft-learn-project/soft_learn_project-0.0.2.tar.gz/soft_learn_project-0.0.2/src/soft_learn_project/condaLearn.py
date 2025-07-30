class CondaLearn():
  def __init__(self) -> None:
    pass

  def install(self):
    string = """conda 安装
    下载: https://www.anaconda.com/ -> free download -> skip registration -> 找到合适的版本
    -> bash Anaconda3-2024.10-1-Linux-aarch64.sh, 输入yes 等, 如果没激活 base 环境 /home/wjl/anaconda3/bin/conda init bash -> 重启终端 或者 source ~/.bashrc
    - bash Anaconda3-2024.10-1-Linux-aarch64.sh -u # -u 这个命令将会覆盖现有的 Anaconda 安装，并更新到最新版本。

    """
    print(string)
    return None

  def source(self):
    string = """
    1. 查看源
        命令 conda config --show-sources
        ==> /home/xxx/.condarc <==
        channels:
        - <https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/>
        - defaults
        这里有两个源，一个是清华的源，另一个是默认的源
    2. 添加源（这里以添加清华源为例，当然也可以选择其他的源）
        添加中科大的源
        conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/
        conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/
        # https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge
        # 查看源 conda config --show-sources
        阿里云的源
        conda config --add channels <http://mirrors.aliyun.com/pypi/simple/>
    4. 移除源
        conda config --remove channels
    """
    print(string)
    return None

  def create_new_env(self):
    """建立一个环境 包括 ase, gpaw, vasp 相关 和 ovito
    conda create -n py39 python=3.9
    conda install -c conda-forge ase
    升级ase
    pip install --upgrade git+https://gitlab.com/ase/ase.git@master
    pip install --upgrade --user gpaw -i https://pypi.mirrors.ustc.edu.cn/simple/
    conda install -c conda-forge gpaw-data
    conda install --strict-channel-priority -c https://conda.ovito.org -c conda-forge ovito=3.10.6
    conda install -c conda-forge ipykernel mpi4py gfortran fftw openblas scalapack hdf5 autopep8 pymatgen py4vasp pylatex pypdf2
    pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ PyMuPDF

    ---
    * 根据已有的环境建立一个环境
    conda env export > jobflow_env.yaml
    然后使用此列表在其他机器上生成等效环境：
    执行命令: conda env create -n jobflow_env --file jobflow_env.yaml
    """
    string = """* 建立一个环境
    conda create -n py39 python=3.9
    激活环境: conda activate py39
    退出环境: conda deactivate  
    添加源: conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/
    更新包: conda update --all 
    安装包: conda install packagename, 包的名字
    """
    print(string)
    return None

  def operations(self):
    """
    ## 更新anaconda
    conda activate base
    conda update anaconda
    - Please update conda by running
    conda update -n base -c defaults conda
    ## 查看conda安装的环境
    conda env list  # 或者 conda info -e # 效果一样
    ## 创建环境
    # conda creat --name env_name python=python3.6
    conda create -n nlp python=3.6
    ## 重命名环境
    conda 其实没有重命名指令，实现重命名是通过 clone 完成的，分两步：
    ①先 clone 一份 new name 的环境
    ②删除 old name 的环境
    如，将nlp重命名成tf2
    conda create -n tf2 --clone nlp
    ## 删除环境
    conda remove -n nlp --all # 或者 conda remove  --name python36 --all

    ## 激活、退出环境
    conda activate py39
    conda deactivate

    ## 查看已有虚拟环境
    conda env list # 或者 conda info -e
    """
    pass

  def conda_init(self):
    """ * conda init zsh # conda 在zsh中初始化
    - 使终端进入 arm64 架构
    arch -arm64 /bin/zsh
    - 进入 arm64 架构 环境
    /Users/wangjinlong/opt/anaconda3/bin/conda init zsh # arm64 架构

    - 使终端进入 x86_64 架构
    arch -x86_64 /bin/zsh
    - 进入 x86_64 架构 环境
    /Users/wangjinlong/opt/x86_64_anaconda/bin/conda init zsh # x86_64 架构
    """
    pass

  def package_管理(self,):
    # conda搜索包&查看安装包的信息
    'conda search numpy'
    # 安装包：
    'conda install numpy'
    # 查看已经安装的包：
    'conda  list'
    # 更新安装包：
    'conda update -n env_name package_name'
    # 更新所有包：
    'conda upgrade --all '
    # conda 移除包
    'conda remove package_name '
    'conda remove -n env_name package_name'

    pass

  def other(self):
    # 显示环境的版本
    # conda list --revision
    # conda install --revision 0 # 回滚到0 最初版本
    pass

  def env_py311_ovito(self):
    """
      * conda install ase
      * conda install pandas
      * pip install jobflow
      * conda install jobflow
      * conda install pylatex
      * conda install py4vasp
      * conda install mp-api pymatgen
      * conda install mpi4py
      * pip install deprecated
      * pip install gpaw
      * pip install pypdf
      * conda install reportla
    """
