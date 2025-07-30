import ase.data.colors
import ase.dft.dos
import ase.calculators.vasp
import ase.optimize.minimahopping
import ase.spectrum.band_structure
import ase.calculators.emt
import ase.calculators
import ase.build
import ase.visualize
import ase.constraints
import ase.optimize
import ase.db
import ase.io
import ase
from ase import Atoms
from ase import units
from ase.md.verlet import VelocityVerlet
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.lattice.cubic import FaceCenteredCubic
from ase.optimize import BFGS
from ase.dft.bandgap import bandgap
from ase.db import connect
from ase.constraints import ExpCellFilter
import ase.neb
from ase.build import molecule
from ase.constraints import FixLinearTriatomic
import ase.collections
import ase.data
import ase.eos
import ase.lattice
import ase.units
import numpy as np
import os
import ase.thermochemistry
import ase.phonons
import ase.spectrum.band_structure
from ase.visualize import view


class Learn():
  def __init__(self) -> None:
    pass

  def install_string(self):
    string = r""" * ASE 的安装
    安装: conda install ase
    安装最新版本: pip install --upgrade git+https://gitlab.com/ase/ase.git@master # beta 版本
    """
    print(string)
    return None

  def learn_string(self):
    string = r""" * 学习网址: https://wiki.fysik.dtu.dk/ase/
    查看支持的文件格式
    'ase info --formats'
    查看概述
    'ase --help'
    引用
    url = 'https://iopscience.iop.org/article/10.1088/1361-648X/aa680e'
    cite = r'\cite{larsen2017atomic}'
    """
    string += r"""
    # ASE 
    1. 读写 lammps 中的data 文件 
    2. 快速查看构型
    3. 建模, 产生各种结构文件 
    ---
    import ase
    import ase.io.lammpsdata
    from ase.visualize import view
    import ase.io
    import ase.build
    # 读取 lammps data 
    atoms = ase.io.lammpsdata.read_lammps_data(
        '/Users/wangjinlong/Desktop/lmp_test/1.data')
    # view(atoms)
    # ase.io.write('/Users/wangjinlong/Desktop/lmp_test/POSCAR', images=atoms)
    # 建模型
    atoms = ase.build.molecule('H2O', vacuum=4, pbc=True)
    ase.io.lammpsdata.write_lammps_data(
        '/Users/wangjinlong/Desktop/lmp_test/H2O.data',
        atoms=atoms)
    # --
    atoms = mypaper_SiP_codope.CalculationsVasp.DataBase.get_atoms_list(
        dbname='graphene72atoms'
    )[-1]
    # view(atoms)
    # 掺杂
    for atom in atoms:
      if atom.index == 42:
        atom.symbol = 'B'
        atom.position += [0, 0, 0.5]
    # view(atoms)
    ads = ase.build.molecule('O2')

    ase.build.add_adsorbate(slab=atoms,
                            adsorbate=ads,
                            height=1.5,
                            position=atoms[42].position[:2],
                            mol_index=1)
    view(atoms)
    atoms = ase.build.bulk(name='W', a=3.165, cubic=True)
    atoms = atoms.repeat((3, 3, 3))
    p = atoms[5, 4, 22, 3].get_center_of_mass()

    He = ase.Atom(symbol='He', position=p)
    atoms.append(He)
    view(atoms)

    """
    print(string)
    return None

  def example_string(self):
    string = """ * ASE 模块建立 原子模型
    一个例子:
    atoms = ase.build.molecule('H2O', vacuum=3.0)
    len(set(atoms.numbers))  # number of species

    from ase.visualize import view
    from ase.collections import g2
    print(g2.names)  # These are the molecule names
    atoms = g2['CH3CH2OH']
    # view(atoms)
    view(g2)  # View all 162 systems
    """
    print(string)
    return None

  def visualization(self, slab):
    AseVisualize()
    pass

  def atoms_obj_operation(self,):
    # ASE knows many common molecules, so we did not really need to type in all the molecular coordinates ourselves.
    atoms = ase.build.molecule('H2O', vacuum=3.0)
    len(set(atoms.numbers))  # number of species

    print(ase.collections.g2.names)  # These are the molecule names
    atoms = ase.collections.g2['CH3CH2OH']
    # view(atoms)
    view(ase.collections.g2)  # View all 162 systems

    # see also
    # AseAtoms()

    # 获取元胞
    import pymatgen.core
    # my_struc = Structure.from_file("./e01_solid-cd-Si/Si_mp-149_conventional_standard.cif")
    mystruc = pymatgen.core.Structure.from_file(
        '/Users/wangjinlong/my_linux/soft_learn/vasp_learn/tmp/Si64/POSCAR')
    atoms = mystruc.to_primitive().to_ase_atoms()

  def structure_optimization(self,
                             fname_out='gpaw.txt',
                             fname_traj='opt.traj',
                             fname_log='opt.log'
                             ):
    import gpaw
    # H2O
    # import gpaw.calculator

    atoms = ase.Atoms('HOH',
                      positions=[[0, 0, -1], [0, 1, 0], [0, 0, 1]])
    atoms.center(vacuum=3.0)

    # run
    calc = gpaw.calculator.GPAW(mode='lcao', basis='dzp', txt=fname_out)
    atoms.calc = calc
    opt = ase.optimize.BFGS(atoms, trajectory=fname_traj, logfile=fname_log)
    opt.run(fmax=0.05)

    atoms = ase.io.read(fname_traj)
    print(atoms.get_angle(0, 1, 2))  # 能给出三个原子之间的夹角

    # another example
    # ase_modelues_learn.AseOptimize().H2O()
    pass

  def dos_and_band(self, fname='gpaw.txt',
                   fname_gpw='Ag.gpw',):
    # ASE provides three frameworks for setting up bulk structures:
    # 1. ase.build.bulk(). Knows lattice types and lattice constants for elemental bulk structures and a few compounds, but with limited customization.
    # 单点计算
    import ase.build
    import gpaw.calculator
    import gpaw

    atoms = ase.build.bulk('Ag')
    # Here we have used the setups keyword to specify that we want the 11-electron PAW dataset instead of the default which has 17 electrons, making the calculation faster.
    calc = gpaw.calculator.GPAW(mode=gpaw.PW(350), kpts=[8, 8, 8], txt=fname,
                                setups={'Ag': '11'})
    # (In principle, we should be sure to converge both kpoint sampling and planewave cutoff – I.e., write a loop and try different samplings so we know both are good enough to accurately describe the quantity we want.)
    atoms.calc = calc
    atoms.get_potential_energy()
    calc.write(fname_gpw)  # GPAW’s own format using calc.write('Ag.gpw').
    # DOS
    import matplotlib.pyplot as plt
    from gpaw import GPAW
    from ase.dft.dos import DOS
    import ase.dft.dos
    # Having saved the ground-state, we can reload it for ASE to extract the density of states:
    calc = gpaw.calculator.GPAW(fname_gpw)  # 'bulk.Ag.gpw'

    dos = ase.dft.dos.DOS(calc, npts=800, width=0)
    energies = dos.get_energies()
    weights = dos.get_dos()

    ax = plt.gca()
    ax.plot(energies, weights)
    ax.set_xlabel('Energy [eV]')
    ax.set_ylabel('DOS [1/eV]')
    # plt.savefig('dos.png')
    plt.show()

    # 查看布里渊区
    lat = atoms.cell.get_bravais_lattice()
    print(lat.description())
    lat.plot_bz(show=True)

    # band structure
    calc = gpaw.calculator.GPAW('bulk.Ag.gpw')
    atoms: ase.Atoms = calc.get_atoms()
    path = atoms.cell.bandpath('WLGXWK', density=10)
    path.write('path.json')  # ase reciprocal path.json # 终端查看路径

    calc.set(kpts=path, fixdensity=True, symmetry='off')
    atoms.get_potential_energy()
    bs = calc.band_structure()
    bs.write('bs.json')  # ase band-structure bs.json # 查看能带结构

    import ase.dft.bandgap
    # ase.dft.bandgap.bandgap() # 可以计算材料的带隙
    pass

  def notes(self,):
    # Most ASE calculators can be made to generate a file without triggering a calculation using calc.write_input_file(atoms).

    # calc.write_input_file(atoms)
    pass

  def vibration_mode(self,):
    from soft_learn_project.gpaw_learn import gpawTutorial
    gpawTutorial.AseGpawTutorials()
    # AseGpaw().vibrational_mode()
    pass
    # another example
    from ase import Atoms
    from ase.calculators.emt import EMT
    from ase.optimize import BFGS
    from ase.vibrations import Vibrations
    n2 = Atoms('N2', [(0, 0, 0), (0, 0, 1.1)],
               calculator=EMT())
    BFGS(n2).run(fmax=0.01)
    vib = Vibrations(n2)
    vib.run()
    vib.summary(log='N2_EMT_summary.txt')
    # Zero-point energy: 0.078 eV
    vib.write_mode(-1)  # write last mode to trajectory file

  def infrared_intensities(self):
    """Infrared is an extension of Vibrations, in addition to the vibrational modes, also the infrared intensities of the modes are calculated for an Atoms object.

    https://wiki.fysik.dtu.dk/ase/ase/vibrations/infrared.html
    """
    from ase.io import read
    from ase.calculators.vasp import Vasp
    from ase.vibrations import Infrared
    water = read('water.traj')  # read pre-relaxed structure of water
    calc = Vasp(prec='Accurate',
                ediff=1E-8,
                isym=0,
                idipol=4,       # calculate the total dipole moment
                dipol=water.get_center_of_mass(scaled=True),
                ldipol=True)
    water.calc = calc
    ir = Infrared(water)
    ir.run()
    ir.summary()
    pass

  def a_fig(self):
    # creates: o2pt100.png
    import numpy as np

    from ase.build import add_adsorbate, fcc100
    from ase.io import write

    # the metal slab
    atoms = ase.build.fcc100('Pt', size=[4, 10, 3], vacuum=10)
    transmittances = [0 for a in atoms]
    bonded_atoms = []

    upper_layer_idx = [a.index for a in atoms if a.tag == 1]
    middle = atoms.positions[upper_layer_idx, :2].max(axis=0) / 2

    # the dissociating oxygen... fake some dissociation curve
    gas_dist = 1.1
    max_height = 8.
    min_height = 1.
    max_dist = 6

    # running index for the bonds
    index = len(atoms)

    for i, x in enumerate(np.linspace(0, 1.5, 6)):
      height = (max_height - min_height) * np.exp(-2 * x) + min_height
      d = np.exp(1.5 * x) / np.exp(1.5**2) * max_dist + gas_dist
      pos = middle + [0, d / 2]
      add_adsorbate(atoms, 'O', height=height, position=pos)
      pos = middle - [0, d / 2]
      add_adsorbate(atoms, 'O', height=height, position=pos)
      transmittances += [x / 2] * 2

      # we want bonds for the first two molecules
      if i < 2:
        bonded_atoms.append([len(atoms) - 1, len(atoms) - 2])

    textures = ['ase3' for a in atoms]

    # add some semi-transparent bath (only in x/y direction for this example)
    cell = atoms.cell

    idx = [a.index for a in atoms if a.symbol == 'Pt']

    Nbulk = len(idx)
    multiples = [0, 1, -1]
    for i in multiples:
      for j in multiples:
        if i == j == 0:
          continue
        chunk = atoms[idx]
        chunk.translate(i * cell[0] + j * cell[1])
        atoms += chunk
        transmittances += [0.8] * Nbulk
        textures += ['pale'] * Nbulk

    bbox = [-30, 10, 5, 25]

    renderer = write(filename='o2pt100.png',  # 'o2pt100.pov',
                     images=atoms,
                     rotation='90z,-75x',
                     bbox=bbox,
                     show_unit_cell=0,
                     #  povray_settings=dict(
                     #      pause=False,
                     #      canvas_width=1024,
                     #      bondatoms=bonded_atoms,
                     #      camera_type='perspective',
                     #      transmittances=transmittances,
                     #      textures=textures)
                     )
    # 不能显示
    # renderer.render()


class PhononCalculations():
  def __init__(self):
    pass

  def example(self,):
    """Simple example showing how to calculate the phonon dispersion for bulk aluminum using a 7x7x7 supercell within effective medium theory:

    https://wiki.fysik.dtu.dk/ase/ase/phonons.html
    """

    # Setup crystal and EMT calculator
    atoms = ase.build.bulk('Al', 'fcc', a=4.05)

    # Phonon calculator
    N = 7
    ph = ase.phonons.Phonons(
        atoms, ase.calculators.emt.EMT(), supercell=(N, N, N), delta=0.05)
    ph.run()

    # Read forces and assemble the dynamical matrix
    ph.read(acoustic=True)
    ph.clean()

    path = atoms.cell.bandpath('GXULGK', npoints=100)
    bs = ph.get_band_structure(path)

    dos = ph.get_dos(kpts=(20, 20, 20)).sample_grid(npts=100, width=1e-3)

    # Plot the band structure and DOS:
    import matplotlib.pyplot as plt  # noqa

    fig = plt.figure(1, figsize=(7, 4))
    ax = fig.add_axes([.12, .07, .67, .85])

    emax = 0.035
    bs.plot(ax=ax, emin=0.0, emax=emax)

    dosax = fig.add_axes([.8, .07, .17, .85])
    dosax.fill_between(dos.get_weights(), dos.get_energies(), y2=0, color='grey',
                       edgecolor='k', lw=1)

    dosax.set_ylim(0, emax)
    dosax.set_yticks([])
    dosax.set_xticks([])
    dosax.set_xlabel("DOS", fontsize=18)

    fig.savefig('Al_phonon.png')

    # Mode inspection:
    # from ase.io.trajectory import Trajectory
    # from ase.io import write

    # Write modes for specific q-vector to trajectory files:
    L = path.special_points['L']
    ph.write_modes([l / 2 for l in L], branches=[2], repeat=(8, 8, 8), kT=3e-4,
                   center=True)

    # Generate gif animation:
    # XXX Temporarily disabled due to matplotlib writer compatibility issue.
    # with Trajectory('phonon.mode.2.traj', 'r') as traj:
    #     write('Al_mode.gif', traj, interval=50,
    #           rotation='-36x,26.5y,-25z')
    pass

  def calc(self, atoms: ase.Atoms,
           calc,
           supercell=(1, 1, 1),
           ):
    # Phonon calculator
    ph = ase.phonons.Phonons(atoms=atoms, calc=calc,
                             supercell=supercell, delta=0.05)
    ph.run()
    # Read forces and assemble the dynamical matrix
    ph.read(acoustic=True)
    ph.clean()
    return ph

  def get_bs(self, atoms: ase.Atoms,
             ph: ase.phonons.Phonons,
             bandpath='GXULGK',):
    path = atoms.cell.bandpath(path=bandpath, npoints=100)
    bs = ph.get_band_structure(path)
    return bs

  def get_dos(self,  ph: ase.phonons.Phonons):
    dos = ph.get_dos(kpts=(20, 20, 20)).sample_grid(npts=100, width=1e-3)
    return dos

  def plot(self,
           bs: ase.spectrum.band_structure.BandStructure,
           dos: ase.dft.dos.DOS):
    # Plot the band structure and DOS:
    import matplotlib.pyplot as plt  # noqa

    fig = plt.figure(1, figsize=(7, 4))
    ax = fig.add_axes([.12, .07, .67, .85])

    emax = 0.035
    bs.plot(ax=ax, emin=0.0, emax=emax)

    dosax = fig.add_axes([.8, .07, .17, .85])
    dosax.fill_between(dos.get_weights(), dos.get_energies(), y2=0, color='grey',
                       edgecolor='k', lw=1)

    dosax.set_ylim(0, emax)
    dosax.set_yticks([])
    dosax.set_xticks([])
    dosax.set_xlabel("DOS", fontsize=18)

    fig.savefig('Al_phonon.png')
    pass

  def write_modes(self, path, ph,):
    # Mode inspection:
    # from ase.io.trajectory import Trajectory
    # from ase.io import write

    # Write modes for specific q-vector to trajectory files:
    L = path.special_points['L']
    ph.write_modes([l / 2 for l in L], branches=[2], repeat=(8, 8, 8), kT=3e-4,
                   center=True)

    # Generate gif animation:
    # XXX Temporarily disabled due to matplotlib writer compatibility issue.
    # with Trajectory('phonon.mode.2.traj', 'r') as traj:
    #     write('Al_mode.gif', traj, interval=50,
    #           rotation='-36x,26.5y,-25z')
    pass


