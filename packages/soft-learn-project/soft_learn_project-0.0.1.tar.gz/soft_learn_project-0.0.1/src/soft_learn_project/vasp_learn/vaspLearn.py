import ase
import ase.build
import ase.io
import ase.calculators.vasp
import ase.vibrations
import os
import re
import shutil
import ase.spectrum.band_structure
import numpy as np
import pandas as pd
import ase.io.vasp
import importlib.resources


class Install():
  def __init__(self) -> None:
    """
    """
    pass

  def download(self):
    string = """vasp5.4.4
    https://rutracker.org/forum/viewtopic.php?t=5319869#opennewwindow  # 包括势文件
    
    VASP 完整赝势库
    这是VASP（Vienna Ab initio Simulation Package）的完整赝势库。该库包含了VASP计算中所需的各种赝势文件，适用于不同元素和材料的模拟计算。请注意，虽然我们提供了这些资源，但请大家务必遵守相关的版权协议，尊重原作者的知识产权
    项目地址: https://gitcode.com/open-source-toolkit/9f9b5b
    原文链接：https://blog.csdn.net/gitblog_09754/article/details/143069045 
    git clone https://gitcode.com/open-source-toolkit/9f9b5b.git
    """
    print(string)
    return None

  def buil_env(self, env_name='vasp_test'):
    # mac 下的安装
    # 1. 建立conda 环境
    s1 = f'conda create -n {env_name} python=3 -y'
    # 2. 在 env_name 环境中安装必要的包
    s2 = f'conda activate {env_name}'
    # hdf5 wannier90 不是必要的 # 要确保是mpich, openmpi 会出错不知道为什么, 可以先conda install mpi4py 查看安装的是否是mpich, 如果不是就先安装 mpich: conda install -c conda-forge mpich
    s22 = 'conda install -c conda-forge ipykernel -y '
    # wannier90 现在找不到了
    s3 = 'conda install -c conda-forge mpi4py gfortran fftw openblas scalapack hdf5 -y'
    commend_list = [s1, s2, s3]

    # 建立环境还是自己一步一步来
    print('建立环境还是自己一步一步来, 步骤为:')
    for comend in commend_list:
      print(comend)

  def modify_makefile_include(self,
                              fname='makefile.include',
                              env_name='vasp',
                              ):
    """cp arch/makefile.include.gnu ./makefile.include
    CPP         = gfortran -cpp 
    CC_LIB      = gcc -arch arm64
    CXX_PARS    = g++ -arch arm64
    LLIBS       = -lc++
    # 其它的库使用 
    conda 环境 /Users/wangjinlong/opt/anaconda3/envs/py3918

    file /Users/wangjinlong/opt/anaconda3/envs/py3918/bin/gfortran 
    file *o 可以查看 文件的架构 
    Args:
        fname (str, optional): _description_. Defaults to 'makefile.include'.
        env_name (str, optional): _description_. Defaults to 'test'.
    """
    # 进入VASP 安装目录, 基于gnu来安装
    import platform
    self.system = platform.system()
    from soft_learn_project.re_learn import re_learn
    os.system(f'cp arch/makefile.include.gnu ./{fname}')

    with open(fname) as f:
      content = f.read()

    # 修改 makefile.include
    # os.system('gcc-13 --version')
    # os.system('gcc --version')  # 根据这两条命令可以看到 gcc 是clang 而gcc-13是gnu gcc
    # CPP         = gcc-13 -E -C -w $*$(FUFFIX) >$*$(SUFFIX) $(CPP_OPTIONS) 中的 gcc 改为gcc-13
    # CC_LIB      = gcc 改为 gcc-13
    if self.system == 'Darwin':
      for pattern_gcc in [r'CPP.*?=.*?gcc.*?\n',
                          r'CC_LIB.*?=.*?gcc.*?\n']:
        content = re_learn.Features().modify_str(
            content=content,
            pattern=pattern_gcc,
            old_str_pattern='gcc',
            new_str='gcc-13',
        ).content_modified
    elif self.system == 'Linux':
      pass

    # 因为macOS 不再默认安装libstdc++库，而使用了libc++库 修改 LLIBS  += -lstdc++ 中的 -lstdc++ 为 -lc++
    if self.system == 'Darwin':
      content = re_learn.Features().modify_str(
          content=content,
          pattern=r'LLIBS.*?=.*?lstdc.*?\n',
          old_str_pattern=r'lstdc',
          new_str=r'lc',
      ).content_modified
    elif self.system == 'Linux':
      pass

    # 所有的库都安装在了 /Users/wangjinlong/opt/anaconda3/envs/vasp_test/lib 故修改 四个root
    lib_root = f'/opt/anaconda3/envs/{env_name}'
    for pattern_root in ['OPENBLAS_ROOT',
                         'SCALAPACK_ROOT',
                         'HDF5_ROOT',
                         'WANNIER90_ROOT',]:
      content = re_learn.Features().modify_str(
          content=content,
          pattern=fr'{pattern_root}.*?=.*?\n',
          old_str_pattern=r'/.*?\n',
          new_str=lib_root+'\n',
      ).content_modified

    # 由于需要 libfftw3.a 文件 故找到 libfftw3.a 所在的目录
    fftw_root = lib_root
    content = re_learn.Features().modify_str(
        content=content,
        pattern=fr'FFTW_ROOT.*?=.*?\n',
        old_str_pattern=r'/.*?\n',
        new_str=fftw_root+'\n',
    ).content_modified

    # 写入文件
    with open(fname, mode='w') as f:
      f.write(content)

    print(f'{fname} 文件修改完成')

  def modify_neb(self, vtst_path='/Users/wangjinlong/my_linux/soft_learn/vasp_learn/vtstcode-198/vtstcode6.4/'):
    """http://theory.cm.utexas.edu/vtsttools/installation.html
    """
    # 备份 main.F  .objects
    if not os.path.exists('src/main.F.bk'):
      shutil.copy('src/main.F', 'src/main.F.bk')
      shutil.copy('src/.objects', 'src/.objects.bk')
      shutil.copy('src/makefile', 'src/makefile.bk')
      # 复制文件
      shutil.copytree(
          '/Users/wangjinlong/my_linux/soft_learn/vasp_learn/vtstcode-198/vtstcode6.4/', dst='src/', dirs_exist_ok=True)

    # 修改 src/main.F
    with open('src/main.F.bk') as fr, open('src/main.F', mode='w') as fw:
      content = fr.read()
      # s1 = """CALL CHAIN_FORCE(T_INFO%NIONS,DYN%POSION,TOTEN,TIFOR, &
      #    LATT_CUR%A,LATT_CUR%B,IO%IU6)"""
      # s2 = """CALL CHAIN_FORCE(T_INFO%NIONS,DYN%POSION,TOTEN,TIFOR, &
      #    TSIF,LATT_CUR%A,LATT_CUR%B,IO%IU6)"""
      # content = content.replace(s1,s2)
      content = content.replace(r'LATT_CUR%A,LATT_CUR%B,IO%IU6)',
                                r'TSIF,LATT_CUR%A,LATT_CUR%B,IO%IU6)', 1)
      content = content.replace('IF (LCHAIN) CALL chain_init( T_INFO, IO)',
                                'CALL chain_init( T_INFO, IO)')
      fw.write(content)
    # 修改 .objects
    s = """bfgs.o dynmat.o instanton.o lbfgs.o sd.o cg.o dimer.o bbm.o \
    fire.o lanczos.o neb.o qm.o \
    pyamff_fortran/*.o ml_pyamff.o \
    opt.o \
    chain.o \
    """
    with open('src/.objects.bk') as fr, open('src/.objects', mode='w') as fw:
      content = fr.read()
      content = content.replace('chain.o', s)
      fw.write(content)
    # 修改 src/makefile
    with open('src/makefile.bk') as fr, open('src/makefile', mode='w') as fw:
      content = fr.read()
      content = content.replace('LIB=lib parser', 'LIB=lib parser pyamff_fortran').replace(
          'dependencies: sources', 'dependencies: sources libs')
      fw.write(content)

  def build_bin(self,
                is_clean=False,
                n_cores=4,
                vasp_type='std',
                fname='make_info.txt',):
    # 编译
    if is_clean:
      os.system('make veryclean')
    print(f'编译中... 请查看输出文件->{fname}')
    os.system(f'make DEPS=1 -j{n_cores} {vasp_type} 2>&1 > {fname}')
    pass

  def build_vasp_gfortran_openmpi(self):
    # gfortran+openmpi-编译vasp.txt
    string = """
    https://www.ivofilot.nl/posts/view/33/How+to+compile+VASP+5.4.1+on+a+MacBook+running+OS+X+El+Capitan
    #gfortran+openmpi 编译安装vasp 
    sudo apt-get install make
    sudo apt-get install g++ build-essential
    sudo apt-get install gfortran
    sudo apt-get install libopenmpi-dev
    sudo apt-get install libblas-dev
    sudo apt-get install liblapack-dev
    sudo apt-get install libscalapack-mpi-dev
    sudo apt-get install libscalapack-openmpi2.1
    sudo apt-get install libfftw3-dev
    sudo apt-get install libfftw3-3
    sudo apt-get install build-essential libopenmpi-dev libfftw3-dev libblas-dev liblapack-dev libscalapack-mpi-dev libblacs-mpi-dev

    #安装指导
    #https://www.ivofilot.nl/posts/view/31/How+to+compile+VASP+5.4.1+for+Linux+Debian+using+the+GNU+compiler
    <<!
    cd vasp.5.4.1
    make std
    cd - 1>/dev/null
    !
    """
    print(string)
    return None


