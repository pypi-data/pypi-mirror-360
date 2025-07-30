import ase.build
import gpaw.mixer
import matplotlib.pyplot as plt
import numpy as np
import ase
import ase.db
import gpaw
import gpaw.calculator
import ase.parallel
import os
import gpaw
import ase.io
import ase.parallel
import ase.visualize
import ase.spectrum.band_structure
import ase.units
import ase.eos
import ase.vibrations
import ase.thermochemistry
import gpaw.solvation
import gpaw.solvation.sjm
import gpaw.external


class Learn():
  def __init__(self) -> None:
    """gitlab: https://gitlab.com/gpaw/gpaw/-/tree/master/
    - 进行测试: mpiexec -n 2 pytest --pyargs gpaw -v
    """
    pass

  def string_install(self):
    """# 安装 Gpaw
    * mac系统需要进行的操作
    brew install libxc
    brew list libxc
    加入 ~/.bashrc
    export C_INCLUDE_PATH=/opt/homebrew/Cellar/libxc/6.2.2/include
    export LIBRARY_PATH=/opt/homebrew/Cellar/libxc/6.2.2/lib
    export LD_LIBRARY_PATH=/opt/homebrew/Cellar/libxc/6.2.2/lib
    pip install gpaw
    升级: python3 -m pip install git+https://gitlab.com/gpaw/gpaw.git
    gpaw info
    gpaw install-data <dir>  # 安装势文件
    # 安装势文件
    - gpaw install-data /Users/wangjinlong/venv/share/gpaw/gpaw-setups-24.11.0 --version=24.11.0
    # 测试:
    gpaw test
    ---
    或者
    你也可以给 Conda 补上缺失的 clang 编译器（但容易踩坑）：
    # 或者 conda install clang_osx-arm64 clangxx_osx-arm64 -c conda-forge
    conda install compilers -c conda-forge
    python3 -m pip install git+https://gitlab.com/gpaw/gpaw.git
    ---
    * linux 直接进行以下操作:
    pip install git+https://github.com/qsnake/gpaw.git
    conda install ase
    conda install gpaw  # x86 可以这样安装
    conda insall gfortran # 需要有gfortran
    python3 -m pip install git+https://gitlab.com/gpaw/gpaw.git # 安装的是beta 版本
    # 安装势文件, e.g.
    - gpaw install-data /Users/wangjinlong/venv/share/gpaw/gpaw-setups-24.1.0 --version=24.11.0
    # 测试:
    gpaw test

    --- 重新设置
    下载
    ---
    gpaw install-data /Users/wangjinlong/job/soft_learn/soft_learn_project/gpaw_learn/gpaw-setups-24.11.0 --version=24.11.0
    ---
    设置
    1. 设置环境变量 GPAW_SETUP_PATH
    2. 修改配置文件
    打开 ~/.gpaw/rc.py 或者对应的配置文件。
    """
    pass

  def string_calc_sp(self):
    string = """* 单点计算:
    from ase import Atoms
    from ase.optimize import BFGS
    from ase.io import write
    from gpaw import GPAW, PW
    h2 = ase.Atoms('H2',
                   positions=[[0, 0, 0],
                              [0, 0, 0.7]])
    h2.center(vacuum=2.5)
    h2.calc = GPAW(xc='PBE',
                   mode=PW(300),
                   txt='h2.txt')
    e = h2.get_potential_energy()
    """
    print(string)
    return None

  def string_get_electronic_density(self):
    string = """* 获取电子密度
    rho_all = calc.get_all_electron_density()
    rho = rho_pseudo if is_pseudo else rho_all
    ase.io.write(filename='density.cube',
                  images=calc.atoms,
                  data=rho * ase.units.Bohr**3)
    """
    print(string)
    return None

  def string_calc_relax_general(self):
    string = """* O2的结构迟豫:
    import ase
    import ase.io
    import ase.build
    from ase.visualize import view as view
    import os
    import ase.optimize
    import gpaw
    import gpaw.calculator

    # 获得结构
    atoms = ase.build.molecule('O2',vacuum=2.5)

    # 建立目录
    directory = 'exercise_tmp/O2'
    os.makedirs(name=directory, exist_ok=True)

    # 获得计算器
    calc = gpaw.calculator.GPAW(xc='PBE',
                    # mode={'name':'pw','ecut': 700},
                    mode='fd',
                    h=0.2,
                    # hund=True,
                    spinpol=True,
                    txt=os.path.join(directory, 'gpaw.txt'), # 写入计算过程
                    directory=directory, # 指定目录
                    )
    # 进行计算
    atoms.calc =calc
    # e = calc.get_potential_energy(atoms=atoms)
    # print(e) # 可以先看下 没有优化的能量

    opt = ase.optimize.QuasiNewton(
        atoms=atoms, trajectory=os.path.join(directory, 'gpaw.traj'))
    opt.run()
    # 保存计算结果
    calc.write(filename=os.path.join(directory, 'gpaw.gpw'),)
    # 可以尝试将这段代码 分成三个部分: 1. 获得结构 atoms, 2. 获得 calc, 3. 进行结构迟豫的计算

    * 使用以上方法计算 H2, H2O 的 结构和能量
    我的计算
    from gpaw_learn import gpawLearn
    importlib.reload(gpawLearn)
    gf = gpawLearn.gpawLearn.Features()
    atoms = ase.build.molecule('H2O',vacuum=2.5, pbc=True)

    calc = gf.get_calc(directory='exercise_tmp/H2O',
                calc_pars_dict=gf.fd_mode_pars,
                )
    calc =gf.calc_relaxation_general_wrapper(atoms=atoms,
                                      calc=calc,)
    """
    print(string)
    return None

  def string_view_structure(self):
    string = """查看体系优化过程
    fname_traj = os.path.join(calc.directory, 'gpaw.traj')
    atoms_list = ase.io.read(filename=fname_traj, index=':')
    view(atoms_list)
    """
    print(string)
    return None

  def string_read_calced_result(self):
    string = """ *读取之前的计算结果
    calc = gpaw.calculator.GPAW(
                restart=os.path.join(directory, 'gpaw.gpw'),
                directory=directory,
                )
    calc.get_potential_energy() # 查看体系能量
    """
    print(string)
    return None

  def string_calc_relax_lattice_graphene_C2(self):
    string = """ graphene 晶胞的迟豫
    # 建立模型
    atoms: ase.Atoms = ase.build.graphene(size=(1, 1, 1), vacuum=5)
    atoms.set_pbc(pbc=True)
    # view(atoms)
    # 获得calc
    directory = '/Users/wangjinlong/job/soft_learn/soft_learn_project/gpaw_learn/my_example/graphene_C2'
    calc = self.gf.get_calc(directory=directory,
                            calc_pars_dict=self.gf.pw_mode_pars, )
    # 优化 x,y 方向
    atoms.calc = calc
    relax_filter = ase.filters.StrainFilter(atoms, mask=[True,True]+[False]*4)
    opt = ase.optimize.BFGS(relax_filter,
                            trajectory=os.path.join(calc.directory,
                                                    'gpaw.traj'))
    opt.run(fmax=0.05)  # Consider much tighter fmax!
    calc.write(filename=os.path.join(calc.directory, 'gpaw.gpw'))
    """
    print(string)
    return None

  def string_calc_general_relax_slab_B_Gra(self):
    string = """ * 获得 B 掺杂的Gra (体系较小 共18个原子, 用于学习)
    from gpaw_learn import gpawLearn
    importlib.reload(gpawLearn)
    gf = gpawLearn.gpawLearn.Features()

    # 建立模型
    atoms: ase.Atoms = ase.build.graphene(size=(1, 1, 1), vacuum=5,)
    # view(atoms)
    directory = '/Users/wangjinlong/job/soft_learn/soft_learn_project/gpaw_learn/my_example/graphene_C2'
    calc = gf.get_calc(directory=directory,
                      calc_pars_dict=gf.pw_mode_pars,
                      kpts=(5, 5, 1))
    atoms = calc.atoms
    atoms = atoms.repeat(rep=(3, 3, 1))
    # view(atoms)
    for atom in atoms:
      if atom.index == 9:
        atom.symbol = 'B'
    # view(atoms)

    # relaxation
    directory = '/Users/wangjinlong/job/soft_learn/soft_learn_project/gpaw_learn/my_example/B_Gra'
    calc = gf.get_calc(directory=directory,
                      calc_pars_dict=gf.pw_mode_pars,
                      kpts=(3, 3, 1))
    gf.calc_relaxation_general_wrapper(atoms=atoms,
                                      calc=calc)
    """
    print(string)
    return None

  def string_calc_general_relax_adsorbate_OH(self):
    string = """ * 迟豫吸附物OH
    from gpaw_learn import gpawLearn
    importlib.reload(gpawLearn)
    gf = gpawLearn.gpawLearn.Features()

    directory = '/Users/wangjinlong/job/soft_learn/soft_learn_project/gpaw_learn/my_example/OH'
    calc = gf.get_calc(directory=directory,
                      calc_pars_dict=gf.pw_mode_pars,
                      spinpol=True
                      #  kpts=(3, 3, 1),
                      )
    atoms = ase.build.molecule('OH',vacuum=2.5)
    gf.calc_relaxation_general_wrapper(atoms=atoms,
                                      calc=calc)
    """
    print(string)
    return None

  def string_calc_general_relax_OH_on_B_Gra(self):
    string = """ * 获得模型并迟豫 OH@B_Gra 构型
    from gpaw_learn import gpawLearn
    importlib.reload(gpawLearn)
    gf = gpawLearn.gpawLearn.Features()

    # 获得 OH_B_Gra
    adsorbate = ase.build.molecule('OH')
    adsorbate.rotate(a=170, v='x')

    calc = gf.get_calc(dbname='B_Gra',
                      directory=None,
                      calc_pars_dict=gf.pw_mode_pars,
                      spinpol=True)
    slab = calc.atoms

    ase.build.add_adsorbate(slab=slab, adsorbate=adsorbate,
                                # 增加一点偏移量以获取可能的稳定构型, 比如桥位
                                position=slab[9].position[:2]*1.005,
                                # 相对于表面的高度, 而表面其它原子可能较高, 而吸附考虑的是吸附物相对吸附位的高度
                                height=2,
                                mol_index=0,
    )
    # view(slab)

    # 进行计算
    calc = gf.get_calc(
                      directory='/Users/wangjinlong/job/soft_learn/soft_learn_project/gpaw_learn/my_example/OH_B_Gra',
                      calc_pars_dict=gf.pw_mode_pars,
                      kpts=(3,3,1))
    gf.calc_relaxation_general_wrapper(atoms=slab,
                                      calc=calc,)

    """
    print(string)
    return None

  def string_calc_vib_H2O(self):
    string = """ * 计算H2O的振动频率
    calc = gf.get_calc(dbname='H2O',
                      directory=None,
                      calc_pars_dict=gf.pw_mode_pars,)
    # Create vibration calculator
    atoms= calc.get_atoms()
    vib = ase.vibrations.Vibrations(atoms,
                                    name=os.path.join(calc.directory,'vib'))
    vib.run()
    vib.summary(method='frederiksen',)
    # vib.summary()
    # Make trajectory files to visualize normal modes:
    vib.write_mode()
    # 获得 零点能
    vib.get_zero_point_energy()
    # 查看振动模式
    view(os.path.join(calc.directory, 'vib.8.traj'))
    """
    print(string)
    return None

  def string_get_gibbs_energy_H2O(self):
    string = """ * 水的 Gibs energy
    calc = gf.get_calc(dbname='H2O',
                      directory=None,
                      calc_pars_dict=gf.pw_mode_pars,)
    atoms = calc.get_atoms()
    potentialenergy = calc.get_potential_energy()

    vibData= gf.calc_vib_get_vibData(calc_with_atoms=calc,)
    vib_energies = vibData.get_energies()

    thermo = ase.thermochemistry.IdealGasThermo(vib_energies=vib_energies,
                                                potentialenergy=potentialenergy,
                                                atoms=atoms,
                                                symmetrynumber=2,
                                                spin=0.0,
                                                geometry='nonlinear',
                                                ignore_imag_modes=True,
                                                )
    thermo.get_gibbs_energy(temperature=300, pressure=101325, verbose=False)
    """
    print(string)
    return None

  def string_calc_vib_OH_on_B_Gra(self):
    string = """ * 计算吸附的OH的振动, 只需要增加OH的索引
    from gpaw_learn import gpawLearn
    gf = gpawLearn.gpawLearn.Features()
    calc = gf.get_calc(dbname='OH_B_Gra',
                   directory=None,
                   calc_pars_dict=gf.pw_mode_pars,)
    atoms = calc.get_atoms()
    # view(atoms)
    vibData = gf.calc_vib_get_vibData(calc_with_atoms=calc,
    indices=[18,19], is_show_summary=True, is_write_mode=True                        )
    """
    print(string)
    return None

  def string_get_gibbs_energy_OH_on_B_Gra(self):
    string = """ *  OH@B_Gra 体系的 gibbs 自由能
    from gpaw_learn import gpawLearn
    gf = gpawLearn.gpawLearn.Features()
    calc = gf.get_calc(dbname='OH_B_Gra',
                   directory=None,
                   calc_pars_dict=gf.pw_mode_pars,)
    potentialenergy = calc.get_potential_energy()
    vib_energies = vibData.get_energies()
    thermo = ase.thermochemistry.HarmonicThermo(vib_energies=vib_energies,
                                                potentialenergy=potentialenergy,
                                                ignore_imag_modes=True)

    thermo.get_helmholtz_energy(temperature=300,)
    """
    print(string)
    return None

  def build_env(self):
    """_summary_
    conda install gpaw pylatex py4vasp pymatgen pylatex
    """
    packages = ['ipykernel', 'gpaw', 'pylatex', 'py4vasp',
                'pymatgen', 'pylatex', 'mpi4py', 'ovito', 'ipympl', 'pypdf',]
    for package in packages:
      if package == 'ovito':
        os.system(
            'conda install --strict-channel-priority -c https://conda.ovito.org -c conda-forge ovito=3.10.6 -y')
      else:
        os.system(f'conda install {package} -y')

    pass

  def example(self):
    from ase import Atoms
    from ase.optimize import BFGS
    from ase.io import write
    from gpaw import GPAW, PW
    h2 = ase.Atoms('H2',
                   positions=[[0, 0, 0],
                              [0, 0, 0.7]])
    h2.center(vacuum=2.5)
    h2.calc = GPAW(xc='PBE',
                   mode=PW(300),
                   txt='h2.txt')
    e = h2.get_potential_energy()
    return e

  def install(self):
    """首先安装ase环境
    别忘了安装mpi4py 安装的时候确认是mpich
    创建gpaw 环境
    conda create -n gpaw --clone ase
    conda install -c conda-forge ase
    ##
    conda install -c conda-forge ase
    pip install --upgrade git+https://gitlab.com/ase/ase.git@master
    # conda install -c conda-forge gpaw  # 失效了
    pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ gpaw
    gpaw install-data /Users/wangjinlong/venv/share/gpaw # 安装势文件

    gpaw info  # 查看安装信息
    可以看到势的数据库就在 PAW-datasets (1)  /opt/anaconda3/envs/gpaw/share/gpaw
    并行测试
    mpiexec -np 4 python3 -c "import gpaw.mpi as mpi; print(mpi.rank)"
    """
    pass

  def optimization(self,
                   fname_out='gpaw.txt',
                   fname_traj='opt.traj',
                   ):
    # 结构优化
    atoms = ase.Atoms('HOH',
                      positions=[[0, 0, -1], [0, 1, 0], [0, 0, 1]])
    atoms.center(vacuum=3.0)

    # ASE provides several optimization algorithms that can run on top of Atoms equipped with a calculator:
    calc = gpaw.calculator.GPAW(mode='lcao', basis='dzp', txt=fname_out)
    atoms.calc = calc
    energy = atoms.get_potential_energy()
    # 这里少了写入gpw 文件的 命令 以后再说
    calc.write('gpaw.gpw')
    print(f'自洽计算的能量{energy}')

    # 结构优化
    opt = ase.optimize.BFGS(atoms, trajectory=fname_traj)
    opt.run(fmax=0.05)

  def dos(self,
          fname_out='gpaw.txt',
          fname_traj='opt.traj',):
    self.optimization(fname_out=fname_out,
                      fname_traj=fname_traj)

    # Having saved the ground-state, we can reload it for ASE to extract the density of states:
    from ase.dft.dos import DOS
    import ase.dft.dos

    calc = gpaw.calculator.GPAW('groundstate.gpw')
    # width=0 means ASE well calculate the DOS using the linear tetrahedron interpolation method
    dos = ase.dft.dos.DOS(calc, npts=500, width=0)
    energies = dos.get_energies()
    weights = dos.get_dos()
    plt.plot(energies, weights)
    plt.show()

    lat = ase.atoms.cell.get_bravais_lattice()
    print(lat.description())
    lat.plot_bz(show=True)
    # Which parts of the spectrum do you think originate (mostly) from s electrons? And which parts (mostly) from d electrons?
    # Time for analysis. As we probably know, the d-orbitals in a transition metal atom are localized close to the nucleus while the s-electron is much more delocalized.
    # In bulk systems, the s-states overlap a lot and therefore split into a very broad band over a wide energy range. d-states overlap much less and therefore also split less: They form a narrow band with a very high DOS. Very high indeed because there are 10 times as many d electrons as there are s electrons.
    # So to answer the question, the d-band accounts for most of the states forming the big, narrow chunk between -6.2 eV to -2.6 eV. Anything outside that interval is due to the much broader s band.
    # The DOS above the Fermi level may not be correct, since the SCF convergence criterion (in this calculation) only tracks the convergenece of occupied states. Hence, the energies over the Fermi level 0 are probably wrong.

  def band_structure(self,):
    # another example
    # TutorialElectronicStructure().band_structure()
    #
    from gpaw import PW
    from ase.constraints import ExpCellFilter
    from ase.io import write
    from ase.optimize import BFGS
    from ase.spacegroup import crystal

    a = 4.6
    c = 2.95

    # Rutile TiO2:
    atoms = crystal(['Ti', 'O'], basis=[(0, 0, 0), (0.3, 0.3, 0.0)],
                    spacegroup=136, cellpar=[a, a, c, 90, 90, 90])
    write('rutile.traj', atoms)

    calc = gpaw.calculator.GPAW(mode=PW(800), kpts=[2, 2, 3],
                                txt='gpaw.rutile.txt')
    atoms.calc = calc

    # The ase.constraints.ExpCellFilter allows us to optimise cell and positions simultaneously.
    opt = BFGS(ExpCellFilter(atoms), trajectory='opt.rutile.traj')
    opt.run(fmax=0.05)

    calc.write('groundstate.rutile.gpw')

    print('Final lattice:')
    print(atoms.cell.get_bravais_lattice())

    # band structure
    calc = gpaw.calculator.GPAW('groundstate.rutile.gpw')
    atoms: ase.Atoms = calc.get_atoms()
    path = atoms.cell.bandpath(density=7)
    # path.write('path.rutile.json')

    calc.set(kpts=path,
             fixdensity=True,
             symmetry='off',)

    atoms.get_potential_energy()
    bs = calc.band_structure()
    bs.write('bs.rutile.json')

    # Finally, the bandstructure can be plotted (using ASE’s band-structure tool ase.spectrum.band_structure.BandStructure):
    bs.plot(filename='bandstructure.png', show=True,)
    pass

  def vibrational_mode(self, directory):
    # Density functional theory can be used to calculate vibrational frequencies of molecules, e.g. either in the gas phase or on a surface. These results can be compared to experimental output, e.g. from IR-spectroscopy, and they can be used to figure out how a molecule is bound to the surface. In this example we will calculate the vibrational frequencies for a water molecule.
    from math import cos, pi, sin
    from ase import Atoms
    from ase.optimize import QuasiNewton
    from ase.vibrations import Vibrations
    from gpaw import GPAW

    # Water molecule:
    d = 0.9575
    t = pi / 180 * 104.51

    h2o = Atoms('H2O',
                positions=[(0, 0, 0),
                           (d, 0, 0),
                           (d * cos(t), d * sin(t), 0)])
    h2o.center(vacuum=3.5)

    h2o.calc = GPAW(txt='h2o.txt',
                    mode='lcao',
                    basis='dzp',
                    symmetry='off',
                    directory=directory)

    QuasiNewton(h2o).run(fmax=0.05)

    """Calculate the vibrational modes of a H2O molecule."""
    # Create vibration calculator
    vib = Vibrations(h2o,)
    vib.run()
    vib.summary(method='frederiksen')

    # Make trajectory files to visualize normal modes:
    for mode in range(9):
      vib.write_mode(n=mode)
    pass

    # ase gui vib.8.traj  # 查看振动模式
    # Since there are nine coordinates, we get nine eigenvalues and corresponding modes. However the three translational and three rotational degrees of freedom will contribute six “modes” that do not correspond to true vibrations. In principle there are no restoring forces if we translate or rotate the molecule, but these will nevertheless have different energies (often imaginary) because of various artifacts of the simulation such as the grid used to represent the density, or effects of the simulation box size.

  def parameters(self):
    """https://wiki.fysik.dtu.dk/gpaw/documentation/basic.html
    """

    def nbands(n):
      # nbands
      # For metals, more bands are needed. Sometimes, adding more unoccupied bands will improve convergence.
      nbands = -n  # will give n empty bands.
      nbands = 0  # will give zero empty bands
      nbands = 'n%'  # will give n/100 times the number of occupied bands.
      # will use the same number of bands as there are atomic orbitals. This corresponds to the maximum nbands value that can be used in LCAO mode.
      nbands = 'nao'

    def kpts(atoms: ase.Atoms,):
      bandpath = atoms.cell.bandpath(density=7)  # 可以根据密度采样
      bandpath = atoms.cell.bandpath('GMKG', npoints=100)
      bandpath.special_points  # 可以看特殊点
      bandpath.plot()  # 可以查看倒格矢空间图

      calc = gpaw.calculator.GPAW('Si_gs.gpw').fixed_density(
          nbands=16,
          symmetry='off',
          kpts={'path': 'GXWKL', 'npoints': 60},
          # kpts=bandpath, # 或者这样设置
          convergence={'bands': 8})

      # kpts : Brillouin-zone sampling
      kpts = (4, 4, 4)
      kpts = {'size': (4, 4, 4)}  # 4x4x4 Monkhorst-pack
      kpts = {'size': (4, 4, 4), 'gamma': True}  # shifted 4x4x4 Monkhorst-pack
      kpts = {'density': 2.5}  # MP with a minimum density of 2.5 points/Ang^-1
      kpts = {'density': 2.5, 'even': True}  # round up to nearest even number
      # MP with a minimum density of 2.5 points/Ang^-1 include gamma-point
      kpts = {'density': 2.5, 'gamma': True}
      kpts = [(0, 0, -0.25), (0, 0, 0), (0, 0, 0.25), (0, 0, 0.5)]

      from ase.dft.kpoints import monkhorst_pack
      kpts = monkhorst_pack((1, 1, 4))
      kpts  # 查看产生的k点坐标

    def spinpol():
      """Spinpolarized calculation¶
      If any of the atoms have magnetic moments, then the calculation will be spin-polarized - otherwise, a spin-paired calculation is carried out. This behavior can be overruled with the spinpol keyword (spinpol=True).
      """
      spinpol = False  # 默认自选配对
      spinpol = True  # 自旋极化

    def h_gpts(n1, n2, n3):
      """Number of grid points

      """
      # 格点与截断能之间的转换
      from gpaw.utilities.tools import cutoff2gridspacing, gridspacing2cutoff
      from ase.units import Rydberg
      h = cutoff2gridspacing(50 * Rydberg)

      # where n1, n2 and n3 are positive int’s all divisible by four.
      gpts = (n1, n2, n3)
      h = 0.25  # Alternatively, one can use something like

    def symmetry():
      symmetry = {'point_group': False}
      # band-structure calculations 不通过对称性减少 k 点
      symmetry = {'point_group': False, 'time_reversal': False}
      symmetry = 'off'  # which is a short-hand notation for the same thing.
      pass

    def occupations():
      """ width=k_B * T
      For calculations with periodic boundary conditions, the default value is 0.1 eV and the total energies are extrapolated to T = 0 Kelvin. For a molecule (no periodic boundaries) the default value is width=0, which gives integer occupation numbers.
      """
      # 收敛测试
      self.convergence_smearing()
      # 用法
      gpaw.occupations.FermiDirac()
      occupations = gpaw.FermiDirac(width=0.5, fixmagmom=True),
      occupations = {'name': 'fermi-dirac', 'width': 0.05},
      # Other distribution functions:
      {'name': 'marzari-vanderbilt', 'width': ...}
      {'name': 'methfessel-paxton', 'width': ..., 'order': ...}
      # For a spin-polarized calculation, one can fix the total magnetic moment at the initial value using:
      occupations = {'name': ..., 'width': ..., 'fixmagmom': True}

    def charge():
      """The default is charge neutral. The systems total charge may be set in units of the negative electron charge (i.e. charge=-1 means one electron more than the neutral).
      """
      charge = -1  # means one electron more than the neutral).
      pass

    def mixer():
      # For small molecules, which is what GPAW will choose if the system has zero-boundary conditions.
      mixer = gpaw.mixer.Mixer(beta=0.25, nmaxold=3, weight=1.0)
      # which is also what GPAW will choose if the system has periodic boundary conditions in one or more directions.
      mixer = gpaw.mixer.Mixer(beta=0.05, nmaxold=5, weight=50.0)

    def fixed_density(path):
      # Fixed density calculation
      # When calculating band structures or when adding unoccupied states to calculation
      # This will use the density (e.g. one read from .gpw or existing from previous calculation) throughout the SCF-cycles (so called Harris calculation).
      gpaw.calculator.GPAW('gpaw.gpw').fixed_density(kpts=path, symmetry='off')

    def setup():
      # The setups keyword is used to specify the name(s) of the setup files used in the calculation.
      setups = {'default': 'soft', 'Li': 'hard', 5: 'ghost', 'H': 'ae'}

    def basis():
      """The basis keyword can be used to specify the basis set which should be used in LCAO mode. This also affects the LCAO initialization in FD or PW mode, where initial wave functions are constructed by solving the Kohn-Sham equations in the LCAO basis.
      """
      pass

    def eigensolver():
      """The default solver for iterative diagonalization of the Kohn-Sham Hamiltonian is a simple Davidson method, (eigensolver='dav'), which seems to perform well in most cases. Sometimes more efficient/stable convergence can be obtained with a different eigensolver. One option is the RMM-DIIS (Residual minimization method - direct inversion in iterative subspace), (eigensolver='rmm-diis'), which performs well when only a few unoccupied states are calculated. Another option is the conjugate gradient method (eigensolver='cg'), which is stable but slower.
      """
      eigensolver = 'dav'
      eigensolver = 'rmm-diis'
      # More control can be obtained by using directly the eigensolver objects:
      from gpaw.eigensolvers import CG
      calc = gpaw.calculator.GPAW(..., eigensolver=CG(niter=5, rtol=0.20))
      # lcao 模式有自己的 eigensolvers
      eigensolver = 'direct'
      eigensolver = 'etdm'  # it is not recommended to use it for metals
      # eigensolver = 'etdm'  还要配合 下面三个设置
      occupations = {'name': 'fixed-uniform'},
      mixer = {'backend': 'no-mixing'},
      nbands = 'nao',

    def poissonsolver():
      """_summary_
      """
      # The old default Poisson solver uses a multigrid Jacobian method. This example corresponds to the old default Poisson solver:
      from gpaw import GPAW, PoissonSolver
      calc = GPAW(poissonsolver=PoissonSolver(
          name='fd', nn=3, relax='J', eps=2e-10),)
      pass

    def hund():
      # the calculation will become spinpolarized, and the initial ocupations, and magnetic moments of all atoms will be set to the values required by Hund’s rule.
      hund = True
      # You may further wish to specify that the total magnetic moment be fixed, by passing e.g. occupations={'name': ..., 'fixmagmom': True}.
      occupations = {'name': ..., 'fixmagmom': True}
      pass

    def verbose():
      # By default, only a limited number of information is printed out for each SCF step. It is possible to obtain more information (e.g. for investigating convergen problems in more detail) by verbose=1 keyword.
      verbose = 1

    pass

  def restart_calculation(self):
    # 改变计算参数后再次计算
    atoms, calc = gpaw.restart('H2.gpw', gpts=(20, 20, 20))
    print(atoms.get_potential_energy())
    # 另一种方法
    atoms, calc = gpaw.restart('H2.gpw')
    calc.set(gpts=(20, 20, 20))
    print(atoms.get_potential_energy())
    pass

  def calc_attch(self):
    calc = gpaw.calculator.GPAW(...)
    occasionally = 5

    class OccasionalWriter:
      def __init__(self):
        self.iter = 0

      def write(self):
        calc.write('filename.%03d.gpw' % self.iter)
        self.iter += occasionally
    calc.attach(OccasionalWriter().write, occasionally)

  def write_file(self,):
    # Be careful when writing to files in a parallel run. Instead of f = open('data', 'w'), use:
    from ase.parallel import paropen
    f = paropen('data', 'w')

    # print text output
    from ase.parallel import parprint
    # print('This is written by all nodes') # 所有节点都会写
    parprint('This is written by the master only')

  def convergence_issues(self,):
    """_summary_
    """
    atoms = ase.Atoms('Fe')
    atoms.center(5)
    atoms.pbc = True
    calc = gpaw.calculator.GPAW(mode='pw',
                                xc='PBE',
                                eigensolver='rmm-diis',  # This solver can parallelize over bands
                                occupations=gpaw.FermiDirac(
                                    width=0.5, fixmagmom=True),
                                # spinpol=True,
                                # nbands=-5,
                                hund=True,
                                # kpts={'density': 3.5, 'even': True}
                                # convergence={'energy': 1e-4,},
                                #              'eigenstates': 1e-5, 'bands': -10}
                                # txt='gpaw.txt',
                                )
    atoms.calc = calc
    e_Fe = atoms.get_potential_energy()
    return e_Fe

  def restart_files(self, calc, n):
    # Writing restart files  mode='all' to include also the wave functions.
    calc.write('xyz.gpw', mode='all')
    # You can register an automatic call to the write method, every n’th iteration of the SCF cycle like this:
    calc.attach(calc.write, n, 'xyz.gpw', mode='all')

    # Reading restart files
    calc = gpaw.calculator.GPAW('xyz.gpw')
    # or By adding the option txt=None you can suppress text output when restarting (e.g. when plotting a DOS):
    atoms, calc = gpaw.restart('xyz.gpw', txt=None)
    pass

  def Excited_State_Calculations(self):
    """https://wiki.fysik.dtu.dk/gpaw/documentation/mom/mom.html
    example1
    Excitation energy Rydberg state of water¶
    """
    import gpaw.mom
    import copy
    atoms = ase.build.molecule('H2O')
    atoms.center(vacuum=7)

    calc = gpaw.calculator.GPAW(mode='fd',
                                basis='dzp',
                                nbands=6,
                                h=0.2,
                                xc='PBE',
                                spinpol=True,
                                symmetry='off',
                                convergence={'bands': -1},
                                txt='h2o.txt')
    atoms.calc = calc

    # Ground-state calculation
    E_gs = atoms.get_potential_energy()

    # Ground-state occupation numbers
    f_gs = []
    for s in range(2):
      f_gs.append(calc.get_occupation_numbers(spin=s))

    # Triplet n->3s occupation numbers
    f_t = copy.deepcopy(f_gs)
    f_t[0][2] -= 1.  # Remove one electron from homo-1 (n) spin up
    f_t[1][4] += 1.  # Add one electron to lumo (3s) spin down

    # MOM calculation for triplet n->3s state
    gpaw.mom.prepare_mom_calculation(calc=calc, atoms=atoms, numbers=f_t)
    E_t = atoms.get_potential_energy()

    # Mixed-spin n->3s occupation numbers
    f_m = copy.deepcopy(f_gs)
    f_m[0][2] -= 1.  # Remove one electron from homo-1 (n) spin up
    f_m[0][4] += 1.  # Add one electron to lumo (3s) spin up

    # MOM calculation for mixed-spin n->3s state
    gpaw.mom.prepare_mom_calculation(calc, atoms, f_m)
    E_m = atoms.get_potential_energy()
    E_s = 2 * E_m - E_t  # Spin purified energy

    with ase.parallel.paropen('h2o_energies.txt', 'w') as fd:
      print(f'Excitation energy triplet n->3s state: {E_t - E_gs:.2f} eV',
            file=fd)
      print(f'Excitation energy singlet n->3s state: {E_s - E_gs:.2f} eV',
            file=fd)
      # https://doi.org/10.1021/acs.jctc.8b00406
      print('Experimental excitation energy triplet n->3s state: 9.46 eV',
            file=fd)
      print('Experimental excitation energy singlet n->3s state: 9.67 eV',
            file=fd)

    return atoms

  def convergence_smearing(self):
    """Convergence with respect to number of k-point for bulk Cu energy with different smearing methods:
    """
    from ase.build import bulk
    from gpaw import GPAW, PW

    cu = bulk('Cu', 'fcc', a=3.6)

    for smearing in [{'name': 'improved-tetrahedron-method'},
                     {'name': 'tetrahedron-method'},
                     {'name': 'fermi-dirac', 'width': 0.05},
                     {'name': 'marzari-vanderbilt', 'width': 0.2}]:
      name = ''.join(word[0].upper() for word in smearing['name'].split('-'))
      width = smearing.get('width')
      if width:
        name += f'-{width}'

      for k in range(8, 21):
        cu.calc = GPAW(
            mode=PW(400),
            kpts=(k, k, k),
            occupations=smearing,
            txt=f'Cu-{name}-{k}.txt')
        e = cu.get_potential_energy()

    # 画图
    fig, ax = plt.subplots(constrained_layout=True)

    e0 = None
    k = np.arange(8, 21, dtype=float)
    for name in ['ITM', 'TM', 'FD-0.05', 'MV-0.2']:
      energies = []
      for n in k:
        e = ase.io.read(f'Cu-{name}-{int(n)}.txt').get_potential_energy()
        energies.append(e)
      if e0 is None:
        e0 = e
      ax.plot(k**-2, (np.array(energies) - e0) * 1000, label=name)

    ax.set_xlabel(r'$1/k^2$')
    ax.set_ylabel(r'$\Delta E$ [meV]')
    ax2 = ax.secondary_xaxis('top', functions=(lambda x: (x + 1e-10)**-0.5,
                                               lambda k: (k + 1e-10)**-2))
    ax2.set_xlabel('Number of k-points (k)')
    plt.legend()
    plt.savefig('cu.png')
    # plt.show()


