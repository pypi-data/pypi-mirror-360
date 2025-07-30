import ase
import ase.io
import ase.calculators.vasp
import ase.io.vasp
import ase.build
import ase.mep
import os
import copy
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class NEBCalc():
  def __init__(self) -> None:
    r"""#region 
    https://theory.cm.utexas.edu/vtsttools/optimizers.html#optimizers
    这里只提供vasp使用的传统 neb 方法, ase方法见 aseLearn.NEBCalc
    vaspwiki:  https://www.vasp.at/wiki/index.php/Collective_jumps_of_a_Pt_adatom_on_fcc-Pt_(001):_Nudged_Elastic_Band_Calculation
    https://theory.cm.utexas.edu/vtsttools_old/index.php
    参数设置:
    #--- NEB parameters ---
    #- standard parameters
    ICHAIN  = 0  		Indicates which method to run. NEB (ICHAIN=0) is the default
    IMAGES  = 4  		Number of NEB images between the fixed endpoints
    SPRING = -5.0  		The spring constant, in eV/Ang^2 between the images; negative value turns on nudging
    LCLIMB = .TRUE.  	Flag to turn on the climbing image algorithm
    LTANGENTOLD  = .FALSE.  Flag to turn on the old central difference tangent
    LDNEB = .FALSE.  	Flag to turn on modified double nudging
    #LNEBCELL = .FALSE.	Flag to turn on SS-NEB. Used with ISIF=3 and IOPT=3.
    #JACOBIAN 	(Ω/N)^{1/3}N^{1/2} Controls weight of lattice to atomic motion. Ω is volume and N is the number of atoms.
    NSW = 300
    IBRION = 3   #2也可以？现在不确定

    #--force based optimization
    POTIM = 0.1  #1?
    IOPT = 0  #use vasp optimizer specified from IBRION
    #--或者如下
    #POTIM = 0  #其它优化方法
    #IOPT =3    #可选项1,2,3,4,7, 1,2 不能用，建议用3，7

    # 数据处理:
    #--参考网址https://wenku.baidu.com/view/4bce8028b4daa58da0114af0.html
    1. 00 初态，05 末态，目录中放置POSCAR和OUTCAR即可
    2. 使用nebmake.pl 构建images #e.g.
    nebmake.pl 00/POSCAR 05/POSCAR 4
    3. 计算过程中可以使用nebbarrier.pl (获取neb.dat),然后cat neb.dat查看, 第三列为能量差值
    4. 查看neb图形结果，nebspline.pl 获取mep.eps和spline.dat
    对于spline.dat可以自定义绘图
    5. 计算结束后查看01-04中的OUTCAR，要有reached acquired accuracy
    获取neb动画，nebmovie.pl
    usage: nebmovie.pl (flag)
    output: movie.xyz
    Can be used to generate a movie from standard xyz files, generated either by POSCARs (flag=0) or CONTCARs (flag=1) in every directory.

    #-
    usage: nebresults.pl
    output: spline.dat, neb.dat, exts.dat, mep.eps, movie.xyz, vaspgr

    6. 为确定过渡态，需要进行频率计算，只有He设置为T T T,获取He的震动频率有且只有一个虚频，查找OUTCAR中关键词"Eigenvector and eigenvaluse"部分

    #--- 如果neb中断想要继续
    vfin.pl
    usage: vfin.pl (output directory)
    This script finds the ICHAIN tag from the OUTCAR and cleans up the run directory accordingly. All relevant files (POSCAR, CONTCAR, OUTCAR (zipped), INCAR, KPOINTS, XDATCAR (zipped), CHGCAR and WAVECAR if the are non-empty) are copied to the output directory. In the run directory CONTCARs are moved over POSCARs in preparation for a new run.

    #---获取指定原子的径向分布函数
    pos2rdf.pl
    usage: pos2rdf.pl (POSCAR) (atom) (bin size)
    output: radial distribution around specified atom, to STDOUT

    ---
    INCAR example
    KSPACING = 0.200000
    SIGMA = 0.200000
    EDIFF = 1.00e-06
    ALGO = Normal
    GGA = PE
    PREC = Normal
    ISIF = 2
    ISMEAR = 1
    ISPIN = 1
    ISYM = 0
    NELM = 100
    NCORE = 8
    LASPH = .TRUE.
    LCHARG = .FALSE.
    LWAVE = .FALSE.
    LREAL = Auto

    # NEB PARAMETERS
    ICHAIN = 0
    LCLIMB = .TRUE.
    SPRING = -5
    IMAGES = 11

    # OPTIMIZER PARAMETERS
    IBRION = 3
    POTIM = 0
    IOPT = 3
    EDIFFG = -0.01
    NSW = 200
    """

    # 我的经验: spring=-5 images=3 400 步没收敛; spring=-1 images=5 275 步就收敛了, 另一个测试 spring=-1 发现有点小了, 有个测试 spring=-5 images=5 86步就收敛了
    self.incar_neb_pars_dict = {
        # https://theory.cm.utexas.edu/vtsttools/
        # 优化器参数
        # https://theory.cm.utexas.edu/vtsttools/optimizers.html#optimizers
        # --- NEB 参数
        # Indicates which method to run. NEB (ICHAIN=0) is the default
        'ichain': 0,
        'images': 5,  # Number of NEB images between the fixed endpoints
        'spring': -5,  # The spring constant, in eV/Ang^2 between the images; negative value turns on nudging 默认-5 感觉有点大, 如果 图像没在鞍点则增大 spring, spring=-1 时测试有点小了
        'lclimb': False,  # Flag to turn on the climbing image algorithm, 如果你的目标是找到过渡态（TS），推荐先用普通 NEB（LCLIMB = .FALSE.）优化路径，然后用 CI-NEB（LCLIMB = .TRUE.）精细优化过渡态。
        # 'ltangentold': False,  # Flag to turn on the old central difference tangent # False 时是采用改进的爬坡 NEB（CI-NEB, Climbing Image NEB）方法中的新切向计算方式。 这种方法在路径弯曲较大时，更准确地计算反应路径上的力，使得 NEB 更容易收敛到合理的过渡态。 适用于大多数 NEB 计算，特别是弯曲路径较多的情况。
        'ldneb': False,  # Flag to turn on modified double nudging 一般情况下，建议 先尝试默认 NEB，如果发现路径力异常或不稳定，再考虑打开 LDNEB 选项。
        # LNEBCELL = .FALSE.	Flag to turn on SS-NEB. Used with ISIF=3 and IOPT=3. 如果研究的是固体相变（如高压下的相变、晶体形变、材料中的扩散），并且需要考虑晶胞变化，可以尝试 LNEBCELL = .TRUE.，但必须 配合 ISIF = 3 和 IOPT = 3 使用。
        # JACOBIAN 	(Ω/N)^{1/3}N^{1/2} Controls weight of lattice to atomic motion. Ω is volume and N is the number of atoms.
        # --- 优化器参数
        'ibrion': 3,
        'potim': 0,
        'iopt': 3,
        # (IOPT = 0) Use VASP optimizers specified from IBRION (default)
        # (IOPT = 1) LBFGS = Limited-memory Broyden-Fletcher-Goldfarb-Shanno
        # (IOPT = 2) CG = Conjugate Gradient  # 该方法不好 尽量用 3
        # (IOPT = 3) QM = Quick-Min
        # (IOPT = 4) SD = Steepest Descent
        # (IOPT = 7) FIRE = Fast Inertial Relaxation Engine  # 7 也可以
        # (IOPT = 8) ML-PYAMFF = Machine learning (PyAMFF)
        'nsw': 400,
        'ediffg': -0.05,
        # ---
        'lwave': False,
        'lcharg': False,
    }
    pass

  def nebmake(self, initial='xxx/POSCAR|ase.Atoms',
              final='xxx/POSCAR|ase.Atoms',
              n_images=5,
              directory='xx/neb',
              ):
    """'usage: nebmake.py POSCAR1 POSCAR2 num_images [-NOIDPP]
    "产生 00-0N 目录
    * 查看下 neb_instance 的 images 是否合理, 如果不合理还是使用下面的方法
    ---
    nebmake.py initial/CONTCAR final/CONTCAR 3
    """
    if isinstance(initial, str):
      initial = ase.io.vasp.read_vasp(initial)
    if isinstance(final, str):
      final = ase.io.vasp.read_vasp(final)
    if isinstance(initial, ase.Atoms):
      pass
    if isinstance(final, ase.Atoms):
      pass
    images = [initial]
    for i in range(n_images):
      images.append(initial.copy())
    images.append(final)
    neb = ase.mep.NEB(images=images)
    # 如果你的系统有约束（如固定部分原子），建议 apply_constraint=True，否则可以省略或设为 False 以获得更自由的插值路径。
    neb.interpolate('idpp', mic=True, apply_constraint=True)

    dir_names = [os.path.join(directory, '0'+str(i))
                 if i < 10 else str(i) for i in range(len(images))]
    for i, image in zip(dir_names, neb.images):
      if not os.path.isdir(i):
        os.makedirs(name=i)
      ase.io.vasp.write_vasp(i+'/POSCAR', image)
    print('Ok, all set up here.')
    print('For later analysis, put OUTCARs in folders 00 and ' + dir_names[-1])
    return neb

  def nebmake_for_restart(self, images,
                          directory='xx/neb',
                          ):
    dir_names = [os.path.join(directory, '0'+str(i))
                 for i in range(len(images)) if i < 10]
    for dir_name, image in zip(dir_names, images):
      # 跳过 00 04 目录
      if os.path.basename(dir_name) in ['00', '0'+str(len(images)-1)]:
        continue
      ase.io.vasp.write_vasp(os.path.join(dir_name, 'POSCAR'), image)

    print('Ok, all set up here.')
    print('For later analysis, put OUTCARs in folders 00 and ' + dir_names[-1])
    return None

  def after_nebmake(self, directory_neb,
                    directory_initial,
                    directory_final,
                    n_images=5):
    """改变 00 为 initial 计算目录, 这里包含OUTCAR
    改变 04 为 final 计算目录
    """

    from py_package_learn.subprocess_learn import subprocessLearn

    dl = [os.path.join(directory_neb, f'0{i}') for i in range(n_images+2)]
    # 去掉 00 0N
    result = subprocessLearn.SubprocessLearn().CLI_cmd(directory=directory_neb,
                                                       args=['rm', '-rf', str(dl[0]), str(dl[-1])])

    # 给初态设置软连接, 要用相对路径, 因为服务器上对于绝对路径有问题
    from py_package_learn.os_learn import osLearn
    directory_initial_relative = osLearn.OsLearn().get_relative_path(
        absolute_path=directory_initial,
        reference_dir=directory_neb)
    directory_final_relative = osLearn.OsLearn().get_relative_path(
        absolute_path=directory_final,
        reference_dir=directory_neb)
    result = subprocessLearn.SubprocessLearn().CLI_cmd(directory=directory_neb,
                                                       args=['ln', '-s', directory_initial_relative, str(dl[0])])
    # 给末态设置软连接
    result = subprocessLearn.SubprocessLearn().CLI_cmd(directory=directory_neb,
                                                       args=['ln', '-s', directory_final_relative, str(dl[-1])])

    pass

  def get_neb_images(self,
                     directory='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/N_dope_graphene/neb/O2_hydrogenation/new/',
                     n_images=5,
                     is_OUTCAR=False):
    """用于查看 neb 00-0N 的 atoms 对象
    """
    atoms_list = []
    for i in range(n_images+2):
      d = os.path.join(directory, f'0{i}')
      file = os.path.join(
          d, 'OUTCAR') if is_OUTCAR else os.path.join(d, 'POSCAR')
      atoms = ase.io.read(filename=file)
      atoms_list.append(atoms)
    return atoms_list

  def run(self,
          atoms_initial,
          calc,
          n_images=5,
          directory='xxx/neb',
          only_write_inputs=True,
          recalc=False,
          **kwargs):
    """* 主要用于产生输入文件
    """
    # calc
    import copy
    calc = copy.deepcopy(calc)  # 如果直接赋值 calculatonvasp.calc 会改变 calc参数
    calc.set(**self.incar_neb_pars_dict, directory=directory,)
    calc.set(images=n_images,)
    calc.set(**kwargs)

    from vasp_learn import base
    base.Base().get_inputs_and_compute(directory=directory,
                                       atoms=atoms_initial,
                                       calc=calc,
                                       recalc=recalc,
                                       only_write_inputs=only_write_inputs,)

    return None

  def restart_neb(self,
                  directory,
                  calc,
                  n_images=5,
                  only_write_inputs=True,
                  **kwargs):
    """1. neb 未收敛, 重新计算neb, 执行完毕后 自己删除01/OUTCAR
    2. 计算 lclimb = True neb 
    """

    # 不要忘记 is_OUTCAR = True
    images = self.get_neb_images(
        directory=directory, n_images=n_images, is_OUTCAR=True)
    # 创建目录
    self.nebmake_for_restart(images=images, directory=directory)
    # 计算
    atoms_initial = ase.io.vasp.read_vasp(
        os.path.join(directory, '00', 'POSCAR'))
    self.run(atoms_initial=atoms_initial,
             n_images=n_images,
             calc=calc,
             directory=directory,
             only_write_inputs=only_write_inputs,
             **kwargs,
             )
    return None

  def restart_neb_with_images(self,
                              directory,
                              calc,
                              images,
                              only_write_inputs=True,
                              **kwargs):
    """xxx
    """

    # 创建目录
    self.nebmake_for_restart(images=images, directory=directory)
    # 计算
    self.run(atoms_initial=images[0],
             n_images=len(images)-2,
             calc=calc,
             directory=directory,
             only_write_inputs=only_write_inputs,
             **kwargs,
             )
    return None

  def analysis_neb(self,
                   directory='xxx/neb',
                   n_images=5,):
    """画 neb.pdf 
    """
    images = self.get_neb_images(directory=directory, is_OUTCAR=True,
                                 n_images=n_images)
    from py_package_learn.ase_learn import aseLearn
    fname_pdf = os.path.join(directory, 'neb.pdf')
    aseLearn.NEB().analysis_neb(images=images,
                                is_save=True,
                                fname_pdf=fname_pdf,
                                )
    return fname_pdf

  # wrapper
  def run_neb_wrapper(self,
                      calc,
                      directory_initial,
                      directory_final,
                      directory_neb='xxx/neb',
                      n_images=5,
                      only_write_inputs=True,
                      **kwargs):
    """需要确定初态和末态
    * **lclimb=False** 推荐先用普通 NEB（LCLIMB = .FALSE.）优化路径，然后用 CI-NEB（LCLIMB = .TRUE.）精细优化过渡态。
    * **'ldneb': False** Flag to turn on modified double nudging 一般情况下，建议 先尝试默认 NEB，如果发现路径力异常或不稳定，再考虑打开 LDNEB 选项。
    """

    from vasp_learn import dataBase
    initial = dataBase.DataBase().get_atoms_list(
        directory=directory_initial)[-1]
    final = dataBase.DataBase().get_atoms_list(directory=directory_final)[-1]
    neb = self.nebmake(initial=initial,
                       final=final,
                       n_images=n_images,
                       directory=directory_neb,)
    # 需要neb 计算目录中 存在 initial final 目录
    self.after_nebmake(directory_neb=directory_neb,
                       directory_initial=directory_initial,
                       directory_final=directory_final,
                       n_images=n_images)
    self.run(atoms_initial=initial,
             n_images=n_images,
             calc=calc,
             directory=directory_neb,
             only_write_inputs=only_write_inputs,
             **kwargs)

    return neb

  def analysis_neb_wrapper(self,
                           directory='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/SiP_codope/Si_P_3V_Gra_system/P_top/neb',
                           n_images=5,
                           ):
    """包含了画出 neb.pdf 和 原子结构图形
    """
    images = self.get_neb_images(directory=directory, is_OUTCAR=True,
                                 n_images=n_images)
    # 分析
    fname_pdf = self.analysis_neb(directory=directory,
                                  n_images=n_images,)
    data = {'images': images, 'fname_pdf': fname_pdf}
    # 保存 neb 结构图像
    from vasp_learn import dealData
    for index in range(images.__len__()):
      camera_dir_list = [(-0.01, 2, -1), (0, 0, -1), (0, 1, 0)]
      viewname_list = ['oblique', 'top', 'side']
      for camera_dir, viewname in zip(camera_dir_list, viewname_list):
        dealData.DealData().DealDataStructure.ovito_fig().atoms_structure(
            atoms=images[index],
            directory=directory,
            dbname=os.path.basename(directory),
            text2overlay_dict_list=[],
            fname_surfix='_'+str(index)+'_'+viewname,
            camera_dir=camera_dir,
        )

    # 剩下的就是ppt 里面处理 neb.pdf
    return data

  def get_data_coordinate_df_for_TST(self,
                                     directory='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/N_dope_graphene/neb/O_hydrogenation_neb',
                                     images_num_for_TST_list=[0, 1, 4],
                                     substrate_name='N-Gra',
                                     n_images=5,):
    """ 可以弃用 获取过渡态计算中 初态过渡态和末态的 atoms 字典
    """
    ads_name = os.path.basename(directory).split('_')[0]
    ads_name = ads_name.replace('O2H', 'OOH').replace('O2', 'O$_2$')
    images = self.get_neb_images(
        directory=directory,
        is_OUTCAR=True,
        n_images=n_images,
    )
    IS = images[images_num_for_TST_list[0]]
    TS = images[images_num_for_TST_list[1]]
    FS = images[images_num_for_TST_list[2]]
    from py_package_learn.ase_learn import aseLearn
    fa = aseLearn.AseFeatures().Model
    data_df = {}
    for name, atoms in zip(['IS', 'TS', 'FS'], [IS, TS, FS]):
      df = fa.get_df_atoms_position(fname_atoms=None,
                                    atoms=atoms,
                                    is_save_excel=False).round(5)
      df = df.reset_index(names=['atom'])
      df.index += 1
      data_df.update({name: df})

    data_out = {f'The initial state structural coordinates of *{ads_name} hydrogenation on the {substrate_name} substrate': data_df['IS'],
                f'The transition state structural coordinates of *{ads_name} hydrogenation on the {substrate_name} substrate': data_df['TS'],
                f'The final state structural coordinates of *{ads_name} hydrogenation on the {substrate_name} substrate': data_df['FS']
                }
    return data_out

  def get_data_coordinate_df_for_TST_ORR_wrapper(
          self,
          ads_list=['O2', 'O2H', 'O', 'OH'],
          images_num_for_TST_lists=[[0, 1, 4], [0, 1, 4],
                                    [0, 1, 4], [0, 2, 4]],
      n_images_list=[3, 3, 3, 3],
          substrate_name='N-Gra',
          directory='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/N_dope_graphene/neb/O2_hydrogenation_neb',
  ):
    """作为例子参考 
    """

    data_all = {}
    for ads, images_num_for_TST_list, n_images in zip(ads_list, images_num_for_TST_lists, n_images_list):
      l = directory.split('/')
      l[-1] = l[-1].replace('O2', ads)
      directory_new = '/'.join(l)
      data = self.get_data_coordinate_df_for_TST(
          directory=directory_new,
          images_num_for_TST_list=images_num_for_TST_list,
          substrate_name=substrate_name,
          n_images=n_images,
      )
      data_all.update(data)

    return data_all

  # OUTCAR

  def get_part_OUTCAR(self,
                      old_OUTCAR='xx/neb/OH_hydrogenation_neb2/OUTCAR_test',
                      new_OUTCAR='xx/OH_hydrogenation_neb2/OUTCAR_xx',
                      num_of_ionic_step=280,
                      ):
    """neb计算过程中 前面的结果比后面的结果好, 想恢复之前的OUTCAR
    * 之后用 mypaper.CalculationsVasp.TsTCalc.analysis_neb_wrapper() 进行处理
    """
    # 获取 new_OUTCAR 的 内容列表
    import re
    with open(old_OUTCAR, mode='r', encoding='utf8') as f:
      lines = f.readlines()

    newlines = []
    for line in lines:
      newlines.append(line)
      if 'Ionic step' in line:
        result = re.search(r'Ionic step(.*?\d+)\s+', line)
        result = int(result.group(1))
        if result == num_of_ionic_step:
          break

    # 写入文件
    with open(new_OUTCAR, mode='w', encoding='utf8') as f:
      for newline in newlines:
        f.write(newline)
    print(f'写入文件-> {new_OUTCAR}')
    return None

  def get_part_OUTCAR_wrapper(self,
                              old_directory='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/Nn_graphene/O_O_N6_graphene_config1/41C_O_O_N6_graphene_config1/neb/OH_hydrogenation_neb2',
                              new_directory='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/Nn_graphene/O_O_N6_graphene_config1/41C_O_O_N6_graphene_config1/neb/OH_hydrogenation_neb',
                              num_of_ionic_step=200,):

    flist = os.listdir(old_directory)
    n = [int(f) for f in flist if f.startswith('0')]
    n.sort()
    d_image_list = ['0'+str(name) for name in n[1:-1]]
    for d_image in d_image_list:
      self.get_part_OUTCAR(
          old_OUTCAR=os.path.join(old_directory, d_image, 'OUTCAR'),
          new_OUTCAR=os.path.join(new_directory, d_image, 'OUTCAR'),
          num_of_ionic_step=num_of_ionic_step,
      )
    return None

  # deprecated

  def get_nebdata(self, directory):
    """deprecated
    """
    cwd = os.getcwd()
    os.chdir(directory)
    os.system('nebbarrier.pl')
    os.system('nebspline.pl')
    os.chdir(cwd)
    print('获得 neb.dat 和 spline.dat')
    pass

  def plot_neb_fig(self, directory):
    """deprecated
    df1,df2 分别为spline.dat,neb.dat 中的数据
    """
    df1 = pd.read_csv(os.path.join(directory, 'spline.dat'), delimiter=r"\t", names=[
        "images", "distance", "energy", "force"])
    df2 = pd.read_csv(os.path.join(directory, 'neb.dat'), delimiter=r"\s+",
                      names=["a", "b", "c", "d", "e"])
    fig = plt.figure(figsize=(4, 3))
    ax = fig.add_subplot()
    ax.plot(df1["distance"], df1["energy"])
    ax.plot(df2["b"], df2["c"], linestyle="", marker="o")
    ax.set_xlabel(r"Reaction Coordinate ($\AA$)")
    ax.set_ylabel("Relative Energy (eV)")
    fig.savefig(os.path.join(directory, 'neb.pdf'))
    return

  def example_vasp_method(self,
                          directory='Au_diffusion/neb_traditional/',
                          ):
    initial, final = self.example_neb_get_initial_final(
        directory=directory,)
    pass

  def example_neb_get_initial_final(self):
    from vasp_learn import dataBase
    from py_package_learn.ase_learn import aseLearn
    atoms = dataBase.DataBase().get_atoms('Al_bulk')
    atoms = aseLearn.AseFeatures().Model.get_atoms_conventional_or_primitive(
        atoms=atoms)

    slab = ase.build.fcc100('Al', size=(2, 2, 3), a=atoms.cell.lengths()[0])
    ase.build.add_adsorbate(slab, 'Au', 1.7, 'hollow')
    slab.center(axis=2, vacuum=4.0)
    # Fix second and third layers:
    mask = [atom.tag > 1 for atom in slab]
    # print(mask)
    slab.set_constraint(ase.constraints.FixAtoms(mask=mask))
    initial = slab.copy()
    slab[-1].x += slab.get_cell()[0, 0] / 2
    final = slab
    return initial, final

  def example_neb_calc_initial_final(self,
                                     directory='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/Al_110/neb'):
    initial, final = self.example_neb_get_initial_final()
    CalculationsVasp = Calculations()
    CalculationsVasp.calc_general_relaxation(
        directory=os.path.join(directory, 'initial'), atoms=initial, )
    CalculationsVasp.calc_general_relaxation(
        directory=os.path.join(directory, 'final'), atoms=final, )
    return None


