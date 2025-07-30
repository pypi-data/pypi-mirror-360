
import re
import numpy as np
import os
import ase
import pandas as pd


class RunlammpsFromPython():
  def __init__(self):
    """https://docs.lammps.org/Python_run.html
    Example Python scripts
    The python/examples directory has Python scripts which show how Python can run LAMMPS, grab data, change it, and put it back into LAMMPS.
    """
    pass

  def system_roperties(self):
    """Methods:
    get_thermo(): return current value of a thermo keyword
    last_thermo(): return a dictionary of the last thermodynamic output
    get_natoms(): total # of atoms as int
    reset_box(): reset the simulation box size
    extract_setting(): return a global setting
    extract_global(): extract a global quantity
    extract_box(): extract box info
    create_atoms(): create N atoms with IDs, types, x, v, and image flags
    Properties:
    last_thermo_step: the last timestep thermodynamic output was computed
    """

    from lammps import lammps
    lmp = lammps()
    lmp.file("in.sysinit")

    natoms = lmp.get_natoms()
    print(f"running simulation with {natoms} atoms")

    lmp.command("run 1000 post no")

    for i in range(10):
      lmp.command("run 100 pre no post no")
      pe = lmp.get_thermo("pe")
      ke = lmp.get_thermo("ke")
      print(f"PE = {pe}\nKE = {ke}")

    lmp.close()
    pass

  def per_atom_properties(self):
    """ https://docs.lammps.org/Python_atoms.html
    Methods:

    extract_atom(): extract a per-atom quantity

    Numpy Methods:

    numpy.extract_atom(): extract a per-atom quantity as numpy array
    """
    import lammps
    lmp = lammps.lammps()
    lmp.file("in.sysinit")

    # Read/Write access via ctypes
    nlocal = lmp.extract_global("nlocal")
    x = lmp.extract_atom("x")

    for i in range(nlocal):
      print("(x,y,z) = (", x[i][0], x[i][1], x[i][2], ")")

    # Read/Write access via NumPy arrays
    atom_id = lmp.numpy.extract_atom("id")
    atom_type = lmp.numpy.extract_atom("type")
    x = lmp.numpy.extract_atom("x")
    v = lmp.numpy.extract_atom("v")
    f = lmp.numpy.extract_atom("f")

    # set position in 2D simulation
    x[0] = (1.0, 0.0)

    # set position in 3D simulation
    x[0] = (1.0, 0.0, 1.)

    lmp.close()

    pass

  def compute_fixes_variables(self):
    """ https://docs.lammps.org/Python_objects.html
    Methods:
    lammps.extract_compute(): extract value(s) from a compute

    lammps.extract_fix(): extract value(s) from a fix

    lammps.extract_variable(): extract value(s) from a variable

    lammps.set_variable(): set existing named string-style variable to value

    NumPy Methods:

    lammps.numpy.extract_compute(): extract value(s) from a compute, return arrays as numpy arrays

    lammps.numpy.extract_fix(): extract value(s) from a fix, return arrays as numpy arrays

    lammps.numpy.extract_variable(): extract value(s) from a variable, return arrays as numpy arrays
    """

    pass

  def scatter_gather_operations(self):
    """https://docs.lammps.org/Python_scatter.html

    # return per-atom property of all atoms gathered into data, ordered by atom ID
    data = lmp.gather_atoms(name,type,count)
                                          # name = "x", "charge", "type", etc
    # ditto, but concatenated atom values from each proc (unordered)
    data = lmp.gather_atoms_concat(name,type,count)
    # ditto, but for subset of Ndata atoms with IDs
    data = lmp.gather_atoms_subset(name,type,count,ndata,ids)

    # scatter per-atom property to all atoms from data, ordered by atom ID
    lmp.scatter_atoms(name,type,count,data)
                                              # name = "x", "charge", "type", etc
                                              # count = # of per-atom values, 1 or 3, etc

    # ditto, but for subset of Ndata atoms with IDs
    lmp.scatter_atoms_subset(name,type,count,ndata,ids,data)
    """
    pass

  def neighbor_list_access(self):
    """https://docs.lammps.org/Python_neighbor.html
    Methods:

    lammps.get_neighlist(): Get neighbor list for given index

    lammps.get_neighlist_size(): Get number of elements in neighbor list

    lammps.get_neighlist_element_neighbors(): Get element in neighbor list and its neighbors

    lammps.find_pair_neighlist(): Find neighbor list of pair style

    lammps.find_fix_neighlist(): Find neighbor list of fix style

    lammps.find_compute_neighlist(): Find neighbor list of compute style

    NumPy Methods:

    lammps.numpy.get_neighlist(): Get neighbor list for given index, which uses NumPy arrays for its element neighbor arrays

    lammps.numpy.get_neighlist_element_neighbors(): Get element in neighbor list and its neighbors (as a numpy array)


    """
    from lammps import lammps
    import numpy as np

    lmp = lammps()
    lmp.commands_string("""
    region box block -2 2 -2 2 -2 2
    lattice fcc 1.0
    create_box 1 box
    create_atoms 1 box
    mass 1 1.0
    pair_style lj/cut 2.5
    pair_coeff 1 1 1.0 1.0
    run 0 post no""")

    # look up the neighbor list
    nlidx = lmp.find_pair_neighlist('lj/cut')
    nl = lmp.numpy.get_neighlist(nlidx)
    tags = lmp.extract_atom('id')
    print("half neighbor list with {} entries".format(nl.size))
    # print neighbor list contents
    for i in range(0, nl.size):
      idx, nlist = nl.get(i)
      print("\natom {} with ID {} has {} neighbors:".format(
          idx, tags[idx], nlist.size))
      if nlist.size > 0:
        for n in np.nditer(nlist):
          print("  atom {} with ID {}".format(n, tags[n]))
    pass

  def configuration_information(sef):
    """https://docs.lammps.org/Python_config.html

    Methods:

    lammps.has_mpi_support

    lammps.has_exceptions

    lammps.has_gzip_support

    lammps.has_png_support

    lammps.has_jpeg_support

    lammps.has_ffmpeg_support

    lammps.installed_packages

    lammps.get_accelerator_config

    lammps.has_style()

    lammps.available_styles()
    """
    from lammps import lammps
    lmp = lammps()

    try:
      lmp.file("in.missing")
    except Exception as e:
      print("LAMMPS failed with error:", e)

    # write compressed dump file depending on available of options

    if lmp.has_style("dump", "atom/zstd"):
      lmp.command("dump d1 all atom/zstd 100 dump.zst")
    elif lmp.has_style("dump", "atom/gz"):
      lmp.command("dump d1 all atom/gz 100 dump.gz")
    elif lmp.has_gzip_support():
      lmp.command("dump d1 all atom 100 dump.gz")
    else:
      lmp.command("dump d1 all atom 100 dump")
    pass


class GetData():
  """注意并行会出问题, 以后再想办法解决这个问题, 应该是需要学习mpi4py, 从多个处理器中搜集数据gather?, 从 rstart 文件中获取原子坐标信息和系统信息
  """

  def __init__(self,) -> None:
    pass

  def get_info_dict(self, filename_restart='xx/restart'):
    """从 restart 文件获取 info_dict

    Returns: atom_info_dict
        _type_: _description_
    """
    from lammps import PyLammps
    L = PyLammps(cmdargs=['-log', 'none'])
    L.command(f'read_restart {filename_restart}')
    # 原子类型
    atom_type = L.lmp.gather_atoms_concat('type', 0, 1)
    # 原子坐标
    atom_coord = L.lmp.gather_atoms_concat('x', 1, 3)
    # 系统信息
    # system = L.system
    L.close()

    atom_type_array = np.array(atom_type[:]).reshape(-1, 1)
    atom_x_coord = np.array(atom_coord[0::3]).reshape(-1, 1)
    atom_y_coord = np.array(atom_coord[1::3]).reshape(-1, 1)
    atom_z_coord = np.array(atom_coord[2::3]).reshape(-1, 1)
    atom_coord_array = np.concatenate(
        [atom_x_coord, atom_y_coord, atom_z_coord], axis=1)

    atom_info = {'atom_type_array': atom_type_array,
                 'atom_coord_array': atom_coord_array,
                 #  'system': system
                 }
    return atom_info

  def get_atomTypeN_coords(self, atomType=3):
    info = self.get_info_dict()
    coords_array = info.atom_coord_array[info.atom_type_array.flatten(
    ) == atomType]
    return coords_array

  def get_atomTypeN_Zcoord(self,
                           atom_type=1,
                           xyzCoord='z'):
    """_summary_

    Args:
        atom_type (int, optional): _description_. Defaults to 1.
        xyzCoord (str, optional): _description_. Defaults to 'z'.

    Returns: atomTypeN_Zcoord
        _type_: _description_
    """
    if xyzCoord == 'x':
      coord_index = 0
    elif xyzCoord == 'y':
      coord_index = 1
    elif xyzCoord == 'z':
      coord_index = 2
    info_dict = self.get_info_dict()
    atom_type_array = info_dict['atom_type_array']
    atom_coord_array = info_dict['atom_coord_array']

    atomTypeN_Zcoord = np.extract(
        atom_type_array == atom_type, atom_coord_array[:, coord_index])
    return atomTypeN_Zcoord


class GetDataFromDump():
  """这样才能并行
  """

  def __init__(self, filename_dump):
    """
    用于从dump文件获取dump_list, ith_dump_array, atom_type_array
    """
    self.filename_dump = filename_dump
    dump_data_dealed_list = self.get_dump_data_list()
    self.numer_of_dump = dump_data_dealed_list.__len__()  # 获取dump_data_list的长度

    with open(filename_dump, mode='r') as f:
      lines_list = f.readlines()
    simulation_cell_array = np.array(
        [line.strip().split() for line in lines_list[5:8]], float)
    self.xlo, self.xhi, self.ylo, self.yhi, self.zlo, self.zhi = simulation_cell_array.flatten()
    pass

  def get_dump_data_list(self):
    """
    用于从dump文件获取dump_list
    @return dump_data_dealed_list
    """
    with open(self.filename_dump, "r") as f:
      content = f.read()

    pattern = re.compile("ITEM: TIMESTEP.*?ITEM: ATOMS.*?\n", flags=re.S)
    dump_data_list = pattern.split(content)[1:]

    dump_data_dealed_list = []
    for dump_data in dump_data_list:
      item_dealed = []
      for item in [item.split() for item in dump_data.split("\n")]:
        if item:
          item_dealed.append(item)
      dump_data_dealed_list.append(item_dealed)
    # print(f"总共为{len(dump_data_dealed_list)}个dump结构")
    return dump_data_dealed_list

  def get_ith_dump_array(self, index, dump_data_dealed_list):
    """
    获取第index个dump_array
    @return: 单个dump的数组 single_dump_array
    """
    dump_array = np.array(dump_data_dealed_list[index], dtype=float)
    return dump_array

  def atom_type_array(self, dump_array, atom_type=1):
    """
    获取元素类型为atom_type
    @dump_array: 单个dump的数组
    @atom_type: 元素类型
    @return: atom_type?_array
    """
    return dump_array[dump_array[:, 1] == atom_type]


class Deal_Dump():
  def __init__(self, ) -> None:
    """ 以后看看有啥用
    """

  def dump2neb_final(self, filename='final.dump', file_out='final'):
    """_summary_

    Args:
        filename (str, optional): _description_. Defaults to 'final.dump'.
        file_out (str, optional): _description_. Defaults to 'final'.
    """
    with open(file=filename, mode='r') as f:
      content = f.readlines()

    natom = int(content[3].strip())
    data_array = np.array([line.split()
                           for line in content[9:9+natom]], dtype=float)
    # 删掉一列
    data_array = np.delete(data_array, obj=[1], axis=1)
    # 写入文件
    with open(file=file_out, mode='w') as f:
      f.write(f'{natom}\n')
      for line in data_array:
        f.write('{:.0f} {:f} {:f} {:f}\n'.format(
            *[num for num in line]))