class Example():
  def __init__(self):
    pass

  # example
  def parallel_example(self):
    """
    import ase.build
    from gpaw_learn import gpawLearn

    gf = gpawLearn.Features()
    atoms = ase.build.bulk(name='Pt')
    pdict = gf.pw_mode_pars
    calc = gf.to_calc(atoms=atoms, calc_pars_dict=pdict,
              directory='/Users/wangjinlong/my_server/my/myORR_B/adsorbate/CO/gpaw_test',
              recalc=True)
    ase.parallel.parprint('done')

    写入test.py
    $ mpiexec -np 4 gpaw python test.py 即可
    """
    pass

  def fd_mode_example(self):
    # 实空间网格模式
    from ase import Atoms
    from gpaw import GPAW
    import gpaw.calculator

    # 创建一个简单的原子体系
    atoms = Atoms('H2O', positions=[(0, 0, 0), (0, 0, 1), (1, 0, 0)])
    # 使用实空间网格模式进行计算
    calc = gpaw.calculator.GPAW(mode='fd', h=0.2, txt='output_fd.txt')
    atoms.calc = calc
    # 进行计算
    atoms.get_potential_energy()
    pass

  def pw_mode_example(self):
    # 平面波模式
    from ase import Atoms
    from gpaw import GPAW

    # 创建一个简单的原子体系
    atoms = Atoms('H2O', positions=[(0, 0, 0), (0, 0, 1), (1, 0, 0)])
    # 使用平面波模式进行计算
    calc = GPAW(mode='pw', ecut=300, txt='output_pw.txt')
    atoms.calc = calc
    # 进行计算
    atoms.get_potential_energy()

    pass

  def lcao_mode_example(self):
    # 局域轨道模式
    from ase import Atoms
    from gpaw import GPAW

    # 创建一个简单的原子体系
    atoms = Atoms('H2O', positions=[(0, 0, 0), (0, 0, 1), (1, 0, 0)])

    # 使用局域轨道模式进行计算
    calc = GPAW(mode='lcao', basis='dzp', txt='output_lcao.txt')
    atoms.calc = calc

    # 进行计算
    atoms.get_potential_energy()

    pass