class AseGettingStarted():
  """Getting Started
  """

  def __init__(self) -> None:
    pass

  def N2Cu(self,):
    """Nitrogen on copper
    """
    # N2Cu 的吸附能

    h = 1.85
    d = 1.10
    # 定义 crystal 对象
    slab: ase.Atoms = ase.build.fcc111('Cu', size=(4, 4, 2), vacuum=10.0)

    # use the effective medium theory (EMT) calculator,
    slab.calc = ase.calculators.emt.EMT()
    e_slab = slab.get_potential_energy()

    # 定义分子对象
    molecule = ase.Atoms('2N', positions=[(0., 0., 0.), (0., 0., d)])
    molecule.calc = ase.calculators.emt.EMT()
    e_N2 = molecule.get_potential_energy()

    # Structure relaxation
    # let us keep the Cu atoms fixed in the slab by using FixAtoms from the constraints module. Only the N2 molecule is then allowed to relax to the equilibrium structure:
    ase.build.add_adsorbate(slab, molecule, h, 'ontop')
    constraint = ase.constraints.FixAtoms(mask=[a.symbol != 'N' for a in slab])
    slab.set_constraint(constraint)
    # Now attach the QuasiNewton minimizer to the system and save the trajectory file. Run the minimizer with the convergence criteria that the force on all atoms should be less than some fmax:
    dyn = ase.optimize.QuasiNewton(slab, trajectory='N2Cu.traj')
    dyn.run(fmax=0.05)

    print('Adsorption energy:', e_slab + e_N2 - slab.get_potential_energy())

    # Input-output
    ase.io.write('slab.xyz', slab)
    slab_from_file = ase.io.read('slab.xyz')
    pass

  def Atoms_and_calculators(self):
    #  计算 N2的总能
    from gpaw import GPAW
    from ase import Atoms
    from ase.io import Trajectory

    atoms = Atoms('N2', positions=[[0, 0, -1], [0, 0, 1]])
    atoms.center(vacuum=3.0)

    calc = GPAW(mode='lcao', basis='dzp', txt='gpaw.txt')
    atoms.calc = calc

    traj = Trajectory('binding_curve.traj', 'w')

    step = 0.05
    nsteps = int(3 / step)

    for i in range(nsteps):
      d = 0.5 + i * step
      atoms.positions[1, 2] = atoms.positions[0, 2] + d
      atoms.center(vacuum=3.0)
      e = atoms.get_potential_energy()
      f = atoms.get_forces()
      print('distance, energy', d, e)
      print('force', f)
      traj.write(atoms)

    # 画结合能曲线
    import matplotlib.pyplot as plt
    from ase.io import iread
    energies = []
    distances = []
    for atoms in iread('binding_curve.traj'):
      energies.append(atoms.get_potential_energy())
      distances.append(atoms.positions[1, 2] - atoms.positions[0, 2])
    ax = plt.gca()
    ax.plot(distances, energies)
    ax.set_xlabel('Distance [Å]')
    ax.set_ylabel('Total energy [eV]')
    plt.show()

    # 计算 N 原子能量
    atoms = Atoms('N')
    atoms.center(vacuum=3.0)
    atoms.set_initial_magnetic_moments([3])

    calc = GPAW(mode='lcao', basis='dzp')
    atoms.calc = calc
    atoms.get_potential_energy()
    pass

  def Manipulating_atoms(self):
    def AgOnNi_slab():
      # Ag adatom on Ni slab
      from math import sqrt
      from ase import Atoms
      a = 3.55
      atoms = Atoms('Ni4',
                    cell=[sqrt(2) * a, sqrt(2) * a, 1.0, 90, 90, 120],
                    pbc=(1, 1, 0),
                    scaled_positions=[(0, 0, 0),
                                      (0.5, 0, 0),
                                      (0, 0.5, 0),
                                      (0.5, 0.5, 0)])
      atoms.center(vacuum=5.0, axis=2)

      # Have a look at the cell and positions of the atoms:
      """
      print(atoms.cell) 
      print(atoms.positions)
      print(atoms[0])
      """

      # Write the structure to a file and plot the whole system by bringing up the ase.gui:
      from ase.visualize import view
      atoms.write('slab.xyz')
      view(atoms)

      # We now add an adatom in a three-fold site at a height of h=1.9 Å:
      h = 1.9
      relative = (1 / 6, 1 / 6, 0.5)
      absolute = np.dot(relative, atoms.cell) + (0, 0, h)
      atoms.append('Ag')
      atoms.positions[-1] = absolute
      return atoms

    def interface_building():
      # 1. get_water_layer
      import numpy as np
      from ase import Atoms

      p = np.array(
          [[0.27802511, -0.07732213, 13.46649107],
           [0.91833251, -1.02565868, 13.41456626],
           [0.91865997, 0.87076761, 13.41228287],
           [1.85572027, 2.37336781, 13.56440907],
           [3.13987926, 2.3633134, 13.4327577],
           [1.77566079, 2.37150862, 14.66528237],
           [4.52240322, 2.35264513, 13.37435864],
           [5.16892729, 1.40357034, 13.42661052],
           [5.15567324, 3.30068395, 13.4305779],
           [6.10183518, -0.0738656, 13.27945071],
           [7.3856151, -0.07438536, 13.40814585],
           [6.01881192, -0.08627583, 12.1789428]])
      c = np.array([[8.490373, 0., 0.],
                    [0., 4.901919, 0.],
                    [0., 0., 26.93236]])
      W = Atoms('4(OH2)', positions=p, cell=c, pbc=[1, 1, 0])
      W.write('WL.traj')

      # 从文件获取 W 对象
      W = ase.io.read('WL.traj')

      # We will need a Ni(111) slab which matches the water as closely as possible. A 2x4 orthogonal fcc111 supercell should be good enough.
      slab = ase.build.fcc111('Ni', size=[2, 4, 3], a=3.55, orthogonal=True)

      # Looking at the two unit cells, we can see that they match with around 2 percent difference, if we rotate one of the cells 90 degrees in the plane. Let’s rotate the cell:
      print(W.cell)
      print(slab.cell)

      W.rotate(90, 'z', center=(0, 0, 0))  # 旋转 W
      # Now we can wrap the atoms into the cell
      # The wrap() method only works if periodic boundary conditions are enabled.
      W.wrap()

      # scale the water in the plane to match the cell of the slab.
      W.set_cell(slab.cell, scale_atoms=True)
      zmin = W.positions[:, 2].min()
      zmax = slab.positions[:, 2].max()
      W.positions += (0, 0, zmax - zmin + 1.5)

      # Finally we use extend to copy the water onto the slab:
      # Adding two atoms objects will take the positions from both and the cell and boundary conditions from the first.
      interface = slab + W
      interface.center(vacuum=6, axis=2)
      interface.write('NiH2O.traj')
      return interface

  def structure_optimization(self):
    """Let’s calculate the structure of the H2O molecule.
    """
    from gpaw import GPAW
    from ase import Atoms
    from ase.optimize import BFGS

    atoms = Atoms('HOH',
                  positions=[[0, 0, -1], [0, 1, 0], [0, 0, 1]])
    atoms.center(vacuum=3.0)

    calc = GPAW(mode='lcao', basis='dzp', txt='gpaw.txt')
    atoms.calc = calc

    opt = BFGS(atoms, trajectory='opt.traj')
    opt.run(fmax=0.05)
    pass

  def crystals_and_band_structure(self):
    AseGettingStarted_crystals_and_band_structure()
    pass

  def nanoparticle(self,):
    # Optimise cuboctahedron:
    from ase.calculators.emt import EMT
    from ase.cluster import Octahedron
    from ase.optimize import BFGS
    # 1. 建立
    atoms = Octahedron('Ag', 5, cutoff=2)

    # 2. 优化
    atoms.calc = EMT()
    opt = BFGS(atoms, trajectory='opt.traj')
    opt.run(fmax=0.01)
    # ase gui groundstate.gpw  # 看图
    # ase gui opt.traj

    # 3. Calculate ground state:
    from gpaw import GPAW, FermiDirac
    from ase.io import read

    # As usual, we set a few parameters to save time since this is not a real production calculation. We want a smaller basis set and also a PAW dataset with fewer electrons than normal. We also want to use Fermi smearing since there could be multiple electronic states near the Fermi level:
    # These are GPAW-specific keywords — with another code, those variables would have other names.
    atoms = read('opt.traj')
    calc = GPAW(mode='lcao', basis='sz(dzp)', txt='gpaw.txt',
                occupations=FermiDirac(0.1),
                setups={'Ag': '11'})
    atoms.calc = calc
    atoms.center(vacuum=4.0)
    atoms.get_potential_energy()  # 相当于单点计算
    atoms.calc.write('groundstate.gpw')  # 写入计算结果

    # 4. Plot DOS:
    import matplotlib.pyplot as plt
    from gpaw import GPAW

    from ase.dft.dos import DOS
    # Once we have saved the .gpw file, we can write a new script which loads it and gets the DOS:
    calc = GPAW('groundstate.gpw')  # 可以从保存的 groundstate.gpw 读取

    # In this example, we sample the DOS using Gaussians of width 0.1 eV. You will want to mark the Fermi level in the plot. A good way is to draw a vertical line: plt.axvline(efermi).
    dos = DOS(calc, npts=800, width=0.1)
    energies = dos.get_energies()
    weights = dos.get_dos()
    efermi = calc.get_fermi_level()

    ax = plt.gca()
    ax.plot(energies, weights)
    ax.set_xlabel(r'$E - E_{\mathrm{Fermi}}$ [eV]')
    ax.set_ylabel('DOS [1/eV]')
    ax.axvline(efermi)
    plt.savefig('dos.png')
    plt.show()
    pass


class AseGettingStarted_crystals_and_band_structure():
  def __init__(self) -> None:
    pass

  def setting_up_bulk_structures(self):
    # ASE provides three frameworks for setting up bulk structures:
    # 1. ase.build.bulk(). Knows lattice types and lattice constants for elemental bulk structures and a few compounds, but with limited customization.
    import ase.build
    atoms = ase.build.bulk('Ag')

    # 2. ase.spacegroup.crystal(). Creates atoms from typical crystallographic information such as spacegroup, lattice parameters, and basis.
    import ase.spacegroup
    a = 4.6
    c = 2.95
    # Rutile TiO2:
    atoms = ase.spacegroup.crystal(['Ti', 'O'], basis=[(0, 0, 0), (0.3, 0.3, 0.0)],
                                   spacegroup=136, cellpar=[a, a, c, 90, 90, 90])
    ase.io.write('rutile.traj', atoms)

    # 3. ase.lattice. Creates atoms explicitly from lattice and basis.
    pass

  def bulk_calculation(self):
    import gpaw.calculator
    import gpaw.wavefunctions.pw

    atoms = ase.build.bulk('Ag')
    calc = gpaw.calculator.GPAW(
        mode=gpaw.wavefunctions.pw.PW(350),
        kpts=[8, 8, 8],
        txt='gpaw.bulk.Ag.txt',
        setups={'Ag': '11'})
    atoms.calc = calc
    atoms.get_potential_energy()
    calc.write('bulk.Ag.gpw')

    pass

  def density_of_states(self,):
    """ 思路
    import matplotlib.pyplot as plt
    from ase.dft.dos import DOS
    from gpaw import GPAW

    calc = GPAW('groundstate.gpw')
    dos = DOS(calc, npts=500, width=0)
    energies = dos.get_energies()
    weights = dos.get_dos()
    plt.plot(energies, weights)
    plt.show()
    """
    # Ag dos
    import matplotlib.pyplot as plt
    from gpaw import GPAW
    from ase.dft.dos import DOS

    calc = GPAW('bulk.Ag.gpw')
    dos = DOS(calc, npts=800, width=0)
    energies = dos.get_energies()
    weights = dos.get_dos()

    ax = plt.gca()
    ax.plot(energies, weights)
    ax.set_xlabel('Energy [eV]')
    ax.set_ylabel('DOS [1/eV]')
    plt.savefig('dos.png')
    plt.show()

  def band_structure(self):
    """ 思路
    calc = GPAW('groundstate.gpw')
    atoms = calc.get_atoms()
    path = atoms.cell.bandpath(<...>)
    calc.set(kpts=path, symmetry='off', fixdensity=True)

    atoms.get_potential_energy()
    bs = calc.band_structure()
    bs.write('bs.json')
    """
    # 例子 Ag band structure:
    from gpaw import GPAW
    calc = GPAW('bulk.Ag.gpw')
    atoms = calc.get_atoms()
    path = atoms.cell.bandpath('WLGXWK', density=10)
    path.write('path.json')

    calc.set(kpts=path, fixdensity=True, symmetry='off')
    # Then we trigger a new calculation, which will be non-selfconsistent, and extract and save the band structure:
    atoms.get_potential_energy()
    bs = calc.band_structure()
    bs.write('bs.json')

    # 例子2 Rutile band structure:
    from gpaw import GPAW
    calc = GPAW('groundstate.rutile.gpw')
    atoms = calc.get_atoms()
    path = atoms.cell.bandpath(density=7)
    path.write('path.rutile.json')

    calc.set(kpts=path, fixdensity=True,
             symmetry='off')

    atoms.get_potential_energy()
    bs = calc.band_structure()
    bs.write('bs.rutile.json')
    pass

  def equation_of_state(self):
    #
    # aseTutorials.AseTutorials().equation_of_state()
    pass

  def Complex_crystals_and_cell_optimisation(self):
    """复杂晶体的结构优化
    思路:
    The ase.constraints.ExpCellFilter allows us to optimise cell and positions simultaneously. It does this by exposing the degrees of freedom to the optimiser as if they were additional positions — hence acting as a kind of filter. We use it by wrapping it around the atoms:

    from ase.optimize import BFGS
    from ase.constraints import ExpCellFilter
    opt = BFGS(ExpCellFilter(atoms), ...)
    opt.run(fmax=0.05)
    """
    # 例子
    from gpaw import GPAW, PW
    from ase.constraints import ExpCellFilter
    from ase.io import write
    from ase.optimize import BFGS
    from ase.spacegroup import crystal
    import ase.spacegroup
    a = 4.6
    c = 2.95

    # Rutile TiO2:
    atoms = ase.spacegroup.crystal(['Ti', 'O'], basis=[(0, 0, 0), (0.3, 0.3, 0.0)],
                                   spacegroup=136, cellpar=[a, a, c, 90, 90, 90])
    write('rutile.traj', atoms)

    calc = GPAW(mode=PW(800), kpts=[2, 2, 3],
                txt='gpaw.rutile.txt')
    atoms.calc = calc

    opt = BFGS(ExpCellFilter(atoms), trajectory='opt.rutile.traj')
    opt.run(fmax=0.05)

    calc.write('groundstate.rutile.gpw')

    print('Final lattice:')
    print(atoms.cell.get_bravais_lattice())
    pass


#  Tutorials
class Tutorial_Basic_property_calculations():
  def __init__(self) -> None:
    pass

  def atomization_energy(self,):
    # The following script will calculate the atomization energy of a nitrogen molecule:
    # First, an Atoms object containing one nitrogen is created and a fast EMT calculator is attached to it simply as an argument. The total energy for the isolated atom is then calculated and stored in the e_atom variable.
    atom = ase.Atoms('N')
    atom.calc = ase.calculators.emt.EMT()
    e_atom = atom.get_potential_energy()

    d = 1.1
    molecule = ase.Atoms('2N', [(0., 0., 0.), (0., 0., d)])
    molecule.calc = ase.calculators.emt.EMT()
    e_molecule = molecule.get_potential_energy()

    e_atomization = e_molecule - 2 * e_atom

    print('Nitrogen atom energy: %5.2f eV' % e_atom)
    print('Nitrogen molecule energy: %5.2f eV' % e_molecule)
    print('Atomization energy: %5.2f eV' % -e_atomization)

  def equation_of_state(self,):  # EOS
    # First, do a bulk calculation for different lattice constants:
    import numpy as np
    from ase import Atoms
    from ase.calculators.emt import EMT
    from ase.io.trajectory import Trajectory

    a = 4.0  # approximate lattice constant
    b = a / 2
    ag = Atoms('Ag',
               cell=[(0, b, b), (b, 0, b), (b, b, 0)],
               pbc=1,
               calculator=EMT())  # use EMT potential
    cell = ag.get_cell()
    traj = Trajectory('Ag.traj', 'w')
    for x in np.linspace(0.95, 1.05, 5):
      ag.set_cell(cell * x, scale_atoms=True)
      ag.get_potential_energy()
      traj.write(ag)

    # This will write a trajectory file containing five configurations of FCC silver for five different lattice constants. Now, analyse the result with the EquationOfState class and this script:

    configs = ase.io.read('Ag.traj@0:5')  # read 5 configurations
    # Extract volumes and energies:
    volumes = [ag.get_volume() for ag in configs]
    energies = [ag.get_potential_energy() for ag in configs]
    eos = ase.eos.EquationOfState(volumes, energies)
    v0, e0, B = eos.fit()
    print(B / ase.units.kJ * 1.0e24, 'GPa')
    eos.plot('Ag-eos.png')

    # $ ase gui Ag.traj # 也可以这样分析

  def finding_lattice_constants(self, method='eos_hcp'):
    """using EOS or the stress tensor
    """
    def eos_bcc_fcc():
      """对于bcc 和 fcc 非常简单

      Returns:
          _type_: _description_
      """
      import ase.build
      import ase.calculators
      import ase.calculators.emt
      import ase.eos
      atoms = ase.build.bulk('Cu', 'fcc', a=3.6)
      atoms.calc = ase.calculators.emt.EMT()
      eos = ase.eos.calculate_eos(atoms=atoms, trajectory='Cu.traj', npoints=9)
      volume, energy, bulk_modulus = eos.fit()
      lc = (4 * volume)**(1 / 3.0)
      # 看图
      # eos.plot()
      atoms = ase.build.bulk('Cu', 'fcc', a=lc)
      return atoms

    def eos_hcp():
      # Let’s try to find the and lattice constants for HCP nickel using the EMT potential.
      # First, we make a good initial guess for and using the FCC nearest neighbor distance and the ideal ratio:
      a0 = 3.52 / np.sqrt(2)
      c0 = np.sqrt(8 / 3.0) * a0

      # and create a trajectory for the results:
      traj = ase.io.Trajectory('Ni.traj', 'w')

      # Finally, we do the 9 calculations (three values for a and three for c):

      eps = 0.01
      for a in a0 * np.linspace(1 - eps, 1 + eps, 3):
        for c in c0 * np.linspace(1 - eps, 1 + eps, 3):
          ni = ase.build.bulk('Ni', 'hcp', a=a, c=c)
          ni.calc = ase.calculators.emt.EMT()
          ni.get_potential_energy()
          traj.write(ni)

      # Analysis Now, we need to extract the data from the trajectory. Try this:
      configs = ase.io.read('Ni.traj@:')
      energies = [config.get_potential_energy() for config in configs]
      a = np.array([config.cell[0, 0] for config in configs])
      c = np.array([config.cell[2, 2] for config in configs])

      # We fit the energy to this expression: https://wiki.fysik.dtu.dk/ase/tutorials/lattice_constant.html
      # The best fit is found like this:
      functions = np.array([a**0, a, c, a**2, a * c, c**2])
      p = np.linalg.lstsq(functions.T, energies, rcond=-1)[0]

      # and we can find the minimum like this:
      p0 = p[0]
      p1 = p[1:3]
      p2 = np.array([(2 * p[3], p[4]),
                    (p[4], 2 * p[5])])
      a0, c0 = np.linalg.solve(p2.T, -p1)

      with open('lattice_constant.csv', 'w') as fd:
        fd.write(f'{a0:.3f}, {c0:.3f}\n')

      atoms = ase.build.bulk('Ni', 'hcp', a=a0, c=c0)
      return atoms

    def tensor():
      """One can also use the stress tensor to optimize the unit cell. For this we cannot use the EMT calculator.:
      """
      from gpaw import GPAW, PW
      a0 = 2.46
      c0 = 4.02
      ni = ase.build.bulk('Ni', 'hcp', a=a0, c=c0)
      calc = GPAW(mode=PW(200), xc='LDA', txt='Ni.out')
      ni.calc = calc
      sf = ase.constraints.StrainFilter(ni)
      opt = ase.optimize.BFGS(sf)
      # If you want the optimization path in a trajectory, add these lines before calling the run() method:
      traj = ase.io.Trajectory('path.traj', 'w', ni)
      opt.attach(traj)

      opt.run(0.005)
      return ni

    if method == 'eos_bcc_fcc':
      atoms = eos_bcc_fcc()
    elif method == "eos_hcp":
      atoms = eos_hcp()
    elif method == 'tensor':
      atoms = tensor()
    return atoms