class DimerCalc():
  def __init__(self):
    """https://vtstools.readthedocs.io/en/latest/dimer.html
    查看 DIMCAR, 力和力矩都降至1 以下, 曲率为负值
    """
    self.incar_dimer_pars_dict = {
        # Required Parameters
        'ichain': 2,  # Use the dimer method (required for the latest code)
        'ibrion': 3,  # Specify that VASP do MD with a zero time step
        'potim': 0,  # Zero time step so that VASP does not move the ions
        # ---
        'ediff': 1e-6,
        'iopt': 2,  # OPTIMIZER PARAMETERS
        'isym': 0,
        'nsw': 600,
        'lreal': False,
        'lwave': False,
        'lcharg': False,
        'ivdw': None,
        # Standard Parameters¶
        'DdR': 5e-3,  # The dimer separation(twice the distance between images)
        'DRotMax': 4,  # 1	Maximum number of rotation steps per translation step
        'DFNMin': 0.01,  # Magnitude of the rotational force below which the dimer is not rotated
        'DFNMax': 1.0,  # Magnitude of the rotational force below which dimer rotation stops
    }
    pass

  def get_MODECAR(self,
                  atoms_initial: ase.atoms,
                  atoms_final: ase.Atoms,
                  directory,):
    pos_arr = atoms_final.positions - atoms_initial.positions
    fname = os.path.join(directory, 'MODECAR')
    with open(fname, mode='w', encoding='utf-8') as f:
      for line in pos_arr:
        for v in line.tolist():
          f.write(str(v)+' ')
        f.write('\n')
    return None

  def run(self,
          atoms_initial,
          calc,
          directory='xxx/dimer',
          only_write_inputs=True,
          recalc=False,
          **kwargs):
    """* 主要用于产生输入文件
    """
    # calc
    import copy
    calc = copy.deepcopy(calc)  # 如果直接赋值 calculatonvasp.calc 会改变 calc参数
    calc.set(**self.incar_dimer_pars_dict, directory=directory,)
    calc.set(**kwargs)

    from vasp_learn import base
    base.Base().get_inputs_and_compute(directory=directory,
                                       atoms=atoms_initial,
                                       calc=calc,
                                       recalc=recalc,
                                       only_write_inputs=only_write_inputs,)

    return None

  def run_wrapper(self, atoms_initial,
                  atoms_final,
                  calc,
                  directory='xxx/dimer',
                  only_write_inputs=True,
                  recalc=False,
                  **kwargs):
    self.run(atoms_initial=atoms_initial,
             calc=calc,
             directory=directory,
             only_write_inputs=only_write_inputs,
             recalc=recalc,
             **kwargs)
    self.get_MODECAR(atoms_initial=atoms_initial,
                     atoms_final=atoms_final,
                     directory=directory)

    return None

  def run_wrapper_vasp(self,
                       directory_initial,
                       directory_final,
                       calc,
                       only_write_inputs=True,
                       recalc=False,
                       **kwargs,
                       ):
    atoms_initial = ase.io.read(os.path.join(directory_initial, 'OUTCAR'))
    atoms_final = ase.io.read(os.path.join(directory_final, 'OUTCAR'))
    self.run_wrapper(atoms_initial=atoms_initial,
                     atoms_final=atoms_final,
                     calc=calc,
                     only_write_inputs=only_write_inputs,
                     recalc=recalc,
                     **kwargs,)
    return None


