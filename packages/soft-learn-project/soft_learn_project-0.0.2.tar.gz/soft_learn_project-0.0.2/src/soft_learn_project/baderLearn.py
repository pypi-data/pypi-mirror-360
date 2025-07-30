import os
import numpy as np


class BaderLearn():
  def __init__(self) -> None:
    from vasp_learn import base, dataBase
    self.Base = base.Base()
    self.DataBase = dataBase.DataBase()
    pass

  def install(self):
    """bader 程序下载及使用: https://theory.cm.utexas.edu/henkelman/code/bader/

    bader 程序放在了 /Users/wangjinlong/my_script/sci_research/vasp_use 
    # 或者直接安装 
    conda install -c conda-forge bader
    """

    # 编译需要gfortran
    'conda install -c conda-forge gfortran'
    'cp makefile.osx_gfortran makefile'
    # 修改makefile
    # 注释掉 LINK = -static
    # FFLAGS = -O2 后面加个 -static 可以生成静态的？
    'make'  # 会生成 bader
    'ln -s ~/my_linux/soft_learn/bader_learn/bader/bader /Users/wangjinlong/my_script/sci_research/vasp_use'
    pass

  def use(self):
    """
    INCAR 中LAECHG = True  # 输出修正核心电荷需要的文件AECCAR0和AECCAR2
    https://theory.cm.utexas.edu/vtsttools_old/index.php  chgsum.pl 从这里的Script 下载也放在bin 目录下面
    'laechg': True,  # 输出修正核心电荷需要的文件AECCAR0和AECCAR2
    chgsum.pl AECCAR0 AECCAR2 # 用于产生CHGCAR_sum 文件
    bader CHG -ref CHGCAR_sum # 用于产生ACF.dat 
    ACF.dat  有一列是CHARGE 就是每个原子的电荷量, 查看POTCAR获得价电子数目 vzal, 减完就是电荷的得失
    """
    pass

  def bader_analysis_download_CHG(self,
                                  directory='xxx/single_point',
                                  exclude_key_list=['WAVECAR']):
    """下载 CHG

    Args:
        directory (str, optional): _description_. Defaults to 'xxx/single_point'.
    """

    if not os.path.exists(os.path.join(directory, "CHG")):
      print(f"{directory} 不存在 CHG->需要这个文件, 正在执行服务器同步!")
      from sci_scripts import rsync_hfeshell_合肥超算
      rsync_hfeshell_合肥超算.ssh_Rsync().rsync(
          local_dir_list=[os.path.abspath(directory)],
          exclude_key_list=exclude_key_list,
          download=True,
          rsync_pars='')
      return None
    else:
      return None

  def bader_analysis_get_ACF(self,
                             directory='xxx/single_point',
                             recalc=False,
                             cube_or_chg="chg",
                             is_hpc=False,):
    """
      bader 分析, 获得 ACF.dat

      Args:
          directory (str, optional): _description_. Defaults to 'xxx/single_point'.
          recalc (bool, optional): _description_. Defaults to False.
          cube_or_chg (str, optional): _description_. Defaults to "chg".

      Returns:
          _type_: _description_
    """
    if is_hpc:
      bader_exe = 'bader_hpc'
      os.environ['PATH'] += ':/public/home/wangjl/job/science_research/sci_scripts/bin:/public/home/wangjl/job/science_research/sci_scripts/vasp_use/vtstscripts-971'
    else:
      bader_exe = 'bader'
    if recalc:
      os.remove(os.path.join(directory, "ACF.dat"))
    if os.path.exists(os.path.join(directory, "ACF.dat")):
      return None
    else:
      cwd = os.getcwd()
      os.chdir(directory)
      # 到底用 chg 还是 cube？
      if cube_or_chg == "chg":
        # 或者 CHGCAR
        bader_cmd = f"chgsum.pl AECCAR0 AECCAR2 && {bader_exe} CHG -ref CHGCAR_sum"
        # bader_cmd = 'bader CHG' # 直接运行这个命令好像是错误的
      elif cube_or_chg == "cube":  # 使用cube 计算的电荷数值不对 以后再考虑如何修改
        file_cube = self.Base.get_cube_from_CHG(directory=directory,
                                                chg_file="CHG")
        bader_cmd = bader_exe + ' ' + file_cube
      # 执行命令
      try:
        with os.popen(bader_cmd) as f:  # bader CHGCAR
          content = f.read()
          print(f"{directory} ->bader 分析完毕.")
      except:
        print(f"{directory} ->bader 分析失败!")

      os.chdir(cwd)
      return None

  def bader_analysis_read_ACF(self, directory='xxx/single_point',):
    file_ACF = os.path.join(directory, "ACF.dat")
    file_ACF_gz = os.path.join(directory, "ACF.dat.gz")

    if os.path.exists(file_ACF):
      charges = []
      with open(file=file_ACF) as fd:
        for line in fd:
          words = line.split()
          if len(words) == 7:
            charges.append(float(words[4]))
    elif os.path.exists(file_ACF_gz):
      import gzip
      charges = []
      with gzip.open(file_ACF_gz, mode='rt') as f:
        for line in f:
          words = line.split()
          if len(words) == 7:
            charges.append(float(words[4]))
    else:
      pass

    return np.array(charges)

  def bader_analysis_with_ACF(self,
                              directory='xxx/single_point', cube_or_chg="chg"):
    """
      获得每个原子所带的电荷
      atoms = Base().set_initial_charge 加入原子磁矩了

      Args:
          directory (_type_): _description_
          cube_or_chg (str, optional): _description_. Defaults to 'chg'.

      Returns:
          _type_: _description_
    """

    atoms = self.Base.set_initial_charge(directory=directory,
                                         cube_or_chg=cube_or_chg
                                         )
    zval = atoms.get_initial_charges()  # 一开始带的电荷
    # 从ACF.dat 读取电荷并赋给atoms
    # 所带的电子
    electrons = self.bader_analysis_read_ACF(directory=directory)
    charges = zval + (-electrons)
    atoms.set_initial_charges(charges=charges)

    return atoms

  def bader_analysis(self,
                     directory='xxx/single_point',
                     recalc=False,
                     cube_or_chg="chg",
                     is_hpc=False):
    """
      单点计算后去分析, 不包含单点计算, directory 应该是 single_point 目录, calc_single_point 包含了 AECCAR0 的输出
      单点计算: Features().prepare_and_calc_single_point_for_bader_and_bader_analysis()  包含了bader 分析
      参考网页 https://zhuanlan.zhihu.com/p/541611145
      from bader_learn import baderLearn
      baderLearn.BaderLearn().install()

      返回bader分析后 每个原子所带的电荷量
      cmd_bader: bader -p all_atom -p atom_index CHG 可以产生  BvAt0017.dat 这些文件
      eg:
      atoms = vaspLearn.Features().bader_analysis(directory='adsorbate_TM_B2C3N/N2_Mn_B2C3N/')
      mask = [atom.index for atom in atoms if atom.position[2] > 10] # N2 的 index
      eletrons_obtained_by_N2 = atoms[mask].get_initial_charges().sum() # 结果-0.548505 表明 N2 获得衬底的电子
      ---
      calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
      atoms = calc.get_atoms()
      # You can attach the output charges from the bader program to the atoms for further processing:
      # 这个分析不准确, 比如N2, 程序认为N只有三个电子, 事实上vasp势中N有5个价电子
      ase.io.bader.attach_charges(
          atoms=atoms, fileobj=os.path.join(directory, 'ACF.dat'))

      Args:
          directory (_type_): directory 应该是 single_point 目录, single_point 包含了 AECCAR0 的输出
          recalc (bool, optional): _description_. Defaults to False.
          cmd_bader (str, optional): _description_. Defaults to 'bader CHG'.
          chg_or_cube : 建议使用chg cube分析数值不太对
      Returns:
          _type_: _description_
    """

    if os.path.exists(os.path.join(directory, 'ACF.dat')) or os.path.exists(os.path.join(directory, 'ACF.dat.gz')):
      pass
    else:
      self.bader_analysis_download_CHG(directory=directory)
      self.bader_analysis_get_ACF(directory=directory,
                                  recalc=recalc,
                                  cube_or_chg=cube_or_chg,
                                  is_hpc=is_hpc)
    atoms = self.bader_analysis_with_ACF(
        directory=directory, cube_or_chg=cube_or_chg)

    return atoms