# class DataBase(dataBase.DataBase):
class DataBase():
  def __init__(self, ):
    super().__init__()
    # 为了能够在服务器上使用
    self.fname_db = os.path.join(
        os.environ['HOME'], 'job/soft_learn/soft_learn_project/gpaw_learn/my_example/dataBase.json')
    self.fname_db_bk = os.path.join(
        os.environ['HOME'], 'job/soft_learn/soft_learn_project/gpaw_learn/my_example/dataBase_bk.json')
    self.db = ase.db.connect(self.fname_db)
    return

  def write_relax_2db(self, calc: gpaw.calculator.GPAW):
    dbname = os.path.basename(calc.directory)
    self.db_write_and_update(atoms=calc.atoms,
                             directory=calc.directory,
                             dbname=dbname)
    ase.parallel.parprint(f'{dbname} -> 写入 relaxation 结果. ')
    return

  def write_sp_2db(self, calc: gpaw.calculator.GPAW,
                   is_bader=True):
    from soft_learn_project.gpaw_learn import gpawTutorial
    if is_bader:
      atoms = gpawTutorial.TutorialChargeAnalysis().method_bader(calc=calc,)
    else:
      atoms = calc.atoms
    dbname = os.path.basename(calc.directory)
    self.db_write_and_update(atoms=atoms,
                             directory=calc.directory,
                             dbname=dbname)
    ase.parallel.parprint(f'{dbname} -> 写入 sp 结果. ')
    return

  def write_thermo_2db_gpaw(self, calc: gpaw.calculator.GPAW,
                            thermo_data_dict: dict):
    if calc.directory.endswith('/sol_eff'):
      directory = calc.directory.removesuffix('/sol_eff')
      if 'gibbs_energy' in thermo_data_dict.keys():
        thermo_data_dict['gibbs_energy_sol_eff'] = thermo_data_dict.pop(
            'gibbs_energy')
      elif 'helmholtz_energy' in thermo_data_dict.keys():
        thermo_data_dict['helmholtz_energy_sol_eff'] = thermo_data_dict.pop(
            'helmholtz_energy')
        pass
    else:
      directory = calc.directory
    dbname = os.path.basename(directory)
    self.db_update_values(name=dbname,
                          **thermo_data_dict
                          )
    ase.parallel.parprint(f'{dbname} -> 写入 thermo 结果. ')
    return thermo_data_dict