class LearnRecords():
  def __init__(self) -> None:
    """ * 学习网址
    - url='https://wiki.fysik.dtu.dk/ase/ase/calculators/vasp.- html#brillouin-zone-sampling'
    - vasp_wiki= 'https://www.vasp.at/wiki/index.php/The_VASP_Manual'
    - 文字教程:http://sobereva.com/455
    - 视频教程:https://www.bilibili.com/video/av39616222
    ---
    1. 设置变量
    vasp_path = os.popen('which vasp_std').read().strip()
    s1 = f'export ASE_VASP_COMMAND="mpiexec {vasp_path}"'  # 或者在终端执行s1命令
    vasp_pot_path = '/Users/wangjinlong/my_script/sci_research/vasp_use/vasp_pot'
    s2 = f'export VASP_PP_PATH={vasp_pot_path}'
    # 可选 when doing van der Waals calculations, where luse_vdw=True.
    s3 = 'export ASE_VASP_VDW=$HOME/<path-to-vdw_kernel.bindat-folder>'
    s4 = 'export ASE_VASP_VDW='
    print('在终端执行以下命令!, 需要手动')
    for s in [s1, s2, s4]:
      # print(s)
      pass
    # 在python环境中执行
    vasp_path = os.popen('which vasp_std').read().strip()
    vasp_pot_path = '/Users/wangjinlong/my_script/sci_research/vasp_use/vasp_pot'
    os.environ['ASE_VASP_COMMAND'] = f'mpiexec -np 4 {vasp_path}'
    os.environ['VASP_PP_PATH'] = vasp_pot_path
    os.environ['ASE_VASP_VDW'] = ''

    # This is not required, if the command keyword is specified in the calculator itself. The command keyword also overrides the enrivonment variables, e.g.:

    # Vasp(command='mpiexec vasp_std')
    self.Vasp = ase.calculators.vasp.Vasp()
    """
    pass

  def incar(self):
    # 体系总价电子20，将NELECT＝22 使体系带负电荷, 以考虑-2 价的阴离子在表面的吸附
    potim = 0.2  # 改变步长， the default value 0.5. Finally
    ibrion = 1  # use DIIS algorithm to converge
    ibrion = 2,  # use the conjugate gradient algorithm

    """ ivdw
    IVDW = 0
    不使用任何范德华力校正（默认设置）。
    IVDW = 1
    使用D2范德华力校正（Grimme D2 方法）。
    参考：S. Grimme, J. Comput. Chem., 27, 1787 (2006).
    IVDW = 2
    使用D3范德华力校正（Grimme D3 方法）。
    参考：S. Grimme, et al., J. Chem. Phys., 132, 154104 (2010).
    IVDW = 10

    使用DFT-D3(BJ)范德华力校正（Grimme D3 方法与Becke-Johnson阻尼）。
    参考：S. Grimme, et al., J. Chem. Phys., 132, 154104 (2010); S. Grimme, S. Ehrlich, and L. Goerigk, J. Comput. Chem., 32, 1456 (2011).
    IVDW = 11

    使用TS-MBD方法（Tkatchenko-Scheffler方法与多体色散校正）。
    参考：A. Tkatchenko, et al., Phys. Rev. Lett., 108, 236402 (2012).
    
    IVDW = 12
    使用optB88-vdW方法（优化B88交换泛函与范德华力校正）。
    参考：J. Klimeš, D. R. Bowler, and A. Michaelides, Phys. Rev. B, 83, 195131 (2011).
    IVDW = 20

    使用DFT-D4范德华力校正（Grimme D4 方法）。
    参考：S. Grimme, et al., J. Chem. Phys., 154, 064103 (2021).

    D2方法（IVDW = 1）：适用于简单的有机分子和小分子间相互作用。
    D3方法（IVDW = 2）：改进了D2方法，适用于更广泛的体系。
    TS-MBD方法（IVDW = 11）：适用于大分子和复杂体系，考虑了多体相互作用。
    optB88-vdW方法（IVDW = 12）：专为层状材料和吸附体系设计。
    D4方法（IVDW = 20）：最新的范德华力校正方法，具有更高的精度和广泛适用性。
    """
    ivdw = 12,
    pass

  def incar_偶极修正(self):
    """ vasp wiki: https://www.vasp.at/wiki/index.php/Monopole_Dipole_and_Quadrupole_Corrections

    LDIPOL    = T
    IDIPOL    = 3 # IDIPOL    = 4 用于isolated molecules.
    DIPOL     = 0.5 0.5 0.5 
    # 查看偶极矩
    grep dipolmoment OUTCAR | tail -1

    """
    pass

  def kpts(self,):
    """k点密度的计算 
    a1,a2,a3 为晶格在三个方向上的长度
    b1,b2,b3 为倒格矢的长度 
    k1,k2,k3 为 三个方向上的 k 点
    V = a1 . (a2 x a3) # 对于正交的情况 V = a1*a2*a3
    b1 = 2*pi * a2 x a3 /V 
    Vb = b1 . (b2 x b3) 
    k_density = k1*k2*k3 /Vb 
    vaspkit 中的k 点设置为 1/k_density 

    在计算中，通常使用奇数个 k 点来确保伽玛点（Gamma point）的包含。伽玛点是 k 空间中的原点，代表了晶体的对称中心。
    Automatic mesh (title)
    0 (为0时，表示自动产生K点)
    M (表示采用Monkhorst-Pack方法生成K点坐标, 也可以为G, 表示包括gamma点)   
    5 5 5(对应于5x5x5网格)
    0 0 0(原点平移大小)

    """
    ase.calculators.vasp.Vasp(kpts=(6, 6, 6), gamma=True)  # Gamma 点网格
    ase.calculators.vasp.Vasp(kpts=(6, 6, 6))  # Monkhorst-Pack 网格
    # 能带路径
    ase.calculators.vasp.Vasp(kpts={'path': 'LGXUKG',     # The BS path
                                    'npoints': 120},    # Number of points along the path)
                              )
    # kpts 的设置可以根据密度来设置, 参考
    # kpts = {'density': 2.5, 'gamma': True}  # MP with a minimum density of 2.5 points/Ang^-1 include gamma-point
    from soft_learn_project.gpaw_learn import gpawLearn
    # gpawLearn.Features().parameters()
    pass

  def poscar(self):
    # 获取元胞
    import pymatgen.core
    # my_struc = Structure.from_file("./e01_solid-cd-Si/Si_mp-149_conventional_standard.cif")
    mystruc = pymatgen.core.Structure.from_file(
        '/Users/wangjinlong/my_linux/soft_learn/vasp_learn/tmp/Si64/POSCAR')
    atoms = mystruc.to_primitive().to_ase_atoms()

  def outcar(self):
    total_energy = '系统的总能是 outca r中 energy without entropy 后面的值'
    E_fermi = 'E-fermi 后面的值 :  -8.8433'

    pass

  def N2(self, fname_struct='N2.xyz'):
    atoms = ase.build.molecule('N2')
    atoms.center(vacuum=5)
    atoms.pbc = True

    # To perform a VASP DFT calculation, we now set up a calculator object.
    calc = ase.calculators.vasp.Vasp(xc='pbe',  # Select exchange-correlation functional
                                     encut=400,  # Plane-wave cutoff
                                     kpts=(1, 1, 1))  # k-points

    atoms.calc = calc
    en = atoms.get_potential_energy()  # This call will start the calculation
    ase.io.write(filename=fname_struct, images=atoms,)
    print('Potential energy: {:.2f} eV'.format(en))

  def other_examles(self,):
    url = 'https://wiki.fysik.dtu.dk/ase/ase/calculators/vasp.html#vasp-calculator'
    pass

  def spin_polarized_calculation(self):
    # If the atoms object has non-zero magnetic moments, a spin-polarized calculation will be performed by default.
    # Here follows an example how to calculate the total magnetic moment of a sodium chloride molecule.

    a = [6.5, 6.5, 7.7]
    d = 2.3608
    # In this example the initial magnetic moments are assigned to the atoms when defining the Atoms object. The calculator will detect that at least one of the atoms has a non-zero magnetic moment and a spin-polarized calculation will automatically be performed.
    NaCl = ase.Atoms([ase.Atom('Na', [0, 0, 0], magmom=1.928),
                      ase.Atom('Cl', [0, 0, d], magmom=0.75)],
                     cell=a)

    calc = ase.calculators.vasp.Vasp(prec='Accurate',
                                     xc='PBE',
                                     lreal=False)
    NaCl.calc = calc

    print(NaCl.get_magnetic_moment())

    # It is also possible to manually tell the calculator to perform a spin-polarized calculation:

  def lda_plus_u(self,):
    # LD(S)A+U
    # The VASP +U corrections can be turned on using the default VASP parameters explicitly, by manually setting the ldaul, ldauu and ldauj parameters, as well as enabling ldau.
    # However, ASE offers a convenient ASE specific keyword to enable these, by using a dictionary construction, through the ldau_luj keyword. If the user does not explicitly set ldau=False, then ldau=True will automatically be set if ldau_luj is set. For example:
    calc = ase.calculators.vasp.Vasp(ldau_luj={'Si': {'L': 1, 'U': 3, 'J': 0}})

  def restart_old_calculation(self):
    # To continue an old calculation which has been performed without the interface use the restart parameter when constructing the calculator
    calc = ase.calculators.vasp.Vasp(restart=True)
    atoms = calc.get_atoms()
    atoms.get_potential_energy()

  def Storing_the_calculator_state(self, calc: ase.calculators.vasp.Vasp):
    # 储存计算器状态 After a calculation
    calc.write_json('mystate.json')

    # 恢复计算器状态
    calc = ase.calculators.vasp.Vasp()
    calc.read_json('mystate.json')
    atoms = calc.get_atoms()  # Get the atoms object

    # ASE计算器不包含有关波函数或电荷密度的信息，因此这些信息不存储在字典或JSON文件中，因此结果可能在重新启动计算时发生变化。
    pass

  def Vibrational_Analysis(self):
    """Vibrational analysis can be performed using the Vibrations class or using the VASP internals (e.g. with IBRION=5). When using IBRION=5-8, the corresponding vibrational analysis can be represented by  from the calculator using
    """
    # retrieving a VibrationsData object
    ase.calculators.vasp.Vasp.get_vibrations()  # 有问题没发现这个方法
    # From the OUTCAR, the energies of all modes can be retrieved
    ase.calculators.vasp.Vasp.read_vib_freq()
    pass

  def band_structure(self):
    """VASP provides a “line-mode” for the generation of band-structure paths. While this is not directly supported by ASE, relevant functionality exists in the ase.dft.kpoints module. For example:
    import ase.build
    from ase.dft.kpoints import bandpath

    si = ase.build.bulk('Si')
    kpts, x_coords, x_special_points = bandpath('GXL', si.cell, npoints=20)
    """

    import ase.build
    si = ase.build.bulk('Si')

    mydir = 'bandstructure'    # Directory where we will do the calculations

    # Make self-consistent ground state
    calc = ase.calculators.vasp.Vasp(kpts=(4, 4, 4), directory=mydir)
    si.calc = calc
    si.get_potential_energy()  # Run the calculation

    # Non-SC calculation along band path
    kpts = {'path': 'WGX',     # The BS path
            'npoints': 30}     # Number of points along the path
    calc.set(isym=0,           # Turn off kpoint symmetry reduction
             icharg=11,        # Non-SC calculation
             kpts=kpts)
    si.get_potential_energy()  # Run the calculation

    # As this calculation might be longer, depending on your system, it may be more convenient to split the plotting into a separate file, as all of the VASP data is written to files. The plotting can then be achieved by using the restart keyword, in a second script
    mydir = 'bandstructure'    # Directory where we did the calculations

    # Load the calculator from the VASP output files
    calc_load = ase.calculators.vasp.Vasp(restart=True, directory=mydir)

    bs = calc_load.band_structure()  # ASE Band structure object
    bs.plot(emin=-13, show=True)    # Plot the band structure

    # We could also find the band gap in the same calculation,
    from ase.dft.bandgap import bandgap
    print(bandgap(calc_load))

  def dos(self, calc=ase.calculators.vasp):
    # The Vasp calculator also allows for quick access to the Density of States (DOS), through the ASE DOS module, see DOS. Quick access to this function, however, can be found by using the get_dos() function:

    energies, dos = calc.get_dos()

  def get_epsilon(self):
    """计算介电常数 
    计算过程：

    1、进行标准的DFT结构优化计算
    2、计算电子对介电函数的贡献与频率的关系
    3、计算离子对介电函数的贡献与频率的关系
    4、分别对电子和离子介电函数做零频近似并做加和
    """
    # 创建 NaCl 晶体
    atoms = ase.build.bulk(
        'NaCl', crystalstructure='rocksalt', a=5.556)  # 设置晶格常数

    # 1、标准的DFT结构优化计算
    calc = ase.calculators.vasp.Vasp(atoms=atoms,
                                     directory='relaxation',
                                     kpts=[11]*3,
                                     prec='acur',
                                     ismear=0,
                                     sigma=0.01,
                                     ediff=1e-6,
                                     xc='pbe',
                                     txt='-',
                                     )
    atoms.get_potential_energy()

    # 2. 计算电子对介电函数的贡献与频率的关系
    calc.set(loptics=True, directory='electron_part')
    atoms.get_potential_energy()

    # 3、计算离子对介电函数的贡献与频率的关系
    calc.set(ibrion=8, lepsilon=True, directory='ion_part')
    atoms.get_potential_energy()
    # 4. 数据处理暂时不懂, 是从 2,3计算目录中的vasprun.xml 中抽取数据
    pass

  def test_vacuum_thick(self,
                        pardir='/Users/wangjinlong/my_linux/soft_learn/vasp_learn/learn_example/Testing/vacuum_thick',):
    atoms_out_list = []
    row = ase.calculators.vasp.Vasp().VaspDataBase.db.get('name=Pt_bulk')
    atoms = row.toatoms()
    vacuum_thick_list = np.arange(8, 11)/2
    for vacuum_thick in vacuum_thick_list:
      surface = ase.build.surface(lattice=atoms,
                                  indices=[1, 1, 1],
                                  layers=3,
                                  periodic=True,
                                  vacuum=vacuum_thick)
      atoms_out = self.Vasp.VaspCalculatons.calc_single_point(atoms=surface, directory=os.path.join(pardir, f'v_{vacuum_thick*2}_angs'),
                                                              kpts=(3, 3, 1),
                                                              only_write_inputs=False,
                                                              )

      atoms_out_list.append(atoms_out)

    # deal data
    energy_list = []
    for atoms in atoms_out_list:
      energy = atoms.get_potential_energy()
      energy_list.append(energy)

    df = pd.DataFrame(
        {'vacuum_thick': vacuum_thick_list, 'energy': energy_list})

    from soft_learn_project.matplotlib_learn import matplotlibLearn
    matplotlibLearn.Features().TwoDimension.plot_df(df, x='vacuum_thick',
                                                    y='energy',
                                                    xlabel=r'Vacuum Thick ($\AA$)',
                                                    ylabel='Energy (eV)',
                                                    save=True,
                                                    fname=os.path.join(pardir, 'test_vacuum_thick.pdf'))

    return atoms_out_list

  def test_kmesh(self,
                 pardir='/Users/wangjinlong/my_linux/soft_learn/vasp_learn/learn_example/Testing/kmesh_test/',
                 kmesh_arr=np.arange(7, 14, step=2),
                 **kwargs,
                 ):
    # calc
    fname_csv = os.path.join(pardir, 'test_kmesh.csv')
    if os.path.exists(fname_csv):
      df = pd.read_csv(fname_csv, index_col=0)
    else:
      atoms_out_list = []
      energy_list = []
      atoms = ase.build.bulk(name='W', cubic=True)
      for kmesh in kmesh_arr:
        atoms_out = self.Vasp.VaspCalculatons.calc_single_point(atoms=atoms, directory=os.path.join(pardir, f'{kmesh}'),
                                                                kpts=[kmesh]*3,
                                                                only_write_inputs=False,)
        atoms_out_list.append(atoms_out)
        energy = atoms.get_potential_energy()
        energy_list.append(energy)

      df = pd.DataFrame({'kmesh': kmesh_arr,
                        'energy': energy_list})
      df.to_csv(fname_csv)

    from soft_learn_project.matplotlib_learn import matplotlibLearn
    ax = matplotlibLearn.Features().TwoDimension.plot_df(df=df, x='kmesh',
                                                         y='energy',
                                                         xlabel='Kmesh',
                                                         ylabel='Energy (eV)',
                                                         save=True,
                                                         fname=os.path.join(
                                                             pardir, 'test_kmesh.pdf'),
                                                         **kwargs,
                                                         )
    return df


