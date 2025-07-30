import numpy as np
import os
import ase
import ase.build
import ase.calculators
import ase.calculators.lammpslib


class Learn():
  def __init__(self):
    """获取势文件的网址: https://atsimpotentials.readthedocs.io/en/latest/potentials/eam_tabulation.html
    https://www.ctcms.nist.gov/potentials/

    """
    pass

  def string_install2(self):
    """
    conda install clang_osx-arm64 clangxx_osx-arm64 -c conda-forge
    # 在mac venv 环境下
    1. git clone -b release https://github.com/lammps/lammps.git mylammps
    2. cd src/MAKE; cp MACHINES/Makefile.mac_mpi .; cd ..
    * 修改:
    CC =	 	/opt/homebrew/bin/mpicxx
    CCFLAGS =	-O3  -std=c++17
    LINK =		/opt/homebrew/bin/mpicxx
    LINKFLAGS =	-O3 -std=c++17
    JPG_INC =       -I/opt/homebrew/Cellar/jpeg-turbo/3.0.4/include
    JPG_PATH = 	-L/opt/homebrew/Cellar/jpeg-turbo/3.0.4/lib
    JPG_LIB =	-ljpeg
    3. make yes-MANYBODY
    4. make clean-all;
    5. make mac_mpi mode=shlib -j8
    # 操作完成后, 进入 conda 环境, make install-python
    """
    pass

  def string_install(self):
    """ 安装python中的lammps模块
    * old 过去的记录
    url = 'https://docs.lammps.org/Howto_pylammps.htm'
    在集群建立lammps环境
    # 1. 安装autojump
    from autojump_learn import autojumpLearn
    autojumpLearn.AutojumpLearn().install()
    # 2. 安装conda 环境
    from anaconda_learn import anacondaLearn
    anacondaLearn.Anacondalearn().install()
    # 3. 可能还需要安装glibc
    from linux_learn import linuxLearn
    linuxLearn.LinuxLearn().install_glibc()
    """

    string = """lammps 安装:
    * 1. 直接安装:
    sudo apt install lammps # linux
    brew install lammps # mac
    which lmp_mpi
    ---
    * 2. 从source安装:
    cd xx/src/MAKE
    cp MACHINES/Makefile.mac_mpi Makefile.mpi
    修改  CC, LINK, JPG_INC, JPG_PATH
    cd ../src # 进入src 目录
    make # 直接make会显示make选项
    make yes-basic; make replica;
    make yes-python # lmp安装python 命令, 可能要修改下 此目录 lib/python 中的Makefile.lammps
    # 编译完成后就会在src中出现lmp_mpi, 会在~/job/soft_learn/lammps_learn/package/lammps_newest/python 安装lammps 包,
    make mpi mode=shlib -j8
    # mode=shlib 的加入会在src中编译动态的 liblammps.so文件
    # 安装 lammps 的python包, 或者 export PYTHONPATH=${PYTHONPATH}:${HOME}/lammps/python, export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${HOME}/lammps/src
    在自己的环境中(如 py3918) 环境中执行: make install-python
    测试:
    import lammps
    lmp = lammps.lammps()
    ---
    或者是不用在 src 中 make install-python 而是加上路径 https://docs.lammps.org/Python_install.html
    # !export PYTHONPATH=${PYTHONPATH}:/Users/wangjinlong/job/soft_learn/lammps_learn/package/mylammps/python
    # !export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/Users/wangjinlong/job/soft_learn/lammps_learn/package/mylammps/python/src
    """
    print(string)
    return None

  def string_calc(self):
    """https://wiki.fysik.dtu.dk/ase/ase/calculators/lammpsrun.html#setting-up-an-opls-calculation
    ase_lammps
    """
    string = """lammps 官网: https://www.lammps.org/
    通过学习例子来学习:
    找到安装目录中的例子: 我的是在 /opt/homebrew/Cellar/lammps/ \
        20240829-update1/share/lammps/examples
    或者直接从官网上下载安装源代码, 里面有 examples 目录
    在 examples/melt 中执行: lmp_mpi -in in.melt, 你从屏幕中看到的就是计算过程, 通过学习 in.melt 中参数的意义逐步熟悉命令
    in.melt 中加入: dump 1 all custom 50 1.dump id type x y z 再次运行 lmp_mpi -in in.melt 你会得到 1.dump, 通过ovito 打开可以看融化过程
    查找命令的网址: https://docs.lammps.org/Manual.html
    一些教学网址: https://www.lammps.org/tutorials.html
    """
    print(string)
    return None

  def pair_style(self):
    # 一个机器学习势例子
    url = 'https://docs.lammps.org/pair_agni.html'
    dpath = '/Users/wangjinlong/my_linux/soft_learn/lammps_learn/package/lammps_newest/examples/PACKAGES/agni'
    # in_file 设置
    'pair_style agni'
    'pair_coeff * * Al_jpc.agni Al'
    # 以后再看 pair_coeff 里面对 Al_jpc.agni 文件格式的描述

    pass

  def note(self):
    """交流记录, 以后可能也会用到
    """
    s1 = """import lammps
    from soft_learn.lammps_learn import lammpsLearn

    # lb = lammpsLearn.Basic()
    lmp = lammps.lammps(
        cmdargs=['-log', '/Users/wangjinlong/Desktop/lmp_test/log.lammps'])
    # 1. 初始化
    lmp.command('units metal')
    lmp.command('dimension 3')
    lmp.command(f'boundary  p p p')
    lmp.command("atom_style atomic")  # molecular  #atomic
    lmp.command("atom_modify map array sort 0 0")  # prd neb 需要sort 0 0确定原子编号不变
    lmp.command(f'timestep 0.001')
    lmp.command(f'thermo 100')
    # 2. 构建模型
    lmp.command(f'lattice bcc 3.165')
    lmp.command(f"region box block -5 5 -5 5 -5 5")
    lmp.command(f'create_box 3 box')
    lmp.command(f'create_atoms 1 box')
    # lmp.command(f'group G_del id 1109')
    # lmp.command(f'delete_atoms group G_del')  # compress yes
    lmp.command('create_atoms 1 single 0.1 0.1 0.1')
    # 3. 势函数
    pair_style_str = 'eam/alloy'
    pair_coeff_str = f'* * /Users/wangjinlong/job/soft_learn/lammps_learn/potential/WHHe.eam_bonny/potential-WHHe-EAM2.eam.alloy W H He'
    lmp.command(f'pair_style {pair_style_str}')
    lmp.command(f'pair_coeff {pair_coeff_str}')
    lmp.command('neighbor 2.0 bin')
    lmp.command('neigh_modify delay 0 every 1 check yes')

    # 4. run
    lmp.command(f'compute cna all cna/atom 4')
    lmp.command(f'group G_type1 type 1')
    lmp.command(
        f'compute coord G_type1 coord/atom cutoff 3.0 group G_type1')  # 1
    lmp.command(
        f'dump 1 all custom 10 /Users/wangjinlong/Desktop/lmp_test/1.dump id type x y z vx vy vz c_cna c_coord')
    lmp.command("thermo_style custom step pe lx press")
    lmp.command(f'minimize 0 0.001 2000 10000')
    lmp.command('run 0')
    lmp.command('write_data /Users/wangjinlong/Desktop/lmp_test/1.data')
    lmp.command('write_restart /Users/wangjinlong/Desktop/lmp_test/restart')
    # ---
    # 方便调试, 如果 in文件出错随时修改
    lmp.get_thermo('lx'), lmp.get_thermo('pe')
    # 查看信息
    lmp.command('info compute')
    # ---
    # 对于较大体系 以及 neb prd 计算 还是需要 获得 in 文件 用服务去算
    lmp = lammps.PyLammps()
    lmp.append_cmd_history('units metal')
    lmp.append_cmd_history('dimension 3')
    lmp.append_cmd_history(f'boundary  p p p')
    # ...
    lmp.write_script(filepath='/Users/wangjinlong/Desktop/lmp_test/in.lmp')
    """
    pass