class GpawLearn():
  def __init__(self):
    r"""
    GPAW（Grid-based Projector-Augmented Wave）是一种基于网格的投影增强平面波方法，用于密度泛函理论（DFT）计算。虽然 GPAW 可以使用平面波基组进行计算，但它的主要特征是基于实空间网格进行计算，并且也支持局域轨道（LCAO）和混合模式。以下是 GPAW 支持的几种计算模式：

    ---
    # 以后都尽量改成 ase.Features 中的方法 这样具有普适性 别的calc 也就可以用了

    GPAW 的计算模式
    实空间网格（Real-space grid）模式：

    这是 GPAW 的默认模式，在一个均匀的三维网格上表示波函数和密度。
    适用于处理复杂的几何结构和界面。
    可以在给定的网格细化程度下提供高度准确的结果。
    平面波（Plane-wave）模式：

    GPAW 也可以使用平面波基组进行计算，适用于周期性系统。
    与传统的平面波 DFT 软件（如 VASP）类似，但 GPAW 的实现基于 PAW 方法。
    局域轨道（LCAO）模式：

    使用局域轨道基组进行计算，适用于初步计算和大规模系统。
    计算速度快，但精度可能不如实空间网格模式。
    """
    super().__init__()
    # ---
    # self.write_py_from_code = self.AseLearn.write_py_from_code
    from soft_learn_project.gpaw_learn import gpawTutorial
    self.gpawTutorial = gpawTutorial
    self.NEB_gpaw = self.TSTcalc = self.gpawTutorial.MolecularDynamics()
    # 溶剂化效应的计算
    self.DataBase = DataBase()
    self.Example = Example()
    self.Learn = Learn()

    pass

  def env_set(self):
    """
    下载
    ---
    gpaw install-data /Users/wangjinlong/job/soft_learn/soft_learn_project/gpaw_learn/gpaw-setups-24.11.0 --version=24.11.0
    ---
    设置
    1. 设置环境变量 GPAW_SETUP_PATH
    2. 修改配置文件
    打开 ~/.gpaw/rc.py 或者对应的配置文件。
    """
    # export GPAW_SETUP_PATH=/Users/wangjinlong/job/soft_learn/soft_learn_project/gpaw_learn/gpaw-setups-24.11.0
    import importlib.resources
    GPAW_SETUP_PATH = importlib.resources.files('soft_learn_project.gpaw_learn.data').joinpath(
        'gpaw-setups-24.11.0')
    os.environ['GPAW_SETUP_PATH'] = str(GPAW_SETUP_PATH)
    pass

  def get_calc_from_gpw_file(self,
                             fname_gpw='./gpaw.gpw',):
    directory = os.path.dirname(fname_gpw)
    for cmd in [gpaw.solvation.sjm.SJM,
                gpaw.solvation.SolvationGPAW,
                gpaw.calculator.GPAW,
                ]:
      try:
        calc = cmd(restart=fname_gpw,
                   directory=directory,
                   txt=None)
        ase.parallel.parprint(f'calc 的名字为 {cmd.__name__}')
        break  # 如果命令成功执行，跳出循环
      except Exception as e:
        # ase.parallel.parprint(f"{cmd.__name__} 失败: {e}")
        continue  # 如果失败，尝试下一个命令
    return calc

  def get_calc(self,
               directory='.',
               calc_mode='pw',
               is_save_log=False,
               **kwargs):
    """* 用于计算或者获取之前的计算结果
    - 不要忘记设置 kpts=()
    - calc_mode='fd|pw|lcao',
    """
    self.env_set()

    if calc_mode.casefold() == 'fd':
      calc_pars_dict = {'mode': 'fd',
                        'h': 0.2,  # 0.17
                        'xc': 'PBE',
                        'spinpol': True,  # 自旋极化计算, 建议使用这个
                        #  'hund': True,  # 洪特定则, 打开后自动进行自旋极化计算, 计算H2会出错还是使用 spinpol
                        #  'kpts': (3, 3, 1),
                        #  'kpts': {'density': 3.0, 'gamma': True},
                        'maxiter': 60,
                        'symmetry': {'point_group': True,
                                     'time_reversal': True,
                                     'symmorphic': True,
                                     'tolerance': 1e-2,  # 1e-7
                                     'do_not_symmetrize_the_density': None},  # deprecated
                        #  'convergence': {'energy': 1e-3,  # eV / electron 5e-4
                        #                  'density': 2.0e-4,  # electrons / electron 1e-4
                        #                  'eigenstates': 5.0e-5,  # eV^2 / electron 4e-8
                        #                  'bands': 'occupied'},
                        #  'mixer': {'backend': 'pulay',
                        #            'beta': 0.05,
                        #            'method': 'sum',
                        #            'nmaxold': 5,
                        #            'weight': 100},
                        }
    elif calc_mode.casefold() == 'pw':
      calc_pars_dict = {'mode': {'name': 'pw',
                                 'ecut': 400, },
                        'xc': 'PBE',
                        'spinpol': True,
                        #  'hund': True,
                        #  'symmetry': 'off', # 对称性关闭可能会导致不收敛
                        #  'kpts': (3, 3, 3),
                        #  'kpts': {'density': 3.0, 'gamma': True},
                        # parallel={'domain': 1, 'band': 1},
                        # magmoms=magmoms,
                        #  'convergence': {'energy': 0.001,  # eV / electron
                        #                  'density': 1.0e-4,  # electrons / electron
                        #                  'eigenstates': 4.0e-8,  # eV^2 / electron
                        #                  'bands': 'occupied'},
                        #  'mixer': {'backend': 'pulay',
                        #            'beta': 0.05,
                        #            'method': 'sum',
                        #            'nmaxold': 5,
                        #            'weight': 100},
                        }
    elif calc_mode.casefold() == 'lcao':
      calc_pars_dict = {'mode': 'lcao', 'basis': 'dzp',
                        'xc': 'PBE', 'spinpol': True,  # 自旋极化计算
                        #  'hund': True,  # 洪特定则
                        #  'convergence': {'energy': 0.001,
                        #                  #  'density': 0.0001,
                        #                  #  'eigenstates': 4e-08,
                        #                  #  'bands': 'occupied'
                        #                  },
                        'maxiter': 60,
                        'symmetry': {'point_group': True,
                                        'time_reversal': True,
                                        'symmorphic': True,
                                        'tolerance': 1e-2,  # 1e-7
                                        'do_not_symmetrize_the_density': None},
                        }

    fname_gpw = os.path.join(directory, 'gpaw.gpw')

    if os.path.exists(fname_gpw):
      calc: gpaw.calculator.GPAW = self.get_calc_from_gpw_file(
          fname_gpw=fname_gpw)
    else:
      if not os.path.exists(directory):
        os.makedirs(directory, )
      fname_txt = os.path.join(
          directory, 'gpaw.log') if is_save_log else None  # '-'
      calc = gpaw.calculator.GPAW(directory=directory,
                                  txt=fname_txt,
                                  **calc_pars_dict,)
      calc.set(_set_ok=True, **kwargs)
    return calc

  def get_calc_sol_eff(self, directory='xxx/sol_eff',
                       calc_pars_dict=None,
                       fname_gpw='gpaw.gpw',
                       fname_txt='gpaw.txt',
                       **kwargs,
                       ):
    fname_gpw = os.path.join(directory, fname_gpw)
    if os.path.exists(fname_gpw):
      calc = self.get_calc_from_gpw_file(fname_gpw=fname_gpw,)
    else:
      if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
      calc_pars_dict = self.calc_pars_default if calc_pars_dict is None else calc_pars_dict
      ed = self.gpawTutorial.Electrostatics_and_dynamics()
      calc = ed.get_calc_water_Continuum_Solvent_Model(directory=directory,
                                                       calc_pars_dict=calc_pars_dict,
                                                       fname_txt=fname_txt,
                                                       **kwargs,
                                                       )
    return calc

  def get_atoms_list(self, dbname=None,
                     directory=None,
                     fname='gpaw.traj',
                     is_view=False):

    calc = self.get_calc(dbname=dbname, directory=directory)
    fname_traj = os.path.join(calc.directory, fname)
    atoms_list = ase.io.read(filename=fname_traj, index=':')

    if is_view:
      ase.visualize.view(atoms_list)
    return atoms_list

  def get_atoms_with_infos(self, dbname=None,
                           directory=None,
                           ):
    calc = self.get_calc(directory=directory,
                         dbname=dbname)
    atoms = self.gpawTutorial.TutorialChargeAnalysis().method_bader(calc=calc,)
    return atoms

  def calc_single_point(self, atoms: ase.Atoms,
                        is_bader=False,
                        ):
    r"""不要忘记确认 kpts"""

    if self.calc.atoms is None:
      atoms = self.AseLearn.calc_single_point(atoms=atoms,
                                              calc=self.calc)
      self.calc.write(filename=os.path.join(self.calc.directory, 'gpaw.gpw'))
      self.DataBase.write_sp_2db(calc=self.calc, is_bader=is_bader)

    return self.calc

  def calc_singel_point_sol_eff(self,
                                atoms,
                                kpts,
                                directory='xxx/sol_eff',
                                **kwargs
                                ):
    calc = self.get_calc_sol_eff(directory=directory,
                                 calc_pars_dict=None,
                                 kpts=kpts,
                                 **kwargs)
    if calc.atoms is None:
      calc = self.calc_single_point(atoms=atoms,
                                    calc=calc,)
      dbname = os.path.basename(calc.directory.removeprefix('/sol_eff'))
      self.DataBase.db_update_values(
          name=dbname,
          energy_sol_eff=calc.get_potential_energy(),
      )
    return calc

  def calc_relaxation_general(self,
                              atoms,
                              opt_name='lbfgs',
                              fmax=0.05,
                              is_recalc=False,):
    if self.calc.atoms is None:
      atoms = self.AseLearn.calc_relaxation_general(
          atoms=atoms,
          calc=self.calc,
          opt_name=opt_name,
          fmax=fmax,
          is_save_log=True,
          is_save_traj=True,
          is_recalc=is_recalc,
      )
      self.calc.write(filename=os.path.join(self.calc.directory, 'gpaw.gpw'))
      self.DataBase.write_relax_2db(calc=self.calc)

    return self.calc

  def calc_lattice_constant(self,
                            atoms: ase.Atoms = None,
                            filter_name='sf',
                            filter_mask=[True]*6,
                            fmax=0.05,
                            is_recalc=False,):
    if self.calc.atoms is None:
      atoms = self.AseLearn.calc_lattice_constant(
          atoms=atoms,
          calc=self.calc,
          filter_name=filter_name,
          filter_mask=filter_mask,
          fmax=fmax,
          is_save_traj=True,
          is_save_log=True,
          is_recalc=is_recalc,
      )
      self.calc.write(os.path.join(self.calc.directory, 'gpaw.gpw'))
      self.DataBase.write_relax_2db(calc=self.calc)
    return self.calc

  def calc_example(self):
    # 1. 保存为指定的数据库
    self.DataBase.db = ase.db.connect(
        '/Users/wangjinlong/my_server/my/W_Re_potential/database_for_WReHe_gpaw/W_Re_He.json')
    # 2. 建立模型
    atoms = self.Model.get_atoms_normal_crsytal(name='W', )
    # 3. 更新计算器, 设置参数
    self.get_calc(
        directory='/Users/wangjinlong/my_server/my/W_Re_potential/database_for_WReHe_gpaw/W_bulk',
        calc_mode='pw',
        kpts={'density': 3.0, 'gamma': True})
    # 4. 计算晶格常数
    self.calc_lattice_constant(atoms=atoms, fmax=0.01)
    # 5. 查看结果
    # la = self.Model.get_lc_a_from_atoms(atoms_relaxed=gp.calc.atoms)
    return

  def relaxation(self, atoms,
                 kpts=[1]*3,
                 directory='/Users/wangjinlong/my_server/my/W_Re_potential/database_for_WReHe_gpaw/W_dimmer',):
    """ 直接计算或者 写入 py 文件
    ---
    还需要在 run.py 中加入 atoms  和 kpts 设置  以后再考虑怎么加入
    ---
    atoms = gp.DataBase.get_atoms(name='W_bulk',
                                  fname_db=fname_db)
    lc = gp.Model.get_lc_a_from_atoms(atoms_relaxed=atoms)
    atoms = ase.build.bulk('W', a=lc, cubic=True).repeat(4)
    atoms = gp.Model.delete_atom(atoms=atoms, index_list=[0])
    """
    def func():
      from soft_learn_project.gpaw_learn import gpawLearn
      import os
      import ase.db
      gp = gpawLearn.GpawLearn()
      fname_db = os.path.join(os.environ['HOME'],
                              'my_server/my/W_Re_potential/database_for_WReHe_gpaw/W_Re_He.json')
      gp.DataBase.db = ase.db.connect(fname_db
                                      )
      gp.get_calc(directory='.',
                  is_save_log=True,
                  kpts=kpts)
      gp.calc_relaxation_general(atoms,)

    self.AseLearn.write_py_from_code(func=func,
                                     directory=directory,
                                     )
    return
  # ---

  def calc_polarizability_tensor(self,
                                 atoms: ase.Atoms,
                                 calc: gpaw.calculator.GPAW,
                                 fname_polarizability_tensor='xx/polarizability_tensor',
                                 ):
    """Calculate polarizability tensor
    """
    from soft_learn_project import pickleLearn
    if os.path.exists(fname_polarizability_tensor):

      polarizability_tensor = pickleLearn.PickleLearn(
      ).load_pyobj(fname=fname_polarizability_tensor)
    else:
      atoms.calc = calc
      polarizability_tensor = gpaw.external.static_polarizability(atoms=atoms,)
      pickleLearn.PickleLearn().dump_pyobj(
          pyobj=polarizability_tensor,
          fname=fname_polarizability_tensor)
    print('Polarizability tensor (units Angstrom^3):')
    print(polarizability_tensor * ase.units.Bohr * ase.units.Ha)
    w, v = np.linalg.eig(polarizability_tensor)
    print('Eigenvalues', w * ase.units.Bohr * ase.units.Ha)
    print('Eigenvectors', v)
    print('average polarizablity', w.sum() *
          ase.units.Bohr * ase.units.Ha / 3, 'Angstrom^3')

    return polarizability_tensor

  def relaxtion_lattice_calc_eos_method_bccfcc(self,
                                               atoms: ase.Atoms,
                                               calc: gpaw.calculator.GPAW,
                                               bravais_lattice='bcc|fcc',
                                               kpts=(5, 5, 5),
                                               ):
    """* 对于bcc 和 fcc 非常简单, 对于 hcp和其它形状还是用 tensor 方法

    Args:
        atoms (ase.Atoms): _description_
        calc (gpaw.calculator.GPAW): _description_
        bravais_lattice (str, optional): _description_. Defaults to 'bcc|fcc'.
        kpts (tuple, optional): _description_. Defaults to (5, 5, 5).

    Returns:
        _type_: _description_
    """

    atoms.calc = calc
    calc.set(kpts=kpts)
    eos = ase.eos.calculate_eos(atoms=atoms,
                                trajectory=os.path.join(calc.directory,
                                                        'gpaw.traj'),
                                npoints=5)
    volume, energy, bulk_modulus = eos.fit()
    # 看图
    eos.plot(show=True)
    if bravais_lattice == 'fcc':
      lc = (4 * volume)**(1 / 3.0)
    elif bravais_lattice == 'bcc':
      lc = (2 * volume)**(1 / 3.0)
      pass
    ase.parallel.parprint(f'优化的晶格常数为lc={lc}')
    # atoms.set_cell([(lc, 0, 0), (0, lc, 0), (0, 0, lc)])
    # 使用优化的晶格常数
    # atoms = ase.build.bulk(name='W', crystalstructure='bcc', a=lc, )
    return eos

  def calc_vib_get_vibData(self,
                           atoms: ase.Atoms,
                           calc: gpaw.calculator.GPAW,
                           indices=None,
                           vib_log='vib_summary.log',
                           is_show_summary=False,
                           is_write_mode=False,

                           ):
    """ 迟豫目录下的vib 中, 如果有数据直接读取结果
    None 表示计算所有原子的振动频率
    """

    calc.set(symmetry='off')  # 是否有必要？
    atoms.calc = calc
    vib = ase.vibrations.Vibrations(atoms=atoms,
                                    name=calc.directory,
                                    indices=indices,)
    vib.run()
    vib.summary(log=vib_log)
    if is_show_summary:
      vib.summary(method='frederiksen',)
    if is_write_mode:
      # Make trajectory files to visualize normal modes:
      # 第一个振动模式文件, 如果不存在, 则写入振动模式
      fname_vib_traj = os.path.join(
          os.path.dirname(calc.directory), 'vib.0.traj')
      if not os.path.exists(fname_vib_traj):
        vib.write_mode()
    vibData = vib.get_vibrations()  # vibData 类
    return vibData

  def calc_vib_get_vibData_wrapper(self,
                                   calc_relax: gpaw.calculator.GPAW,
                                   indices=None,
                                   ):
    """ 迟豫目录下的vib 中, 如果有数据直接读取结果
    """
    directory = os.path.join(calc_relax.directory, 'vib')
    calc = self.get_calc(directory=directory,
                         **calc_relax.parameters)
    vib_data = self.calc_vib_get_vibData(
        atoms=calc_relax.atoms,
        calc=calc,
        indices=indices,
        is_show_summary=False,
        is_write_mode=True,
        vib_log=os.path.join(
            directory, 'vib_summary.log')
    )
    return vib_data

  def photon_dos(self, vibData: ase.vibrations.VibrationsData):
    vibData.get_pdos().plot()
    return

  def get_thermochemistry_idealgas(self,
                                   calc_with_atoms: gpaw.calculator.GPAW,
                                   vibData: ase.vibrations.VibrationsData,
                                   temperature=300,
                                   pressure=101325,
                                   ):
    atoms = calc_with_atoms.get_atoms()

    if len(atoms) == 1:
      geometry = 'monatomic'
    elif len(atoms) == 2:
      geometry = 'linear'
    else:
      geometry = 'nonlinear'
    potentialenergy = calc_with_atoms.get_potential_energy()
    vib_energies = vibData.get_energies()
    thermo = ase.thermochemistry.IdealGasThermo(atoms=atoms,
                                                potentialenergy=potentialenergy,
                                                vib_energies=vib_energies,
                                                symmetrynumber=2,
                                                spin=0.0,
                                                geometry=geometry,
                                                ignore_imag_modes=True,
                                                )
    gibbs_energy = thermo.get_gibbs_energy(temperature=temperature,
                                           pressure=pressure,
                                           verbose=False)
    entropy = thermo.get_entropy(temperature=temperature,
                                 pressure=pressure,
                                 verbose=False)
    zpe = thermo.get_ZPE_correction()
    enthalpy = thermo.get_enthalpy(temperature=temperature,
                                   verbose=False)
    thermo_data = {
        # 'thermo': thermo,
        'entropy': entropy,
        'zpe': zpe,
        'enthalpy': enthalpy,
        'gibbs_energy': gibbs_energy}

    return thermo_data

  def get_thermochemistry_adsorbate_slab(self,
                                         calc_with_atoms: gpaw.calculator.GPAW,
                                         vibData: ase.vibrations.VibrationsData,
                                         temperature=300,
                                         ):
    potentialenergy = calc_with_atoms.get_potential_energy()
    vib_energies = vibData.get_energies()
    thermo = ase.thermochemistry.HarmonicThermo(vib_energies=vib_energies,
                                                potentialenergy=potentialenergy,
                                                ignore_imag_modes=True)

    zpe = thermo.get_ZPE_correction()
    entropy = thermo.get_entropy(temperature=temperature,
                                 verbose=False)
    internal_energy = thermo.get_internal_energy(temperature=temperature,
                                                 verbose=False)
    helmholtz_energy = thermo.get_helmholtz_energy(temperature=temperature,
                                                   verbose=False)
    thermo_data = {
        # 'thermo': thermo,
        'zpe': zpe,
        'entropy': entropy,
        'internal_energy': internal_energy,
        'helmholtz_energy': helmholtz_energy}

    return thermo_data

  def calc_gibbs_energy_idealgas(self,
                                 calc_relax,
                                 calc_se,
                                 temperature=298.15,
                                 pressure=101325,
                                 ):
    """ 计算 Gibbs 自由能
    """
    vib_data = self.calc_vib_get_vibData_wrapper(calc_relax=calc_relax,
                                                 indices=None,)
    thermo_data_dict_all = {}
    for calc in [calc_relax, calc_se]:
      thermo_data_dict = self.get_thermochemistry_idealgas(
          calc_with_atoms=calc,
          vibData=vib_data,
          temperature=temperature,
          pressure=pressure,)
      thermo_data_dict = self.DataBase.write_thermo_2db_gpaw(calc=calc,
                                                             thermo_data_dict=thermo_data_dict)
      thermo_data_dict_all.update(thermo_data_dict)
    return thermo_data_dict_all

  def calc_gibbs_energy_adsorbate_on_slab(self,
                                          calc_relax,
                                          calc_se,
                                          indices_vib=None,
                                          atom_symbol_list=['O', 'H'],
                                          position_z_downlim=None,
                                          temperature=298.15,
                                          ):
    """ 计算 Gibbs 自由能
    提供 index_vib 用于选择振动的原子 或者 atom_symbol_list
    """

    if indices_vib is None:
      indices_vib = self.AseLearn.get_atoms_index_list(
          atoms=calc_relax.atoms,
          atom_symbol_list=atom_symbol_list,
          position_z_downlim=position_z_downlim,
      )

    vib_data = self.calc_vib_get_vibData_wrapper(calc_relax=calc_relax,
                                                 indices=indices_vib,)
    thermo_data_dict_all = {}
    for calc in [calc_relax, calc_se]:
      thermo_data_dict = self.get_thermochemistry_adsorbate_slab(
          calc_with_atoms=calc,
          vibData=vib_data,
          temperature=temperature,)
      thermo_data_dict = self.DataBase.write_thermo_2db_gpaw(
          calc=calc,
          thermo_data_dict=thermo_data_dict)
      thermo_data_dict_all.update(thermo_data_dict)
    return thermo_data_dict_all

  def calc_band_structure(self, fname_gpw,
                          kpts={'path': 'GMKG', 'npoints': 60},
                          #  fname_bs='band_structure.json',
                          fig_pars_dict={'emin': -3, 'emax': 3},
                          ):
    fname_bs = os.path.splitext(fname_gpw)[0] + '_band_structure.json'
    if not os.path.exists(fname_bs):
      # Restart from ground state and fix potential:
      calc = gpaw.calculator.GPAW(restart=fname_gpw).fixed_density(
          # nbands=16,
          symmetry='off',
          kpts=kpts,
          # convergence={'bands': 8}  # 这是干什么的
      )
      band_structure = calc.band_structure()
      # calc.write('Pt_bands.gpw')
      band_structure.write(fname_bs)
    else:
      band_structure = ase.spectrum.band_structure.BandStructure
      band_structure = band_structure.read(fname_bs)

    # 以费米能级为参考后的能带 band_structure.reference 是费米能级
    band_structure = band_structure.subtract_reference()
    band_structure.plot(filename=os.path.splitext(fname_gpw)[0] + '_band_structure.pdf',
                        show=True, emin=fig_pars_dict['emin'],
                        emax=fig_pars_dict['emax'])
    # Finally, the bandstructure can be plotted (using ASE’s band-structure tool ase.spectrum.band_structure.BandStructure):
    ase.parallel.parprint(
        "进行画图: band_structure.plot(filename='band_structure.pdf', show=True, emin=-3, emax=3, marker='o')")
    return band_structure

  def calc_band_structure_example(self, ):
    """https://wiki.fysik.dtu.dk/ase/gettingstarted/tut04_bulk/bulk.html"""
    calc = gpaw.calculator.GPAW(restart='groundstate.gpw')
    atoms: ase.Atoms = calc.get_atoms()
    path = atoms.cell.bandpath()
    calc = calc.fixed_density(kpts=path, symmetry='off')
    atoms.get_potential_energy()
    bs: ase.spectrum.band_structure.BandStructure = calc.band_structure()
    bs.write('bs.json')
    # bs.plot()
    return

  def get_electrostatic_potential(self,
                                  directory='/Users/wangjinlong/my_server/my/myORR_B/slab/X_graphene/As_DVG/gpaw_bader'):
    """查看静电势
    """
    calc = self.get_calc(directory=directory)
    local_potential = calc.get_electrostatic_potential()
    plt.imshow(local_potential.sum(axis=2))
    plt.colorbar(label='Electrostatic Potential')
    plt.show()

    pass

  # dos

  def plot_tdos(self, calc=gpaw.calculator.GPAW, width=0.2):
    fig = plt.figure()
    ax = fig.add_subplot()
    ef = calc.get_fermi_level()
    energy, dos = calc.get_dos(spin=0, width=width)
    ax.plot(energy - ef, dos)
    if calc.get_number_of_spins() == 2:
      energy, dos = calc.get_dos(spin=1, width=width)
      ax.plot(energy - ef, -dos)
      ax.legend(('up', 'down'), loc='best')
    ax.set_xlabel(r'$\epsilon - \epsilon_F \ \rm{(eV)}$')
    ax.set_ylabel('Density of States (1/eV)')

    from soft_learn_project.matplotlib_learn import matplotlibLearn
    ax = matplotlibLearn.Features().TwoDimension.add_vlines_hlines(ax=ax)
    return fig, ax

  def plot_ldos(self, calc: gpaw.calculator.GPAW,
                a=0, lorbs='spd', width=0.2,
                is_save=False, fname='xxx/ldos.pdf'):
    """某个原子的dos: ldos, 可以考虑 pldos
    a: 表示根据原子的索引画ldos

    """
    from soft_learn_project.matplotlib_learn import matplotlibLearn
    color_list = matplotlibLearn.Features().color_list

    fig = plt.figure()
    ax = fig.add_subplot()
    # Plot s, p, d projected LDOS:
    ef = calc.get_fermi_level()
    for c, color in zip(lorbs, color_list):
      energies, ldos = calc.get_orbital_ldos(
          a=a, spin=0, angular=c, width=width)
      ax.plot(energies - ef, ldos, label=c + '-up', color=color)
      energies, ldos = calc.get_orbital_ldos(
          a=a, spin=1, angular=c, width=width)
      ax.plot(energies - ef, -ldos, label=c + '-down', color=color)

    # 这样就是sp 的总态密度
    # x, y = calc.get_orbital_ldos(a=0, spin=1, angular='sp',width=0.2)
    # plt.plot(x-ef,-y,label='down')
    ax.legend()
    ax.set_xlabel(r'$\epsilon - \epsilon_F \ \rm{(eV)}$')
    ax.set_ylabel('Density of States (1/eV)')
    ax = matplotlibLearn.Features().TwoDimension.add_vlines_hlines(ax=ax)

    if is_save:
      fig.savefig(fname=fname, bbox_inches='tight',)
    return fig, ax

  def plot_electronic_density(self,
                              directory='/Users/wangjinlong/my_server/my/myORR_B/slab/X_graphene/As_DVG/gpaw_bader'):
    # 获取 GPAW 计算的赝势密度
    calc = self.get_calc(directory=directory)
    density = calc.get_pseudo_density()

    # # 在某个特定的切片上绘制电荷密度分布
    # plt.imshow(density.sum(axis=2))  # 投影在 xy 平面
    # plt.colorbar(label='Electron Density')
    # plt.show()

    # 提取某个切片的密度数据（例如 z = mid 位置的切片）
    z_slice = density[:, :, density.shape[2] // 2]  # 选取 z 方向中间的一层
    # 绘制电荷密度的等值线图
    plt.contour(z_slice, levels=10, cmap='viridis')  # 设置 20 条等值线
    plt.colorbar(label='Electron Density')
    plt.title('Electron Density Contour Map (z-plane slice)')
    plt.xlabel('X direction')
    plt.ylabel('Y direction')
    plt.show()

  # wrapper
  def calc_bader_wrapper(self, calc,):
    atoms = self.gpawTutorial.TutorialChargeAnalysis().method_bader(
        calc=calc, gridrefinement=2)
    return atoms

  def calc_ideagas_completely(self,
                              atoms,
                              kpts=(1, 1, 1),
                              directory='xxx/H2',
                              pressure=101325,
                              **kwargs):
    if self.calc_pars_default['mode'] == 'fd':
      atoms.pbc = False
    if len(atoms) == 1:
      calc = self.calc_single_point(atoms=atoms,
                                    kpts=kpts,
                                    hund=True,
                                    directory=directory,
                                    **kwargs)
      # sol_eff
      directory_se = os.path.join(calc.directory, 'sol_eff')
      calc_se = self.calc_singel_point_sol_eff(
          atoms=calc.atoms,
          kpts=kpts,
          hund=True,
          directory=directory_se,
          **kwargs,
      )
      return calc_se
    else:
      calc_relax = self.calc_relaxation_general(
          atoms=atoms,
          kpts=kpts,
          directory=directory,
          **kwargs)
      # sol_eff
      directory_se = os.path.join(calc_relax.directory, 'sol_eff')
      calc_se = self.calc_singel_point_sol_eff(
          atoms=calc_relax.atoms,
          kpts=kpts,
          directory=directory_se,
          **kwargs,
      )
      # thomo_data
      thermo_data_dict = self.calc_gibbs_energy_idealgas(calc_relax=calc_relax,
                                                         calc_se=calc_se,
                                                         pressure=pressure,
                                                         )
      return thermo_data_dict

  def calc_slab_completely(self,
                           atoms,
                           kpts=(3, 3, 1),
                           directory='xxx',
                           **kwargs):
    if self.calc_pars_default['mode'] == 'fd':
      atoms.pbc = (True, True, False)
    calc_relax = self.calc_relaxation_general(
        atoms=atoms,
        kpts=kpts,
        directory=directory,
        **kwargs)
    # sol_eff
    directory_se = os.path.join(calc_relax.directory, 'sol_eff')
    calc_se = self.calc_singel_point_sol_eff(
        atoms=calc_relax.atoms,
        kpts=kpts,
        directory=directory_se,
        **kwargs,
    )

    return

  def calc_adsorbate_on_slab_completely(self,
                                        atoms,
                                        kpts=(3, 3, 1),
                                        directory='xxx',
                                        indices_vib=None,
                                        atom_symbol_list=['O', 'H'],
                                        position_z_downlim=None,
                                        opt_name='bfgs',
                                        **kwargs):
    """ 可以提供 indices_vib 或者 atom_symbol_list 
    """
    if self.calc_pars_default['mode'] == 'fd':
      atoms.pbc = [True, True, False]
    calc_relax = self.calc_relaxation_general(
        atoms=atoms,
        kpts=kpts,
        directory=directory,
        opt_name=opt_name,
        **kwargs)
    # sol_eff
    directory_se = os.path.join(calc_relax.directory, 'sol_eff')
    calc_se = self.calc_singel_point_sol_eff(
        atoms=calc_relax.atoms,
        kpts=kpts,
        directory=directory_se,
        **kwargs,
    )
    # thomo_data
    thermo_data_dict = self.calc_gibbs_energy_adsorbate_on_slab(
        calc_relax=calc_relax,
        calc_se=calc_se,
        indices_vib=indices_vib,
        temperature=298.15,
        atom_symbol_list=atom_symbol_list,
        position_z_downlim=position_z_downlim,)
    return thermo_data_dict

  # wrapper wrapper
  # wrapper example

  def calc_ideagas_completely_O_hpc(self,
                                    fname_py='/Users/wangjinlong/my_server/my/myORR_B/test_O/run.py'):
    self.write_py_from_code(func=self.calc_ideagas_completely_O,
                            fname_py=fname_py)
    pass

  def calc_slab_completely_O2H_Pt111_2x2_hpc(self,
                                             fname_py='/Users/wangjinlong/job/soft_learn/soft_learn_project/gpaw_learn/my_example/Pt111_2x2_system/O2H_Pt111_2x2/run.py'):
    self.write_py_from_code(
        func=self.calc_slab_completely_O2H_Pt111_2x2,
        fname_py=fname_py,
    )

  def calc_adsorbate_on_slab_completely_OH_B_Gra_3x3_get_model(self,
                                                               directory=None,):

    fname_atoms_traj = os.path.join(directory, 'atoms.traj')

    atoms = self.GetModel.graphene_pure(
        surface_size=(3, 3, 1), vacuum=5)
    atoms = self.GetModel.replace_atom_wrapper(
        atoms=atoms,
        index_lists=[[8]],
        symbol_list=['B'])

    atoms = self.GetModel.get_adsorbate_on_slab_model_wrapper(
        slab=atoms,
        adsorbate_name='OH',
        adsorbate_postion_symbol_list=['B'],
        height=2
    )

    atoms.write(filename=fname_atoms_traj)
    print(f'先产生 atoms.traj 然后再读取atoms, 以上的命令直接并行会出错. -> {fname_atoms_traj}')
    return fname_atoms_traj

  def writing_restart_files(self, calc: gpaw.calculator.GPAW):
    # 1.
    calc.write('xyz.gpw')
    # 2. 包括波函数
    # To also save the(potentially very large) wavefunctions, use
    calc.write('xyz.gpw', mode='all')
    # 3. 减小空间 保存单精度
    calc.write('xyz.gpw', precision='single')
    # 4. 这对于非常昂贵的计算非常有用
    n = 3
    calc.attach(calc.write, n, 'xyz.gpw', mode='all')

    # # Reading restart files
    # calc = gpaw.calculator.GPAW('xyz.gpw')
    return calc
