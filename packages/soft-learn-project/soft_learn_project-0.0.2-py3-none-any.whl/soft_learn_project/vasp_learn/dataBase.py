import ase.db
import os
import ase.parallel
import ase.visualize
import ase.io
import ase.visualize
import ase.calculators.vasp
import pandas as pd
from py_package_learn.functools_learn import functoolsLearn
import numpy as np
from py_package_learn.ase_learn import aseLearn


class DataBase(aseLearn.DataBase, metaclass=functoolsLearn.AutoDecorateMeta):
  def __init__(self):
    """如果出错可以查看是否多出文件'db_all.json.lock',删除即可
    """
    super().__init__()
    self.fname_db = os.path.join(
        os.environ['HOME'], 'my_server/my/db_all.json')
    self.fname_db_bk = os.path.join(
        os.environ['HOME'], 'my_server/my/db_all.bk.json')
    self.db = ase.db.connect(self.fname_db)
    self.df_researchdata = pd.DataFrame()
    pass

  def write_relax_2db(self,
                      directory_relax=None,
                      dbname=None, ):
    """dbname | directory_relax 提供一个

    Args:
        dbname (_type_, optional): _description_. Defaults to None.
        directory_relax (_type_, optional): _description_. Defaults to None.
    """
    directory_relax, dbname = self.choice_directory_dname(
        directory=directory_relax, dbname=dbname)
    f_outcar = os.path.join(directory_relax, 'OUTCAR')
    try:
      atoms = ase.io.read(filename=f_outcar)
    except:
      print(f'{dbname} -> 没有迟豫完成!')
      return

    calc = ase.calculators.vasp.Vasp(directory=directory_relax, restart=True)
    if calc.converged:  # 收敛标准
      self.db_write_and_update(atoms=atoms,
                               directory=directory_relax,
                               dbname=dbname)
      print(f'{dbname} -> 写入 relaxation 结果. ')
      self.delete_large_file(pardir=directory_relax,
                             check=False,)
    else:
      print(f'{dbname} -> 未写入db, 计算未收敛!!!')
    return

  def write_single_point_2db(self,
                             dbname=None,
                             directory_relax=None,
                             **kwargs):
    """单点计算后获取ACF.dat, 写入 db initial_charges 和 initial_magnetic_moments 到 db
    """

    from vasp_learn import dealData
    directory_relax, dbname = self.choice_directory_dname(
        directory=directory_relax, dbname=dbname)
    directory_sp = os.path.join(directory_relax, 'single_point')
    calc = ase.calculators.vasp.Vasp(directory=directory_sp, restart=True)
    if not calc.read_convergence():
      print(f'Waring: 单点计算为收敛, 没有写入单点数据.')
      return None

    # bader charge
    atoms: ase.Atoms = dealData.DealData().bader_analysis(
        directory_relax=directory_relax, dbname=dbname)
    # 写入 db initial_charges 和 initial_magnetic_moments
    self.db_update_values(name=dbname,
                          data={'initial_charges': atoms.get_initial_charges(),
                                'initial_magnetic_moments': atoms.get_initial_magnetic_moments()},
                          **kwargs)
    print(f'{dbname} ->写入单点计算的电荷和磁矩数据. ')
    # 写入必要的数据到db后删除大文件
    self.delete_large_file(pardir=directory_relax,
                           check=False,)
    return None

  def write_sol_eff2db(self,
                       dbname=None,
                       directory_relax=None,):
    """* sol_eff 目录计算完成后写入数据.
    * directory_relax 和 dbname 取其一, 优先directory_relax

    Args:
        directory_relax (_type_, optional): _description_. Defaults to None.
        dbname (str, optional): _description_. Defaults to 'graphene72atoms'.
    """

    directory_relax, dbname = self.choice_directory_dname(
        directory=directory_relax, dbname=dbname)

    # db
    atoms = atoms = ase.io.read(os.path.join(
        directory_relax, 'sol_eff', 'OUTCAR'))
    self.db_update_values(name=dbname,
                          energy_sol_eff=atoms.get_potential_energy(),
                          )
    # 写入必要的数据到db后删除大文件
    self.delete_large_file(pardir=directory_relax,
                           check=False,)
    print(f'{dbname} ->写入溶剂化效应的能量 energy_sol_eff. ')

    return

  def write_thermodata2db(self,
                          dbname=None,
                          directory_relax=None,
                          system='adsorbate|adsorbate_on_slab',
                          temperature=298.15,
                          pressure=101325,
                          gas_paras_dict={'symmetrynumber': 1,
                                          'spin': 0,
                                          'geometry': 'linear', }):
    """
    - vib 和 sol_eff 目录计算完成后才能写入完整的数据
    - directory_relax 和 dbname 取其一, 优先directory_relax

    Args:
        directory_relax (_type_, optional): _description_. Defaults to None.
        dbname (str, optional): _description_. Defaults to 'O2_graphene72atoms'.
        system (str, optional): _description_. Defaults to 'adsorbate|adsorbate_on_slab'.
        temperature (int, optional): _description_. Defaults to 298.15.
        pressure (int, optional): _description_. Defaults to 101325.

    Returns:
        _type_: _description_
    """

    from vasp_learn import dealData
    directory_relax, dbname = self.choice_directory_dname(
        directory=directory_relax, dbname=dbname)

    # 获得 thermodata
    if system == 'adsorbate':
      thermodata = dealData.DealData().get_thermodata_gas_sol_eff_wrapper(
          directory_relax=directory_relax,
          pressure=pressure,
          temperature=temperature,
          **gas_paras_dict,
      )
    elif system == 'adsorbate_on_slab':
      thermodata = dealData.DealData().get_thermodata_adsorbate_on_slab_sol_eff_wrapper(
          directory_relax=directory_relax,
          temperature=temperature)
    else:
      print("请输入正确的system: 'adsorbate|adsorbate_on_slab'")
      return
    # 写入 db
    self.db_update_values(name=dbname,
                          **thermodata)
    print(f'{dbname} ->写入热力学数据. ')
    # 写入必要的数据到db后删除大文件
    self.delete_large_file(pardir=directory_relax,
                           check=False,)
    return thermodata

  def write_thermodata2db_wrapper(self,
                                  is_gas=False,
                                  dbname='OH|B_O_Gra',
                                  directory_relax=None,
                                  temperature=298.15,
                                  gas_paras_dict={'symmetrynumber': 1,
                                                  'spin': 0,
                                                  'geometry': 'linear', }
                                  ):
    if is_gas:
      pressure = 3500 if dbname == 'H2O' else 101325
      self.write_thermodata2db(directory_relax=directory_relax,
                               dbname=dbname,
                               system='adsorbate',
                               temperature=temperature,
                               pressure=pressure,
                               gas_paras_dict=gas_paras_dict)
    else:
      self.write_thermodata2db(dbname=dbname,
                               directory_relax=directory_relax,
                               system='adsorbate_on_slab',
                               temperature=temperature,
                               )
      pass
    pass

  def delete_large_file(self, pardir='.',
                        check=True,
                        key_list=['CHG', 'WAVECAR',
                                  'AEC', 'RHOION',
                                  ],  # 'PROCAR', 'DOSCAR'
                        ):
    """写入数据到 db 后 删除大文件"""
    from py_package_learn.os_learn import osLearn
    fname_list = []
    for dirpath, dirnames, filenames in os.walk(top=pardir):
      for filename in filenames:
        for key in key_list:
          if key in filename:
            fname = os.path.join(dirpath, filename)
            fsize = osLearn.OsLearn().get_file_size(fname=fname)
            if fsize > 0:
              fname_list.append(fname)
    for f in fname_list:
      if check:
        print(f'确认删除? check=False -> {f}')
      else:
        os.remove(f)
        print(f'删除文件-> {f}')

    return fname_list

  # 进阶
  def write_relax_2db_wrapper(self, pardir):
    """ 获取pardir 下面目录的迟豫信息
    """
    fl = os.listdir(path=pardir)
    for f in fl:
      d = os.path.join(pardir, f)
      self.write_relax_2db(directory_relax=d)
    return None

  def write_sp_se_vib_2db(self,
                          is_gas=False,
                          dbname=None,
                          ):
    """根据dbname 写入 single_point, sol_eff, vib (热力学) 能量等信息
    # 注意是否是气体

    Args:
        dbname (_type_, optional): _description_. Defaults to None.
        directory_relax (_type_, optional): _description_. Defaults to None.
        is_gas (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """

    try:
      self.write_single_point_2db(dbname=dbname,
                                  directory_relax=None)
    except:
      print(f'{dbname} 没有 single_point 计算而出错.')
    try:
      self.write_sol_eff2db(dbname=dbname,
                            directory_relax=None,)
    except:
      print(f'{dbname} 没有 sol_eff 计算而出错.')

    try:
      self.write_thermodata2db_wrapper(is_gas=is_gas,
                                       dbname=dbname,
                                       directory_relax=None)
    except:
      print(f'{dbname} 没有频率计算而出错, 没问题.')

    return None

  def write_sp_se_vib_2db_wrapper(self,
                                  slab,
                                  adsorbates=['O2', 'O2H', 'O', 'OH'],
                                  is_gas=False,
                                  ):
    for ads in adsorbates:
      dbname = f'{ads}_{slab}'
      self.write_sp_se_vib_2db(is_gas=is_gas,
                               dbname=dbname)
    return None

  def write_relax_sp_se_vib_2db(self, directory_relax,
                                is_gas):
    """对于气体, is_gas=True
    """
    self.write_relax_2db(directory_relax=directory_relax,)
    directory_relax, dbname = self.choice_directory_dname(
        directory=directory_relax, dbname=None)
    self.write_sp_se_vib_2db(is_gas=is_gas,
                             dbname=dbname)
    pass

  def write_relax_sp_se_vib_2db_ORR_wrapper(self,
                                            pardir='/Users/wangjinlong/my_server/my/myORR_B/slab/X_graphene/P_MVG',
                                            ads_list=['O2', 'O2H', 'O', 'OH'],
                                            slab='Si_P_3V_Gra',
                                            ):
    """获取父目录下 四个吸附物@slab 的信息

    Args:
        pardir (str, optional): _description_. Defaults to '/Users/wangjinlong/my_server/my/myORR_B/slab/X_graphene/P_MVG'.

    Returns:
        _type_: _description_
    """

    for adsorbate in ads_list:
      ads_on_slab = f'{adsorbate}_{slab}'
      directory_relax = os.path.join(pardir, ads_on_slab)
      self.write_relax_sp_se_vib_2db(directory_relax=directory_relax,
                                     is_gas=False)
    return None

  # other
  def get_directory(self, dbname='N1_graphene'):
    directory = self.db.get(name=dbname).directory
    return directory

  def get_energy(self, dbname='O2H_graphene72atoms',
                 directory=None,
                 energy_name='energy',
                 is_sol_eff=False,
                 is_ammend_O2=True,):
    """获取dbname 的指定能量

    Args:
        dbname (str, optional): _description_. Defaults to 'O2H_graphene72atoms'.
        energy_name (str, optional): 'energy' 或者 'free_energy', Defaults to 'energy'.
        is_sol_eff (bool, optional): _description_. Defaults to True.
        is_ammend_O2 (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """

    try:
      if dbname is not None:
        row = self.db.get(name=dbname)
      elif directory is not None:
        row = self.db.get(directory=directory)
    except:
      print(f'{dbname} 不存在')
    if energy_name == 'energy':
      energy = row.energy_sol_eff if is_sol_eff else row.energy
    elif energy_name == 'free_energy':  # 获取自由能
      try:
        if dbname == 'O2' and is_ammend_O2:
          # 是否使用4.92 来修正 2*E_H2O - 2 *E_H2 + 4.92
          if is_sol_eff:
            energy = 2*self.db.get(name='H2O').gibbs_energy_sol_eff - \
                2*self.db.get(name='H2').gibbs_energy_sol_eff + 4.92
          else:
            energy = 2*self.db.get(name='H2O').gibbs_energy - \
                2*self.db.get(name='H2').gibbs_energy + 4.92
        else:
          energy = row.gibbs_energy_sol_eff if is_sol_eff else row.gibbs_energy
      except:
        try:
          energy = row.helmholtz_energy_sol_eff if is_sol_eff else row.helmholtz_energy
        except:  # 如果是衬底则取总能量
          energy = row.energy_sol_eff if is_sol_eff else row.energy
          pass
    else:
      print('energy_name 参数错误!')
      return

    return energy

  def get_energy_from_dir(self,
                          directory='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/X_graphene/Br_DVG/C40/O2H_Br_DVG'):
    calc = ase.calculators.vasp.Vasp(restart=True, directory=directory)
    energy = calc.get_potential_energy()
    return energy

  def get_atoms(self, dbname):
    atoms = self.get_atoms_list(dbname=dbname)[-1]
    return atoms

  def get_atoms_list(self, dbname=None,
                     directory=None,
                     is_md=False,
                     is_view=False):
    """获取vasp 计算目录中的 atoms_list
    终端执行该命令可以看能量变化(plot)= f'ase gui {os.path.join(directory,fname)}'

    使用vasprun.xml 能查看体系的能量和最大力, 但对于VASP md 模拟读取会出错要用 XDATCAR
    aseLearn.Features().view_and_save(atoms: Any, fname: str = 'atoms.png', rotation: str = '-90x,0y,0z')
    """

    directory, dbname = self.choice_directory_dname(
        directory=directory, dbname=dbname)

    if is_md:  # 对于 md 文件路径包括 'ab_md'
      filename = os.path.join(directory, 'ab_md', 'XDATCAR')
    else:
      filename = os.path.join(directory, 'vasprun.xml')

    try:
      atoms_list = ase.io.read(filename=filename, index=':')
    except:
      atoms_list = ase.io.read(filename=filename+'.gz', index=':')

    if is_view:
      ase.visualize.view(atoms_list)
    return atoms_list

  def get_atoms_with_infos(self, dbname='P_N1_graphene', is_view=False):
    """计算单点并运行 self.write_single_point_info2db() 之后,
    获得原子结构以及电荷分布和自旋磁矩分布的 atoms

    之后的输出 ase.io.write('output.xyz', atoms, ) 会带有这些信息

    Args:
        dbname (str, optional): _description_. Defaults to 'P_N1_graphene'.

    Returns:
        _type_: _description_
    """

    row = self.db.get(name=dbname)
    atoms: ase.Atoms = row.toatoms()
    atoms.set_initial_charges(row.data['initial_charges'])
    atoms.set_initial_magnetic_moments(row.data['initial_magnetic_moments'])
    if is_view:
      ase.visualize.view(atoms)
    return atoms

  def get_atoms_from_file(self, fname='xxx/POSCAR'):
    atoms = ase.io.read(filename=fname)
    return atoms

  def get_df_zpe_entropy_for_SI(self, dbname_list=['O2', 'O']):
    zpe_list = []
    entropy_list = []
    for name in dbname_list:
      row = self.db.get(name=name)
      zpe = row.key_value_pairs.get('zpe')
      entropy = row.key_value_pairs.get('entropy')
      zpe_list.append(zpe)
      entropy_list.append(entropy)

    df = pd.DataFrame(data={'entropy': entropy_list,
                      'ZPE': zpe_list},
                      index=dbname_list,)
    return df

  def get_energy_for_SI(self, dbname, directory=None,
                        energy_name='energy',
                        is_sol_eff=False,
                        is_ammend_O2=True,
                        ):
    try:
      energy = self.get_energy(dbname=dbname,
                               directory=directory,
                               energy_name=energy_name,
                               is_sol_eff=is_sol_eff,
                               is_ammend_O2=is_ammend_O2)
    except:
      energy = np.nan

    return energy

  def get_df_research_data(self, dbname_list=[],
                           decimals=3):
    """获得文中主要用到的数据

    Args:
        dbname_list_slab (_type_): _description_
    """

    energy_list = []
    energy_sol_list = []
    gibbs_energy_list = []
    gibbs_energy_sol_list = []
    dbname_list_added = []
    zpe_list = []
    entropy_list = []
    for dbname in dbname_list:
      if dbname in self.df_researchdata.index:
        pass
      else:
        dbname_list_added.append(dbname)
        energy = self.get_energy_for_SI(dbname=dbname,
                                        energy_name='energy',
                                        is_sol_eff=False)
        energy_list.append(energy)
        energy_sol = self.get_energy_for_SI(dbname=dbname,
                                            energy_name='energy',
                                            is_sol_eff=True)
        energy_sol_list.append(energy_sol)
        gibbs_energy = self.get_energy_for_SI(dbname=dbname,
                                              energy_name='free_energy',
                                              is_sol_eff=False)
        gibbs_energy_list.append(gibbs_energy)
        gibbs_energy_sol = self.get_energy_for_SI(dbname=dbname,
                                                  energy_name='free_energy',
                                                  is_sol_eff=True)
        gibbs_energy_sol_list.append(gibbs_energy_sol)

        # ZPE and entropy
        row = self.db.get(name=dbname)
        zpe = row.key_value_pairs.get('zpe')
        zpe_list.append(zpe)
        entropy = row.key_value_pairs.get('entropy')
        entropy_list.append(entropy)

    data = {
        'energy': energy_list,
        'energy_sol': energy_sol_list,
        'gibbs_energy': gibbs_energy_list,
        'gibbs_energy_sol': gibbs_energy_sol_list,
        'zpe': zpe_list,
        'entropy': entropy_list}

    df = pd.DataFrame(data=data,
                      index=dbname_list_added).round(decimals=decimals)
    # 更新 self.df_researchdata
    self.df_researchdata = pd.concat([self.df_researchdata, df])
    self.df_researchdata: pd.DataFrame = self.df_researchdata.loc[dbname_list]
    return self.df_researchdata

  def get_df_research_data_wrapper(self, dbname_slab_list,
                                   decimals=6,
                                   is_save=False,
                                   directory='/Users/wangjinlong/my_server/my/myORR_B/xxx/',
                                   fname='research_data.csv',
                                   format_str='{: .5e}'):
    """获得文中主要用到的数据
    """
    # 设置显示格式为科学计数法，并保留 6 位有效数字
    pd.options.display.float_format = format_str.format
    fname = os.path.join(directory, fname)
    if os.path.exists(fname):
      df = pd.read_csv(fname, index_col=0)
    else:
      dbname_gas_list = ['H2', 'H2O',]
      dbname_adsorbate_list = ["O2", 'O2H', 'O', 'OH']
      dbname_adsorbate_on_slab_list = []
      for slab in dbname_slab_list:
        for adsorbate in dbname_adsorbate_list:
          dbname_adsorbate_on_slab = f'{adsorbate}_{slab}'
          dbname_adsorbate_on_slab_list.append(dbname_adsorbate_on_slab)
      dbname_list = [*dbname_gas_list, *dbname_adsorbate_list,
                     *dbname_slab_list, *dbname_adsorbate_on_slab_list]

      df = self.get_df_research_data(dbname_list=dbname_list,
                                     decimals=decimals)
      df = df.dropna(how='all')  # 来删除 DataFrame 中全为 NaN 的行
      if is_save:
        df.to_csv(fname)
    # 最后处理
    # energy	energy_sol	gibbs_energy	gibbs_energy_sol	zpe	entropy
    df.columns = ['E', r'E$_{sol}$', 'G', r'G$_{sol}$', 'ZPE', 'S']
    return df

  def write_info2_db_all(self):
    """误删 db_all.json 重新获取数据
    """
    for dirpath, dirnames, filenames in os.walk(top='/Users/wangjinlong/my_server/my/myORR_B'):
      if ('OUTCAR' in filenames) and ('single_point' not in dirpath) and ('sol_eff' not in dirpath) and ('cdd' not in dirpath) and ('ab_md' not in dirpath):
        try:
          self.write_relax_2db(directory_relax=dirpath)
          dbname = os.path.basename(dirpath)
          is_gas = True if ('/adsorbate/' in dirpath) else False
          self.write_sp_se_vib_2db(is_gas=is_gas, dbname=dbname)
        except:
          pass
        pass