class FeaturesAtomsAndMoleculars():
  def __init__(self) -> None:
    """https://www.vasp.at/tutorials/latest/molecules/part1/
    vasp tutorial: https://www.vasp.at/tutorials/latest/molecules/part1/  
    这个网址比 vasp wiki 要详细
    """
    pass

  def single_atom_calc(self, atoms,
                       directory='O',
                       ispin=2,  # spin polarized calculation
                       xc='pbe',
                       fname_state_json='state.json',
                       ):
    """In general, only relative energies (band energies with reference to Fermi level, total energies of two related systems etc.) can be interpreted and have physical meaning.
    ISMEAR = 0  ! Gaussian smearing
    SIGMA  = 0.01
    ISPIN =  2  ! spin polarized calculation

    Args:
        atoms (ase.Atoms): _description_
        directory (str, optional): _description_. Defaults to 'O'.
        ispin (int, optional): _description_. Defaults to 2.

    Returns:
        _type_: _description_
    """
    fname_state_json = os.path.join(directory, fname_state_json)
    if not os.path.exists(fname_state_json):
      atoms.cell[:] += np.diag([-0.5, 0, 0.5])  # 破坏对称性
      calc = ase.calculators.vasp.Vasp(directory=directory,
                                       atoms=atoms,
                                       xc=xc,
                                       kpts={'gamma': True},
                                       ismear=0,  # Gaussian smearing
                                       ispin=ispin,
                                       #  小sigma会导致收敛慢, 对能量的影响大, if the energy of two calculations shall be compared, both calculations must use the same value of the SIGMA tag for the Gaussian broadening.
                                       sigma=0.01,  # 减小sigma
                                       lorbit=11,
                                       )
      atoms.get_potential_energy()
      calc.write_json(os.path.basename(fname_state_json))
    else:
      calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
      calc.read_json(fname_state_json)
      calc.read_results()

    return calc

  def relaxation_single_molecular(self, atoms,
                                  calc_method='diis',
                                  directory='O2',
                                  is_recalc=False,
                                  xc='pbe',
                                  fname_state_json='state.json',
                                  ispin=2,  # spin polarized calculation
                                  ):
    calc_cg = ase.calculators.vasp.Vasp(directory=directory,
                                        atoms=atoms,
                                        xc=xc,
                                        kpts={'gamma': True},
                                        ispin=ispin,
                                        ismear=0,  # Gaussian smearing
                                        sigma=0.03,
                                        nsw=50,
                                        ibrion=2,  # use the conjugate gradient algorithm
                                        lorbit=11,
                                        )
    calc_diis = ase.calculators.vasp.Vasp(directory=directory,
                                          atoms=atoms,
                                          xc=xc,
                                          kpts={'gamma': True},
                                          ispin=ispin,
                                          ismear=0,  # Gaussian smearing
                                          sigma=0.03,
                                          # encut =  # largest ENMAX from POTCAR +30%
                                          ibrion=1,  # use DIIS algorithm to converge
                                          nfree=2,  # 2 independent degrees of freedom
                                          nsw=200,
                                          ediffg=-0.02,  # forces smaller 0.02 A/eV
                                          lorbit=11,
                                          )

    if calc_method == 'cg':
      calc = calc_cg
    elif calc_method == 'diis':
      calc = calc_diis
    fname_state_json = os.path.join(directory, fname_state_json)
    if not os.path.exists(fname_state_json) or is_recalc:
      atoms.set_calculator(calc=calc)
      atoms.get_potential_energy()
      calc.write_json(os.path.basename(fname_state_json))
    else:
      calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
      calc.read_json(fname_state_json)
      calc.read_results()

    return calc

  def vibration_molecular(self, atoms,
                          directory='CO',
                          is_recalc=False,
                          xc='pbe',
                          fname_state_json='state.json',
                          ispin=2,  # spin polarized calculation
                          method='vasp',
                          fname_vib_json='vib.json',
                          ):
    """用法:
    mf = Learn.MyFeatures()
    atoms = ase.build.molecule('CO',vacuum=4,pbc=True)
    calc = mf.vibration_molecular(atoms=atoms,directory='CO', method='ase')

    Args:
        atoms (ase.Atoms): _description_
        directory (str, optional): _description_. Defaults to 'O2'.
        is_recalc (bool, optional): _description_. Defaults to False.
        xc (str, optional): _description_. Defaults to 'pbe'.
        fname_state_json (str, optional): _description_. Defaults to 'state.json'.
        ispin (int, optional): _description_. Defaults to 2.

    Returns:
        _type_: _description_
    """
    if method == 'vasp':
      fname_state_json = os.path.join(directory, fname_state_json)
      if not os.path.exists(fname_state_json) or is_recalc:
        calc: ase.calculators.vasp.Vasp = ase.calculators.vasp.Vasp(directory=directory,
                                                                    atoms=atoms,
                                                                    xc=xc,
                                                                    kpts={
                                                                        'gamma': True},
                                                                    ispin=ispin,
                                                                    ismear=0,  # Gaussian smearing
                                                                    # ibrion=5,   # calculate second derivatives, Hessian matrix, and phonon frequencies from finite differences
                                                                    ibrion=8,    # 使用微扰理论计算 perturbation theory
                                                                    nfree=2,  # central differences
                                                                    potim=0.02,  # 0.02 A stepwidth
                                                                    nsw=1,
                                                                    lorbit=11,
                                                                    )

        atoms.get_potential_energy()
        calc.write_json(os.path.basename(fname_state_json))
      else:
        calc: ase.calculators.vasp.Vasp = ase.calculators.vasp.Vasp(
            directory=directory, restart=True)
        calc.read_json(fname_state_json)
        calc.read_results()

      # 分析
      # retrieving a VibrationsData object
      # calc.get_vibrations()  # From the OUTCAR, the energies of all modes can be retrieved
      vib_freq = calc.read_vib_freq()  # meV
      print(f'实频和虚频为 {vib_freq} meV')
      calc: ase.calculators.vasp.Vasp
      return calc
    elif method == 'ase':
      fname_vib_json = os.path.join(directory, fname_vib_json)
      if not os.path.exists(fname_vib_json) or is_recalc:
        atoms.calc = ase.calculators.vasp.Vasp(directory=directory, xc=xc,
                                               kpts={'gamma': True},
                                               ismear=0,
                                               )
        vib = ase.vibrations.Vibrations(atoms,
                                        # indices=[0, 1] # 计算索引原子的振动频率, None 表示所有
                                        name=os.path.join(directory, 'vib')
                                        )
        vib.run()
        vib.write_mode(-1)  # write last mode to trajectory file
        vib_data = vib.get_vibrations()
        vib.summary()
      else:
        vib_data: ase.vibrations.VibrationsData = ase.vibrations.VibrationsData.read(
            fname_state_json)
        print(vib_data.tabulate())
        pass
      return vib_data

  def ab_initio_MD(self, atoms,
                   directory='H2O',
                   is_recalc=False,
                   xc='pbe',
                   fname_state_json='state.json',
                   ispin=0,  # if or not : spin polarized calculation
                   ):
    """for water 对于别的或许需要修改
    缓慢降低温度可以模拟退火 This so-called simulated annealing approach
    ab_initio_MD 的好处: It enables the computation of the pair-correlation function, which is the probability of finding the a particle at a given distance from the center of another particle.
    """
    import py4vasp
    fname_state_json = os.path.join(directory, fname_state_json)
    if not os.path.exists(fname_state_json) or is_recalc:
      calc = ase.calculators.vasp.Vasp(atoms=atoms,
                                       directory=directory,
                                       xc=xc,
                                       ispin=ispin,
                                       prec='Normal',  # standard precision
                                       #  encut=520,
                                       ismear=0,
                                       sigma=0.1,  # ?
                                       # standard molecular dynamics (MD)
                                       ibrion=0,
                                       nsw=500,       # 500 steps
                                       potim=0.5,     # timestep 0.5 fs
                                       isym=0,        # no imposed symmetry for MD
                                       smass=-3,
                                       tebeg=2000,  # temperature at beginning
                                       teend=2000,  # temperature at end
                                       nbands=8,
                                       )
      atoms.calc = calc
      atoms.get_potential_energy()
      calc.write_json(os.path.basename(fname_state_json))

    else:
      calc: ase.calculators.vasp.Vasp = ase.calculators.vasp.Vasp(
          directory=directory, restart=True)
      calc.read_json(fname_state_json)
      calc.read_results()

    # 分析:
    energy = py4vasp.data.Energy.from_path(path=directory)
    energy[:].plot().show()

    pc = py4vasp.data.PairCorrelation.from_path(path=directory)
    fig = pc.plot().to_plotly()
    fig.update_layout(yaxis=dict(range=[0, 20])).show()

    structure = py4vasp.data.Structure.from_path(path=directory)
    structure[:].plot()
    return calc

  def bond_length_of_O2(self, directory='O2', calc=ase.calculators.vasp.Vasp(xc='pbe', kpts=(1, 1, 1), gamma=True)):
    """run a geometry relaxation using a conjugate-gradient algorithm to find the bond length of a dimer

    Args:
        calc (_type_, optional): _description_. Defaults to ase.calculators.vasp.Vasp(xc='pbe', directory='O2').
    """
    atoms = ase.build.molecule('O2', vacuum=5)
    atoms.pbc = True
    calc.set(**{
        'ismear': 0,  # Gaussian smearing
        'ispin': 2,
        'nsw': 5,
        'ibrion': 2,  # use the conjugate-gradient algorithm
    })
    atoms.cacl = calc
    if not os.path.exists(directory):
      atoms.get_potential_energy()
    else:
      calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
      atoms = calc.get_atoms()
    return atoms

  def bond_length_of_CO(self, directory='CO', calc=ase.calculators.vasp.Vasp(xc='pbe', kpts=(1, 1, 1), gamma=True)):
    """If dimers with short bonds are present in the compound (O 2, CO, N 2, F 2, P 2, S 2 , Cl 2), hard pseudopotentials are recommended.
    """

    import py4vasp
    atoms = ase.build.molecule('CO', vacuum=5)
    atoms.pbc = True
    calc.set(**{
        'ismear': 0,  # Gaussian smearing
        'ispin': 2,
        'nsw': 5,
        'ibrion': 2,  # use the conjugate-gradient algorithm
        'potim': 0.2,  # 改变步长
    })
    atoms.cacl = calc
    if not os.path.exists(directory):
      atoms.get_potential_energy()
    else:
      calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
      atoms = calc.get_atoms()

    my_calc = py4vasp.Calculation.from_path("./e05_CO-bond")
    my_calc.structure[:].plot().show()

    return atoms

  def Carbon_monoxide_vibration(self, directory='CO',):
    """compute vibration frequencies of molecules with VASP
    explain how the Hessian matrix and the phonon frequency are connected
    """
    atoms = ase.build.molecule('CO')
    atoms.center(5)
    atoms.pbc = True

    calc = ase.calculators.vasp.Vasp(xc='pbe', kpts=(1, 1, 1), gamma=True)
    calc = calc.set(**{
        'nsw': 1,  # ionic steps > 0
        'ismear': 0,
        'ibrion': 5,  # use the conjugate gradient algorithm
        'nfree': 2,  # central differences
        'potim': 0.02,  # 0.02 A stepwidth
    })

    atoms.calc = calc
    if not os.path.exists(directory):
      atoms.get_potential_energy()
    else:
      cacl = ase.calculators.vasp.Vasp(directory=directory, restart=True)
      atoms = cacl.get_atoms()
    return atoms

  def Partial_density_of_states_of_the_CO_molecule(self, directory='CO/dos',
                                                   calc=ase.calculators.vasp.Vasp(xc='pbe', kpts=(1, 1, 1), gamma=True)):
    """By the end of this tutorial, you will be able to:
    plot the density of states (DOS) using py4vasp
    explain the difference between the partial DOS, local DOS and the total DOS
    """
    import py4vasp
    atoms = ase.build.molecule('CO')
    atoms.center(vacuum=5)
    atoms.pbc = True

    calc.set(**{'ismear': 0,
                'lorbit': 11})
    atoms.calc = calc
    if not os.path.exists(directory):
      atoms.get_potential_energy()
    else:
      calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
      atoms = calc.get_atoms()

    # 画图
    my_calc = py4vasp.Calculation.from_path("./e07_CO-partial-dos")
    my_calc.dos.plot().show()
    # uncomment the line below to plot the partial DOS
    # my_calc.dos.plot("p").show()
    return atoms

  def Bond_length_in_H2O(self, directory, calc=ase.calculators.vasp.Vasp(xc='pbe', kpts=(1, 1, 1), gamma=True)):
    """By the end of this tutorial, you will be able to:

    explain the residual minimization method with direct inversion in the iterative subspace (RMM-DIIS) on the level of pseudocode
    judge whether to use the RMM-DIIS or conjugate-gradient (CG) algorithm
    write a POSCAR file from scratch
    use the scaling parameter in the POSCAR file
    perform a geometry relaxation with two degrees of freedom
    set the convergence criterion for the ionic relaxiation
    """
    atoms = ase.build.molecule('H2O', vacuum=5)
    atoms.pbc = True

    incar_dict = {'ismear': 0,
                  'sigma': 0.1,
                  'encut': 520,
                  'ibrion': 1,  # use DIIS algorithm to converge
                  'nfree': 2,  # 2 independent degrees of freedom
                  'nsw': 10,
                  'ediffg': -0.02,  # forces smaller 0.02 A/eV
                  }
    calc.set(directory=directory)
    calc.set(**incar_dict)
    atoms.calc = calc

    if not os.path.exists(directory):
      atoms.get_potential_energy()
    else:
      calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
      atoms = calc.get_atoms

    # 查看结构
    # Alternatively, you can use py4vasp and extract the information directly from the structure plot. First, plot a 2x2x2 supercell. Then, right click the first atom and right click the second atom twice to get the distance. For the angle, right click atom 1, then atom 2 and right click atom 3 twice. Check that the result agrees with the discussion above!
    import py4vasp
    my_calc = py4vasp.Calculation.from_path(path_name=directory)
    my_calc.structure.plot(2).show()

    return atoms

  def Energy_cutoff_for_H2O(self, directory, calc=ase.calculators.vasp.Vasp(
      xc='pbe', kpts=(1, 1, 1), gamma=True),
  ):
    """By the end of this tutorial, you will be able to:

    set the energy cutoff for the plane wave basis of the pseudo-orbitals
    set the precision of a calculation using PREC
    """

    atoms = ase.build.molecule('H2O', vacuum=5)
    atoms.pbc = True

    incar_dict = {'ismear': 0,
                  'sigma': 0.1,
                  'encut': 400, }
    calc.set(directory)
    calc.set(**incar_dict)

    encut_list = list(range(400, 820, 50))
    energy_list = []
    for encut in encut_list:
      calc.set(encut=encut)
      atoms.calc = calc
      energy_list.apend(atoms.get_potential_energy())

    data = {'encut': encut_list, 'energy': energy_list}
    import pandas as pd
    df = pd.DataFrame(data=data)

    return df

  def H2O_vibration_frequency(self, directory,
                              calc=ase.calculators.vasp.Vasp(
                                  xc='pbe', kpts=(1, 1, 1), gamma=True),
                              ):

    incar_set_ibrion8 = {'prec': 'Accurate',  # recommended for computing forces,
                         'encut': 520,
                         'ismear': 0,
                         'sigma': 0.1,
                         'ibrion': 6,  # finite differences with symmetry
                         'nfree': 2,  # central differences (default)
                         'potim': 0.015,  # step size (default)
                         'ediff': 1e-8,
                         'nsw': 1,
                         }
    incar_set_ibrion6 = {**incar_set_ibrion8, 'nbands': 6}

    atoms = ase.build.molecule('H2O', vacuum=5)
    atoms.pbc = True

    if not os.path.exists(directory):
      calc.set(directory=directory+'/ibrion8')
      calc.set(**incar_set_ibrion8)
      atoms.calc = calc
      atoms.get_potential_energy()

      calc.reset()
      calc.set(directory=directory+'/ibrion8')
      calc.set(**incar_set_ibrion8)
      atoms.calc = calc
      atoms.get_potential_energy()
    else:
      calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
      atoms = calc.get_atoms()
    return atoms

  def H2O_pair_correlation_function(self, directory,
                                    calc=ase.calculators.vasp.Vasp(
                                        xc='pbe', kpts=(1, 1, 1), gamma=True),
                                    ):

    import py4vasp
    incar_set = {'encut': 520,
                 'ismear': 0,
                 'sigma': 0.1,
                 'isym': 0,  # no imposed symmetry for MD
                 # ! standard molecular dynamics (MD)
                 'ibrion': 0,
                 'nsw': 500,
                 'potim': 0.5,  # timestep 0.5 fs
                 'smass': -3,
                 'tebeg': 2000,  # temperature at beginning
                 'teend': 2000,  # temperature at end
                 'nbands': 8,
                 }
    atoms = ase.build.molecule('H2O', vacuum=5)
    atoms.pbc = True
    calc.set(directory=directory)
    calc.set(**incar_set)
    atoms.calc = calc
    if not os.path.exists(directory):
      atoms.get_potential_energy()
    else:
      calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
      atoms = calc.get_atoms()

    # Plot the total energy of the structure at each time step using py4vasp:
    my_calc = py4vasp.Calculation.from_path("./e11_H2O-MD")
    my_calc.energy[:].plot().show()
    my_calc.structure[:].plot()
    # 想办法画 pair_correlation.pdf
    # 以后再说
    return atoms


