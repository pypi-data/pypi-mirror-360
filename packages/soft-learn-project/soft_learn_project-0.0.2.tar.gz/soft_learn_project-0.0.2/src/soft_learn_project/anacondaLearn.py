class Anacondalearn():
  def __init__(self) -> None:
    pass

  def install(self):
    """安装anaconda
      1. sh Anaconda....sh
      2. 建立虚拟环境: `conda create -n py39 python==3.9.12`
      3. 默认进入py39环境 .zshrc 中加入 conda activate py39
      4. `conda config --add channels conda-forge`
      5. `conda install lammps`   # `conda install -c conda-forge lammps==2022.06.23`
      6. `conda install matplotlib`
      7. `conda instll pandas`
      8. `conda install mpi4py`
      9. 在 ~/.zshrc 中加入pythonpath
          1. home=/home/users/lxiaochun
          2. export PYTHONPATH=$PYTHONPATH:${home}/my_script
    4. 大功告成
    """
    pass
