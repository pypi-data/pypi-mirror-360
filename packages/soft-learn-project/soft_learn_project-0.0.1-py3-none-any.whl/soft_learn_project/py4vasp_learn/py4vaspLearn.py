import os
import py4vasp
import py4vasp.calculation
import pandas as pd
from py_package_learn.functools_learn import functoolsLearn
from py_package_learn.matplotlib_learn import matplotlibLearn


# 主要使用这个 py4vasp_data


class Py4vaspData():
  def __init__(self) -> None:
    """Module
    用来处理数据
    """
    pass

  def dos_example(self):
    calc = py4vasp.Calculation.from_path('CO')
    calc.dos.to_graph(selection="1(p)")

  def plot_band(self):
    # The electronic band structure.
    py4vasp.data.Band
    calc = py4vasp.Calculation.from_path(
        '/Users/wangjinlong/my_linux/soft_learn/vasp_learn/tmp/Si_bulk/bs')
    # calc.band.plot()
    band = py4vasp.data.Band.from_path(
        path='/Users/wangjinlong/my_linux/soft_learn/vasp_learn/tmp/Si_bulk/bs')
    band.plot()

  def born_effective_charge(self):
    # The Born effective charge tensors coupling electric field and atomic displacement.
    py4vasp.data.BornEffectiveCharge
    pass

  def density(self,):
    # The charge and magnetization density. (py4vasp.data.Density)
    py4vasp.data.Density.plot()

  def dielectric_function(self):
    # The dielectric function resulting from electrons and ions.
    py4vasp.data.DielectricFunction()

  def dielectric_tensor(self):
    # The static dielectric tensor obtained from linear response.
    py4vasp.data.DielectricTensor

  def dispersion(self):
    # Generic class for all dispersions (electrons, phonons).
    py4vasp.data.Dispersion

  def dos(self):
    calc = py4vasp.Calculation.from_path(
        '/Users/wangjinlong/my_linux/soft_learn/vasp_learn/tmp/CO')
    dos = calc.dos.read('C(s)')
    dos = calc.dos.read('C(s,px)')
    calc.dos.plot('C(s,px)')

    # 可以用于加标签 和将两幅图加起来
    py4vasp.data.Dos.from_path('bulk_Si/dos').plot().label('Si') + \
        py4vasp.data.Dos.from_path('CO/pdos/').plot().label('CO')

  def elastic_modulus(self):
    # The elastic modulus (second derivatives w.r.t. strain)
    py4vasp.data.ElasticModulus

  def energy(self, directory):
    # The energy data for one or several steps of a relaxation or MD simulation.
    # py4vasp.data.Energy
    energy = py4vasp.data.Energy.from_path(path=directory)
    # print(energy[1:5].read()) # 查看
    energy[:].plot("TOTEN, ETOTAL").to_plotly().show()

  def fatband(self):
    # Access data for producing BSE fatband plots.
    py4vasp.data.Fatband

  def force(self):
    # The forces acting on the atoms for selected steps of the simulation.
    py4vasp.data.Force

  def force_constant(self):
    # The force constants (second derivatives of atomic displacement).
    py4vasp.data.ForceConstant

  def internal_strain(self):
    # The internal strain
    py4vasp.data.InternalStrain

  def kpoint(self):
    # The k points used in the Vasp calculation.
    py4vasp.data.Kpoint

  def magnetism(self):
    # The magnetic moments and localized charges for selected ionic steps.
    py4vasp.data.Magnetism

  def pair_correlation(self, directory):
    """ 径向分布函数g(r) 当r 超过晶胞尺寸最小的维度一半时就变得无意义 当前的模型尺寸为array([10.937456, 10.937456, 10.937456]) 一半为5.46
    example
    pcf1 = py4vasp.data.PairCorrelation.from_path('Si64')
    pcf2 = py4vasp.data.PairCorrelation.from_path('Si64/continue/')
    pcf1.plot().label('90fs') + pcf2.plot().label('180fs')
    """
    # The pair-correlation function for one or several blocks of an MD simulation.
    # py4vasp.data.PairCorrelation
    pcf = py4vasp.data.PairCorrelation.from_path(directory)
    return pcf

  def phonon_band(self):
    # The phonon band structure.
    py4vasp.data.PhononBand

  def phonon_dos(self):
    # The phonon density of states (DOS).
    py4vasp.data.PhononDos

  def piezoelectric_tensor(self):
    # The piezoelectric tensor (second derivatives w.r.t. strain and field)
    py4vasp.data.PiezoelectricTensor

  def polarization(self):
    # The static polarization of the structure obtained from linear response.
    py4vasp.data.Polarization

  def projector(self):
    # The projectors used for atom and orbital resolved quantities.
    py4vasp.data.Projector

  def stress(self):
    # The stress acting on the unit cell for selected steps of the simulation.
    py4vasp.data.Stress

  def structure(self):
    # The structure of the crystal for selected steps of the simulation.
    py4vasp.data.Structure
    # mycalc = py4vasp.Calculation.from_path("./e01_solid-cd-Si")
    # mycalc.structure[:].plot()
    structure = py4vasp.data.Structure.from_path('Si64')
    structure[:].plot()

  def system(self):
    # Extract the system tag from the INCAR file.
    py4vasp.data.System

  def topology(self):
    # This class accesses the topology of the crystal.
    py4vasp.data.Topology

  def velocity(self):
    # The ion velocities for all steps of the calculation.
    py4vasp.data.Velocity