class Tutorial_Surface_adsorption():
  def __init__(self) -> None:
    pass

  def surface_adsorption(self,):
    # Surface adsorption study using the ASE database¶
    # In this tutorial we will adsorb C, N and O on 7 different FCC(111) surfaces with 1, 2 and 3 layers and we will use database files to store the results.

    # 1. bulk, we calculate the equilibrium bulk FCC lattice constants for the seven elements where the EMT potential works well:
    # from ase.calculators.emt import EMT

    db = ase.db.connect('bulk.db')  # we connect() to the database:
    for symb in ['Al', 'Ni', 'Cu', 'Pd', 'Ag', 'Pt', 'Au']:
      atoms = ase.build.bulk(symb, 'fcc')
      atoms.calc = ase.calculators.emt.EMT()
      eos = ase.eos.calculate_eos(atoms)
      v, e, B = eos.fit()  # find minimum
      # Do one more calculation at the minimu and write to database:
      atoms.cell *= (v / atoms.get_volume())**(1 / 3)
      atoms.get_potential_energy()
      db.write(atoms, bm=B)
    # ase db bulk.db -c +bm # 用于查看数据库

    # 2. Adsorbates, Now we do the adsorption calculations (run the ads.py script).
    from ase.calculators.emt import EMT
    from ase.constraints import FixAtoms
    from ase.optimize import BFGS

    db1 = ase.db.connect('bulk.db')
    db2 = ase.db.connect('ads.db')

    def run(symb, a, n, ads):
      atoms = ase.build.fcc111(symb, (1, 1, n), a=a)
      ase.build.add_adsorbate(atoms, ads, height=1.0, position='fcc')

      # Constrain all atoms except the adsorbate:
      fixed = list(range(len(atoms) - 1))
      atoms.constraints = [FixAtoms(indices=fixed)]

      atoms.calc = ase.calculators.emt.EMT()
      opt = BFGS(atoms, logfile=None)
      opt.run(fmax=0.01)
      return atoms

    # The reserve() method will check if there is a row with the keys layers=n, surf=symb and ads=ads. If there is, then the calculation will be skipped. If there is not, then an empty row with those keys-values will be written and the calculation will start. When done, the real row will be written and the empty one will be removed. This modified script can run in several jobs all running in parallel and no calculation will be done twice.
    for row in db1.select():
      # row.cell 元胞 row.cell[:] 元胞基矢数组  row.cell[0, :] 元胞x基矢数组,
      a = row.cell[0, 1] * 2
      symb = row.symbols[0]
      for n in [1, 2, 3]:
        for ads in 'CNO':
          id = db2.reserve(layers=n, surf=symb, ads=ads)
          if id is not None:
            atoms = run(symb, a, n, ads)
            db2.write(atoms, id=id, layers=n, surf=symb,
                      ads=ads)  # 这里写上id=id, 下面就不用删除了
            # del db2[id]
    pass

    # 3. Reference energies, Let’s also calculate the energy of the clean surfaces and the isolated adsorbates (refs.py):

    db1 = ase.db.connect('bulk.db')
    db2 = ase.db.connect('refs.db')

    def run(symb, a, n):
      atoms = ase.build.fcc111(symb, (1, 1, n), a=a)
      atoms.calc = ase.calculators.emt.EMT()
      atoms.get_forces()
      return atoms

    # Clean slabs:
    for row in db1.select():
      a = row.cell[0, 1] * 2
      symb = row.symbols[0]
      for n in [1, 2, 3]:
        id = db2.reserve(layers=n, surf=symb, ads='clean')
        if id is not None:
          atoms = run(symb, a, n)
          db2.write(atoms, id=id, layers=n, surf=symb, ads='clean')

    # Atoms:
    for ads in 'CNO':
      a = Atoms(ads)
      a.calc = EMT()
      a.get_potential_energy()
      db2.write(a)

    # 4. Analysis, Now we have what we need to calculate the adsorption energies and heights (ea.py):

    refs = ase.db.connect('refs.db')
    db = ase.db.connect('ads.db')

    for row in db.select():
      ea = (row.energy -
            refs.get(formula=row.ads).energy -
            refs.get(layers=row.layers, surf=row.surf).energy)
      h = row.positions[-1, 2] - row.positions[-2, 2]
      db.update(row.id, height=h, ea=ea)
    pass


class Tutorial_Global_optimization():
  def __init__(self) -> None:
    pass

  def constrained_minima_hopping(self,):
    """ one of global optimization
    """
    # Constrained minima hopping
    # Make the Pt 110 slab.
    atoms: ase.Atoms = ase.build.fcc110('Pt', (2, 2, 2), vacuum=7.)

    # Add the Cu2 adsorbate.
    adsorbate = ase.Atoms([ase.Atom('Cu', atoms[7].position + (0., 0., 2.5)),
                           ase.Atom('Cu', atoms[7].position + (0., 0., 5.0))])
    atoms.extend(adsorbate)

    # Constrain the surface to be fixed and a Hookean constraint between
    # the adsorbate atoms.
    constraints = [ase.constraints.FixAtoms(indices=[atom.index for atom in atoms if
                                                     atom.symbol == 'Pt']),
                   ase.constraints.Hookean(a1=8, a2=9, rt=2.6, k=15.),
                   ase.constraints.Hookean(a1=8, a2=(0., 0., 1., -15.), k=15.), ]
    atoms.set_constraint(constraints)

    # Set the calculator.
    calc = ase.calculators.emt.EMT()
    atoms.calc = calc

    # Instantiate and run the minima hopping algorithm.
    hop = ase.optimize.minimahopping.MinimaHopping(atoms,
                                                   Ediff0=2.5,
                                                   T0=4000.,
                                                   logfile='hop.log',
                                                   minima_traj='minima.traj',
                                                   )
    hop(totalsteps=10)

    # This script will produce 10 molecular dynamics and 11 optimization files. It will also produce a file called ‘minima.traj’ which contains all of the accepted minima. You can look at the progress of the algorithm in the file hop.log in combination with the trajectory files.

    # Alternatively, there is a utility to allow you to visualize the progress of the algorithm. You can run this from within the same directory as your algorithm as:
    from ase.optimize.minimahopping import MHPlot

    mhplot = MHPlot()
    mhplot.save_figure('summary.png')

  def Optimization_with_Genetic_Algorithm(self):
    ga = AseTutorials_OptimizationGeneticAlgorithm()
    ga.initialisations()
    ga.run()
    pass

  def Genetic_algorithm_Search_for_stable_FCC_alloys(self):
    ga_instande = AseTutorials_GeneticAlgorithmSearch()
    ga_instande.get_refers_db()
    ga_instande.initial_population()
    ga_instande.main()
    pass

  def Determination_of_convex_hull_with_a_genetic_algorithm(self):
    """https://wiki.fysik.dtu.dk/ase/tutorials/ga/ga_convex_hull.html
    """
    pass

  def Genetic_algorithm_search_for_bulk_crystal_structures(self):
    """https://wiki.fysik.dtu.dk/ase/tutorials/ga/ga_bulk.html
    """
    pass

  def Genetic_algorithm_search_for_molecular_crystal_structures(self):
    """https://wiki.fysik.dtu.dk/ase/tutorials/ga/ga_molecular_crystal.html
    """
    pass


class TutorialCalculating_diffusion_dissociation_properties():
  def __init__(self) -> None:
    r"""https://wiki.fysik.dtu.dk/ase/tutorials/tutorials.html#calculating-diffusion-dissociation-properties
    https://wiki.fysik.dtu.dk/ase/ase/neb.html#module-ase.mep.neb
    references: \cite{henkelman2000improved, henkelman2000climbing, smidstrup2014improved, lindgren2019scaled}
    # 已经转移到 aseLearn NEB 类中
    """

    pass


class ASE_database():
  def __init__(self) -> None:
    """https://wiki.fysik.dtu.dk/ase/tutorials/tut06_database/database.html
    """
    pass

  def opening_a_database_in_Python(self):
    from ase.db import connect
    db = connect('database.db')
    for row in db.select():
      atoms = row.toatoms()
      print(atoms)

    row = db.select(id=1)[0]
    dir(row)  # will show all attributes of the row object.

  def introduction_to_ASE_databases(self):
    from pathlib import Path
    import gpaw

    if Path('database.db').is_file():
      Path('database.db').unlink()

    structures = ['Si', 'Ge', 'C']
    db = connect('database.db')

    for f in structures:
      db.write(ase.build.bulk(f))

    for row in db.select():
      atoms = row.toatoms()
      calc = gpaw.GPAW(mode=gpaw.PW(400),
                       kpts=(4, 4, 4),
                       txt=f'{row.formula}-gpaw.txt', xc='LDA')
      atoms.calc = calc
      atoms.get_stress()
      filter = ExpCellFilter(atoms)
      opt = BFGS(filter)
      opt.run(fmax=0.05)
      db.write(atoms=atoms, relaxed=True)

    for row in db.select(relaxed=True):
      atoms = row.toatoms()
      calc = gpaw.GPAW(mode=gpaw.PW(400),
                       kpts=(4, 4, 4),
                       txt=f'{row.formula}-gpaw.txt', xc='LDA')
      atoms.calc = calc
      atoms.get_potential_energy()
      bg, _, _ = bandgap(calc=atoms.calc)
      db.update(row.id, bandgap=bg)
    pass


class TutorialMolecularDynamics():
  def __init__(self) -> None:
    pass

  def constant_energy_MD(self):
    """Demonstrates molecular dynamics with constant energy."""
    # Use Asap for a huge performance increase if it is installed
    use_asap = True

    if use_asap:
      # from asap3 import EMT
      size = 10
    else:
      from ase.calculators.emt import EMT
      size = 3

    # Set up a crystal
    atoms = FaceCenteredCubic(directions=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                              symbol="Cu",
                              size=(size, size, size),
                              pbc=True)

    # Describe the interatomic interactions with the Effective Medium Theory
    atoms.calc = EMT()

    # Set the momenta corresponding to T=300K
    MaxwellBoltzmannDistribution(atoms, temperature_K=300)

    # We want to run MD with constant energy using the VelocityVerlet algorithm.
    dyn = VelocityVerlet(atoms, 5 * units.fs)  # 5 fs time step.

    def printenergy(a=atoms):  # store a reference to atoms in the definition.
      """Function to print the potential, kinetic and total energy."""
      epot = a.get_potential_energy() / len(a)
      ekin = a.get_kinetic_energy() / len(a)
      print('Energy per atom: Epot = %.3feV  Ekin = %.3feV (T=%3.0fK)  '
            'Etot = %.3feV' % (epot, ekin, ekin / (1.5 * units.kB), epot + ekin))

    # Now run the dynamics
    dyn.attach(function=printenergy, interval=10)
    printenergy()
    dyn.run(200)

  def constant_temperature_MD(self):
    """Demonstrates molecular dynamics with constant temperature."""
    # from asap3 import EMT  # Way too slow with ase.EMT !
    import ase.calculators.emt
    from ase import units
    from ase.io.trajectory import Trajectory
    from ase.lattice.cubic import FaceCenteredCubic
    from ase.md.langevin import Langevin

    size = 10

    T = 1500  # Kelvin

    # Set up a crystal
    atoms = FaceCenteredCubic(directions=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                              symbol="Cu",
                              size=(size, size, size),
                              pbc=False)

    # Describe the interatomic interactions with the Effective Medium Theory
    atoms.calc = ase.calculators.emt.EMT()

    # We want to run MD with constant energy using the Langevin algorithm
    # with a time step of 5 fs, the temperature T and the friction
    # coefficient to 0.02 atomic units.
    dyn = Langevin(atoms, 5 * units.fs, T * units.kB, 0.002)

    def printenergy(a=atoms):  # store a reference to atoms in the definition.
      """Function to print the potential, kinetic and total energy."""
      epot = a.get_potential_energy() / len(a)
      ekin = a.get_kinetic_energy() / len(a)
      print('Energy per atom: Epot = %.3feV  Ekin = %.3feV (T=%3.0fK)  '
            'Etot = %.3feV' % (epot, ekin, ekin / (1.5 * units.kB), epot + ekin))

    dyn.attach(printenergy, interval=50)

    # We also want to save the positions of all atoms after every 100th time step.
    traj = Trajectory('moldyn3.traj', 'w', atoms)
    dyn.attach(traj.write, interval=50)

    # Now run the dynamics
    printenergy()
    dyn.run(5000)

    pass

  def isolated_particle(self,
                        use_asap=True):
    # When simulating isolated particles with MD, it is sometimes preferable to set random momenta corresponding to a specific temperature and let the system evolve freely. With a relatively high temperature, the is however a risk that the collection of atoms will drift out of the simulation box because the randomized momenta gave the center of mass a small but non-zero velocity too.
    """Demonstrates molecular dynamics for isolated particles."""
    from ase import units
    from ase.cluster.cubic import FaceCenteredCubic
    from ase.md.velocitydistribution import (MaxwellBoltzmannDistribution,
                                             Stationary, ZeroRotation)
    from ase.md.verlet import VelocityVerlet
    from ase.optimize import QuasiNewton

    if use_asap:
      # from asap3 import EMT
      size = 4
    else:
      from ase.calculators.emt import EMT
      size = 2

    # Set up a nanoparticle
    atoms = FaceCenteredCubic('Cu',
                              surfaces=[[1, 0, 0], [1, 1, 0], [1, 1, 1]],
                              layers=(size, size, size),
                              vacuum=4,
                              )
    atoms.center(vacuum=4)

    # Describe the interatomic interactions with the Effective Medium Theory
    atoms.calc = EMT()

    # Do a quick relaxation of the cluster
    qn = QuasiNewton(atoms)
    qn.run(0.001, 10)

    # Set the momenta corresponding to T=1200K
    MaxwellBoltzmannDistribution(atoms, temperature_K=1200)
    Stationary(atoms)  # zero linear momentum
    ZeroRotation(atoms)  # zero angular momentum

    # We want to run MD using the VelocityVerlet algorithm.

    # Save trajectory:
    dyn = VelocityVerlet(atoms, 5 * units.fs, trajectory='moldyn4.traj')

    def printenergy(a=atoms):  # store a reference to atoms in the definition.
      """Function to print the potential, kinetic and total energy."""
      epot = a.get_potential_energy() / len(a)
      ekin = a.get_kinetic_energy() / len(a)
      print('Energy per atom: Epot = %.3feV  Ekin = %.3feV (T=%3.0fK)  '
            'Etot = %.3feV' % (epot, ekin, ekin / (1.5 * units.kB), epot + ekin))

    dyn.attach(printenergy, interval=10)

    # Now run the dynamics
    printenergy()
    dyn.run(2000)

    # 查看
    # ase gui moldyn4.traj

  def equilibrating_a_TIPnP_Water_Box(self, temperature=300):
    # Equilibrating a TIPnP Water Box
    import numpy as np
    import ase.units as units
    from ase import Atoms
    from ase.calculators.tip3p import TIP3P, angleHOH, rOH
    from ase.constraints import FixBondLengths
    from ase.io.trajectory import Trajectory
    from ase.md import Langevin

    # Set up water box at 20 deg C density
    x = angleHOH * np.pi / 180 / 2
    pos = [[0, 0, 0],
           [0, rOH * np.cos(x), rOH * np.sin(x)],
           [0, rOH * np.cos(x), -rOH * np.sin(x)]]
    atoms = Atoms('OH2', positions=pos)

    vol = ((18.01528 / 6.022140857e23) / (0.9982 / 1e24)
           )**(1 / 3.)  # 根据水的密度算出一个水分子的体积
    atoms.set_cell((vol, vol, vol))
    atoms.center()

    atoms = atoms.repeat((3, 3, 3))
    atoms.set_pbc(True)

    # RATTLE-type constraints on O-H1, O-H2, H1-H2.
    atoms.constraints = FixBondLengths([(3 * i + j, 3 * i + (j + 1) % 3)
                                        for i in range(3**3)
                                        for j in [0, 1, 2]])

    tag = 'tip3p_27mol_equil'
    atoms.calc = TIP3P(rc=4.5)
    md = Langevin(atoms, 1 * units.fs, temperature_K=temperature,  # temperature=300 * units.kB,
                  friction=0.01, logfile=tag + '.log')

    traj = Trajectory(filename=tag + '.traj', mode='w', atoms=atoms)
    md.attach(traj.write, interval=1)
    md.run(4000)

    # Repeat box and equilibrate further.
    tag = 'tip3p_216mol_equil'
    # repeat not compatible with FixBondLengths currently.
    atoms.set_constraint()
    atoms = atoms.repeat((2, 2, 2))
    atoms.constraints = FixBondLengths([(3 * i + j, 3 * i + (j + 1) % 3)
                                        for i in range(len(atoms) / 3)
                                        for j in [0, 1, 2]])
    atoms.calc = TIP3P(rc=7.)
    md = Langevin(atoms, timestep=2 * units.fs, temperature_K=temperature,  # temperature=300 * units.kB,
                  friction=0.01, logfile=tag + '.log')

    traj = Trajectory(tag + '.traj', 'w', atoms)
    md.attach(traj.write, interval=1)
    md.run(2000)

    # The temperature calculated by ASE is assuming all degrees of freedom are available to the system. Since the constraints have removed the 3 vibrational modes from each water, the shown temperature will be 2/3 of the actual value.
    pass

  def Equilibrating_an_MD_box_of_acetonitrile(self):
    """https://wiki.fysik.dtu.dk/ase/tutorials/acn_equil/acn_equil.html
    """
    # The MD procedure we use for the equilibration closely follows the one presented in the tutorial Equilibrating a TIPnP Water Box.
    import numpy as np

    import ase.units as units
    from ase import Atoms
    from ase.calculators.acn import ACN, m_me, r_cn, r_mec
    from ase.constraints import FixLinearTriatomic
    from ase.io import Trajectory
    from ase.md import Langevin

    pos = [[0, 0, -r_mec],
           [0, 0, 0],
           [0, 0, r_cn]]
    atoms = Atoms('CCN', positions=pos)
    atoms.rotate(30, 'x')

    # First C of each molecule needs to have the mass of a methyl group
    masses = atoms.get_masses()
    masses[::3] = m_me
    atoms.set_masses(masses)

    # Determine side length of a box with the density of acetonitrile at 298 K
    # Density in g/Ang3 (https://pubs.acs.org/doi/10.1021/je00001a006)
    d = 0.776 / 1e24
    L = ((masses.sum() / units.mol) / d)**(1 / 3.)
    # Set up box of 27 acetonitrile molecules
    atoms.set_cell((L, L, L))
    atoms.center()
    atoms = atoms.repeat((3, 3, 3))
    atoms.set_pbc(True)

    # Set constraints for rigid triatomic molecules
    nm = 27
    atoms.constraints = FixLinearTriatomic(
        triples=[(3 * i, 3 * i + 1, 3 * i + 2)
                 for i in range(nm)])

    tag = 'acn_27mol_300K'
    atoms.calc = ACN(rc=np.min(np.diag(atoms.cell)) / 2)

    # Create Langevin object
    md = Langevin(atoms, 1 * units.fs,
                  temperature=300 * units.kB,
                  friction=0.01,
                  logfile=tag + '.log')

    traj = Trajectory(tag + '.traj', 'w', atoms)
    md.attach(traj.write, interval=1)
    md.run(5000)

    # Repeat box and equilibrate further
    atoms.set_constraint()
    atoms = atoms.repeat((2, 2, 2))
    nm = 216
    atoms.constraints = FixLinearTriatomic(
        triples=[(3 * i, 3 * i + 1, 3 * i + 2)
                 for i in range(nm)])

    tag = 'acn_216mol_300K'
    atoms.calc = ACN(rc=np.min(np.diag(atoms.cell)) / 2)

    # Create Langevin object
    md = Langevin(atoms, 2 * units.fs,
                  temperature=300 * units.kB,
                  friction=0.01,
                  logfile=tag + '.log')

    traj = Trajectory(tag + '.traj', 'w', atoms)
    md.attach(traj.write, interval=1)
    md.run(3000)
    pass


