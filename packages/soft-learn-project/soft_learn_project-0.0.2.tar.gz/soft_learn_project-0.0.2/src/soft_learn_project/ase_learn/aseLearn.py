
import ase.cluster.cubic
import ase.filters
import ase.io.trajectory
import ase.lattice.cubic
import ase.mep.dimer
import ase.optimize
import ase.optimize.fire
import ase.calculators.vasp
import ase.parallel
import matplotlib.pyplot as plt
import ase.optimize.basin
import ase.calculators.emt
import ase.calculators
import ase.build
import ase.visualize
import ase.constraints
import ase.optimize
import ase.db
import ase.io
import ase
import ase.cluster
import ase.data
import ase.eos
import ase.lattice
import ase.units
import ase.vibrations
import ase.db.core
import ase.thermochemistry
import ase.calculators.calculator
import ase.mep
import ase.dft.kpoints  # ase.dft.kpoints.BandPath
import ase.io.trajectory
import ase.stress
import ase.neighborlist
import copy
import pandas as pd
import numpy as np
import os
import shutil


class Base():
  def __init__(self,) -> None:
    pass

  def atomic_electronegativity_array(self):
    """鲍林标度电负性, 由于ase.data 中没有原子电负性数据, 因此我自己添加
    https://mp2.allhistory.com/detail/5837a5da05c3fbad758b4568
    直接使用 ase.data.atomic_electronegativity = ... 出错不知道为什么
    """
    atomic_electronegativity = np.array([0.00,  # X
                                         2.20,  # H
                                         4.16,  # He
                                         0.98,  # Li
                                         1.57,  # Be
                                         2.04,  # B
                                         2.25,  # C
                                         3.04,  # N
                                         3.44,  # O
                                         3.98,  # F
                                         4.79,  # Ne
                                         0.93,  # Na
                                         1.31,  # Mg
                                         1.61,  # Al
                                         1.98,  # Si
                                         2.19,  # P
                                         2.58,  # S
                                         3.16,  # Cl
                                         3.24,  # Ar
                                         0.82,  # K
                                         1.01,  # Ca
                                         1.36,  # Sc
                                         1.54,  # Ti
                                         1.63,  # V
                                         1.66,  # Cr
                                         1.55,  # Mn
                                         1.83,  # Fe
                                         1.88,  # Co
                                         1.91,  # Ni
                                         1.90,  # Cu
                                         1.65,  # Zn
                                         1.81,  # Ga
                                         2.01,  # Ge
                                         2.18,  # As
                                         2.55,  # Se
                                         2.96,  # Br
                                         3.00,  # Kr
                                         0.82,  # Rb
                                         0.95,  # Sr
                                         1.22,  # Y
                                         1.33,  # Zr
                                         1.59,  # Nb
                                         2.16,  # Mo
                                         1.91,  # Tc
                                         2.20,  # Ru
                                         2.28,  # Rh
                                         2.20,  # Pd
                                         1.93,  # Ag
                                         1.69,  # Cd
                                         1.78,  # In
                                         1.96,  # Sn
                                         2.05,  # Sb
                                         2.12,  # Te
                                         2.66,  # I
                                         2.60,  # Xe
                                         0.79,  # Cs
                                         0.89,  # Ba
                                         1.11,  # La
                                         1.12,  # Ce
                                         1.13,  # Pr
                                         1.14,  # Nd
                                         1.13,  # Pm
                                         1.17,  # Sm
                                         1.19,  # Eu
                                         1.22,  # Gd
                                         1.13,  # Tb
                                         1.22,  # Dy
                                         1.23,  # Ho
                                         1.24,  # Er
                                         1.25,  # Tm
                                         1.26,  # Yb
                                         1.27,  # Lu
                                         1.32,  # Hf
                                         1.51,  # Ta
                                         2.36,  # W
                                         1.93,  # Re
                                         2.18,  # Os
                                         2.20,  # Ir
                                         2.28,  # Pt
                                         2.54,  # Au
                                         2.00,  # Hg
                                         1.62,  # Tl
                                         2.33,  # Pb
                                         2.02,  # Bi
                                         1.99,  # Po
                                         2.22,  # At
                                         2.43,  # Rn
                                         0.71,  # Fr
                                         0.92,  # Ra
                                         1.09,  # Ac
                                         1.32,  # Th
                                         1.54,  # Pa
                                         1.38,  # U
                                         1.36,  # Np
                                         1.28,  # Pu
                                         1.13,  # Am
                                         1.28,  # Cm
                                         1.35,  # Bk
                                         1.29,  # Cf
                                         1.31,  # Es
                                         1.34,  # Fm
                                         1.33,  # Md
                                         1.36,  # No
                                         1.34,  # Lr
                                         np.nan,  # Rf
                                         np.nan,  # Db
                                         np.nan,  # Sg
                                         np.nan,  # Bh
                                         np.nan,  # Hs
                                         np.nan,  # Mt
                                         np.nan,  # Ds
                                         np.nan,  # Rg
                                         np.nan,  # Cn
                                         np.nan,  # Nh
                                         np.nan,  # Fl
                                         np.nan,  # Mc
                                         np.nan,  # Lv
                                         np.nan,  # Ts
                                         np.nan,  # Og
                                         ])
    return atomic_electronegativity

  def get_atomic_electron_affinity(self, element='H'):
    """元素或化合物 X 的电子亲合能（或电子亲和势或电子亲和力） Eea表征了该元素或物质夺取电子的能力。根据IUPAC的定义，电子亲合能等于该物质的 -1 价离子失去一个电子，变成基态原子或化合物时所需吸收的能量。
    """

    data_dict = {'H': 0.754, 'He': 0, 'Li': 0.618, 'Be': 0, 'B': 0.277,
                 'C': 1.263, 'N': -0.07047727, 'O': 1.461, 'F': 3.399, 'Ne': 0,
                 'Na': 0.543, 'Mg': 0, 'Al': 0.441, 'Si': 1.385, 'P': 0.746,
                 'S': 2.077, 'Cl': 3.617, 'Ar': 0, 'K': 0.501, 'Ca': 0,
                 'Sc': 0.188, 'Ti': 0.079, 'V': 0.525, 'Cr': 0.666, 'Mn': 0.124,
                 'Fe': 0.163, 'Co': 0.661, 'Ni': 1.156, 'Cu': 1.228, 'Zn': 0,
                 'Ga': 3, 'Ge': 1.35, 'As': 0.81, 'Se': 2.021, 'Br': 3.365,
                 'Kr': 0, 'Rb': 0.486, 'Sr': 0, 'Y': 0.307, 'Zr': 0.426,
                 'Nb': 0.893, 'Mo': 0.746, 'Tc': 0.55, 'Ru': 1.05, 'Rh': 1.137,
                 'Pd': 0.557, 'Ag': 1.302, 'Cd': 0, 'In': 0.3, 'Sn': 1.2,
                 'Sb': 1.07, 'Te': 1.971, 'I': 3.059, 'Xe': 0, 'Cs': 0.472,
                 'Ba': 0, 'La': 0.5, 'Hf': 0, 'Ta': 0.322, 'W': 0.815,
                 'Re': 0.15, 'Os': 1.1, 'Ir': 1.565, 'Pt': 2.128, 'Au': 2.309,
                 'Hg': 0, 'Tl': 0.2, 'Pb': 0.36, 'Bi': 0.946, 'Po': 1.9,
                 'At': 2.8, 'Rn': 0, 'Pr': 0.470, 'Ra': 0,
                 }
    atomic_electron_affinity = data_dict[element]
    return atomic_electron_affinity

  def get_atomic_electronegativity(self, atomic_symbol='O'):
    """鲍林标度电负性

    Args:
        atomic_symbel (str, optional): _description_. Defaults to 'O'.

    Returns:
        _type_: _description_
    """
    atomic_electronegativity_array = self.atomic_electronegativity_array()
    atomic_electronegativity_value = atomic_electronegativity_array[
        ase.data.atomic_numbers[atomic_symbol]]
    return atomic_electronegativity_value

  def get_atomic_electronegativity_df(self,
                                      atomic_symbol_list=['Si', 'P', 'C']):
    import pandas as pd
    atomic_electronegativity_list = []
    for atomic_symbol in atomic_symbol_list:
      v = self.get_atomic_electronegativity(atomic_symbol)
      atomic_electronegativity_list.append(v)
    df = pd.DataFrame(data=atomic_electronegativity_list,
                      index=atomic_symbol_list,
                      columns=['atomic_electronegativity'])
    return df

  def get_atomic_vdw_radii(self, atomic_symbel):
    atomic_numbers = ase.data.atomic_numbers[atomic_symbel]
    vdw_radii = ase.data.vdw_radii[atomic_numbers]
    return vdw_radii

  def get_atomic_covalent_radii(self, atomic_symbel):
    """* 判断成键的具体依据
    - 原子间距离：ASE-GUI 根据原子之间的实际距离 与标准键长 的比值，来决定是否显示成键。
    - 距离阈值比例：默认情况下，ASE-GUI 允许显示键的阈值比例为 1.2 倍。例如，如果两个原子间的距离小于 1.2 倍的标准键长，则会显示为有键。
    - 标准键长的来源：标准键长
      是根据原子类型（即化学元素）及其典型的共价半径来计算的。例如，C-H、C-C 等常见的键长可以通过元素的共价半径之和来估算。
    """
    atomic_numbers = ase.data.atomic_numbers[atomic_symbel]
    atom_covalent_radii = ase.data.covalent_radii[atomic_numbers]
    return atom_covalent_radii

  def get_magmom(self, chemical_symbols='Pt', is_print=False):
    """对于单原子计算时需要给出初始磁矩, 才会更容易收敛

    Args:
        chemical_symbols (str, optional): _description_. Defaults to 'Pt'.

    Returns:
        _type_: _description_
    """
    for idx in range(1, ase.data.chemical_symbols.__len__()):
      if chemical_symbols == ase.data.chemical_symbols[idx]:
        magmom = ase.data.ground_state_magnetic_moments[idx]
        if is_print:
          print(f'{chemical_symbols} 的序号为{idx}')
        return magmom

  def set_initial_magmom(self, atoms: ase.Atoms):
    """给原子对象设置初始磁矩

    Args:
        atoms (ase.Atoms): _description_

    Returns:
        _type_: _description_
    """
    for atom in atoms:
      atom.magmom = self.get_magmom(chemical_symbols=atom.symbol)
    return atoms

  def set_selective_dynamics(self, atoms: ase.Atoms, mask):
    """
    eg: mask = atoms.positions[:, 2] < 10
    mask = [atom.index for atom in atoms if atom.position[2] <10]
    Args:
        atoms (ase.Atoms): _description_
        mask (_type_): mask 为需要固定的原子索引
    """
    # 产生selective poscar
    constraint = ase.constraints.FixAtoms(mask=mask)  #
    atoms.set_constraint(constraint)
    return atoms

  def set_selective_dynamics_wrapper(self,
                                     atoms,
                                     position_z_downlim,
                                     atom_symbol_list=['O', 'H']):
    """选择性迟豫原子
    position_z_downlim 和 atom_symbol_list 控制需要固定的原子索引

    Args:
        atoms (_type_): _description_
        position_z_downlim (int, optional): _description_. Defaults to 11.
        atom_symbol_list (str, optional): _description_. Defaults to 'OH'.

    Returns:
        _type_: _description_
    """
    unmask = self.get_atoms_index_list(atoms=atoms,
                                       position_z_downlim=position_z_downlim,
                                       atom_symbol_list=atom_symbol_list)
    mask = [atom.index for atom in atoms if atom.index not in unmask]  # 衬底
    atoms = self.set_selective_dynamics(atoms=atoms, mask=mask)
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

  def read_cube(self, fname='tmp.cube'):
    import ase.io.cube
    cube_dict = ase.io.cube.read_cube(open(fname))
    atoms = cube_dict['atoms']
    data = cube_dict['data']
    result = [atoms, data]
    return result

  def plot_cube(self, data):
    """data 为read_cube 读取的字典

    Args:
        data (_type_): _description_
    """
    # 3D
    """
    from mayavi import mlab
    mlab.contour3d(data['data'], contours=10, opacity=0.4)
    mlab.axes()
    mlab.colorbar(title='Charge density', orientation='vertical')
    mlab.title('3D Charge density')
    mlab.show()
    """
    # 2D
    data = data['data']
    # 选择在z轴的中间切片
    z_slice = data[:, :, data.shape[2] // 2]

    # 使用matplotlib绘制2D切片图
    plt.imshow(z_slice, origin='lower', cmap='viridis', extent=[
        0, z_slice.shape[1], 0, z_slice.shape[0]])
    plt.colorbar(label='Charge density')
    plt.xlabel('X axis')
    plt.ylabel('Y axis')
    plt.title('Charge density slice (middle of Z)')
    plt.show()
    pass

  def plot_energies(self, directory):
    """画图, 目录中体系能量的变化

    Args:
        directory (_type_): _description_
    """
    from soft_learn_project.py4vasp_learn import py4vaspLearn
    py4vaspLearn.Py4vaspLearn().get_energy(directory=directory)
    pass

  def get_atoms_index_list(self, atoms,
                           position_z_downlim=None,
                           atom_symbol_list=None,
                           ):
    """根据元素和z 方向的位置选取原子索引, 以后测试
    # 以后atom_symbol_list 要改成 ['O','H','He'] 这种 否则 'B' 会认为在'Br'里面

    eg:
    position_z_downlim=8
    atom_symbol_list='OH'

    Args:
        atoms (_type_): _description_
        position_z_downlim (int, optional): _description_. Defaults to 8.
        atom_symbol_list (str, optional): _description_. Defaults to 'OH'.

    Returns:
        _type_: _description_
    """
    if position_z_downlim:
      index_list1 = [
          atom.index for atom in atoms if atom.position[2] > position_z_downlim]
    else:
      index_list1 = [atom.index for atom in atoms]

    if atom_symbol_list:
      index_list2 = [
          atom.index for atom in atoms if atom.symbol in atom_symbol_list]
    else:
      index_list2 = [atom.index for atom in atoms]
    # 求交集
    intersection = set(index_list1).intersection(index_list2)
    intersection = list(intersection)
    return intersection

  def get_kpts_density(self, a=3.16, k=7):
    """获得沿某个方向上的k点密度, ase 中 k_density > 2.5 即可

    Args:
        a (float, optional): _description_. Defaults to 3.16.
        k (int, optional): _description_. Defaults to 7.

    Returns:
        _type_: _description_
    """
    b = 2*np.pi / a
    k_density = k/b
    return k_density

  def get_property_kpts(self, a=3.16, criterion_k_density=0.02):
    """只考虑正交的晶格
    vaspkit 中的k 点密度标准为 一般计算使用0.04，精确计算0.03或0.02  # 单位是Angstrom-1?
    """
    for k in range(1, 50):
      k_density = self.get_kpts_density(a=a, k=k)
      k_density_volume = k_density**3
      if 1/k_density_volume < criterion_k_density:
        break
    return k

  # 原子列表
  def get_index_list_and_symbol_list(self, atoms: ase.Atoms,
                                     symbol_list=None,
                                     index_list=None,):
    """给出一个 symbol_list | index_list, 获取两个 index_list, symbol_list

    Args:
        atoms (ase.Atoms): _description_
        symbol_list (_type_, optional): _description_. Defaults to None.
        index_list (_type_, optional): _description_. Defaults to None.

    Returns: index_list, symbol_list
        _type_: _description_
    """
    if symbol_list:
      index_list = [atom.index for atom in atoms if atom.symbol in symbol_list]
    elif index_list:
      # symbol_list = [atoms.get_chemical_symbols()[index] for index in index_list]
      symbol_list = [atoms.symbols[index] for index in index_list]
      pass
    else:
      print('请输入 symbol_list|index_list 中的一个.')
      return None
    return index_list, symbol_list

  def get_neighbors_list(self, atoms: ase.Atoms,
                         atom_index=72,
                         distance_max=3.0,
                         max_neighbors=12,
                         tolerance=0.1,
                         max_iter=100,
                         _iter=0):
    """根据原子索引获得该原子的最近邻列表，自动调整距离"""

    # 判断原子间近邻的距离
    if distance_max is None:
      cutoffs_list = [self.get_atomic_covalent_radii(atom.symbol)
                      for atom in atoms]
      distance_max = max(cutoffs_list)*2
    else:
      cutoff_radius = distance_max/2  # 设置截断半径
      cutoffs_list = [cutoff_radius] * len(atoms)

    if distance_max <= 0 or _iter >= max_iter:
      return []  # 防止死循环或负数距离

    nl = ase.neighborlist.NeighborList(cutoffs=cutoffs_list,
                                       self_interaction=False, bothways=True)
    nl.update(atoms)

    indices, offsets = nl.get_neighbors(atom_index)
    n_neighbors = len(indices)

    if n_neighbors == 0:
      # 如果没有邻居，则增加截断距离
      return self.get_neighbors_list(atoms=atoms,
                                     atom_index=atom_index,
                                     distance_max=distance_max *
                                     (1 + tolerance),
                                     max_neighbors=max_neighbors, tolerance=tolerance,
                                     max_iter=max_iter,
                                     _iter=_iter + 1)
    elif n_neighbors > max_neighbors:
      # 如果邻居太多，则减小截断距离
      return self.get_neighbors_list(atoms=atoms,
                                     atom_index=atom_index,
                                     distance_max=distance_max *
                                     (1 - tolerance),
                                     max_neighbors=max_neighbors, tolerance=tolerance,
                                     max_iter=max_iter,
                                     _iter=_iter + 1)
    else:
      return indices

  def get_neighbor_index_list_wrapper(self,
                                      atoms: ase.Atoms,
                                      index_list=None,
                                      symbol_list=None):
    """根据 index_list 或者 symbol_list 获取近邻的索引列表

    Args:
        dbname (str, optional): _description_. Defaults to 'graphene72atoms'.
        center_index_list (list, optional): _description_. Defaults to [29, 42].

    Returns: center_neighbor_index_list
        _type_: _description_
    """

    index_list, symbol_list = self.get_index_list_and_symbol_list(atoms=atoms,
                                                                  symbol_list=symbol_list,
                                                                  index_list=index_list)

    center_neighbor_index_list = []
    for center_index in index_list:
      neighbor_index_list = self.get_neighbors_list(atoms=atoms,
                                                    atom_index=center_index)
      center_neighbor_index_list.extend(neighbor_index_list)
      center_neighbor_index_set = set(
          center_neighbor_index_list).difference(index_list)
      center_neighbor_index_list = list(center_neighbor_index_set)
    return center_neighbor_index_list

  def set_tags(self, atoms: ase.Atoms):
    for atom in atoms:
      atom.tag = atom.index
    return atoms


class DataBase():
  def __init__(self):
    """如果出错可以查看是否多出文件'db_all.json.lock',删除即可"""
    self.fname_db = os.path.join(
        os.environ['HOME'], 'my_server/my/db_all.json')
    a, b = os.path.split(self.fname_db)
    c, d = b.split('.')
    c += '_bk'
    b = c + '.' + d
    self.fname_db_bk = os.path.join(a, b)

    self.db: ase.db.core.Database = ase.db.connect(self.fname_db)
    self.df_researchdata = pd.DataFrame()
    pass

  # basic
  def db_write(self, name, atoms, directory, **kwargs,):
    id = self.db.reserve(name=name)
    if id:
      self.db.write(id=id, name=name, atoms=atoms,
                    directory=directory, **kwargs)
      ase.parallel.parprint(f'{name} -> 写入了 db.')

  def db_update(self, name, atoms, directory, **kwargs,):
    # 更新 db
    row = self.db.get(name=name)
    self.db.update(id=row.id, name=name, atoms=atoms,
                   directory=directory, **kwargs)
    ase.parallel.parprint(f'{name} -> 更新了db.')

  def db_update_values(self, name, **kwargs,):
    """不更新原子对象
    """
    # 更新 db
    row = self.db.get(name=name)
    self.db.update(id=row.id, **kwargs)
    ase.parallel.parprint(f'{name} -> 更新了db.')
    return None

  def db_write_and_update(self, atoms,
                          directory,
                          dbname=None,
                          **kwargs,):
    """dbname 默认采用目录名, 如果添加了name 关键词, 则使用name
    保存到 db_all.json, 并备份 db_all.bk.json, 如果以后出错则用备份
    """

    # dbname 默认采用目录名, 如果添加了name 关键词, 则使用name
    if dbname is None:
      dbname = os.path.basename(os.path.abspath(directory))

    try:
      self.db_update(name=dbname, atoms=atoms, directory=directory, **kwargs)
    except Exception:
      ase.parallel.parprint('没有之前的数据更新不了而出错, 没问题.')
      self.db_write(name=dbname, atoms=atoms, directory=directory, **kwargs)
    finally:
      # 备份
      fname = self.fname_db
      fname_bk = self.fname_db_bk
      bk_days = 1
      import datetime
      time_now = datetime.datetime.now()
      file_mod_time = datetime.datetime.fromtimestamp(
          os.path.getmtime(fname_bk))
      days = (time_now - file_mod_time).days
      if days > bk_days:
        shutil.copy(fname, fname_bk)
        ase.parallel.parprint(f'{fname} 已备份-> {fname_bk}')
    return None

  def choice_directory_dname(self, directory=None, dbname=None):
    """给出一个参数, 也获取另一个参数
    """
    if directory:
      dbname = os.path.basename(os.path.abspath(directory))
    elif dbname:
      row = self.db.get(name=dbname)
      directory = row.directory
    else:
      pass
    return directory, dbname

  def get_atoms(self, name, fname_db=None):
    if fname_db is not None:
      self.db = ase.db.connect(fname_db)
    for row in self.db.select(name=name):
      atoms = row.toatoms()
    return atoms


class Model(Base):
  def __init__(self):
    """建立, 保存, 查看 模型
    晶体结构查找的网站: https://zhuanlan.zhihu.com/p/616730035
    # 比如 B alpha-rhombohedral 晶体结构 ase 中是没有的
    https://rruff.geo.arizona.edu/AMS/amcsd.php 在 'General Search'框中搜索 black Phosphorus
    # 或者
    http://www.crystallography.net/cod/search.html 在 text 中搜索 black Phosphorus -> send --> 新的网页
    # 或者
    https://next-gen.materialsproject.org/

    ---
    # 获取元胞:
    AseLearn().atoms_obj_operation
    """

    super().__init__()
    self.view = ase.visualize.view
    pass

  # 构造方法
  def get_atoms_normal_crsytal(self, name='Au',
                               cubic=False,
                               lc_a=None):
    atoms = ase.build.bulk(name=name,
                           cubic=cubic,
                           a=lc_a)
    return atoms

  def get_atoms_rocksalt_crystal(self, name='NaCl',
                                 crystalstructure="rocksalt",
                                 a=5.64,
                                 cubic=True):
    """atoms = ase.build.bulk(name="MgO", crystalstructure="rocksalt", a=4.2,cubic=True)
    - https://wiki.fysik.dtu.dk/ase/ase/lattice.html

    Returns:
        _type_: _description_
    """
    atoms = ase.build.bulk(name=name,
                           crystalstructure=crystalstructure,
                           a=a,
                           cubic=cubic)

    return atoms

  def get_atoms_abnormal_crystal(self, symbol='Mn', a=3):
    # 获得晶体的方法, 用于之后的迟豫计算晶格常数
    if symbol == 'Mn':
      bcc = ase.lattice.BCC(a=a).cellpar()
      atoms = ase.Atoms(symbols=symbol, cell=bcc, pbc=True)
    else:
      atoms = ase.build.bulk(name=symbol, a=a)

    # 其它方法
    # atoms = ase.io.read('/Users/wangjinlong/Desktop/AMS_DATA.cif', )
    return atoms

  def get_atoms_bulk_bcc111(self,
                            symbol='W',
                            size=(2, 2, 25),
                            a=3.165,
                            vacuum=0,
                            orthogonal=True,
                            periodic=True):
    """对于其它方向也有类似的方法
    """
    atoms = ase.build.bcc111(symbol=symbol,
                             size=size,
                             a=a,
                             vacuum=vacuum,
                             orthogonal=orthogonal,
                             periodic=periodic)
    # ase.build.cut(atoms, a=10)
    return atoms

  def get_atoms_bulk_bcc110(self,
                            symbol='W',
                            size=(3, 4, 10),
                            a=3.165,
                            vacuum=0,
                            orthogonal=True,
                            periodic=True):
    """该方法建立表面比较方便, 对于体块的话有错误 会多一层原子"""
    atoms = ase.build.bcc110(symbol=symbol,
                             size=size,
                             a=a,
                             vacuum=vacuum,
                             orthogonal=orthogonal,
                             periodic=periodic)
    # ase.build.cut(atoms, a=10)
    return atoms

  def get_atoms_bulk_specify_direction(self,
                                       name='W',
                                       cubic=True,
                                       a=3.165,
                                       vector_a=(0, 0, 1),
                                       vector_b=(1, -1, 0),
                                       vector_c=(1, 1, 0),
                                       repeat=(3, 2, 5)):
    """三个向量分别对应三个方向
    lattice_args_dict = {
        '111': 'orient x 1 -1 0 orient y 1 1 -2 orient z 1 1 1',
        '100': 'orient x 1 0 0 orient y 0 1 0 orient z 0 0 1',
        '110': 'orient x 0 0 1 orient y 1 -1 0 orient z 1 1 0', }
    """
    atoms = ase.build.bulk(name=name, cubic=cubic, a=a)
    atoms: ase.Atoms = ase.build.cut(atoms=atoms,
                                     a=vector_a,
                                     b=vector_b,
                                     c=vector_c,)
    atoms = atoms.repeat(rep=repeat)
    return atoms

  def get_atoms_bulk_specify_direction_z100(self,
                                            name='W',
                                            a=3.165,
                                            repeat=(3, 3, 8)):
    atoms = self.get_atoms_bulk_specify_direction(name=name,
                                                  cubic=True,
                                                  a=a,
                                                  vector_a=(1, 0, 0),
                                                  vector_b=(0, 1, 0),
                                                  vector_c=(0, 0, 1),
                                                  repeat=repeat)
    return atoms

  def get_atoms_bulk_specify_direction_z110(self,
                                            name='W',
                                            a=3.165,
                                            repeat=(3, 2, 6)):
    atoms = self.get_atoms_bulk_specify_direction(name=name,
                                                  cubic=True,
                                                  a=a,
                                                  vector_a=(0, 0, 1),
                                                  vector_b=(1, -1, 0),
                                                  vector_c=(1, 1, 0),
                                                  repeat=repeat)
    return atoms

  def get_atoms_bulk_specify_direction_z111(self,
                                            name='W',
                                            a=3.165,
                                            repeat=(2, 1, 5)):
    atoms = self.get_atoms_bulk_specify_direction(name=name,
                                                  cubic=True,
                                                  a=a,
                                                  vector_a=(1, -1, 0),
                                                  vector_b=(1, 1, -2),
                                                  vector_c=(1, 1, 1),
                                                  repeat=repeat)
    return atoms

  def get_atoms_nanapartile_fcc_cubic(self,
                                      symbols='Cu',
                                      size=4):
    """Set up a nanoparticle
    以 fcc_cubic 为例, 可以作为参考
    """
    atoms = ase.cluster.cubic.FaceCenteredCubic(symbols=symbols,
                                                surfaces=[[1, 0, 0], [
                                                    1, 1, 0], [1, 1, 1]],
                                                layers=(size, size, size),
                                                vacuum=4)
    return atoms

  def get_atoms_molecular(self, name='CO', vacuum=None,
                          pbc=False):
    atoms = ase.build.molecule(name=name, vacuum=vacuum,
                               pbc=pbc)
    return atoms

  def get_atoms_isolated(self,  symbol='O',
                         pbc=True,
                         vacuum=5,
                         ):
    """获得孤立的原子
    """
    atoms = ase.Atoms(symbols=symbol, pbc=pbc, )
    atoms.center(vacuum=vacuum)
    atoms.cell += np.diag([-0.5, 0, 0.5])
    return atoms

  def get_atoms_molecular_wrapper(self, adsorbate):
    """获得ORR 或NRR 中的吸附物 的 atoms, 用于 之后的 self.calc_molecular_relax() 分子迟豫
    """
    try:
      # if adsorbate in ['N2', 'NH3', 'NH2', 'NH', 'N']:
      atoms_adsorbate = ase.build.molecule(name=adsorbate)
      atoms_adsorbate.rotate(180, 'x')
    except Exception:
      if adsorbate in ['N2H', 'N2H2']:
        atoms_adsorbate = ase.build.molecule('N')
        atoms_adsorbate2 = ase.build.molecule(
            'NH') if adsorbate == 'N2H' else ase.build.molecule('NH2')
        atoms_adsorbate2.rotate(180, 'x')
        ase.build.add_adsorbate(slab=atoms_adsorbate,
                                adsorbate=atoms_adsorbate2, height=1.6)
      if adsorbate == 'O2H':
        atoms_adsorbate = self.get_O2H()
        atoms_adsorbate.rotate(a=-90, v='y')
        # return atoms_adsorbate
      elif adsorbate == 'H3O':
        atoms_adsorbate = self.get_H3O()
      else:
        atoms_adsorbate = ase.Atoms(symbols=adsorbate,)
    return atoms_adsorbate

  def get_H3O(self):
    from soft_learn_project.numpy_learn import numpyLearn
    atoms = self.get_atoms_molecular_wrapper('H2O')
    vec = atoms.get_center_of_mass()
    vec_u = numpyLearn.NumpyLearn().get_unit_vector(vector_arr=vec)
    atoms = self.add_new_atom(atoms=atoms,
                              new_atom_symbol='H',
                              position=vec_u*1.1)
    return atoms

  def get_O2H(self):
    atoms = ase.build.molecule('O2')
    atoms = self.add_new_atom_along_vector(atoms=atoms,
                                           new_atom_symbol='H',
                                           vector_point_atom_index_list=[
                                               0, 1],
                                           distance=0.98,
                                           ref_index=1,
                                           )
    return atoms

  def get_atoms_surface_for_bcc(self, symbol='W',
                                a=3.165,
                                size=(3, 3, 9),
                                vacuum=5,
                                surface_indices='100',):
    if surface_indices == '100':
      atoms = ase.build.bcc100(symbol=symbol,
                               size=size,
                               vacuum=vacuum,
                               a=a,
                               #  periodic=True # for DFT calc
                               )
    elif surface_indices == '110':
      atoms = ase.build.bcc110(symbol=symbol,
                               size=size,
                               vacuum=vacuum,
                               a=a,
                               #  periodic=True # for DFT calc
                               )
    elif surface_indices == '111':
      atoms = ase.build.bcc111(symbol=symbol,
                               size=size,
                               vacuum=vacuum,
                               a=a,
                               #  periodic=True # for DFT calc
                               )
    # 固定表面中间一层
    z_center = atoms.get_center_of_mass()[2]
    mask = (atoms.positions[:, 2] < z_center +
            0.1) & (atoms.positions[:, 2] > z_center-0.1)
    # constraint = ase.constraints.FixCom()
    constraint = ase.constraints.FixAtoms(mask=mask,)
    atoms.set_constraint(constraint=constraint)

    return atoms

  def get_atoms_surface(self,
                        atoms,
                        indices=(1, 1, 1),
                        layers=4,
                        vacuum=7.5,
                        position_z_downlim=10,
                        atom_symbol_list=['Au'],):
    """  # atoms 是传统晶胞而不是元胞, 而且要具有优化后的晶格常数
    创建一个表面: atoms = ase.build.add_vacuum()
    """

    surface = ase.build.surface(lattice=atoms,
                                indices=indices,
                                layers=layers,
                                vacuum=vacuum,)
    surface = self.set_selective_dynamics_wrapper(
        atoms=surface,
        position_z_downlim=position_z_downlim,
        atom_symbol_list=atom_symbol_list)

    return surface

  def get_surface_area(self, atoms: ase.Atoms):
    """atoms 为表面模型 z方向为真空方向
    """
    a = atoms.cell.cellpar()[0]
    b = atoms.cell.cellpar()[1]
    ab_theta = atoms.cell.cellpar()[5]
    area = a*b*np.sin(ab_theta/180*np.pi)
    return area

  def get_XmYn_model(self,
                     atoms=None,
                     center_index_list=[29, 42],
                     center_num=2,
                     center_name='B',
                     neighbor_num=4,
                     neighbor_name='N',):
    """取代中心或者近邻的原子
    """

    neighbor_index_list = self.get_neighbor_index_list_wrapper(
        atoms=atoms,
        index_list=center_index_list,
        symbol_list=None)

    # 替换近邻的原子
    for atom in atoms:
      if atom.index in neighbor_index_list[:neighbor_num]:
        atom.symbol = neighbor_name
    # 中心原子设置
    if center_num == 1:
      position = atoms[center_index_list].get_center_of_mass()*1.02
      atom_center = ase.Atom(symbol=center_name, position=position)
      atoms.append(atom_center)  # 增加多个用 atoms.extend(atoms)
      # 去掉原来的中心原子
      # for index in center_index_list:  # 该方法每次去掉原子后, 原来的索引会变, 故不用
      # atoms.pop(index)
      atoms = atoms[[
          atom.index for atom in atoms if atom.index not in center_index_list]]
    elif center_num == len(center_index_list):
      # 替换中心原子的元素
      for index in center_index_list:
        atoms[index].symbol = center_name
      pass
    elif center_num == 0:
      # 不增加中心原子
      atoms = atoms[[
          atom.index for atom in atoms if atom.index not in center_index_list]]
    else:
      print(f'请确认: {center_num}')
      return None
    return atoms

  def get_adsorbate_on_slab_model(self, slab: ase.Atoms,
                                  adsorbate='O2H|ase.Atoms',
                                  adsorbate_postion_index_list=[42],
                                  adsorbate_postion_symbol_list=None,
                                  x_degree=0,
                                  y_degree=0,
                                  z_degree=0,
                                  height=1.5,
                                  offset=None,
                                  ):
    """
    adsorbate_roate_pars_dict 可以是一个列表, 对吸附物进行多次操作
    """
    # 注意! slab 需要深拷贝 copy.deepcopy()
    slab = copy.deepcopy(slab)

    if isinstance(adsorbate, ase.Atoms):
      atoms_adsorbate = adsorbate
    elif isinstance(adsorbate, str):
      if adsorbate in ['O', 'OH', 'O2']:
        atoms_adsorbate = self.get_atoms_molecular_wrapper(adsorbate=adsorbate)
        atoms_adsorbate.rotate(a=90, v='y')
      else:
        atoms_adsorbate = self.get_atoms_molecular_wrapper(adsorbate=adsorbate)
        # if adsorbate == 'CO':
        #   atoms_adsorbate.rotate(a=180, v='x')
    else:
      print('请检查 adsorbate 的类型是否是 ase.Atoms 或者 str')

    index_list, symbol_list = self.get_index_list_and_symbol_list(
        atoms=slab,
        symbol_list=adsorbate_postion_symbol_list,
        index_list=adsorbate_postion_index_list)
    position_adsorbate = slab[index_list].get_center_of_mass(
    )

    # 旋转吸附物
    for adsorbate_roate_pars in [{'a': x_degree, 'v': 'x', 'center': 'COP'},
                                 {'a': y_degree, 'v': 'y', 'center': 'COP'},
                                 {'a': z_degree, 'v': 'z', 'center': 'COP'}]:
      atoms_adsorbate.rotate(**adsorbate_roate_pars)

    mol_index = 1 if adsorbate in ['O2H'] else 0
    # 表面最高的原子比吸附位高出的距离
    delta_h = slab.positions[:, 2].max() - position_adsorbate[2]
    ase.build.add_adsorbate(
        slab=slab,
        adsorbate=atoms_adsorbate,
        # 增加一点偏移量以获取可能的稳定构型, 比如桥位
        position=position_adsorbate[:2]*1.005,
        # 相对于表面的高度, 而表面其它原子可能较高, 而吸附考虑的是吸附物相对吸附位的高度
        height=height - delta_h,
        mol_index=mol_index,
        offset=offset)
    return slab

  def graphene_pure(self, surface_size=(4, 4, 1), vacuum=5):
    graphene: ase.Atoms = ase.build.graphene()
    graphene.center(axis=2, vacuum=vacuum)
    graphene = graphene.repeat(surface_size)
    system = graphene
    return system

  def get_graphdiyne(self, ):
    """通过修改atom.position[0] > -0.68 上下限获取 不同类型的 graphdiyne
    * 我已经保存在 / Users/wangjinlong/my_server/my/myORR_B/slab/graphdiyne type2 type3
    """
    atoms = ase.io.read(
        '/Users/wangjinlong/my_server/my/myORR_B/slab/graphdiyne/CONTCAR', format='vasp')
    index_list = []
    for atom in atoms:
      if atom.position[0] > -0.68 and atom.position[0] < 10.3:
        if atom.position[1] > 2.3 and atom.position[1] < 13.1:
          index_list.append(atom.index)

    atoms = atoms[index_list]
    index_list2 = []
    for atom in atoms:
      if atom.index in [32, 25, 27, 31, 26, 24, 29, 33]:
        pass
      else:
        index_list2.append(atom.index)

    atoms_new = atoms[index_list2]
    atoms_new.center(0.7)
    for atom in atoms_new:
      atom.position[2] = 0

    atoms_new.cell[2] = [0.0, 0.0, 0]

    atoms_new.pbc = [True, True, False]
    atoms_new.center(vacuum=5, axis=2)
    return atoms_new

  def get_supercell_example(self, atoms_relaxed, size=(3, 3, 3),):
    lc = self.get_lc_a_from_atoms(atoms_relaxed=atoms_relaxed)
    atoms = ase.build.bulk('W', cubic=True, a=lc).repeat(size)
    return atoms

  def get_atoms_in_vaccum(self, symbols=['W', 'W'],
                          positions=[(0, 0, 0), (0, 0, 2.8)]):
    """用于 dimmer """
    atoms = ase.Atoms(symbols=symbols, positions=positions)
    atoms.center(vacuum=4)
    return atoms

  # 编辑修改方法
  def get_pos_center_list(self, atoms: ase.Atoms,
                          index_lists=[[26, 35, 36], [27, 39, 40], [30, 41, 42]]):
    pos_center_list = []
    for index_list in index_lists:
      pos_center = atoms[index_list].get_center_of_mass()*1.02
      pos_center_list.append(pos_center)
    return pos_center_list

  def get_vector_unit(self,
                      atoms: ase.Atoms,
                      vector_point_atom_index_list=[74, 75],):
    pos0 = atoms[vector_point_atom_index_list[0]].position
    pos1 = atoms[vector_point_atom_index_list[1]].position
    vector_arr = pos1 - pos0
    from soft_learn_project.numpy_learn import numpyLearn
    vector_unit_arr = numpyLearn.NumpyLearn().get_unit_vector(vector_arr=vector_arr)
    return vector_unit_arr

  def delete_atom(self,
                  atoms: ase.Atoms,
                  index_list=[29, 42],
                  symbol_list=None,
                  delete_neighbor=False,):
    """ * 去掉索引中或者索引近邻的原子
    - dbname 和 atoms 提供一个
    - index_list 和 symbol_list 设置其一

    Args:
        dbname(str, optional): _description_. Defaults to 'graphene72atoms'.
        atoms(_type_, optional): _description_. Defaults to None.
        index_list(list, optional): _description_. Defaults to[29, 42].
        symbol_list(_type_, optional): _description_. Defaults to None.
        delete_neighbor(bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """

    index_list, symbol_list = self.get_index_list_and_symbol_list(
        atoms=atoms,
        symbol_list=symbol_list,
        index_list=index_list)
    if delete_neighbor:
      neighbor_index_list = self.get_neighbor_index_list_wrapper(
          atoms=atoms,
          index_list=index_list,
          symbol_list=symbol_list)
      al = [atom.index for atom in atoms if atom.index not in neighbor_index_list]
    else:
      al = [atom.index for atom in atoms if atom.index not in index_list]

    return atoms[al]

  def replace_atom(self,
                   atoms: ase.Atoms,
                   atom_symbol_to_replace='Si',
                   atoms_index_replaced_list=[29, 42],):
    # 稍微有些偏移
    pos_center = atoms[atoms_index_replaced_list].get_center_of_mass()*1.01
    atom_to_replace = ase.Atom(
        symbol=atom_symbol_to_replace, position=pos_center)
    atoms.append(atom_to_replace)
    atoms = atoms[[
        atom.index for atom in atoms if atom.index not in atoms_index_replaced_list]]
    return atoms

  def replace_atom_wrapper(self, atoms: ase.Atoms,
                           index_lists=[[15, 28, 17], [
                               27, 39, 40], [30, 41, 42]],
                           symbol_list=['P', 'P', 'P'],

                           ):
    pos_center_list = self.get_pos_center_list(atoms=atoms,
                                               index_lists=index_lists)
    for symbol, pos in zip(symbol_list, pos_center_list):
      atoms = self.add_new_atom(atoms=atoms,
                                new_atom_symbol=symbol,
                                position=pos)
    atoms = self.delete_atom(atoms=atoms,
                             index_list=np.array(index_lists).flatten().tolist())
    return atoms

  def add_new_atom(self,
                   atoms: ase.Atoms,
                   new_atom_symbol,
                   position,):
    """根据位置增加新原子"""
    # 加入新的原子
    atom_new = ase.Atom(symbol=new_atom_symbol, position=position)
    atoms.append(atom_new)
    return atoms

  def add_new_atom_along_vector(self,
                                atoms: ase.Atoms,
                                new_atom_symbol,
                                vector_point_atom_index_list=[
                                    72, 73],
                                distance=1.1,
                                ref_index=72,
                                offset=[0, 0, 0]):
    """沿着矢量, 在距离为 distance 出增加 原子"""
    vector_unit = self.get_vector_unit(
        atoms=atoms,
        vector_point_atom_index_list=vector_point_atom_index_list,)
    pos = atoms[ref_index].position
    pos = pos + vector_unit * distance + offset
    atoms = self.add_new_atom(atoms=atoms.copy(),
                              new_atom_symbol=new_atom_symbol,
                              position=pos)
    return atoms

  def add_new_atoms_along_vector(self,
                                 atoms: ase.Atoms,
                                 new_atoms_name='H2O',
                                 new_atoms_roate_pars_dict={'a': 0,
                                                            'v': 'x',
                                                            'center': 'COP'},
                                 vector_point_atom_index_list=[
                                     72, 73],
                                 distance=0.98,
                                 ref_index=72,  # 72|73
                                 ):

    new_atoms = ase.build.molecule(name=new_atoms_name,)
    new_atoms.rotate(**new_atoms_roate_pars_dict)

    vector_unit = self.get_vector_unit(
        atoms=atoms,
        vector_point_atom_index_list=vector_point_atom_index_list,)

    pos = atoms[ref_index].position
    pos = pos + vector_unit * distance
    for atom in new_atoms:
      atom.position += pos
    atoms.extend(new_atoms)

    return atoms

  def set_atom_position(self,
                        atoms: ase.Atoms,
                        atom_index=72,
                        position=[0, 0, 0]):
    for atom in atoms:
      if atom.index == atom_index:
        atom.position = position
    return atoms

  def set_atom_position_along_vector(self,
                                     atoms: ase.Atoms,
                                     atom_index=72,
                                     vector_point_atom_index_list=[
                                         74, 75],
                                     distance=1.2,
                                     ref_index=74,
                                     offset=[0, 0, 0],
                                     ):
    """沿矢量设置原子位置, 相对于ref_index 作为起点
    """
    vector_unit_arr = self.get_vector_unit(atoms=atoms,
                                           vector_point_atom_index_list=vector_point_atom_index_list)
    pos0 = atoms[ref_index].position
    pos = pos0 + vector_unit_arr*distance
    pos += offset
    atoms = self.set_atom_position(atoms=atoms.copy(),
                                   atom_index=atom_index,
                                   position=pos)
    return atoms

  # 查看, 保存
  def get_atoms_from_traj(self,
                          directory='xx',
                          fname_traj=None,
                          index=':'):
    """从 traj 文件中获取 atoms
    """

    if fname_traj is None:
      fl = os.listdir(directory)
      for f in fl:
        if '.traj' in f:
          fname = os.path.join(directory, f)
          break
    else:
      fname = os.path.join(directory, fname_traj)
    atoms_list = ase.io.read(filename=fname, index=index)
    return atoms_list

  def view_atoms_from_traj(self, directory='xx',
                           viewer='ase',):
    """从 traj 文件中获取 atoms并查看
    viewer = 'ase|x3d|ngl'  对于单个atoms 可以使用 viewer = 'x3d|ngl'
    """
    atoms = self.get_atoms_from_traj(directory=directory,
                                     index=':',)
    ase.visualize.view(atoms, viewer=viewer)
    return None

  def get_atoms_conventional_or_primitive(self,
                                          atoms: ase.Atoms,
                                          cell_name='conventional|primitive'):
    from soft_learn_project.pymatgen_learn import pymatgenLearn
    atoms = pymatgenLearn.PymatgenLearn().get_atoms_conventional_or_primitive(
        atoms=atoms, cell_name=cell_name)
    return atoms

  def save_atoms(self, atoms: ase.Atoms,
                 fname='xxx/atoms.traj'
                 ):
    atoms.write(filename=fname)
    print(f'{fname} 保存为-> {fname}')
    return None

  def save_model(self, atoms: ase.Atoms,
                 directory='xxx'):
    """将建立的模型保存的文件, 因为建立模型的过程可能无法并行计算, 以后再说

    Args:
        atoms(ase.Atoms): _description_
        directory(str, optional): _description_. Defaults to 'xxx'.
    """

    if not os.path.exists(directory):
      os.makedirs(directory, exist_ok=True)
    fname = os.path.join(directory, 'atoms.traj')
    atoms.write(filename=fname)
    ase.parallel.parprint(f'atoms 文件保存在: {fname}')
    return None

  # 其它的方法
  def translate_atoms(self, atoms: ase.Atoms,
                      vector_fraction=[0.5, 0.5, 0]):
    """平移原子
    """
    cell = atoms.get_cell()
    # 构造平移向量（0.5 * a1 + 0.5 * a2）
    translation = np.zeros_like(vector_fraction)
    for v, lattice in zip(vector_fraction, cell):
      translation += v*lattice
    # 平移结构
    atoms.translate(translation)
    atoms.wrap()
    return atoms

  def get_lc_a_from_atoms(self,
                          atoms_relaxed: ase.Atoms,
                          ):
    """查看更多的晶格参数  primitive conventional
    bl = atoms.cell.get_bravais_lattice()
    bl.conventional()  # 传统晶胞
    bl.cellpar()  # 晶格参数
    """
    bl = atoms_relaxed.cell.get_bravais_lattice()
    bl.conventional()  # 传统晶胞
    bl.cellpar()  # 晶格参数
    lc_a = bl.a
    return lc_a

  def get_df_atoms_position(self,
                            fname_atoms='/Users/wangjinlong/Desktop/IS.pdb',
                            atoms=None,
                            is_save_excel=False,
                            sheet_name=None,
                            fname_excel='/Users/wangjinlong/Desktop/atoms_position.xlsx',
                            ):
    """  # 弃用, 已经放入 self.PaperSupplementaryInformation
    fname_atoms | atoms 给出一个, 另一个为 None
    """
    import pandas as pd
    from soft_learn_project.pandas_learn import pandasLearn
    if atoms is None:
      atoms = ase.io.read(fname_atoms)
    else:
      pass
    df = pd.DataFrame(data=atoms.positions, index=atoms.symbols,
                      columns=['x', 'y', 'z'],).sort_index()
    if is_save_excel:
      sheet_name = os.path.basename(
          fname_atoms) if sheet_name is None else sheet_name
      pandasLearn.PandasLearn().write_df2excel(df=df,
                                               fname=fname_excel,
                                               sheet_name=sheet_name,
                                               index=True)
    return df

  def get_atoms_dict(self, atoms: ase.Atoms):
    atoms_dict = atoms.todict()
    # mongodb 中不能存储 array 所以需要转换为 list
    atoms_dict_new = {}
    for k, v in atoms_dict.items():
      if isinstance(v, np.ndarray):
        v = v.tolist()
      atoms_dict_new[k] = v
    return atoms_dict_new

  def get_atoms_from_dict(self, atoms_dict):
    # 从字典中获取 atoms 对象
    atoms = ase.Atoms(symbols=atoms_dict['numbers'],
                      positions=atoms_dict['positions'],
                      cell=atoms_dict['cell'],
                      pbc=atoms_dict['pbc'])
    return atoms

  def get_atoms_index_from_symbol(self, atoms: ase.Atoms,
                                  symbols=['Si', 'P'],
                                  ):
    """找到atoms中的 元素的索引, 可以用于之后计算距离
    """
    symbol_list = atoms.get_chemical_symbols()
    symbol_arr = np.array(symbol_list)
    indices = np.where(np.isin(symbol_arr, symbols))[0]
    return indices

  def get_distance_from_symbol(self, atoms: ase.Atoms,
                               symbols=['Si', 'P'],):
    indices = self.get_atoms_index_from_symbol(atoms=atoms,
                                               symbols=symbols)
    distance = atoms[indices].get_distance(a0=0, a1=1)
    return distance

  # old code
  def WS2(self):
    # 构造WS2 模型
    import ase.lattice.hexagonal
    a = 3.160
    c = 12.0

    cell = ase.lattice.hexagonal.Hexagonal(
        symbol='W', latticeconstant={'a': a, 'c': c}).get_cell()
    layer = ase.Atoms(symbols='WS2', cell=cell, pbc=(1, 1, 1),
                      scaled_positions=[(0, 0, 0),
                                        (2 / 3, 1 / 3, 0.3),
                                        (2 / 3, 1 / 3, -0.3)])

    layer.center(axis=2)
    layer.set_pbc(True)
    pos = layer.get_positions()
    pos[1][2] = pos[0][2] + 3.172 / 2
    pos[2][2] = pos[0][2] - 3.172 / 2
    layer.set_positions(pos)
    return layer

  def MS2_plus_graphene(self,
                        metal='W',
                        ):
    import ase.lattice.hexagonal
    a = 3.160
    c = 12.0
    cell = ase.lattice.hexagonal.Hexagonal(
        symbol=metal, latticeconstant={'a': a, 'c': c}).get_cell()
    slab = ase.Atoms(symbols=metal+'S2', cell=cell, pbc=(1, 1, 1),
                     scaled_positions=[(0, 0, 0),
                                       (2 / 3, 1 / 3, 0.3),
                                       (2 / 3, 1 / 3, -0.3)])

    graphene: ase.Atoms = ase.build.graphene(formula='C2')
    graphene.set_cell(cell=cell, scale_atoms=True)
    slab += graphene
    slab.positions[-2:, 2] = slab.positions[0, 2] - 6
    return slab

  def get_silicene(self,):
    atoms: ase.Atoms = ase.build.graphene(vacuum=15)
    atoms.pbc = True
    atoms[0].position += [0, 0, 0.15]
    atoms[1].position += [0, 0, -0.15]
    atoms.set_chemical_symbols(['Si', 'Si'])

    # view(atoms)
    # 优化
    string = """
    from vasp_learn import calculation
    calculation.Calculations().calc_relax_2dimention_material(atoms=atoms,
                                                                         directory='/Users/wangjinlong/my_server/my/myORR_B/bulks/silicene',
                                                                         only_write_inputs=False)
    """
    print(f'优化-> \n{string}')
    return atoms


class Moduli():
  def __init__(self):
    """计算各种模量, 体块模量, 杨氏模量等"""
    pass

  def calc_bulk_modulus(self, atoms: ase.Atoms,
                        calc: ase.calculators.calculator.Calculator,
                        nums_config=5,
                        is_plot=False,
                        is_reacalc=False,
                        ):
    """atoms = ase.build.bulk('W', cubic=True,
                        a=3.17)
    """
    fname_traj = os.path.join(calc.directory, 'atoms.traj')
    if os.path.exists(fname_traj) and (not is_reacalc):
      pass
    else:
      atoms.calc = calc
      cell = atoms.get_cell()
      traj = ase.io.trajectory.Trajectory(fname_traj, mode='w')
      for x in np.linspace(0.95, 1.05, nums_config):
        atoms.set_cell(cell * x, scale_atoms=True)
        atoms.get_potential_energy()
        traj.write(atoms)

    # read 5 configurations
    configs = ase.io.read(filename=fname_traj,
                          index=f'-{nums_config}:')
    # Extract volumes and energies:
    volumes = [atoms.get_volume() for atoms in configs]
    energies = [atoms.get_potential_energy() for atoms in configs]
    eos = ase.eos.EquationOfState(volumes=volumes,
                                  energies=energies)
    # 体系的最小体积和最小能量
    v0, e0, bulk_modulus = eos.fit()

    bulk_modulus = bulk_modulus / ase.units.kJ * 1.0e24  # GPa
    if is_plot:
      eos.plot()
    return bulk_modulus

  def convert_Cijkl_to_Cvoigt(self, C_ijkl):
    """ 另一种方法:

    def convert_Cijkl_to_voigt(self, c_ijkl):
      voigt_matrix = np.zeros((6, 6))
      voigt_pairs = [(0, 0), (1, 1), (2, 2), (1, 2), (0, 2), (0, 1)]

      for i_voigt, (i, j) in enumerate(voigt_pairs):
        for j_voigt, (k, l) in enumerate(voigt_pairs):
          voigt_matrix[i_voigt, j_voigt] = c_ijkl[i, j, k, l]
      return voigt_matrix
    """
    C_voigt = np.zeros((6, 6))
    for i in range(3):
      for j in range(3):
        Ia = ase.stress.full_3x3_to_voigt_6_index(i, j)
        for k in range(3):
          for lb in range(3):
            J = ase.stress.full_3x3_to_voigt_6_index(k, lb)
            C_voigt[Ia, J] = C_ijkl[i, j, k, lb]
    return C_voigt

  def calc_elasticity_tensor(self,
                             atoms: ase.Atoms,
                             calc,
                             h=1e-3,
                             ):
    """atoms = ase.build.bulk('W', a=3.14, cubic=True)
    calc = alib.get_calc(directory='xx')
    """

    atoms.calc = calc
    C_ijkl = ase.stress.get_elasticity_tensor(atoms=atoms,
                                              h=h,
                                              )
    C_ijkl = C_ijkl / ase.units.kJ * 1.0e24  # GPa
    return C_ijkl

  def get_moduli_from_C_voigt(self, C_voigt):
    # Voigt 平均体模量
    Bv = (C_voigt[0, 0] + C_voigt[1, 1] + C_voigt[2, 2] + 2 *
          (C_voigt[0, 1] + C_voigt[0, 2] + C_voigt[1, 2])) / 9

    # Voigt 平均剪切模量
    Gv = ((C_voigt[0, 0] + C_voigt[1, 1] + C_voigt[2, 2]) - (C_voigt[0, 1] + C_voigt[0, 2] + C_voigt[1, 2])) \
        / 15 + (C_voigt[3, 3] + C_voigt[4, 4] + C_voigt[5, 5]) / 5

    # Reuss 平均剪切模量需要先计算 S = C^-1
    S = np.linalg.inv(C_voigt)

    Br = 1.0 / (S[0, 0] + S[1, 1] + S[2, 2] +
                2 * (S[0, 1] + S[0, 2] + S[1, 2]))

    Gr = 15.0 / (4 * (S[0, 0] + S[1, 1] + S[2, 2]) -
                 4 * (S[0, 1] + S[0, 2] + S[1, 2]) +
                 3 * (S[3, 3] + S[4, 4] + S[5, 5]))

    # Hill 平均
    B = (Bv + Br) / 2
    G = (Gv + Gr) / 2

    # 杨氏模量 和 泊松比
    E = 9 * B * G / (3 * B + G)
    nu = (3 * B - 2 * G) / (2 * (3 * B + G))

    data = {'Bulk_modulus_B_Hill': B,
            'Shear_modulus_G_Hill': G,
            'Youngs_modulus_E': E,
            'Poissons_ratio_nu': nu
            }
    return data

  def calc_moduli_wrapper(self,
                          atoms: ase.Atoms,
                          calc,
                          h=1e-3,):
    C_ijkl = self.calc_elasticity_tensor(atoms=atoms.copy(),
                                         calc=calc,
                                         h=h,)
    C_voigt = self.convert_Cijkl_to_Cvoigt(C_ijkl=C_ijkl)
    data_dict = self.get_moduli_from_C_voigt(C_voigt=C_voigt)
    return data_dict


class NEB():
  def __init__(self):
    r"""https: // wiki.fysik.dtu.dk/ase/tutorials/tutorials.html  # calculating-diffusion-dissociation-properties
    https: // wiki.fysik.dtu.dk/ase/ase/neb.html  # module-ase.mep.neb
    references: \cite{henkelman2000improved, henkelman2000climbing, smidstrup2014improved, lindgren2019scaled}
    """
    super().__init__()

  def get_neb_instance_serial(self,
                              initial: ase.Atoms,
                              final: ase.Atoms,
                              calc_func,
                              directory='xxx/neb',
                              nimages=3,
                              neb_method='string',
                              mic=False,
                              ):
    """ 推荐使用 dyneb
    --- 参考下面的代码
    from soft_learn_project.gpaw_learn import gpawLearn
    gpawLearn.Features().TSTcalc.get_neb_instance_gpaw_serial()
    """
    if not os.path.exists(directory):
      os.makedirs(directory, exist_ok=True)

    images = [initial]
    for i in range(nimages):
      image = initial.copy()
      # calc = gpaw.calculator.GPAW(txt=os.path.join(directory,
      #                                              f'neb{i+1:d}.txt'),
      #                             **initial.calc.parameters,
      #                             )
      # calc.set(**initial.calc.parameters,)
      # calc.set(**calc_pars_dict)
      # calc.set(**kwargs)
      image.calc = calc_func()
      images.append(image)
    images.append(final)
    # ---
    neb_instance = ase.mep.NEB(images=images,
                               parallel=False,
                               climb=True,
                               method=neb_method,
                               )
    neb_instance.interpolate(method='idpp', mic=mic)
    return neb_instance

  def get_neb_instance_parallel(self, initial, final,
                                calc_func=ase.calculators.emt.EMT,
                                nimages=3,
                                neb_method='aseneb',
                                parallel=True,
                                mic=False):
    """mpiexec -np $nimages gpaw-python diffusion3.py

    把下面的内容写入文件好像必须是gpaw 环境 运行时: mpiexec - np 3 gpaw python nebparallel.py
    mpiexec - np 3 gpaw python nebparallel.py
    ---
    aseneb: standard ase NEB implementation
    improvedtangent: Paper I NEB implementation
    eb: Paper III full spring force implementation
    spline: Paper IV spline interpolation(supports precon)
    string: Paper IV string interpolation

    neb_method = 'aseneb|improvedtangent|eb|spline|string'
    """
    images = [initial]
    j = ase.parallel.world.rank * nimages // ase.parallel.world.size  # my image number
    for i in range(nimages):
      image = initial.copy()
      if i == j:
        image.calc = calc_func()
      image.set_constraint(initial.constraints)
      images.append(image)
    images.append(final)

    neb = ase.mep.NEB(images, climb=True,
                      parallel=parallel,
                      method=neb_method)
    neb.interpolate(method='idpp', mic=mic)
    return neb

  def get_neb_instance(self, initial, final,
                       calc_func=ase.calculators.emt.EMT,
                       nimages=3,
                       neb_method='aseneb',
                       parallel=False,
                       mic=False):
    """
    if parallel 则必须在py文件中执行: mpiexec -np 3 gpaw python nebparallel.py
    ---
    aseneb: standard ase NEB implementation
    improvedtangent: Paper I NEB implementation
    eb: Paper III full spring force implementation
    spline: Paper IV spline interpolation(supports precon)
    string: Paper IV string interpolation

    neb_method = 'aseneb|improvedtangent|eb|spline|string'
    """
    images = [initial]
    j = ase.parallel.world.rank * nimages // ase.parallel.world.size  # my image number
    for i in range(nimages):
      image = initial.copy()
      if parallel:
        if i == j:
          image.calc = calc_func()
      else:
        image.calc = calc_func()
      image.set_constraint(initial.constraints)
      images.append(image)
    images.append(final)

    allow_shared_calculator = False if parallel else True
    neb = ase.mep.NEB(images, climb=True,
                      parallel=parallel,
                      method=neb_method,
                      allow_shared_calculator=allow_shared_calculator)
    neb.interpolate(method='idpp', mic=mic)
    return neb

  def run_neb(self, neb_instance: ase.mep.NEB,
              directory='xx/neb',
              fmax=0.05,
              opt_name='lbfgs',
              opt_pars_dict={'loginterval': 1},
              is_save_log=True,
              is_save_traj=True,
              is_recalc=False,
              ):
    """获得 neb.traj 然后用于分析
    opt_name = 'bfgs|fire|mdmin'
    ---
    qn = ase.optimize.BFGS(neb, trajectory='neb.traj')
    qn.run(fmax=0.05)
    """
    if not os.path.exists(directory):
      os.makedirs(name=directory, exist_ok=True)

    logfile = os.path.join(directory, 'neb.log') if is_save_log else None
    trajectory = os.path.join(directory, 'neb.traj')

    if os.path.exists(trajectory) and (not is_recalc):
      ase.parallel.parprint(f'trajectory 文件存在-> {trajectory}')
    else:
      opt = self.AseLearn.get_opt(atoms=neb_instance,
                                  opt_name=opt_name,
                                  is_save_log=is_save_log,
                                  logfile=logfile,
                                  is_save_traj=is_save_traj,
                                  trajectory=trajectory,
                                  **opt_pars_dict,
                                  )
      opt.run(fmax=fmax)
      return neb_instance

  def get_iamges_from_fname_traj(self,
                                 fname_traj,
                                 nimages=5,):
    """获得最后迟豫的几个 images
    nimages: 总图像数目
    """
    images = ase.io.read(f'{fname_traj}@-{nimages:d}:')
    return images

  def analysis_neb(self, images,
                   is_plot=True,
                   is_save=False,
                   fname_pdf='xxx/neb.pdf',):
    """images = self.get_iamges_from_fname_traj(fname_traj=fname_traj,
                                             nimages=nimages)
    # Get the calculated barrier and the energy change of the reaction.
    Ef, dE = nebtools.get_barrier()
    ---
    # Get the barrier without any interpolation between highest images.
    Ef, dE = nebtools.get_barrier(fit=False)
    ---
    # Get the actual maximum force at this point in the simulation.
    max_force = nebtools.get_fmax()
    """
    # 如果要 restart neb 读取
    nebtools = ase.mep.NEBTools(images)
    if is_plot:
      # Create a figure like that coming from ASE-GUI.
      # fig = nebtools.plot_band()
      # fig.savefig('diffusion-barrier.png')

      # Create a figure with custom parameters.
      fig = plt.figure(figsize=(5.5, 4.0))
      ax = fig.add_axes((0.15, 0.15, 0.8, 0.75))
      fig = nebtools.plot_band(ax)
      from soft_learn_project.matplotlib_learn import matplotlibLearn
      if is_save:
        matplotlibLearn.Features().savefig(fig=fig,
                                           fname=fname_pdf)
    return nebtools

  def run_neb_wrapper(self,
                      initial,
                      final,
                      calc_func,
                      directory='.',
                      nimages=3,
                      parallel=False,
                      mic=False,
                      is_save_log=False,
                      is_save_traj=False,
                      opt_name='mdmin',
                      fmax=0.05,
                      is_recalc=False,
                      is_plot_fig=True,
                      is_save_fig=False,
                      ):
    """分析用到了 fname_traj
    """
    neb = self.get_neb_instance(
        initial=initial,
        final=final,
        calc_func=calc_func,
        nimages=nimages,
        parallel=parallel,
        mic=mic,
    )
    neb_instance = self.run_neb(neb_instance=neb,
                                directory=directory,
                                fmax=fmax,
                                opt_name=opt_name,
                                is_save_log=is_save_log,
                                is_save_traj=is_save_traj,
                                is_recalc=is_recalc,
                                )

    if parallel:  # 并行不能进行分析
      return neb_instance
    else:
      # images = self.get_iamges_from_fname_traj(
      #     fname_traj=os.path.join(directory, 'neb.traj'), nimages=nimages+2)
      if ase.parallel.world.rank == 0:
        nebtools = self.analysis_neb(images=neb_instance.images,
                                     is_plot=is_plot_fig,
                                     is_save=is_save_fig,
                                     fname_pdf=os.path.join(
                                         directory, 'neb.pdf'),
                                     )
        # E_barrier_forward, dE = nebtools.get_barrier()
        return nebtools

  def restart_neb(self, images,
                  directory,
                  ):
    """ Restart NEB from the trajectory file:
    # read the last structures (of 5 images used in NEB)
    images = ase.io.read('neb.traj@-5:')

    Args:
        directory(_type_): _description_
        fname_traj(str, optional): _description_. Defaults to 'neb_restart.traj'.
        images(_type_, optional): _description_. Defaults to None.
    """

    for i in range(1, len(images) - 1):
      images[i].calc = ase.calculators.emt.EMT()

    neb = ase.mep.NEB(images)
    self.run_neb(neb_instance=neb,
                 directory=directory,
                 )
    return None

  # ---
  def get_neb_IF_example(self, calc_func,
                         name='W',
                         lc_a=3.14,
                         box_size=[4]*3,):
    """
    get_initial_final_for_vacancy_migration in W
    """
    atoms = ase.build.bulk(name=name, cubic=True, a=lc_a,)
    atoms = atoms.repeat(box_size)
    # 获得初态结构
    atom_A_index = 0
    atom_B_index = Model().get_neighbors_list(
        atoms=atoms,
        atom_index=atom_A_index,
        distance_max=3,
    )[0]
    initial = Model().delete_atom(
        atoms=atoms,
        index_list=[atom_A_index],
    )
    # 获取终态结构
    final = Model().delete_atom(
        atoms=atoms,
        index_list=[atom_B_index],
    )
    initial = AseLearn().calc_relaxation_general(atoms=initial,
                                                 calc=calc_func(),)
    final = AseLearn().calc_relaxation_general(atoms=final,
                                               calc=calc_func(),)
    data: dict = {'initial': initial,
                  'final': final}

    return data

  def get_neb_IF_example1(self, calc_func):
    """Au on Al surface
    0.374 eV"""
    # 2x2-Al(001) surface with 3 layers and an
    # Au atom adsorbed in a hollow site:
    slab = ase.build.fcc100('Al', size=(2, 2, 3))
    ase.build.add_adsorbate(slab, 'Au', 1.7, 'hollow')
    slab.center(axis=2, vacuum=4.0)

    # Make sure the structure is correct:
    # view(slab)

    # Fix second and third layers:
    mask = [atom.tag > 1 for atom in slab]
    # print(mask)
    slab.set_constraint(ase.constraints.FixAtoms(mask=mask))
    # Use EMT potential:
    slab.calc = calc_func()

    # Initial state:
    qn = ase.optimize.QuasiNewton(slab,)
    qn.run(fmax=0.05)
    initial = copy.deepcopy(slab)

    # Final state:
    slab[-1].x += slab.get_cell()[0, 0] / 2
    qn = ase.optimize.QuasiNewton(slab,)
    qn.run(fmax=0.05)
    final = copy.deepcopy(slab)
    data_atoms = {'initial': initial, 'final': final}
    return data_atoms

  def get_neb_IF_example2(self,
                          calc_func=ase.calculators.emt.EMT,
                          ):
    # Some algebra to determine surface normal and the plane of the surface.
    d3 = [2., 1., 1.]
    a1 = np.array([0., 1., 1.])
    d1 = np.cross(a1, d3)
    a2 = np.array([0., -1., 1.])
    d2 = np.cross(a2, d3)

    # Create the slab.
    slab = ase.lattice.cubic.FaceCenteredCubic(directions=np.array([d1, d2, d3]).astype(int),
                                               size=(2, 1, 2),
                                               symbol=('Pt'),
                                               latticeconstant=3.9)

    # # Add some vacuum to the slab.
    uc = slab.get_cell()
    uc[2] += [0., 0., 10.]  # There are ten layers of vacuum.
    uc = slab.set_cell(uc, scale_atoms=False)

    # Some positions needed to place the atom in the correct place.
    x1 = 1.379
    x2 = 4.137
    x3 = 2.759
    y1 = 0.0
    y2 = 2.238
    z1 = 7.165
    z2 = 6.439

    # # Add the adatom to the list of atoms and set constraints of surface atoms.
    slab += ase.Atoms('N', [((x2 + x1) / 2, y1, z1 + 1.5)])
    mask = [atom.symbol == 'Pt' for atom in slab]
    slab.set_constraint(ase.constraints.FixAtoms(mask=mask))

    # # Optimise the initial state: atom below step.
    initial = slab.copy()
    initial.calc = calc_func()
    relax = ase.optimize.fire.FIRE(initial,)
    relax.run(fmax=0.05)

    # Optimise the final state: atom above step.
    slab[-1].position = (x3, y2 + 1., z2 + 3.5)
    final = slab.copy()
    final.calc = calc_func()
    relax = ase.optimize.fire.FIRE(final,)
    relax.run(fmax=0.05)

    data = {'initial': initial, 'final': final}
    return data

  def get_neb_IF_example3(self,
                          calc_func,):
    """N2 dissociation on Cu(111) surface """
    # The first step is to find the relaxed structures of the initial and final states.
    # Find the initial and final states for the reaction.

    # Set up a (4 x 4) two layer slab of Cu:
    slab: ase.Atoms = ase.build.fcc111('Cu', size=(4, 4, 2))
    slab.set_pbc((1, 1, 0))

    # Initial state.
    # Add the N2 molecule oriented at 60 degrees:
    d = 1.10  # N2 bond length
    N2mol = ase.Atoms('N2', positions=[[0.0, 0.0, 0.0],
                                       [0.5 * 3**0.5 * d, 0.5 * d, 0.0]])
    ase.build.add_adsorbate(slab, N2mol, height=1.0, position='fcc')

    # We don't want to worry about the Cu degrees of freedom, so fix these atoms:

    mask = [atom.symbol == 'Cu' for atom in slab]
    slab.set_constraint(ase.constraints.FixAtoms(mask=mask))
    # slab.set_constraint(ase.constraints.FixAtoms(indices=[0])

    # Relax the structure
    self.AseLearn.calc_relaxation_general(
        atoms=slab,
        calc=calc_func(),
    )

    initial = copy.deepcopy(slab)
    # Now the final state.
    # Move the second N atom to a neighboring hollow site:
    slab[-1].position[0] = slab[-2].position[0] + 0.25 * slab.cell[0, 0]
    slab[-1].position[1] = slab[-2].position[1]
    # and relax.
    self.AseLearn.calc_relaxation_general(
        atoms=slab,
        calc=calc_func(),)
    final = copy.deepcopy(slab)
    data = {'initial': initial, 'final': final}
    return data

  def get_neb_IF_example4(self, calc_func,):
    """neb 之前先迟豫始末结构能够加快优化, 并且建议使用IDPP方法
    Ethane H 绕C-C 键旋转
    This example illustrates the use of the IDPP interpolation scheme to generate an initial guess for rotation of a methyl group around the CC bond.
    """

    # Create initial state.
    initial = ase.build.molecule('C2H6', vacuum=4, pbc=True)
    self.AseLearn.calc_relaxation_general(atoms=initial,
                                          calc=calc_func())
    initial = copy.deepcopy(initial)
    # Create final state.
    final = initial.copy()
    final.positions[2:5] = initial.positions[[3, 4, 2]]
    self.AseLearn.calc_relaxation_general(atoms=final,
                                          calc=calc_func())
    final = copy.deepcopy(final)
    data = {'initial': initial, 'final': final}
    return data

  def get_neb_IF_example5(self, calc_func,):
    """N on Pt(111) surface."""
    # Some algebra to determine surface normal and the plane of the surface.
    d3 = [2, 1, 1]
    a1 = np.array([0, 1, 1])
    d1 = np.cross(a1, d3)
    a2 = np.array([0, -1, 1])
    d2 = np.cross(a2, d3)
    d1.astype(int)
    d2.astype(int)
    # Create the slab.
    slab = ase.lattice.cubic.FaceCenteredCubic(directions=[d1, d2, d3],
                                               size=(2, 1, 2),
                                               symbol=('Pt'),
                                               latticeconstant=3.9)
    # Add some vacuum to the slab.
    uc = slab.get_cell()
    uc[2] += [0., 0., 10.]  # There are ten layers of vacuum.
    uc = slab.set_cell(uc, scale_atoms=False)

    # Some positions needed to place the atom in the correct place.
    x1 = 1.379
    x2 = 4.137
    x3 = 2.759
    y1 = 0.0
    y2 = 2.238
    z1 = 7.165
    z2 = 6.439

    # Add the adatom to the list of atoms and set constraints of surface atoms.
    slab += ase.Atoms('N', [((x2 + x1) / 2, y1, z1 + 1.5)])
    mask = [atom.symbol == 'Pt' for atom in slab]
    slab.set_constraint(ase.constraints.FixAtoms(mask=mask))

    # Optimise the initial state: atom below step.
    initial = slab.copy()
    self.AseLearn.calc_relaxation_general(atoms=initial,
                                          calc=calc_func(),)
    initial = copy.deepcopy(initial)

    # Optimise the final state: atom above step.
    slab[-1].position = (x3, y2 + 1., z2 + 3.5)
    final = slab.copy()
    self.AseLearn.calc_relaxation_general(atoms=final,
                                          calc=calc_func(),)
    final = copy.deepcopy(final)

    data = {'initial': initial, 'final': final}
    return data

  def get_neb_IF_example6(self, calc_func,):
    """Diffusion along rows
    self_diffusion_on_Al_surface_using_the_NEB_and_Dimer_path1
    """

    a = 4.0614
    b = a / np.sqrt(2)
    h = b / 2
    initial = ase.Atoms('Al2',
                        positions=[(0, 0, 0),
                                   (a / 2, b / 2, -h)],
                        cell=(a, b, 2 * h),
                        pbc=(1, 1, 0))
    initial *= (2, 2, 2)
    initial.append(ase.Atom('Al', (a / 2, b / 2, 3 * h)))
    initial.center(vacuum=4.0, axis=2)

    final = initial.copy()
    final.positions[-1, 1] += b

    # Make a mask of zeros and ones that select fixed atoms (the
    # two bottom layers):
    mask = initial.positions[:, 2] - min(initial.positions[:, 2]) < 1.5 * h
    constraint = ase.constraints.FixAtoms(mask=mask)

    initial.set_constraint(constraint=constraint)
    final.set_constraint(constraint=constraint)
    self.AseLearn.calc_relaxation_general(atoms=initial,
                                          calc=calc_func(),
                                          )
    self.AseLearn.calc_relaxation_general(atoms=final,
                                          calc=calc_func(),)
    data = {'initial': initial,
            'final': final}
    print('参考能垒:  126 meV')
    return data

  def get_neb_IF_example7(self, calc_func,):
    """Diffusion by an exchange process
    Self_diffusion_on_Al_surface_using_the_NEB_and_Dimer_path2
    """

    a = 4.0614
    b = a / np.sqrt(2)
    h = b / 2
    initial = ase.Atoms('Al2',
                        positions=[(0, 0, 0),
                                   (a / 2, b / 2, -h)],
                        cell=(a, b, 2 * h),
                        pbc=(1, 1, 0))
    initial *= (2, 2, 2)
    initial.append(ase.Atom('Al', (a / 2, b / 2, 3 * h)))
    initial.center(vacuum=4.0, axis=2)

    final = initial.copy()
    # move adatom to row atom 14
    final.positions[-1, :] = initial.positions[14]
    # Move row atom 14 to the next row
    final.positions[14, :] = initial.positions[-1] + [a, b, 0]
    # ase.visualize.view([initial, final])

    # Make a mask of zeros and ones that select fixed atoms (the two bottom layers):
    mask = initial.positions[:, 2] - min(initial.positions[:, 2]) < 1.5 * h
    constraint = ase.constraints.FixAtoms(mask=mask)

    initial.set_constraint(constraint)
    final.set_constraint(constraint)

    self.AseLearn.calc_relaxation_general(atoms=initial,
                                          calc=calc_func()
                                          )
    self.AseLearn.calc_relaxation_general(atoms=final,
                                          calc=calc_func())
    data = {'initial': initial,
            'final': final, }
    print('参考能垒: 235 meV')
    return data

  def run_neb_wrapper_parallel_example(self, directory='.',):
    def run():
      from . import aseLearn
      import ase.calculators.emt
      calc_func = ase.calculators.emt.EMT
      # calc_func = mypaper.JanusCoreFeatures.get_calc_MLIP
      data = aseLearn.AseFeatures().NEB.get_neb_IF_example(calc_func=calc_func)
      aseLearn.AseFeatures().NEB.run_neb_wrapper(
          initial=data['initial'],
          final=data['final'],
          directory='.',
          calc_func=calc_func,
          parallel=False,
          opt_name='lbfgs',
          nimages=3,
          is_recalc=True,
          is_save_fig=True,
      )
    self.AseLearn.write_py_from_code(func=run,
                                     directory=directory)
    return None

  def surface_diffusion_energy_barriers_using_ASE_constraints(self):
    """ * 放弃这种 没有neb 好用
    https://wiki.fysik.dtu.dk/ase/tutorials/constraints/diffusion.html
    Surface diffusion energy barriers using ASE constraints
    Here, we use a simple FixedPlane constraint that forces the Au atom to relax in the yz-plane only:
    """

    # 2x2-Al(001) surface with 3 layers and an
    # Au atom adsorbed in a hollow site:
    slab: ase.Atoms = ase.build.fcc100('Al', size=(2, 2, 3))
    ase.build.add_adsorbate(slab, 'Au', 1.7, 'hollow')
    slab.center(axis=2, vacuum=4.0)

    # Fix second and third layers:
    mask = [atom.tag > 1 for atom in slab]
    # print(mask)
    fixlayers = ase.constraints.FixAtoms(mask=mask)

    # Constrain the last atom (Au atom) to move only in the yz-plane:
    plane = ase.constraints.FixedPlane(-1, (1, 0, 0))

    slab.set_constraint([fixlayers, plane])

    # Use EMT potential:
    slab.calc = ase.calculators.emt.EMT()

    for i in range(5):
      qn = ase.optimize.QuasiNewton(slab, trajectory='mep%d.traj' % i)
      # qn = QuasiNewton(slab, trajectory='mep_constrian.traj')  # 不行
      qn.run(fmax=0.05)
      # Move gold atom along x-axis:
      slab[-1].x += slab.get_cell()[0, 0] / 8
    # The result can be analysed with the command ase gui mep?.traj -n -1 (choose Tools ‣ NEB). The barrier is found to be 0.35 eV - exactly as in the NEB tutorial.
    # 命令行看图
    # $ase gui mep?.traj -n -1
    pass

  def get_dimer_instance(self,
                         atoms_initial: ase.Atoms,
                         ):
    """The dimer method is a means of finding a saddle point on a potential energy surface starting from a single point(as opposed to a NEB calculation, which requires an initial and final state). You can read about this method here:

    ‘A dimer method for finding saddle points on high dimensional potential surfaces using only first derivatives’, G. Henkelman and H. Jonsson, J. Chem. Phys. 111, 7010, 1999.

    Args:
        atoms_initial(ase.Atoms): _description_

    Returns:
        _type_: _description_
    """
    N = len(atoms_initial)
    # Making dimer mask list:
    d_mask = [False] * (N - 1) + [True]

    # Set up the dimer:
    d_control = ase.mep.dimer.DimerControl(
        initial_eigenmode_method='displacement',
        displacement_method='vector',
        logfile=None,
        mask=d_mask)
    d_atoms = ase.mep.dimer.MinModeAtoms(atoms=atoms_initial,
                                         control=d_control)
    # 使Al沿着y方向加一个位移
    displacement_vector = np.zeros((N, 3))
    displacement_vector[-1, 1] = 0.001  # 可以查看这个变量
    d_atoms.displace(displacement_vector=displacement_vector)
    return d_atoms

  def run_dimer(self, directory,
                atoms_initial: ase.Atoms,
                dimer_instance: ase.mep.dimer.DimerAtoms,
                ):
    fname_traj = os.path.join(directory, 'dimer.traj')
    traj = ase.io.Trajectory(fname_traj, 'w', atoms_initial)
    traj.write()  # 执行这个才会写入 initial 对象
    fname_log = os.path.join(directory, 'dimer.txt')
    # Converge to a saddle point:
    dim_rlx = ase.mep.dimer.MinModeTranslate(
        dimeratoms=dimer_instance,
        trajectory=traj,
        logfile=fname_log)
    dim_rlx.run(fmax=0.001)
    return dimer_instance

  def Self_diffusion_on_Al_surface_using_the_NEB_and_Dimer_dimer(
          self,
          directory='/Users/wangjinlong/job/soft_learn/soft_learn_project/ase_learn/my_examples/Self_diffusion_on_Al_surface_using_the_NEB_and_Dimer_dimer',
  ):
    """Dimer: Diffusion along rows
    在上面的NEB计算中我们知道最终状态，所以我们要做的就是计算初始状态和最终状态之间的路径。但在某些情况下，我们不知道最终状态。然后用二聚体法找到过渡态。因此，二聚体计算的结果将不是NEB输出中的完整粒子轨迹，而是过渡状态图像的配置。
    """

    # Setting up the initial image:
    a = 4.0614
    b = a / np.sqrt(2)
    h = b / 2
    initial = ase.Atoms('Al2',
                        positions=[(0, 0, 0),
                                   (a / 2, b / 2, -h)],
                        cell=(a, b, 2 * h),
                        pbc=(1, 1, 0))
    initial *= (2, 2, 2)
    initial.append(ase.Atom('Al', (a / 2, b / 2, 3 * h)))
    initial.center(vacuum=4.0, axis=2)

    # N = len(initial)  # number of atoms

    # Make a mask of zeros and ones that select fixed atoms - the two
    # bottom layers:
    mask = initial.positions[:, 2] - min(initial.positions[:, 2]) < 1.5 * h
    constraint = ase.constraints.FixAtoms(mask=mask)
    initial.set_constraint(constraint)

    # Calculate using EMT:
    calc = self.AseLearn.get_light_calc_emt(directory=directory)
    self.AseLearn.calc_relaxation_general(atoms=initial,
                                          calc=copy.deepcopy(calc),
                                          fname_traj='initial.traj',
                                          opt_name='bfgs')
    e0 = initial.get_potential_energy()

    # Making dimer mask list:
    # d_mask = [False] * (N - 1) + [True]

    dimer_instance = self.get_dimer_instance(atoms_initial=initial,)
    dimer_instance = self.run_dimer(directory=directory,
                                    atoms_initial=initial,
                                    dimer_instance=dimer_instance,)
    # diff = dimer_instance.atoms.get_potential_energy() - dimer_instance.atoms0.get_potential_energy()
    # diff = initial.get_potential_energy() - e0
    diff = dimer_instance.get_potential_energy() - e0
    print(f'The energy barrier is {diff:f} eV.')
    return dimer_instance

  def dimer_example(self,
                    directory='/Users/wangjinlong/job/soft_learn/soft_learn_project/ase_learn/my_examples/dimer_example'):
    """https: // wiki.fysik.dtu.dk/ase/ase/dimer.html
    """
    import ase
    import ase.build
    # Set up a small "slab" with an adatoms
    atoms: ase.Atoms = ase.build.fcc100('Pt', size=(2, 2, 1), vacuum=10.0)
    ase.build.add_adsorbate(atoms, 'Pt', 1.611, 'hollow')

    # Freeze the "slab"
    mask = [atom.tag > 0 for atom in atoms]
    atoms.set_constraint(ase.constraints.FixAtoms(mask=mask))

    # Calculate using EMT
    calc = self.AseLearn.get_light_calc_emt(directory=directory)
    self.AseLearn.calc_relaxation_general(atoms=atoms,
                                          calc=calc,
                                          fname_traj='initial.traj')

    # Set up the dimer
    import ase.mep.dimer
    with ase.mep.dimer.DimerControl(
            initial_eigenmode_method='displacement',
            displacement_method='vector', logfile=None,
            mask=[0, 0, 0, 0, 1]) as d_control:
      d_atoms = ase.mep.dimer.MinModeAtoms(atoms, d_control)

      # Displace the atoms
      displacement_vector = [[0.0] * 3] * 5
      displacement_vector[-1][1] = -0.1
      d_atoms.displace(displacement_vector=displacement_vector)

      # Converge to a saddle point
      d_atoms = self.run_dimer(directory=directory,
                               atoms_initial=atoms,
                               dimer_instance=d_atoms,)
      diff = d_atoms.atoms.get_potential_energy() - d_atoms.atoms0.get_potential_energy()
      print(f'能垒为 {diff} eV')
      fname_traj = os.path.join(directory, 'dimer.traj')
      images = ase.io.read(filename=fname_traj, index=':')
    return images

  # other
  def Scaled_and_dynamic_optimizations(self):
    # import ase.mep
    # ase.mep.dyneb.DyNEB
    pass

  def auto_NEB(self):
    # class
    # import ase.mep.autoneb
    # ase.mep.autoneb.AutoNEB
    pass


class CalcModule():
  def __init__(self):
    super().__init__()
    from soft_learn_project.janus_core_learn import janus_coreLearn
    self.get_calc_MLIP = janus_coreLearn.JanuscoreLearn().get_calc_MLIP
    from soft_learn_project.lammps_learn import lammpsLearn
    self.get_calc_lammps = lammpsLearn.LammpsLearn().get_calc
    # 这两个不兼容？ 不知道为什么
    from soft_learn_project.vasp_learn import vaspLearn
    self.get_calc_vasp = vaspLearn.AseVaspLearn().get_calc
    from soft_learn_project.gpaw_learn import gpawLearn
    self.get_calc_gpaw = gpawLearn.GpawLearn().get_calc

    import ase.calculators.lj
    self.get_calc_LennardJones = ase.calculators.lj.LennardJones
    pass

  def get_calc_mace_func_old(self, default_dtype="float32"):
    import pathlib
    CURRENT_DIR = pathlib.Path(__file__).parent
    fpath = CURRENT_DIR / 'data' / 'mace-mpa-0-medium.model'
    from soft_learn_project.mace_learn import maceLearn
    get_calc = maceLearn.MaceLearn().get_calc
    calc = maceLearn.MaceLearn().get_calc(model_paths=[fpath],
                                          device='cpu',
                                          default_dtype=default_dtype)
    return calc


class Examples():
  def __init__(self):
    pass

  def get_calc(self,
               directory='.',
               **kwargs):
    """示例, 对于lammps 和 gpaw 需要另外设置
    log_file = 'None|xxx/calc.log'
    """
    if not os.path.exists(directory):
      os.makedirs(directory)

    calc = ase.calculators.calculator.Calculator(directory=directory,
                                                 **kwargs,
                                                 )
    self.calc = calc
    return calc

  def get_lc_a(self, calc,
               name='W',):
    """加入if 语句, 避免重复计算
    """
    if 'lc_a' in self.data:
      lc_a = self.data['lc_a']
      return lc_a

    atoms = ase.build.bulk(name=name,)
    atoms = self.AseLearn.calc_lattice_constant(
        atoms=atoms,
        calc=calc,
        filter_mask=[True]*6,
        is_save_traj=False,
        is_save_log=False,
    )
    lc_a = self.Model.get_lc_a_from_atoms(atoms_relaxed=atoms,)
    self.data['lc_a'] = lc_a

    return lc_a

  def get_E_patom(self,
                  name='W',
                  a=3.14,
                  opt_name='lbfgs',
                  is_save_traj=False,
                  is_save_log=False,
                  is_recalc=False,):
    if 'E_patom' in self.data:
      E_patom = self.data['E_patom']
    else:
      lc_a = self.get_lc_a(name=name,
                           a=a,
                           opt_name=opt_name,
                           is_save_traj=is_save_traj,
                           is_save_log=is_save_log,
                           is_recalc=is_recalc,)
      atoms: ase.Atoms = ase.build.bulk(name=name, a=lc_a,)
      atoms = self.AseLearn.calc_single_point(
          atoms=atoms,
          calc=self.calc,
      )
      E_patom = atoms.get_potential_energy()/atoms.get_global_number_of_atoms()
      self.data['E_patom'] = E_patom

    return E_patom

  def get_data_moduli(self,
                      name='W',
                      a=3.14,
                      is_save_traj=False,
                      is_save_log=False,
                      is_recalc=False,):
    lc_a = self.get_lc_a(
        name=name, a=a,
        is_save_traj=is_save_traj,
        is_save_log=is_save_log,
        is_recalc=is_recalc,)
    atoms = ase.build.bulk(name=name, a=lc_a)
    data_dict = self.Moduli.calc_moduli_wrapper(
        calc=self.calc,
        atoms=atoms,
        h=0.001,
    )
    self.data.update(data_dict)
    return data_dict

  def get_E_atom_in_vacuum(self,
                           name='W',):
    if 'E_atom_in_vacuum' in self.data:
      E_atom_in_vacuum = self.data['E_atom_in_vacuum']
    else:
      atoms = self.AseLearn.calc_single_atoms(
          calc=self.calc,
          symbols=name,
      )
      E_atom_in_vacuum = atoms.get_potential_energy()
      self.data['E_atom_in_vacuum'] = E_atom_in_vacuum
    return E_atom_in_vacuum

  def get_E_cohensive(self,
                      name='W',
                      a=3.14,
                      is_save_traj=False,
                      is_save_log=False,
                      is_recalc=False,):
    """cohensive energy = (E_bulk - natoms*Eatom_in_vacuum) / natoms
    聚合能: 如果把各组成部分分开到“无穷远”处，当然需要一定的能量来提供克服有关吸引力，即需做功。所需做的功的大小，说明各组成部分结合的紧密程度，称为该物体的结合能。
    """

    if 'E_cohensive' in self.data:
      E_cohensive = self.data['E_cohensive']
    else:
      # 真空中原子能
      E_atom_in_vacuum = self.get_E_atom_in_vacuum(name=name,)
      # 体块中的原子能
      E_patom = self.get_E_patom(name=name, a=a,
                                 is_save_traj=is_save_traj,
                                 is_save_log=is_save_log,
                                 is_recalc=is_recalc,)
      # 聚合能
      E_cohensive = E_atom_in_vacuum - E_patom
      self.data['E_cohensive'] = E_cohensive
    return E_cohensive

  def get_E_f_vacancy(self,
                      name='W',
                      a=3.14,
                      box_size=[5, 5, 5],
                      opt_name='lbfgs',
                      is_save_traj=False,
                      is_save_log=False,
                      is_recalc=False,
                      ):
    if 'E_f_vacancy' in self.data:
      E_f_vacancy = self.data['E_f_vacancy']
    else:
      lc_a = self.get_lc_a(name=name, a=a,
                           is_save_traj=is_save_traj,
                           is_save_log=is_save_log,
                           is_recalc=is_recalc,)
      E_patom = self.get_E_patom(name=name,
                                 a=lc_a,
                                 is_save_traj=is_save_traj,
                                 is_save_log=is_save_log,
                                 is_recalc=is_recalc,
                                 )
      atoms = ase.build.bulk(name=name, a=lc_a).repeat(box_size)
      atoms = self.Model.delete_atom(atoms=atoms,
                                     index_list=[0])
      atoms: ase.Atoms = self.AseLearn.calc_relaxation_general(
          calc=self.calc,
          atoms=atoms,
          opt_name=opt_name,
          is_save_traj=is_save_traj,
          is_save_log=is_save_log,
          is_recalc=is_recalc)
      E_f_vacancy = atoms.get_potential_energy() - E_patom * \
          atoms.get_global_number_of_atoms()
      self.data['E_f_vacancy'] = E_f_vacancy
    return E_f_vacancy

  def get_E_f_SIA_for_bcc(self,
                          name='W',
                          a=3.14,
                          direction='100',
                          box_size=[8, 8, 8],
                          opt_name='fire2',
                          is_save_log=False,
                          is_save_traj=False,
                          is_recalc=False,):
    if f'E_f_SIA_{direction}' in self.data:
      E_f_SIA = self.data[f'E_f_SIA_{direction}']
    else:
      lc_a = self.get_lc_a(name=name, a=a,
                           is_save_traj=is_save_traj,
                           is_save_log=is_save_log,
                           is_recalc=is_recalc,)
      E_patom = self.get_E_patom(name=name, a=lc_a,
                                 is_save_traj=is_save_traj,
                                 is_save_log=is_save_log,
                                 is_recalc=is_recalc,)
      atoms: ase.Atoms = ase.build.bulk(
          name=name, cubic=True, a=lc_a,).repeat(box_size)
      position_shift = np.where([int(i) for i in direction], 0.7, 0)
      atom = ase.Atom(symbol=name,
                      position=np.array(box_size)*lc_a/2 + position_shift,
                      # position=position_shift,
                      )
      atoms.append(atom)
      atoms = self.AseLearn.calc_relaxation_general(
          calc=self.calc,
          atoms=atoms,
          opt_name=opt_name,
          is_save_log=is_save_log,
          is_save_traj=is_save_traj,
          is_recalc=is_recalc,
      )
      E_f_SIA = atoms.get_potential_energy() - E_patom * \
          atoms.get_global_number_of_atoms()
      self.data[f'E_f_SIA_{direction}'] = E_f_SIA
    return E_f_SIA

  def get_E_b_vacancy_migration(self,
                                name='W',
                                a=3.14,
                                box_size=[4]*3,
                                nimages=3,
                                opt_name='lbfgs',
                                is_save_log=False,
                                is_save_traj=False,
                                is_plot_fig=False,
                                is_recalc_neb=True,):
    if 'E_b_vacancy_migration' in self.data:
      E_b_vacancy_migration = self.data['E_b_vacancy_migration']
    else:
      lc_a = self.get_lc_a(name=name, a=a,
                           is_save_traj=False,
                           is_save_log=False,
                           )
      atoms = ase.build.bulk(name=name, cubic=True, a=lc_a,)
      atoms = atoms.repeat(box_size)
      data_atoms = self.NEB.get_neb_IF_example(
          calc_func=self.get_calc,
          name=name,
          lc_a=lc_a,
          box_size=box_size,
      )
      for k, v in data_atoms.items():  # 迟豫始末态
        data_atoms[k] = self.AseLearn.calc_relaxation_general(
            calc=self.get_calc(),
            atoms=v,
            opt_name='lbfgs',
            is_save_log=False,
            is_save_traj=False,
        )
      # neb 计算
      neb_tools = self.NEB.run_neb_wrapper(
          initial=data_atoms['initial'],
          final=data_atoms['final'],
          calc_func=self.get_calc,
          directory=self.calc.directory,
          nimages=nimages,
          opt_name=opt_name,
          is_plot_fig=is_plot_fig,
          is_save_log=is_save_log,
          is_save_traj=is_save_traj,
          is_recalc=is_recalc_neb,
      )
      E_b_vacancy_migration, dE = neb_tools.get_barrier()
      self.data['E_b_vacancy_migration'] = E_b_vacancy_migration
    return E_b_vacancy_migration

  def get_E_surface_for_bcc(self, name='W',
                            a=3.14,
                            size=(3, 3, 9),
                            vacuum=5,
                            surface_indices='100',
                            opt_name='lbfgs',
                            is_save_traj=False,
                            is_save_log=False,
                            is_recalc=False,):
    if f'E_surface_energy_{surface_indices}' in self.data:
      E_surface_energy = self.data[f'E_surface_energy_{surface_indices}']
    else:
      lc_a = self.get_lc_a(name=name, a=a,
                           is_save_traj=False,
                           is_save_log=False,)
      atoms = self.Model.get_atoms_surface_for_bcc(
          symbol=name,
          a=lc_a,
          size=size,
          vacuum=vacuum,
          surface_indices=surface_indices,
      )
      atoms = self.AseLearn.calc_relaxation_general(
          calc=self.calc,
          atoms=atoms,
          opt_name=opt_name,
          is_save_traj=is_save_traj,
          is_save_log=is_save_log,
          is_recalc=is_recalc,
      )
      E_patom = self.get_E_patom(name=name, a=lc_a,
                                 is_save_traj=False,
                                 is_save_log=False,
                                 )
      surface_area = self.Model.get_surface_area(atoms=atoms)
      E_surface_energy = (atoms.get_potential_energy(
      ) - atoms.get_global_number_of_atoms()*E_patom)/2/surface_area  # eV/A^2
      E_surface_energy = E_surface_energy * 16.0218  # J/m^2
      self.data[f'E_surface_energy_{surface_indices}'] = E_surface_energy

    return E_surface_energy

  def get_data_dimmer(self,
                      name='W',
                      opt_name='mdmin',
                      is_save_traj=False,
                      is_save_log=False,
                      is_recalc=False,):
    if 'E_b_dimmer' in self.data:
      E_b_dimmer = self.data['E_b_dimmer']
      distance = self.data['distance_dimmer']
      data = {'E_b_dimmer': E_b_dimmer,
              'distance': distance}
    else:
      E_atom_in_vacuum = self.get_E_atom_in_vacuum(name=name,)
      atoms = self.Model.get_atoms_in_vaccum(symbols=[name, name],
                                             positions=[(0, 0, 0), (0, 0, 2.02)],)
      atoms = self.AseLearn.calc_relaxation_general(atoms=atoms,
                                                    calc=self.calc,
                                                    opt_name=opt_name,
                                                    is_save_traj=is_save_traj,
                                                    is_save_log=is_save_log,
                                                    is_recalc=is_recalc,
                                                    )
      E_dimer = atoms.get_potential_energy()
      E_b_dimmer = E_atom_in_vacuum*atoms.get_global_number_of_atoms() - E_dimer
      distance = atoms.get_distance(a0=0, a1=1)
      data = {'E_b_dimmer': E_b_dimmer,
              'distance_dimmer': distance}
      self.data.update(data)
    return data

  def view(self, atoms):
    from ase.visualize import view
    return view(atoms=atoms)


class AseLearn():
  def __init__(self):
    """定义一些基本的功能
    --- cite---

    @article{ase-paper,
      author = {Ask Hjorth Larsen and Jens Jørgen Mortensen and Jakob Blomqvist and Ivano E Castelli and Rune Christensen and Marcin
    Dułak and Jesper Friis and Michael N Groves and Bjørk Hammer and Cory Hargus and Eric D Hermes and Paul C Jennings and Peter
    Bjerre Jensen and James Kermode and John R Kitchin and Esben Leonhard Kolsbjerg and Joseph Kubal and Kristen
    Kaasbjerg and Steen Lysgaard and Jón Bergmann Maronsson and Tristan Maxson and Thomas Olsen and Lars Pastewka and Andrew
    Peterson and Carsten Rostgaard and Jakob Schiøtz and Ole Schütt and Mikkel Strange and Kristian S Thygesen and Tejs
    Vegge and Lasse Vilhelmsen and Michael Walter and Zhenhua Zeng and Karsten W Jacobsen},
      title = {The atomic simulation environment—a Python library for working with atoms},
      journal = {Journal of Physics: Condensed Matter},
      volume = {29},
      number = {27},
      pages = {273002},
      url = {http: // stacks.iop.org/0953-8984/29/i = 27/a = 273002},
      year = {2017},
      abstract = {The atomic simulation environment(ASE) is a software package written in the Python programming language with the aim of setting up, steering, and analyzing atomistic simulations. In ASE, tasks are fully scripted in Python. The powerful syntax of Python combined with the NumPy array library make it possible to perform very complex simulation tasks. For example, a sequence of calculations may be performed with the use of a simple ‘for -loop’ construction. Calculations of energy, forces, stresses and other quantities are performed through interfaces to many external electronic structure codes or force fields using a uniform interface. On top of this calculator interface, ASE provides modules for performing many standard simulation tasks such as structure optimization, molecular dynamics, handling of constraints and performing nudged elastic band calculations.}
    }
    """

    self.Model = Model()
    self.CalcModule = CalcModule()
    self.NEB = NEB()
    self.Moduli = Moduli()
    from . import aseMDLearn
    self.aseMDLearn = aseMDLearn
    # --
    from . import aseTutorial
    self.Tutorial = aseTutorial
    self.Examples = Examples()
    # 存储数据
    self.data = {}

    pass

  def get_opt(self,
              atoms: ase.Atoms,
              opt_name='lbfgs',
              is_save_log=True,
              logfile='ase.log',
              is_save_traj=True,
              trajectory='ase.traj',
              **kwargs,
              ):
    """opt_name_list = ['lbfgs', 'lbfgslinesearch', 'scipyfmincg',
                'fire2', 'fire',
                'bfgs', 'gpmin',  'mdmin', 'goodoldquasinewton',
                'bfgslinesearch', 'scipyfminbfgs',  'scipyfmin',]
    'quasinewton' = 'bfgslinesearch'
    """
    logfile = logfile if is_save_log else None  # 可以为 '-'
    trajectory = trajectory if is_save_traj else None

    import ase.optimize.sciopt
    if opt_name.lower() == 'lbfgs':
      opt = ase.optimize.LBFGS(atoms=atoms,
                               logfile=logfile,
                               trajectory=trajectory,
                               **kwargs)
    elif opt_name.lower() == 'gpmin':
      '''
        # 适用于黑箱优化问题：如果你的优化问题是“黑箱”的，意味着你只能通过计算获得能量或力，而无法直接从函数式表达式中获取信息，那么 GPMin 是一个非常合适的选择。它能够在这种情况下进行优化。
        # 全局优化能力：与传统的基于梯度的优化器相比，GPMin 可以更好地在复杂的多峰势能面中进行全局优化，避免局部最小值。
        # 适合不容易获取梯度的问题：在某些问题中，计算梯度非常困难，或者梯度计算成本太高，GPMin 作为无梯度的优化方法，可以提供一个解决方案。
        # 缺点：
        # 计算开销较大：由于每一步都需要对目标函数进行回归建模，这会带来较大的计算开销。尤其在系统较大或者优化步骤较多时，计算资源消耗可能会很大。
        # 优化速度较慢：相比传统的梯度优化方法，GPMin 的收敛速度通常较慢，尤其是对于较简单的优化问题，使用 GPMin 的开销可能没有必要。
        # 适用场景有限：对于需要快速优化的系统，或者优化过程中已经能够计算梯度的系统，GPMin 可能不是最佳选择。它更适合那些复杂、非平稳或者梯度计算困难的问题。
        # 使用场景：
        # 复杂的多峰势能面：如果你的系统存在多个局部最小值，或者势能面非常复杂，GPMin 可以帮助你找到全局最小值。
        # 黑箱优化：在那些无法直接获取梯度，或者梯度计算非常昂贵的系统中，GPMin 提供了一个有效的优化手段。
        '''
      opt = ase.optimize.GPMin(atoms=atoms,
                               logfile=logfile,
                               trajectory=trajectory,
                               **kwargs)
    elif opt_name.lower() == 'bfgs':
      opt = ase.optimize.BFGS(atoms=atoms,
                              logfile=logfile,
                              trajectory=trajectory,
                              **kwargs)
    elif opt_name.lower() in ['bfgslinesearch', 'quasinewton']:
      opt = ase.optimize.BFGSLineSearch(atoms=atoms,
                                        logfile=logfile,
                                        trajectory=trajectory,
                                        **kwargs)
    elif opt_name.lower() == 'fire':
      opt = ase.optimize.FIRE(atoms=atoms,
                              logfile=logfile,
                              trajectory=trajectory,
                              **kwargs)
    elif opt_name.lower() == 'fire2':
      opt = ase.optimize.FIRE2(atoms=atoms,
                               logfile=logfile,
                               trajectory=trajectory,
                               **kwargs)
    elif opt_name.lower() in ['mdmin', 'quickmin']:
      opt = ase.optimize.MDMin(atoms=atoms,
                               logfile=logfile,
                               trajectory=trajectory,
                               **kwargs)
    elif opt_name.lower() == 'goodoldquasinewton':
      opt = ase.optimize.GoodOldQuasiNewton(atoms=atoms,
                                            logfile=logfile,
                                            trajectory=trajectory,
                                            **kwargs)
    elif opt_name.casefold() == 'lbfgslinesearch':
      opt = ase.optimize.LBFGSLineSearch(atoms=atoms,
                                         logfile=logfile,
                                         trajectory=trajectory,
                                         **kwargs)
    elif opt_name.lower() in ['scipyfmin', 'sd']:
      opt = ase.optimize.sciopt.SciPyFmin(atoms=atoms,
                                          logfile=logfile,
                                          trajectory=trajectory,
                                          **kwargs)
    elif opt_name.lower() == 'scipyfminbfgs':
      opt = ase.optimize.sciopt.SciPyFminBFGS(atoms=atoms,
                                              logfile=logfile,
                                              trajectory=trajectory,
                                              **kwargs)
    elif opt_name.lower() in ['scipyfmincg', 'cg']:
      opt = ase.optimize.sciopt.SciPyFminCG(atoms=atoms,
                                            logfile=logfile,
                                            trajectory=trajectory,
                                            **kwargs)
    else:
      print('请提供正确的 opt_name')
      pass
    return opt

  def get_traj(self, atoms: ase.Atoms,
               fname_traj='ase.traj',
               mode='w',):
    """用于迟豫等的 opt.attach()
    """
    traj = ase.io.Trajectory(filename=fname_traj,
                             mode=mode,
                             atoms=atoms)
    return traj

  def calc_relaxation_general(self,
                              atoms: ase.Atoms,
                              calc: ase.calculators.calculator.Calculator,
                              opt_name='lbfgs',
                              opt_pars_dict={'loginterval': 1},
                              fmax=0.05,
                              is_save_log=False,
                              is_save_traj=False,
                              is_recalc=False,
                              ):
    """calc 应该设置 directory 属性
    """
    # 如果存在 fname_traj 直接读取并返回
    logfile = os.path.join(calc.directory, 'relaxation.log')
    trajectory = os.path.join(calc.directory, 'relaxation.traj')
    if os.path.exists(trajectory) and (not is_recalc):
      ase.parallel.parprint(f'{trajectory} -> 存在, 读取的是其中的atoms!')
      atoms: ase.Atoms = ase.io.read(filename=trajectory, index='-1')
      pass
    else:  # 否则执行计算
      atoms.calc = calc
      opt = self.get_opt(atoms=atoms,
                         opt_name=opt_name,
                         is_save_log=is_save_log,
                         logfile=logfile,
                         is_save_traj=is_save_traj,
                         trajectory=trajectory,
                         **opt_pars_dict,
                         )
      opt.run(fmax=fmax)

    return atoms

  def calc_single_point(self,
                        atoms: ase.Atoms,
                        calc,):
    atoms.calc = calc
    atoms.get_potential_energy()
    # ase.parallel.parprint(f'能量为: {energy}')
    return atoms

  def calc_lattice_constant(self, atoms: ase.Atoms,
                            calc,
                            filter_name='sf',
                            filter_mask=[True]*6,
                            fmax=0.005,
                            opt_name='lbfgs',
                            opt_pars_dict={'loginterval': 1},
                            is_save_traj=True,
                            is_save_log=True,
                            is_recalc=False,
                            ):
    r"""filter_name = 'sf|uf'
    使用张量的方法而不是 eos, 这种方法最方便 可以优化fcc, hcp
    atoms = ase.build.bulk('Ni', 'hcp', a=2.46, c=4.02)
    ---
    * 直接使用 UnitCellFilter 可能会出错, 最好是sf
    * filter_mask = [True]*6 用于控制是否迟豫应力的六个独立分量 x, y, z, xz, yz, xy
    ---
    calc 应该是已经设定了 directory
    ---
    参考 self.aseTutorial.Tutorial_Basic_property_calculations().finding_lattice_constants()
    """
    trajectory = os.path.join(
        calc.directory, 'optimization.traj') if is_save_traj else None
    logfile = os.path.join(calc.directory,
                           'optimization.log') if is_save_log else None  # 或者 '-'
    if (trajectory is not None) and os.path.exists(trajectory) and (not is_recalc):
      atoms = ase.io.read(filename=trajectory, index='-1')
    else:
      atoms.calc = calc
      # filter_dict = {'sf': ase.filters.StrainFilter,
      #                'uf': ase.filters.UnitCellFilter}
      # filter = filter_dict[filter_name]
      # relax_filter = filter(atoms, mask=filter_mask)
      if filter_name == 'sf':
        relax_filter = ase.filters.StrainFilter(atoms, mask=filter_mask)
      elif filter_name == 'uf':
        relax_filter = ase.filters.UnitCellFilter(atoms, mask=filter_mask)
      else:
        print('请提供真确的 filter_name')
        pass

      opt = self.get_opt(atoms=relax_filter,
                         opt_name=opt_name,
                         is_save_log=is_save_log,
                         logfile=logfile,
                         is_save_traj=is_save_traj,
                         trajectory=trajectory,
                         **opt_pars_dict,
                         )
      opt.run(fmax=fmax,)

    return atoms

  def calc_frequency_and_get_vib_data(self, atoms: ase.Atoms, calc,
                                      directory='vibration',
                                      # [0, 1], 计算索引原子的振动频率, None 表示所有
                                      indices=None,
                                      recalc=False,):
    """能直接显示零点能, 还能画声子态密度

    Args:
        atoms(_type_): _description_
        calc(_type_): _description_
        pardir(str, optional): _description_. Defaults to 'vibration'.
        indices(_type_, optional): _description_. Defaults to None.

    Returns: vib_data
        _type_: _description_
    """
    subdir = os.path.join(directory, 'vib_data')

    # 例如使用如下计算器
    # calc = ase.calculators.vasp.Vasp(directory=pardir)
    atoms.calc = calc
    vib = ase.vibrations.Vibrations(atoms,
                                    indices=indices,
                                    name=subdir,
                                    )

    if not os.path.exists(subdir):
      if recalc:
        vib.clean()  # 不知道为什么无法清理并重新计算 以后再说
      vib.run()
    vib.summary()  # 能直接显示零点能
    # 获得零点能
    # zpe = vib.get_zero_point_energy()
    # 写入振动模式结构
    vib.write_mode()  # -1: write last mode to trajectory file
    vib_data = vib.get_vibrations()  # 获得vibdata 对象后 有更多的方法可以使用
    # vib_data.get_pdos().plot()  # 等等
    # vib_data.get_zero_point_energy()
    # print(vib.get_energies())  print(vib_data.get_energies()) # 结果是一样的
    return vib_data

  def calc_thermochemistry(self, atoms, potentialenergy,
                           vib_data: ase.vibrations.VibrationsData, system='gas|adsorbate_on_slab',
                           temperature=300, pressure=101325, verbose=True,
                           ignore_imag_modes=True):
    """ 获得体系的 gibbs 自由能for gas  或者 helmholtz_energy 自由能 for adsorbates on slab
    AseThermochemistry()  # 参考这个

    Args:
        atoms(_type_): _description_
        potentialenergy(_type_): _description_
        vib_data(ase.vibrations.VibrationsData): _description_
        system(str, optional): 'gas' or 'adsorbates'. Defaults to 'gas'.
        temperature(int, optional): _description_. Defaults to 300.
        pressure(int, optional): _description_. Defaults to 101325.

    Returns: data
        _type_: _description_
    """
    # self.aseTutorial.AseThermochemistry()  # 参考这个
    if system == 'gas':
      # 计算热学量
      thermo = ase.thermochemistry.IdealGasThermo(vib_energies=vib_data.get_energies(),
                                                  potentialenergy=potentialenergy,
                                                  atoms=atoms,
                                                  geometry='linear',
                                                  symmetrynumber=2, spin=0,
                                                  ignore_imag_modes=ignore_imag_modes,
                                                  )
      zpe = vib_data.get_zero_point_energy()
      # 获得 gibs 自由能
      gibbs_energy = thermo.get_gibbs_energy(
          temperature=temperature, pressure=pressure, verbose=verbose)
      # 获得熵
      entropy = thermo.get_entropy(
          temperature=temperature, pressure=pressure, verbose=verbose)
      # zpe = thermo.get_ZPE_correction()
      data = {'atoms': atoms,
              'zpe': zpe,
              'temperature': temperature,
              'pressure': pressure,
              'entropy': entropy,
              'gibbs_energy': gibbs_energy,
              'vib_data': vib_data,
              'thermo': thermo}
    elif system == 'adsorbate_on_slab':
      thermo = ase.thermochemistry.HarmonicThermo(vib_energies=vib_data.get_energies(),
                                                  potentialenergy=potentialenergy,
                                                  ignore_imag_modes=ignore_imag_modes)
      entropy = thermo.get_entropy(temperature=temperature, verbose=verbose)
      helmholtz_energy = thermo.get_helmholtz_energy(
          temperature=temperature, verbose=verbose)
      zpe = vib_data.get_zero_point_energy()
      # zpe = thermo.get_ZPE_correction()
      data = {'atoms': atoms,
              'zpe': zpe,
              'temperature': temperature,
              'entropy': entropy,
              'helmholtz_energy': helmholtz_energy,
              'vib_data': vib_data,
              'thermo': thermo}
    else:
      print('system = gas or adsorbates, 请重新设置system 参数')
    return data

  def global_optimization(self,
                          slab: ase.Atoms,
                          adsorbate,
                          constraints,
                          calc=ase.calculators.emt.EMT()):
    """
    # Make the Pt 110 slab.
    atoms: ase.Atoms = ase.build.fcc100('Pt', (2, 2, 2), vacuum=7.)
    atoms.pbc = True

    # adsorbate.
    adsorbate = ase.build.molecule('CO')
    adsorbate.rotate(a=180, v='x')

    # Constrain the surface to be fixed and a Hookean constraint between the adsorbate atoms.
    constraints = [ase.constraints.FixAtoms(indices=[atom.index for atom in atoms if atom.symbol == 'Pt'],),
                  ase.constraints.Hookean(8, 9, k=10, rt=1.15)]
    """
    # Add adsorbate.
    ase.build.add_adsorbate(
        slab=slab, adsorbate=adsorbate, height=2, position='ontop')

    # 束缚
    slab.set_constraint(constraints)

    # Set the calculator.
    slab.calc = calc

    # Instantiate and run the minima hopping algorithm.
    bh = ase.optimize.basin.BasinHopping(
        atoms=slab,         # the system to optimize
        temperature=300 * ase.units.kB,  # 'temperature' to overcome barriers
        dr=0.5,               # maximal stepwidth
        optimizer=ase.optimize.LBFGS,      # optimizer to find local minima
        fmax=0.1,             # maximal force for the optimizer
    )
    import time
    t1 = time.perf_counter()
    bh.run(steps=6)
    t2 = time.perf_counter()
    print(t2-t1)
    return None

  def write_py_from_code(self, func,
                         directory='xx',
                         fname_py='run.py',
                         string_import_list=[''],):
    r""" * 注意需要在 func 中 导入相应的包
    - 直接在run.py 目录中运行 mpirun - np 4 gpaw python run.py
    - fname_py 所在的目录即为计算目录
    """
    directory = os.path.abspath(directory)
    fname_py = os.path.join(directory, fname_py)
    if not os.path.exists(directory):
      os.makedirs(name=directory, exist_ok=True)
    # ---
    from soft_learn_project import inspectLearn
    code = inspectLearn.InspectLearn().getsource(func=func,)
    import re
    code = re.sub(pattern=r"directory='.*?'",
                  repl=fr"directory='{directory}'",
                  string=code,
                  count=1,  # 只替换一次
                  )
    with open(fname_py, mode='w', encoding='utf-8') as file:
      for string in string_import_list:
        file.write(string+'\n')
      if code.splitlines()[0].startswith(r' '):
        line0 = code.splitlines()[0]
        line0 = line0.replace('self,', '').strip()
        line0 = line0.replace('self', '').strip()
        lines = code.splitlines()[1:]
        lines.insert(0, line0)
        code = '\n'.join(lines)
      file.write(code + '\n'*3)
      # file.write(f"{func.__name__}(directory='{directory}')")
      file.write(f"{func.__name__}()")

    ase.parallel.parprint(f'写入文件-> {fname_py}')
    ase.parallel.parprint('直接在run.py 目录中运行 mpirun -np 4 gpaw python run.py')
    return None

  def view_and_save(self, atoms,
                    fname='atoms.png',
                    rotation='-90x,0y,0z',):
    r"""可以保存特定角度的图片
    """
    ase.io.write(filename=fname,
                 images=atoms,
                 rotation=rotation)

  def get_light_calc_emt(self, directory='xxx'):
    import ase.calculators.emt
    calc = ase.calculators.emt.EMT(directory=directory)
    return calc

  def get_light_calc_lj(self,
                        directory='xxx',
                        sigma=1,
                        epsilon=1):
    """默认的参数不行, 结构迟豫的不合理, 需要给定
    """
    import ase.calculators.lj
    calc = ase.calculators.lj.LennardJones(directory=directory,
                                           sigma=sigma,
                                           epsilon=epsilon)
    return calc

  def get_light_calc_morse(self,
                           directory='xxx',
                           epsilon=1,
                           r0=1):
    """默认的参数不行, 结构迟豫的不合理, 需要给定
    """
    import ase.calculators.morse
    calc = ase.calculators.morse.MorsePotential(directory=directory,
                                                epsilon=epsilon,
                                                r0=r0)
    return calc

  def get_db_data_example(self):
    # AseDB() # 参考这个
    db = ase.db.connect('database.json')
    db.get_atoms('calculator=vasp,S>2')
    for row in db.select(selection='S,natoms>30'):
      print(row, row.name)
    db.get('natoms>10,S>2').energy
    # Base().db_all.get('calculator=vasp,S>2').toatoms()
    ase.io.read('database.json@S>3', index=':')
    db.get(name='Al_bulk').toatoms()
    db.get('name=Al_bulk').toatoms()
    pass

  def get_bandpath(self, atoms: ase.Atoms):
    bandpath = atoms.cell.bandpath()
    return bandpath

  def example_ase(self):
    from soft_learn_project.ase_learn import aseLearn
    al = aseLearn.AseLearn()
    calc = al.CalcModule.get_calc_vasp(
        directory='/Users/wangjinlong/job/tmp/t1',
        kpts=[3]*3,
        ispin=1,
    )
    atoms = al.Model.get_atoms_normal_crsytal(name='W', cubic=True)
    atoms = al.calc_lattice_constant(atoms=atoms,
                                     calc=calc,
                                     fmax=0.05,
                                     is_recalc=True,
                                     )
    return atoms

  def example_janus_core(self):
    from soft_learn_project.ase_learn import aseLearn
    from soft_learn_project.janus_core_learn import janus_coreLearn
    al = aseLearn.AseLearn()
    calc = al.CalcModule.get_calc_MLIP(
        directory='/Users/wangjinlong/job/tmp/t1',
        # kpts=[3]*3,
        # ispin=1,
    )
    atoms = al.Model.get_atoms_normal_crsytal(name='W', cubic=True)

    jl = janus_coreLearn.JanuscoreLearn()
    atoms.calc = calc
    atoms = jl.geom_opt_universal(atoms=atoms,
                                  #   file_prefix='/Users/wangjinlong/job/tmp/t2',
                                  file_prefix=None,
                                  )
    return atoms