class Py4vaspLearn(metaclass=functoolsLearn.AutoDecorateMeta):
  def __init__(self) -> None:
    """
    https://www.vasp.at/py4vasp/latest/
    从官网学习
    - 不清楚某个函数或方法的用法时: help(py4vasp.calculation.dos.read)
    """
    import py4vasp.calculation._projector
    self.selection_examples = py4vasp.calculation._projector.selection_examples
    self.Py4vaspData = Py4vaspData()
    pass

  def install(self):
    """
    - pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ py4vasp
    - conda install py4vasp 
    """
    pass

  def usage(self,):
    """
    # 过去记录的
    # 可以用于加标签 和将两幅图加起来
    py4vasp.data.Dos.from_path('bulk_Si/dos').plot().label('Si') + \
        py4vasp.data.Dos.from_path('CO/pdos/').plot().label('CO')

    # 查看参数的用法
    # selection 的用法
    # import py4vasp._data.projector
    print(py4vasp._data.projector.selection_doc)
    calc = py4vasp.Calculation.from_path('CO')
    print(py4vasp._data.projector.selection_examples(
        instance_name=calc, function_name=calc.dos))

    # 不推荐 没有提示啊
    calc = py4vasp.Calculation.from_path('CO')
    dos = calc.dos.read('C(s)')
    dos = calc.dos.read('C(s,px)')
    dos = calc.dos.read(selection='s,p')
    calc.dos.plot(selection='O(up)')
    calc.dos.plot(selection='down(O)')
    pass
    """
    import py4vasp.calculation._dos
    # example 1
    calc = py4vasp.Calculation.from_path(
        '/Users/wangjinlong/my_linux/soft_learn/vasp_learn/tmp/CO')
    dos: py4vasp.calculation._dos.Dos = calc.dos
    dos.plot(selection='O(px)')

    # example 2
    calc = py4vasp.Calculation.from_path(
        path_name='/Users/wangjinlong/my_server/my/myORR_B/slab/X_graphene/As_DVG/ab_md')
    calc
    enery: py4vasp.calculation ._energy.Energy = calc.energy[:]
    df = enery.to_frame(selection='ETOTAL, TEIN')
    return df

  def get_energy(self, directory,):
    """
    - energy.selections() 可以查看所有可能的 selections 参数
    - 查看用法 help(energy[1:5].read()) 
    - 画图 energy.to_graph(selection='ETOTAL, TEIN')

    Args:
        directory (_type_): _description_

    Returns: energy
        _type_: _description_
    """

    import py4vasp.calculation._energy
    calc = py4vasp.Calculation.from_path(path_name=directory)
    energy: py4vasp.calculation._energy.Energy = calc.energy[:]
    return energy

  def get_sturcture(self, directory='CO'):
    """
    - structure.plot(2)  # 2x2x2 的超胞  # 右键选中多个原子可以查看角度和键长
    - atoms = structure.to_ase()

    Args:
        directory (str, optional): _description_. Defaults to 'CO'.

    Returns:
        _type_: _description_
    """

    import py4vasp.calculation._structure
    calc = py4vasp.Calculation.from_path(path_name=directory)
    structure: py4vasp.calculation._structure.Structure = calc.structure

    return structure

  def density(self):
    """
    # 没有 vaspwave.h5 文件, 无法看图
    Examples
    calc = py4vasp.Calculation.from_path(".")
    Plot an isosurface of the electronic charge density
    calc.density.plot()
    Plot isosurfaces for positive (blue) and negative (red) magnetization
    of a spin-polarized calculation (ISPIN=2)
    calc.density.plot("m")
    Plot the isosurface for the third component of a noncollinear magnetization
    calc.density.plot("m(3)")
    """
    pass

  def get_dos_obj(self,
                  directory='/Users/wangjinlong/my_linux/soft_learn/vasp_learn/tmp/CO',):
    """
    self.selection_examples # 可以查看所有可能的 selections 参数
    - 看图: dos.to_graph(selection=selection).to_plotly()
    - dos.plot(selection=selection)
    - df = dos.to_frame(selection='1(p),2(s)')

    Args:
        directory (str, optional): _description_. Defaults to '/Users/wangjinlong/my_linux/soft_learn/vasp_learn/tmp/CO'.

    Returns: dos 
        _type_: _description_
    """

    import py4vasp.calculation._dos
    from py_package_learn.subprocess_learn import subprocessLearn
    fname_h5 = os.path.join(directory, 'vaspout.h5')
    fname_h5_gz = os.path.join(directory, 'vaspout.h5.gz')
    if os.path.exists(fname_h5):
      pass
    elif os.path.exists(fname_h5_gz):
      subprocessLearn.SubprocessLearn().CLI_popen(
          directory=directory,
          args=['gunzip', '-f', fname_h5_gz]
      )
    else:
      print('没有 vaspout.h5 文件')
      return
    calc = py4vasp.Calculation.from_path(path_name=directory)
    dos: py4vasp.calculation._dos.Dos = calc.dos

    return dos

  def get_df_dos(self,
                 directory,
                 show=False,
                 selection=None,  # 'C(p),O(p)',
                 ):
    """* 注意, 如果selection 中是原子索引 '70,39' 的时候需要 多加1 才可以, selection 中好像是以1开始的
    selection: None表示total dos, or 'p(O)','C(p),O(p)','72(p)', 'total(O)','O(total),P(up),S(down)','O(total),P(total), 'total(P(d)),total(P(p))', '71(s,pd),70(s,p,d)', 'total(71(s,p),70(s,p))'

    Args:
        directory (_type_): _description_
        show (bool, optional): _description_. Defaults to False.
        selection (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    dos = self.get_dos_obj(directory=directory)
    df: pd.DataFrame = dos.to_frame(selection=selection)
    if show:
      fig = dos.to_graph(selection=selection).to_plotly()
    return df

  def plot_df_dos(self, df_dos: pd.DataFrame,
                  name_column_x='energies',
                  name_column_y_list=['O_s', 'O_p'],
                  index_column_y_list=[1, 2],
                  name_line_label_list=['O', 'P'],
                  line_color_list=['black', 'red'],
                  linestyle_list=['-', '-'],
                  save=False,
                  xlim_list=None,
                  ylim_list=None,
                  fname='dos.pdf',
                  alpha=0.7,
                  fig=None,
                  ax=None,
                  legend_loc='best'):
    """selection: None表示total dos, or 'p(O)','C(p),O(p)','1(p)', 'total(O)','O(total),P(up),S(down)','O(total),P(total), total(P(d)),total(P(p))

    """

    fig, ax = matplotlibLearn.Features().TwoDimension.plot_df_dos(
        df_dos=df_dos,
        name_column_x=name_column_x,
        name_column_y_list=name_column_y_list,
        index_column_y_list=index_column_y_list,
        name_line_label_list=name_line_label_list,
        linestyle_list=linestyle_list,
        line_color_list=line_color_list,
        save=save,
        xlim_list=xlim_list,
        ylim_list=ylim_list,
        fname=fname,
        alpha=alpha,
        fig=fig,
        ax=ax,
        legend_loc=legend_loc)

    return fig, ax

  def plot_pdos_wrapper(self, directory,
                        selection=None,
                        xlim_list=[None, None],
                        ylim_list=[None, None],
                        name_column_y_list=None,
                        index_column_y_list=[-2, -1],
                        name_line_label_list=None,
                        line_color_list=None,
                        linestyle_list=None,
                        save=False,
                        fname='dos.pdf',
                        fig=None,
                        ax=None,):
    """selection: None表示total dos, or 'p(O)','C(p),O(p)','72(p)', 'total(O)','O(total),P(up),S(down)','O(total),P(total), total(P(d)),total(P(p))
    """

    df_dos = self.get_df_dos(directory=directory, show=False,
                             selection=selection)
    # 使得自旋向下为负值
    for column in df_dos.columns:
      if 'down' in column:
        df_dos[column] *= -1
    fname = os.path.join(directory, fname)
    fig, ax = matplotlibLearn.Features().TwoDimension.plot_df_dos(
        df_dos=df_dos,
        xlim_list=xlim_list,
        ylim_list=ylim_list,
        name_column_y_list=name_column_y_list,
        index_column_y_list=index_column_y_list,
        name_line_label_list=name_line_label_list,
        line_color_list=line_color_list,
        linestyle_list=linestyle_list,
        save=save,
        fname=fname,
        fig=fig,
        ax=ax)

    return df_dos, fname, fig, ax

  def plot_spin_pdos_example(self,
                             directory='/Users/wangjinlong/my_server/my/myORR_B/slab/Nn_graphene/N4_graphene/single_point',
                             selection='39'):
    df = self.get_df_dos(directory=directory, selection=selection)
    df['diff'] = df[f'C_{selection}_up'] - df[f'C_{selection}_down']
    self.plot_df_dos(df_dos=df, name_column_y_list=['diff'])

  def band_structure_plot(self,
                          directory,
                          fname_fig='band_structure.pdf',):
    band = py4vasp.data.Band.from_path(path=directory)
    fig = band.plot().to_plotly()
    fig.write_image(os.path.join(directory, fname_fig))
    fig.show()
    pass