class Uncategorized():
  def __init__(self) -> None:
    """https://wiki.fysik.dtu.dk/ase/tutorials/defects/defects.html
    """
    pass


class AseTutorials_OptimizationGeneticAlgorithm():
  def __init__(self) -> None:
    """Optimization with a Genetic Algorithm
    """
    url = 'https://wiki.fysik.dtu.dk/ase/tutorials/ga/ga_optimize.html'
    pass

  def initialisations(self):
    # 1. The script doing all the initialisations should be run in the folder in which the GA optimisation is to take place. The script looks as follows:

    import numpy as np
    from ase.build import fcc111
    from ase.constraints import FixAtoms
    from ase.ga.data import PrepareDB
    from ase.ga.startgenerator import StartGenerator
    from ase.ga.utilities import closest_distances_generator, get_all_atom_types

    db_file = 'gadb.db'

    # create the surface
    slab = fcc111('Au', size=(4, 4, 1), vacuum=10.0, orthogonal=True)
    slab.set_constraint(FixAtoms(mask=len(slab) * [True]))

    # define the volume in which the adsorbed cluster is optimized
    # the volume is defined by a corner position (p0)
    # and three spanning vectors (v1, v2, v3)
    pos = slab.get_positions()
    cell = slab.get_cell()
    p0 = np.array([0., 0., max(pos[:, 2]) + 2.])
    v1 = cell[0, :] * 0.8  # 元胞x方向的矢量
    v2 = cell[1, :] * 0.8
    v3 = cell[2, :]
    v3[2] = 3.

    # Define the composition of the atoms to optimize
    atom_numbers = 2 * [47] + 2 * [79]  # [47, 47, 79, 79]

    # define the closest distance two atoms of a given species can be to each other
    unique_atom_types = get_all_atom_types(slab, atom_numbers)
    blmin = closest_distances_generator(atom_numbers=unique_atom_types,
                                        ratio_of_covalent_radii=0.7)

    # create the starting population
    sg = StartGenerator(slab, atom_numbers, blmin,
                        box_to_place_in=[p0, [v1, v2, v3]])

    # generate the starting population
    population_size = 20
    starting_population = [sg.get_new_candidate()
                           for i in range(population_size)]

    # from ase.visualize import view   # uncomment these lines
    # view(starting_population)        # to see the starting population

    # create the database to store information in
    d = PrepareDB(db_file_name=db_file,
                  simulation_cell=slab,
                  stoichiometry=atom_numbers)

    for a in starting_population:
      d.add_unrelaxed_candidate(a)

  def run(self,):
    # Having initialized the GA optimization we now need to actually run the GA. The main script running the GA consists of first an initialization part, and then a loop proposing new structures and locally optimizing them. The main script can look as follows:
    from random import random
    from ase.calculators.emt import EMT
    from ase.ga.cutandsplicepairing import CutAndSplicePairing
    from ase.ga.data import DataConnection
    from ase.ga.offspring_creator import OperationSelector
    from ase.ga.population import Population
    from ase.ga.standard_comparators import InteratomicDistanceComparator
    from ase.ga.standardmutations import (MirrorMutation, PermutationMutation,
                                          RattleMutation)
    from ase.ga.utilities import closest_distances_generator, get_all_atom_types
    from ase.io import write
    from ase.optimize import BFGS

    # Change the following three parameters to suit your needs
    population_size = 20
    mutation_probability = 0.3
    n_to_test = 20

    # Initialize the different components of the GA
    da = DataConnection('gadb.db')
    atom_numbers_to_optimize = da.get_atom_numbers_to_optimize()
    n_to_optimize = len(atom_numbers_to_optimize)
    slab = da.get_slab()
    all_atom_types = get_all_atom_types(slab, atom_numbers_to_optimize)
    blmin = closest_distances_generator(all_atom_types,
                                        ratio_of_covalent_radii=0.7)

    comp = InteratomicDistanceComparator(n_top=n_to_optimize,
                                         pair_cor_cum_diff=0.015,
                                         pair_cor_max=0.7,
                                         dE=0.02,
                                         mic=False)

    pairing = CutAndSplicePairing(slab, n_to_optimize, blmin)
    mutations = OperationSelector([1., 1., 1.],
                                  [MirrorMutation(blmin, n_to_optimize),
                                  RattleMutation(blmin, n_to_optimize),
                                  PermutationMutation(n_to_optimize)])

    # Relax all unrelaxed structures (e.g. the starting population)
    while da.get_number_of_unrelaxed_candidates() > 0:
      a = da.get_an_unrelaxed_candidate()
      a.calc = EMT()
      print('Relaxing starting candidate {}'.format(a.info['confid']))
      dyn = BFGS(a, trajectory=None, logfile=None)
      dyn.run(fmax=0.05, steps=100)
      a.info['key_value_pairs']['raw_score'] = -a.get_potential_energy()
      da.add_relaxed_step(a)

    # create the population
    population = Population(data_connection=da,
                            population_size=population_size,
                            comparator=comp)

    # test n_to_test new candidates
    for i in range(n_to_test):
      print(f'Now starting configuration number {i}')
      a1, a2 = population.get_two_candidates()
      a3, desc = pairing.get_new_individual([a1, a2])
      if a3 is None:
        continue
      da.add_unrelaxed_candidate(a3, description=desc)

      # Check if we want to do a mutation
      if random() < mutation_probability:
        a3_mut, desc = mutations.get_new_individual([a3])
        if a3_mut is not None:
          da.add_unrelaxed_step(a3_mut, desc)
          a3 = a3_mut

      # Relax the new candidate
      a3.calc = EMT()
      dyn = BFGS(a3, trajectory=None, logfile=None)
      dyn.run(fmax=0.05, steps=100)
      a3.info['key_value_pairs']['raw_score'] = -a3.get_potential_energy()
      da.add_relaxed_step(a3)
      population.update()

    write('all_candidates.traj', da.get_all_relaxed_candidates())

    # The above script proposes and locally relaxes 20 new candidates. To speed up the execution of this sample the local relaxations are limited to 100 steps. This restriction should not be set in a real application. Note it is important to set the raw_score, as it is what is being optimized (maximized). It is really an input in the atoms.info['key_value_pairs'] dictionary.

    # The GA progress can be monitored by running the tool ase/ga/tools/get_all_candidates in the same folder as the GA. This will create a trajectory file all_candidates.traj which includes all locally relaxed candidates the GA has tried. This script can be run at the same time as the main script is running. This is possible because the ase.db database is being updated as the GA progresses.

  def run_parallel(self):
    import sys
    from ase.calculators.emt import EMT
    from ase.ga.relax_attaches import VariansBreak
    from ase.io import read, write
    from ase.optimize import BFGS

    fname = sys.argv[1]

    print(f'Now relaxing {fname}')
    a = read(fname)

    a.calc = EMT()
    dyn = BFGS(a, trajectory=None, logfile=None)
    vb = VariansBreak(a, dyn)
    dyn.attach(vb.write)
    dyn.run(fmax=0.05)

    a.info['key_value_pairs']['raw_score'] = -a.get_potential_energy()

    write(fname[:-5] + '_done.traj', a)

    print(f'Done relaxing {fname}')

  def run_on_pbs(self):
    from random import random
    from ase.ga.cutandsplicepairing import CutAndSplicePairing
    from ase.ga.data import DataConnection
    from ase.ga.offspring_creator import OperationSelector
    from ase.ga.pbs_queue_run import PBSQueueRun
    from ase.ga.population import Population
    from ase.ga.standard_comparators import InteratomicDistanceComparator
    from ase.ga.standardmutations import (MirrorMutation, PermutationMutation,
                                          RattleMutation)
    from ase.ga.utilities import closest_distances_generator, get_all_atom_types
    from ase.io import write

    def jtg(job_name, traj_file):
      s = '#!/bin/sh\n'
      s += '#PBS -l nodes=1:ppn=12\n'
      s += '#PBS -l walltime=48:00:00\n'
      s += f'#PBS -N {job_name}\n'
      s += '#PBS -q q12\n'
      s += 'cd $PBS_O_WORKDIR\n'
      s += f'python calc.py {traj_file}\n'
      return s

    population_size = 20
    mutation_probability = 0.3

    # Initialize the different components of the GA
    da = DataConnection('gadb.db')
    tmp_folder = 'tmp_folder/'
    # The PBS queing interface is created
    pbs_run = PBSQueueRun(da,
                          tmp_folder=tmp_folder,
                          job_prefix='Ag2Au2_opt',
                          n_simul=5,
                          job_template_generator=jtg)

    atom_numbers_to_optimize = da.get_atom_numbers_to_optimize()
    n_to_optimize = len(atom_numbers_to_optimize)
    slab = da.get_slab()
    all_atom_types = get_all_atom_types(slab, atom_numbers_to_optimize)
    blmin = closest_distances_generator(all_atom_types,
                                        ratio_of_covalent_radii=0.7)

    comp = InteratomicDistanceComparator(n_top=n_to_optimize,
                                         pair_cor_cum_diff=0.015,
                                         pair_cor_max=0.7,
                                         dE=0.02,
                                         mic=False)
    pairing = CutAndSplicePairing(slab, n_to_optimize, blmin)
    mutations = OperationSelector([1., 1., 1.],
                                  [MirrorMutation(blmin, n_to_optimize),
                                  RattleMutation(blmin, n_to_optimize),
                                  PermutationMutation(n_to_optimize)])

    # Relax all unrelaxed structures (e.g. the starting population)
    while (da.get_number_of_unrelaxed_candidates() > 0 and
           not pbs_run.enough_jobs_running()):
      a = da.get_an_unrelaxed_candidate()
      pbs_run.relax(a)

    # create the population
    population = Population(data_connection=da,
                            population_size=population_size,
                            comparator=comp)

    # Submit new candidates until enough are running
    while (not pbs_run.enough_jobs_running() and
           len(population.get_current_population()) > 2):
      a1, a2 = population.get_two_candidates()
      a3, desc = pairing.get_new_individual([a1, a2])
      if a3 is None:
        continue
      da.add_unrelaxed_candidate(a3, description=desc)

      if random() < mutation_probability:
        a3_mut, desc = mutations.get_new_individual([a3])
        if a3_mut is not None:
          da.add_unrelaxed_step(a3_mut, desc)
          a3 = a3_mut
      pbs_run.relax(a3)

    write('all_candidates.traj', da.get_all_relaxed_candidates())

  def search_struct_screen(self):
    from random import random
    import numpy as np

    from ase.ga import get_parametrization
    from ase.ga.cutandsplicepairing import CutAndSplicePairing
    from ase.ga.data import DataConnection
    from ase.ga.offspring_creator import OperationSelector
    from ase.ga.pbs_queue_run import PBSQueueRun
    from ase.ga.population import Population
    from ase.ga.standard_comparators import InteratomicDistanceComparator
    from ase.ga.standardmutations import (MirrorMutation, PermutationMutation,
                                          RattleMutation)
    from ase.ga.utilities import (closest_distances_generator, get_all_atom_types,
                                  get_angles_distribution, get_atoms_connections,
                                  get_atoms_distribution, get_neighborlist,
                                  get_rings)
    from ase.io import write

    def jtg(job_name, traj_file):
      s = '#!/bin/sh\n'
      s += '#PBS -l nodes=1:ppn=16\n'
      s += '#PBS -l walltime=100:00:00\n'
      s += f'#PBS -N {job_name}\n'
      s += '#PBS -q q16\n'
      s += 'cd $PBS_O_WORKDIR\n'
      s += 'NPROCS==`wc -l < $PBS_NODEFILE`\n'
      s += 'mpirun --mca mpi_warn_on_fork 0 -np $NPROCS '
      s += f'gpaw-python calc_gpaw.py {traj_file}\n'
      return s

    def combine_parameters(conf):
      # Get and combine selected parameters
      parameters = []
      gets = [get_atoms_connections(conf) + get_rings(conf) +
              get_angles_distribution(conf) + get_atoms_distribution(conf)]
      for get in gets:
        parameters += get
      return parameters

    def should_we_skip(conf, comparison_energy, weights):
      parameters = combine_parameters(conf)
      # Return if weights not defined (too few completed
      # calculated structures to make a good fit)
      if weights is None:
        return False
      regression_energy = sum(p * q for p, q in zip(weights, parameters))
      # Skip with 90% likelihood if energy appears to go up 5 eV or more
      if (regression_energy - comparison_energy) > 5 and random() < 0.9:
        return True
      else:
        return False

    population_size = 20
    mutation_probability = 0.3

    # Initialize the different components of the GA
    da = DataConnection('gadb.db')
    tmp_folder = 'work_folder/'
    # The PBS queing interface is created
    pbs_run = PBSQueueRun(da,
                          tmp_folder=tmp_folder,
                          job_prefix='Ag2Au2_opt',
                          n_simul=5,
                          job_template_generator=jtg,
                          find_neighbors=get_neighborlist,
                          perform_parametrization=combine_parameters)

    atom_numbers_to_optimize = da.get_atom_numbers_to_optimize()
    n_to_optimize = len(atom_numbers_to_optimize)
    slab = da.get_slab()
    all_atom_types = get_all_atom_types(slab, atom_numbers_to_optimize)
    blmin = closest_distances_generator(all_atom_types,
                                        ratio_of_covalent_radii=0.7)

    comp = InteratomicDistanceComparator(n_top=n_to_optimize,
                                         pair_cor_cum_diff=0.015,
                                         pair_cor_max=0.7,
                                         dE=0.02,
                                         mic=False)
    pairing = CutAndSplicePairing(slab, n_to_optimize, blmin)
    mutations = OperationSelector([1., 1., 1.],
                                  [MirrorMutation(blmin, n_to_optimize),
                                  RattleMutation(blmin, n_to_optimize),
                                  PermutationMutation(n_to_optimize)])

    # Relax all unrelaxed structures (e.g. the starting population)
    while (da.get_number_of_unrelaxed_candidates() > 0 and
           not pbs_run.enough_jobs_running()):
      a = da.get_an_unrelaxed_candidate()
      pbs_run.relax(a)

    # create the population
    population = Population(data_connection=da,
                            population_size=population_size,
                            comparator=comp)

    # create the regression expression for estimating the energy
    all_trajs = da.get_all_relaxed_candidates()
    sampled_points = []
    sampled_energies = []
    for conf in all_trajs:
      no_of_conn = list(get_parametrization(conf))
      if no_of_conn not in sampled_points:
        sampled_points.append(no_of_conn)
        sampled_energies.append(conf.get_potential_energy())

    sampled_points = np.array(sampled_points)
    sampled_energies = np.array(sampled_energies)

    if len(sampled_points) > 0 and len(sampled_energies) >= len(sampled_points[0]):
      weights = np.linalg.lstsq(sampled_points, sampled_energies, rcond=-1)[0]
    else:
      weights = None

    # Submit new candidates until enough are running
    while (not pbs_run.enough_jobs_running() and
           len(population.get_current_population()) > 2):
      a1, a2 = population.get_two_candidates()

      # Selecting the "worst" parent energy
      # which the child should be compared to
      ce_a1 = da.get_atoms(a1.info['relax_id']).get_potential_energy()
      ce_a2 = da.get_atoms(a2.info['relax_id']).get_potential_energy()
      comparison_energy = min(ce_a1, ce_a2)

      a3, desc = pairing.get_new_individual([a1, a2])
      if a3 is None:
        continue
      if should_we_skip(a3, comparison_energy, weights):
        continue
      da.add_unrelaxed_candidate(a3, description=desc)

      if random() < mutation_probability:
        a3_mut, desc_mut = mutations.get_new_individual([a3])
        if (a3_mut is not None and
                not should_we_skip(a3_mut, comparison_energy, weights)):
          da.add_unrelaxed_step(a3_mut, desc_mut)
          a3 = a3_mut
      pbs_run.relax(a3)

    write('all_candidates.traj', da.get_all_relaxed_candidates())


