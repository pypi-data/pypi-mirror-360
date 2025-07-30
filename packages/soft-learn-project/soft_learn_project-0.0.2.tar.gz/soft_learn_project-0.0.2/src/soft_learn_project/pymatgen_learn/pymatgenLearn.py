from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.core import Structure, Molecule
import pymatgen
import pymatgen.io.vasp
import pymatgen.core
import os
import json


class PymatgenLearn():
  def __init__(self) -> None:
    """https://pymatgen.org/
    https://pymatgen.org/usage.html

    main features:
    1. Highly flexible classes for the representation of Element, Site, Molecule, Structure objects.
    2. Extensive input/output support, including support for VASP, ABINIT, CIF, Gaussian, XYZ, and many other file formats.
    3. Powerful analysis tools, including generation of phase diagrams, Pourbaix diagrams, diffusion analyses, reactions, etc.
    4.Electronic structure analyses, such as density of states and band structure.
    5. Integration with the Materials Project REST API, Crystallography Open Database and other external data sources.

    ---
    mp_mpi
    1. 注册账号: https://next-gen.materialsproject.org/dashboard
    2. 获取秘钥: 为了使用客户端，需要API密钥。这是提供给每个材料项目帐户的唯一密钥。您的API密钥可以在您的个人资料仪表板页面或登录后的主API页面上找到。
    """
    self.my_API_Key = 'aKB0GGIGwkraQwvSLIkYLfvxOMtnjaKQ'
    pass

  def install(self):
    """
    """
    s1 = ['conda install gcc']
    s1.append('conda install -c conda-forge pymatgen')
    s1.append('conda upgrade pymatgen')
    # s2 = ['pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ pymatgen']  # 安装
    # s2.extend('pip install --upgrade pymatgen')  # 升级

    pass

  def env_set(self,
              directory_pmg_potcars='./pmg_vasp_potcars'):
    """ https://pymatgen.org/installation.html#potcar-setup
    * After installation, do 
    pmg config -p <EXTRACTED_VASP_POTCAR> <MY_PSP>
    eg: pmg config -p /Users/wangjinlong/job/soft_learn/vasp_learn/vasp_pot/vasp_pot.54/potpaw_PBE.54 /Users/wangjinlong/job/soft_learn/py_package_learn/pymatgen_learn/pmg_vasp_potcars
    pmg config --add PMG_VASP_PSP_DIR /Users/wangjinlong/job/soft_learn/py_package_learn/pymatgen_learn/pmg_vasp_potcars
    """
    cmd1 = f'pmg config -p /Users/wangjinlong/job/soft_learn/vasp_learn/vasp_pot/vasp_pot.54/potpaw_PBE.54 {directory_pmg_potcars}'
    cmd2 = f'pmg config - p / Users/wangjinlong/job/soft_learn/vasp_learn/vasp_pot/vasp_pot.54/potpaw_LDA.54 {directory_pmg_potcars}'
    # 生成<MY_PSP>目录后，您应该将其添加到Pymatgen配置文件中
    cmd11 = f'pmg config --add PMG_VASP_PSP_DIR {directory_pmg_potcars}'
    # 如果需要，您可以如下指定伪势的默认版本和类型：
    cmd12 = 'pmg config --add PMG_DEFAULT_FUNCTIONAL PBE'
    for cmd in [cmd1, cmd11, cmd12]:  # 手动执行 cmd2,cmd3
      os.system(command=cmd)
    # ---
    # 以上命令合在一起

    # 增加 Materials Project API key
    from pypkg_learn_project import mp_apiLearn
    my_API_Key = mp_apiLearn.MpApiLearn().my_API_Key
    os.system(command=cmd1)
    string2 = f'pmg config - -add PMG_VASP_PSP_DIR {directory_pmg_potcars} PMG_MAPI_KEY {my_API_Key}'
    os.system(command=string2)
    pass

  def basic_useage(self):
    """https://pymatgen.org/usage.html
    以后再学学
    """
    import pymatgen.core as pmg
    # Integrated symmetry analysis tools from spglib

    si = pmg.Element("Si")
    si.atomic_mass  # 28.0855
    print(si.melting_point)
    # 1687.0 K

    comp = pmg.Composition("Fe2O3")
    comp.weight  # 159.6882
    # Note that Composition conveniently allows strings to be treated just like an Element object.
    comp["Fe"]  # 2.0
    comp.get_atomic_fraction("Fe")  # 0.4
    lattice = pmg.Lattice.cubic(4.2)
    structure = pmg.Structure(lattice, ["Cs", "Cl"], [
                              [0, 0, 0], [0.5, 0.5, 0.5]])
    # structure.volume
    # 74.088000000000008
    # structure[0]
    # PeriodicSite: Cs (0.0000, 0.0000, 0.0000) [0.0000, 0.0000, 0.0000]

    # You can create a Structure using spacegroup symmetry as well.
    li2o = pmg.Structure.from_spacegroup(
        "Fm-3m", pmg.Lattice.cubic(3), ["Li",
                                        "O"], [[0.25, 0.25, 0.25], [0, 0, 0]]
    )

    finder = SpacegroupAnalyzer(structure)
    finder.get_space_group_symbol()
    "Pm-3m"

    # Convenient IO to various formats. You can specify various formats.
    # Without a filename, a string is returned. Otherwise,
    # the output is written to the file. If only the filename is provided,
    # the format is intelligently determined from a file.
    structure.to(fmt="poscar")
    structure.to(filename="POSCAR")
    structure.to(filename="CsCl.cif")

    # Reading a structure is similarly easy.
    structure = pmg.Structure.from_str(open("CsCl.cif").read(), fmt="cif")
    structure = pmg.Structure.from_file("CsCl.cif")

    # Reading and writing a molecule from a file. Supports XYZ and
    # Gaussian input and output by default. Support for many other
    # formats via the optional openbabel dependency (if installed).
    methane = pmg.Molecule.from_file("methane.xyz")
    methane.to("methane.gjf")

    # Pythonic API for editing Structures and Molecules (v2.9.1 onwards)
    # Changing the specie of a site.
    structure[1] = "F"
    print(structure)

    # Changes species and coordinates (fractional assumed for structures)
    structure[1] = "Cl", [0.51, 0.51, 0.51]
    print(structure)

    # Replaces all Cs in the structure with K
    structure["Cs"] = "K"
    print(structure)

    # Replaces all K in the structure with K: 0.5, Na: 0.5, i.e.,
    # a disordered structure is created.
    structure["K"] = "K0.5Na0.5"
    print(structure)

    # Because structure is like a list, it supports most list-like methods
    # such as sort, reverse, etc.
    structure.reverse()
    print(structure)

    # Molecules function similarly, but with Site and Cartesian coords.
    # The following changes the C in CH4 to an N and displaces it by 0.01A
    # in the x-direction.
    methane[0] = "N", [0.01, 0, 0]

  def write_and_read(self):
    # 可以把以下的 json 改为可读性更强的yaml 格式
    with open('structure.json', 'w') as file:
      json.dump(structure.as_dict(), file)

    # read
    with open('structure.json') as file:
      dct = json.load(file)
      structure = Structure.from_dict(dct)

  def Creating_Structure_manually(self):
    """这通常是最痛苦的方法。虽然有时是必要的，但它很少是你会使用的方法。下面提供了一个创建基本硅晶体的例子:
    """
    from pymatgen.core import Lattice, Structure, Molecule
    coords = [[0, 0, 0], [0.75, 0.5, 0.75]]
    lattice = Lattice.from_parameters(a=3.84, b=3.84, c=3.84, alpha=120,
                                      beta=90, gamma=60)
    struct = Structure(lattice, ["Si", "Si"], coords)

    coords = [[0.000000, 0.000000, 0.000000],
              [0.000000, 0.000000, 1.089000],
              [1.026719, 0.000000, -0.363000],
              [-0.513360, -0.889165, -0.363000],
              [-0.513360, 0.889165, -0.363000]]
    methane = Molecule(["C", "H", "H", "H", "H"], coords)

  def Reading_writing_Structures_Molecules(self):
    # The format is automatically guessed from the filename.
    # Read a POSCAR and write to a CIF.
    structure = Structure.from_file("POSCAR")
    structure.to(filename="CsCl.cif")

    # Read an xyz file and write to a Gaussian Input file.
    methane = Molecule.from_file("methane.xyz")
    methane.to(filename="methane.gjf")

    # For more fine-grained control over which parsed to use, you can specify specific io packages. For example, to create a Structure from a cif::
    from pymatgen.io.cif import CifParser
    parser = CifParser("mycif.cif")
    structure = parser.get_structures()[0]

    from pymatgen.io.vasp import Poscar
    poscar = Poscar.from_file("POSCAR")
    structure = poscar.structure

    # There are also many typical transforms you can do on Structures. Here are some examples::
    # Make a supercell
    structure.make_supercell([2, 2, 2])

    # Get a primitive version of the Structure
    structure.get_primitive_structure()
    pass

  def neb_calc(self):
    # Interpolate between two structures to get 10 structures (typically for
    # NEB calculations.
    # structure.interpolate(another_structure, nimages=10)
    pass

  def input_outputs(self):
    """pymatgen.io - Managing calculation inputs and outputs
    The :mod:pymatgen.io module contains classes to facilitate writing input files and parsing output files from a variety of computational codes, including VASP, Q-Chem, LAMMPS, CP2K, AbInit, and many more.
    """
    from pymatgen.io.packmol import PackmolBoxGen
    input_gen = PackmolBoxGen(tolerance=3.0)
    packmol_set = input_gen.get_input_set({"name": "water",
                                          "number": 500,
                                           "coords": "/path/to/input/file.xyz"})
    packmol_set.write_input('/path/to/calc/directory')

    from pymatgen.apps.borg.hive import VaspToComputedEntryDrone
    from pymatgen.apps.borg.queen import BorgQueen
    from pymatgen.analysis.reaction_calculator import ComputedReaction

    # These three lines assimilate the data into ComputedEntries.
    drone = VaspToComputedEntryDrone()
    queen = BorgQueen(drone)
    queen.load_data('Li-O_entries.json')
    entries = queen.get_data()

    # Extract the correct entries and compute the reaction.
    rcts = filter(lambda e: e.composition.reduced_formula in [
                  'Li', 'O2'], entries)
    prods = filter(lambda e: e.composition.reduced_formula == 'Li2O', entries)
    rxn = ComputedReaction(rcts, prods)
    # print rxn
    # print rxn.calculated_reaction_energy

    # To obtain information on a material with Materials Project Id “mp-1234”, one can use the following::
    from pymatgen.ext.matproj import MPRester
    with MPRester("USER_API_KEY") as m:
      # Structure for material id
      structure = m.get_structure_by_material_id("mp-1234")

      # Dos for material id
      dos = m.get_dos_by_material_id("mp-1234")

      # Bandstructure for material id
      bandstructure = m.get_bandstructure_by_material_id("mp-1234")
    # The Materials API also allows for query of data by formulas::
    # To get a list of data for all entries having formula Fe2O3
    data = m.get_data("Fe2O3")

    # To get the energies of all entries having formula Fe2O3
    energies = m.get_data("Fe2O3", "energy")

  def my(self):
    import pymatgen.io.vasp
    pymatgen.io.vasp.Vasprun(
        'CO/vasp/vasprun.xml').complete_dos.get_element_spd_dos('C')

  def read_chgcar(self,
                  fname_chg='xxx/single_point/CHG'):
    """pymatgen 方法读取atoms对象所在目录的chgcar

    Args:
        fname_chg (str, optional): _description_. Defaults to 'xxx/single_point/CHG'.

    Returns:
        _type_: _description_
    """

    chgcar = pymatgen.io.vasp.Chgcar.from_file(fname_chg)

    return chgcar

  def get_chg_data(self, chgcar: pymatgen.io.vasp.Chgcar,
                   data_name='diff|total',):
    """chgcar 中包含结构数据和电荷密度, 这里只获取电荷密度data

    Args:
        chgcar (pymatgen.io.vasp.Chgcar): _description_

    Returns:
        _type_: _description_
    """

    chg_data = chgcar.data[data_name]
    return chg_data

  def get_data_from_CHG(self,
                        fname_chg='xxx/single_point/CHG',
                        data_name='diff|total',
                        fname_out='xxx/single_point/diff|total.vasp',):
    """ 
    - 自旋极化（spin polarization）指的是系统中自旋向上（spin-up）和自旋向下（spin-down）电子密度之间的差异。它是一个重要的物理概念，特别是在研究磁性材料和自旋电子学（spintronics）中。自旋极化现象可以在固态物理、量子化学和材料科学等领域中观察到。 在量子力学中，电子自旋是一种内禀的角动量，它可以取两个值：自旋向上（通常表示为 +1/2）和自旋向下（通常表示为 -1/2）。在自旋极化系统中，自旋向上和自旋向下电子的数量不相等，这种不对称性导致了系统的总磁矩。

    Args:
        fname_chg (str, optional): _description_. Defaults to 'xxx/single_point/CHG'.
        data_name (str, optional): _description_. Defaults to 'diff|total'.
        fname_out (str, optional): _description_. Defaults to 'xxx/single_point/diff|total.vasp'.

    Returns:
        _type_: _description_
    """
    # 读取 chgcar
    chgcar = self.read_chgcar(fname_chg=fname_chg)
    structure = chgcar.structure
    data = {'total': chgcar.data[data_name]}
    # 保存 数据
    chgcar_obj = pymatgen.io.vasp.Chgcar(
        structure, data)
    chgcar_obj.write_file(file_name=fname_out)
    print(f'保存在-> {fname_out}\n用vesta画图!')

    return chgcar_obj

  def get_cube_from_CHG(self,
                        fname_chg='xxx/single_point/CHG',
                        data_name='diff|total',
                        fname_cube='xxx/single_point/diff|total.cube',
                        ):
    """获得 total or diff(自旋极化)的 chg.cube 
    """
    # 读取 chgcar
    chgcar = self.read_chgcar(fname_chg=fname_chg)
    structure = chgcar.structure
    data = {'total': chgcar.data[data_name]}
    # 保存 数据
    chgcar_obj = pymatgen.io.vasp.Chgcar(
        structure, data)
    chgcar_obj.to_cube(filename=fname_cube)
    print(f'cube 保存在-> {fname_cube}\n用vesta画图!')

    return chgcar_obj

  def get_cube_from_CHG_wrapper(self,
                                directory_sp='xxx/single_point/',
                                data_name='diff|total',
                                ):
    """data_name = diff 为自旋密度
    # 注意单位是不对的, VEASTA 打开后单位跟 CHG 的数值不一样, 内容是一样的应该是VESTA读取的 .cube 文件时的问题 
    - 自旋极化（spin polarization）指的是系统中自旋向上（spin-up）和自旋向下（spin-down）电子密度之间的差异。它是一个重要的物理概念，特别是在研究磁性材料和自旋电子学（spintronics）中。自旋极化现象可以在固态物理、量子化学和材料科学等领域中观察到。 在量子力学中，电子自旋是一种内禀的角动量，它可以取两个值：自旋向上（通常表示为 +1/2）和自旋向下（通常表示为 -1/2）。在自旋极化系统中，自旋向上和自旋向下电子的数量不相等，这种不对称性导致了系统的总磁矩。

    Args:
        directory_sp (str, optional): _description_. Defaults to 'xxx/single_point/'.
        data_name (str, optional): _description_. Defaults to 'diff|total'.

    Returns:
        _type_: _description_
    """

    fname_chg = os.path.join(directory_sp, 'CHG')
    fname_cube = os.path.join(directory_sp, f'{data_name}.cube')
    chg_obj = self.get_cube_from_CHG(fname_chg=fname_chg,
                                     data_name=data_name,
                                     fname_cube=fname_cube)
    return chg_obj

  def get_aseAtoms2pymagenStructure(self,
                                    atoms,
                                    is_pbc=True,
                                    ):
    """pymatgen 和 ase 是两个常用的材料科学库，通常需要将 ase.Atoms 对象转换为 pymatgen 的结构对象（pymatgen.core.Structure 或 Molecule）来使用 pymatgen 提供的功能。pymatgen 提供了 from_ase 方法来实现这种转换。

    注意事项
    如果 Atoms 对象是周期性的（例如晶体结构），使用 Structure.from_ase() 方法。
    如果 Atoms 对象是非周期性的（例如分子），使用 Molecule.from_ase() 方法。
    无单元格信息： 如果 ase.Atoms 对象没有定义晶胞（cell）信息，直接转换为 Structure 可能会失败。这种情况下，如果是分子，可以用以下代码处理：
    molecule = Molecule.from_ase(atoms)

    # ase.Atoms 
    atoms = ase.Atoms(
        symbols=["O", "H", "H"],
        positions=[[0.0, 0.0, 0.0], [0.0, 0.76, 0.58], [0.0, -0.76, 0.58]],
        cell=[10.0, 10.0, 10.0],  # 周期性边界条件 (PBC) 的单元格大小
        pbc=[True, True, True],    # 设置 PBC
    )
    """

    # 将 ASE 的 Atoms 转换为 pymatgen 的 Structure
    if is_pbc:
      structure = pymatgen.core.Structure.from_ase_atoms(atoms)
    else:
      structure = pymatgen.core.Molecule.from_ase_atoms(atoms)
    return structure

  def get_atoms_conventional_or_primitive(self,
                                          atoms,
                                          cell_name='conventional|primitive',
                                          ):
    structure = self.get_aseAtoms2pymagenStructure(atoms=atoms)
    if cell_name == 'primitive':
      structrue = structure.to_primitive()
    elif cell_name == 'conventional':
      structrue = structure.to_conventional()
    else:
      structrue = structure.to_conventional()
    atoms = structrue.to_ase_atoms()
    return atoms

  def get_mpr(self):
    # 从 Materials Project 获取数据
    import pymatgen.ext.matproj
    with pymatgen.ext.matproj.MPRester(self.my_API_Key) as mpr:
      return mpr

  def search_mp_api_example(self,):
    mpr = self.get_mpr()
    results = mpr.summary.search(material_ids=["mp-48"])
    atoms = results[0]['structure'].to_ase_atoms()
    return atoms