class FeaturesBulkSystem():
  def __init__(self) -> None:
    pass

  def band_structure_plot(self, method, *args, **kwargs):
    def band_structure_plot_ase(fname_bs_json, fname_fig=None, emin=None, emax=None, ):
      band_structure = ase.spectrum.band_structure.BandStructure
      band_structure = band_structure.read(fname_bs_json)
      # 4. 绘图
      # 以费米能级为参考后的能带 band_structure.reference 是费米能级
      band_structure = band_structure.subtract_reference()  # 对于vasp是否需要减去？

      band_structure.plot(filename=fname_fig,
                          show=True, emin=emin,
                          emax=emax)
      print("进行画图: band_structure.plot(filename='band_structure.pdf', show=True, emin=-3, emax=3, marker='o')")
    from soft_learn_project.py4vasp_learn import py4vaspLearn

    if method == 'ase':
      return band_structure_plot_ase
    elif method == 'py4vasp':
      return py4vaspLearn.Features().band_structure_plot

  def pdos_molecular(self,
                     atoms,
                     directory='CO',
                     is_recalc=False,
                     xc='pbe',
                     ispin=2,  # spin polarized calculation
                     pdos_slection='C(p),O(px)',
                     fname_state_json='state.json',
                     fname_fig='pdos.pdf',
                     ):
    """绘图: 可以使用 py4vasp 或者 p4vasp, pdos 的数据在 PROCAR 中

    Args:
        atoms (ase.Atoms): _description_
        directory (str, optional): _description_. Defaults to 'O2'.
        is_recalc (bool, optional): _description_. Defaults to False.
        xc (str, optional): _description_. Defaults to 'pbe'.
        fname_state_json (str, optional): _description_. Defaults to 'state.json'.
        ispin (int, optional): _description_. Defaults to 2.

    Returns:
        _type_: _description_
    """
    import py4vasp
    fname_state_json = os.path.join(directory, fname_state_json)
    if not os.path.exists(fname_state_json) or is_recalc:
      calc = ase.calculators.vasp.Vasp(directory=directory,
                                       atoms=atoms,
                                       xc=xc,
                                       kpts={'gamma': True},
                                       ispin=ispin,
                                       ismear=0,  # Gaussian smearing
                                       lorbit=11,  # DOSCAR and lm decomposed PROCAR file
                                       )

      atoms.get_potential_energy()
      calc.write_json(os.path.basename(fname_state_json))
    else:
      calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
      calc.read_json(fname_state_json)
      calc.read_results()

    # 绘图: 可以使用 py4vasp
    dos = py4vasp.data.Dos.from_path(path=directory)
    fig = dos.plot(selection=pdos_slection).to_plotly()
    fig.write_image(os.path.join(directory, fname_fig))
    fig.show()
    return calc

  def relaxation_lattice_constant_ase(self,):
    from soft_learn_project.ase_learn import aseLearn
    # aseLearn.Features().lattice_constant()
    pass

  def relaxation_lattice_constant_vasp(self,
                                       directory='Si',

                                       fname_state_json='state.json',
                                       is_recalc=False,):
    """用vasp内部的方法获得晶格常数

    Args:
        directory (str, optional): _description_. Defaults to 'Si'.
        atoms (ase.Atoms, optional): _description_. Defaults to ase.build.bulk('Si').
        calc (_type_, optional): _description_. Defaults to ase.calculators.vasp.Vasp(kpts=(11, 11, 11), xc='pbe',).
        fname_state_json (str, optional): _description_. Defaults to 'state.json'.
        is_recalc (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    atoms = ase.build.bulk('Si')
    calc = ase.calculators.vasp.Vasp(kpts=(11, 11, 11), xc='pbe',)
    fname_state_json = os.path.join(directory, fname_state_json)
    if not os.path.exists(fname_state_json) or is_recalc:
      calc.set(directory=directory)
      calc.set(**self.Vasp.Cal .Features().incar_relaxation_crsytal_bulk_lc)

      atoms.calc = calc
      atoms.get_potential_energy()
      calc.write_json(os.path.basename(fname_state_json))
    else:
      calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
      atoms = calc.get_atoms()
    return atoms

  def relaxation_lattice_constant(self,
                                  method='ase',
                                  ):
    if method == 'ase':
      from soft_learn_project.ase_learn import aseLearn
      aseLearn.AseFeatures().calc_lattice_constant
    elif method == 'vasp':
      return self.relaxation_lattice_constant_vasp

  def self_consistent_ground_state_calc(self, directory='Si',
                                        fname_state_json='sc_state.json',
                                        is_recalc=False,
                                        ):
    atoms = ase.build.bulk('Si')
    calc = ase.calculators.vasp.Vasp(xc='pbe', kpts=(11, 11, 11))
    fname_state_json = os.path.join(directory, fname_state_json)
    if not os.path.exists(fname_state_json) or is_recalc:
      # 单点计算, 为了获得自洽CHGCAR
      calc.set(directory=directory,
               ismear=0,
               lorbit=11,
               )
      atoms.calc = calc
      atoms.get_potential_energy()
      calc.write_json(os.path.basename(fname_state_json))
    else:
      calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
      calc.read_json(fname_state_json)
      calc.read_results()
      atoms = calc.get_atoms()
    return atoms

  def dos_bulk(self,
               directory='bulk_Si_fcc',
               selection=None,
               is_recalc=False):
    """基于计算 Si fcc 
    """

    atoms = ase.build.bulk('Si', 'fcc', a=3.9)
    calc = ase.calculators.vasp.Vasp(kpts=(11, 11, 11), xc='pbe')
    if not os.path.exists(directory) or is_recalc:
      # 1. 基态计算
      atoms = self.self_consistent_ground_state_calc(directory=directory,
                                                     atoms=atoms,
                                                     calc=calc)
      # 2. dos calcu
      calc.set(directory=directory,
               ismear=-5,  # tetrahedron method  不能用于金属的几何优化
               lorbit=11,
               icharg=11,  # ! read CHGCAR file
               nedos=401,    # no of points for DOS # 指定态密度图的分辨率也就是多少个 点
               emin=-5,  # 设置能量范围, 相对费米能级之前的
               emax=12,
               )
      atoms.calc = calc
      atoms.get_potential_energy()
    else:
      calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
      atoms = calc.get_atoms()

    # 处理数据

    self.dos_plot(directory=directory,
                  selection=selection)
    return atoms

  def band_structure_bulk_sys(self,
                              directory='bulk_Si_fcc',
                              fname_bs_json='band_structure.json',
                              is_recalc=False):
    """kpts={'path': 'LGXUKG',     # The BS path
                     'npoints': 60},    # Number of points along the path

    Args:
        directory (str, optional): _description_. Defaults to 'bulk_Si_fcc'.
        atoms (ase.Atoms, optional): _description_. Defaults to ase.build.bulk( 'Si', 'fcc', a=3.9).
        calc (_type_, optional): _description_. Defaults to ase.calculators.vasp.Vasp( kpts=(5, 5, 5), xc='pbe').
        fname_bs_json (str, optional): _description_. Defaults to 'band_structure.json'.
        is_recalc (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """

    atoms = ase.build.bulk('Si', 'fcc', a=3.9)
    calc = ase.calculators.vasp.Vasp(kpts=(15, 15, 15), xc='pbe'),
    kpts = {'path': 'LGXUKG',     # The BS path
            'npoints': 120},    # Number of points along the path
    fname_bs_json = os.path.join(directory, fname_bs_json)

    if not os.path.exists(fname_bs_json) or is_recalc:
      # 1. 基态计算
      atoms = self.self_consistent_ground_state_calc(directory=directory,
                                                     atoms=atoms,
                                                     calc=calc)

      # 2. 非自洽计算
      calc.set(directory=directory,
               icharg=11,  # read CHGCAR file and keep density fixed
               kpts=kpts,)
      atoms.calc = calc
      atoms.get_potential_energy()
      # 3. 保存能带数据
      band_structure = calc.band_structure()  # ASE Band structure object
      band_structure.write(fname_bs_json)
    else:
      band_structure = ase.spectrum.band_structure.BandStructure
      band_structure = band_structure.read(fname_bs_json)
      calc = ase.calculators.vasp.Vasp(directory=directory,
                                       restart=True)
      atoms = calc.get_atoms()

    # 画图
    self.band_structure_plot(method='ase')(fname_bs_json=fname_bs_json)
    # self.band_structure_plot(method='py4vasp')(directory=directory)
    return atoms


class FeaturesMolecularDynamics():
  def __init__(self) -> None:
    """The structure of a liquid can be studied using the radial distribution function, also known as pair-correlation function.
    回想一下，在晶体中，我们观察到长程有序，这导致了对相关函数的明显峰值。在液体状态下，粒子是紧密结合的，不像在气体状态下，但不像在固体状态下那样僵硬。当系统熔化时，对相关函数的特征特征发生显著变化。

    10000 MD steps is a typical number of steps necessary to deduce anything reasonable from an MD simulation. Therefore, this example shows that ab-initio MD simulations are computationally expensive and time-consuming. This renders ab-initio MD infeasible for many systems.

    下表概述了VASP中系综和恒温器的可能组合:
    https://www.vasp.at/wiki/index.php/Category:Ensembles
    """
    pass

  def pars_set(self):
    self.pars_initial_dict = {'xc': 'pbe', 'kpts': (1, 1, 1)}
    self.pars_ab_initio_dict = {'prec': 'Normal',
                                'ivdw': 10,
                                'ismear': -1,  # ! Fermi smearing
                                'sigma': 0.0258,  # ! smearing in eV
                                'encut': 300,
                                'ediff': 1e-6,
                                'lwave': False,
                                'lcharg': False,
                                'lreal': False,
                                }
    self.pars_md_dict = {'isym': 0,
                         'ibrion': 0,  # ! MD (treat ionic degrees of freedom)
                         'nsw': 10,  # ! no of ionic steps
                         'potim': 2.0,  # ! MD time step in fs
                         'mdalgo': 3,  # ! Langevin thermostat
                         'langevin_gamma': [1],  # ! friction  # 以后研究下这两个参数的意义
                         'langevin_gamma_l': 10,  # ! lattice friction
                         'pmass': 10,  # ! lattice mass
                         'tebeg': 400,  # ! temperature
                         'isif': 3,  # ! update positions, cell shape and volume
                         }
    self.pars_machine_learning_dict = {
        # 'lwave': False,  # 不生成 wavecar
        #                                  'lcharg': False,  # 不生成 chgcar chg
        'ml_lmlff': 'T',  # 开启机器学习力场方法的使用。
        #  'ml_istart': 0,  # 从ab-initio MD中选择训练新力场的模式。
        'ml_mode': 'train',  # 或者用这个
        'ml_wtsif': 2,  # 该标签在机器学习力场方法中为训练数据中的应力缩放设置权值。
        # 确保此示例的可再现性。
        'random_seed': [688344966, 0, 0],
    }
    # 使用机器学习的力场
    self.pars_ML_use_dict = {
        'ml_lmlff': 'T',
        # 'ml_istart': 2,
        # ml_mode= train: 实时训练力场(ML_AB 不必匹配POSCAR): 1. ML_AB (ML_ABN的copy) 不存在则训练新的力场, 2. ML_AB 存在, 读取 ML_AB 的数据产生力场, 并更新力场
        # ml_mode= select:重新选择本地参考配置(ML_AB), 训练力场(我猜测对于相同的ML_AB, 对于两次训练可能会得到有些差异的力场ML_FFN)
        # ML_MODE = refit:为“快速”评估改装力场. 如果训练的力场在适用性和残余误差方面符合您的期望时, 在力场应应用于仅预测的MD运行之前需要最后一步:为快速预测模式进行改装。再次将最终数据集复制到ML_AB,ML_MODE = refit, 运行VASP将创建一个新的ML_FFN，最终可以用于生产。
        # ml_mode=run: 只执行力场预测
        'ml_mode': 'run',  # 只执行力场预测 cp ML_FFN ML_FF 到MD运算目录 然后 ml_mode=run 开始MD。
        'random_seed':         [688344966,               0,            0],
    }
    pass

  def melting_silicon(self, directory='Si64',
                      is_recalc=False,
                      is_plot=False,
                      ):
    import ase.io.vasp
    import py4vasp
    import ase.calculators.vasp
    calc = ase.calculators.vasp.Vasp(xc='pbe', kpts=(1, 1, 1)),

    if not os.path.exists(directory) or is_recalc:
      os.makedirs(directory, exist_ok=True)
      import pymatgen.core
      # my_struc = Structure.from_file("./e01_solid-cd-Si/Si_mp-149_conventional_standard.cif")
      s = """
      1.0
      10.937456 0.000000 0.000000
      0.000000 10.937456 0.000000
      0.000000 0.000000 10.937456
      Si
      64
      direct
      0.125000 0.375000 0.125000 Si
      0.125000 0.375000 0.625000 Si
      0.125000 0.875000 0.125000 Si
      0.125000 0.875000 0.625000 Si
      0.625000 0.375000 0.125000 Si
      0.625000 0.375000 0.625000 Si
      0.625000 0.875000 0.125000 Si
      0.625000 0.875000 0.625000 Si
      0.000000 0.000000 0.250000 Si
      0.000000 0.000000 0.750000 Si
      1.000000 0.500000 0.250000 Si
      1.000000 0.500000 0.750000 Si
      0.500000 0.000000 0.250000 Si
      0.500000 0.000000 0.750000 Si
      0.500000 0.500000 0.250000 Si
      0.500000 0.500000 0.750000 Si
      0.125000 0.125000 0.375000 Si
      0.125000 0.125000 0.875000 Si
      0.125000 0.625000 0.375000 Si
      0.125000 0.625000 0.875000 Si
      0.625000 0.125000 0.375000 Si
      0.625000 0.125000 0.875000 Si
      0.625000 0.625000 0.375000 Si
      0.625000 0.625000 0.875000 Si
      1.000000 0.250000 0.000000 Si
      1.000000 0.250000 0.500000 Si
      1.000000 0.750000 0.000000 Si
      1.000000 0.750000 0.500000 Si
      0.500000 0.250000 0.000000 Si
      0.500000 0.250000 0.500000 Si
      0.500000 0.750000 1.000000 Si
      0.500000 0.750000 0.500000 Si
      0.375000 0.375000 0.375000 Si
      0.375000 0.375000 0.875000 Si
      0.375000 0.875000 0.375000 Si
      0.375000 0.875000 0.875000 Si
      0.875000 0.375000 0.375000 Si
      0.875000 0.375000 0.875000 Si
      0.875000 0.875000 0.375000 Si
      0.875000 0.875000 0.875000 Si
      0.250000 0.000000 0.000000 Si
      0.250000 0.000000 0.500000 Si
      0.250000 0.500000 0.000000 Si
      0.250000 0.500000 0.500000 Si
      0.750000 0.000000 0.000000 Si
      0.750000 0.000000 0.500000 Si
      0.750000 0.500000 1.000000 Si
      0.750000 0.500000 0.500000 Si
      0.375000 0.125000 0.125000 Si
      0.375000 0.125000 0.625000 Si
      0.375000 0.625000 0.125000 Si
      0.375000 0.625000 0.625000 Si
      0.875000 0.125000 0.125000 Si
      0.875000 0.125000 0.625000 Si
      0.875000 0.625000 0.125000 Si
      0.875000 0.625000 0.625000 Si
      0.250000 0.250000 0.250000 Si
      0.250000 0.250000 0.750000 Si
      0.250000 0.750000 0.250000 Si
      0.250000 0.750000 0.750000 Si
      0.750000 0.250000 0.250000 Si
      0.750000 0.250000 0.750000 Si
      0.750000 0.750000 0.250000 Si
      0.750000 0.750000 0.750000 Si
      """
      my_struc = pymatgen.core.Structure.from_str(input_string=s, fmt='poscar')
      # my_struc = my_struc.to_primitive()
      mystruc = pymatgen.core.Structure.from_file(
          '/Users/wangjinlong/my_linux/soft_learn/vasp_learn/tmp/Si64/POSCAR')
      # atoms = mystruc.to_primitive().to_ase_atoms()
      # make a 2x2x2 supercell
      my_struc.make_supercell(1)  # 2
      # write supercell to POSCAR format with specified filename
      my_struc.to(fmt="poscar", filename=os.path.join(directory, "POSCAR"))

      # -------
      import ase.build
      atoms = ase.build.bulk('Si', cubic=True)
      atoms = atoms.repeat(2)
      pars_ab_initio_dict = {'ismear': 0,       # Gaussian smearing
                             'sigma': 0.1,     # smearing in eV
                             'lreal': 'Auto',    # projection operators in real space
                             'algo': 'VeryFast',  # RMM-DIIS for electronic relaxation
                             'prec': 'Low',     # precision
                             'isym': 0,      # no symmetry imposed
                             }
      pars_md_dict = {'ibrion': 0,     # MD (treat ionic degrees of freedom)
                      'nsw': 30,     # no of ionic steps
                      'potim': 3.0,     # MD time step in fs
                      'mdalgo': 2,     # Nosé-Hoover thermostat
                      'smass': 1.0,     # Nosé mass
                      'tebeg': 2000,     # temperature at beginning
                      'teend': 2000,     # temperature at end
                      'isif': 2,     # update positions; cell shape and volume fixed
                      }
      calc.set(directory=directory, **pars_ab_initio_dict, **pars_md_dict)
      atoms.calc = calc
      atoms.get_potential_energy()
    else:
      calc = ase.calculators.vasp.Vasp(restart=True, directory=directory)
      atoms = calc.get_atoms()

    # plot energies
    if is_plot:
      energy = py4vasp.data.Energy.from_path(path=directory)
      # print(energy[1:5].read()) # 查看
      energy[:].plot("TOTEN, ETOTAL").to_plotly().show()
      energy[:].plot("EKIN, temperature").to_plotly().show()
      energy[:].plot("ES,EP").to_plotly().show()
    return atoms

  def melting_silicon_continuation(self, directory='Si64/continue'):
    if not os.path.exists(directory):
      atoms = self.melting_silicon()
      calc = ase.calculators.vasp.Vasp(restart=True, directory='Si64')
      calc.reset()
      calc.set(directory=directory)
      atoms.calc = calc
      atoms.get_potential_energy()

      calc.reset()
      calc.set(directory=directory+'2',
               nsw=5,
               apaco=5.4,  # 设置相关函数的评估中的最大距离
               )
      atoms.get_potential_energy()
    else:
      calc = ase.calculators.vasp.Vasp(restart=True, directory=directory)
      atoms = calc.get_atoms()

    # 画图, 对关联函数
    from soft_learn_project.py4vasp_learn import py4vaspLearn
    pcf1 = py4vaspLearn.Py4vaspData().pair_correlation('Si64').plot().label('Si64')
    pcf2 = py4vaspLearn.Py4vaspData().pair_correlation(
        directory).plot().label(directory)
    pcf3 = py4vaspLearn.Py4vaspData().pair_correlation(
        directory+'2').plot().label(directory+'2')
    pcf_fig = pcf1+pcf2+pcf3
    pcf_fig.to_plotly().show()
    return atoms

  def get_iconst(self, directory):
    """iconst 设置
    """
    iconst = """
    LR 1 7
    LR 2 7
    LR 3 7
    LA 2 3 7
    LA 1 3 7
    LA 1 2 7
    LV 7
    """
    fname_iconst = os.path.join(directory, 'ICONST')
    with open(fname_iconst, 'w') as f:
      f.write(iconst)

  def monitoring_molecular_geometry(self,
                                    directory,
                                    calc,
                                    is_recalc=False
                                    ):
    """Monitor the geometric coordinates during an ab-initio MD simulation of 16 silicon atoms in an NpT ensemble using the Langevin thermostat.
    """

    atoms = ase.build.bulk('Si', a=5.47).repeat(2),  # 为了观察体积缩小
    if not os.path.exists(directory) or is_recalc:
      os.makedirs(directory, exist_ok=True)
      self.get_iconst(directory=directory)  # 监视几何坐标
      calc.set(directory=directory)
      calc.set(**self.pars_initial_dict, **
               self.pars_ab_initio_dict, **self.pars_md_dict)
      atoms.calc = calc
      atoms.get_potential_energy()

    os.system(
        f'cat {directory}/REPORT | grep "mc> LV" > {directory}/monitored_cell_volume.dat')
    import numpy as np
    from py4vasp import plot
    volume = np.loadtxt(
        f"{directory}/monitored_cell_volume.dat", usecols=2)
    # plot the volume
    plot(np.arange(len(volume))+1, volume, "relaxation",
         xlabel="Number of MD steps", ylabel="Volume (Å³)").show()
    pass

  def machine_learning_force_fields(self,
                                    directory='machine_learning_force_fields',
                                    added_pars={},
                                    nsw=10000,
                                    is_recalc=False):
    """本例子网址: https://www.vasp.at/tutorials/latest/md/part2/  
    https://www.vasp.at/wiki/index.php/Machine_learning_force_field_calculations:_Basics
    https://www.vasp.at/wiki/index.php/Machine_learning_force_field:_Theory
    训练一个机器学习力场
    要训练多元素力场更新之前的力场, 只需要 cp ML_ABN MLAB 即可在当前目录下继续训练, 继续训练之前要先去掉 WAVECAR 和CHG* 
    vasp in 文件在MD目录中
    ml_mode = train 为训练, 之后 cp ML_ABN MLAB, 之后ml_mode=refit 再运行一次产生 ML_FFN, cp ML_FFN ML_FF 就是用于生产的力场, 当然要确定力场足够好
    """

    import py4vasp
    import os
    atoms = ase.build.bulk('Si',).repeat(2)
    if not os.path.exists(directory) or is_recalc:
      # Train a force field on-the-fly during an ab-initio MD simulation of 16 silicon atoms in an NpT ensemble using the Langevin thermostat.
      # iconst 设置
      os.makedirs(directory, exist_ok=True)
      self.get_iconst(directory=directory)
      calc = ase.calculators.vasp.Vasp(directory=directory)
      calc.set(**self.pars_initial_dict)
      calc.set(**self.pars_ab_initio_dict, **self.pars_md_dict,
               **self.pars_machine_learning_dict)
      calc.set(nsw=nsw)
      calc.set(**added_pars)
      atoms.calc = calc
      calc.write_input(atoms=atoms)
      # atoms.get_potential_energy()
      calc._run(command='mpirun -np 4 vasp_std')

      # 用来进行继续训练和新的训练
      shutil.copy(os.path.join(directory, 'ML_ABN'),
                  os.path.join(directory, 'ML_AB'))
      # 用于应用力场
      shutil.copy(os.path.join(directory, 'ML_FFN'),
                  os.path.join(directory, 'ML_FF'))
    else:
      pass

    # 使用下面的代码绘制力的贝叶斯误差和样本内误差!
    def old():

      with open(os.path.join(directory, 'ML_LOGFILE')) as f:
        content = f.read()
      colname = re.search('# BEEF.*?nstep.*?bee_energy.*?\n',
                          content).group().split()[2:]
      lines = re.findall('^BEEF.*?\n', content, re.M)
      arr = np.array([line.split()[1:] for line in lines], dtype=float)
      df = pd.DataFrame(data=arr, columns=colname)

      py4vasp.plot(df['nstep'], df['bee_max_force'],
                   xlabel="Time step",
                   ylabel="Bayesian error",
                   title="Bayesian error estimate of forces (max) (eV Angst^-1)"
                   ).show()

      os.system(f'cat {directory}/ML_LOGFILE | grep ERR > {directory}/ERR.dat')
      t2, inerr = np.loadtxt(f"{directory}/ERR.dat",
                             usecols=[1, 2], unpack=True)
      py4vasp.plot(t2, inerr,
                   xlabel="Time step",
                   ylabel="RMSE",
                   title="Root mean squared error of forces (eV Angst^-1)"
                   ).show()

    def new():
      # 力的贝叶斯误差也就是样本外误差
      import os
      import numpy as np
      from py4vasp import plot
      directory = './MD/e04_MLFF'
      os.system(
          f'cat {directory}/ML_LOGFILE | grep BEEF > {directory}/BEEF.dat')
      t1, beef = np.loadtxt("./MD/e04_MLFF/BEEF.dat",
                            usecols=[1, 3], unpack=True)
      plot(t1, beef,
           xlabel="Time step",
           ylabel="Bayesian error",
           title="Bayesian error estimate of forces (max) (eV Angst^-1)"
           ).show()

      # 力的样本内误差
      os.system(f'cat {directory}/ML_LOGFILE | grep ERR > {directory}/ERR.dat')
      t2, inerr = np.loadtxt(f"{directory}/ERR.dat",
                             usecols=[1, 2], unpack=True)
      plot(t2, inerr,
           xlabel="Time step",
           ylabel="RMSE",
           title="Root mean squared error of forces (eV Angst^-1)"
           ).show()
    new()
    return None

  def testing_force_fields_with_ionic_relaxation(self,
                                                 directory='testing_force_fields_with_ionic_relaxation',):
    """测试机器学习生成的力场
    By the end of this tutorial, you will be able to:
    1. test a force field by comparison of the relaxed lattice parameters and reference data
    2. use the conjugate-gradient algorithm with force fields

    测试力场的策略:
    In order to implement a test of the force fields computed in Example 4, you can follow one, or both, of these strategies:

    1. Set up an independent test set of random configurations. Then, check the average errors comparing forces, stresses and energy differences of two structures based on DFT and predicted by machine-learned force fields.
    2. If you have both, ab-initio reference data and a calculation using force fields, check the agreement of some physical properties. For instance, you might check the relaxed lattice parameters, phonons, relative energies of different phases, the elastic constant, the formation of defects etc.

    如何使用机器学习力场:
    To let VASP read the force field as an input file, you can copy ML_FFN to ML_FF. Then, to restart learning or use the force field to run an MD simulation ML_ISTART must be set appropriately. We will use this force field in Example 5 to 8.
    """
    # atoms = self.machine_learning_force_fields()
    atoms = ase.build.bulk('Si', a=5.469).repeat(2)
    fname_ml_ff = os.path.abspath(os.path.join(directory, 'ML_FF'))
    if not os.path.exists(fname_ml_ff):
      os.system(
          f'ln -s /Users/wangjinlong/my_linux/soft_learn/vasp_learn/tmp/machine_learning_force_fields/ML_FFN {fname_ml_ff}')
    calc = ase.calculators.vasp.Vasp(directory=directory,)
    # 获得晶格常数
    calc.set(ibrion=2, nsw=20, isif=3)
    # 使用机器学习力场
    calc.set(**self.pars_ML_use_dict)

    atoms.calc = calc
    # atoms.get_potential_energy()
    calc.write_input(atoms=atoms)
    calc._run(command='vasp_std')
    atoms = ase.io.vasp.read_vasp(f'{directory}/CONTCAR')

    #
    def func():
      import numpy as np
      from py4vasp import plot
      import os
      os.system('bash volume_energy_MLFF.sh > volume_energy_MLFF.dat')
      directory = 'MD/e05_ionic-relaxation-FF/'
      volume_dft, energy_dft = np.loadtxt(
          f"{directory}/volume_energy_DFT.dat", unpack=True)
      volume_mlff, energy_mlff = np.loadtxt(
          f"{directory}/volume_energy_MLFF.dat", unpack=True)

      plot(
          (volume_dft, energy_dft, "DFT"),
          (volume_mlff, energy_mlff, "MLFF"),
          xlabel="Volume (Å³)",
          ylabel="Total energy (eV)",
      ).show()

    func()
    return atoms

  def get_lc_vol(self, directory):
    # 晶格常数和体积的平均
    with open(os.path.join(directory, 'REPORT')) as f:
      content = f.read()
    vectors_list = re.findall('mc> LR(.*?)\n', content, re.M)
    vectors = np.array([float(line.strip()) for line in vectors_list])
    vecorts_mean = vectors.reshape(-1, 3)[5000:].mean()  # axis=0
    vol = re.findall('mc> LV(.*?)\n', content, re.M)
    vol = np.array([float(line.strip()) for line in vol])
    vol_mean = vol[5000:].mean()
    print(f'晶格矢量平均:{vecorts_mean}, 体积平均: {vol_mean}')
    data = {'vecorts_mean': vecorts_mean, 'vol_mean': vol_mean}
    return data

  def lattice_constant_and_cell_volume_as_ensemble_averages(self,
                                                            atoms,
                                                            directory='lattice_constant_and_cell_volume_as_ensemble_averages',
                                                            is_recalc=False,
                                                            ):
    """By the end of this tutorial, you will be able to:
    1. compute the lattice constant and cell volume as an ensemble average
    2. run a molecular-dynamics simulation using a pretrained force field

    # 确定400K 时 16 Si原子的晶格常数和体积
    Determine the lattice constant and cell volume of 16 silicon atoms in an NpT ensemble using the Langevin thermostat as ensemble average at 400 K using a machine-learned force field.
    """
    if not os.path.exists(directory) or is_recalc:
      fname_ml_ff = os.path.abspath(os.path.join(directory, 'ML_FF'))
      if not os.path.exists(fname_ml_ff):
        os.system(
            f'ln -s /Users/wangjinlong/my_linux/soft_learn/vasp_learn/tmp/machine_learning_force_fields/ML_FFN {fname_ml_ff}')
      self.get_iconst(directory=directory)

      calc = ase.calculators.vasp.Vasp(kpts=(1, 1, 1), xc='pbe')
      calc.set(directory=directory)
      calc.set(**self.pars_md_dict, **self.pars_ML_use_dict, isym=0)
      calc.set(nsw=10000)

      atoms.calc = calc
      atoms.get_potential_energy()
    else:
      pass

    # 晶格常数和体积的平均
    data = self.get_lc_vol(directory=directory)
    return data

  def transferability_of_machine_learned_force_fields_and_the_thermal_expansion_coefficient(self,
                                                                                            atoms,
                                                                                            directory='transferability_of_machine_learned_force_fields',
                                                                                            tebeg=200,
                                                                                            is_recalc=False):
    """
    check if a force field is applicable to a specific system or parameter set
    extract monitored geometric coordinates from the REPORT file without guidance
    compute the thermal expansion coefficient

    Determine the lattice constant and cell volume at 200 K and 300 K of silicon using a simulation of 16 Si atoms using a machine-learned force field, that is trained at 400 K, and check the transferability. Then, plot the volume vs temperature curve at T = 200 K, 300 K and 400 K to extract the thermal expansion coefficient.
    """

    import ase.io.vasp

    directory = os.path.join(directory, str(tebeg))

    if not os.path.exists(directory) or is_recalc:
      os.makedirs(directory, exist_ok=True)

      fname_ml_ff = os.path.abspath(os.path.join(directory, 'ML_FF'))
      if not os.path.exists(fname_ml_ff):
        os.system(
            f'ln -s /Users/wangjinlong/my_linux/soft_learn/vasp_learn/tmp/machine_learning_force_fields/ML_FFN {fname_ml_ff}')
      self.get_iconst(directory=directory)

      calc = ase.calculators.vasp.Vasp(**self.pars_initial_dict)
      calc.set(directory=directory)
      calc.set(**self.pars_md_dict, **self.pars_ML_use_dict)
      calc.set(nsw=10000, tebeg=tebeg)
      atoms.calc = calc
      atoms.get_potential_energy()

    data = self.get_lc_vol(directory=directory)
    return data

  def thermal_expansion_calc(self):
    atoms = ase.build.bulk('Si').repeat(2)
    temperature = [200, 300, 400]
    volume = []
    lattice_vector = []
    for tebeg in temperature:
      data = self.transferability_of_machine_learned_force_fields_and_the_thermal_expansion_coefficient(atoms=atoms,
                                                                                                        tebeg=tebeg,
                                                                                                        directory='transferability_of_machine_learned_force_fields',
                                                                                                        )
      volume.append(data['vol_mean'])
      lattice_vector.append(data['vecorts_mean'].mean())

    # Linear expansion coefficient of Si: 1.1561686750765887e-06
    alpha_V = 1./volume[2] * (volume[2]-volume[0]) / \
        (temperature[2]-temperature[0])
    print("Thermal expansion coefficient of Si:", alpha_V/3)
    # 或者
    alpha_L = 1./lattice_vector[1] * (lattice_vector[2] -
                                      lattice_vector[0])/(temperature[2]-temperature[0])
    print("Linear expansion coefficient of Si:", alpha_L)

  def thermal_expansion_calc_new(self):
    from py4vasp import plot
    # fill the list of volume in the same order as the temperature
    volume = [319.0557, 319.17776, 319.399933]
    temperature = [200, 300, 400]

    plot(temperature, volume, xlabel="T (K)", ylabel="V (Å³)")
    alpha_V = 1./volume[2] * (volume[2]-volume[0]) / \
        (temperature[2]-temperature[0])
    print("Thermal expansion coefficient of Si:", alpha_V)
    alpha_L = alpha_V/3
    print("Linear expansion coefficient of Si:", alpha_L)

    lattice_vector = [7.6709362918889177,
                      7.6723234856666895, 7.6730585861110878]
    temperature = [200, 300, 400]

    alpha_L = 1./lattice_vector[1] * (lattice_vector[2] -
                                      lattice_vector[0])/(temperature[2]-temperature[0])
    print("Linear expansion coefficient of Si:", alpha_L)

    plot(temperature, lattice_vector, xlabel="T (K)", ylabel="a (Å)")


class HybridFunctionals():
  def __init__(self) -> None:
    pass

  def pars_set(self):
    self.pars_pbe_dict = {'gga': 'PE',
                          'ismear': -5,
                          'lorbit': 11, }
    self.pars_pbe0_dict = {'gga':      'PE',
                           'lhfcalc':  'T',
                           'ismear':   0,
                           'sigma': 0.01,
                           'algo':     'Damped',
                           'time':   0.8, }
    self.pars_HF_dict = {'lhfcalc': 'T',
                         'aexx': 1,
                         'ismear': 0,
                         'sigma': 0.01,
                         'algo': 'Damped',
                         'time': 0.4, }
    self.pars_B3LYP_dict = {'gga': 'PE',
                            # 'gga': 'B3',
                            'lhfcalc': 'T',
                            'aexx': 0.2,
                            'aggax': 0.72,
                            'aggac': 0.81,
                            'aldac': 0.19,
                            'ismear': 0,
                            'sigma': 0.01,
                            'algo': 'Damped',
                            'time': 0.4,
                            }

    self.pars_screened_hybrid_dict = {'ismear': 0,
                                      'sigma': 0.01,
                                      'lhfcalc': 'T',
                                      'hfscreen': 0.2,
                                      'aexx': 0.25,
                                      'algo': 'Damped',
                                      'time': 0.4,
                                      }
    self.pars_HSE06_dict = self.pars_screened_hybrid_dict

  def get_band_gap(self, atoms):
    """计算带隙

    Args:
        atoms (_type_): _description_

    Returns:
        _type_: _description_
    """
    a, b = atoms.calc.get_homo_lumo()
    return b-a

  def band_gap_of_Si_with_pbe_and_pbe0_functionals(self,
                                                   directory='band_gap_of_Si_with_pbe_and_pbe0_functionals',):
    """By the end of this tutorial, you will be able to:
    explain what is a hybrid functional
    setup a PBE0 calculation
    compute the band gap
    """

    import py4vasp
    atoms = ase.build.bulk('Si')
    calc = ase.calculators.vasp.Vasp(kpts=(7, 7, 7))

    def func(directory, pars_dict):
      if not os.path.exists(directory):
        calc.set(directory=directory)
        calc.set(**pars_dict)
        atoms.calc = calc
        atoms.get_potential_energy()
        if 'pbe0' in directory:
          calc.reset()
          calc.set(algo=None, ismear=-5, lorbit=11, gga='PE',
                   lhfcalc='T',)
          atoms.get_potential_energy()
          pass
      else:
        calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
        atoms = calc.get_atoms()
        return atoms

    atoms_pbe = func(directory=os.path.join(
        directory, 'pbe'), pars_dict=self.pars_pbe_dict)
    atoms_pbe0 = func(directory=os.path.join(
        directory, 'pbe0'), pars_dict=self.pars_pbe0_dict)

    # plot DOS
    # pbe_calc = py4vasp.Calculation.from_path("./e01_Si-gap")
    dos1 = py4vasp.data.Dos.from_path(
        'band_gap_of_Si_with_pbe_and_pbe0_functionals/pbe')
    dos2 = py4vasp.data.Dos.from_path(
        'band_gap_of_Si_with_pbe_and_pbe0_functionals/pbe0')
    fig = dos1.plot().label('PBE') + dos2.plot().label('PBE0')
    fig.to_plotly().show()

    # 计算带隙
    print(
        f'带隙pbe: {self.get_band_gap(atoms_pbe)}, pbe0: {self.get_band_gap(atoms_pbe0)}')
    return atoms_pbe, atoms_pbe0

  def band_gap_with_B3LYP_functionals_and_HF_mehtod(
      self,
      directory='band_gap_with_B3LYP_functionals_and_HF_mehtod',

  ):
    """By the end of this tutorial, you will be able to:

    use the B3LYP functional
    use the HF method
    explain the limitations of HF and B3LYP
    """
    atoms = ase.build.bulk('Ar')
    calc = ase.calculators.vasp.Vasp(kpts={'size': (4, 4, 4), 'gamma': True})

    def func(pars_dict, directory=directory,  atoms=atoms, calc=calc):
      if not os.path.exists(directory):
        calc.set(directory=directory)
        calc.set(**pars_dict)
        atoms.calc = calc
        atoms.get_potential_energy()
      else:
        calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
        atoms = calc.get_atoms()
      return atoms

    atoms_hf = func(pars_dict=self.pars_HF_dict,
                    directory=os.path.join(directory, 'HF'))
    atoms_b3lyp = func(pars_dict=self.pars_B3LYP_dict,
                       directory=os.path.join(directory, 'b3lyp'))

    print(
        f'band_gap_hf: {self.get_band_gap(atoms=atoms_hf)}, band_gap_b3lyp: {self.get_band_gap(atoms=atoms_b3lyp)}')
    pass

  def band_gap_optimization_for_MgO_for_screened_hybrid_functionals(
          self,
          directory='band_gap_optimization_for_MgO_for_screened_hybrid_functionals',
          fname_json='result.json',):
    """By the end of this tutorial, you will be able to:
    understand the fundamentals of screened hybrid functionals
    explain the basic assumptions taken by the HSE06 functional
    optimize the fraction of exchange and the screening length for the band gap

    Optimize the fraction of Fock exchange in a screened hybrid functional in order to reproduce the experimental band gap of MgO.
    """
    import ase.spacegroup
    import ase.calculators.vasp
    import json

    calc = ase.calculators.vasp.Vasp(kpts=(5, 5, 5), xc='pbe')

    fname_json = os.path.join(directory, fname_json)
    if not os.path.exists(fname_json):
      a = 3.01
      atoms = ase.spacegroup.crystal(['Mg', 'O'], basis=[(0, 0, 0), (0.5, 0.5, 0.5)],
                                     cellpar=[a, a, a, 60, 60, 60])
      calc.set(**self.pars_pbe_dict, directory=directory)
      atoms.calc = calc
      atoms.get_potential_energy()
      # dos = py4vasp.data.Dos.from_path(directory)
      # dos.plot().to_plotly().show()

      band_gaps = []
      aexxs = [0.40, 0.45, 0.50, 0.55]
      for aexx in aexxs:
        self.pars_screened_hybrid_dict.update({'aexx': aexx})
        calc.set(**self.pars_screened_hybrid_dict)
        atoms.calc = calc
        atoms.get_potential_energy()
        band_gap = self.get_band_gap(atoms=atoms)
        band_gaps.append(band_gap)
        print(f'aexx: {aexx}, band_gap: {band_gap}')

      result_dict_aexx_test = {'aexx': aexxs, 'band_gap': band_gaps}
      print('MgO 带隙的实验值为7.7 因此The optimal AEXX should be between 0.45 and 0.50.')

      # 测试 hfscreen 参数
      hfscreens = np.arange(0.15, 0.35, 0.05)
      band_gaps2 = []
      for hfscreen in hfscreens:
        self.pars_screened_hybrid_dict.update({'hfscreen': hfscreen})
        calc.set(**self.pars_screened_hybrid_dict)
        atoms.calc = calc
        atoms.get_potential_energy()
        band_gap = self.get_band_gap(atoms=atoms)
        band_gaps2.append(band_gap)
        print(f'hfscreen: {hfscreen}, band_gap: {band_gap}')

      result_dict_hfscreen_test = {
          'hfscreen': hfscreens, 'band_gap': band_gaps2}

      result_dict = {'result_dict_aexx_test': result_dict_aexx_test,
                     'result_dict_hfscreen_test': result_dict_hfscreen_test}
      with open(fname_json, 'w') as f:
        json.dump(result_dict, fp=f, ensure_ascii=True, indent=2)
    else:
      with open(fname_json,) as f:
        result_dict = json.load(fp=f,)

    return result_dict

  def band_structure_of_CaS_with_the_PBE_and_HSE06_functionals(self,
                                                               directory='band_structure_of_CaS_with_the_PBE_and_HSE06_functionals'):
    """By the end of this tutorial, you will be able to:
    compute the band structure using a hybrid functional
    """
    import ase.spacegroup
    import ase.calculators.vasp
    import ase
    a = 4.042
    atoms = ase.spacegroup.crystal(['Ca', 'S'], basis=[(0, 0, 0), (0.5, 0.5, 0.5)],
                                   cellpar=[a, a, a, 60, 60, 60])

    calc = ase.calculators.vasp.Vasp(
        directory=directory, kpts=(1, 1, 1), gamma=True, xc='pbe')

    def compute(sets, directory, atoms=atoms, calc=calc):
      atoms.calc = calc
      calc.reset()
      calc.set(**sets, directory=directory)
      atoms.get_potential_energy()
      return atoms
    # pbe 单点
    directory_pbe = directory+'/pbe_results'
    atoms = compute(sets=self.pars_pbe0_dict, directory=directory_pbe)
    # pbe band structure
    sets = {'ismear': 0, 'sigma': 0.01,  # 'icharg': 11, # 为什么呢？
            'kpts': {'path': 'LWXG', 'npoints': 20}}
    atoms = compute(sets=sets, directory=directory_pbe, calc=calc)

    # HSE06
    # 单点
    directory_hse06 = directory+'/hse06_results'
    compute(sets=self.pars_HSE06_dict, directory=directory_hse06)
    # band
    atoms = compute(sets=self.pars_HSE06_dict.update(
        {'lorbit': 11, 'kpts': {'path': 'LWXG', 'npionts': 20}}),
        directory=directory_hse06)

    return atoms


class GWApproximation():
  def __init__(self) -> None:
    pass

  def compute(self, sets, atoms, calc):
    calc.set(**sets)
    atoms.calc = calc
    atoms.get_potential_energy()

  def band_gap_of_Si_within_the_G0W0_approximation(self,
                                                   directory='band_gap_of_Si_within_the_G0W0_approximation'):
    """url='https://www.vasp.at/tutorials/latest/gw/part1/'
    输入文件可以从这里下载
    By the end of this tutorial, you will be able to:
    run a single-shot GW calculation (G0W0
    obtain the quasiparticle energies and renormalization factor
    """
    atoms = ase.build.bulk('Si')
    calc = ase.calculators.vasp.Vasp(xc='pbe', directory=directory)

    def bs(atoms, calc):
      # 单点
      sets = {'ismear': -5,
              'encut': 400,
              'ediff': 1e-6,
              'kpts': (6, 6, 6),
              'gamma': True,
              'lorbit': 11}
      self.compute(sets=sets, atoms=atoms, calc=calc)

      # bs
      sets = {'kpts': {'path': 'GXUKLW', 'npoints': 20}, 'ismear': 0}
      self.compute(sets=sets, atoms=atoms, calc=calc)

    def unoccupied_ks_orbitals(directory='xx/unoccupied_ks/'):
      import py4vasp
      # Compute additional unoccupied Kohn-Sham orbitals
      atoms = ase.build.bulk('Si')
      calc = ase.calculators.vasp.Vasp(xc='pbe', directory=directory)
      sets = {'ismear': -5,
              'encut': 400,
              'ediff': 1e-6,
              'kpts': (6, 6, 6),
              'gamma': True,
              'lorbit': 11}
      calc.set(**sets)
      atoms.calc = calc
      atoms.get_potential_energy()

      sets = {'ismear': 0,
              'nbands': 64,  # maybe even more bands
              'algo': 'Exact',  # use exact diagonalization of the Hamiltonian
              'nelm': 1,  # ! since we are already converged stop after one step
              'loptics': True,  # write WAVEDER
              }
      calc.set(**sets)
      atoms.calc = calc
      atoms.get_potential_energy()

      # As a byproduct, you are now able to plot the electronic dielectric function using py4vasp!
      optics_calc = py4vasp.data.DielectricFunction.from_path(path=directory)
      optics_calc.plot().to_plotly().show()

    unoccupied_ks_orbitals()

    def G0W0():
      from py4vasp import Calculation
      directory_base = 'band_gap_of_Si_within_the_G0W0_approximation/unoccupied_ks'
      directory = 'band_gap_of_Si_within_the_G0W0_approximation/unoccupied_ks/G0W0'
      if not os.path.exists(directory):
        os.mkdir(directory)
        shutil.copy(directory_base+'/WAVECAR', directory)

      atoms = ase.build.bulk('Si')
      calc = ase.calculators.vasp.Vasp(xc='pbe', directory=directory)

      sets = {'ismear': 0,
              'sigma': 0.05,
              'nbands': 64,
              # G0W0,
              'algo':   'EVGW0',  # use "GW0" for VASP.5.X
              'nelm': 1,     # use "NELM" prior to VASP.6.3
              'nomega': 50,    # default
              }
      calc.set(**sets)
      atoms.calc = calc

      # calc.calculate(atoms=atoms)
      calc._run(command='vasp_std')

      calc = Calculation.from_path(directory)
      calc.dielectric_function.plot("Re(IPA, RPA)")

    def GW0():
      import os
      import shutil
      directory_base = 'band_gap_of_Si_within_the_G0W0_approximation/unoccupied_ks'
      directory = 'band_gap_of_Si_within_the_G0W0_approximation/unoccupied_ks/GW0'
      if not os.path.exists(directory):
        os.mkdir(directory)
        shutil.copy(directory_base+'/WAVECAR', directory)
        shutil.copy(directory_base+'/WAVEDER', directory)

      atoms = ase.build.bulk('Si')
      calc = ase.calculators.vasp.Vasp(xc='pbe', directory=directory)

      sets = {'ismear': 0,
              'sigma': 0.05,
              'nbands': 64,
              'nbandsgw': 16,
              # G0W0,
              'algo':   'EVGW0',  # use "GW0" for VASP.5.X
              'nelm': 3,     # use "NELM" prior to VASP.6.3
              'nomega': 50,    # default
              }

      calc.set(**sets)
      atoms.calc = calc

      calc.write_input(atoms)
      calc._run(command='vasp_std')
      pass


class BetheSalpeterEquation():
  def __init__(self) -> None:
    pass

  def pars_set(self):
    self.pars_ground_state = {
        'ismear': 0,  # Gaussian smearing
        'sigma': 0.01,  # smearing in eV, small sigma is required to avoid partial occupancies
        'encut': 400,
    }
    self.pars_ground_state_DDH_dict = {
        'ismear': 0,  # Gaussian smearing
        'sigma': 0.01,  # smearing in eV, small sigma is required to avoid partial occupancies
        'encut': 400,
        'lhfcalc': True,  # exact exchange
        'lmodelhf': True,  # range-separated hybrid functional
        'hfscreen': 1.7,  # the range-separation parameter
        'aexx': 0.175,  # the fraction of exact exchange
    }

    self.pars_unoccupied_states_DDH_dict = {**self.pars_ground_state_DDH_dict,
                                            'nbands': 8,  # include 4 unoccupied bands
                                            'algo': 'Exact',  # use exact diagonalization of the Hamiltonian
                                            'nelm': 1,  # since we are already converged stop after one step
                                            'loptics': True,  # write WAVEDER
                                            }
    self.pars_TDHF_dict = {**self.pars_unoccupied_states_DDH_dict,
                           'lfxc': True,  # local xc kernel
                           'algo': 'TDHF',  # use TDHF algorithm
                           'antires': 0,  # Tamm-Dancoff approximation
                           'nbandsv': 4,  # number of conduction bands in BSE
                           'nbandso': 4,  # number of valence bands in BSE
                           'cshift': 0.6,  # complex shift/broadening
                           }

  def fgap(self, gs):
    homo = gs.band.to_frame().query('occupations > 0.5').max()['bands']
    lumo = gs.band.to_frame().query('occupations < 0.5').min()['bands']
    return lumo - homo

  def dgap(self, gs):
    energies = gs.band.to_dict()
    dir_gaps = [min(b[o < 0.5]) - max(b[o > 0.5])
                for b, o in zip(energies["bands"], energies["occupations"])]
    return min(dir_gaps)

  def optical_absorption_of_diamond_carbon(self,
                                           directory='optical_absorption_of_diamond_carbon',
                                           ):
    """1. DFT ground state
    2. DFT with exact diagonalization to compute unoccupied bands 
    3. G0W0 calculation
    """
    atoms = ase.build.bulk('C', cubic=True)
    calc = ase.calculators.vasp.Vasp(kpts=(2, 2, 2), gamma=True, xc='pbe'),
    directory_gs = directory+'/ground_state'

    def ground_state():
      # groud_state
      calc.set(directory=directory_gs)
      calc.set(ismear=0, sigma=0.01)
      atoms.calc = calc
      atoms.get_potential_energy()

      gs = py4vasp.Calculation.from_path(directory_gs)
      print("PBE fundamental band gap for C: {0:.2f}".format(self.fgap(gs)))
      print("PBE direct band gap for C: {0:.2f}".format(self.dgap(gs)))
    # ground_state()

    directory_us = directory+'/unoccupied_states'
    import py4vasp

    def unoccupied_states():
      if not os.path.exists(directory_us):
        os.makedirs(directory_us, exist_ok=True)
        shutil.copy(f'{directory_gs}/WAVECAR', directory_us)
        calc.set(directory=directory_us)
        sets = {
            'nbands': 64,  # include 60 unoccupied bands
            'algo': 'Exact',  # use exact diagonalization of the Hamiltonian
            'nelm': 1,  # since we are already converged, stop after one step
            'loptics': True,  # write orbitals derivatives to WAVEDER
            'cshift': 0.6,  # broadening of the dielectric function
        }
        calc.set(**sets)
        atoms.calc = calc
        atoms.get_potential_energy()

      die = py4vasp.data.DielectricFunction.from_path(directory_us)
      die.plot('Im').show()
    # unoccupied_states()

    directory_g0w0 = directory+'/G0W0'

    def g0w0(is_recalc=False):
      import py4vasp
      #  GW pseudopotentials of C.
      if not os.path.exists(directory_g0w0) or is_recalc:
        os.makedirs(directory_g0w0, exist_ok=True)
        shutil.copy(directory_us+'/WAVECAR', directory_g0w0)
        shutil.copy(directory_us+'/WAVEDER', directory_g0w0)

        calc.set(setups={'C': '_GW'}, directory=directory_g0w0)
        sets = sets = {
            'nbands': 64,  # include 60 unoccupied bands
            'algo': 'G0W0',  # use the evGW algorithm
            'nelm': 1,  # only one iteration for G0W0
            'kpar': 4,  # number of k-points treated in parallel
            'nomega': 50,  # the default is 100
            'lrpa': True,
            'encut': 400,
        }
        calc.set(**sets)
        atoms.calc = calc
        # atoms.get_potential_energy()
        calc.write_input(atoms)
        calc._run(command='mpirun -np 4 vasp_std')

      # 查看带隙
      gs = py4vasp.Calculation.from_path(directory_g0w0)
      print("PBE fundamental band gap for C: {0:.2f}".format(self.fgap(gs)))
      print("PBE direct band gap for C: {0:.2f}".format(self.dgap(gs)))

      die_ipa = py4vasp.data.DielectricFunction.from_path(directory_us)
      die_rpa = py4vasp.data.DielectricFunction.from_path(directory_g0w0)
      fig = die_ipa.plot('Im').label('IPA') + \
          die_rpa.plot('RPA(Im)').label('RPA')
      fig.to_plotly().show()
      pass
    # g0w0(is_recalc=False)

    directory_bse = directory + '/bse'

    def optical_absorption_in_BSE(is_recalc=False):
      if not os.path.exists(directory_bse) or is_recalc:
        os.makedirs(directory_bse, exist_ok=True)
        os.system(f'cp {directory_g0w0}' +
                  '/{WAVECAR,WAVEDER,W*.tmp} ' + directory_bse)

        sets = {'nbands': 64,  # should be the same as in the GS
                # ! BSE
                'algo': 'BSE',  # ! BSE calculation
                'antires': 0,  # ! Tamm-Dancoff approximation
                'nbandsv': 4,  # ! number of conduction bands in BSE
                'nbandso': 4,  # ! number of valence bands in BSE
                'cshift': 0.6,  # ! complex shift/broadening
                'encut': 400,
                }
        calc.set(directory=directory_bse)
        calc.set(**sets)
        atoms.calc = calc
        calc.write_input(atoms=atoms)
        calc._run(command='vasp_std')
        # atoms.get_potential_energy()
      ipa = py4vasp.data.DielectricFunction.from_path(directory_us)
      rpa = py4vasp.data.DielectricFunction.from_path(directory_g0w0)
      bse = py4vasp.data.DielectricFunction.from_path(directory_bse)
      fig = ipa.plot("Im").label(
          "IPA") + rpa.plot("RPA(Im)").label("RPA") + bse.plot("BSE(Im)").label("BSE")
      fig.to_plotly().show()
      pass

    optical_absorption_in_BSE()
    pass

  def compute(self, atoms, calc, sets, directory):
    calc.set(directory=directory)
    calc.set(**sets)
    calc.write_input(atoms=atoms)
    calc._run(command='vasp_std')

  def optical_absorption_of_diamond_through_TDDDH(self,
                                                  directory='optical_absorption_of_diamond_through_TDDH',
                                                  ):
    """Find parameters for the model dielectric function
    Perform calculations of the optical absorption via TDDFT including the excitonic effects

    Args:
        seof (_type_): _description_
    """
    atoms = ase.build.bulk('C')
    calc = ase.calculators.vasp.Vasp(kpts=(2, 2, 2), gamma=True, xc='pbe'),

    # ground_states
    directory_gs = directory+'/gs'
    if not os.path.exists(directory_gs):
      self.compute(atoms, calc, sets=self.pars_ground_state,
                   directory=directory_gs)

    directory_gs_ddh = directory+'/ground_states_DDH'
    if not os.path.exists(directory_gs_ddh):
      os.makedirs(directory_gs_ddh, exist_ok=True)
      shutil.copy(directory_gs+'/WAVECAR', directory_gs_ddh)
      self.compute(atoms, calc, sets=self.pars_ground_state_DDH_dict,
                   directory=directory_gs_ddh)

    # unoccupied_states
    directory_unoccupied_states = directory+'/unoccupied_states'
    if not os.path.exists(directory_unoccupied_states):
      os.makedirs(directory_unoccupied_states, exist_ok=True)
      shutil.copy(directory_gs+'/WAVECAR', directory_unoccupied_states)
      self.compute(atoms, calc, sets=self.pars_unoccupied_states_DDH_dict,
                   directory=directory_unoccupied_states)

    # TDHF
    directory_TDHF = directory + '/TDHF'
    if not os.path.exists(directory_TDHF):
      os.makedirs(directory_TDHF, exist_ok=True)
      shutil.copy(directory_unoccupied_states+'/WAVECAR', directory_TDHF)
      shutil.copy(directory_unoccupied_states+'/WAVEDER', directory_TDHF)
      self.compute(atoms, calc, sets=self.pars_TDHF_dict,
                   directory=directory_TDHF)

    # plot # 有错误以后在处理
    # import py4vasp.data
    # die = py4vasp.data.DielectricFunction
    # p1 = die.from_path(directory_unoccupied_states)
    # p2 = die.from_path(directory_TDHF)
    # fig = p1.plot('p1').label('IPA') + p2.plot('p2').label('rPA')
    # fig.to_plotly().show()

    pass

  def Optical_absorption_of_LiF(self):
    """https://www.vasp.at/tutorials/latest/bse/part2/
    不想做了，以后再说
    """
    pass

  def Efficient_Brillouin_zone_sampling_and_analysis_of_the_excitons(self):
    """https://www.vasp.at/tutorials/latest/bse/part3/
    不想做了，以后再说
    """
    pass


# vaspsol

class VaspSol():
  def __init__(self) -> None:
    """查看溶剂的介电常数, 比如水73.355 https://gaussian.com/scrf/ -> more-> solvent 

    VASPsol是在平面波DFT代码VASP中植入了一个实现使用隐式溶剂化模型的代码。该模型描述了静电、空化和色散对溶质和溶剂相互作用的影响。它实现了考虑溶剂化对分子在晶体表面吸附及其反应能垒的影响。溶剂化模型实现的优势在于其具有处理大型周期性系统(如金属和半导体表面)的能力，以及与标准超软赝势(ultrasoft pseudopotential)和投影缀加波(PAW)势函数具有较好的兼容性。

    VASPsol的参数
    lsol=True,  # 溶剂化模型控制开关
    eb_k=78.4  # 溶剂的相对介电常数可以从水的默认值78.4改为其它
    lrhob=True,  # if you would like to write out the bound charge density in the CHGCAR format. The file is named RHOB.
    tau=0, # surface tension parameter, 忽略 cavitation energy contribution, set TAU = 0
    lambda_d_k=x? # the Debye length in Angstroms parameter,to use the linearized Poisson-Boltzmann model(electrolyte model)

    数据分析: 
    对费米能级修正
    E_fermi += FERMI_SHIFT
    能量修正
    energy += Q*V  # 其中Q是模拟单元的净电荷，V是参考电势的偏移，例如，V = FERMI_SHIFT。
    """

    pass

  def install(self):
    """有关装说明: https://github.com/henniggroup/VASPsol

    1. copy solvation.F from path_to_VASPsol/src/solvation.F to path_to_VASP6_install/src/
    cp /Users/wangjinlong/my_linux/soft_learn/vasp_learn/package/VASPsol-master/src/solvation.F src/
    2. Set the CPP option "-Dsol_compat" in the VASP makefile.include file.
    3. 在src/ 目录下执行: patch -p0 < ~/my_linux/soft_learn/vasp_learn/package/VASPsol-master/src/patches/pbz_patch_610
    4. make DEPS=1 -j10 all 
    """
    os.system(
        'cp /Users/wangjinlong/my_linux/soft_learn/vasp_learn/package/VASPsol-master/src/solvation.F src/')
    cwd = os.getcwd()
    os.chdir('src')
    os.system(
        'patch -p0 < ~/my_linux/soft_learn/vasp_learn/package/VASPsol-master/src/patches/pbz_patch_610')
    os.chdir(cwd)
    os.system('make DEPS=1 -j10 all')
    pass

  def example_h2o(self):
    # v = VaspLearn()  # 初始化环境变量
    # 第一步获取普通DFT结构弛豫波函数
    atoms = ase.build.molecule('H2O', vacuum=5, pbc=True)
    calc = ase.calculators.vasp.Vasp(atoms=atoms,
                                     command='mpirun -np 4 vasp',
                                     encut=400,  # 800
                                     sigma=0.01,
                                     ediff=1e-6,
                                     prec='Acuurate',
                                     ismear=0,
                                     lsol=False,  # 溶剂化模型控制开关
                                     txt='-',
                                     kpts={'gamma': True}
                                     )
    atoms.get_potential_energy()
    # 第二步: 得到第一步的波函数后，打开溶剂化模型，输入溶剂介电常数即可：
    calc.set(lsol=True,
             eb_k=80  # 溶剂介电常数
             )
    atoms.get_potential_energy()
    pass

  def example_PbS_111(self):
    # 创建 PbS 的块体结构
    bulk = ase.build.bulk('PbS', crystalstructure='rocksalt', a=5.995)
    # 创建 PbS (100) 表面，
    surface = ase.build.surface(lattice=bulk, indices=(
        1, 0, 0), layers=5, vacuum=5.0, periodic=True)

    calc = ase.calculators.vasp.Vasp(atoms=surface,
                                     command='mpirun -np 4 vasp',
                                     encut=400,  # 800
                                     sigma=0.1,
                                     ediff=1e-6,
                                     prec='Acuurate',
                                     ismear=1,  # 注意
                                     txt='-',
                                     kpts=(8, 8, 1),
                                     )

    surface.get_potential_energy()
    # 第二步: 得到第一步的波函数后，打开溶剂化模型，输入溶剂介电常数即可：
    calc.set(lsol=True,  # 溶剂化模型控制开关
             eb_k=80  # 溶剂的相对介电常数可以从水的默认值78.4改为其它
             )
    surface.get_potential_energy()

    pass

  def analysis(self):

    pass

  def verify(sef):
    """* 对于O@Pt100表明, 结果表明, 考虑溶剂化效应后, 体系的能量降低, 计算溶剂化效应的吸附能时, slab+O, slab, O 都需要考虑溶剂化效应

    Args:
        sef (_type_): _description_
    """
    pass


class AseVaspLearn():
  def __init__(self):
    """ 建议使用这个类
    * https://www.bigbrosci.com/zh-cn/latest/
    * B站搜视频: VASP理论催化计算实战教学课堂, VASP 新手教程Part1-软件基本介绍
    ---
    获得 calc 然后用 aseLearn.AseFeatures 来计算各种特征
    """
    super().__init__()
    # ---
    self.Install = Install()
    self.LearnRecords = LearnRecords()
    self.FeaturesAtomsAndMoleculars = FeaturesAtomsAndMoleculars()
    self.FeaturesBulkSystem = FeaturesBulkSystem()
    self.FeaturesMolecularDynamics = FeaturesMolecularDynamics()
    self.HybridFunctionals = HybridFunctionals()
    self.GWApproximation = GWApproximation()
    self.BetheSalpeterEquation = BetheSalpeterEquation()
    self.VaspSol = VaspSol()
    # ---
    # from vasp_learn import calculation
    # self.vaspCalculation = calculation
    pass

  def set_env(self,):
    r""" https://wiki.fysik.dtu.dk/ase/ase/calculators/vasp.html
    初始化VASP使用环境
      1. 设置 势文件的目录
      2. 设置 vdw_kernel.bindat 的目录
    example:
      export ASE_VASP_COMMAND="mpirun -np 4 vasp_std"
      export VASP_PP_PATH="/Users/wangjinlong/job/soft_learn_project/src/soft_learn_project/vasp_learn/data"
      export ASE_VASP_VDW='/Users/wangjinlong/job/soft_learn_project/src/soft_learn_project/vasp_learn/data/vasp_pot.54'
    """
    # 在python环境中执行
    VASP_PP_PATH = importlib.resources.files(
        'soft_learn_project.vasp_learn.data').joinpath('')
    os.environ['VASP_PP_PATH'] = str(VASP_PP_PATH)
    # The environment variable ASE_VASP_VDW should point to the folder where the vdw_kernel.bindat file is located.
    ASE_VASP_VDW = importlib.resources.files(
        'soft_learn_project.vasp_learn.data').joinpath('vasp_pot.54')  # .joinpath('vdw_kernel.bindat')
    os.environ['ASE_VASP_VDW'] = str(ASE_VASP_VDW)
    return None

  def get_calc(self,
               directory='.',
               incar_pars_dict={'xc': 'pbe',
                                'isym': -1,  # 不考虑对称性, 永远是安全的设置，只是速度慢。适用于,畸变、掺杂、表面、分子吸附、NEB、磁性体系
                                'encut': 400,
                                'ispin': 2,  # 最好加上
                                'lorbit': 11,
                                'kpts': (1, 1, 1),
                                'gamma': True,
                                'ediff': 1e-5,
                                # 'ediffg': -5e-2,
                                'ivdw': 11,
                                # 'symprec': 1e-4,
                                # 'lreal': 'Auto',
                                # 'ncore': 4,
                                'ismear': 0,
                                'sigma': 0.03,
                                },
               command='mpirun -np 4 vasp_std',
               **kwargs,):
    """https://wiki.fysik.dtu.dk/ase/ase/calculators/vasp.html
      1. incar_pars_dict 为设置的默认参数
      2. **kwargs 为设置的其他参数
      * 如果你对你的系统没有先验知识，例如，如果你不知道你的系统是绝缘体、半导体还是金属，那么总是使用高斯涂抹ISMEAR=0结合小SIGMA=0.03-0.05。这还不是VASP的默认设置，所以为了安全起见，您可能希望在所有INCAR文件中包含此设置。# 我自己的测试: 对于单原子来说, 小sigma会导致收敛慢, 对能量的影响大, 应该使用相同的sigma值比较两个计算
    """
    self.set_env()
    # ---
    if not os.path.exists(directory):
      os.makedirs(directory)
    calc = ase.calculators.vasp.Vasp(directory=directory,
                                     command=command,
                                     **incar_pars_dict,
                                     )
    calc.set(**kwargs)
    return calc

  def string_install(self):
    string = """vasp mac 安装
    直接复制arch/makefile.include.gnu 到 makefile.include 
    1. 修改库的root外:例如brew list openblas, 找到 /opt/homebrew/Cellar/openblas/0.3.28
    2. 修改: LLIBS       =  -lc++
    3. 修改: CPP         = gcc-14 -E -C -w $*$(FUFFIX) >$*$(SUFFIX) $(CPP_OPTIONS)
      CC_LIB      = gcc 改为gcc-14 也可以
    4. 编译: make veryclean; make DEPS=1 -j18 std |tee a.txt
    """
    print(string)
    return None

  def string_ase_vasp_env(self, vasp_path='xxx/vasp_std'):
    string = r"""将以下内容写入 ~/.bashrc
    export ASE_VASP_COMMAND="/opt/homebrew/bin/mpirun -np 4 vasp_std"
    export VASP_PP_PATH="/Users/wangjinlong/job/soft_learn/vasp_learn/vasp_pot"

    方法二: python 方法,
    os.environ['ASE_VASP_COMMAND'] = f'/opt/homebrew/bin/mpirun -np 4 vasp_std'
    os.environ['VASP_PP_PATH'] = '/Users/wangjinlong/job/soft_learn/vasp_learn/vasp_pot'
    """
    print(string)
    return None

  def string_calc(self):
    string = """vasp 计算:
    方法1: 通过ase 来计算
    import ase
    import ase.build 
    import ase.calculators
    import ase.calculators.vasp
    from ase.visualize import view as view 
    import os 

    os.environ['ASE_VASP_COMMAND'] = f'/opt/homebrew/bin/mpirun -np 4 vasp_std'
    os.environ['VASP_PP_PATH'] = '/Users/wangjinlong/job/soft_learn/vasp_learn/vasp_pot'
    atoms = ase.build.molecule('H2',vacuum=4,pbc=True)
    calc = ase.calculators.vasp.Vasp(directory='exercise_tmp/H2_test',
                                    xc='pbe', encut=400, ispin=1, kpts=(1,1,1))
    calc.write_input(atoms=atoms,)
    energy = calc.get_potential_energy()
    print(energy)
    ---
    方法2: 
    直接建立四个 输入文件 INCAR, POSCAR, POTCAR, KPOINTS, 并在该目录下运行: mpirun -np 4 vasp_std 
    """
    print(string)
    return None