class AseTutorials_GeneticAlgorithmSearch():
  def __init__(self) -> None:
    """Genetic algorithm Search for stable FCC alloys
    """
    url = 'https://wiki.fysik.dtu.dk/ase/tutorials/ga/ga_fcc_alloys.html'
    pass

  def get_refers_db(self):
    # 获得参考数据, 获得7种fcc金属的优化晶格常数和最低能量
    import numpy as np
    from ase.calculators.emt import EMT
    from ase.db import connect
    from ase.eos import EquationOfState
    from ase.lattice.cubic import FaceCenteredCubic

    db = connect('refs.db')

    metals = ['Al', 'Au', 'Cu', 'Ag', 'Pd', 'Pt', 'Ni']
    for m in metals:
      atoms = FaceCenteredCubic(m)
      atoms.calc = EMT()
      e0 = atoms.get_potential_energy()
      a = atoms.cell[0][0]

      eps = 0.05
      volumes = (a * np.linspace(1 - eps, 1 + eps, 9))**3
      energies = []
      for v in volumes:
        atoms.set_cell([v**(1. / 3)] * 3, scale_atoms=True)
        energies.append(atoms.get_potential_energy())

      eos = EquationOfState(volumes, energies)
      v1, e1, B = eos.fit()

      atoms.set_cell([v1**(1. / 3)] * 3, scale_atoms=True)
      ef = atoms.get_potential_energy()

      db.write(atoms, metal=m,
               latticeconstant=v1**(1. / 3),
               energy_per_atom=ef / len(atoms))

  def initial_population(self,):
    # We choose a population size of 10 individuals and create the initial population by randomly selecting four elements for each starting individual.
    import random
    from ase import Atoms
    from ase.ga.data import PrepareDB
    import ase.ga.data

    metals = ['Al', 'Au', 'Cu', 'Ag', 'Pd', 'Pt', 'Ni']

    population_size = 10

    # Create database
    db = PrepareDB('fcc_alloys.db',
                   population_size=population_size,
                   metals=metals)

    # Create starting population
    for i in range(population_size):
      atoms_string = [random.choice(metals) for _ in range(4)]
      db.add_unrelaxed_candidate(Atoms(atoms_string),
                                 atoms_string=''.join(atoms_string))

  def relax(self, input_atoms, ref_db):
    import numpy as np
    from ase.calculators.emt import EMT
    from ase.db import connect
    from ase.eos import EquationOfState
    from ase.lattice.cubic import FaceCenteredCubic

    atoms_string = input_atoms.get_chemical_symbols()

    # Open connection to the database with reference data
    db = connect(ref_db)

    # Load our model structure which is just FCC
    atoms = FaceCenteredCubic('X', latticeconstant=1.)
    atoms.set_chemical_symbols(atoms_string)

    # Compute the average lattice constant of the metals in this individual
    # and the sum of energies of the constituent metals in the fcc lattice
    # we will need this for calculating the heat of formation
    a = 0
    ei = 0
    for m in set(atoms_string):
      dct = db.get(metal=m)
      count = atoms_string.count(m)
      a += count * dct.latticeconstant
      ei += count * dct.energy_per_atom
    a /= len(atoms_string)
    atoms.set_cell([a, a, a], scale_atoms=True)

    # Since calculations are extremely fast with EMT we can also do a volume
    # relaxation
    atoms.calc = EMT()
    eps = 0.05
    volumes = (a * np.linspace(1 - eps, 1 + eps, 9))**3
    energies = []
    for v in volumes:
      atoms.set_cell([v**(1. / 3)] * 3, scale_atoms=True)
      energies.append(atoms.get_potential_energy())

    eos = EquationOfState(volumes, energies)
    v1, ef, B = eos.fit()
    latticeconstant = v1**(1. / 3)

    # Calculate the heat of formation by subtracting ef with ei
    hof = (ef - ei) / len(atoms)

    # Place the calculated parameters in the info dictionary of the
    # input_atoms object
    input_atoms.info['key_value_pairs']['hof'] = hof

    # Raw score must always be set
    # Use one of the following two; they are equivalent
    input_atoms.info['key_value_pairs']['raw_score'] = -hof
    # set_raw_score(input_atoms, -hof)

    input_atoms.info['key_value_pairs']['latticeconstant'] = latticeconstant

    # Setting the atoms_string directly for easier analysis
    atoms_string = ''.join(input_atoms.get_chemical_symbols())
    input_atoms.info['key_value_pairs']['atoms_string'] = atoms_string

    pass

  def main(self):
    # from ga_fcc_alloys_relax import relax

    from ase.ga.convergence import GenerationRepetitionConvergence
    from ase.ga.data import DataConnection
    from ase.ga.element_crossovers import OnePointElementCrossover
    from ase.ga.element_mutations import RandomElementMutation
    from ase.ga.offspring_creator import OperationSelector
    from ase.ga.population import Population

    # Specify the number of generations this script will run
    num_gens = 40

    db = DataConnection('fcc_alloys.db')
    ref_db = 'refs.db'

    # Retrieve saved parameters
    population_size = db.get_param('population_size')
    metals = db.get_param('metals')

    # Specify the procreation operators for the algorithm
    # Try and play with the mutation operators that move to nearby
    # places in the periodic table
    oclist = ([1, 1], [RandomElementMutation(metals),
                       OnePointElementCrossover(metals)])
    operation_selector = OperationSelector(*oclist)

    # Pass parameters to the population instance
    pop = Population(data_connection=db,
                     population_size=population_size)

    # We form generations in this algorithm run and can therefore set
    # a convergence criteria based on generations
    cc = GenerationRepetitionConvergence(pop, 3)

    # Relax the starting population
    while db.get_number_of_unrelaxed_candidates() > 0:
      a = db.get_an_unrelaxed_candidate()
      self.relax(a, ref_db)
      db.add_relaxed_step(a)
    pop.update()

    # Run the algorithm
    for _ in range(num_gens):
      if cc.converged():
        print('converged')
        break
      for i in range(population_size):
        a1, a2 = pop.get_two_candidates(with_history=False)
        op = operation_selector.get_operator()
        a3, desc = op.get_new_individual([a1, a2])

        db.add_unrelaxed_candidate(a3, description=desc)

        self.relax(a3, ref_db)
        db.add_relaxed_step(a3)

      pop.update()

      # Print the current population to monitor the evolution
    pass


# Modelues

class AseAtoms():
  def __init__(self) -> None:
    pass

  def CO_moleculer(self,):
    # define a CO molecule:
    from ase import Atoms
    d = 1.1
    co = ase.Atoms('CO', positions=[(0, 0, 0), (0, 0, d)])
    # Here, the first argument specifies the type of the atoms and we used the positions keywords to specify their positions. Other possible keywords are: numbers, tags, momenta, masses, magmoms and charges.

    # These three are equivalent:
    from ase import Atom
    d = 1.104  # N2 bondlength
    a = Atoms('N2', [(0, 0, 0), (0, 0, d)])
    a = Atoms(numbers=[7, 7], positions=[(0, 0, 0), (0, 0, d)])
    a = Atoms([Atom('N', (0, 0, 0)), Atom('N', (0, 0, d))])
    return co

  def gold_wire(self,):
    # make an infinite gold wire with a bond length of 2.9 Å:
    d = 2.9
    L = 10.0
    # You can also use the following methods to work with the unit cell and the boundary conditions: set_pbc(), set_cell(), get_cell(), and get_pbc().
    wire = ase.Atoms('Au',
                     positions=[[0, L / 2, L / 2]],
                     cell=[d, L, L],
                     pbc=[1, 0, 0])
    return wire

  def methods(self):
    atom = ase.Atom('C', (0, 0.0))
    atom.symbol  # 获得原子对象的符号

    atoms = Atoms('N3', [(0, 0, 0), (1, 0, 0), (0, 0, 1)])
    atoms.get_positions()  # 获取位置
    atoms.set_positions([(2, 0, 0), (0, 2, 2), (2, 2, 0)])
    atoms.get_positions()

    # 改变原子种类
    atoms.symbols
    # Symbols('AlN2')
    atoms.symbols[2] = 'Cu'
    atoms.symbols
    # Symbols('AlNCu')
    atoms.numbers
    # array([13,  7, 29])

    # Hexagonal unit cell: 变为三斜晶胞
    atoms.cell = [2.5, 2.5, 15, 90, 90, 120]

  def add_calculator(self, atoms, calc):
    # A calculator can be attached to the atoms with the purpose of calculating energies and forces on the atoms. ASE works with many different ase.calculators.
    atoms.calc = calc
    # After the calculator has been appropriately setup the energy of the atoms can be obtained through
    atoms.get_potential_energy()

  def methods(self):
    def tags():
      """set_tags
      通过使用 set_tags 方法为 Atoms 对象设置标签，你可以为每个原子附加额外的信息。这些标签可以用于各种目的，例如：
      标记特定的原子： 你可以使用标签来标记特定的原子，以便在后续的分析或可视化中更容易识别和操作这些原子。
      记录原子的状态： 标签可以用来记录原子的状态或属性，例如其所属的簇、其结构状态等。
      筛选和过滤： 你可以根据标签的值对原子进行筛选和过滤。例如，你可以选择所有具有特定标签值的原子。
      """
      # example
      # 创建一个包含一些原子的 Atoms 对象
      atoms = ase.Atoms('H2O')
      # 设置要应用的标签数组
      tags_to_set = [1, 2, 3]  # 与原子数相同的标签数组
      atoms.set_tags(tags_to_set)
      # 选择所有具有特定标签值的原子
      selected_atoms = atoms[atoms.get_tags() == 2]
    # 删除H原子
    from ase.build import molecule
    atoms = molecule('CH3CH2OH')
    del atoms[[atom.index for atom in atoms if atom.symbol == 'H']]


class AseCell():
  def __init__(self) -> None:
    pass

  def ce(self):
    # The Cell object represents three lattice vectors forming a parallel epiped.
    # atoms.cell is a Cell object.
    cell = ase.build.bulk('Au').cell

    # The cell behaves like a 3x3 array when used like one:
    """
    cell[:]
    array([[0.  , 2.04, 2.04],
          [2.04, 0.  , 2.04],
          [2.04, 2.04, 0.  ]])
    # Common functionality:

    cell.lengths()
    array([2.88499567, 2.88499567, 2.88499567])
    cell.angles()
    array([60., 60., 60.])
    cell.volume
    16.979328000000002
    """
    return cell


class AseUnits():
  def __init__(self) -> None:
    # Physical units are defined in the ase/units.py module. Electron volts (eV), Ångström (Ang), the atomic mass unit and Kelvin are defined as 1.0. Other units are (amongst others) nm, Bohr, Hartree or Ha, kJ, kcal, mol, Rydberg or Ry, second, fs and kB.

    pass

  def show(self,):
    from ase.units import Bohr, Rydberg, kJ, kB, fs, Hartree, mol, kcal
    for k, v in zip('Bohr,Rydberg,kJ,kB,fs,Hartree,mol,kcal'.split(','),
                    [Bohr, Rydberg, kJ, kB, fs, Hartree, mol, kcal]):
      print(f'{k}={v}')


class AseInputOutput():
  def __init__(self) -> None:
    # 查看所有的文件格式
    ase.io.formats.ioformats
    # 计算器的 io
    url = 'https://wiki.fysik.dtu.dk/ase/ase/io/formatoptions.html'
    pass

  def read_file(self, fname='slab.traj'):
    # Reading from a file is done like this:
    from ase import io
    slab_from_file = io.read(fname)

    import ase.io.vasp
    ase.io.vasp.read_vasp_out()
    import ase.io.gpaw_out
    ase.io.gpaw_out.read_gpaw_out()

    # If the file contains several configurations, the default behavior of the write() function is to return the last configuration. However, we can load a specific configuration by doing:
    io.read(fname)      # last configuration
    io.read(fname, -1)  # same as above
    io.read(fname, 0)   # first configuration

    io.iread(fname)  # reads multiple images, one at a time.
    for atoms in io.iread(fname):  # 从iread 读取图像
      # print(atoms) # 获得
      pass

    # The read() function is only designed to retrieve the atomic configuration from a file, but for the CUBE format you can import the function:
    from ase.io.cube import read_cube_data
    data, atoms = read_cube_data('abc.cube')

  def write_file(self,):
    # 可选的格式 xyz, cube, pdb, traj, py
    # 以下两种方式都可以, 但是 ase.io.vasp.write_vasp 这种方式能够查看具体的参数
    atoms = AseAtoms().gold_wire()
    atoms.write('poscar', format='vasp')
    import ase.io
    ase.io.write('poscar', atoms, format='vasp')
    import ase.io.vasp
    ase.io.vasp.write_vasp('poscar1', atoms, direct=True)

    # --- traj file
    adsorbate = ase.Atoms('CO')
    adsorbate[1].z = 1.1
    a = 3.61
    slab = ase.build.fcc111('Cu', (2, 2, 3), a=a, vacuum=7.0)
    ase.build.add_adsorbate(slab, adsorbate, 1.8, 'ontop')
    # Use ASE’s native format for writing all information:
    ase.io.write('slab.traj', slab)
    b = ase.io.read('slab.traj')
    b.cell.round(3)
    b.pbc
    #
    self.trajectory()

    # Note that in general the XYZ-format does not contain information about the unit cell, however, ASE uses the extended XYZ-format which stores the unitcell:
    from ase.io import read, write
    ase.io.write('slab.xyz', slab)  # .xyz 可以用ovito 查看  atoms_obj 可以是上面的slab
    a = ase.io.read('slab.xyz')
    cell = a.get_cell()
    cell.round(3)  # 保留三位小数显示晶胞
    a.get_pbc()  # 查看是周期的

    # Write PNG image
    ase.io.write('slab.png', slab * (3, 3, 1), rotation='10z,-80x')

    # Write animation with 500 ms duration per frame
    ase.io.write('movie.gif',
                 [ase.build.bulk(s) for s in ['Cu', 'Ag', 'Au']], interval=500)

    # Write POVRAY file (the projection settings and povray specific settings are separated)
    ase.io.write('slab.pov', slab * (3, 3, 1),
                 rotation='10z,-80x',
                 )
    # This is an example of displaying bond order for a molecule
    # 由于最后一个命令出错 无法得到图片
    import ase.build.molecule
    from ase.io.pov import get_bondpairs, set_high_bondorder_pairs

    C2H4 = ase.build.molecule.molecule('C2H4')
    r = [{'C': 0.4, 'H': 0.2}[at.symbol] for at in C2H4]
    bondpairs = get_bondpairs(C2H4, radius=1.1)
    high_bondorder_pairs = {}
    # This defines offset, bond order, and bond_offset of the bond between 0 and 1
    high_bondorder_pairs[(0, 1)] = ((0, 0, 0), 2, (0.17, 0.17, 0))
    bondpairs = set_high_bondorder_pairs(bondpairs, high_bondorder_pairs)
    renderer = ase.io.write('C2H4.pov', C2H4, format='pov',
                            radii=r, rotation='90y',
                            povray_settings=dict(canvas_width=200, bondatoms=bondpairs))
    # renderer.render()

  def trajectory(self, dyn):
    # Typically, trajectories are used to store different configurations of the same system (i.e. the same atoms). If you need to store configurations of different systems, the ASE Database module may be more appropriate.
    # The Trajectory function returns a Trajectory reading or writing object, depending on the mode.
    # ase.io.Trajectory(filename, mode='r', atoms=None, properties=None, master=None)
    # Reading a trajectory file is done by indexing the TrajectoryReader object, i.e. traj[0] reads the first configuration, traj[-1] reads the last, traj[3:8] returns a list of the third through seventh, etc.
    # Writing a trajectory file is done by calling the write method. If no atoms object was given when creating the object, it must be given as an argument to the write method.

    # Reading a configuration:
    from ase.io.trajectory import Trajectory
    traj = Trajectory('example.traj')
    atoms = traj[-1]

    # Reading all configurations:
    traj = Trajectory('example.traj')
    for atoms in traj:
      # Analyze atoms
      pass

    # Writing every 100th time step in a molecular dynamics simulation: dyn is the dynamics (e.g. VelocityVerlet, Langevin or similar)
    traj = Trajectory('example.traj', 'w', atoms)
    dyn.attach(traj.write, interval=100)
    dyn.run(10000)
    traj.close()
    return

  def database(self):
    return AseDB()


class AseVisualize():
  def __init__(self) -> None:
    pass

  def visualize(self, atoms):
    # The simplest way to visualize the atoms is the view() function:
    from ase.visualize import view
    ase.visualize.view(atoms)
    # 查看 .traj
    os.system('ase gui N2Cu.traj')

    # where atoms is any Atoms object. Alternative viewers can be used by specifying the optional keyword viewer=... - use one of ‘ase.gui’, ‘gopenmol’, ‘vmd’, ‘rasmol’, ‘paraview’, ‘ngl’. The VMD and Avogadro viewers can take an optional data argument to show 3D data, such as charge density:
    "view(atoms, viewer='VMD', data=...)"
    ase.visualize.view(atoms, repeat=(3, 3, 2))

    # If you do not wish to open an interactive gui, but rather visualize your structure by dumping directly to a graphics file; you can use the write command of the ase.io module, which can write ‘eps’, ‘png’, and ‘pov’ files directly, like this:
    from ase.io import write
    write('image.png', atoms)

  def view_for_jupyter(self, atoms):
    # Viewer for Jupyter notebooks¶
    # A simple viewer based on X3D is built into ASE, which should work on modern browsers without additional packages, by typing the following command into a Jupyter notebook:
    ase.visualize.view(atoms, viewer='x3d')

  def iso_surface(self,):
    # Plotting iso-surfaces with Mayavi¶

    # The ase.visualize.mlab.plot() function can be used from the command-line:
    # $ python -m ase.visualize.mlab abc.cube

    # to plot data from a cube-file or alternatively a wave function or an electron density from a calculator restart file:
    # $ python -m ase.visualize.mlab -C gpaw abc.gpw

    # ase.visualize.mlab.plot(atoms, data, contours)
    pass