class Basic():
  def __init__(self):
    """lammps 内部命令"""
    pass

  def df_command_usage(self, search_str='create'):
    """用于lammps命令的参考说明
    """

    command_usage_data = {
        'change_box': 'all z delta -3.0 0 # 用于改变盒子的大小',
        'compute_displaceAtom': 'compute ID group-ID displace/atom',
        'compute_reduce':
            r'C_reduce {group_ID_He} reduce max c_{compute_ID_clusterAtom}',
        'create_atoms_description':
            'atomtype single 0 0 0 units lattice, atomtype single 6.8 5.5 7.7 units box, atomtype random N seed region-ID, 1 region R_enlarged',
        'delete_atoms': 'region region1_delete compress yes, group group_delete compress yes',
        'dump': '1 all custom 100 1.dump id type x y z, prd_events all custom 1 prd_events.dump id type x y z',
        'dump_modify': 'dump_id append yes thresh x>0',
        'fix_setforce': 'Fsetforce Group_bottom_layer setforce 0 0 0',
        'gather_concat': "ex = lmp.L.lmp.gather_concat('c_C_cluster', 1, 1), ex_array = np.array(ex[:], dtype=int)ex_array'",
        'group': 'group ID style args, style = delete or clear or empty or region or type or id or molecule or variable or include or subtract or union or intersect or dynamic or static, group_ID region region_id, He type 3, mobile union mobile He, group_Id variable variable-name # 这个慎用, 很奇怪, 会出现Compute used in variable between runs is not current, G_He_delete dynamic G_He every 1 var zHe # 用了之后还要run 0/1 一下, 才会更新 He_delete, G_del id == 1, group_delete id 91 93, group_delete id 1:18:3 # 不给出3 默认为1, group_delete id <> 91 93, group_delete id <= 91, group_ID delete',
        'lattice': 'bcc 3.165 {lattice_args_dict[surface]["110"]}',
        'read_dump': 'initial.dump 0 x y z replace no purge yes add yes',
        'region': 'region1_delete sphere 0 0 0 0.1, region_ID block xlo xhi ylo yhi zlo zhi units box',
        'reset_timestep': 'reset_timestep 0',
        'run': r'{number_of_run} every 2000 "delete_atoms group G_He_delete compress yes"',
        'thermo_style': 'custom step pe c_C_reduce, custom step elapsed elaplong dt time  cpu tpcpu spcpu cpuremain part timeremain  atoms temp press pe ke etotal  evdwl ecoul epair ebond eangle edihed eimp  emol elong etail  enthalpy ecouple econserve  vol density lx ly lz xlo xhi ylo yhi zlo zhi  xy xz yz xlat ylat zlat  bonds angles dihedrals impropers  pxx pyy pzz pxy pxz pyz  fmax fnorm nbuild ndanger  cella cellb cellc cellalpha cellbeta cellgamma  c_ID c_ID[I] c_ID[I][J]  f_ID f_ID[I] f_ID[I][J]  v_name v_name[I]',
        'variable': """V_type atom type, V_z_coord atom z, zHe atom "(z > c_z_max) && (vz > 0)", zHe atom "z > c_zmax_W || z < {-self.lower_limit -5 }""",
        'write_restart_description': 'restart',
        'write_dump': 'all custom 1.dump id type x y z, all custom 1.dump id type x y z modify append yes sort id, write_dump group-ID style file dump-args modify dump_modify-args',
    }
    import pandas as pd
    df = pd.DataFrame(data=command_usage_data.values(),
                      index=command_usage_data.keys(),
                      columns=['usage'])
    bl = df.index.str.contains(pat=search_str,
                               case=False,
                               na=False)
    df_result = df[bl]
    # df[bl]['usage'].values
    return df_result

  def get_info(self, lmp,
               info_str='all|fix|compute|group|system|variable'):
    """不能使用 -screen none 否则什么都看不到 可以是 fix compute
    """
    lmp.command(f"info {info_str}")
    return None

  def extract_info(self,
                   lmp,):
    result = lmp.extract_compute('thermo_pe', 0, 0,)
    return result

  def read_restart(self,
                   lmp,
                   fname_restart='write_restart'):
    """从保存的restart 中 读取
    """

    lmp.command(f'read_restart {fname_restart}')
    return lmp

  def write_restart(self, lmp,
                    fname_restart='xxx/write_restart'):
    lmp.command(f'write_restart {fname_restart}')
    return lmp

  def read_dump(self, lmp,
                fname='xx/dump.dump',
                Nstep=1):
    """盒子和原子都被重新替换"""
    lmp.command(
        f'read_dump {fname} {Nstep} x y z box yes purge yes replace no add yes')
    return lmp

  def write_dump(self, lmp,
                 element_list=['W', 'H', 'He'],
                 dump_append='no',
                 fname='xxx/x.dump', ):
    lmp.command(
        f'write_dump all custom {fname} id type element x y z modify element {" ".join(element_list)} append {dump_append}')
    return lmp

  def write_data(self, lmp,
                 labelmap_dict={'1': 'W', '2': 'H', '3': 'He'},
                 fname_data='xxx/lmp.data'):
    labelmap_str = ' '.join(f"{k} {v}" for k, v in labelmap_dict.items())
    lmp.command(f'labelmap atom {labelmap_str}')
    lmp.command(f'write_data {fname_data}')
    return lmp

  def create_atoms(self, lmp,
                   string='3 single 0.1 0.1 0.1'):
    lmp.command(f'create_atoms {string}')
    return lmp

  def delete_atoms_with_no_group(self,
                                 lmp,
                                 build_group_id=None,
                                 build_group_type=None,
                                 ):
    """* 删除的逻辑为: 定义组, 删除组, 还可以根据 region 删除 原子
    现有的根据 id 和 type 建立组并删除组, build_group_id| build_group_type 二者给其一 
    ---
    lmp.command('group G_delatom id 1')
    lmp.command('delete_atoms group G_delatom')
    ---
    lmp.eval('count(G_delatom)')
    """
    group_name = 'G_delatom'
    if build_group_id:
      lmp.command(f'group {group_name} id {build_group_id}')
    elif build_group_type:
      lmp.command(f'group {group_name} type {build_group_type}')
    lmp.command(f'delete_atoms group {group_name} compress yes')  # 默认压缩

    return lmp

  def delete_atoms_with_group(self, lmp,
                              group_name='all'):
    lmp.command(f'delete_atoms group {group_name} compress yes')  # 默认压缩
    return lmp

  def reset_timestep(self, lmp,
                     Nstep=0):
    lmp.command(f'reset_timestep {Nstep}')
    return lmp

  def initialize(self, lmp,
                 boundary='p p p',
                 thermo=100):
    """初始化设置
    --- 有以下两种方式
    # pass command parameters as one string
    L.cmd.region("box block 0 10 0 5 -0.5 0.5")

    # OR pass them individually
    L.cmd.region("box block", 0, 10, 0, 5, -0.5, 0.5)
    """
    lmp.command('units metal')
    lmp.command('dimension 3')
    lmp.command(f'boundary {boundary}')
    lmp.command("atom_style atomic")  # molecular  #atomic
    lmp.command("atom_modify map array sort 0 0")  # prd neb 需要sort 0 0确定原子编号不变
    lmp.command(f'timestep 0.001')
    lmp.command(f'thermo {thermo}')
    return lmp

  def region(self, lmp,
             region_str='prism 0 2 0 3 0 4 0 0 0|block -5 5 -5 5 -5 5'):
    # 正交盒子
    lmp.command(f"region box {region_str}")
    # 平行六面体
    lmp.command(f'region box {region_str}')
    return lmp

  def build_model_universal(self,
                            lmp,
                            lattice_type='bcc',
                            lc=3.165,
                            region_str='prism 0 2 0 3 0 4 0 0 0|block -5 5 -5 5 -5 5',
                            create_atoms_type=1,
                            N_ele=3,
                            ):

    if lattice_type == 'bcc':
      #  "lattice bcc 3.165 orient x 1 0 0 orient y 0 1 0 orient z 0 0 1")
      lmp.command(f'lattice {lattice_type} {lc}')
    elif lattice_type == 'hcp':
      # hcp 结构,
      # self.L.variable("a1 equal", 2.76176)
      # self.L.variable("a3 equal", 1.6097)  # L.eval('lz')/L.eval('lx')=1.6097
      # self.L.lattice(
      #     "custom ${a1} a1 1.0 0.0 0.0 a2 0.0 1.732 0.0 a3 0.0 0.0 ${a3} basis 0.0 0.0 0.0 basis 0.5 0.5 0.0 basis 0.5 0.83333 0.5 basis 0.0 0.33333 0.5")
      # 上面几行直接以下面一行代替
      lmp.command(f'lattice {lattice_type} {lc}')
    else:
      lmp.command(f'lattice {lattice_type} {lc}')

    lmp.command(f'region box {region_str}')
    lmp.command(f'create_box {N_ele} box')
    lmp.command(f'create_atoms {create_atoms_type} box')
    return lmp

  def define_interatomic_potential(
      self,
      lmp,
      pair_style_str='eam/alloy',
      pair_coeff_str='* * /Users/wangjinlong/job/soft_learn/lammps_learn/potential/WHHe.eam_bonny/potential-WHHe-EAM2.eam.alloy W H He',
      extra_cmd_list=[],
  ):
    """
    pair_style_str = 'eam/fs|eam/alloy'
    ---
    table
    - self.L.mass("1 183.84000")
    - 使用table的形式，注意这是两体势
    - L.pair_style("table linear 1000")
    - L.pair_coeff("* * pot_W_W W_W 5")
    ---
    eam/alloy
    - 这是eam/alloy 的形式
    - L.pair_style("eam/alloy")
    - L.pair_coeff(f"* * {pot_path}/W.eam.alloy W")
    """

    lmp.command(f'pair_style {pair_style_str}')
    lmp.command(f'pair_coeff {pair_coeff_str}')

    lmp.command('neighbor 2.0 bin')
    lmp.command('neigh_modify delay 0 every 1 check yes')
    # 其他的命令
    for extra_cmd in extra_cmd_list:
      lmp.command(extra_cmd)
    return lmp

  def construct_bulk(self,
                     lmp,
                     lattice_type='bcc',
                     lc=3.165,
                     create_atoms_type=1,
                     N_ele=3,
                     block_size=[-5, 5, -5, 5, -5, 5],
                     ):
    """ 构建体块 
    """

    if lattice_type == 'bcc':
      # , "orient x 1 0 0 orient y 0 1 0 orient z 0 0 1")
      lmp.command(f'lattice {lattice_type} {lc}')
    elif lattice_type == 'hcp':
      # hcp 结构,
      # self.L.variable("a1 equal", 2.76176)
      # self.L.variable("a3 equal", 1.6097)  # L.eval('lz')/L.eval('lx')=1.6097
      # self.L.lattice(
      #     "custom ${a1} a1 1.0 0.0 0.0 a2 0.0 1.732 0.0 a3 0.0 0.0 ${a3} basis 0.0 0.0 0.0 basis 0.5 0.5 0.0 basis 0.5 0.83333 0.5 basis 0.0 0.33333 0.5")
      # 上面几行直接以下面一行代替
      lmp.command(f'lattice {lattice_type} {lc}')
    else:
      lmp.command(f'lattice {lattice_type} {lc}')

    lmp.command(f"region box block {' '.join([str(i) for i in block_size])}")
    lmp.command(f'create_box {N_ele} box')
    lmp.command(f'create_atoms {create_atoms_type} box')
    return lmp

  def construct_bulk_specify_direction(self,
                                       lmp,
                                       surface_index='110',
                                       block_size=[0, 3, 0, 3, 0, 5],
                                       lc=3.165,
                                       N_ele=3,
                                       create_atoms_type=1,
                                       ):
    """ ## 注意 初始化时 boundary 可能需要 'p p f'
    内部定义了运动组和固定组

    * 较小的表面模型, 可以用于DFT模型
    block_size_dict = {'111': (0, 2, 0, 2, -0.01, 4.1),
        '100': (0, 3, 0, 3, -0.01, 4.9),
        '110': (0, 3, 0, 2, -0.01, 4.9),}
    """

    lattice_args_dict = {
        '111': 'orient x 1 -1 0 orient y 1 1 -2 orient z 1 1 1',
        '100': 'orient x 1 0 0 orient y 0 1 0 orient z 0 0 1',
        '110': 'orient x 0 0 1 orient y 1 -1 0 orient z 1 1 0', }

    # create_aotms
    lmp.command(f'lattice bcc {lc} {lattice_args_dict[surface_index]}')
    lmp.command(f"region box block {' '.join([str(i) for i in block_size])}")
    lmp.command(f'create_box {N_ele} box')
    lmp.command(f'create_atoms {create_atoms_type} box')
    return lmp

  def construct_surface(self,
                        lmp,
                        surface_index='110',
                        block_size=[0, 3, 0, 3, -0.01, 4.9],
                        lc=3.165,
                        N_ele=3,
                        create_atoms_type=1,
                        vacuum_size=10,
                        bottom_layer_hight=1.02,
                        group_ID_mobile='G_mobile',
                        group_ID_fixed='G_fixed',
                        ):
    """ ## 注意 初始化时 boundary 可能需要 'p p f'
    内部定义了运动组和固定组

    * 较小的表面模型, 可以用于DFT模型
    block_size_dict = {'111': (0, 2, 0, 2, -0.01, 4.1),
        '100': (0, 3, 0, 3, -0.01, 4.9),
        '110': (0, 3, 0, 2, -0.01, 4.9),}
    """
    self.construct_bulk_specify_direction(lmp=lmp,
                                          surface_index=surface_index,
                                          block_size=block_size,
                                          lc=lc,
                                          N_ele=N_ele,
                                          create_atoms_type=create_atoms_type,
                                          )
    lmp.command(
        f"change_box all z final {lmp.get_thermo('zlo')} {lmp.get_thermo('zhi') + vacuum_size} units box")
    lmp.command(
        f'region Region_bottom_layer block INF INF INF INF INF {block_size[4] + bottom_layer_hight}')
    lmp.command(f'group {group_ID_fixed} region Region_bottom_layer')
    lmp.command(f'group {group_ID_mobile} subtract all {group_ID_fixed}')
    return lmp

  def dump(self, lmp,
           group_id='all',
           fname_dump='run.dump',
           num_run=2000,
           num_dump=10,
           dump_element_list=['W', 'H', 'He'],
           dump_append='no',):
    lmp.command(f'compute patom all pe/atom')
    # https://docs.lammps.org/compute_cna_atom.html
    cutoff = 1.207 * 3.165  # 1.207 * lc for bcc
    lmp.command(f'compute cna all cna/atom {cutoff}')
    lmp.command(f'group G_type1 type 1')
    # https://docs.lammps.org/compute_coord_atom.html
    lmp.command(
        f'compute coord G_type1 coord/atom cutoff 3.0 group G_type1')  # 1
    lmp.command(f'compute pke all ke/atom')
    dumpN = max(1, num_run // num_dump)
    lmp.command(
        f'dump 1 {group_id} custom {dumpN} {fname_dump} id type element mass x y z vx vy vz c_patom c_pke c_cna c_coord')
    lmp.command(
        f"dump_modify 1 element {' '.join(dump_element_list)} append {dump_append}")
    return lmp

  def minimize(
          self,
          lmp,
          is_box_relax=False,
          etol=0,  # 0
          ftol=1e-3,  # 0.001
          maxiter=2000,  # 2000
          maxeval=10000,
          min_style_str='cg',
          min_modify_str='dmax 0.1',):
    """ 
    min_style_str = ['cg', 'hftn', 'sd','quickmin', 'fire', 'spin', 'spin/cg', 'spin/lbfgs']
    ---
    minimize_relax 'hftn'
    min_style: {'usually_can_relax_box': [
        'cg', 'sd'], 'can_neb_cannot_relax_box': ['quickmin', 'fire']}

    * 注意事项:
    1. 当有 固定组 和 运动组 的体系时, 能量最小化时为了防止原子移动可以 fix_freeze
    `fix freeze base setforce 0.0 0.0 0.0`
    """
    if is_box_relax:
      lmp.command("fix relax all box/relax iso 0.0")
    lmp.command(f'min_style {min_style_str}')
    lmp.command(f'min_modify {min_modify_str}')
    lmp.command("thermo_style custom step pe lx press")
    lmp.command(f'minimize {etol} {ftol} {maxiter} {maxeval}')

    return lmp

  def equilibrium_NPT(self,
                      lmp,
                      Tstart,
                      Tstop=None,
                      group_id="all",
                      thermo_style_custom="pe ke press lx vol density",
                      ):
    """ # 对于热平衡, 有以下注意事项
        1. 当有 运动组 合固定组 的时候, 对于体系的温度需要 `compute` 和 `thomo_modify` 的设置, 才能得出正确的温度
            ```
            compute         tmobile mobile temp
            thermo		100
            thermo_modify   temp tmobile
            ```
        2. 保持温度时, 可以用以下设置
            ```
            fix		1 mobile nve
            fix		2 mobile langevin ${Tequil} ${Tequil} 1.0 ${seed} zero yes
            ```
    """

    Tstop = Tstart if Tstop is None else Tstop
    random_seed = np.random.randint(1, 1e+5)
    lmp.command(f"variable T equal {Tstart}")
    lmp.command(
        f'velocity {group_id} create {Tstart} {random_seed} mom yes rot yes dist gaussian')
    lmp.command(
        f'fix Fnpt {group_id} npt temp {Tstart} {Tstop} $(100*dt) iso 0 0 $(1000*dt)')
    lmp.command(f'fix Fdt {group_id} dt/reset 1 NULL NULL 0.1 units box')
    lmp.command(
        f'fix Fmomentum {group_id} momentum 1 linear 1 1 1 angular rescale')
    lmp.command(f'thermo_style custom step time temp {thermo_style_custom}')

    return lmp

  def equilibrium_nve_langevin(self,
                               lmp,
                               Tstart=1300,
                               Tstop=1300,
                               group_ID_mobile='all|G_mobile',
                               group_ID_fixed='None|G_fixed',
                               compute_ID_temp='temp_mobile',
                               thermo_style_custom="pe ke etotal press dt",
                               ):
    """固定运动组, 温度平衡运动组
    """

    if group_ID_fixed is None:
      pass
    else:
      lmp.command(f'fix Fsetforce {group_ID_fixed} setforce 0 0 0')
    random_seed = np.random.randint(1, 1e+5)
    lmp.command(f'fix Fnve {group_ID_mobile} nve')
    lmp.command(
        f'fix Flangevin {group_ID_mobile} langevin {Tstart} {Tstop} 0.1 {random_seed} zero yes')
    lmp.command(f'fix Fdt all dt/reset 1 NULL NULL 0.1 units box')
    lmp.command(f'thermo 100')
    lmp.command(f'compute {compute_ID_temp} {group_ID_mobile} temp')
    lmp.command(f'thermo_style custom step time temp {thermo_style_custom}')
    # 注意 thermo_modify 放在下面, 上面的 temp 才是修正后的温度 也就等于 c_{compute_ID_temp} 的温度, 此时temp为运动组的温度
    lmp.command(f'thermo_modify temp {compute_ID_temp} lost ignore')

    return lmp

  def run(self, lmp,
          num_run=2000,
          ):
    """一般平衡只需要2000步, 但融化的平衡也就是达到融化状态需要至少10000步.
    """

    lmp.command(f'run {num_run}')
    return lmp

  def run_old(self, lmp,
              num_run=2000,
              is_dump=False,
              group_id='all',
              num_dump=10,
              dump_append='no',
              fname_dump='run.dump',
              is_write_restart=False,
              fname_restart='xxx/equil.restart',
              ):
    """以后考虑删掉
    """

    if is_dump:
      lmp = self.dump(lmp=lmp,
                      fname_dump=fname_dump,
                      group_id=group_id,
                      num_run=num_run,
                      num_dump=num_dump,
                      dump_element_list=self.dump_element_list,
                      dump_append=dump_append,
                      )

    lmp.command(f'run {num_run}')
    if is_write_restart:
      lmp = self.write_restart(lmp=lmp, fname_restart=fname_restart)
    return lmp

  def prd(self,
          lmp,
          temperature=1300,
          group_ID_mobile='G_mobile',
          group_ID_fixed='None|G_fixed',
          compute_event_str='event all event/displace 1.5',
          num_of_prd=2000,
          t_event=100,
          n_dephase=10,
          t_dephase=10,
          t_correlate=100,
          is_dump=True,
          dump_element_list=['W', 'H', 'He'],
          filename_dump='prd_events.dump',
          random_number_seed=np.random.randint(1000, 100000),
          ):
    """ 产生 in.prd 文件
    * prd 需要 /opt/homebrew/bin/mpirun -np 4 lmp_mac_mpi -p 4x1 -in in.prd
    * 参考例子 /Users/wangjinlong/job/soft_learn/lammps_learn/package/mylammps/examples/prd

    lmp: lammps.PyLammps 需要这个实例, 这个可以
    l = lammps.PyLammps()
    l.enable_cmd_history = True
    l.command('units metal')
    ...
    l.write_script('in.prd')
    ---
    prd 的计算逻辑
    1. 给定初始速度, 运行 t_dephase 步， 去相(dephase).
        * dephase 的目的是消除副本之间的关联, 具体做法是: 选择随机数和一套随机速度, 然后运行 t_dephase 时间步. 重复 n_dephase 次。
        * dephase 的总步数为 t_dephase * n_dephase, 如果在 t_dephase 期间发生了时间, 则重复这个阶段直到没有事件发生.

    2. 所有副本运行 t_event 时间步后, 淬火, 比较MD运行前后结构是否改变(比较的是MD前的淬火态和MD后的淬火态), 也就是说是否发生了 转变事件
    3. 发生事件的副本继续运行 MD 搜索关联事件, 运行的时间步为 t_correlate, 然后每 t_event 次淬火, 检查是否发生了另一事件。
    4. 第一个没有发生关联事件的副本会共享给所有副本, 淬火态得到更新, 所有的副本继续进行相同的流程。淬火态总是会被发生事件的副本覆盖(更新)

    * 外部循环是总共运行 N 次 MD 时间步, N 只包括阶段 2 和 3 的时间步, 不包括 去相 和 淬火 的时间步。
    * num_of_prd 和 t_correlate 必须是 t_event 的整数倍

    ---
    ### prd 的输出
    1. Event 事件数是一个计数器，随着每个事件的增加而增加，无论它是不相关的还是相关的。
    2. Correlated 如果发生的是不相关事件, 标记为0, 也就是所有的副本都独立运行, 如果再第三个阶段发生相关联事件标记为1, 根据现在的理解这个出现1也没有关系
    3. Coincident 这一列 表示共同发生同一事件的副本的数目, 正常情况下，这个值应该是1。如果它经常大于1，那么要么是副本数量太大，要么是t_event太大。
    4. Replica 这一列 表示的是探测到事件发生的副本 从 0 到 M-1
    """

    # 温度 fix
    if group_ID_fixed is None:
      pass
    else:
      lmp.command(f'fix F_setforce {group_ID_fixed} setforce 0 0 0')
    lmp.command(f"fix Fnve {group_ID_mobile} nve")
    lmp.command(
        f"fix Flangevin {group_ID_mobile} langevin {temperature} {temperature} 0.1 {random_number_seed} zero yes")

    # PRD 计算
    lmp.command('reset_timestep 0')
    lmp.command('min_style fire')
    lmp.command('timestep 0.001')
    lmp.command(f'compute {compute_event_str}')
    compute_event_ID = compute_event_str.split()[0]
    lmp.command("thermo_style custom step time temp pe")
    lmp.command("thermo_modify lost ignore")

    # min 默认是 0.1 0.1 40 50  time 的值['steps','clock'] 默认为 'steps'
    if is_dump:
      dump_ID_prd = 'D_prd'
      lmp.command(
          f'dump {dump_ID_prd} all custom 1 {filename_dump} id type element x y z')
      lmp.command(
          f"dump_modify {dump_ID_prd} element {' '.join(dump_element_list)}")

    lmp.append_cmd_history(
        f'prd {num_of_prd} {t_event} {n_dephase} {t_dephase} {t_correlate} {compute_event_ID} {random_number_seed} temp {temperature} min 0.01 0.1 100 200 time steps')

    return lmp

  def neb(self,
          lmp,
          is_dump=True,
          dump_element_list=['W', 'H', 'He'],
          min_style='fire',
          fname_final='xxx/final',):
    """ neb 计算设置 
    """
    lmp.append_cmd_history(f'fix Fneb all neb 1')  # Kspring = force/distanc 1
    if is_dump:
      lmp.append_cmd_history('variable u uloop 64')  # 设置最大的核数目
      lmp.append_cmd_history('compute patom all pe/atom')
      lmp.append_cmd_history(
          'dump events all custom 5000 neb_*_$u.dump id type element x y z c_patom')
      lmp.append_cmd_history(
          f'dump_modify events first yes element {" ".join(dump_element_list)}')
    # NEB will often converge more quickly if you use a timestep about 10x larger  尽管手册上说通常10倍大的时间步通常算的更快，但不知道为什么如果设置为0.01 经常出现问题，算不了
    lmp.append_cmd_history('timestep 0.001')
    lmp.append_cmd_history(f'min_style {min_style}')  # quickmin fire fire 更好
    lmp.append_cmd_history('thermo 100')
    lmp.append_cmd_history('thermo_style custom step pe')
    lmp.append_cmd_history(
        f'neb 0 0.05 1000 1000 1000 final {os.path.abspath(fname_final)}')
    return lmp

  def hyper(self,
            lmp,
            temperature=1300,
            group_ID_fixed='G_fixed',
            group_ID_mobile='G_mobile',
            compute_event_args='event G_W event/displace 1.7',
            is_hyper_LHD=True,
            fix_hyper_local_args_dict={'cutbond': 3.4,
                                       'qfactor': 0.3,
                                       'Vmax': 0.5,
                                       'Tequil': 1300,
                                       'Dcut': 10,
                                       'alpha': 10,  # 200
                                       "Btarget": 50,  # boost 4000
                                       'ghostcut': 15,
                                       },
            hyper_args_N=5000,
            hyper_args_Nevent=100,
            Nrebond=100,
            filename_dump='hyper_cal.dump',
            fix_hyper_global_args_dict={'cutbond': 3.2,
                                        'qfactor': 0.3,
                                        'Vmax': 0.5,
                                        'Tequil': 1300,
                                        'ghostcut': 15,
                                        },
            ):
    """ ### 构造表面必须是周期性的, 否则会计算出错
    温度平衡后才能进行 hyper 计算
    * 使用该命令前, 注意再次确定运动和固定组 或者更新这两个组, 例如:`lmp.L.group('G_He type 3')\n lmp.L.group('G_mobile union G_mobile G_He')`

    hyperdynamics (HD) 的计算逻辑如下:

        ```
        quench
        create initial list of bonds

        while (time remains):
            run dynamics for Nevent steps
            quench
            check for an event
            if event occurred: reset list of bonds
                restore pre-quench state 恢复淬火前的状态继续 MD 模拟
        ```

    * fix hype/global 还是 fix hype/local 决定运行全局还是局部超动力学算法。
    * 指定的总步数N必须是Nevent的倍数
    * 检查事件是否发生, 是通过 compute event/displace 命令实现的 看是否大约指定的位移
    * 从 log.lammps 输出的最后部分可以看到 加速因子 (time boost factor), 发生的事件数 (event timesteps), 最大的移动距离 (max drift distance of any atom )
    * hyper 命令中的 dump 关键词可以在每次事件监测到时触发dump快照输出, 快照是淬火的结构。 dump会输出 时间步为 hyper_args_N 的结构, 要避免的话, dump 的 N 要大于 hyper_args_N
    * hyper 命令中的 rebond 关键词可以在每次 Nrebond 时强制更新 bond list, 即使此时没有事件发生, Nrebond必须是Nevent的倍数.

    ## GHD只能给单原子对添加偏置势, 可以加速一个小的模拟, 最多100个原子。对于较大的系统, LHD需要实现良好的时间加速度。
    ### fix_hyper_global_args_dict 参数解释: 只能给单原子对添加偏置势
        cutbond: 一对原子被认为成键的最大距离(距离单位), 建议设置为 近邻原子之间距离的1.25 倍  在钨中 d_a-a = 2.72  2.72*1.25 = 3.4
        qfactor: 偏置势的最大应变, 通常 0.3 为合理值
        Vmax: 偏置势的高度, 应设置为略小于事件发生的最小能垒, 设置的时候要仔细考虑, 0.3~0.5? 如果设置较小则发生的事件就越少, 可以根据产生的事件数来决定这个参数值
        Tequil: 平衡温度,
    * 一般情况下，Tequil值越低，Vmax值越高，GHD算法获得的时间提升越多。
        cutbond: 同上
        qfactor: 同上
        Vmax:
        Tequil: 同上
        Dcut: minimum distance between boosted bonds (distance units), 建议两倍的原子间相互作用势截断半径, 对于大多数体系可以取10
        alpha: boostostat relaxation time (time units), 设为几个 ps 就够了
        Btarget: desired time boost factor (unitless), 通过以下函数能够计算出大约加速的值, 如果设置的值小于该值能够正确的运行

            ```python
            def get_Btarget():
                import numpy as np
                k_B = 1.380649e-23  # J/K
                q_e = 1.602176634e-19 #  C
                k_B = k_B/q_e  # in eV
                T = 1300
                beta = 1/(k_B/q_e*T)
                V_small = 0.7  # 检测事件的最小能垒
                Btarget = np.exp(beta * V_small)
                return Btarget
            ```

        keyword: bound or reset or check/ghost or check/bias
        ghostcut: 其值至少为 Dcut + cutevent, cutevent 是判断是否发生事件的距离 compute_event/displace 中的距离, comm_modify cutoff 命令默认的 cutoff 距离是不够的, 因此需要被 ghost_cut 覆盖


    ### fix_hyper_local_args_dict 参数解释: 能给多原子对添加偏置势

    Args:
        lmp_instance (_type_): _description_
        temperature (int, optional): _description_. Defaults to 1300.
        group_ID_fixed (str, optional): _description_. Defaults to 'fixed_group'.
        group_ID_mobile (str, optional): _description_. Defaults to 'mobile'.
        compute_event_args (str, optional): _description_. Defaults to 'event all event/displace 1.1'.
        fix_hyper_global_args_dict (dict, optional): _description_. Defaults to {'cutbond': 3.2, 'qfactor': 0.3, 'Vmax': 0.5, 'Tequil': 500, }.
        hyper_args_N (int, optional): # of timesteps to run. Defaults to 5000.
        hyper_args_Nevent (int, optional): 每隔这么多步检查事件. Defaults to 100.
        Nrebond (int, optional): Nrebond必须是Nevent的倍数.
    """

    # 必须要使用 fix langevin 进行NVT
    lmp.command(f'fix F_nve {group_ID_mobile} nve')
    lmp.command(
        f'fix F_langevin {group_ID_mobile} langevin {temperature} {temperature} 1.0 {np.random.randint(1000,100000)} zero yes'
    )
    lmp.command('timestep 0.001')
    lmp.command('neighbor 2.0 bin')
    # delay 0 every 1 check yes once no cluster no include all
    lmp.command(f'neigh_modify delay 0 every 1 check yes')
    if is_hyper_LHD:
      # fix hyper/local
      fix_hyper_ID = 'HL'
      cutbond = fix_hyper_local_args_dict['cutbond']
      qfactor = fix_hyper_local_args_dict['qfactor']
      Vmax = fix_hyper_local_args_dict['Vmax']
      Tequil = fix_hyper_local_args_dict['Tequil']
      Dcut = fix_hyper_local_args_dict['Dcut']
      alpha = fix_hyper_local_args_dict['alpha']
      Btarget = fix_hyper_local_args_dict['Btarget']
      lmp.command(
          f'fix {fix_hyper_ID} {group_ID_mobile} hyper/local {cutbond} {qfactor} {Vmax} {Tequil} {Dcut} {alpha} {Btarget} bound 0.1 reset 0'
      )
      # comm_modify cutoff 命令默认的距离是不够的, 因此需要被 ghost_cut 覆盖
      ghostcut = fix_hyper_local_args_dict['ghostcut']
      lmp.command(f'comm_modify cutoff {ghostcut}')
    else:
      # fix hyper/glocal  # 不常用, 在此仅仅作为参考
      cutbond = fix_hyper_global_args_dict['cutbond']
      qfactor = fix_hyper_global_args_dict['qfactor']
      Vmax = fix_hyper_global_args_dict['Vmax']
      Tequil = fix_hyper_global_args_dict['Tequil']
      fix_hyper_ID = 'HG'
      lmp.command(
          f"fix {fix_hyper_ID} {group_ID_mobile} hyper/global {cutbond} {qfactor} {Vmax} {Tequil}")
      # comm_modify cutoff 命令默认的 cutoff 距离是不够的, 因此需要被 ghost_cut 覆盖
      ghostcut = fix_hyper_global_args_dict['ghostcut']
      lmp.command(f'comm_modify cutoff {ghostcut}')
    # thermo output
    compute_ID_temp = 'Tmobile'  # 准备工作: 要记得 考虑体系的温度时需要注意的要点
    lmp.command(f'compute {compute_ID_temp} {group_ID_mobile} temp')
    lmp.command(
        f'thermo_style custom step temp pe f_{fix_hyper_ID} f_{fix_hyper_ID}[*]')
    lmp.command(f'thermo_modify lost ignore temp {compute_ID_temp}')

    # dump output options
    dump_ID = 'hyper_dump'
    lmp.command(
        f'dump {dump_ID} all custom 1000000 {filename_dump} id type x y z')

    # pin group_ID_fixed so will not move during quenches
    lmp.command(f'fix freeze {group_ID_fixed} setforce 0.0 0.0 0.0')

    # event detection
    lmp.command('group G_W type 1')
    lmp.command(f'compute {compute_event_args}')
    compute_ID_eventDisplace = compute_event_args.split()[0]
    # hyper run
    lmp.command(f'thermo {hyper_args_Nevent}')
    lmp.command(
        # 1e-6 1e-6 100 100
        f' hyper {hyper_args_N} {hyper_args_Nevent} {fix_hyper_ID} {compute_ID_eventDisplace} min 0.1 0.1 40 50 dump {dump_ID} rebond {Nrebond}'
    )
    return lmp

  # old
  def change_box_and_add_atoms(self,
                               lmp,
                               lc=3.165,
                               atom_type_added=1,
                               change_box_str='all z delta -3 0 units box', ):
    """这只是一个特例, 不具有普遍意义, 对于不同的模型, 下面的命令仅供参考
    """

    zlo_old = lmp.get_thermo('zlo')
    # 改变盒子边界
    lmp.command(f'change_box {change_box_str}')  # 下边界和上边界改变的长度
    # 加入原子
    lmp.command(
        f'region R_enlarged block INF INF INF INF INF {zlo_old} units box')
    lmp.command(
        f'lattice bcc {lc} orient x 1 0 0 orient y 0 1 0 orient z 0 0 1')
    lmp.command(f'create_atoms {atom_type_added} region R_enlarged')
    return lmp

  def change_box_example(self,
                         lmp,
                         change_box_str="all z delta -81 0 units box",
                         ):

    # z 的负方向加长多少
    lmp = self.change_box_and_add_atoms(
        atom_type_added=1, change_box_str=change_box_str)

    lmp.command("group G_W type 1")
    lmp.command(
        f"region R_fixed block INF INF INF INF INF {lmp.L.system.zlo + 8} units box"
    )
    # 重新确定固定组
    # 需要删除之前的组,否则是直接在之前的组的基础上添加
    lmp.command(f"group {self.group_ID_fixed} delete")
    lmp.command(f"group {self.group_ID_fixed} region R_fixed")
    # 重新定义运动组
    lmp.command(
        f"group {self.group_ID_mobile} subtract all {self.group_ID_fixed}")
    return lmp


class BasicFeatures(Basic):
  def __init__(self):
    """https://docs.lammps.org/Python_properties.html
    lammps 命令的组合实现特定功能
    """

    self.dump_element_list = ['W', 'H', 'He']
    self.pair_style_str = 'eam/alloy'
    self.pair_coeff_str = f'* * /Users/wangjinlong/job/soft_learn/lammps_learn/potential/WHHe.eam_bonny/potential-WHHe-EAM2.eam.alloy {" ".join(self.dump_element_list)}'
    pass

  def get_atoms_from_dump(self, fname='xxx/1.dump',
                          index=':'):
    """
    读取lammps的dump文件

    Parameters
    ----------
    fname : str
        dump文件的路径
    index : slice
        读取的slice

    Returns
    -------
    atoms : object
        ase的atoms对象
    """
    # import ase.io.lammpsrun
    # atoms = ase.io.lammpsrun.read_lammps_dump(
    #     infileobj=fname,
    #     index=slice(0, None, 1),)
    import ase.io
    atoms = ase.io.read(filename=fname,
                        format='lammps-dump-text',
                        index=index,
                        )
    if isinstance(atoms, ase.Atoms):
      atoms = [atoms]
    elif isinstance(atoms, list):
      pass  # ok
    return atoms

  def get_atoms_from_data(self, fname='xxx/data',
                          Z_of_type={1: 74, 2: 1, 3: 2}):
    # import ase.io.lammpsdata
    # atoms = ase.io.lammpsdata.read_lammps_data(fname,
    #                                            Z_of_type={1: 74, 2: 1, 3: 2})
    import ase.io
    atoms = ase.io.read(filename=fname,
                        format='lammps-data',
                        Z_of_type=Z_of_type)

    return atoms

  def get_lmpData_from_atoms(self, atoms,
                             fname='lammps.data',
                             specorder=['W', 'H', 'He'],
                             ):
    """读取atoms对象, 写入lammps数据文件
    --- 这样也可以
    import ase.io
    ase.io.write(
        filename='t.data',
        format='lammps-data',
        masses=True,
        images=atoms,
        specorder=['W', 'H', 'He'],
        write_image_flags=True,
    )
    """
    import ase.io.lammpsdata
    ase.io.lammpsdata.write_lammps_data(
        file=fname,
        atoms=atoms,
        masses=True,  # 写入质量
        specorder=specorder,  # 指定顺序
        write_image_flags=True,  # 如果为True，则写入图像标志，即原子所在的周期性模拟盒的图像。
    )
    return

  def get_lmp(self, cmdargs=['-log', 'none']):
    """cmdargs_list = [
        '-log', 'none', '-screen', 'none', '-echo', 'none', '-p', '7x1',
        '-in', 'in.lmp', '-plog', 'none', '-pscreen', 'none' ]
    ---
    命令行选项: 目前主要使用以下几种
    * -in in.lmp
    * -log none or log.lammps
    * -screen none or screen.lammps  # 注意 为none 可能会出问题，得不到L.eval('pe')的值
    * -echo none or echo.lammps
    * -p 7x1 用于NEB, PRD, TAD
    * -plog none
    * -pscreen none

    """

    import lammps
    lmp = lammps.lammps(cmdargs=cmdargs,)
    return lmp

  def get_lmp_pylammps(self,
                       cmdargs=[]):
    """用于prd neb 的计算
    cmdargs = ['-log', 'none','-echo','none', 'screen','none']
    """
    import lammps
    lmp = lammps.PyLammps(cmdargs=cmdargs)
    return lmp

  def get_lmp_from_atoms(self,
                         atoms: ase.Atoms,
                         fname_tmp_data='xxx/tmp.data',
                         cmdargs=['-log', 'none'],
                         extra_cmd_list=[],
                         ):
    # 写入 data
    pbc = ' '.join(np.where(atoms.pbc, 'p', 'f'))
    self.get_lmpData_from_atoms(atoms=atoms,
                                fname=fname_tmp_data,
                                specorder=self.dump_element_list,
                                )
    # 读取 data
    lmp = self.get_lmp(cmdargs=cmdargs)
    lmp = self.initialize(lmp=lmp, boundary=pbc)
    lmp.command(f'read_data {fname_tmp_data}')
    lmp = self.define_interatomic_potential(lmp=lmp,
                                            extra_cmd_list=extra_cmd_list,
                                            pair_coeff_str=self.pair_coeff_str,
                                            pair_style_str=self.pair_style_str
                                            )
    return lmp

  def get_lmp_from_dump(self,
                        fname_dump='/Users/wangjinlong/my_server/my/W_Re_potential/test/prd_events_min.dump',
                        Nstep=0,
                        boundary='p p p',
                        cmdargs=['-log', 'none', ],
                        extra_cmd_list=[],):
    """注意读取 dump 时, 可能要根据dump的边界周期性来修改 boundary 参数
    """

    lmp = self.get_lmp(cmdargs=cmdargs)
    lmp = self.initialize(lmp=lmp,
                          boundary=boundary,)
    lmp = self.construct_bulk(lmp=lmp,)
    lmp = self.read_dump(lmp=lmp,
                         fname=fname_dump,
                         Nstep=Nstep)
    lmp = self.define_interatomic_potential(lmp=lmp,
                                            extra_cmd_list=extra_cmd_list,
                                            pair_coeff_str=self.pair_coeff_str,
                                            pair_style_str=self.pair_style_str
                                            )
    return lmp

  def get_lmp_from_restart(self,
                           fname_restart='test/equili.restart',
                           cmdargs=['-log', 'none'],
                           extra_cmd_list=[],
                           ):
    lmp = self.get_lmp(cmdargs=cmdargs)
    lmp = self.read_restart(lmp=lmp,
                            fname_restart=fname_restart)
    lmp = self.define_interatomic_potential(
        lmp=lmp,
        pair_coeff_str=self.pair_coeff_str,
        pair_style_str=self.pair_style_str,
        extra_cmd_list=extra_cmd_list,
    )
    return lmp

  def get_lmp_universal(self,
                        cmdargs=['-log', 'none',
                                 '-screen', 'none',
                                 '-echo', 'none'],
                        boundary='p p p',
                        lattice_type='bcc',
                        lc=3.165,
                        create_atoms_type=1,
                        N_ele=3,
                        block_size=[0, 1, 0, 1, 0, 1],
                        extra_cmd_list=[],
                        ):
    lmp = self.get_lmp(cmdargs=cmdargs)
    lmp = self.initialize(lmp=lmp, boundary=boundary)
    lmp = self.construct_bulk(lmp=lmp,
                              lattice_type=lattice_type,
                              lc=lc,
                              create_atoms_type=create_atoms_type,
                              N_ele=N_ele,
                              block_size=block_size
                              )
    lmp = self.define_interatomic_potential(
        lmp=lmp,
        pair_coeff_str=self.pair_coeff_str,
        pair_style_str=self.pair_style_str,
        extra_cmd_list=extra_cmd_list,
    )
    return lmp

  # prd
  def prd_calc(self,
               fname_restart='xxx/equili.restart',
               directory='xxx/prd',
               temperature=4000,
               num_of_prd=4000,
               is_run=True,
               cmdargs=['-log', 'none', '-screen', 'none']
               ):
    """1. 读取温度平衡后的 write_restart
    2. 写入 prd 文件
    3. 运行prd
    """

    lmp = self.get_lmp_pylammps(cmdargs=cmdargs)
    lmp.enable_cmd_history = True
    lmp = self.read_restart(lmp=lmp,
                            fname_restart=os.path.abspath(fname_restart))
    lmp = self.define_interatomic_potential(lmp=lmp,
                                            pair_coeff_str=self.pair_coeff_str,
                                            pair_style_str=self.pair_style_str)
    lmp = self.prd(lmp=lmp,
                   temperature=temperature,
                   group_ID_fixed=None,
                   group_ID_mobile='all',
                   compute_event_str='event all event/displace 1.5',
                   num_of_prd=num_of_prd,
                   )
    fname_in = os.path.join(directory, 'in.prd')
    lmp.write_script(fname_in)
    print(f'写入文件-> {fname_in}')
    # run prd
    if is_run:
      from soft_learn_project import subprocessLearn
      subprocessLearn.SubprocessLearn().CLI_popen(
          directory=directory,
          args=['/opt/homebrew/bin/mpirun', '-np', '4', 'lmp_mpi', '-p', '4x1', '-in', 'in.prd', '-pscreen', 'none', '-plog', 'none',])
    return None

  def deal_prd_calc(self,
                    directory='.',
                    fname_input='prd_events.dump',
                    fname_output='prd_events_min.dump',
                    cmdargs=['-log', 'none', '-screen', 'none']):
    """把prd 事件原子构型都能量最小化并保存为  fname_output
    """
    fname_input = os.path.join(directory, fname_input)
    fname_output = os.path.join(directory, fname_output)
    fname_tmp_data = os.path.join(directory, 'tmp.data')
    al = self.get_atoms_from_dump(fname=fname_input, index=':')
    if os.path.exists(fname_output):
      os.remove(fname_output)
    for index, atoms in enumerate(al):
      lmp = self.get_lmp_from_atoms(atoms=atoms,
                                    fname_tmp_data=fname_tmp_data,
                                    cmdargs=cmdargs)
      lmp = self.minimize(lmp=lmp,)
      lmp.command(f'reset_timestep {index}')
      lmp = self.write_dump(lmp=lmp,
                            element_list=self.dump_element_list,
                            dump_append='yes',
                            fname=fname_output,)

    return

  def prd_calc_wrapper(self,
                       fname_restart,
                       directory='/Users/wangjinlong/my_server/my/W_Re_potential/test/prd',
                       temperature=100,
                       num_of_prd=2000,
                       is_run=True):
    """ fname_restart: 温度平衡后的 restart """
    if not os.path.exists(directory):
      os.makedirs(name=directory)
    self.prd_calc(fname_restart=fname_restart,
                  directory=directory,
                  temperature=temperature,
                  num_of_prd=num_of_prd,
                  is_run=is_run)
    self.deal_prd_calc(directory=directory)
    return None

  # neb
  def get_neb_final_lmp_method(self,
                               fname_dump='test/prd_events_min.dump',
                               Nstep=0,
                               fname_final='test/neb/final',
                               cmdargs=['-log', 'none', '-screen', 'none']):
    """从dump文件中获取 final"""
    lmp = self.get_lmp_from_dump(fname_dump=fname_dump,
                                 Nstep=Nstep,
                                 cmdargs=cmdargs)
    arr_id = lmp.numpy.extract_atom(name='id',)
    arr_x = lmp.numpy.extract_atom(name='x',)
    # len(arr_id)
    with open(file=fname_final, mode='w') as f:
      print(len(arr_id), file=f)
      for id, x in zip(arr_id, arr_x):
        print(id, *x, file=f)
    print(f'文件final -> {fname_final}')
    return None

  def get_neb_final_ase_method(self,
                               fname_dump='test/prd_events_min.dump',
                               index='1',
                               fname_final='test/neb/final'):
    """从dump文件中获取 final"""
    atoms = self.get_atoms_from_dump(fname=fname_dump,
                                     index=index)[0]
    with open(file=fname_final, mode='w') as f:
      print(len(atoms), file=f)
      for atom in atoms:
        print(atom.index+1, *atom.position, file=f)
    return None

  def neb_calc(self,
               fname_restart_initial='xxx/initial.restart',
               fname_final='xxx/final',
               directory='xxx/neb',
               is_dump=True,
               is_run=True,
               num_cores=4,
               cmdargs=['-log', 'none',
                        '-screen', 'none'],):
    """需要在 neb_prepare 中准备好初态和末态的dump 
    """
    lmp = self.get_lmp_pylammps(cmdargs=cmdargs)
    lmp.enable_cmd_history = True
    lmp = self.read_restart(lmp=lmp, fname_restart=fname_restart_initial)
    lmp = self.define_interatomic_potential(lmp=lmp,
                                            pair_coeff_str=self.pair_coeff_str,
                                            pair_style_str=self.pair_style_str)

    lmp = self.neb(lmp=lmp,
                   is_dump=is_dump,
                   dump_element_list=self.dump_element_list,
                   fname_final=fname_final,)
    fname_in = os.path.join(directory, 'neb.in')
    lmp.write_script(fname_in)

    if is_run:
      from soft_learn_project import subprocessLearn
      subprocessLearn.SubprocessLearn().CLI_popen(
          directory=directory,
          args=['/opt/homebrew/bin/mpirun', '-np', str(num_cores), 'lmp_mpi', '-p', f'{num_cores}x1', '-in', fname_in, '-pscreen', 'none', '-plog', 'none', '-echo', 'none', '-screen', 'none'])

    return None

  def get_df_neb_data_row(self,
                          filename='/Users/wangjinlong/my_server/my/W_Re_potential/test/neb/log.lammps'):

    with open(file=filename, mode='r') as f:
      lines = f.readlines()
    data = lines[-3:]
    # 解析列名
    columns = re.split(r'\s+', data[0].strip())
    # 解析数据行
    rows = [re.split(r'\s+', line.strip()) for line in data[1:]]
    # 转换为 DataFrame
    df = pd.DataFrame(rows, columns=columns).astype(float)
    return df

  def get_df_neb_data_index(self,
                            filename='/Users/wangjinlong/my_server/my/W_Re_potential/test/neb/log.lammps'):
    with open(file=filename, mode='r') as f:
      lines = f.readlines()

    index = re.split(r'\s+', lines[-3].strip())
    values = re.split(r'\s+', lines[-1].strip())
    df = pd.DataFrame(data=values, index=index,
                      columns=['values'])
    return df

  def get_neb_plot_data(self,
                        df_neb_data_index: pd.DataFrame):
    # 获得能量数组
    energy_arr = df_neb_data_index.filter(
        like='PE', axis=0).to_numpy(dtype=float).flatten()
    # energy_arr = df.iloc[df.index.str.startswith('PE')].to_numpy(dtype=float).flatten() # 或者这个
    energy_arr -= energy_arr[0]
    # 获得反应坐标数组
    reaction_coordinate_arr_reduce = df_neb_data_index.filter(like="RD", axis=0).drop(
        index="RDT", errors="ignore").to_numpy(dtype=float).flatten()
    RDT = df_neb_data_index.loc['RDT'].to_numpy(dtype=float)
    reaction_coordinate_arr = reaction_coordinate_arr_reduce * RDT
    data_dict = {'x_arr': reaction_coordinate_arr,
                 'y_arr': energy_arr}
    return data_dict

  def neb_plot(self,
               reaction_coord_arr,
               energy_arr,
               is_savefig=False,
               fname_fig="xxx/mep.pdf",
               interp_kind='quadratic',):
    from soft_learn_project.matplotlib_learn import matplotlibLearn
    import scipy.interpolate
    import matplotlib.pyplot as plt
    x = reaction_coord_arr
    y = energy_arr

    # 能量归一化
    fig = plt.figure()
    ax = fig.add_subplot()
    # 获取插值点
    func = scipy.interpolate.interp1d(x, y, kind=interp_kind)  # quadratic
    x_interp = np.linspace(0, x.max(), 300)
    y_interp = func(x_interp)

    ax.plot(x, y, "or", x_interp, y_interp, "k")
    for i in range(len(x)):
      ax.text(x=x[i], y=y[i], s=str(round(y[i], 2)))
    ax.set_xlabel("Reaction Coordinate ($\AA$)")
    ax.set_ylabel("Relative Energy (eV)")
    if is_savefig:
      # 保存图片
      matplotlibLearn.Features().savefig(fig=fig,
                                         fname=fname_fig,)
    plt.show()
    plt.close()
    return None

  def neb_plot_wrapper(self, directory='xx/neb',
                       is_savefig=False,):
    fname_log = os.path.join(directory, 'log.lammps')
    df_neb_data_index = self.get_df_neb_data_index(filename=fname_log)
    neb_plot_data = self.get_neb_plot_data(
        df_neb_data_index=df_neb_data_index)
    self.neb_plot(reaction_coord_arr=neb_plot_data['x_arr'],
                  energy_arr=neb_plot_data['y_arr'],
                  is_savefig=is_savefig,
                  fname_fig=os.path.join(directory, 'mep.pdf'))
    return None

  def get_neb_images(self,
                     directory='/Users/wangjinlong/my_server/my/W_Re_potential/test/neb',
                     ):
    df = self.get_df_neb_data_index(
        filename=os.path.join(directory, 'log.lammps'))
    step = df.loc['Step'].to_numpy(dtype=int)[0]
    n_images = df.filter(like='PE', axis=0).__len__()

    fname_images_dump = os.path.join(directory, 'neb_images.dump')
    for index in range(n_images):
      fname_dump = os.path.join(directory, f'neb_{step}_{index+1}.dump')
      lmp = self.get_lmp_from_dump(fname_dump=fname_dump,
                                   Nstep=step,
                                   cmdargs=['-log', 'none', '-screen', 'none'])
      lmp = self.write_dump(lmp=lmp,
                            dump_append='yes',
                            fname=fname_images_dump,
                            )
    print(f'neb_imags.dump -> {fname_images_dump}')
    return None

  def neb_calc_prepare(self,
                       directory_neb_prepare='/Users/wangjinlong/my_server/my/W_Re_potential/test/neb/neb_prepare',
                       ):
    """ 在 neb_prepare 目录中准备 initial.restart 和 final, initial.dump 和 final.dump 是用来之后看图的
    """
    if not os.path.exists(directory_neb_prepare):
      os.makedirs(name=directory_neb_prepare)

    fname_dump_initial = os.path.join(directory_neb_prepare, 'initial.dump')
    fname_dump_final = os.path.join(directory_neb_prepare, 'final.dump')
    # 准备 initial
    lmp = self.get_lmp_from_dump(
        fname_dump='/Users/wangjinlong/my_server/my/W_Re_potential/test/prd/prd_events_min.dump',
        Nstep=1,
        cmdargs=['-log', 'none', '-screen', 'none',]
    )
    lmp.command('reset_timestep 0')
    lmp = self.write_dump(lmp=lmp,
                          element_list=self.dump_element_list,
                          dump_append='no',
                          fname=fname_dump_initial
                          )
    lmp = self.write_restart(lmp=lmp,
                             fname_restart=os.path.join(
                                 directory_neb_prepare, 'initial.restart')
                             )
    # final
    lmp = self.get_lmp_from_dump(
        fname_dump='/Users/wangjinlong/my_server/my/W_Re_potential/test/prd/prd_events_min.dump',
        Nstep=2,
        cmdargs=['-log', 'none', '-screen', 'none',]
    )
    lmp.command('reset_timestep 0')
    lmp = self.write_dump(lmp=lmp,
                          element_list=self.dump_element_list,
                          dump_append='no',
                          fname=fname_dump_final,
                          )
    self.get_neb_final_lmp_method(
        fname_dump=fname_dump_final,
        Nstep=0,
        fname_final=os.path.join(directory_neb_prepare,
                                 'final'))
    al = []
    for fname in [fname_dump_initial, fname_dump_final]:
      atoms = self.get_atoms_from_dump(fname=fname,)
      al.extend(atoms)
    return al

  def neb_calc_wrapper(self,
                       directory_prepare='/Users/wangjinlong/my_server/my/W_Re_potential/test/neb/neb_prepare',
                       directory='/Users/wangjinlong/my_server/my/W_Re_potential/test/neb',
                       is_dump=True,
                       is_run=True,
                       num_cores=3,):
    """需要在 neb_prepare 中准备好初态和末态的dump 
    """
    self.neb_calc(
        fname_restart_initial=os.path.join(
            directory_prepare, 'initial.restart'),
        fname_final=os.path.join(directory_prepare, 'final'),
        directory=directory,
        is_dump=is_dump,
        is_run=is_run,
        num_cores=num_cores,)
    # self.neb_plot_wrapper()
    # self.get_neb_images()
    pass

  # old 以后处理
  def cluster_counter(self,
                      lmp,
                      group_ID_He='G_He',
                      element_type=3,
                      criterion_for_cluster=3,
                      ):
    """ 经过修改,该函数可以用于多核计算 根据 restart 文件获得元素类型为 element_type 的团簇数目的数组
    """
    # 1. 获得数据
    lmp.cmd.group(f'{group_ID_He} type {element_type}')
    compute_ID_clusterAtom = 'C_cluster'
    lmp.cmd.compute(
        f'{compute_ID_clusterAtom} {group_ID_He} cluster/atom {criterion_for_cluster}')  # 是否为团簇的距离判据
    compute_ID_reduce = 'C_reduce'
    lmp.cmd.compute(
        f'{compute_ID_reduce} {group_ID_He} reduce max c_{compute_ID_clusterAtom}')
    lmp.cmd.thermo_style(f'custom pe c_{compute_ID_reduce}')  # 更新 compute
    lmp.cmd.run(0)

    atomic_cluster_ID_list = lmp.cmd.lmp.gather_concat('c_C_cluster', 1, 1)[
        :]
    cluster_ID_array = np.array(atomic_cluster_ID_list, dtype=int)
    # 注意这两种方法在并行时都会出现每个处理器有各自不同的结果
    # cluster_ID_array = np.array(
    #     lmp.L.variables['variable_cluser'].value, dtype=int)
    # cluster_ID_array = lmp.L.lmp.numpy.extract_compute(
    #     f'{compute_ID_clusterAtom}', 1, 1)
    lmp.cmd.close()

    # 2. 处理数据
    cluster_ID_array = np.sort(cluster_ID_array[cluster_ID_array != 0])
    cluster_ID_list = list(cluster_ID_array)
    cluster_list = sorted([cluster_ID_list.count(value)
                           for value in set(cluster_ID_list)], reverse=True)
    cluster_array = np.array(cluster_list)
    return cluster_array

  def get_num_of_He_and_num_of_cluster(self,
                                       lmp,
                                       fname_restart):
    """ 以后修改
    """
    # 获得温度平衡前的氦的数目和氦团簇数目
    cluster_array = self.cluster_counter(
        lmp=lmp,
        fname_restart=fname_restart,
        group_ID_He='G_He',
        use_bonnyPot=True,
        element_type=3,
        criterion_for_cluster=3,
    )
    num_of_cluster = cluster_array.__len__()
    num_of_He = cluster_array.sum()

    return num_of_He, num_of_cluster

  def cluster_counter_from_dump(self,
                                lmp,
                                fname_restart='restart',
                                group_ID_He='G_He',
                                element_type=3,
                                fname_dump='cluster.dump',
                                ):
    """用于计算某种元素的团簇数目 例如, He 的团簇数目
    """
    # 获得数据
    lmp = self.read_restart(lmp=lmp,
                            fname_restart=fname_restart)

    lmp.cmd.group(f'{group_ID_He} type {element_type}')
    compute_ID_clusterAtom = 'C_cluster'
    lmp.cmd.compute(f'{compute_ID_clusterAtom} {group_ID_He} cluster/atom 3')
    lmp.cmd.dump('100 all custom 1', fname_dump, 'id type x y z',
                 f'c_{compute_ID_clusterAtom}')  # 用来更新compute

    lmp = self.run(lmp=lmp, num_run=0,
                   is_dump=True)

    # 处理数据
    d = Deal_Dump(filename=fname_dump)
    cluster_list = [
        i for i in d.dump_info_array[:, -1].astype(int) if i != 0
    ]
    cluster_size_list = [
        cluster_list.count(cluster_id) for cluster_id in set(cluster_list)
    ]
    cluster_size_list.sort(reverse=True)
    cluster_size_dict = {
        'cluster_{}'.format(k): v
        for k, v in enumerate(cluster_size_list)
    }

    return cluster_size_dict

  def delete_escaped_He(self,
                        lmp,
                        is_dump=True,
                        filename_dump="1.dump",
                        is_append_dump=True,
                        ):
    """表面模型中去除逃逸出钨和靠近固定层区域的氦原子, 并保存 restart
    """

    lmp.cmd.group("G_He type 3")
    lmp.cmd.group("G_W type 1")
    lmp.cmd.compute("zmax_W G_W reduce max z")
    # 找到逃逸的氦
    zlo = lmp.get_thermo('zlo')
    lmp.cmd.variable(
        f'V_delete_He atom "(z > c_zmax_W) || (z < {zlo + 20})"'
    )
    lmp.cmd.group("G_He_delete dynamic G_He every 1 var V_delete_He")
    lmp.cmd.thermo_style("custom step temp pe c_zmax_W")
    lmp.cmd.run(0)  # 必须要有个 run 否则不会计算compute
    number_of_He_deleted = int(lmp.L.eval("count(G_He_delete)"))
    lmp.command("delete_atoms group G_He_delete compress yes")
    if is_dump:
      write_dump_str = f"all custom {filename_dump} id type x y z modify sort id"
      if is_append_dump:
        write_dump_str += ' append yes'
      lmp.cmd.write_dump(write_dump_str)

    lmp.cmd.group("G_He_delete delete")
    lmp.cmd.close()

    return number_of_He_deleted

  def get_escaped_He_coords(self,
                            fname_restart='restart',
                            criterion_distance=4):

    gd_instance = GetData(filename_restart=fname_restart)
    W_coords = gd_instance.get_atomTypeN_coords(atomType=1)
    He_coords = gd_instance.get_atomTypeN_coords(atomType=3)
    # 找到He与其它He的距离都较大的He的索引
    solo_He_idxs = []
    for idx, He_coord in enumerate(He_coords):
      mask = np.all(He_coords == He_coord, axis=1)
      other_He_coords = He_coords[~mask]
      distances_array = np.linalg.norm(
          He_coord - other_He_coords, axis=1)  # 求He与其他He的距离
      if distances_array.min() > criterion_distance:
        solo_He_idxs.append(idx)

    # 在这些 He 中找到距离W较大的He 也就是逃逸的氦
    escaped_He_idxs = []
    for idx in solo_He_idxs:
      distances_array = np.linalg.norm(He_coords[idx] - W_coords, axis=1)
      if distances_array.min() > criterion_distance:
        escaped_He_idxs.append(idx)

    # 加上z坐标高于W的氦
    escaped_He_idxs.extend(
        np.where(He_coords[:, 2] > W_coords[:, 2].max())[0])
    escaped_He_idxs = list(set(escaped_He_idxs))
    escaped_He_coords_array = He_coords[escaped_He_idxs]
    return escaped_He_coords_array

  def delete_escaped_He_new(self,
                            lmp,
                            escaped_He_coords_array,
                            ):
    """表面模型中去除从钨中逃逸的氦原子, 并保存 restart
    """
    for idx, escaped_He_coord_array in enumerate(escaped_He_coords_array):
      lmp.cmd.region(
          f'{idx} sphere {escaped_He_coord_array[0]} {escaped_He_coord_array[1]} {escaped_He_coord_array[2]} 0.1 units box')
      lmp.command(f'delete_atoms region {idx}')

    number_of_He_deleted = escaped_He_coords_array.__len__()
    return number_of_He_deleted

  def thermo_fig(self, runs_data,
                 x_name='Step',
                 y_name='Temp',
                 is_savefig=False,
                 fname_fig='1.pdf'):

    import matplotlib.pyplot as plt
    print(runs_data[-1].thermo.__dir__())
    for name in runs_data[-1].thermo.__dir__():
      if x_name.lower() == name.lower():
        xdata = eval(f'runs_data[-1].thermo.{x_name}')
      elif y_name == name:
        ydata = eval(f'runs_data[-1].thermo.{y_name}')
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.plot(xdata, ydata, label=y_name)
    ax.set_xlabel(x_name)
    ax.set_ylabel(y_name)
    ax.legend()
    if is_savefig:
      fig.savefig(fname_fig, bbox_inches='tight', dpi=300)
    plt.show()

  def get_velocity_He(self, incidence_energy=30):
    """根据入射能获取He的入射速度, 单位为: A/ps
    """

    q_e = 1.602176462e-19  # C
    energy_incident_in_J = incidence_energy * q_e  # J
    mass_atom = 1.6606e-27  # atom mass unit in kg
    mass_He = mass_atom * 4
    velocity_He_SI = np.sqrt(2 * energy_incident_in_J /
                             mass_He)  # in SI  (m/s)
    velocity_He = velocity_He_SI * 1e-2  # (A/ps)
    return velocity_He

  def get_zmax_W(self,
                 lmp,):
    """获取W 的最高z坐标
    """

    lmp.cmd.group("W type 1")
    lmp.cmd.compute("zmax_W W reduce max z")
    lmp.cmd.thermo_style("custom step c_zmax_W")
    lmp.cmd.run(0)
    zmax_W = lmp.numpy.extract_compute("zmax_W", 0, 0)
    print(zmax_W)
    return lmp

  def incident_single_He(self,
                         lmp,
                         incidence_energy=30,
                         temperature=1300,
                         num_run=2e+5,
                         is_write_restart=False,  # 是否更新restart,
                         fname_restart='restart',
                         num_He_incidence=1,
                         group_ID_mobile='G_mobile',
                         thermo=100,
                         langevin_damp=0.1,
                         is_dump=False,
                         fname_dump='1.dump',
                         ):

    # 获取变量
    velocity_He = self.get_velocity_He(incidence_energy=incidence_energy)
    zmax_W = self.get_zmax_W(fname_restart=fname_restart)

    # Initialize Simulation
    lmp.L.read_restart(fname_restart)
    # Define Interatomic Potential
    lmp.define_interatomic_potential(use_bonnyPot=True)

    # Define Settings
    lmp.L.region('slab',
                 f'block EDGE EDGE EDGE EDGE {zmax_W+10} {zmax_W+10.1} units box')
    lmp.L.group("G_added_He empty")
    lmp.L.compute("add G_added_He temp")
    lmp.L.compute_modify("add dynamic/dof yes extra/dof 0")
    lmp.L.fix('Fdeposit',
              f'G_added_He deposit {num_He_incidence} 3 {int(num_run)} {np.random.randint(100, 1e+5)} region slab vz {-velocity_He} {-velocity_He} units box')  # near 3 去掉了这个关键字
    # 这里run 1 只是为了定义入射氦的组, 由于没有 fix nve 因此所有的原子都不会动, 不论氦的速度多大都不会跑出 slab region
    lmp.L.run(1)
    lmp.L.group('G_added_He region slab')

    # 温度平衡
    # G_He 更新坐标
    lmp.L.group('G_He type 3')
    lmp.L.fix("Fnve2 G_He nve")
    # 衬底温度平衡
    lmp.L.fix(f"Fnve1 {group_ID_mobile} nve")
    lmp.L.fix('Flangevin',
              f"{group_ID_mobile} langevin {temperature} {temperature} {langevin_damp} {np.random.randint(100, 1e+5)} zero yes")
    lmp.L.timestep(1e-3)
    lmp.L.fix("Fdt all dt/reset 1 NULL NULL 0.1 units box")

    # 计算入射的氦的属性 组名: G_added_He
    # lmp.L.compute('properties_He He property/atom z vz')
    # lmp.L.compute(f'z_He He reduce ave c_properties_He[1]')
    # lmp.L.compute(f'vz_He He reduce ave c_properties_He[2]') # 或者这么干
    lmp.L.compute("patom all pe/atom")
    lmp.L.compute("katom all ke/atom")
    lmp.L.compute("He G_added_He reduce ave vz z c_patom c_katom")  # He的速度和z坐标
    lmp.L.variable("vz_He equal c_He[1]")
    lmp.L.variable("z_He equal c_He[2]")
    lmp.L.variable("pe_He equal c_He[3]")
    lmp.L.variable("ke_He equal c_He[4]")
    lmp.L.variable("etotal_He equal (v_ke_He+v_pe_He)")  # He的总能

    lmp.L.compute(f"temp_mobile {group_ID_mobile} temp")
    lmp.L.thermo(thermo)
    lmp.L.thermo_style(
        "custom step time temp etotal pe dt v_z_He v_vz_He v_etotal_He")
    lmp.L.thermo_modify("temp temp_mobile lost ignore")  # lost ignore

    if is_dump:
      lmp.L.dump(f"1 all custom 10 {fname_dump} id type x y z")
      lmp.L.dump_modify("1 first yes")
    if not is_write_restart:  # 如果不更新restart 则可以中途停止
      # 是否中途停止运算, 逻辑值返回1或者0,两种情况: 1.植入，2.反弹，
      average_energy_He = 2.85  # 300K时He在钨中的总能量平均约为2.85 eV.
      lmp.L.variable(
          f'condition equal "((v_etotal_He < {average_energy_He}) && (({zmax_W} - v_z_He) > 3.14) ) || ( (v_z_He > {zmax_W}) && (v_vz_He > 0) )"')
      lmp.L.fix("Fhalt all halt 1 v_condition == 1 message no error continue")
    lmp.L.run(int(num_run))

    # 获取入射信息
    z_He = lmp.L.eval('v_z_He')
    etotal_He = lmp.L.eval('v_etotal_He')
    num_added_He = lmp.L.eval('count(G_added_He)')
    step = lmp.L.runs[-1].thermo.Step
    num_stop_run = step[-1] - step[0]
    if (num_added_He == 1) and ((zmax_W - z_He) > 3) and (num_stop_run < num_run):
      info = f'{z_He} {etotal_He} {num_stop_run} True'
    else:
      info = f'False'

    lmp.L.unfix('Fdeposit')
    lmp.L.uncompute('add')
    lmp.L.uncompute('He')
    lmp.L.uncompute('patom')
    lmp.L.uncompute('katom')
    lmp.L.group('G_added_He delete')

    # 更新restart
    if is_write_restart:
      # 更新运动组
      lmp.L.group(f'{group_ID_mobile} union {group_ID_mobile} G_He')
      lmp.L.write_restart(fname_restart)

    data = {'lmp_instance': lmp,
            'calculated_result': info, }
    return data

  def get_number_of_lines(self,
                          filename='data.csv'):
    """_summary_

    Args:
        filename (str, optional): _description_. Defaults to 'data.csv'.

    Returns: number_of_He_in, number_of_He_total
        _type_: _description_
    """
    if os.path.exists(filename):
      with open(file=filename, mode='r') as f:
        content = f.read()
        He_in_W_list = re.findall("True", content)
        He_out_W_list = re.findall("False", content)
        number_of_He_in = len(He_in_W_list)
        number_of_He_out = len(He_out_W_list)
        number_of_He_total = number_of_He_out+number_of_He_in
      return number_of_He_in, number_of_He_total
    else:
      return 0, 0

  def multiple_irradiation_Non_accumulation(self,
                                            incidence_energy=30,
                                            temperature=1300,
                                            fname_restart='fuzz_restart/restart',
                                            fname_out='data.csv',
                                            min_irradiation_success=2000,
                                            max_irradiation=7000,
                                            ):
    from mpi4py import MPI
    number_of_He_in, num_incidence_times = self.get_number_of_lines(
        filename=fname_out)

    while ((number_of_He_in < min_irradiation_success) and (num_incidence_times < max_irradiation)):
      data = self.incident_single_He(incidence_energy=incidence_energy,
                                     temperature=temperature,
                                     fname_restart=fname_restart,
                                     is_write_restart=False,
                                     num_run=2e+5,
                                     is_dump=False,
                                     )
      if MPI.COMM_WORLD.rank == 0:
        with open(fname_out, mode='a+') as f:
          f.write(data.calculated_result+'\n')
      # 更新
      number_of_He_in, num_incidence_times = self.get_number_of_lines(
          filename=fname_out)

    # 返回数据
    data = {'number_of_He_in': number_of_He_in,
            'num_incidence_times': num_incidence_times}
    return data


class ElasticConstants(BasicFeatures):
  def __init__(self):
    super().__init__()
    """主要参考examples/ELASTIC这个目录来进行的计算"""
    self.parameters_set()
    pass

  def parameters_set(self,
                     lc=3.165,  # 初始化晶格常数
                     lattice_type='bcc',
                     create_atoms_type=1,
                     N_ele=3,
                     dump_element_list=['W', 'H', 'He'],
                     pair_style_str='eam/alloy',
                     pair_coeff_str='* * /Users/wangjinlong/job/soft_learn/lammps_learn/potential/WHHe.eam_bonny/potential-WHHe-EAM2.eam.alloy W H He',
                     ) -> None:
    # 可以在这里重新指定势函数, 要使用自己构建的势函数时需要修改
    self.dump_element_list = dump_element_list
    self.pair_style_str = pair_style_str
    self.pair_coeff_str = pair_coeff_str
    self.lattice_type = lattice_type
    self.N_ele = N_ele
    self.create_atoms_type = create_atoms_type
    self.lc = lc
    return None

  def minimize_for_EC(self, lmp,
                      is_box_relax=False):
    """之后验证 下面两个thermo 命令对结果是否有影响
    用 bf 中的 minimize 进行能量最小化就可以
    """
    # lmp.command('neighbor 1.0 nsq')  # 是否需要？
    # lmp.command('neigh_modify once no every 1 delay 0 check yes')
    # ---
    lmp.command(
        f'thermo_style custom step temp pe press pxx pyy pzz pxy pxz pyz lx ly lz vol')
    lmp.command('thermo_modify norm no')  # 热动力学输出是否根据原子数目进行归一
    lmp = self.minimize(lmp=lmp,
                        min_modify_str='dmax 0.01',
                        min_style_str='cg',
                        is_box_relax=is_box_relax)
    return lmp

  def get_equil_state(self,
                      fname_restart='/Users/wangjinlong/my_server/my/W_Re_potential/test/bulkmod/restart',
                      extra_cmd_list=[],):
    lmp = self.get_lmp(cmdargs=['-log', 'none', '-screen', 'none'])
    lmp = self.initialize(lmp=lmp,)
    # 这里不能使用正交的盒子, 例如block
    lmp = self.build_model_universal(lmp=lmp,
                                     lattice_type=self.lattice_type,
                                     lc=self.lc,
                                     region_str='prism 0 2 0 3 0 4 0 0 0',
                                     create_atoms_type=self.create_atoms_type,
                                     N_ele=self.N_ele)
    lmp = self.define_interatomic_potential(
        lmp=lmp,
        pair_coeff_str=self.pair_coeff_str,
        pair_style_str=self.pair_style_str,
        extra_cmd_list=extra_cmd_list,
    )
    lmp = self.minimize_for_EC(lmp=lmp, is_box_relax=True)

    # ---
    # 这可以防止原子停留在鞍点上, 并写入到 restart
    atomjiggle = 1e-5
    lmp.command(
        f'displace_atoms all random {atomjiggle} {atomjiggle} {atomjiggle} {np.random.randint(1,1000)} units box')
    self.write_restart(
        lmp=lmp,
        fname_restart=fname_restart
    )

    data_dict = {'pxx0': lmp.eval('pxx'),
                 'pyy0': lmp.eval('pyy'),
                 'pzz0': lmp.eval('pzz'),
                 'pyz0': lmp.eval('pyz'),
                 'pxz0': lmp.eval('pxz'),
                 'pxy0': lmp.eval('pxy'),
                 'lx0': lmp.eval('lx'),
                 'ly0': lmp.eval('ly'),
                 'lz0': lmp.eval('lz'),
                 'fname_restart': fname_restart, }

    return data_dict

  def get_elastic_constant(self,
                           equil_state_data,
                           direction,
                           positive_negtive=-1,
                           extra_cmd_list=[],):

    lmp = self.get_lmp_from_restart(
        cmdargs=['-log', 'none', '-screen', 'none'],
        fname_restart=equil_state_data['fname_restart'],
        extra_cmd_list=extra_cmd_list,)

    # Find which reference length to use
    if direction in [1]:
      len0 = equil_state_data['lx0']
    elif direction in [2, 6]:
      len0 = equil_state_data['ly0']
    elif direction in [3, 4, 5]:
      len0 = equil_state_data['lz0']

     # deformation positive_negtive 为1表示正变形，为-1表示负变形 Define the finite deformation size. Try several values of this variable to verify that results do not depend on it.
    up = 1e-6
    delta = positive_negtive * up*len0
    deltaxy = positive_negtive * up * lmp.eval('xy')
    deltaxz = positive_negtive * up * lmp.eval('xz')
    deltayz = positive_negtive * up * lmp.eval('yz')

    if direction == 1:
      lmp.command(
          f"change_box all x delta 0 {delta} xy delta {deltaxy} xz delta {deltaxz} remap units box")
    elif direction == 2:
      lmp.command(
          f"change_box all y delta 0 {delta} yz delta {deltayz} remap units box")
    elif direction == 3:
      lmp.command(f"change_box all z delta 0 {delta} remap units box")
    elif direction == 4:
      lmp.command(f"change_box all yz delta {delta} remap units box")
    elif direction == 5:
      lmp.command(f"change_box all xz delta {delta} remap units box")
    elif direction == 6:
      lmp.command(f"change_box all xy delta {delta} remap units box")

    # Relax atoms positions
    lmp = self.minimize(lmp=lmp, is_box_relax=False)

    # Obtain new stress tensor
    pxx1 = lmp.eval('pxx')
    pyy1 = lmp.eval('pyy')
    pzz1 = lmp.eval('pzz')
    pyz1 = lmp.eval('pyz')
    pxz1 = lmp.eval('pxz')
    pxy1 = lmp.eval('pxy')

    # These formulas define the derivatives w.r.t. strain components
    # Constants uses $, variables use v_
    # Compute elastic constant from pressure tensor
    cfac = 1e-4  # elastic constants in GPa

    C1 = -(pxx1 - equil_state_data['pxx0'])/(delta/len0) * cfac
    C2 = -(pyy1 - equil_state_data['pyy0'])/(delta/len0) * cfac
    C3 = -(pzz1 - equil_state_data['pzz0'])/(delta/len0) * cfac
    C4 = -(pyz1 - equil_state_data['pyz0'])/(delta/len0) * cfac
    C5 = -(pxz1 - equil_state_data['pxz0'])/(delta/len0) * cfac
    C6 = -(pxy1 - equil_state_data['pxy0'])/(delta/len0) * cfac

    arr = np.array([C1, C2, C3, C4, C5, C6])
    return arr

  def get_elastic_constant_tensor(self,
                                  equil_state_data,
                                  extra_cmd_list=[],):
    arr_result = np.zeros((6, 6))  # 初始化一个 6x6 的零矩阵
    for direction in np.arange(1, 7):
      arr1 = self.get_elastic_constant(
          equil_state_data=equil_state_data,
          direction=direction,
          positive_negtive=-1,
          extra_cmd_list=extra_cmd_list,
      )
      arr2 = self.get_elastic_constant(
          equil_state_data=equil_state_data,
          direction=direction,
          positive_negtive=1,
          extra_cmd_list=extra_cmd_list,
      )
      arr = (arr1 + arr2) / 2  # 平均正负变形的结果
      arr_result[:, direction - 1] = arr  # 将结果作为矩阵的一列

    return arr_result

  def get_data_dict(self,
                    elastic_constant_tensor):
    # Average moduli for cubic crystals
    ec_arr = elastic_constant_tensor
    C11cubic = (ec_arr[0, 0] + ec_arr[1, 1] + ec_arr[2, 2])/3
    C12cubic = (ec_arr[0, 1] + ec_arr[0, 2] + ec_arr[1, 2])/3
    C44cubic = (ec_arr[3, 3] + ec_arr[4, 4] + ec_arr[5, 5])/3
    bulk_modulus = (C11cubic + 2*C12cubic)/3
    shear_modulus1 = C44cubic
    shear_modulus2 = (C11cubic - C12cubic)/2
    poisson_ratio = 1/(1 + C11cubic/C12cubic)
    data_dict = {'C11': C11cubic, 'C12': C12cubic,
                 'C44': C44cubic, 'bulk_modulus': bulk_modulus,
                 'shear_modulus1': shear_modulus1, 'shear_modulus2': shear_modulus2, 'poisson_ratio': poisson_ratio}
    return data_dict

  def get_data_dict_wrapper(self,
                            lc=3.165,  # 初始化晶格常数
                            lattice_type='bcc',
                            create_atoms_type=1,
                            N_ele=3,
                            dump_element_list=['W', 'H', 'He'],
                            pair_style_str='eam/alloy',
                            pair_coeff_str='* * /Users/wangjinlong/job/soft_learn/lammps_learn/potential/WHHe.eam_bonny/potential-WHHe-EAM2.eam.alloy W H He',
                            fname_restart='/Users/wangjinlong/my_server/my/W_Re_potential/test/bulkmod/restart',
                            extra_cmd_list=[],):
    self.parameters_set(lc=lc,
                        lattice_type=lattice_type,
                        create_atoms_type=create_atoms_type,
                        N_ele=N_ele,
                        dump_element_list=dump_element_list,
                        pair_style_str=pair_style_str,
                        pair_coeff_str=pair_coeff_str,
                        )
    equil_state_data = self.get_equil_state(
        fname_restart=fname_restart,
        extra_cmd_list=extra_cmd_list,)
    elastic_constant_tensor = self.get_elastic_constant_tensor(
        equil_state_data=equil_state_data,
        extra_cmd_list=extra_cmd_list,)
    data_dict = self.get_data_dict(
        elastic_constant_tensor=elastic_constant_tensor)
    return data_dict

  def get_data_dict_wrapper_example_Si(self):
    data_dict = self.get_data_dict_wrapper(lc=5.43,
                                           lattice_type='diamond',
                                           create_atoms_type=1,
                                           N_ele=1,
                                           dump_element_list=['Si'],
                                           pair_coeff_str='* * /Users/wangjinlong/job/soft_learn/lammps_learn/package/mylammps/examples/ELASTIC/Si.sw Si',
                                           pair_style_str='sw',
                                           extra_cmd_list=['mass 1 1.0e-20']
                                           )
    return data_dict


class LmpFeatures():
  def __init__(self) -> None:
    """ lammps 中带的 python 包
    完整的lammps计算, 用于完成特定的功能
    直接使用的是, lammps 的 python 包, 建议使用 aselammpslib
    """
    self.BasicFeatures = self.bf = BasicFeatures()

    # 总结计算获得的数据
    self.parameters_set()
    pass

  def determine_lc_E_patom(self, lc=3.165,
                           lattice_type='bcc',
                           create_atoms_type=1,
                           N_ele=3,
                           ) -> pd.DataFrame:
    """获取晶格常数和 化学势
    """
    lmp = self.bf.get_lmp_universal(
        cmdargs=['-log', 'none',
                 '-screen', 'none',
                 '-echo', 'none',
                 ],
        boundary='p p p',
        lattice_type=lattice_type,
        lc=lc,
        create_atoms_type=create_atoms_type,
        N_ele=N_ele,
        block_size=[0, 1, 0, 1, 0, 1],
    )
    lmp = self.bf.minimize(lmp=lmp,
                           is_box_relax=True,
                           etol=0,
                           ftol=1e-8,)
    lc_a = lmp.eval('lx')
    lc_b = lmp.eval('ly')
    lc_c = lmp.eval('lz')
    E_patom = lmp.eval('pe')/lmp.get_natoms()

    lc_arr = np.array([lc_a, lc_b, lc_c])
    if not np.all(lc_arr == lc_arr[0]):
      print('注意晶格常数不同')

    data = {'lc_a': lc_a, 'lc_b': lc_b, 'lc_c': lc_c, 'E_patom': E_patom}
    df = self.pandasLearn.PandasLearn().get_df_from_dict(data=data)
    return df

  def parameters_set(self,
                     lc=3.165,  # 初始化晶格常数
                     lattice_type='bcc',
                     create_atoms_type=1,
                     N_ele=3,
                     dump_element_list=['W', 'H', 'He'],
                     pair_style_str='eam/alloy',
                     pair_coeff_str='* * /Users/wangjinlong/job/soft_learn/lammps_learn/potential/WHHe.eam_bonny/potential-WHHe-EAM2.eam.alloy W H He',
                     extra_cmd_list=[],
                     ) -> None:
    # 可以在这里重新指定势函数, 要使用自己构建的势函数时需要修改
    self.BasicFeatures.dump_element_list = self.dump_element_list = dump_element_list
    self.BasicFeatures.pair_style_str = self.pair_style_str = pair_style_str
    self.BasicFeatures.pair_coeff_str = self.pair_coeff_str = pair_coeff_str

    self.lattice_type = lattice_type
    self.N_ele = N_ele
    self.create_atoms_type = create_atoms_type
    self.df = self.determine_lc_E_patom(
        lc=lc,
        lattice_type=self.lattice_type,
        create_atoms_type=self.create_atoms_type,
        N_ele=self.N_ele
    )
    self.lc = self.df.loc['lc_a'].value
    self.extra_cmd_list = extra_cmd_list
    return None

  def minimize_example(self,
                       directory='/Users/wangjinlong/my_server/my/W_Re_potential/test',
                       cmdargs=['-log', 'none', '-screen', 'none',
                                '-echo', 'none']
                       ):
    lmp = self.bf.get_lmp(cmdargs=cmdargs)
    lmp = self.bf.initialize(lmp=lmp,)
    lmp = self.bf.construct_bulk(lmp=lmp,
                                 block_size=[-2, 2, -2, 2, -2, 2],
                                 )
    lmp = self.bf.define_interatomic_potential(lmp=lmp)
    lmp = self.bf.create_atoms(lmp=lmp, string='3 single 0.5 0 0.5')
    lmp = self.bf.minimize(lmp=lmp,)
    self.bf.dump(lmp=lmp, num_run=0,
                 dump_element_list=self.bf.dump_element_list)
    lmp = self.bf.run(
        lmp=lmp,
        num_run=0,
    )

    self.bf.write_restart(lmp=lmp,
                          fname_restart=os.path.join(directory, 'minimize.restart'))

    return lmp

  def equilibrium_example(self,
                          directory='/Users/wangjinlong/my_server/my/W_Re_potential/test',
                          num_run=2000,
                          cmdargs=['-log', 'none', '-screen', 'none',
                                   '-echo', 'none']
                          ):
    lmp = self.bf.get_lmp_from_restart(
        fname_restart=os.path.join(directory, 'minimize.restart'),
        cmdargs=cmdargs,
    )
    lmp = self.BasicFeatures.equilibrium_NPT(lmp=lmp, Tstart=80,)
    lmp = self.BasicFeatures.dump(lmp=lmp,
                                  num_run=num_run,
                                  fname_dump=os.path.join(
                                      directory, 'equili.dump'),
                                  dump_element_list=self.dump_element_list,
                                  )
    lmp = self.BasicFeatures.run(
        lmp=lmp,
        num_run=num_run,
    )
    lmp = self.BasicFeatures.write_restart(lmp=lmp,
                                           fname_restart=os.path.join(directory, 'equili.restart'))
    return lmp

  def add_df_to_self_df(self, df):
    self.df = self.pandasLearn.PandasLearn().concat_df(df_list=[self.df, df])
    return self.df

  def get_E_cohensive(self,):
    """cohensive energy = (E_bulk - natoms*Eatom_in_vacuum)/ natoms
    聚合能: 如果把各组成部分分开到“无穷远”处，当然需要一定的能量来提供克服有关吸引力，即需做功。所需做的功的大小，说明各组成部分结合的紧密程度，称为该物体的结合能。
    """
    lmp = self.bf.get_lmp_universal(cmdargs=['-log', 'none',
                                             '-screen', 'none',
                                             '-echo', 'none',
                                             ],
                                    boundary='p p p',
                                    lattice_type='bcc',
                                    lc=self.lc,
                                    create_atoms_type=1,
                                    N_ele=3,
                                    block_size=[-3, 3, -3, 3, -3, 3],)
    lmp = self.bf.delete_atoms_with_group(lmp=lmp, group_name='all')
    lmp = self.bf.create_atoms(lmp=lmp, string='1 single 0 0 0')
    lmp = self.bf.run(lmp=lmp, num_run=0)

    E_atom_in_vacuum = lmp.eval('pe')
    E_cohensive = E_atom_in_vacuum - self.df.loc['E_patom'].value
    df = self.pandasLearn.PandasLearn().get_df_from_dict(
        data={'E_atom_in_vacuum': E_atom_in_vacuum,
              'E_cohensive': E_cohensive
              })
    self.add_df_to_self_df(df)
    return df

  def get_Ef_vacancy(self,):
    """对于不是W的空位形成能, 则需要另外设置
    """
    lmp = self.bf.get_lmp_universal(lc=self.lc,
                                    block_size=[-5, 5]*3,
                                    lattice_type=self.lattice_type,
                                    create_atoms_type=self.create_atoms_type,
                                    N_ele=self.N_ele
                                    )
    lmp = self.bf.minimize(lmp=lmp,
                           is_box_relax=False)
    E_pefect_bulk = lmp.eval('pe')
    E_patom = E_pefect_bulk/lmp.get_natoms()
    lmp = self.bf.delete_atoms_with_no_group(lmp=lmp,
                                             build_group_id=1)
    self.bf.minimize(lmp=lmp, is_box_relax=False)
    E_defect_bulk = lmp.get_thermo('pe')
    Ef_vacancy = E_defect_bulk + E_patom - E_pefect_bulk
    df = self.pandasLearn.PandasLearn().get_df_from_dict(
        data={'Ef_vacancy': Ef_vacancy},)
    self.add_df_to_self_df(df)
    return df

  def get_elastic_constants(self,):
    data_dict = ElasticConstants().get_data_dict_wrapper(
        lc=self.lc,
        lattice_type=self.lattice_type,
        create_atoms_type=self.create_atoms_type,
        N_ele=self.N_ele,
        dump_element_list=self.dump_element_list,
        pair_coeff_str=self.pair_coeff_str,
        pair_style_str=self.pair_style_str,
        extra_cmd_list=self.extra_cmd_list,
    )
    df = self.pandasLearn.PandasLearn().get_df_from_dict(
        data=data_dict)
    self.add_df_to_self_df(df)
    return df

  def get_Ef_SIA(self,
                 direction='111'):
    lmp = self.bf.get_lmp_universal(
        cmdargs=['-log', 'none', '-screen', 'none'],
        boundary='p p p',
        lattice_type=self.lattice_type,
        lc=self.lc,
        create_atoms_type=self.create_atoms_type,
        N_ele=self.N_ele,
        block_size=[-5, 5, -5, 5, -5, 5],
        extra_cmd_list=self.extra_cmd_list,
    )
    lmp = self.bf.run(lmp=lmp, num_run=0)
    E_patoms = lmp.eval('pe')/lmp.get_natoms()
    coords = np.where([int(i) for i in direction], 0.1, 0)
    lmp = self.bf.create_atoms(
        lmp=lmp,
        string=f"{self.create_atoms_type} single {' '.join(coords.astype(str))}")
    lmp = self.bf.minimize(lmp=lmp, is_box_relax=False)
    E_f_SIA = lmp.eval('pe') - E_patoms*lmp.get_natoms()

    return E_f_SIA

  def get_Ef_SIAs(self,
                  direction_list=['111', '110', '100']):
    data = {}
    for direction in direction_list:
      E_f_SIA = self.get_Ef_SIA(direction=direction)
      data.update({f'E_f_{direction}_SIA': E_f_SIA, })

    df = self.pandasLearn.PandasLearn().get_df_from_dict(
        data=data)
    self.add_df_to_self_df(df)
    return df

  def get_Eatom_in_vacuum(self,
                          atom_type=1,):
    lmp = self.bf.get_lmp_universal(
        cmdargs=['-log', 'none', '-screen', 'none'],
        boundary='p p p',
        lattice_type=self.lattice_type,
        lc=self.lc,
        create_atoms_type=self.create_atoms_type,
        N_ele=self.N_ele,
        block_size=[-3, 3, -3, 3, -3, 3],
        extra_cmd_list=self.extra_cmd_list,
    )
    lmp = self.bf.delete_atoms_with_group(lmp=lmp,
                                          group_name='all')
    lmp = self.bf.create_atoms(lmp=lmp,
                               string=f'{atom_type} single 0 0 0')
    lmp = self.bf.run(lmp=lmp, num_run=0)
    E_atom_in_vacuum = lmp.eval('pe')

    df = self.pandasLearn.PandasLearn().get_df_from_dict(
        data={f'E_{self.dump_element_list[atom_type-1]}_in_vacuum': E_atom_in_vacuum})
    self.add_df_to_self_df(df)
    return lmp