class DissolutionPotential():
  def __init__(self) -> None:
    super().__init__()
    self.CalculationsVasp = Calculations()
    self.CalculationsVasp.calc = self.CalculationsVasp.set_basic_calc(
        ivdw=11, kpts=(5, 5, 1), encut=400, ispin=2, )
    r"""参考文章: Oxidation of ethylbenzene to acetophenone with N-doped graphene: Insight from theory
    \cite{greeley2007electrochemical}

    # 目的是重复文章的计算 算算溶解能, 当前只考虑 Au,Pt 111 表面 Fe, Cu的溶解
    """

  def get_bulk(self, name='Au',
               kpts=(9, 9, 9),):
    import ase.build
    atoms = ase.build.bulk(name=name, cubic=True)
    atoms = self.Calculatons.calc_crystal_relax_lc(directory=f'/Users/wangjinlong/my_server/my/myORR_B/bulks/{name}_bulk', atoms=atoms,
                                                   kpts=kpts,
                                                   gamma=True,
                                                   only_write_inputs=False
                                                   )

  def get_slab(self, name='Au',
               position_z_downlim=11,):
    atoms = self.DataBase.get_atoms_list(dbname=f'{name}_bulk')[-1]
    surface = self.GetModel.get_surface(atoms=atoms,
                                        position_z_downlim=position_z_downlim,
                                        atom_symbol_list=[name],
                                        vacuum=7.5)
    surface = self.Calculatons.calc_general_relaxation(
        directory=f'/Users/wangjinlong/my_server/my/myORR_B/slab/{name}111_2x2_system/{name}111_2x2', atoms=surface,
        only_write_inputs=True)
    return surface

  def get_X_on_slab(self,
                    adsorbate_name='Fe',
                    dbname_slab='Au111_2x2',
                    adsorbate_postion_index_list=[12, 13, 14],
                    only_write_inputs=True,):
    atoms = self.Calculatons.wrapper_calc_relax_adsorbate_on_slab(
        pardir=f'/Users/wangjinlong/my_server/my/myORR_B/slab/{dbname_slab}_system/',
        dbname_slab=dbname_slab,
        adsorbate_name=adsorbate_name,
        adsorbate_postion_index_list=adsorbate_postion_index_list,
        height=2,
        only_write_inputs=only_write_inputs,
    )
    return atoms

  def example(self):
    self.get_bulk(name='Ni')
    self.DealData.get_df_chemical_potentials_wrapper(
        rawdata_dict={'Ni': 'Ni_bulk'})
    self.get_X_on_slab(adsorbate_name='Ni',
                       dbname_slab='Pt111_2x2',)
    # 然后提交任务计算
    self.DataBase.write_relaxation2db('Ni_Pt111_2x2')
    self.DataBase.write_relaxation2db('Ni_Au111_2x2')
    self.DealData.DealDataEnergy.get_dissolution_potential_of_A_on_B(
        element_A='Ni',
        element_B='Au',
        shift_dissolution_potential=True)
    pass


