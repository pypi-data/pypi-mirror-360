class DpGen():
  def __init__(self) -> None:

    pass

  def install(self):
    """https://tutorials.deepmodeling.com/en/latest/
    # 直接根据官网上的教学来安装, 因为这应该是最新版本的安装方式
    conda create -n dpgen python=3.9
    pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ dpgen deepmd-kit
    # 不建议
    https://www.bilibili.com/video/BV1ZZ4y1k7d2/?spm_id_from=333.999.0.0&vd_source=5ec84b7f759de5474190c5f84b86a564
    # 安装 dpdata
    # pip install dpdata
    conda install -c conda-forge dpgen # 好像安装了这个就自动安装dpdata 了
    # 
    创建 CPU 版本 的 DeePMD-kit 和 LAMMPS的 Conda环境:
    conda create -n deepmd deepmd-kit=*=*cpu libdeepmd=*=*cpu lammps-dp -c https://conda.deepmodeling.org
    创建 GPU 版本 的 DeePMD-kit 和 LAMMPS的 Conda环境(可选CUDA版本10.1 or 11.3):conda create -n deepmd deepmd-kit=*=*gpu libdeepmd=*=*gpu lammps-dp cudatoolkit=11.3 horovod -chttps://conda.deepmodeling.org
    可以指定DeePMD-kit的版本号，比如:2.0.3:
    conda create -n deepmd deepmd-kit=2.0.3=*cpu libdeepmd=2.0.3=*cpu lammps-dp=2.0.0 horovod -chttps://conda.deepmodeling.org
    """

  def learn(self):
    """https://github.com/deepmodeling/deepmd-kit
    https://github.com/deepmodeling/dpgen
    https://github.com/deepmodeling/dpdata
    DeePMD-kit网站
    https://deepmodeling.org/
    相关视频[ChengLab]DeePMD-kit:化学与机器学习的结合https://www.bilibili.com/video/av414666336Hackathon _2 DeePMD-kit:https://www.bilibili.com/video/av291801113[ChengLab]DP-GEN:深度势能生成器教程https://www.bilibili.com/video/av66965740420210703 王涵 基于深度学习的分子动力学模拟https://www.bilibili.com/video/av462185202
    """