class AseDB():
  def __init__(self) -> None:
    """https://wiki.fysik.dtu.dk/ase/ase/db/db.html
    """
    pass

  def read_db(self,):
    # Integration with other parts of ASE¶
    import ase.io
    ase.io.read('Al.db', index=':')  # 读取原子对象后就可以获得各种属性

    # Also the ASE’s GUI program can read from databases using the same syntax.
    import ase.io
    a = ase.io.read('abc.db@42')
    a = ase.io.read('abc.db@id=42')  # same thing
    b = ase.io.read('abc.db@v3,abc=H')
    ase.io.read('Al.db@surface')  # 包含键surface的
    ase.io.read('Al.db@Al,surface=100,formula=Al5')
    # 更详细的参考 https://wiki.fysik.dtu.dk/ase/ase/db/db.html

    pass

  def python_interface(self):
    """https://wiki.fysik.dtu.dk/ase/ase/db/db.html#module-ase.db
    """
    # 1. 连接 db
    from ase.optimize import BFGS
    from ase.calculators.emt import EMT
    from ase import Atoms
    import ase.db
    db = ase.db.connect('abc.db')
    # 2. db 写入内容
    h2 = Atoms('H2', [(0, 0, 0), (0, 0, 0.7)])
    h2.calc = EMT()
    h2.get_total_energy()
    db.write(h2)
    # 再写个
    BFGS(h2).run(fmax=0.01)
    db.write(h2, relaxed=True)
    # db.write(h2, data={'parents':[3,4,5],'b':40},id=1)  # data是可以写入复杂的数据的参数
    # row.data.parents # 抽取复杂数据
    # 3. 选择行
    row_gen = db.select()  # 选择多行
    for row in row_gen:
      print(row.id, row.energy)  # 查看
    row = db.get(selection=2)  # 选择单行, 通过行号
    # row = db.get(relaxed=1)  # 选择单行, 通过键值对选取
    for key in row:
      print(key, row[key])  # 查看单行内容
    # 4. 更新行
    e2 = row.energy
    e1 = db.get(H=1).energy
    ae = 2 * e1 - e2
    id = db.get(relaxed=1).id
    db.update(id, atomization_energy=ae)

    db.update(atoms=h2, id=2)  # 更新第二行
    # 5. 删除行
    db.delete(ids=[1, 2,])  # 删除1，2行

    # 从db 数据库抽取 atoms 对象
    h2 = db.get_atoms(H=2)
    row = db.get(formula='Al5')
    atoms: ase.Atoms = row.toatoms()
    atoms.get_potential_energy()

    atoms = db.get_atoms(id=row.id)  # 或者
    atoms.get_potential_energy()

    db = ase.db.connect('bulk.db')
    for row in db.select():
      atoms = row.toatoms()  # 抽取原子对象
      print(atoms)

    # dir(db)  # dir 查看对象的所有属性

    # 抽取行数据的列值, 以下三种方法
    """
    as attributes (row.key)
    indexing (row['key'])
    the get() method (row.get('key'))
    """
    # you will be able to run several jobs in parallel without worrying about two jobs trying to do the same calculation. The reserve() method will write an empty row with the name key and return the ID of that row. Other jobs trying to make the same reservation will fail. While the jobs are running, you can keep an eye on the ongoing (reserved) calculations by identifying empty rows:
    """
    for name in many_molecules:
      id = db.reserve(name=name)
      if id is None:
          continue
      mol = read(name)
      calculate_something(mol)
      db.write(mol, id=id, name=name)
    """
    # 查看数据库
    # $ase db abc.db

    # You can also write/read to/from JSON using:
    # $ ase db proj1.db --set-metadata metadata.json
    # $ ase db proj1.db --show-metadata > metadata.json

    # External Tables
    # If the number of key_value_pairs becomes large, for example when saving a large number of features for your machine learning model, ASE DB offers an alternative way of storing them. Internally ASE can create a dedicated table to store groups of key_value_pairs. You can store a group of key_value_pairs in a separate table named features by:

    atoms = Atoms()
    no_features = 5000
    feature_dict = dict(('feature' + str(i), i) for i in range(no_features))
    id = db.write(atoms, external_tables={'features': feature_dict})
    pass

  def example(self):
    from pathlib import Path
    from gpaw import GPAW, PW
    from ase.constraints import ExpCellFilter
    import ase.optimize
    import ase.db
    import ase.build
    import ase.dft.bandgap

    if Path('database.db').is_file():
      Path('database.db').unlink()

    structures = ['Si', 'Ge', 'C']
    db = ase.db.connect('database.db')

    for f in structures:
      db.write(ase.build.bulk(f))

    for row in db.select():
      atoms: ase.Atoms = row.toatoms()
      calc = GPAW(mode=PW(400),
                  kpts=(4, 4, 4),
                  txt=f'{row.formula}-gpaw.txt', xc='LDA')
      atoms.calc = calc
      atoms.get_stress()
      filter = ExpCellFilter(atoms)
      opt = ase.optimize.BFGS(filter)
      opt.run(fmax=0.05)
      db.write(atoms=atoms, relaxed=True)

    for row in db.select(relaxed=True):
      atoms = row.toatoms()
      calc = GPAW(mode=PW(400),
                  kpts=(4, 4, 4),
                  txt=f'{row.formula}-gpaw.txt', xc='LDA')
      atoms.calc = calc
      atoms.get_potential_energy()
      bg, _, _ = ase.dft.bandgap.bandgap(calc=atoms.calc)
      db.update(row.id, bandgap=bg)

    pass


class AseBuild():
  def __init__(self) -> None:
    # See also
    # The ase.lattice module. The module contains functions for creating most common crystal structures with arbitrary orientation. The user can specify the desired Miller index along the three axes of the simulation, and the smallest periodic structure fulfilling this specification is created. Both bulk crystals and surfaces can be created.

    # The ase.cluster module. Useful for creating nanoparticles and clusters.

    # The ase.spacegroup module

    # The ase.geometry module
    pass

  def bulk(self,):
    # simple_bulk_crystals: bulk()
    # 元胞
    a1 = ase.build.bulk('Cu', 'fcc', a=3.6)
    # 立方单胞
    a2 = ase.build.bulk('Cu', 'fcc', a=3.6, orthorhombic=True)
    # 晶胞
    a3 = ase.build.bulk('Cu', 'fcc', a=3.6, cubic=True)

    MgO = ase.build.bulk("MgO", crystalstructure="rocksalt", a=4.2)

    # 建立想要的体块晶体
    # atoms=ase.build.bulk('Mn','bcc',a=3) # 无法创建
    # 通过以下的方式建立
    atoms: ase.Atoms = ase.build.bulk('Ag', 'bcc', a=3, cubic=True)
    atoms.set_chemical_symbols(['Mn' for _ in range(len(atoms))])
    ase.visualize.view(atoms)
    # 或者如下
    bcc = ase.lattice.BCC(a=3,).cellpar()
    atoms = ase.Atoms(symbols='Mn', cell=bcc,)
    # 或者
    from ase.lattice.cubic import BodyCenteredCubic
    atoms = BodyCenteredCubic(symbol='Mn',
                              latticeconstant=4.0,
                              # directions=[[1, 0, 0], [1, 1, 0], [1,1,1]], 或者任意方向
                              )

    pass

  def molecule(self,):
    # Simple molecules: molecule()
    from ase.collections import g2
    # print(g2.names)  # 查看分子数据库
    from ase.build import molecule
    atoms = molecule('H2O')
    return atoms

  def surfaces(self,):
    # ----- example
    from ase.build import fcc111, add_adsorbate
    import ase.build
    # This will produce a slab 2x2x3 times the minimal possible size, with a (111) surface in the z direction. A 10 Å vacuum layer is added on each side.
    slab = fcc111(symbol='Al', size=(2, 2, 3), vacuum=10)
    # To set up the same surface with with a hydrogen atom adsorbed in an on-top position 1.5 Å above the top layer:
    ase.build.add_adsorbate(slab, 'H', 1.5, 'ontop')
    # 加入吸附原子后还留10埃真空层 we want to leave 10 Å of vacuum after the adsorbate has been added
    slab.center(vacuum=10.0, axis=2)
    # The atoms in the slab will have tags set to the layer number: First layer atoms will have tag=1, second layer atoms will have tag=2, and so on. Adsorbates get tag=0:
    print(slab.get_tags())

    # ----- fcc: fcc100(), fcc110(), fcc111(), fcc211(), fcc111_root()
    ase.build.fcc111(symbol='Cu', size=(1, 1, 4), a=None, vacuum=None,
                     orthogonal=False,  # 是否创建正交的表面
                     periodic=False)

    # ----- bcc: bcc100(), bcc110(), bcc111() * - bcc111_root()

    # ----- hcp: hcp0001(), hcp10m10(), hcp0001_root()

    # ----- diamond: diamond100(), diamond111()

    # ----- Create root cuts of surfaces
    # To create some more complicated cuts of a standard surface, a root cell generator has been created. While it can be used for arbitrary cells, some more common functions have been provided.
    ase.build.fcc111_root(symbol='Cu', root=3, size=(2, 2, 2), a=None,
                          vacuum=None, orthogonal=False)

    from ase.build import fcc111, root_surface
    atoms = fcc111('Ag', (1, 1, 3))
    atoms = root_surface(atoms, 27)

    # ----- Create specific non-common surfaces
    s1 = ase.build.surface('Au', (2, 1, 1), 9)  # Au(211) surface
    s1.center(vacuum=10, axis=2)

    Mobulk = ase.build.bulk('Mo', 'bcc', a=3.16, cubic=True)
    s2 = ase.build.surface(lattice=Mobulk,
                           # molybdenum bcc(321) surface
                           indices=(3, 2, 1), layers=9)
    s2.center(vacuum=10, axis=2)

    a = 4.0
    Pt3Rh = Atoms('Pt3Rh',
                  scaled_positions=[(0, 0, 0),
                                    (0.5, 0.5, 0),
                                    (0.5, 0, 0.5),
                                    (0, 0.5, 0.5)],
                  cell=[a, a, a],
                  pbc=True)
    # Pt3Rh fcc(211) surfaces will be created:
    s3 = ase.build.surface(Pt3Rh, (2, 1, 1), 9)
    s3.center(vacuum=10, axis=2)

    Pt3Rh.set_chemical_symbols('PtRhPt2')
    s4 = ase.build.surface(Pt3Rh, (2, 1, 1), 9)
    s4.center(vacuum=10, axis=2)

    # ----- Other surface tools: surface(), add_adsorbate(), add_vacuum(), root_surface()

    # ----- interface
    # Example: Create an Ag(110)-Si(110) interface with three atomic layers on each side.
    import ase
    from ase.spacegroup import crystal
    from ase.build.tools import cut, stack

    a_ag = 4.09
    ag = ase.spacegroup.crystal(['Ag'], basis=[(0, 0, 0)], spacegroup=225,
                                cellpar=[a_ag, a_ag, a_ag, 90., 90., 90.])
    ag110 = cut(atoms=ag, a=(0, 0, 3), b=(-1.5, 1.5, 0), nlayers=3)

    a_si = 5.43
    si = crystal(['Si'], basis=[(0, 0, 0)], spacegroup=227,
                 cellpar=[a_si, a_si, a_si, 90., 90., 90.])
    si110 = cut(si, (0, 0, 2), (-1, 1, 0), nlayers=3)

    interface = stack(ag110, si110, maxstrain=1)
    ase.visualize.view(interface)

    # Once more, this time adjusted such that the distance between
    # the closest Ag and Si atoms will be 2.3 Angstrom (requires scipy).
    interface2 = stack(ag110, si110,
                       maxstrain=1, distance=2.3)
    # Optimization terminated successfully.
    ase.visualize.view(interface2)
    pass

  def attach(self,):
    # Attach two structures
    s1 = 'ase.build.attach.attach(atoms1, atoms2, distance, direction=(1, 0, 0), maxiter=50, accuracy=1e-05)'

    # Randomly attach two structures with a given minimal distance
    s2 = "ase.build.attach.attach_randomly(atoms1, atoms2, distance, rng=<module 'numpy.random' from '/tmp/ase-docs/venv/lib/python3.11/site-packages/numpy/random/__init__.py'>)"

    # Randomly attach two structures with a given minimal distance and ensure that these are distributed.
    s3 = "ase.build.attach.attach_randomly_and_broadcast(atoms1, atoms2, distance, rng=<module 'numpy.random' from '/tmp/ase-docs/venv/lib/python3.11/site-packages/numpy/random/__init__.py'>, comm=<ase.parallel.MPI object>)"
    pass

  def mx2(self):
    # (2H or 1T): mx2()
    pass

  def nanotube(self,):
    from ase.build import nanotube
    cnt1 = nanotube(6, 0, length=4)
    cnt2 = nanotube(3, 3, length=6, bond=1.4, symbol='Si')
    pass

  def graphene(self):
    ase.build.graphene(formula='C2', a=2.46, thickness=0.0,
                       size=(1, 1, 1), vacuum=None)
    pass

  def graphene_nanoribbon(self,):
    from ase.build import graphene_nanoribbon
    gnr1 = graphene_nanoribbon(3, 4, type='armchair', saturated=True,
                               vacuum=3.5)
    gnr2 = graphene_nanoribbon(2, 6, type='zigzag', saturated=True,
                               C_H=1.1, C_C=1.4, vacuum=3.0,
                               magnetic=True, initial_mag=1.12)
    pass

  def other_tools(self):
    # cut(), stack(), sort(), minimize_tilt(), niggli_reduce(), rotate(), minimize_rotation_and_translation(), get_deviation_from_optimal_cell_shape(), find_optimal_cell_shape(), make_supercell()
    pass

  def separation(self):
    # connected_indices(), connected_atoms(), separate(), split_bond()
    pass


class AseEos():
  def __init__(self) -> None:
    """The EquationOfState class can be used to find equilibrium volume, energy, and bulk modulus for solids:
    """
    # Equation of state
    pass

  def equation_of_state(self,):
    # example
    # from ase_learn import aseLearn
    # aseLearn.Tutorial_Basic_property_calculations().equation_of_state()
    pass


class AseData():

  def __init__(self,) -> None:
    """ase data module 可用于查看原子的质量 共价键半径等信息
    This module defines the following variables:
    All of these are lists that should be indexed with an atomic number:

    ase.data.atomic_masses
    ase.data.atomic_names
    ase.data.chemical_symbols
    ase.data.covalent_radii
    # ase.data.cpk_colors
    ase.data.reference_states
    ase.data.vdw_radii
    ase.data.atomic_masses_iupac2016
    ase.data.atomic_masses_legacy
    """
    ase.data.atomic_masses
    ase.data.atomic_names
    ase.data.chemical_symbols
    ase.data.covalent_radii
    ase.data.colors.cpk_colors
    ase.data.reference_states
    ase.data.vdw_radii
    ase.data.atomic_masses_iupac2016
    ase.data.atomic_masses_legacy

  def example(self,):
    from ase.data import atomic_numbers, atomic_names, atomic_masses, covalent_radii
    import ase.data
    ase.data.atomic_names[74]
    ase.data.atomic_masses[2]  # 获取元素信息
    import ase.data
    atoms: ase.Atoms = ase.build.bulk('Re')
    print(atoms.cell.get_bravais_lattice())  # 获取晶格信息
    ase.data.reference_states[74]
    ase.data.covalent_radii[74]