class Calculations():
  name = 'Calculations'

  def __init__(self,) -> None:
    """继承该类时, 只需要重新设置 self.calc 即可
    ---
    ase 辅助建立输入文件, 用vasp 参数设置方法进行计算
    """
    super().__init__()
    # incar 的常用设置
    self.incar_sets()
    from vasp_learn import dataBase, dealData, getModel, base
    self.Base = base.Base()
    from py_package_learn.ase_learn import aseLearn
    self.calc = self.set_basic_calc(ivdw=11,
                                    kpts=(3, 3, 1),
                                    ispin=2,
                                    encut=400,
                                    isym=-1,  # 不考虑对称性, 永远是安全的设置，只是速度慢。适用于,畸变、掺杂、表面、分子吸附、NEB、磁性体系
                                    )
    self.DataBase = dataBase.DataBase()
    self.GetModel = getModel.GetModel()
    self.DealData = dealData.DealData()
    self.TsTCalc = NEBCalc()
    self.TsTCalcDimmer = DimerCalc()
    pass

  def convergence_sets(self):
    """https://blog.shishiruqi.com//2019/05/01/scf/
    SCF不收敛尝试以下方法：
    （1）先检查初始几何结构是不是合理，非常离谱的初始结构会导致SCF难收敛。
    （2）检查初始磁矩设置(MAGMOM)是否合理，对于无磁性体系给与默认的磁矩或者高初始磁矩可能会出现Error EDDDAV: Call to ZHEGV failed报错。特殊的磁性排列的体系(AFM, FM)，MAGMOM要设置合理。
    （3）对于DFT+U和ICHARGE=11的任务，添加LMAXMIN=4 (对于d区体系)，添加LMAXMIN=6 (对于f区体系)。
    （4）检查是不是ISTART=1 或 ICHARG = 1读取了不合理的波函数，如果是，rm WAVECAR CHGCAR重新跑。
    （5）更换ALGO，Fast或VeryFast，或Normal。
    （6）对于杂化泛函计算使用ALGO =All，或ALGO=Damped。（此法也可用于 非杂化泛函的计算，SCF收敛以后要读取WAVECAR再用ALGO =Fast或Normal重新收敛一遍）
    （7）尝试使用更大的SIGMA值，如SIGMA=0.5，先粗略收敛，再读取WAVECAR用小的SIGMA计算。(此方法经常奏效，但是读波函数再次用小SIGMA优化有可能碰到仍不收敛的情况。)
    （8）对于非磁性体系（闭壳层ISPIN=1）添加：（注意AMIX和BMIX对收敛有很大影响，可以自己调试）
    AMIX = 0.2
    BMIX = 0.0001 #almost zero, but 0 will crash some versions
    （9）对于磁性体系（自旋极化，ISPIN=2）添加：
    AMIX = 0.2
    BMIX = 0.0001 #almost zero, but 0 will crash some versions
    AMIX MAG = 0.8
    BMIX MAG = 0.0001 #almost zero, but 0 will crash some versions
    (10) 偶极矫正通常会使得SCF变困难，可以把偶极矫正参数LDIPOL，IDIPOL删掉试试。
    (11) 尝试更换不同的ISMEAR。（金属等导体用ISMEAR >= 1，半导体用ISMEAR = 0）
    (12) 提高积分精度，PREC=Accurate，提高辅助格点精度，ADDGRID = .TRUE. 。
    (13) 换用不同K点计算收敛，再读取CHGCAR，用高K点计算。
    (14) 如果在结构优化或者MD过程中，某一步突然不收敛，使用MAXMIX = 50
    (15) 尝试用更小的ENCUT或者更大的ENCUT的预收敛。
    (16) 换更小的赝势或者更soft的赝势。
    """
    pass

  def set_basic_calc(self, **kwargs):
    basic_calc = ase.calculators.vasp.Vasp(xc='pbe',
                                           isym=-1,  # 不考虑对称性, 永远是安全的设置，只是速度慢。适用于,畸变、掺杂、表面、分子吸附、NEB、磁性体系
                                           ispin=2,  # 最好加上
                                           encut=400,
                                           kpts=(1, 1, 1), gamma=True,
                                           ediff=1e-4,  # 好像-4就足够了
                                           ediffg=-5e-2,
                                           symprec=1e-4,
                                           lreal='Auto',
                                           ncore=4,
                                           # 如果你对你的系统没有先验知识，例如，如果你不知道你的系统是绝缘体、半导体还是金属，那么总是使用高斯涂抹ISMEAR=0结合小SIGMA=0.03-0.05。这还不是VASP的默认设置，所以为了安全起见，您可能希望在所有INCAR文件中包含此设置。# 我自己的测试: 对于单原子来说, 小sigma会导致收敛慢, 对能量的影响大, 应该使用相同的sigma值比较两个计算
                                           ismear=0, sigma=0.03,
                                           )
    calc = basic_calc  # 获得基本的计算参数
    calc.set(**kwargs)
    return calc

  def incar_sets(self):
    self.incar_single_point_calc = {'lorbit': 11,
                                    'laechg': True,  # 输出修正核心电荷需要的文件AECCAR0和AECCAR2
                                    }
    # 获得lm-decomposed DOS 的单点计算, 然后进行如下设置可以获得 parchag 也就是STM, 该计算算的很快
    self.incar_partial_charge_densities_calc = {'lpard': True,  # 可以用来获得分电荷密度
                                                'lsepk': False,
                                                'lsepb': False,
                                                'nbmod': -3,
                                                # EINT = -0.1 0.1, 画出STM图
                                                'eint': (-0.1, 0.1),
                                                }

    self.incar_dos_calc_dict = {'lorbit': 11,
                                'icharg': 11,  # ! read CHGCAR file
                                'nedos': 401,    # default 301,  no of points for DOS # 指定态密度图的分辨率也就是多少个点
                                # 'emin': -5,  # 设置能量范围, 相对费米能级之前的
                                # 'emax': 12,
                                }

    self.incar_single_atom_calc = {'ispin': 2,
                                   # magmom=self.get_magmom(chemical_symbols='Pt'),
                                   #  'ismear': 0,
                                   #  'sigma': self.sigma,  # 小sigma会导致收敛慢, 对能量的影响大, 应该使用相同的sigma值比较两个计算
                                   'lorbit': 11,
                                   'kpts': (1, 1, 1),
                                   'gamma': True,
                                   #  'nelm': 100,
                                   # atoms.cell[:] += np.diag([-0.5, 0, 0.5])  # 破坏对称性
                                   'lwave': False,
                                   'lcharg': False,
                                   }

    self.incar_relaxation_crsytal_bulk_lc = {'ibrion': 2,
                                             'isif': 3,
                                             'nsw': 200,
                                             'lorbit': 11,
                                             # 优化晶格常数时, 默认值为1e-5, 太小会出错 VERY BAD NEWS! internal error in subroutine INVGRP: inverse of rotation matrix was not found (increase SYMPREC)
                                             'symprec': 1e-4,
                                             'lwave': False,
                                             'lcharg': False,
                                             }

    self.incar_general_relaxation_dict = {'ibrion': 2,  # 2更稳定. 1 对于graphene 优化快
                                          'isif': 2,
                                          'nsw': 400,
                                          'lorbit': 11,
                                          'potim': 0.1,  # 默认值为0.5, 当初始结构不太好时, 第一步的离子迟豫时, 发现离子跑的距离太远了
                                          'lwave': False,
                                          'lcharg': False,
                                          'ediffg': -5e-2,
                                          }

    self.incar_relaxation_molecular_dict = self.incar_general_relaxation_dict.copy()
    self.incar_relaxation_molecular_dict.update({'kpts': (1, 1, 1)})

    self.incar_frequencies_calc_dict = {'nsw': 1,  # ionic steps > 0
                                        'ibrion': 5,  # calculate second derivatives, Hessian matrix, and phonon frequencies from finite differences
                                        'nfree': 2,  # central differences
                                        'potim': 0.015,  # 0.02 A stepwidth
                                        # calc.set(ivdw=None, ncore=None)  # 频率计算不能有 ncore
                                        'ncore': None,
                                        'ivdw': None,
                                        'npar': None,
                                        'lwave': False,
                                        'lcharg': False,
                                        'prec': 'Accurate',  # is recommended,
                                        }
    self.incar_phonon_dict = copy.deepcopy(
        self.incar_frequencies_calc_dict)  # old
    self.incar_phonon_dispersion_dict = {
        'ibrion': 6,
        'lphon_dispersion': True,
        'lwave': False,
        'lcharg': False,
        'potim': 0.015,
        'ncore': None,
        # 'prec': 'Accurate',  # is recommended
    }
    self.incar_frequencies_calc2_dict = self.incar_frequencies_calc_dict.copy()
    self.incar_frequencies_calc2_dict.update({'ibrion': 8,    # 使用微扰理论计算 perturbation theory
                                              })

    self.incar_ab_MD_dict = {'lreal': 'Auto',    # projection operators in real space
                             'algo': 'VeryFast',  # RMM-DIIS for electronic relaxation
                             'prec': 'Low',     # precision
                             'isym': 0,      # no symmetry imposed
                             'ivdw': 10,
                             'lwave': False,
                             'lcharg': False,
                             # 第一原理参数部分
                             # -------
                             # MD 参数部分
                             'ediff': 1e-3,
                             'ibrion': 0,
                             'nsw': 1000,     # no of ionic steps
                             'potim': 3.0,     # MD time step in fs
                             'mdalgo': 2,     # Nosé-Hoover thermostat
                             'smass': 1.0,     # Nosé mass
                             'tebeg': 2000,     # temperature at beginning
                             'teend': 2000,     # temperature at end
                             'isif': 2,     # update positions; cell shape and volume fixed
                             }

    # ML
    self.MLFF_ab_initio_pars_dict = {'prec': 'low',
                                     'ivdw': 10,
                                     'encut': 300,
                                     'ediff': 1e-6,
                                     'lwave': False,
                                     'lcharg': False,
                                     }
    # 优化晶格常数了
    self.MLFF_md_pars_dict = {'isym': 0,
                              # ! MD (treat ionic degrees of freedom)
                              'ibrion': 0,
                              'nsw': 1000,  # ! no of ionic steps
                              'potim': 2.0,  # ! MD time step in fs
                              'mdalgo': 3,  # ! Langevin thermostat
                              # ! friction  # 以后研究下这两个参数的意义
                              'langevin_gamma': [1],
                              'langevin_gamma_l': 10,  # ! lattice friction
                              'pmass': 10,  # ! lattice mass
                              'tebeg': 400,  # ! temperature
                              'isif': 3,  # ! update positions, cell shape and volume
                              }

    self.MLFF_train_pars_dict = {
        # ase 中没有更新, 故需要 在 ase.calculators.vasp.Vasp 中的父类: GenerateVaspInput 所在的模块中(create_input.py ?) 找到 string_keys (加 'ml_mode'), int_keys (加 'ml_wtsif'), bool_keys (加 ’ml_lmlff') 等 分别添加'ml_lmlff','ml_mode', 'ml_wtsif', 这三个 key
        'ml_lmlff': 'T',  # 开启机器学习力场方法的使用。
        #  'ml_istart': 0,  # 从ab-initio MD中选择训练新力场的模式。
        'ml_mode': 'train',  # 或者用这个
        'ml_wtsif': 2,  # 该标签在机器学习力场方法中为训练数据中的应力缩放设置权值。
        # 确保此示例的可再现性。
        'random_seed': [688344966, 0, 0],
    }
    # 使用机器学习的力场
    self.pars_ML_use_pars_dict = {
        'ml_lmlff': 'T',
        # 'ml_istart': 2,
        # ml_mode= train: 实时训练力场(ML_AB 不必匹配POSCAR): 1. ML_AB (ML_ABN的copy) 不存在则训练新的力场, 2. ML_AB 存在, 读取 ML_AB 的数据产生力场, 并更新力场
        # ml_mode= select:重新选择本地参考配置(ML_AB), 训练力场(我猜测对于相同的ML_AB, 对于两次训练可能会得到有些差异的力场ML_FFN)
        # ML_MODE = refit:为“快速”评估改装力场. 如果训练的力场在适用性和残余误差方面符合您的期望时, 在力场应应用于仅预测的MD运行之前需要最后一步:为快速预测模式进行改装。再次将最终数据集复制到ML_AB,ML_MODE = refit, 运行VASP将创建一个新的ML_FFN，最终可以用于生产。
        # ml_mode=run: 只执行力场预测
        'ml_mode': 'run',  # 只执行力场预测 cp ML_FFN ML_FF 到MD运算目录 然后 ml_mode=run 开始MD。
        'random_seed': [688344966, 0, 0],
    }

    # 表面有吸附物时, 考虑偶极修正
    self.pars_dipol_dict = {'ldipol': True,
                            'idipol': 3}

    # 参考 VaspSol()
    # 在 ase.calculators.vasp.create_input.py 中的  float_keys 中添加 'lambda_dk', 即可
    self.pars_solvent_effect_dict = {'lsol': True,  # 溶剂化模型控制开关
                                     'eb_k': 78.4,  # 溶剂的相对介电常数可以从水的默认值78.4改为其它
                                     'tau': 0,
                                     'lambda_dk': 3.0,
                                     'lrhoion': False,  # write ioniccharge density 产生 rhoion 文件, 该文件较大
                                     'nelm': 60,  # 电子迟豫, sol_eff 较难收敛 故增大
                                     #  'lwave': False, # 保留 wavecar 下次计算收敛的更快, 或者
                                     #  'lcharg': False,
                                     'laechg': False,  # 输出修正核心电荷需要的文件AECCAR0和AECCAR2, 这些文件太大了
                                     }

    self.electro_dict = """"
    System=11
    ENCUT=500
    ISTART=1 # job : 0-new 1-cont 2-samecut
    ICHARG=0 # charge: 1-file 2-atom 10-const
    EDIFF =0.1E-04 # stopping-criterion for ELM(for large system setting 0.
    1E-03)
    EDIFFG=-0.01
    ISMEAR=-5
    PREC= A # medium, high low
    LPARD= TRUE
    IBAND=25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64
    KPUSE=45
    LSEPB =.TRUE.
    LSEPK =.TRUE.
    NGX=30
    NGY=30
    NGZ=80
    LPLANE=.TURE.
    NSIM=4
    LSCALU=.FALSE.
    ISPIN=2
    NBANDS=64"""

    self.electronic_field_dict = {'efield': 0.3,
                                  'ldipol': True,
                                  'idipol': 3,  # 1,2,3
                                  }

  # @jobflow.job
  def calc_universal(self, atoms, incar_sets_dict,
                     directory='.',
                     recalc=False,
                     only_write_inputs=True,
                     **kwargs):
    """通用计算
    """

    calc = copy.deepcopy(self.calc)
    calc.set(**incar_sets_dict)
    calc.set(**kwargs)
    atoms = self.Base.get_inputs_and_compute(directory, atoms=atoms,
                                             calc=calc,
                                             recalc=recalc,
                                             only_write_inputs=only_write_inputs,)

    return atoms

  def calc_single_atom(self, symbol,
                       directory='/Users/wangjinlong/my_server/my/myORR_B/isolated_atoms/xx_atoms',
                       dbname=None,
                       only_write_inputs=True,
                       recalc=False,
                       charge=0,  # 考虑体系是否带电, 为负值表示带负电
                       **kwargs):
    """计算单原子能量
    symbol='Pt'
    """

    atoms = ase.Atoms(symbols=symbol, pbc=True, )
    atoms.center(5)
    atoms.cell += np.diag([-0.5, 0, 0.5])
    # calc
    calc = copy.deepcopy(self.calc)
    calc.set(**self.incar_single_atom_calc, directory=directory,
             #  magmom=[Base().get_magmom(chemical_symbols=symbol)]
             charge=charge,
             )
    calc.set(**kwargs)
    # compute
    atoms = self.Base.get_inputs_and_compute(directory=directory,
                                             atoms=atoms,
                                             calc=calc, recalc=recalc,
                                             only_write_inputs=only_write_inputs)
    # db 不论是否计算完成都写入 db, 计算完成后会更新db
    self.DataBase.db_write_and_update(atoms=atoms,
                                      directory=os.path.abspath(directory),
                                      dbname=dbname)
    return atoms

  def calc_molecular_relax(self, directory, atoms=None, dbname=None,
                           recalc=False, only_write_inputs=True, **kwargs):
    """迟豫 molecular

    Args:
        atoms (_type_): 可以通过 atoms = ase.build.molecule(name='O2',pbc=True, vacuum=5)
        directory (_type_): _description_
        recalc (bool, optional): _description_. Defaults to False.
        only_write_inputs (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """

    # atoms 对象可以通过 atoms = ase.build.molecule(name='O2',pbc=True, vacuum=5)
    # calc set
    calc = copy.deepcopy(self.calc)
    calc.set(**self.incar_relaxation_molecular_dict)
    calc.set(**kwargs)
    # compute
    atoms = self.Base.get_inputs_and_compute(directory=directory, atoms=atoms, calc=calc,
                                             only_write_inputs=only_write_inputs,
                                             recalc=recalc,)

    # db 不论是否计算完成都写入 db, 计算完成后会更新db
    self.DataBase.db_write_and_update(atoms=atoms,
                                      directory=os.path.abspath(directory),
                                      dbname=dbname)
    return atoms

  def calc_crystal_relax_lc(self, directory,
                            atoms=None,
                            dbname=None,
                            only_write_inputs=True, recalc=False,
                            kpts={'density': 2.5, 'gamma': True},
                            **kwargs):
    """如果only_write_inputs=True, 可以不设置 atoms, 即None
    ISIF =2 只驰豫原子位置

    Args:
        atoms (ase.Atoms): _description_
        directory (_type_): _description_
        only_write_inputs (bool, optional): _description_. Defaults to False.
        recalc (bool, optional): _description_. Defaults to False.
        kpts (dict, optional):  Defaults to {'density': 2.5, 'gamma': True}, MP with a minimum density of 2.5 points/Ang^-1 include gamma-point.

    Returns:
        _type_: _description_
    """
    calc = copy.deepcopy(self.calc)
    calc.set(**self.incar_relaxation_crsytal_bulk_lc)
    calc.set(kpts=kpts)
    if kwargs:
      calc.set(**kwargs)

    atoms = self.Base.get_inputs_and_compute(directory=directory, atoms=atoms,
                                             calc=calc, recalc=recalc, only_write_inputs=only_write_inputs)
    # db 不论是否计算完成都写入 db, 计算完成后会更新db
    if only_write_inputs:
      self.DataBase.db_write_and_update(atoms=atoms,
                                        directory=os.path.abspath(directory),
                                        dbname=dbname)
    else:
      self.DataBase.write_relax_2db(directory_relax=directory,
                                    dbname=None)
    return atoms

  # @jobflow.job
  def calc_general_relaxation(self, directory, atoms=None,
                              only_write_inputs=True,
                              recalc=False,
                              dbname=None,
                              charge=0,  # 考虑体系是否带电
                              **kwargs):
    """ # 对于ORR 先确定 O2, O, H 的最稳定吸附, 然后再去确定O2H 和 OH 
    如果已经存在目录可以不设置 atoms, 即None
    ISIF =2 只驰豫原子位置

    #离子弛豫的收敛速度，有三个很大的影响因素：弛豫方法（IBRION）,步长（POTIM）和收敛判据（EDIFFG）.

    Args:
        atoms (ase.Atoms): _description_
        directory (_type_): _description_
        recalc (bool, optional): _description_. Defaults to False.
        only_write_inputs (bool, optional): _description_. Defaults to False.

    Returns: atoms
        _type_: _description_
    """
    # calc
    calc = copy.deepcopy(self.calc)
    calc.set(**self.incar_general_relaxation_dict,
             charge=charge,)
    calc.set(**kwargs)

    # compute
    atoms = self.Base.get_inputs_and_compute(directory=directory,
                                             atoms=atoms,
                                             calc=calc, recalc=recalc,
                                             only_write_inputs=only_write_inputs)

    # db 不论是否计算完成都写入 db, 计算完成后会更新db
    if only_write_inputs:
      self.DataBase.db_write_and_update(atoms=atoms,
                                        directory=os.path.abspath(directory),
                                        dbname=dbname)
    else:
      self.DataBase.write_relax_2db(
          directory_relax=os.path.abspath(directory),
          dbname=dbname)

    return atoms

  def calc_relax_2dimention_material_graphene_example(self, directory='graphene',
                                                      only_write_inputs=True, recalc=False,):
    """对于二维材料我们并不希望在真空层的方向优化, 需要增加 OPCELL, 当然vasp也需要相应的编译
    编译参考: https://blog.shishiruqi.com//2019/05/05/constr/

    Args:
        directory (str, optional): _description_. Defaults to 'graphene'.

    Returns:
        _type_: _description_
    """
    atoms = ase.build.graphene(vacuum=7.5)
    atoms.pbc = True
    # 对于二维材料我们并不希望在真空层的方向优化, 需要增加 OPCELL, 当然vasp也需要相应的编译
    self.Base.get_optcell(directory=directory,
                          optcell_lines=['100', '110', '000'])

    atoms: ase.Atoms = self.calc_crystal_relax_lc(atoms=atoms, directory=directory, kpts=(8, 8, 1),
                                                  only_write_inputs=only_write_inputs, recalc=recalc)
    # db
    if not only_write_inputs:
      directory = os.path.abs(directory)
      dbname = os.path.basename(directory)
      self.DataBase.db_write_and_update(atoms=atoms,
                                        directory=directory,
                                        dbname=dbname)
    return atoms

  def calc_relax_2dimention_material(self, atoms: ase.Atoms,
                                     directory,
                                     only_write_inputs=True,
                                     recalc=False,
                                     **kwargs):
    """对于二维材料我们并不希望在真空层的方向优化, 需要增加 OPCELL, 当然vasp也需要相应的编译
    编译参考: https://blog.shishiruqi.com//2019/05/05/constr/

    Args:
        directory (str, optional): _description_. Defaults to 'graphene'.

    Returns:
        _type_: _description_
    """

    # 对于二维材料我们并不希望在真空层的方向优化, 需要增加 OPCELL, 当然vasp也需要相应的编译
    self.Base.get_optcell(directory=directory,
                          optcell_lines=['100', '110', '000'])

    atoms: ase.Atoms = self.calc_crystal_relax_lc(atoms=atoms, directory=directory,
                                                  only_write_inputs=only_write_inputs,
                                                  recalc=recalc, **kwargs)
    # db
    if not only_write_inputs:
      directory = os.path.abspath(directory)
      dbname = os.path.basename(directory)
      self.DataBase.db_write_and_update(atoms=atoms,
                                        directory=directory,
                                        dbname=dbname)
    return atoms

  def calc_dos(self, atoms, directory, recalc=False,
               only_write_inputs=True,  **kwargs):
    """dos计算，增大k点，

    Args:
        atoms (_type_): _description_
        directory (_type_): _description_
        recalc (bool, optional): _description_. Defaults to False.
        only_write_inputs (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    atoms = self.calc_single_point(atoms=atoms,
                                   directory=directory,
                                   recalc=recalc,
                                   only_write_inputs=only_write_inputs,)
    # dos calcu
    calc = copy.deepcopy(self.calc)
    calc.set(**self.incar_dos_calc_dict, directory=directory,)
    calc.set(**kwargs)
    atoms.calc = calc
    atoms = self.Base.get_inputs_and_compute(directory=directory, atoms=atoms,
                                             calc=calc,
                                             recalc=recalc,
                                             only_write_inputs=only_write_inputs,)
    return atoms

  def calc_ab_MD_with_MLFF(self, atoms: ase.Atoms,
                           directory, recalc=False,
                           only_write_inputs=True,
                           ml_mode='train',
                           **kwargs,):
    """第一原理分子动力学, 要设置 tebeg=1000, teend=1000,ivdw=10,kpts=(1,1,1),ediffg=None,ediff=1e-4
    ml_mode='train' or 'run'

    训练完成后保存 ML_ABN -> ML_AB, ML_FFN -> ML_FF 这样可以用于产生力场

    Args:
        atoms (ase.Atoms): _description_
        directory (_type_): _description_
        recalc (bool, optional): _description_. Defaults to False.
        only_write_inputs (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    # calc
    calc = copy.deepcopy(self.calc)
    calc.set(**self.incar_ab_MD_dict)
    calc.set(**self.MLFF_train_pars_dict)
    calc.set(ml_mode=ml_mode)  # 默认是'train', 也可以设置为run
    calc.set(**kwargs)
    # compute
    atoms = self.Base.get_inputs_and_compute(directory=directory,
                                             atoms=atoms,
                                             calc=calc, recalc=recalc,
                                             only_write_inputs=only_write_inputs)
    if not only_write_inputs:
      # 训练完成后保存 ML_AB 这样可以用于产生力场
      directory_abs = os.path.abspath(directory)
      for file in ['ML_ABN', 'ML_FFN']:
        src = os.path.join(directory_abs, file)
        dst = os.path.join(directory_abs, file[:-1])
        shutil.copy(src=src, dst=dst)

    return

  def calc_ab_MD_with_MLFF_wrapper(self,
                                   dbname=None,
                                   directory_relax=None,
                                   ml_mode='train',
                                   nsw=10000,
                                   potim=3,
                                   ivdw=12,
                                   temp=1000,
                                   ediff=1e-3,  # -4
                                   kpts=(1, 1, 1),
                                   only_write_inputs=True,
                                   recalc=False,
                                   ):
    """directory_relax, dbname 给定一个就可以了
    * ivdw=12, 专为层状材料, 13 也可以, 20 最新的方法.
    - potim=3: 时间步长
    - 使用DealData.get_fig_ab_md_wrapper() 进行分析

    Args:
        directory_relax (_type_): _description_
        ml_mode (str, optional): _description_. Defaults to 'train'.
        nsw (int, optional): _description_. Defaults to 1000.
        potim (int, optional): _description_. Defaults to 3.
        ivdw (int, optional): _description_. Defaults to 12.
        temp (int, optional): _description_. Defaults to 1000.
        ediff (_type_, optional): _description_. Defaults to 1e-4.
        only_write_inputs (bool, optional): _description_. Defaults to False.
        recalc (bool, optional): _description_. Defaults to False.
    """

    directory_relax, dbname = self.DataBase.choice_directory_dname(
        directory=directory_relax,
        dbname=dbname)
    atoms = self.DataBase.get_atoms_list(dbname=dbname,)[-1]
    # 由于ml_mode = 'run' 时 会意外结束
    directory = os.path.join(directory_relax, 'ab_md')
    self.calc_ab_MD_with_MLFF(atoms=atoms,
                              directory=directory,
                              recalc=recalc,
                              only_write_inputs=only_write_inputs,
                              nsw=nsw,
                              potim=potim,
                              tebeg=temp, teend=temp,
                              ivdw=ivdw,
                              kpts=kpts,
                              ediffg=None,
                              ediff=ediff,
                              ml_mode=ml_mode,)
    return None

  def calc_lobster_wrapper(self,
                           dbname=None,
                           directory_relax=None,
                           directory_lobster=None,
                           atom_index_list=[[71, 29],
                                            [71, 31],
                                            [71, 42]],
                           only_write_inputs=True,
                           recalc=False,
                           incar_pars_dict={}):
    """* dbname|directory_relax
    * 详细参见 LobsterLearn().calc_lobster_wrapper

    Args:
        dbname (_type_, optional): _description_. Defaults to None.
        directory_relax (_type_, optional): _description_. Defaults to None.
        atom_index_list (list, optional): _description_. Defaults to [[71, 29], [71, 31], [71, 42]].
        xlim (list, optional): _description_. Defaults to [-2, 2].
        ylim (list, optional): _description_. Defaults to [-10, 5].
        xlim_icohp (list, optional): _description_. Defaults to [0, 8].
        legend_loc (str, optional): _description_. Defaults to 'best'.
        line_label_list (_type_, optional): _description_. Defaults to None.
        only_write_inputs (bool, optional): _description_. Defaults to True.
        recalc (bool, optional): _description_. Defaults to False.
        incar_pars_dict (dict, optional): _description_. Defaults to {}.

    Returns:
        _type_: _description_
    """

    directory_relax, dbname = self.DataBase.choice_directory_dname(
        directory=directory_relax,
        dbname=dbname)
    from lobster_learn.lobsterLearn import LobsterLearn
    LobsterLearn().calc_lobster_wrapper(
        directory_relax=directory_relax,
        directory_lobster=directory_lobster,
        atom_index_list=atom_index_list,
        only_write_inputs=only_write_inputs,
        recalc=recalc,
        incar_pars_dict=incar_pars_dict)
    return None

  def calc_phonons_dispersion(self, atoms,
                              directory='xxx/phonon_dispersion',
                              kpts=(3, 3, 3),
                              path_str='GXG',
                              npoints=40,
                              only_write_inputs=True,
                              recalc=False,
                              **kwargs):
    """KeyError: 'name'
    这个错误以后去解决, 不影响计算 
    """
    calc = copy.deepcopy(self.calc)
    calc.set(kpts=kpts)
    calc.set(**self.incar_phonon_dispersion_dict,)
    calc.set(**kwargs)
    self.Base.get_inputs(directory=directory,
                         atoms=atoms,
                         calc=calc)
    # 产生 QPOINTS 文件
    self.Base.get_line_mode_KPOINTS(atoms=atoms,
                                    path_str=path_str,
                                    npoints=npoints,
                                    fname=os.path.join(directory, 'QPOINTS'))

    # calc
    if only_write_inputs:
      pass
    else:
      atoms = self.Base.get_compute(atoms=atoms,
                                    directory=directory,
                                    recalc=recalc)
    return atoms

  def calc_dft_plus_U(self):
    """
    # LDAU = .TRUE.
    # LDAUTYPE = 2
    # LDAUL =   2  -1   -1   -1  -1
    # LDAUU =  4.6 0.0  0.0 0.0 0.0
    # LDAUJ =  0.4 0.0  0.0 0.0 0.0
    # LDAUALPHA = 0.0 0.5
    # LDAUPRINT = 2
    # LMAXMIX = 4
    """
    pass

  def calc_elastic_moduli(self):
    """INCAR设置
    NSW = 1
    EDIFFG=-1e-3
    ISIF=3
    IBRION=6 #计算弹性常数
    POTIM=0.015
    NFREE = 4

    2. 查看OUTCAR得到弹性刚度矩阵 关键词: TOTAL ELASTIC MODULI (kBar)
    3. 单位转换
    1 kBar = 1e-1 GPa
    value = 123 # e.g.123
    Bar = 1e+5 # Pa
    GPa = 1e+9 #Pa
    kBar = 123 * 1e+3 * 1e+5 /1e+9  # Gpa
    # kBar = 12.3 Gpa
    """
    # ELASTIC MODULI
    pass

  def calc_parchg_STM(self, atoms, directory,
                      only_write_inputs=True,
                      ):
    atoms = self.calc_single_point(atoms=atoms, directory=directory,
                                   only_write_inputs=only_write_inputs,)
    # STM
    directory_STM = os.path.join(directory, 'STM')
    calc = copy.deepcopy(self.calc)
    calc.set(**self.incar_partial_charge_densities_calc,
             directory=directory_STM)
    atoms.calc = calc
    atoms = self.Base.get_inputs_and_compute(directory=directory_STM, atoms=atoms,
                                             calc=calc,
                                             only_write_inputs=True,)
    print(f'all done. 用parchg 绘图,directory=\n{directory_STM}')
    pass

  def calc_single_point(self, atoms: ase.Atoms,
                        directory='xxx/single_point',
                        recalc=False,
                        only_write_inputs=True,
                        **kwargs):
    """ 对于有些体系例如H2, ispin=2 反而会出错, 对于一个O原子要多进行多次单点计算--> 好烦, 增加k点2次就行了
    包含了 bader 分析的数据 ACECAR0

    Args:
        atoms (_type_): _description_
        directory (_type_): _description_
        recalc (bool, optional): _description_. Defaults to False.
        only_write_inputs (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    calc = copy.deepcopy(self.calc)
    calc.set(**self.incar_single_point_calc, directory=directory,)
    calc.set(**kwargs)
    atoms.calc = calc
    atoms = self.Base.get_inputs_and_compute(directory, atoms=atoms,
                                             calc=calc,
                                             recalc=recalc,
                                             only_write_inputs=only_write_inputs,)

    return atoms

  def calc_single_point_wrapper(self, dbname=None,
                                directory_relax=None,
                                only_write_inputs=True,
                                recalc=False,
                                **kwargs):
    """给出 dbnmae 或者 directory_relax 就可以计算单点了

    Args:
        directory_relax (_type_): _description_
        only_write_inputs (bool, optional): _description_. Defaults to False.
        recalc (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """

    directory_relax, dbname = self.DataBase.choice_directory_dname(
        directory=directory_relax,
        dbname=dbname)
    # 获取迟豫中的计算参数
    calc = ase.calculators.vasp.Vasp(
        directory=directory_relax, restart=True)
    if 'kpts' in kwargs.keys():
      kpts = kwargs['kpts']
      kwargs.pop('kpts')
    else:
      kpts = calc.parameters['kpts']
    gamma = calc.parameters['gamma']

    # 单点计算产生 WAVECAR
    directory_sp = os.path.join(directory_relax, 'single_point')
    if not only_write_inputs:
      print(f'开始计算单点... -> {directory_sp}')
    atoms = self.calc_single_point(atoms=calc.get_atoms(),
                                   directory=directory_sp,
                                   recalc=recalc,
                                   only_write_inputs=only_write_inputs,
                                   gamma=gamma,
                                   kpts=kpts,
                                   **kwargs)
    if only_write_inputs:
      pass
    else:
      self.DataBase.write_single_point_2db(dbname=dbname,
                                           directory_relax=directory_relax)
    return atoms

  def get_charge_for_electrode_potential(self,
                                         atoms: ase.Atoms,
                                         delta_V=-0.62,
                                         ):
    """* 根据电容估算, 某个电压下所需要的电荷量, 不一定对, 以后验证
    * 例子:
    - a = atoms.cell[0][0] * 1e-10
    - area = a*a*np.sin(1/3*np.pi)

    正阳氧, 负阴还
    Args:
        area (_type_): _description_
        d (_type_, optional): _description_. Defaults to 15*1e-10.
    """

    from scipy import constants

    def get_capacitance(area, d):
      """获得电容 都使用国际电位

      Args:
          area (_type_): _description_
          d (_type_): _description_

      Returns:
          _type_: _description_
      """
      capacitance = constants.epsilon_0 * area/d
      return capacitance

    area = self.Base.get_surface_area(atoms=atoms)
    d = atoms.cell.cellpar()[2]
    capacitance = get_capacitance(area=area*1e-20, d=d*1e-10)
    # 对于还原电极需要加电子
    delta_Q = capacitance * delta_V
    charge = delta_Q/constants.elementary_charge
    return charge

  def calc_general_relax_plus_electrode_potential(self, dbname='As_N4_DVG',
                                                  delta_V=-0.14,
                                                  pardir='xxx',
                                                  only_write_inputs=True,
                                                  **kwargs,):
    """根据电容估算, 某个电压下所需要的电荷量, 不一定对, 以后验证

    Args:
        dbname (str, optional): _description_. Defaults to 'As_N4_DVG'.
        delta_V (float, optional): _description_. Defaults to -0.14.
        pardir (str, optional): _description_. Defaults to 'xxx'.
        only_write_inputs (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """

    # 获得某个电压下阴极额外需要的电子
    atoms = self.DataBase.get_atoms_list(dbname=dbname)[-1]
    charge = self.get_charge_for_electrode_potential(atoms=atoms,
                                                     delta_V=delta_V)
    # 计算
    directory = os.path.join(pardir, dbname) + str(delta_V)+'V'
    atoms = self.calc_general_relaxation(atoms=atoms,
                                         directory=directory,
                                         charge=charge,
                                         only_write_inputs=only_write_inputs,
                                         **kwargs,
                                         )
    return atoms

  def calc_sol_eff(self, atoms,
                   directory,
                   only_write_inputs=True,
                   recalc=False,
                   **kwargs):
    """* WARNING: Sub-Space-Matrix is not hermitian in DAV
    - 出错时, ALGO=Fast|VeryFast|Subrot|Damped|Conjugate
    Eigenval 这个不行
    NELMDL = 12 for ALGO =VeryFast

    必须保证有WAVECAR 存在且不为空, 才能计算出正确的sol_eff
    directory='xxx/sol_eff', 写入db, name = xxx-sol_eff
    slab 体系和 gas 分子考虑溶剂化效应后势能都是不同的
    我测试了 Pt111_surface_2x2_test 先计算单点在有wavecar的情况下考虑溶剂效应
    与直接考虑溶剂效应进行单点计算的体系能量结果是一样的, 而且也不影响bader分析的结果, 以后再验证一个OH的吸附

    溶剂化能计算流程 https://www.bilibili.com/video/BV1ts4y167tr/?spm_id_from=333.337.search-card.all.click&vd_source=5ec84b7f759de5474190c5f84b86a564
    1.在真空中进行结构优化，进行静态计算设置 LWAVE=.TRUE.保存波函数文件WAVECAR，OSZICAR中读取真空下能量E.Vac2打开LSOL=.TRUE.，设置ISTART=1读取真空静态计算波函数，进行隐式溶剂下能量计算， OSZICAR中读取溶剂环境下能量E两能量作差得到溶剂化能Eso- Evac.   slab 体系和真空中的分子都可以计算溶剂化能   迟豫的时候也可以考虑溶剂化效应, 但要保证结构的改变比较小且是有意义的, J. Chem. Phys. 2014, 140, 084106 and J. Chem.Phvs.2019.151.234101

    第一步: 要有波函数, 单点计算
    第二步: 打开溶剂化模型，输入溶剂介电常数

    LSOL: TRUE # switch on solvation model
    EB_K=78.4 # relative permittivity of the bulk solvent
    SIGMA_K=0.600000 # width of the dielectric cavity
    NC_K=0.002500 #  cutoff charge density which determines theelectronic density value at which the cavityis formed
    TAU =0.000525 # cavity surface tension which describes thenon-electrostatic interactions # 建议设置为 0
    LAMBDA_DK=3.0 # Debye length in Angstroms which is related with ionic concentration and their valence
    LRHOB = TRUE # write boundcharge density in the CHGCAR format
    LRHOION=TRUE # write ioniccharge density to visualize theionic charge distribution


    Args:
        atoms (_type_): _description_
        directory (str): _description_
        recalc (bool, optional): _description_. Defaults to False.
        only_write_inputs (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """

    calc = copy.deepcopy(self.calc)
    calc.set(**self.incar_single_point_calc, directory=directory,)
    calc.set(**self.pars_solvent_effect_dict)
    calc.set(**kwargs)
    atoms = self.Base.get_inputs_and_compute(directory,
                                             atoms=atoms,
                                             calc=calc,
                                             recalc=recalc,
                                             only_write_inputs=only_write_inputs,)

    return atoms

  def calc_sol_eff_wrapper(self, dbname=None,
                           directory_relax=None,
                           only_write_inputs=True,
                           recalc=False,
                           **kwargs):
    """only_write_inputs=True, 包含了写入db: energy_sol_eff
    先进性单点计算, 该计算是在relax目录中建立 sol_eff
    # 该目录中需要有单点的WAVCAR, 我在提交任务的时候自动复制了single_point 中的WAVECAR

    Args:
        directory_relax (_type_): _description_
        only_write_inputs (bool, optional): _description_. Defaults to False.
        recalc (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """

    directory_relax, dbname = self.DataBase.choice_directory_dname(directory=directory_relax,
                                                                   dbname=dbname)
    directory_sol_eff = os.path.join(directory_relax, 'sol_eff')
    if not os.path.exists(directory_sol_eff):
      os.makedirs(directory_sol_eff, exist_ok=True)
    else:  # copy WAVECAR
      # 我已经在 serverUse.HPC().qsub_batch 内部加入了从single_point/WAVECAR 拷贝到sol_eff 目录
      if not os.path.exists(os.path.join(directory_sol_eff, 'WAVECAR')):
        directory_sp = os.path.join(directory_relax, 'single_point')
        file_wavecar = os.path.join(directory_sp, 'WAVECAR')
        # shutil.copy(file_wavecar, directory_sol_eff)
        pass

    # 读取获取迟豫中的计算参数
    calc = ase.calculators.vasp.Vasp(
        directory=directory_relax, restart=True)
    kpts = calc.parameters['kpts']
    gamma = calc.parameters['gamma']
    # 计算
    if not only_write_inputs:
      print(f'开始计算sol_eff... ->{directory_sol_eff}')
    atoms = self.calc_sol_eff(atoms=calc.get_atoms(),
                              directory=directory_sol_eff,
                              only_write_inputs=only_write_inputs,
                              recalc=recalc,
                              gamma=gamma,
                              kpts=kpts,
                              **kwargs)
    # db
    if only_write_inputs:
      pass
    else:
      self.DataBase.write_sol_eff2db(directory_relax=directory_relax)

    return atoms

  def calc_frequency(self, atoms,
                     directory,
                     only_write_inputs=True,
                     recalc=False,
                     is_sol_eff=False,
                     **kwargs):
    """仅仅是计算频率
    vasp的频率计算 需要使用优化之后的结构计算频率
    我的测试发现 sol_eff 对 zpe 和 S 的影响较小 < 0.02 eV, 对总能的影响较大, 所以频率计算可以不考虑 sol_eff
    **kwargs 是用来增加一些额外的计算参数的

    要计算液态水分子的能量 = 0.035bar=3500 pa  压力下的气态水分子的能量 1bar =10^5 pa
    https://www.bilibili.com/video/av67721985/?vd_source=5ec84b7f759de5474190c5f84b86a564

    # SHE 中OER 反应的吸热 -4.92 eV
    G(O2) 不能直接计算 vasp算的不准。  2G(H2O) - 2G(H2) - G(O2) = -4.92 eV
    O2的自由能要这样算: G(O2) = 2G(H2O) - 2G(H2) + 4.92

    Args:
        atoms (_type_): _description_
        db_name (_type_): _description_
        directory (_type_): xxx/vibration
        recalc (bool, optional): _description_. Defaults to False.
        only_write_inputs (bool, optional): _description_. Defaults to False.
        method (str, optional): _description_. Defaults to 'vasp'.
        indices_ase_method (list, optional): _description_. Defaults to [0, 1].

    Returns: atoms
        _type_: _description_
    """

    if atoms.__len__() == 1:
      print(f'只有一个原子, 原子不会振动也没有零点能')
      return atoms
    else:
      # calc
      calc = copy.deepcopy(self.calc)
      calc.set(**self.incar_frequencies_calc_dict, directory=directory)
      if is_sol_eff:
        calc.set(**self.pars_solvent_effect_dict)
      calc.set(**kwargs)
      # compute
      atoms = self.Base.get_inputs_and_compute(
          directory=directory, atoms=atoms, calc=calc, recalc=recalc, only_write_inputs=only_write_inputs)

      return atoms

  def calc_frequency_ase_method(self, atoms, directory,
                                recalc=False,
                                indices_ase_method=[0, 1]):
    """需要使用优化之后的结构计算频率 ase 方法

    Args:
        atoms (_type_): _description_
        directory (_type_): _description_
        recalc (bool, optional): _description_. Defaults to False.
        indices_ase_method (list, optional): _description_. Defaults to [0, 1].

    Returns: vib_data
        _type_: _description_
    """

    if atoms.__len__() == 1:
      print(f'只有一个原子, 原子不会振动也没有零点能')
      return atoms

    calc = ase.calculators.vasp.Vasp(directory=directory)
    from py_package_learn.ase_learn import aseLearn

    vib_data = aseLearn.AseFeatures().AseLearn.calc_frequency_and_get_vib_data(atoms=atoms,
                                                                               calc=calc,
                                                                               indices=indices_ase_method,
                                                                               directory=directory,
                                                                               recalc=recalc)
    return vib_data

  def calc_frequency_adsorbate(self,
                               dbname=None,
                               directory_relax=None,
                               only_write_inputs=True,
                               pressure=101325,
                               recalc=False,
                               kpts=(1, 1, 1),  # 计算的是气体分子
                               ):
    """同时把热力学数据写入 db

    Args:
        directory_relax (_type_): _description_
        only_write_inputs (bool, optional): _description_. Defaults to True.
        recalc (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """

    directory_relax, dbname = self.DataBase.choice_directory_dname(directory=directory_relax,
                                                                   dbname=dbname)

    atoms = ase.io.read(os.path.join(directory_relax, 'OUTCAR'))
    directory_vibration = os.path.join(directory_relax, 'vibration')
    self.calc_frequency(atoms=atoms,
                        directory=directory_vibration,
                        recalc=recalc,
                        only_write_inputs=only_write_inputs,
                        is_sol_eff=False,
                        kpts=kpts,  # 计算的是气体分子
                        )

    # db
    if only_write_inputs:
      pass
    else:
      thermodata = self.DataBase.write_thermodata2db(
          directory_relax=directory_relax,
          system='adsorbate',
          temperature=300,
          pressure=pressure,)

    return None

  def calc_frequency_bulk(self,
                          dbname=None,
                          directory_relax=None,
                          only_write_inputs=True,
                          pressure=101325,
                          recalc=False,
                          kpts=(7, 7, 7)):
    self.calc_frequency_adsorbate(dbname=dbname,
                                  directory_relax=directory_relax,
                                  only_write_inputs=only_write_inputs,
                                  pressure=pressure,
                                  recalc=recalc,
                                  kpts=kpts,)
    return None

  def calc_frequency_adsorbate_on_slab(self,
                                       directory_relax=None,
                                       dbname=None,
                                       atom_symbol_list=['O', 'H'],
                                       atom_index_list=None,
                                       check_mask=True,
                                       only_write_inputs=True,
                                       recalc=False,
                                       is_sol_eff=False,
                                       **kwargs,):
    """计算频率并将 thermodata 写入db
    """

    directory_relax, dbname = self.DataBase.choice_directory_dname(
        directory=directory_relax,
        dbname=dbname)
    # 计算热化学量
    atoms = ase.io.read(os.path.join(directory_relax, 'OUTCAR'))
    index_list, symbol_list = self.Base.get_index_list_and_symbol_list(
        atoms=atoms,
        index_list=atom_index_list,
        symbol_list=atom_symbol_list)
    unmask = index_list
    mask = [atom.index for atom in atoms if atom.index not in unmask]  # 衬底
    atoms = self.Base.set_selective_dynamics(atoms=atoms, mask=mask)  # 固定衬底
    if check_mask:
      print(f'请确认迟豫的N原子索引->{unmask} 是否正确, 然后设置 check_mask=False')
      return atoms
    else:
      directory_vibration = os.path.join(directory_relax, 'vibration')
      if not only_write_inputs:
        print(f'开始计算vib... ->{directory_vibration}')
      atoms = self.calc_frequency(atoms=atoms,
                                  directory=directory_vibration,
                                  only_write_inputs=only_write_inputs,
                                  recalc=recalc,
                                  is_sol_eff=is_sol_eff,
                                  **kwargs)
      # db
      if only_write_inputs:
        pass
      else:
        thermodata = self.DataBase.write_thermodata2db(
            directory_relax=directory_relax,
            system='adsorbate_on_slab',
            temperature=300,)
    return None

  # wrapper
  def get_and_calc_adsorbate_on_slab_wrapper(self, pardir='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/pristine_graphene',
                                             dbname_slab='graphene72atoms',
                                             adsorbate_name='O',
                                             dbname_adsorbate_on_slab=None,
                                             adsorbate_postion_index_list=[42],
                                             adsorbate_postion_symbol_list=None,
                                             adsorbate_roate_pars_dict=[
                                                 {'a': -30, 'v': 'x', },
                                                 {'a': -30, 'v': 'y', },
                                                 {'a': 0, 'v': 'z', },
                                             ],
                                             offset=None,
                                             height=2,
                                             only_write_inputs=True,
                                             ):
    """直接迟豫 ORR吸附物@slab
    - 最好首先测试O2H的最稳定吸附位
    - 对于任何体系, 先考察 O2H 和 O 的吸附能是否位于 O2H(-1.5~ -0.7) 和O(-4.4~-2.6) 最佳的应该是 O2H=-1.23, O=-2.46?
    - adsorbate_postion_index_list: 确定吸附位, 给定两个原子则是桥位, 3个则为hollow 位
    dbname_adsorbate_on_slab: None 表示使用默认的 {adsorbate_name}_{dbname_slab}, 否则使用给定的dbname, 例如 O_CCbridge_graphene72atoms

    Args:
        pardir (str, optional): _description_. Defaults to 'xxx/pristine_graphene'.
        dbname_slab (str, optional): _description_. Defaults to 'graphene72atoms'.
        adsorbate_name (str, optional): _description_. Defaults to 'OH'.
        dbname_adsorbate_on_slab (_type_, optional): _description_. Defaults to None.
        adsorbate_postion_index_list (list, optional): _description_. Defaults to [42].
        adsorbate_roate_pars_dict (dict, optional): _description_. Defaults to { 'a': 0, 'v': 'x', 'center': 'COP'}.
        only_write_inputs (bool, optional): _description_. Defaults to False.

    Returns: adsorbate_on_slab
        _type_: _description_
    """

    adsorbate_on_slab = self.GetModel.get_adsorbate_on_slab_model_wrapper(
        dbname_slab=dbname_slab,
        adsorbate_name=adsorbate_name,
        adsorbate_postion_index_list=adsorbate_postion_index_list,
        adsorbate_postion_symbol_list=adsorbate_postion_symbol_list,
        adsorbate_roate_pars_dict=adsorbate_roate_pars_dict,
        offset=offset,
        height=height,
    )

    if dbname_adsorbate_on_slab is None:
      dbname_adsorbate_on_slab = f'{adsorbate_name}_{dbname_slab}'
    directory = os.path.join(pardir, dbname_adsorbate_on_slab)
    adsorbate_on_slab = self.calc_general_relaxation(directory=directory,
                                                     atoms=adsorbate_on_slab,
                                                     only_write_inputs=only_write_inputs,)

    return adsorbate_on_slab

  def get_and_calc_adsorbate_on_slab_wrapper_ORR(self,
                                                 dbname_slab='B_O_Gra',
                                                 adsorbate_list=[
                                                     'O2', 'O2H', 'O', 'OH'],
                                                 pardir='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/B_O_Gra',
                                                 adsorbate_postion_index_list=None,
                                                 adsorbate_postion_symbol_list=None,
                                                 dbname_adsorbate_on_slab_list=[
                                                     None, None, None, None],
                                                 x_degree=-30,  # -150
                                                 y_degree=-10,
                                                 z_degree=0,
                                                 offset=None,
                                                 height=2,
                                                 ):
    """构建 吸附物 'O2', 'O2H', 'O', 'OH' @ slab 并迟豫
    最好首先测试O2H的最稳定吸附位

    Args:
        dbname_slab (str, optional): _description_. Defaults to 'B_O_Gra'.
        adsorbate_list (list, optional): _description_. Defaults to [ 'O2', 'O2H', 'O', 'OH'].
        pardir (str, optional): _description_. Defaults to '/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/B_O_Gra'.
        adsorbate_postion_index_list (_type_, optional): _description_. Defaults to None.
        adsorbate_postion_symbol_list (_type_, optional): _description_. Defaults to None.
        dbname_adsorbate_on_slab_list (list, optional): _description_. Defaults to [ None, None, None, None].
        x_degree (int, optional): _description_. Defaults to -30.
        z_degree (int, optional): _description_. Defaults to 0.
        offset (_type_, optional): _description_. Defaults to None.
        height (int, optional): _description_. Defaults to 2.

    Returns:
        _type_: _description_
    """

    adsorbate_roate_pars_dict = [{'a': x_degree, 'v': 'x'},
                                 {'a': y_degree, 'v': 'y'},
                                 {'a': z_degree, 'v': 'z'}
                                 ]
    atoms_list = []
    for adsorbate, dbname_adsorbate_on_slab in zip(adsorbate_list, dbname_adsorbate_on_slab_list):
      atoms = self.get_and_calc_adsorbate_on_slab_wrapper(
          pardir=pardir,
          dbname_slab=dbname_slab,
          adsorbate_name=adsorbate,
          dbname_adsorbate_on_slab=dbname_adsorbate_on_slab,
          adsorbate_postion_index_list=adsorbate_postion_index_list,
          adsorbate_postion_symbol_list=adsorbate_postion_symbol_list,
          adsorbate_roate_pars_dict=adsorbate_roate_pars_dict,
          height=height,
          only_write_inputs=True,
          offset=offset,
      )
      atoms_list.append(atoms)

    return atoms_list

  def wrapper_calc_relax_X_on_slab_test(self,
                                        dbname_slab='Br_MVG',
                                        adsorbate='O2H',
                                        adsorbate_postion_index_list=[61, 50],
                                        pardir='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/X_graphene/',
                                        x_degree=-30,
                                        y_degree=-10,
                                        z_degree=0,
                                        height=2,
                                        offset=None,
                                        ):
    """首先测试 O2H 在衬底上的最稳定吸附位

    Args:
        dbname_slab (str, optional): _description_. Defaults to 'Br_MVG'.
        adsorbate_postion_index_list (list, optional): _description_. Defaults to [61, 50].
        parpardir (str, optional): _description_. Defaults to '/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/X_graphene/'.
        z_degree (int, optional): _description_. Defaults to 0.
        height (float, optional): _description_. Defaults to 1.4.

    Returns:
        _type_: _description_
    """

    atoms_list = []
    for adsorbate_postion_index in adsorbate_postion_index_list:
      atoms = self.wrapper_calc_relax_adsorbate_on_slab_ORR(
          dbname_slab=dbname_slab,
          pardir=pardir,
          adsorbate_list=[adsorbate],
          adsorbate_postion_index_list=[adsorbate_postion_index],
          dbname_adsorbate_on_slab_list=[
              f'{adsorbate}_{dbname_slab}_{adsorbate_postion_index}'],
          x_degree=x_degree,
          y_degree=y_degree,
          z_degree=z_degree,
          height=height,
          offset=offset,
      )
      atoms_list.extend(atoms)

    return atoms_list

  def wrapper_calc_sp_se_slab(self,
                              dbname_list,
                              only_write_inputs=True):
    for dbname in dbname_list:
      self.calc_single_point_wrapper(dbname=dbname,
                                     directory_relax=None,
                                     only_write_inputs=only_write_inputs)
      self.calc_sol_eff_wrapper(dbname=dbname,
                                directory_relax=None,
                                only_write_inputs=only_write_inputs)
    return None

  def wrapper_calc_sp_se_vib_adsorbate_on_slab(self,
                                               dbname_list=['O2H_As_DVG'],
                                               directory_relax_list=None,
                                               atom_symbol_list=['O', 'H'],
                                               only_write_inputs=True):
    """* atom_symbol_list=['O', 'H'] for ORR, NRR 应该是 更复杂的设置
    * dbname_list|directory_relax_list 提供一个
    """

    if directory_relax_list is None and dbname_list is not None:
      directory_relax_list = [None]*len(dbname_list)
    elif directory_relax_list is not None and dbname_list is None:
      dbname_list = [None]*len(directory_relax_list)
    else:
      print('directory_relax_list|dbname_list 设置一个另一个为None')
      return
    for dbname, directory_relax in zip(dbname_list, directory_relax_list):
      self.calc_single_point_wrapper(directory_relax=directory_relax,
                                     dbname=dbname,
                                     only_write_inputs=only_write_inputs)
      self.calc_sol_eff_wrapper(directory_relax=directory_relax,
                                dbname=dbname,
                                only_write_inputs=only_write_inputs)
      self.calc_frequency_adsorbate_on_slab(
          directory_relax=directory_relax,
          dbname=dbname,
          atom_symbol_list=atom_symbol_list,
          atom_index_list=None,
          check_mask=False,
          only_write_inputs=only_write_inputs)

    return None

  def wrapper_calc_sp_se_vib_adsorbate_on_slab_ORR(self,
                                                   dbname_slab_list=['As_MVG'],
                                                   adsorbate_list=[
                                                       'O2', 'O2H', 'O', 'OH'],
                                                   only_write_inputs=True):
    """需要先计算衬底上吸附物O2H,O2, O,OH的迟豫 完成
    对于某个衬底, 计算衬底上吸附物O2H,O2 等的 sp,se,vib

    Args:
        dbname_slab_list (list, optional): _description_. Defaults to ['As_MVG'].
        adosorbate_list (list, optional): _description_. Defaults to ['O2','O2H','O','OH'].
        only_write_inputs (bool, optional): _description_. Defaults to True.
    """
    for dbname_slab in dbname_slab_list:
      for adsorbate in adsorbate_list:
        dbname = f'{adsorbate}_{dbname_slab}'
        self.wrapper_calc_sp_se_vib_adsorbate_on_slab(dbname_list=[dbname],
                                                      directory_relax_list=None,
                                                      only_write_inputs=only_write_inputs,)

    return None

  def wrapper_ORR(self, dbname_slab_list=['B_O_Gra', 'B_P_Gra', 'B_S_Gra'],
                  adsorbate_postion_index_list=None, adsorbate_postion_symbol_list=['B'],
                  step_num=2,
                  ):
    """用于参考: 从构建吸附物 到最后记录数据的流程

    - step1: 构建 吸附物在衬底上的吸附构型
    - step2: 写入迟豫信息, 计算 sp vib se
    - step3: 写入 sp vib se 信息

    Args:
        dbname_slab_list (list, optional): _description_. Defaults to ['B_O_Gra','B_P_Gra','B_S_Gra'].
        adsorbate_postion_index_list (_type_, optional): _description_. Defaults to None.
        adsorbate_postion_symbol_list (list, optional): _description_. Defaults to ['B'].
        step_num (int, optional): _description_. Defaults to 2.

    Returns:
        _type_: _description_
    """

    # 构建 吸附物在衬底上的吸附构型
    def step1(dbname_slab_list=dbname_slab_list,
              adsorbate_postion_index_list=adsorbate_postion_index_list, adsorbate_postion_symbol_list=adsorbate_postion_symbol_list,):
      atoms_list = []
      for dbname_slab in dbname_slab_list:
        alist = self.wrapper_calc_relax_adsorbate_on_slab_ORR(dbname_slab=dbname_slab,
                                                              adsorbate_postion_index_list=adsorbate_postion_index_list, adsorbate_postion_symbol_list=adsorbate_postion_symbol_list,
                                                              )
        atoms_list.extend(alist)
      return atoms_list

    # 提交任务
    ...
    # 写入迟豫信息, 计算 sp vib se

    def step2(dbname_slab_list=dbname_slab_list):
      # 写入迟豫信息
      self.DataBase.write_relaxation2db_wrapper_ORR(
          dbname_slab_list=dbname_slab_list)
      # 计算 sp vib se
      self.wrapper_calc_sp_se_vib_adsorbate_on_slab_ORR(
          dbname_slab_list=dbname_slab_list, only_write_inputs=True)
    # 提交任务
    ...
    # 写入 sp vib se 信息

    def step3(dbname_slab_list=dbname_slab_list):
      self.DataBase.write2db_sp_se_vib_wrapper_ORR(
          dbname_slab_list=dbname_slab_list)

    if step_num == 1:
      atoms_list = step1()
      return atoms_list
    elif step_num == 2:
      step2()
    elif step_num == 3:
      step3()

  def get_electrostatic_potential(self):
    """VASP 中的操作步骤：
    静电势计算：
    在 INCAR 文件中，设置 LVTOT = .TRUE. 来输出局部电势数据到 LOCPOT 文件中。
    可视化局部电势：
    和电荷密度类似，使用 VESTA 或 PyMOL 可视化 LOCPOT 文件。你可以在 As 原子附近绘制局部电势分布图，看是否存在不对称的电势分布。
    """
    pass

  # qsub 相关
  def get_qsub_directory_list(self,
                              pardir='adsorbate_slab',
                              sol_eff=False,
                              relax=False,
                              sp_vib=False,
                              ):
    """获取需要提交任务的目录, 这些目录中只有输入文件, 没有输出文件 'OUTCAR'

    Args:
        pardir (str, optional): _description_. Defaults to 'adsorbate_slab/PN_codoping_sub/slab'.

    Returns:
        _type_: _description_
    """
    qsub_directory_list = serverUse.Features().get_qsub_directory_list(pardir=pardir,
                                                                       relax=relax,
                                                                       sp_vib=sp_vib,
                                                                       sol_eff=sol_eff,
                                                                       )

    return qsub_directory_list

  def encut_converage_test(self, atoms,
                           pardir,
                           encut_list=range(200, 550, 50)):
    for encut in encut_list:
      self.calc_single_point(atoms=atoms,
                             directory=os.path.join(pardir, str(encut)),
                             encut=encut,
                             )
