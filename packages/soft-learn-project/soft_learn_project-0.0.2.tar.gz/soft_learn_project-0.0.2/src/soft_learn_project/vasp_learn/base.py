import numpy as np
import ase
import os
import ase.io
import ase.calculators.vasp
from vasp_learn import dataBase
import ase.io.cube
import ase.units
from py_package_learn.ase_learn import aseLearn
from py_package_learn.functools_learn import functoolsLearn


class Base(aseLearn.Base,):
  def __init__(self,) -> None:
    super().__init__()
    self.DataBase = dataBase.DataBase()
    # --- 以后去掉
    self.env_set_ase_vasp()
    pass

  def env_set_ase_vasp(self,
                       mpirun_path='/opt/homebrew/bin/mpirun',
                       is_mpirun=False,
                       n_cores=4,
                       ):
    r""" 弃用 已在 asevaspLearn 中 使用
    """
    # 在python环境中执行
    vasp_path = os.popen('which vasp').read().strip()
    os.environ['ASE_VASP_COMMAND'] = f'{mpirun_path} -np {n_cores} {vasp_path}' if is_mpirun else vasp_path

    os.environ['VASP_PP_PATH'] = os.path.join(
        os.environ['HOME'],
        'job/soft_learn/vasp_learn/vasp_pot')
    # The environment variable ASE_VASP_VDW should point to the folder where the vdw_kernel.bindat file is located.
    os.environ['ASE_VASP_VDW'] = os.path.join(
        os.environ['HOME'], 'job/soft_learn/vasp_learn/vasp_pot/vasp_pot.54')
    return None

  def get_line_mode_KPOINTS(self, atoms: ase.Atoms,
                            path_str='GXWG',
                            npoints=40,
                            fname='xxx/QPOINTS',):
    """用于产生 线性模式的 KPOINTS 对于声子的计算 需要 QPOINTS 
    """
    path_str_new = ''
    for i in range(len(path_str)-1):
      path_str_new += path_str[i]
      path_str_new += path_str[i+1]
    # path_str_new= 'GXXWWG'
    bp = atoms.cell.bandpath(path=path_str,)

    with open(file=fname, mode='w') as f:
      f.write('k points along high symmetry lines\n')
      f.write(f'{npoints}\t! number of points per line\n')
      f.write('line mode\n')
      # Use Cartesian (C, c, K, or k) or fractional (any other character) coordinates.
      f.write('fractional\n')
      for index, special_point in enumerate(path_str_new):
        coords = bp.special_points[special_point]
        for coord in coords:
          f.write(f'{coord}\t')
        f.write(f'! {special_point}\n')
        if index % 2 == 1:
          f.write('\n')
      return None

  def get_inputs(self, directory, atoms: ase.Atoms,
                 calc: ase.calculators.vasp.Vasp):
    """只产生 vasp 四个输入文件, 返回包含calc的atoms

    Args:
        directory (_type_): _description_
        atoms (ase.Atoms): _description_
        calc (ase.calculators.vasp.Vasp): _description_

    Returns: atoms 
        _type_: _description_
    """

    if not os.path.exists(directory):
      os.makedirs(directory)

    # 设置初始磁矩
    # calc.param_state['int_params']['ispin'] == 2:
    try:
      ispin = calc.parameters['ispin']
    except:
      ispin = 1

    if ispin == 2:
      atoms = self.set_initial_magmom(atoms=atoms)
      calc.set(lorbit=11)
    else:
      calc.set(ispin=1)
      atoms = self.set_initial_magmom(atoms=atoms)

    """ 是否设置以后再说
    if atoms.__len__() > 1:
      for atom in atoms:
        if atom.symbol in ['Fe','Co','Ni']:
          calc.set(ispin=2)
          atoms = self.set_initial_magmom(atoms=atoms)
          break
    """
    # calc
    # if not atoms.calc: #  如果atoms里面包含calc 属性, 则下面的就有问题, 无法重新设置 directory
    lreal = False if atoms.get_global_number_of_atoms() < 10 else 'Auto'
    calc.set(directory=directory, lreal=lreal)

    atoms.calc = calc

    calc.write_input(atoms=atoms)
    # print('写入输入文件完毕!')
    return atoms

  def get_compute(self, atoms: ase.Atoms,
                  directory='xxx',
                  recalc=False):
    try:
      atoms = ase.io.read(os.path.join(directory, 'OUTCAR'))
      # atoms = ase.calculators.vasp.Vasp(
      #     directory=directory, restart=True).get_atoms()
    except:
      if recalc:
        atoms.calc.clear_results()
      atoms.get_potential_energy()
    return atoms

  def get_inputs_and_compute(self, directory,
                             atoms: ase.Atoms,
                             only_write_inputs=False,
                             calc=None,
                             recalc=False,):
    """# 会读取已经存在的 CONTCAR
    如果只读取结果即only_write_inputs=False, 可以不设置 atoms, calc 

    Args:
        directory (_type_): 计算目录
        atoms (ase.Atoms): 要计算的原子结构
        calc (_type_): 计算器
        only_write_inputs (bool, optional): _description_. Defaults to True.
        recalc (bool, optional): _description_. Defaults to False.

    Returns: atoms 
        _type_: _description_
    """

    atoms = self.get_inputs(directory=directory, atoms=atoms, calc=calc,)
    if only_write_inputs:
      atoms = self.get_inputs(directory=directory, atoms=atoms, calc=calc,)
      print(f'将输入文件写入-> {directory}')
    else:
      try:
        atoms = ase.calculators.vasp.Vasp(
            directory=directory, restart=True).get_atoms()
      except:
        atoms = self.get_inputs(directory=directory, atoms=atoms, calc=calc,)
      if recalc:
        atoms.calc.clear_results()
      atoms.get_potential_energy()
    return atoms

  def read_chgcar(self, chg_file='xxx/single_point/CHG'):
    """只能读取CHG 很奇怪 以后再说

    Args:
        atoms (ase.Atoms): _description_

    Returns:
        _type_: _description_
    """
    # 读取CHG文件
    charge_density = ase.calculators.vasp.VaspChargeDensity(filename=chg_file)
    return charge_density

  def get_chg_data(self, chgcar: ase.calculators.vasp.VaspChargeDensity):
    """_summary_

    Args:
        chgcar (ase.calculators.vasp.VaspChargeDensity): _description_

    Returns: chg_data
        _type_: _description_
    """
    # 获取电荷密度数据
    chg_data = chgcar.chg[-1]  # 获取最后一步的电荷密度数据
    return chg_data

  def save_cube_from_chg(self, atoms: ase.Atoms,
                         charge_data,):
    """ 根据 chg_data 和 atoms 保存 cube

    Args:
        atoms (ase.Atoms): _description_
        charge_data (_type_): _description_
    """
    filename = os.path.join(atoms.calc.directory,
                            atoms.get_chemical_formula()+'.cube')
    # 保存的cube文件也能够直接用 vesta 看图
    ase.io.write(filename=filename, images=atoms,
                 data=charge_data*ase.units.Bohr**3)  # 必须要乘这个
    # 或者
    # ase.io.cube.write_cube(open('a.cube',mode='w'), atoms=atoms,
    #                        data=charge_data*ase.units.Bohr**3,) # 要乘吗？

  def save_cube_from_chg_simplify(self, atoms, chg_file='CHG'):
    """CHG 文件保存为 atoms 同目录下的 cube文件
    filename = os.path.join(atoms.calc.directory,atoms.get_chemical_formula()+'.cube')

    Args:
        atoms (_type_): _description_

    Returns: filename cube文件
        _type_: _description_
    """

    filename = os.path.join(atoms.calc.directory,
                            atoms.get_chemical_formula()+'.cube')
    if not os.path.exists(filename):
      charge_density = self.read_chgcar(chg_file=chg_file)
      chg_data = self.get_chg_data(chgcar=charge_density)
      self.save_cube_from_chg(atoms=atoms, charge_data=chg_data)
    return filename

  def get_cube_from_CHG(self, directory, chg_file='CHG'):
    """ ase 的方法

    Args:
        directory (_type_): _description_

    Returns: fname_cube
        _type_: _description_
    """

    calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
    atoms = calc.get_atoms()
    fname_cube = self.save_cube_from_chg_simplify(atoms=atoms,
                                                  chg_file=chg_file)
    return fname_cube

  def get_chg_diff(self, atoms1, atoms2, atoms3, directory):
    """需要计算好之后三部分的CHG 用VESTA 处理, edit-> edit data -> Volumetric data -> import data 注意减去
    # 或者使用程序处理
    # 出现这个错误 RuntimeError: The number of scaling factors must be 1 or 3. 可能是由于CHG是从服务器下载的 不适用于 vaps6 重新算个单点获得新的CHG就行

    Args:
        atoms1 (_type_): _description_
        atoms2 (_type_): _description_
        atoms3 (_type_): _description_
        directory (_type_): _description_
    """

    filename_atoms1 = self.save_cube_from_chg_simplify(atoms=atoms1)
    filename_atoms2 = self.save_cube_from_chg_simplify(atoms=atoms2)
    filename_atoms3 = self.save_cube_from_chg_simplify(atoms=atoms3)
    chg1 = self.read_cube(fname=filename_atoms1)['data']
    chg2 = self.read_cube(fname=filename_atoms2)['data']
    chg3 = self.read_cube(fname=filename_atoms3)['data']
    chg_diff = chg1 - chg2 - chg3

    # 保存 chg_diff
    fname_cub = os.path.join(directory, 'chg_diff.cube')
    ase.io.cube.write_cube(open(fname_cub, mode='w'),
                           atoms=atoms1,
                           data=chg_diff)  # 因为是从cube文件读取的不用再乘 *ase.units.Bohr**3
    print(f'chg_diff 保存在-> {fname_cub}\n用vesta画图!')

  def show_chgcar(self, fname_chg='CHG'):
    """ 这里 data 出错以后再考虑
    import ase.visualize.mlab
    chg = ase.calculators.vasp.VaspChargeDensity(filename='N2/CHG')
    ase.visualize.mlab.plot(atoms=chg.atoms[0], data=chg.chg[-1], contours=[0, 0.002])
    """
    try:
      """
      from mayavi import mlab
      # 读取CHGCAR文件
      chgcar = ase.calculators.vasp.VaspChargeDensity(filename=fname_chg)
      # 创建Mayavi场景
      mlab.figure(bgcolor=(1, 1, 1), size=(800, 600))
      # 绘制等密度曲面
      mlab.contour3d(chgcar.chg[-1], opacity=0.5, colormap='coolwarm',
                     contours=[0.005, 0.01, 0.02, 0.04, 0.06])
      mlab.show()
      """
      pass
    except:
      pass

  def get_optcell(self, directory, optcell_lines=['100', '110', '000']):
    """在 directory 增加 OPCELL 文件
    对于二维材料我们并不希望在真空层的方向优化, 需要在计算目录中增加 OPCELL 文件, 当然vasp也需要相应的编译
    编译参考: https://blog.shishiruqi.com//2019/05/05/constr/

    optcell_lines=['100', '110', '000'] # 表示只在 <100> <110> 方向优化
    Args:
        directory (_type_): _description_
        optcell_lines (list, optional): _description_. Defaults to ['100', '110', '000'].
    """
    if not os.path.exists(os.path.join(directory, 'OPTCELL')):
      os.makedirs(name=directory, exist_ok=True)
      with open(os.path.join(directory, 'OPTCELL'), mode='w') as f:
        for line in optcell_lines:
          f.write(f'{line}\n')

  def get_zval_from_potcar(self, directory=None,
                           dbname=None):
    """ 从potcar 中获取 zval, 需要有POTCAR 文件
    Args:
        directory (_type_): _description_

    Returns:
        _type_: _description_
    """

    directory, dbname = self.DataBase.choice_directory_dname(
        dbname=dbname, directory=directory)

    file_potcar = os.path.join(directory, 'POTCAR')
    file_potcar_gz = os.path.join(directory, 'POTCAR.gz')
    if os.path.exists(file_potcar):
      file_obj = open(file_potcar, mode='r', encoding='utf-8')
    elif os.path.exists(file_potcar_gz):
      import gzip
      file_obj = gzip.open(file_potcar_gz, mode='rt',
                           encoding='utf-8')
    else:
      raise FileNotFoundError('POTCAR 文件不存在!')

    import ase.calculators.vasp.create_input
    tuple_list = ase.calculators.vasp.create_input.read_potcar_numbers_of_electrons(
        file_obj=file_obj)
    data = {element: zval for element, zval in tuple_list}
    return data

  def get_nelect(self, dbname=None, directory=None):
    """# 弃用 直接在计算器中加参数 charge=-0.1  即可
    需要有POTCAR 文件, 获得体系总的电子数, 以考虑带电的体系
    例如: 体系总价电子20, 将NELECT=22 使体系带负电荷, 以考虑-2 价的阴离子在表面的吸附

    Args:
        dbname (_type_, optional): _description_. Defaults to None.
        directory (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    pass

  def set_initial_charge(self, directory='CO', cube_or_chg='chg'):
    """给目录中的原子对象附上初始价电子的数目
    最好使用 chg 结果比较合理
    # 加入了原子磁矩

    Args:
        directory (str, optional): _description_. Defaults to 'CO'.

    Returns:
        _type_: _description_
    """
    # 不能用常规的方法读取atoms: atoms=ase.io.read(), calc=ase.calculators.vasp.Vasp()
    if cube_or_chg == 'cube':
      for file in os.listdir(directory):
        if file.endswith('cube'):
          file_cube = file
          atoms = self.read_cube(os.path.join(directory, file_cube))['atoms']
    elif cube_or_chg == 'chg':
      from pymatgen.io.vasp.outputs import Chgcar
      # 这个较慢
      # chgcar = Chgcar.from_file(os.path.join(directory, 'CHG'))
      # atoms = chgcar.structure.to_ase_atoms()
      try:
        atoms = ase.io.read(os.path.join(directory, 'OUTCAR'))
      except:
        atoms = ase.io.read(os.path.join(directory, 'OUTCAR.gz'))
      # 加入原子磁矩
      initial_magnetic_moments = atoms.get_magnetic_moments()
      atoms.set_initial_magnetic_moments(initial_magnetic_moments)

      """ try 不行
      try:
        data_chg = ase.calculators.vasp.VaspChargeDensity(
            os.path.join(directory, 'CHG'))
        atoms = data_chg.atoms[-1]
      except:
        atoms = ase.io.read(os.path.join(directory, 'POSCAR'))
      """
    # 从potcar 中获取 zval
    data = self.get_zval_from_potcar(directory=directory)

    # 设置初始 charge
    for atom in atoms:
      atom.charge = data[atom.symbol]
      # atom.magmom = initial_magnetic_moments[atom.index]
    atoms: ase.Atoms

    return atoms