class LammpsLearn():
  def __init__(self):
    """# 推荐这个
    最好用的就是AseLammpslib, 当前类就是基于AseLammpslib的封装 https://wiki.fysik.dtu.dk/ase/ase/calculators/lammpslib.html
    ---
    升级到最新版本 LAMMPSlib 的例子就可以跑通
    pip install git+https://gitlab.com/ase/ase.git
    ---
    只有 is_recalc 时, atoms 才包含 calc(lammpslib) 否则是 从文件 optimization.traj 中读取的atoms
    --- 
    LAMMPS provides a set of python functions to allow execution of the underlying C++ LAMMPS code. The functions used by the LAMMPSlib interface are:

    from lammps import lammps
    lmp = lammps(cmd_args)  # initiate LAMMPS object with command line args
    lmp.scatter_atoms('x', 1, 3, positions)  # atom coords to LAMMPS C array
    lmp.command(cmd)  # executes a one line cmd string
    lmp.extract_variable(...)  # extracts a per atom variable
    lmp.extract_global(...)  # extracts a global variable
    lmp.close()  # close the lammps object
    """
    super().__init__()
    from . import lammpslibLearn, aselammpsLearn
    # ase 中 有两个lammps包, 这是其中 lammps
    self.aselammpsLearn = aselammpsLearn
    # lammps 中带的 python 包
    self.lammpslibLearn = lammpslibLearn
    pass

  def get_calc(self,
               directory='.',
               is_save_log_calc=False,
               atom_types={'W': 1, 'H': 2, 'He': 3},
               lmpcmds=['pair_style eam/alloy',
                        'pair_coeff * * /Users/wangjinlong/job/soft_learn_project/src/soft_learn_project/lammps_learn/data/potentials/WHHe-EAM2.eam.alloy W H He',]
               ):
    """log_file = os.path.join(directory, 'lammps.log')
    ---
    通过该方法更改属性
    """

    if not os.path.exists(directory):
      os.makedirs(directory)
    log_file = os.path.join(
        directory, 'lammps.log') if is_save_log_calc else None
    calc = ase.calculators.lammpslib.LAMMPSlib(directory=directory,
                                               log_file=log_file,
                                               lmpcmds=lmpcmds,
                                               atom_types=atom_types,
                                               )
    return calc

  def example_NiH(self, directory='.',
                  is_save_log_calc=False,
                  ):

    Ni = ase.build.bulk('Ni', cubic=True)
    H = ase.Atom('H', position=Ni.cell.diagonal()/2)
    NiH: ase.Atoms = Ni + H

    self.get_calc(directory=directory,
                  is_save_log_calc=is_save_log_calc,
                  lmpcmds=['pair_style eam/alloy',
                           'pair_coeff * * /Users/wangjinlong/job/soft_learn/lammps_learn/potential/MD_pot/NiAlH_jea.eam.alloy Ni H',],
                  atom_types={'Ni': 1, 'H': 2})

    NiH.calc = self.calc
    pe = NiH.get_potential_energy()
    print(f'势能为 {pe}')
    return NiH

  def other_run(self, calc: ase.calculators.lammpslib.LAMMPSlib):
    """calc 可以继续使用
    """
    # self.get_pe(atoms=calc.atoms, directory=calc.directory)
    dump_element_list = ['W', 'H', 'He']
    calc.lmp.command('fix Fnve all nve')
    calc.lmp.command('fix Flangevin all langevin 1300 1300 0.1 3 zero yes')
    calc.lmp.command(
        'dump 1 all custom 10 1.dump id type element mass x y z vx vy vz')
    calc.lmp.command(f"dump_modify 1 element {' '.join(dump_element_list)}")
    calc.lmp.command('run 100')
    return calc

  def my_example_neb_He_migrate(self,
                                directory='/Users/wangjinlong/my_server/my/W_Re_potential/xx',
                                is_plot_fig=True,
                                is_save_fig=False,
                                is_recalc=True):
    if is_recalc:
      os.remove(os.path.join(directory, 'neb.traj'))
    atoms = ase.build.bulk('W', cubic=True, a=3.14).repeat([4, 4, 4])
    He = ase.Atom(symbol='He', position=np.array([0.5, 0, 0.25])*3.14)
    atoms += He
    initial = self.AseLearn.calc_relaxation_general(
        calc=self.get_calc(directory=directory),
        atoms=atoms.copy(),
        fmax=0.05,)
    atoms = self.Model.set_atom_position(atoms=atoms.copy(),
                                         atom_index=128,
                                         position=np.array([0.25, 0, 0.5])*3.14)
    final = self.AseLearn.calc_relaxation_general(
        atoms=atoms,
        calc=self.get_calc(directory=directory),
        fmax=0.05,)

    nebtools = self.NEB.run_neb_wrapper(
        calc=self.get_calc(directory=directory),
        atoms_initial=initial,
        atoms_final=final,
        directory=directory,
        nimages=3,
        is_plot_fig=is_plot_fig,
        is_recalc=is_recalc,
        is_save_fig=is_save_fig,
    )
    return nebtools

  # 具体的计算
  def get_data_dict_all(self,
                        name='W',
                        a=3.14,
                        is_save_traj=False,
                        is_save_log=False,
                        is_recalc=False):
    self.get_lc_a(name=name, a=a,
                  opt_name='lbfgs',
                  is_save_traj=is_save_traj,
                  is_save_log=is_save_log,
                  is_recalc=is_recalc)
    self.get_E_patom(name=name, a=a,
                     opt_name='lbfgs',
                     is_save_traj=is_save_traj,
                     is_save_log=is_save_log,
                     is_recalc=is_recalc
                     )
    self.get_data_moduli(name=name, a=a,
                         is_save_traj=is_save_traj,
                         is_save_log=is_save_log,
                         is_recalc=is_recalc
                         )
    self.get_E_atom_in_vacuum(name=name)
    self.get_E_cohensive(name=name, a=a,
                         is_save_traj=is_save_traj,
                         is_save_log=is_save_log,
                         is_recalc=is_recalc
                         )
    self.get_E_f_vacancy(name=name, a=a,
                         opt_name='lbfgs',
                         is_save_traj=is_save_traj,
                         is_save_log=is_save_log,
                         is_recalc=is_recalc,
                         box_size=[5]*3,)
    for direction in ['100', '110', '111']:
      self.get_E_f_SIA_for_bcc(name=name, a=a,
                               direction=direction,
                               box_size=[9]*3,
                               opt_name='fire2',
                               is_save_traj=is_save_traj,
                               is_save_log=is_save_log,
                               is_recalc=is_recalc,
                               )
    self.get_E_b_vacancy_migration(name=name, a=a,
                                   opt_name='lbfgs',
                                   box_size=[4]*3,
                                   nimages=3,
                                   is_plot_fig=False,
                                   is_save_traj=is_save_traj,
                                   is_save_log=is_save_log,
                                   is_recalc_neb=True,)
    for surface_indices in ['100', '110', '111']:
      self.get_E_surface_for_bcc(name=name, a=a,
                                 size=[3, 3, 9],
                                 vacuum=5,
                                 opt_name='lbfgs',
                                 surface_indices=surface_indices,
                                 is_save_traj=is_save_traj,
                                 is_save_log=is_save_log,
                                 is_recalc=is_recalc,)

    self.get_data_dimmer(name=name,
                         opt_name='mdmin',
                         is_recalc=is_recalc,)

    return self.data