class AseStructureOtimization():
  def __init__(self) -> None:
    """https://wiki.fysik.dtu.dk/ase/ase/optimize.html#transition-state-search
    The optimization algorithms can be roughly divided into local optimization algorithms which find a nearby local minimum and global optimization algorithms that try to find the global minimum (a much harder task).

    Local optimization
    The local optimization algorithms available in ASE are: BFGS, BFGSLineSearch, LBFGS, LBFGSLineSearch, GPMin, MDMin and FIRE. Optimizer classes themselves optimize only internal atomic positions. Cell volume and shape can also be optimized in combination with Filter classes. (See Filters for details.)

    Global optimization
    There are currently two global optimisation algorithms available: Basin hopping and Minima hopping
    """
    pass

  def local_optimization_H2O(self, fname_traj='H2O.traj'):
    """https://wiki.fysik.dtu.dk/ase/ase/optimize.html
    The local optimization algorithms available in ASE are: BFGS, BFGSLineSearch, LBFGS, LBFGSLineSearch, GPMin, MDMin and FIRE.
    """
    # The BFGS object is one of the minimizers in the ASE package. The below script uses BFGS to optimize the structure of a water molecule, starting with the experimental geometry: which produces the following output. The columns are the solver name, step number, clock time, potential energy (eV), and maximum force.
    from ase import Atoms
    from ase.optimize import BFGS
    from ase.calculators.emt import EMT
    import numpy as np
    d = 0.9575
    t = np.pi / 180 * 104.51
    water = Atoms('H2O',
                  positions=[(d, 0, 0),
                             (d * np.cos(t), d * np.sin(t), 0),
                             (0, 0, 0)],
                  calculator=EMT())
    dyn = BFGS(water, trajectory=fname_traj,
               restart='qn.pckl')  # restart 可以保存/读取 the Hessian matrix
    dyn.run(fmax=0.05)

    #  可以用于再次优化
    # dyn = BFGS(atoms=water, trajectory='qn.traj', restart='qn.pckl')
    # dyn.replay_trajectory('history.traj')

  def global_optimization(self):
    """There are currently two global optimisation algorithms available.
    Basin hopping, Minima hopping
    """
    def basin_hopping(system):
      """ Tutorial_Global_optimization()

      Args:
          system (_type_): _description_
      """
      Tutorial_Global_optimization()  # 参考这个例子
      # The global optimization algorithm can be used quite similar as a local optimization algorithm:
      import ase.units
      import ase.optimize
      from ase.optimize.basin import BasinHopping
      bh = BasinHopping(atoms=system,         # the system to optimize
                        temperature=100 * ase.units.kB,  # 'temperature' to overcome barriers
                        dr=0.5,               # maximal stepwidth
                        optimizer=ase.optimize.LBFGS,      # optimizer to find local minima
                        fmax=0.1,             # maximal force for the optimizer
                        )
      bh.run(steps=4)

    def minima_hopping():
      # example
      # Make the Pt 110 slab.
      atoms: ase.Atoms = ase.build.fcc100('Pt', (2, 2, 2), vacuum=7.)
      atoms.pbc = True

      # Add the Cu2 adsorbate.
      adsorbate = ase.build.molecule('CO')
      adsorbate.rotate(a=180, v='x')
      ase.build.add_adsorbate(
          slab=atoms, adsorbate=adsorbate, height=2, position='ontop')

      # Constrain the surface to be fixed and a Hookean constraint between
      # the adsorbate atoms.
      constraints = [ase.constraints.FixAtoms(indices=[atom.index for atom in atoms if atom.symbol == 'Pt'],),
                     ase.constraints.Hookean(8, 9, k=10, rt=1.15)]
      atoms.set_constraint(constraints)

      # Set the calculator.
      calc = ase.calculators.emt.EMT()
      atoms.calc = calc
      # calc = ase.calculators.vasp.Vasp(directory='test',prec='low', ediff=1e-3,ispin=1)
      # atoms.calc = calc

      # Instantiate and run the minima hopping algorithm.
      from ase.optimize.basin import BasinHopping
      bh = BasinHopping(atoms=atoms,         # the system to optimize
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

  def Transition_state_search(self):
    """There are several strategies and tools for the search and optimization of transition states available in ASE. The transition state search and optimization algorithms are: ClimbFixInternals, neb and dimer.
    """

    def ClimbFixInternals():
      # Example
      import numpy as np
      # import pytest

      from ase.build import add_adsorbate, fcc100
      from ase.calculators.emt import EMT
      from ase.constraints import FixAtoms, FixInternals
      # from ase.optimize.climbfixinternals import BFGSClimbFixInternals
      from ase.vibrations import Vibrations

      def setup_atoms():
        """Setup transition state search for the diffusion barrier for a Pt atom
        on a Pt surface."""
        atoms = fcc100('Pt', size=(2, 2, 1), vacuum=10.0)
        add_adsorbate(slab=atoms, adsorbate='Pt',
                      height=1.611, position='hollow')
        atoms.set_constraint(FixAtoms(list(range(4))))  # freeze the slab
        return atoms

      # @pytest.mark.optimize
      # @pytest.mark.parametrize('scaling', [0.0, 0.01])
      def test_climb_fix_internals(scaling, testdir):
        """Climb along the constrained bondcombo coordinate while optimizing the
        remaining degrees of freedom after each climbing step.
        For the definition of constrained internal coordinates see the
        documentation of the classes FixInternals and ClimbFixInternals."""
        atoms = setup_atoms()
        atoms.calc = EMT()

        # Define reaction coordinate via linear combination of bond lengths
        reaction_coord = [[0, 4, 1.0], [1, 4, 1.0]]  # 1 * bond_1 + 1 * bond_2
        # Use current value `FixInternals.get_combo(atoms, reaction_coord)`
        # as initial value

        # 'None' will converts to current value
        bondcombo = [None, reaction_coord]
        atoms.set_constraint([FixInternals(bondcombos=[bondcombo])]
                             + atoms.constraints)

        # Optimizer for transition state search along reaction coordinate
        # 以后再说
        'opt = BFGSClimbFixInternals(atoms, climb_coordinate=reaction_coord, optB_fmax_scaling=scaling)'
        opt = ase.optimize.BFGS()  # 我加入的
        opt.run(fmax=0.05)  # Converge to a saddle point

        # Validate transition state by one imaginary vibrational mode
        vib = Vibrations(atoms, indices=[4])
        vib.run()
        assert ((np.imag(vib.get_energies()) > 0)
                == [True, False, False]).all()

    def neb(configs):
      #  我的总结使用 动态cneb, 图像插值时使用 idpp 方法
      neb = ase.neb.DyNEB(  # 动态优化
          images=configs,
          climb=True,  # To use the climbing image NEB method,
          fmax=0.05,
          dynamic_relaxation=True,
          scale_fmax=1,
      )
      neb.interpolate(method='idpp', mic=True)  # 图像插值时使用 idpp 方法

      # The AutoNEB algorithm streamlines the execution of NEB and CI-NEB calculations following the algorithm described in:
      ase.neb.autoneb.AutoNEB()  # ? 没找到

      # Parallelization over images, Create the NEB object with NEB(images, parallel=True).
      # from ase_learn import aseTutorials
      # aseTutorials.AseTutorials_NEB_Surface_diffusion_energy_barriers()
      pass

    def dimmer(self):
      # from ase_learn import aseTutorials
      # aseTutorials.AseTutorials_self_diffusion_on_Al_surface(
      # ).diffusion_along_rows_with_dimmer()
      pass
    pass


class AseMD():
  def __init__(self) -> None:
    # Room temperature simulation (300 Kelvin, Andersen probability: 0.002)
    # dyn = Andersen(atoms, 5 * units.fs, 300, 0.002)
    pass

  def velocity_verlet(self, ):
    # Let us look at the nitrogen molecule as an example of molecular dynamics with the VelocityVerlet algorithm. We first create the VelocityVerlet object giving it the molecule and the time step for the integration of Newton’s law. We then perform the dynamics by calling its run() method and giving it the number of steps to take:

    from ase.md.verlet import VelocityVerlet
    from ase import units
    from ase import Atoms
    import ase.calculators.emt
    # 定义分子对象
    molecule = Atoms('2N', positions=[(0., 0., 0.), (0., 0., 1.10)])
    molecule.calc = ase.calculators.emt.EMT()

    dyn = VelocityVerlet(molecule, dt=1.0 * units.fs, trajectory='test.traj')
    for i in range(10):
      pot = molecule.get_potential_energy()
      kin = molecule.get_kinetic_energy()
      print('%2d: %.5f eV, %.5f eV, %.5f eV' % (i, pot + kin, pot, kin))
      dyn.run(steps=20)

  def analysis(self, traj, timestep):
    import ase.md.analysis
    # This class calculates the Diffusion Coefficient for the given Trajectory using the Einstein Equation:
    ase.md.analysis.DiffusionCoefficient(
        traj, timestep, atom_indices=None, molecule=False)


class AseConstraints():
  def __init__(self) -> None:
    """When performing minimizations or dynamics one may wish to keep some degrees of freedom in the system fixed. One way of doing this is by attaching constraint object(s) directly to the atoms object.

    """
    pass

  def fix_atoms(self, atoms):
    # atoms.set_constraint()
    # You must supply either the indices of the atoms that should be fixed or a mask. The mask is a list of booleans, one for each atom, being true if the atoms should be kept fixed.

    # 固定原子位置 For example, to fix the positions of all the Cu atoms in a simulation with the indices keyword:
    c = ase.constraints.FixAtoms(
        indices=[atom.index for atom in atoms if atom.symbol == 'Cu'])
    atoms.set_constraint(c)
    # or with the mask keyword:
    c = ase.constraints.FixAtoms(mask=[atom.symbol == 'Cu' for atom in atoms])
    atoms.set_constraint(c)

  def fix_bond_length(self, atoms):
    # 固定键长 This class is used to fix the distance between two atoms specified by their indices (a1 and a2)
    c = ase.constraints.FixBondLength(0, 1)
    atoms.set_constraint(c)
    # If fixing multiple bond lengths, use the FixBondLengths class below, particularly if the same atom is fixed to multiple partners.
    c = ase.constraints.FixBondLengths([[0, 1], [0, 2]])
    atoms.set_constraint(c)
    # Here the distances between atoms with indices 0 and 1 and atoms with indices 0 and 2 will be fixed. The constraint is for the same purpose as the FixBondLength class.

  def fix_linear_triatomic(self, atoms):
    # 固定线性三原子 The example below shows how to fix the geometry of two carbon dioxide molecules:
    atoms = molecule('CO2')
    dimer = atoms + atoms.copy()
    c = FixLinearTriatomic(triples=[(1, 0, 2), (4, 3, 5)])
    dimer.set_constraint(c)

    # Fix all Copper atoms to only move in the x-direction:
    from ase.constraints import FixedLine
    c = FixedLine(
        indices=[atom.index for atom in atoms if atom.symbol == 'Cu'],
        direction=[1, 0, 0],
    )
    atoms.set_constraint(c)

  def fix_line(self, atoms):
    # or constrain a single atom with the index 0 to move in the z-direction:
    c = ase.constraints.FixedLine(indices=0, direction=[0, 0, 1])
    atoms.set_constraint(c)

  def fix_plane(self, atoms):
    # Fix all Copper atoms to only move in the yz-plane:
    atoms = ase.build.bulk('Cu', 'fcc', a=3.6)
    c = ase.constraints.FixedPlane(
        indices=[atom.index for atom in atoms if atom.symbol == 'Cu'],
        direction=[1, 0, 0],
    )
    atoms.set_constraint(c)
    # or constrain a single atom with the index 0 to move in the xy-plane:
    c = ase.constraints.FixedPlane(indices=0, direction=[0, 0, 1])
    atoms.set_constraint(c)

  def fix_com(self, atoms):
    """Constraint class for fixing the center of mass.
    """
    # Example of use:
    c = ase.constraints.FixCom()
    atoms.set_constraint(c)

  def hooken(self, atoms):
    c = ase.constraints.Hookean(a1=3, a2=atoms[3].position, rt=0.94, k=2.)
    atoms.set_constraint(c)

  def ExternalForce(self, atoms):
    c = ase.constraints.ExternalForce(0, 1, 0.5)
    atoms.set_constraint(c)

  def combine_constriants(self, atoms):
    # It is possible to supply several constraints on an atoms object. For example one may wish to keep the distance between two nitrogen atoms fixed while relaxing it on a fixed ruthenium surface:
    pos = [[0.00000, 0.00000,  9.17625],
           [0.00000, 0.00000, 10.27625],
           [1.37715, 0.79510,  5.00000],
           [0.00000, 3.18039,  5.00000],
           [0.00000, 0.00000,  7.17625],
           [1.37715, 2.38529,  7.17625]]
    unitcell = [5.5086, 4.7706, 15.27625]

    atoms = Atoms(positions=pos,
                  symbols='N2Ru4',
                  cell=unitcell,
                  pbc=[True, True, False])

    fa = ase.constraints.FixAtoms(mask=[a.symbol == 'Ru' for a in atoms])
    fb = ase.constraints.FixBondLength(0, 1)
    atoms.set_constraint([fa, fb])


class AseFilters():
  def __init__(self) -> None:
    """Constraints can also be applied via filters, which acts as a wrapper around an atoms object. A typical use case will look like this:
    atoms = Atoms(...)
    filter = Filter(atoms, ...)
    dyn = Dynamics(filter, ...)
    """
    pass

  def example(self):
    # Example of use:
    from ase import Atoms, Filter
    atoms = Atoms(positions=[[0, 0, 0],
                             [0.773, 0.600, 0],
                             [-0.773, 0.600, 0]],
                  symbols='OH2')
    f1 = Filter(atoms, indices=[1, 2])
    f2 = Filter(atoms, mask=[0, 1, 1])
    f3 = Filter(atoms, mask=[a.Z == 1 for a in atoms])
    f1.get_positions()
    pass

  def exp_cell_filter(self):
    atoms = Atoms(symbols='Fe')
    ecf = ase.constraints.ExpCellFilter(atoms)
    qn = ase.optimize.QuasiNewton(ecf)
    traj = ase.io.Trajectory('TiO2.traj', 'w', atoms)
    qn.attach(traj)
    qn.run(fmax=0.05)


class AseSpacegroup():
  def __init__(self) -> None:
    pass

  def crystal(self):
    from ase.spacegroup import crystal
    a = 4.05
    al = crystal('Al', [(0, 0, 0)], spacegroup=225,
                 cellpar=[a, a, a, 90, 90, 90])


class AseGui():
  def __init__(self) -> None:
    """图形用户界面可以进行新建模型, 表面 团簇 纳米管等
    """
    pass

  def command_line(self,
                   fname='N2Fe110-path.traj'):
    os.system(f'ase gui {fname}')  # 文件名可以是 ase.io.read() 可读的文件
    # ase gui x.traj@0:10:1  # first 10 images
    # ase gui x.traj@0:10    # first 10 images
    # ase gui x.traj@:10     # first 10 images
    # ase gui x.traj@-10:    # last 10 images
    # ase gui x.traj@0       # first image

    # If you want to select the same range from many files, the you can use the -n or --image-number option:
    # $ ase gui -n -1 *.traj   # last image from all files

    # Writing files¶
    # $ ase gui -n -1 a*.traj -o new.traj

  def interactive_use(self,):
    """ 参见 AseVisualize()
    """
    AseVisualize()

    # Use ase.gui.gui.GUI.repeat_poll() to interact programmatically with the GUI, for example to monitor an ongoing calculation and update the display on the fly.

    # Example to run a movie manually, then quit:
    from ase.collections import g2
    from ase.gui.gui import GUI

    names = iter(g2.names)

    def main(gui):
      try:
        name = next(names)
      except StopIteration:
        gui.window.win.quit()
      else:
        atoms = g2[name]
        gui.images.initialize([atoms])

    gui = GUI()
    gui.repeat_poll(main, 30)
    gui.run()
    pass


class AseLattice():
  def __init__(self) -> None:
    pass

  def Bravais_lattices(self,):

    # Bravais lattice objects, which represent primitive cells and Brillouin zone information which is useful for calculating band structures
    # A general framework for building Atoms objects based Bravais lattice and basis
    # ase.lattice.BravaisLattice()
    from ase.lattice import FCC, MCL
    FCC.name
    FCC.longname
    FCC.pearson_symbol
    MCL.parameters

    pass

  def cubic(self,):
    # 任意方向的晶体
    from ase.lattice.cubic import BodyCenteredCubic
    atoms = BodyCenteredCubic(directions=[[1, 0, 0], [0, 1, 0], [1, 1, 1]],
                              size=(2, 2, 3), symbol='Cu', pbc=(1, 1, 0),
                              latticeconstant=4.0)
    # 正交方向的晶体
    from ase.lattice.cubic import FaceCenteredCubic
    atoms = FaceCenteredCubic(directions=[[1, -1, 0], [1, 1, -2], [1, 1, 1]],
                              size=(2, 2, 3), symbol='Cu', pbc=(1, 1, 0))


class AseCluster():
  def __init__(self) -> None:
    """There are modules for creating nanoparticles (clusters) with a given crystal structure by specifying either the number of layers in different directions, or by making a Wulff construction.
    """
    pass

  def layer_specification(self,
                          surfaces=[(1, 0, 0), (1, 1, 0), (1, 1, 1)],
                          layers=[6, 9, 5],
                          lc=3.61000,
                          ):
    """Layer specification 指定层构建团簇
    This example sets up a nanoparticle of copper in the FCC crystal structure, by specifying 6 layers in the (100) directions, 9 in the (110) directions and 5 in the (111) directions:
    """
    from ase.cluster.cubic import FaceCenteredCubic
    atoms = FaceCenteredCubic('Cu', surfaces=surfaces,
                              layers=layers, latticeconstant=lc)
    return atoms

  def Wulff_construction(self,
                         surfaces=[(1, 0, 0), (1, 1, 0), (1, 1, 1)],
                         esurf=[1.0, 1.1, 0.9],   # Surface energies.
                         lc=3.61000,
                         size=1000,  # Number of atoms
                         structure='fcc',
                         ):
    """To set up a Wulff construction, the surface energies should be specified, in units of energy per area (not energy per atom). The actual unit used does not matter, as only the ratio between surface energies is important. In addition, the approximate size of the nanoparticle should be given. As the Wulff construction is build from whole layers, it is not possible to hit the desired particles size exactly:
    """
    from ase.cluster import wulff_construction
    atoms = wulff_construction('Cu',
                               surfaces=surfaces,
                               energies=esurf,
                               size=size,
                               structure=structure,
                               rounding='above',
                               latticeconstant=lc)
    return atoms

  def possible_crystal_structures(self,):
    import ase.cluster
    import ase.visualize
    # ase.cluster.Cluster()
    # ase.cluster.Decahedron()
    # ase.cluster.Icosahedron()
    # ase.cluster.Octahedron()
    # import ase.cluster
    atoms = ase.cluster.Icosahedron(symbol='W',
                                    noshells=2,  # 13 个原子, noshells=3 为55个原子
                                    latticeconstant=3.14,)
    ase.visualize.view(atoms)
    atoms.get_global_number_of_atoms()
    return atoms


class AseCalculator():
  def __init__(self) -> None:
    """For ASE, a calculator is a black box that can take atomic numbers and atomic positions from an Atoms object and calculate the energy and forces and sometimes also stresses.
    """
    pass

  def supported_calculators(self,):
    """The calculators can be divided in four groups:

    1. Abacus, AMS, Asap, BigDFT, DeePMD-kit, DFTD3, DFTD4, DFTK, FLEUR, GPAW, Hotbit, TBLite, and XTB have their own native or external ASE interfaces.

    2. ABINIT, AMBER, CP2K, CASTEP, deMon2k, DFTB+, ELK, EXCITING, FHI-aims, GAUSSIAN, Gromacs, LAMMPS, MOPAC, NWChem, Octopus, ONETEP, PLUMED, psi4, Q-Chem, Quantum ESPRESSO, SIESTA, TURBOMOLE and VASP, have Python wrappers in the ASE package, but the actual FORTRAN/C/C++ codes are not part of ASE.

    3. Pure python implementations included in the ASE package: EMT, EAM, Lennard-Jones, Morse and HarmonicCalculator.

    4. Calculators that wrap others, included in the ASE package: ase.calculators.checkpoint.CheckpointCalculator, the ase.calculators.loggingcalc.LoggingCalculator, the ase.calculators.mixing.LinearCombinationCalculator, the ase.calculators.mixing.MixedCalculator, the ase.calculators.mixing.SumCalculator, the ase.calculators.mixing.AverageCalculator, the ase.calculators.socketio.SocketIOCalculator, the Grimme-D3 potential, and the qmmm calculators EIQMMM, and SimpleQMMM.
    """
    pass

  def tips(self):
    """Keyword arguments can also be set or changed at a later stage using the set() method:
    ase.calculators.set(key1=value1, key2=value2, ...)
    """

    pass


class AseThermochemistry():
  def __init__(self) -> None:
    """https://wiki.fysik.dtu.dk/ase/ase/thermochemistry/thermochemistry.html#ase.thermochemistry.CrystalThermo.get_entropy
    该模块目前处理四种情况:理想气体极限(考虑平移和旋转自由度)、谐波极限(通常用于吸附，所有自由度都进行谐波处理)、受阻平移/受阻转子模型(用于吸附，两个自由度为平移，一个自由度为旋转，其余3N-3为振动)、以及晶体固体模型(其中N个原子的晶格被视为3N个独立谐振子的系统)。
    """

  def ideal_gas(self, directory='tmp'):
    """IdealGasThermo类通常在能量优化和振动分析之后调用。如果需要熵或自由能，用户需要提供某些参数，例如几何和对称数
    The IdealGasThermo class would generally be called after an energy optimization and a vibrational analysis. The user needs to supply certain parameters if the entropy or free energy are desired, such as the geometry and symmetry number. 

    An example on the nitrogen molecule is:
    """
    from ase.build import molecule
    from ase.calculators.emt import EMT
    from ase.optimize import QuasiNewton
    from ase.thermochemistry import IdealGasThermo
    from ase.vibrations import Vibrations

    atoms = ase.build.molecule('N2')
    # atoms.calc = EMT(directory=directory)
    atoms.pbc = True
    atoms.center(vacuum=4)
    atoms.calc = ase.calculators.vasp.Vasp(directory=directory, xc='pbe')
    dyn = QuasiNewton(atoms)
    dyn.run(fmax=0.01)
    potentialenergy = atoms.get_potential_energy()

    vib = Vibrations(atoms, name=os.path.join(directory, 'vib'))
    vib.run()
    vib_energies = vib.get_energies()

    thermo = IdealGasThermo(vib_energies=vib_energies,
                            potentialenergy=potentialenergy,
                            atoms=atoms,
                            geometry='linear',
                            symmetrynumber=2, spin=0)
    # 获得 gibs 自由能
    G = thermo.get_gibbs_energy(temperature=298.15, pressure=101325.)
    # 获得熵
    S = thermo.get_entropy(temperature=300, pressure=101325)
    # vib_data = vib.get_vibrations()
    return vib
    pass

  def Harmonic_limit(self, vib_energies):
    thermo = ase.thermochemistry.HarmonicThermo(
        vib_energies, potentialenergy=0.0, ignore_imag_modes=False)
    pass

  def hindered_Thermo(self):
    """对于含有N个原子的吸附质，两个自由度被视为平行于表面的两个方向上的受阻平移，一个自由度被视为围绕垂直于表面的轴的受阻旋转，其余的3N-3个自由度被视为振动。HinderedThermo类支持内部能、熵、自由能和零点能的计算
    乙烷在铂(111)表面的一个例子:
    """
    from numpy import array
    from ase.thermochemistry import HinderedThermo

    vibs = array([3049.060670,
                  3040.796863,
                  3001.661338,
                  2997.961647,
                  2866.153162,
                  2750.855460,
                  1436.792655,
                  1431.413595,
                  1415.952186,
                  1395.726300,
                  1358.412432,
                  1335.922737,
                  1167.009954,
                  1142.126116,
                  1013.918680,
                  803.400098,
                  783.026031,
                  310.448278,
                  136.112935,
                  112.939853,
                  103.926392,
                  77.262869,
                  60.278004,
                  25.825447])
    vib_energies = vibs / 8065.54429  # convert to eV from cm^-1
    trans_barrier_energy = 0.049313   # eV
    rot_barrier_energy = 0.017675     # eV
    sitedensity = 1.5e15              # cm^-2
    rotationalminima = 6
    symmetrynumber = 1
    mass = 30.07                      # amu
    inertia = 73.149                  # amu Ang^-2

    thermo = HinderedThermo(vib_energies=vib_energies,
                            trans_barrier_energy=trans_barrier_energy,
                            rot_barrier_energy=rot_barrier_energy,
                            sitedensity=sitedensity,
                            rotationalminima=rotationalminima,
                            symmetrynumber=symmetrynumber,
                            mass=mass,
                            inertia=inertia)
    F = thermo.get_helmholtz_energy(temperature=298.15)
    pass

  def Crystals(self):
    """CrystalThermo类通常会在晶体的能量优化和声子振动分析之后被调用。散装黄金的一个例子是:

    Returns:
        _type_: _description_
    """
    from ase.calculators.emt import EMT
    from ase.optimize import QuasiNewton
    from ase.phonons import Phonons
    from ase.spacegroup import crystal
    from ase.thermochemistry import CrystalThermo
    import ase.phonons
    import ase.thermochemistry

    # Set up gold bulk and attach EMT calculator
    a = 4.078
    atoms = crystal('Au', (0., 0., 0.),
                    spacegroup=225,
                    cellpar=[a, a, a, 90, 90, 90],
                    pbc=(1, 1, 1))
    calc = EMT()
    atoms.calc = calc
    qn = QuasiNewton(atoms)
    qn.run(fmax=0.05)
    potentialenergy = atoms.get_potential_energy()

    # Phonon analysis
    N = 5
    ph = ase.phonons.Phonons(atoms, calc, supercell=(N, N, N), delta=0.05)
    ph.run()
    ph.read(acoustic=True)
    phonon_energies, phonon_DOS = ph.dos(kpts=(40, 40, 40), npts=3000,
                                         delta=5e-4)

    # Calculate the Helmholtz free energy
    thermo = ase.thermochemistry.CrystalThermo(phonon_energies=phonon_energies,
                                               phonon_DOS=phonon_DOS,
                                               potentialenergy=potentialenergy,
                                               formula_units=4)
    F = thermo.get_helmholtz_energy(temperature=298.15)
    pass


# other ----


class Other():
  def __init__(self) -> None:
    pass

  def water_QM(self):
    # 看不懂, 以后再说
    # The following script will calculate the QM/MM single point energy of the water dimer from the S22 database of weakly interacting dimers and complexes, using LDA and TIP3P, for illustration purposes.

    from gpaw import GPAW

    from ase.calculators.qmmm import EIQMMM, Embedding, LJInteractions
    from ase.calculators.tip3p import TIP3P, epsilon0, sigma0
    from ase.data import s22

    # Create system
    atoms = s22.create_s22_system('Water_dimer')
    atoms.center(vacuum=4.0)

    # Make QM atoms selection of first water molecule:
    qm_idx = range(3)

    # Set up interaction & embedding object
    interaction = LJInteractions({('O', 'O'): (epsilon0, sigma0)})
    embedding = Embedding(rc=0.02)  # Short range analytical potential cutoff

    # Set up calculator
    atoms.calc = EIQMMM(qm_idx,
                        GPAW(txt='qm.out'),
                        TIP3P(),
                        interaction,
                        embedding=embedding,
                        vacuum=None,  # if None, QM cell = MM cell
                        output='qmmm.log')

    print(atoms.get_potential_energy())

  def dimensionality_analysis(self):
    # Dimensionality analysis¶
    # This is a example of analysis of the dimensionality of a structure using the ase.geometry.dimensionality.analyze_dimensionality() function. This is useful for finding low-dimensional materials, such as 1D chain-like structures, 2D layered structures, or structures with multiple dimensionality types, such as 1D+3D.

    # The example below creates a layered MoS2 structure and analyzes its dimensionality.
    import ase.build
    from ase.geometry.dimensionality import analyze_dimensionality
    from ase.visualize import view

    atoms = ase.build.mx2(formula='MoS2', kind='2H', a=3.18, thickness=3.19)
    atoms.cell[2, 2] = 7.0
    atoms.set_pbc((1, 1, 1))
    atoms *= 3

    intervals = analyze_dimensionality(atoms, method='RDA')
    m = intervals[0]
    print(sum([e.score for e in intervals]))
    print(m.dimtype, m.h, m.score, m.a, m.b)

    atoms.set_tags(m.components)  # 通过设置标签 这样在显示的时候就可以根据标签给原子上色
    view(atoms)

  def Partly_occupied_Wannier_Functions(self):
    # Partly occupied Wannier Functions
    from gpaw import GPAW
    from ase.build import molecule

    atoms = molecule('C6H6')
    atoms.center(vacuum=3.5)

    calc = GPAW(h=.21, xc='PBE', txt='benzene.txt', nbands=18)
    atoms.calc = calc
    atoms.get_potential_energy()

    calc.set(fixdensity=True, txt='benzene-harris.txt',
             nbands=40, eigensolver='cg', convergence={'bands': 35})
    atoms.get_potential_energy()

    calc.write('benzene.gpw', mode='all')

    # ---
    from gpaw import restart

    from ase.dft.wannier import Wannier

    atoms, calc = restart('benzene.gpw', txt=None)

    # Make wannier functions of occupied space only
    wan = Wannier(nwannier=15, calc=calc)
    wan.localize()
    for i in range(wan.nwannier):
      wan.write_cube(i, 'benzene15_%i.cube' % i)

    # Make wannier functions using (three) extra degrees of freedom.
    wan = Wannier(nwannier=18, calc=calc, fixedstates=15)
    wan.localize()
    wan.save('wan18.json')
    for i in range(wan.nwannier):
      wan.write_cube(i, 'benzene18_%i.cube' % i)

    # ----
    import matplotlib.pyplot as plt
    import numpy as np
    from gpaw import restart
    from ase.dft.wannier import Wannier

    atoms, calc = restart('benzene.gpw', txt=None)
    wan = Wannier(nwannier=18, calc=calc, fixedstates=15, file='wan18.json')

    weight_n = np.sum(abs(wan.V_knw[0])**2, 1)
    N = len(weight_n)
    F = wan.fixedstates_k[0]
    plt.figure(1, figsize=(12, 4))
    plt.bar(range(1, N + 1), weight_n, width=0.65, bottom=0,
            color='k', edgecolor='k', linewidth=None,
            align='center', orientation='vertical')
    plt.plot([F + 0.5, F + 0.5], [0, 1], 'k--')
    plt.axis(xmin=0.32, xmax=N + 1.33, ymin=0, ymax=1)
    plt.xlabel('Eigenstate')
    plt.ylabel('Projection of wannier functions')
    plt.savefig('spectral_weight.png')
    plt.show()

    # ---
    import numpy as np
    from gpaw import GPAW

    from ase import Atoms
    from ase.dft.kpoints import monkhorst_pack

    kpts = monkhorst_pack((13, 1, 1)) + [1e-5, 0, 0]
    calc = GPAW(h=.21, xc='PBE', kpts=kpts, nbands=12, txt='poly.txt',
                eigensolver='cg', convergence={'bands': 9})

    CC = 1.38
    CH = 1.094
    a = 2.45
    x = a / 2.
    y = np.sqrt(CC**2 - x**2)
    atoms = Atoms('C2H2', pbc=(True, False, False), cell=(a, 8., 6.),
                  calculator=calc, positions=[[0, 0, 0],
                                              [x, y, 0],
                                              [x, y + CH, 0],
                                              [0, -CH, 0]])
    atoms.center()
    atoms.get_potential_energy()
    calc.write('poly.gpw', mode='all')

    # ----
    import numpy as np
    from gpaw import restart
    from ase.dft.wannier import Wannier

    atoms, calc = restart('poly.gpw', txt=None)

    # Make wannier functions using (one) extra degree of freedom
    wan = Wannier(nwannier=6, calc=calc, fixedenergy=1.5,
                  initialwannier='orbitals',
                  functional='var')
    wan.localize()
    wan.save('poly.json')
    wan.translate_all_to_cell((2, 0, 0))
    for i in range(wan.nwannier):
      wan.write_cube(i, 'polyacetylene_%i.cube' % i)

    # Print Kohn-Sham bandstructure
    ef = calc.get_fermi_level()
    with open('KSbands.txt', 'w') as fd:
      for k, kpt_c in enumerate(calc.get_ibz_k_points()):
        for eps in calc.get_eigenvalues(kpt=k):
          print(kpt_c[0], eps - ef, file=fd)

    # Print Wannier bandstructure
    with open('WANbands.txt', 'w') as fd:
      for k in np.linspace(-.5, .5, 100):
        ham = wan.get_hamiltonian_kpoint([k, 0, 0])
        for eps in np.linalg.eigvalsh(ham).real:
          print(k, eps - ef, file=fd)

    # ---
    import matplotlib.pyplot as plt
    import numpy as np

    fig = plt.figure(1, dpi=80, figsize=(4.2, 6))
    fig.subplots_adjust(left=.16, right=.97, top=.97, bottom=.05)

    # Plot KS bands
    k, eps = np.loadtxt('KSbands.txt', unpack=True)
    plt.plot(k, eps, 'ro', label='DFT', ms=9)

    # Plot Wannier bands
    k, eps = np.loadtxt('WANbands.txt', unpack=True)
    plt.plot(k, eps, 'k.', label='Wannier')

    plt.plot([-.5, .5], [1, 1], 'k:', label='_nolegend_')
    plt.text(-.5, 1, 'fixedenergy', ha='left', va='bottom')
    plt.axis('tight')
    plt.xticks([-.5, -.25, 0, .25, .5],
               [r'$X$', r'$\Delta$', r'$\Gamma$', r'$\Delta$', r'$X$'], size=16)
    plt.ylabel(r'$E - E_F\  \rm{(eV)}$', size=16)
    plt.legend()
    plt.savefig('bands.png', dpi=80)
    plt.show()


class Ase_EAM_Learn():
  def __init__(self) -> None:
    """Generally all that is required to use this calculator is to supply a potential file or as a set of functions that describe the potential. The files containing the potentials for this calculator are not included but many suitable potentials can be downloaded from The Interatomic Potentials Repository Project at https://www.ctcms.nist.gov/potentials/"""
    pass

  def example(self):
    from ase.calculators.eam import EAM
    import ase.build
    # 画出势的图
    mishin = EAM(potential='../eam_learn/Al99.eam.alloy')
    mishin.plot()
    import matplotlib.pyplot as plt
    plt.ylim(-0.1, 0.1)

    slab = ase.build.fcc100('Al', size=(2, 2, 4), vacuum=10)
    slab.calc = mishin
    slab.get_potential_energy()
    slab.get_forces()
    pass

  def my(self,):
    from ase.calculators.eam import EAM
    import ase.build
    # mishin = EAM(potential='../eam_learn/Al99.eam.alloy')
    mishin = EAM(
        potential='/Users/wangjinlong/my_linux/soft_learn/lammps_learn/potential/MD_pot/WHHe-EAM2.eam.alloy')
    # mishin.plot()
    # import matplotlib.pyplot as plt
    # plt.ylim(-0.1,0.1)

    slab = ase.build.bulk('W')
    # He = ase.atom.Atom('He', position=(0.1,0.1,0.1))
    # ase.build.add_adsorbate(slab, He, position=(0.1,0.1),height=0.1)
    slab.calc = mishin
    slab.get_potential_energy()

  def example_1(self):
    import ase.calculators.eam
    # 创建包含 W 的 Atoms 对象
    a = 3.14
    atoms: ase.Atoms = ase.build.bulk(
        'W', orthorhombic=True, a=a).repeat((4, 4, 4,),)
    atom_He = ase.Atom(symbol='He', position=[a/2, a/4, 0])
    atoms.append(atom_He)

    # # 设置 EAM 计算器并传递势能文件路径
    eam_potential = '/Users/wangjinlong/my_script/sci_research/lmp_use/potential/MD_pot/potential-WHHe-EAM2.eam.alloy'

    atoms.calc = ase.calculators.eam.EAM(potential=eam_potential)
    atoms.get_potential_energy()

    opt = ase.optimize.BFGS(atoms)
    opt.run(fmax=0.05)

    return atoms


class Ase_LennardJones():
  def __init__(self) -> None:
    pass

  def example(self):
    """Lennard-Jones 计算器不支持不同元素之间的相互作用。是吗？
    """
    import ase.calculators.lj
    # 创建体积钨结构
    atoms = ase.build.bulk('W', orthorhombic=True).repeat((4, 4, 4))
    # 设置 Lennard-Jones 计算器
    lj_calculator = ase.calculators.lj.LennardJones(
        epsilon=0.0104, sigma=3.18, rc=10.0, ro=15.0)
    # 将计算器附加到 atoms 对象
    atoms.calc = lj_calculator
    # 计算能量
    atoms.get_potential_energy()


class Ase_MorsePotential():
  def __init__(self) -> None:
    pass

  def example_1(self):
    """在 Morse 势能曲线中，势能 V(r) 的形式为：...
    epsilon=0.0104, 是势能曲线的深度，表示结合能的强度。
    rho0=3.18, 是平衡位置附近的斜率。
    r0=1.0 是平衡位置，即势能曲线的最小点.

    Returns:
        _type_: _description_
    """
    import ase.calculators.morse
    # 创建包含钨（W）的体积结构
    atoms = ase.build.bulk('W', orthorhombic=True).repeat((4, 4, 4))

    # 添加氦（He）原子
    atom_He = ase.Atom(symbol='He', position=(0.3, 0.1, 0))
    atoms.append(atom_He)

    # 设置 Morse 计算器
    morse_calculator = ase.calculators.morse.MorsePotential(
        epsilon=0.0104,
        rho0=3.18,
        r0=1.0
    )

    # 将计算器附加到 atoms 对象
    atoms.calc = morse_calculator

    # 计算能量和力
    energy = atoms.get_potential_energy()
    return atoms


class Ase_harmonic_SpringCalculator():
  def __init__(self) -> None:
    pass

  def example_1(self):
    import ase.calculators.harmonic
    # 创建一个原子对象
    atoms = ase.Atoms('H2', positions=[[0, 0, 0], [0, 0, 1]])

    # 设置弹簧计算器
    ideal_positions = [[0, 0, 0], [0, 0, 0.74]]  # 你需要提供理想平衡位置
    k = -1.0  # 弹簧常数
    lj_calculator = ase.calculators.harmonic.SpringCalculator(
        ideal_positions=ideal_positions, k=k)

    # 将计算器附加到原子对象
    atoms.set_calculator(lj_calculator)

    # 获取势能
    atoms.get_potential_energy()
    pass
