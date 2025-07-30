import ase.constraints
import ase.io.cube
import ase.mep
import ase.spacegroup
import gpaw.jellium
import gpaw.utilities.bader
from gpaw.wannier90 import Wannier90
from gpaw.hybrids.energy import non_self_consistent_energy as nsc_energy
from ase.parallel import paropen as open
import matplotlib.pyplot as plt
import numpy as np
import ase
import ase.build
import ase.optimize
import ase.db
import ase.constraints
import gpaw
import gpaw.calculator
import gpaw.utilities.dos
import ase.parallel
import os
import gpaw.calculator
import gpaw
import ase.io
import ase.optimize
import ase.build
import ase.parallel
import ase.visualize
import gpaw.analyse.hirshfeld
import ase.build
import ase.io.bader
import pickle
import ase.units
import gpaw.wavefunctions.pw
import gpaw.occupations
import ase.visualize.mlab
import gpaw.solvation
import ase.data.vdw
import gpaw.solvation.sjm
import gpaw.utilities.adjust_cell
import gpaw.mpi
import ase.md.verlet


# Tutorial

class AseGpawTutorials():
  def __init__(self) -> None:
    """GPAW 的参数 
    mode='fd': finite-difference 有限差分
    'lcao': linear combinations of pre-calculated atomic orbitals
    """
    pass

  def kpts(self, atoms: ase.Atoms):
    """kpts 取值的经验法则: 
    A rule of thumb for choosing the initial k-point sampling is, that the product, ka, between the number of k-points, k, in any direction, and the length of the basis vector in this direction, a, should be:

    ka ~ 30 Å, for d band metals
    ka ~ 25 Å, for simple metals
    ka ~ 20 Å, for semiconductors
    ka ~ 15 Å, for insulators

    Remember that convergence in this parameter should always be checked.
    """
    # Convergence in number of k-points¶
    for k in [6, 8, 10, 12]:
      calc = gpaw.calculator.GPAW(mode=gpaw.PW(350),
                                  kpts=(k, k, k))
      # calc.set(kpts=(k,k,k))
      energy = atoms.get_potential_energy()
      # ...
    pass

  def parallelization_run(self,):
    """如何进行并行计算
    In order to run GPAW in parallel, you do one of these two:
    $ mpiexec -n <cores> gpaw python script.py
    $ gpaw -P <cores> python script.py
    $ mpiexec -n <cores> python3 script.py
    Tutorial_1_BasicsAndStructureOptimization().atomization_energy()
    # Submitting a job to a queuing system
    # You can write a shell-script that contains this line:
    'mpiexec -np 4 gpaw python script.py'

    # Alternative submit tool
    '$ gpaw-runscript -h'
    # to get the architectures implemented and the available options. As an example, use:
    '$ gpaw-runscript script.py 32'
    """
    Tutorial_1_BasicsAndStructureOptimization().atomization_energy()
    pass

  def Exchange_and_correlation_functionals(self,):
    """xc (str, optional): _description_. Defaults to 'LDA'. where name is a string such as 'LDA', 'PBE' or 'RPBE'.
    """
    pass

  def get_info_from_gpw(self,):
    from gpaw import GPAW
    calc = GPAW('Al-fcc.gpw', txt=None)
    bulk = calc.get_atoms()
    bulk.get_potential_energy()
    density = calc.get_pseudo_density()
    density.max()
    # from mayavi import mlab
    # mlab.contour3d(density)
    # mlab.show()
    pass

  def bulk_Al(self,
              calc,
              fname_db='Al.db',
              ):
    """
    calc=gpaw.calculator.GPAW(mode=gpaw.PW(ecut=350), kpts=(5, 5, 5),
                                        xc='PBE', )
    """

    # 1. 计算原子能
    db = ase.db.connect(fname_db)
    id = db.reserve(system='Al_bulk')
    if id is not None:
      atoms = ase.build.bulk('Al')
      atoms.calc = calc
      natoms = atoms.numbers.__len__()
      pe_atom = atoms.get_potential_energy()/natoms
      db.write(atoms=atoms, id=id, system='Al_bulk', pe_atom=pe_atom)

    atoms: ase.Atoms = db.get_atoms(system='Al_bulk')
    return atoms

  def surface_Al(self,
                 calc,
                 fname_db='Al.db',
                 atoms: ase.Atoms = ase.build.fcc100(
                     symbol='Al', size=(1, 1, 5), vacuum=8),
                 fname_gpw='Al_slab.gpw',
                 ):
    """注意表面的z方向非周期 kpts 只能是 1):
    calc=gpaw.calculator.GPAW(mode=gpaw.PW(ecut=350),
                                           kpts=(5, 5, 1), xc='PBE', 
                                           )
    """

    #  计算 slab 的能量
    db = ase.db.connect(fname_db)
    id = db.reserve(system='Al_slab')
    if id is not None:
      atoms.calc = calc
      calc.write(fname_gpw)
      pe = atoms.get_potential_energy()
      surface_area = atoms.cell.volume / atoms.cell.lengths()[2]
      num_atom = atoms.numbers.__len__()
      db.write(atoms, id=id, system='Al_slab',
               surface_area=surface_area, num_atom=num_atom)
    atoms = db.get_atoms(system='Al_slab')
    return atoms

  def graphene_on_metal(self,):
    from ase import Atoms
    from ase.build import fcc111

    # Lattice parametes of Cu:
    d = 2.56
    a = 2**0.5 * d
    slab: ase.Atoms = ase.build.fcc111('Cu', a=a, size=(1, 1, 4), vacuum=10.0)
    slab.pbc = True

    # Add graphite (we adjust height later):
    slab += ase.Atoms('C2',
                      scaled_positions=[[0, 0, 0],
                                        [1 / 3, 1 / 3, 0]],
                      cell=slab.cell)
    slab.positions[4:6, 2] = slab.positions[3, 2] + d
    slab = slab.repeat((2, 2, 1))
    return slab


class Tutorial_1_BasicsAndStructureOptimization():
  def __init__(self) -> None:
    pass

  def structure_optimization_emt(self,):
    """也称为relaxation 迟豫
    """
    # creates: h2.emt.traj
    import ase.calculators.emt
    import ase.optimize

    system = ase.Atoms('H2', positions=[[0.0, 0.0, 0.0],
                                        [0.0, 0.0, 1.0]])
    # 计算器可以计算原子集合上的能量和力等量。计算器有很多种，EMT是一种特别简单的计算器。
    calc = ase.calculators.emt.EMT()

    system.calc = calc
    # 将创建一个优化器并将其与Atoms对象相关联。它还提供了一个可选参数，轨迹，它指定了一个文件的名称，该文件将保存几何优化中每个步骤的位置。
    opt = ase.optimize.QuasiNewton(system, trajectory='h2.emt.traj')

    opt.run(fmax=0.05)

  def structure_optimization_gpaw(self, fname_traj='h2o.traj'):
    """也称为relaxation 迟豫
    """
    system = ase.build.molecule('H2O')

    # GPAW使用实空间网格来表示密度和波函数，网格存在于一个单元中。因此，必须为Atoms对象设置一个单元格。作为一个粗值，让我们使用6 Ångström单元格:
    system.center(6)

    # 计算器可以计算原子集合上的能量和力等量。
    calc = gpaw.calculator.GPAW(mode='fd')
    system.calc = calc

    # 将创建一个优化器并将其与Atoms对象相关联。它还提供了一个可选参数，轨迹，它指定了一个文件的名称，该文件将保存几何优化中每个步骤的位置。
    opt = ase.optimize.QuasiNewton(system, trajectory=fname_traj)

    opt.run(fmax=0.05)

  def structure_optimization_H2(self,):
    # 首先进行这个计算 获得 H2.gpw
    # web-page: optimization.txt
    molecule, calc = gpaw.restart('H2.gpw', txt='H2-relaxed.txt')
    molecule: ase.Atoms
    e2 = molecule.get_potential_energy()
    d0 = molecule.get_distance(0, 1)

    with ase.parallel.paropen('optimization.txt', 'w') as fd:
      print('experimental bond length:', file=fd)
      print(f'hydrogen molecule energy: {e2:5.2f} eV', file=fd)
      print(f'bondlength              : {d0:5.2f} Ang', file=fd)

      # Find the theoretical bond length:
      relax = ase.optimize.QuasiNewton(molecule, logfile='qn.log')
      relax.run(fmax=0.05)

      # To save time you could have told the minimizer to keep one atom fixed, and only relaxing the other. This is achieved through the use of constraints:
      molecule.set_constraint(ase.constraints.FixAtoms(mask=[0, 1]))

      e2 = molecule.get_potential_energy()
      d0 = molecule.get_distance(0, 1)

      print(file=fd)
      print('PBE energy minimum:', file=fd)
      print(f'hydrogen molecule energy: {e2:5.2f} eV', file=fd)
      print(f'bondlength              : {d0:5.2f} Ang', file=fd)

  def atomization_energy(self,):
    """分子的原子化能, 就是分子的结合能
    并行计算的方法: mpiexec -np 4 gpaw python run.py # 这样也行: mpiexec -np 4 python run.py
    注意 hund 参数

    Returns:
        _type_: _description_
    """

    a = 8.0
    h = 0.2

    energies = {}
    # 避免产生乱码数据
    resultfile = ase.parallel.paropen('results-%.2f.txt' % h, 'w')
    for name in ['H2O', 'H', 'O']:
      system = ase.build.molecule(name)
      system.set_cell((a, a, a))
      system.center()

      if name in ['H', 'O']:
        hund = True
      else:
        hund = False
      # GPAW calculations are by default spin-paired, i.e. the spin-up and spin-down densities are assumed to be equal. As this is not the case for isolated atoms, it will be necessary to instruct GPAW to do something different:
      # With the hund keyword, Hund’s rule is applied to initialize the atomic states, and the calculation will be made spin-polarized.
      calc = gpaw.calculator.GPAW(mode='fd', h=h, hund=hund,
                                  txt=f'gpaw-{name}-{h:.2f}.txt')

      system.calc = calc

      energy = system.get_potential_energy()  # 并行其计算时, 只有这一行并行计算了，其余代码在每个cpu上独立运行
      energies[name] = energy
      print(name, energy, file=resultfile)

    e_atomization = energies['H2O'] - 2 * energies['H'] - energies['O']
    print(e_atomization, file=resultfile)
    return e_atomization

  def calculated_mode(self,):
    """ 
    'fd', 'pw' and 'lcao'
    Memory consumption:
    With LCAO, you have fewer degrees of freedom so memory usage is low. PW mode uses more memory and FD a lot more.

    Speed:
    For small systems with many k-points, PW mode beats everything else. For larger systems LCAO will be most efficient. Whereas PW beats FD for smallish systems, the opposite is true for large systems where FD will parallelize better.

    """
    def fd(atoms,):
      # mode='fd': finite-difference 有限差分
      calc = gpaw.calculator.GPAW(mode='fd', h=0.2)  # 关于h的设置, 参见下面的收敛测试

      # 收敛性测试
      a = 6  # 晶胞大小
      for ngridpoints in [24, 28, ...]:
        h = a / ngridpoints
        calc.set(h=h)  # ngridpoints 列表的选择使得 0.15 < h < 0.25
        energy = atoms.get_potential_energy()

    def lcao():
      #  lcao: linear combinations of pre-calculated atomic orbitals
      # Performing an LCAO calculation requires setting the mode and normally a basis:
      calc = gpaw.calculator.GPAW(mode='lcao',
                                  basis='dzp',
                                  )
      basis = ['sz(dzp)', 'szp(dzp)', 'dzp']

      # 选择合适的basis 函数测试
      for basis in ['sz(dzp)', 'szp(dzp)', 'dzp']:
        calc = gpaw.calculator.GPAW(mode='lcao',
                                    basis=basis,)
        # ...

    def pw():
      # Plane-wave calculations
      # For systems with small unit-cells, it can be much faster to expand the wave-functions in plane-waves. Try running a calculation for a water molecule with a plane-wave cutoff of 350 eV using this:
      from gpaw import GPAW, PW
      k = 4
      calc = GPAW(mode=PW(350), kpts=(k, k, k),)

    pass

  def bulk_Al(self):
    """Bulk Al(fcc) test"""
    name = 'Al-fcc'
    a = 4.05  # fcc lattice parameter
    b = a / 2

    bulk = ase.Atoms('Al',
                     cell=[[0, b, b],
                           [b, 0, b],
                           [b, b, 0]],
                     pbc=True)

    k = 4
    calc = gpaw.calculator.GPAW(mode=gpaw.PW(300),       # cutoff
                                kpts=(k, k, k),     # k-points
                                txt=name + '.txt')  # output file
    bulk.calc = calc

    energy = bulk.get_potential_energy()
    # A tar-file (conventional suffix .gpw) containing binary data such as eigenvalues, electron density and wave functions (see Restart files).
    calc.write(name + '.gpw')

    print('Energy:', energy, 'eV')

  def optimizing_unit_cell_with_stress(self):
    import numpy as np
    from ase.optimize.bfgs import BFGS
    from ase.constraints import UnitCellFilter
    from gpaw import GPAW
    from gpaw import PW

    si = ase.build.bulk('Si', 'fcc', a=6.0)
    # Experimental Lattice constant is a=5.421 A

    si.calc = GPAW(xc='PBE',
                   mode=PW(400, dedecut='estimate'),
                   kpts=(4, 4, 4),
                   # convergence={'eigenstates': 1.e-10},  # converge tightly!
                   txt='stress.txt')

    # Warning: due to difficulties in optimizing cell and positions simultaneously ase.filters.UnitCellFilter may produce incorrect results. Always verify obtained structures by means of performing separate cell (see ase.filters.StrainFilter) and positions optimizations (see ase.optimize). Consider a much more tight fmax than the one used in this tutorial!
    # uf = UnitCellFilter(si)
    # relax = BFGS(uf)
    # 直接使用 UnitCellFilter 可能会出错, 最好是...
    sf = ase.constraints.StrainFilter(si)
    relax = BFGS(sf)
    relax.run(fmax=0.05)  # Consider much tighter fmax!

    a = np.linalg.norm(si.cell[0]) * 2**0.5
    print(f'Relaxed lattice parameter: a = {a} Ang')
    pass

  def equilibrium_lattice_properties(self,):
    """有以下三种方法优化晶格晶胞
    1. 使用 Equation of state module, eos 或者下面的方法
    # 正式计算需要测试 平面波数量(ecut)和 kpots 的收敛参数
    2. 根据应力张量
    3. 其它方法
    """
    # 1. 使用 Equation of state module, 该方法更简便
    from py_package_learn.ase_learn import aseLearn
    aseLearn.Tutorial_Basic_property_calculations(
    ).finding_lattice_constants(method='eos_bcc_fcc')

    # 2. 根据应力张量
    self.optimizing_unit_cell_with_stress()
    # or
    aseLearn.Tutorial_Basic_property_calculations(
    ).finding_lattice_constants(method='tensor')

    # 3. 其它方法
    def traditional_eos():
      from ase import Atoms
      from ase.visualize import view
      from gpaw import GPAW, PW

      for a in [3.9, 4.0, 4.1, 4.2]:
        name = f'bulk-fcc-{a:.1f}'
        b = a / 2
        bulk = Atoms('Al',
                     cell=[[0, b, b],
                           [b, 0, b],
                           [b, b, 0]],
                     pbc=True)

        k = 4
        calc = gpaw.calculator.GPAW(mode=PW(300),       # cutoff
                                    kpts=(k, k, k),     # k-points
                                    txt=name + '.txt')  # output file

        bulk.calc = calc
        energy = bulk.get_potential_energy()
        calc.write(name + '.gpw')

      # 获得体块模量
      'ase gui bulk-*.txt'  # Then choose Tools ‣ Bulk Modulus

    pass


class Tutorial_2_AluminiumSurfac():
  def __init__(self) -> None:
    self.calc = gpaw.GPAW(mode=gpaw.PW(ecut=350), kpts=(
        5, 5, 5), xc='PBE', txt=None)
    pass

  def aluminium_surface(self,):
    pass
    slab: ase.Atoms = ase.build.fcc100('Al', (1, 1, 5), vacuum=10)
    # view(s, repeat=(4, 4, 1))
    return slab

  def surface_energetics(self, fname_db='Al.db'):
    """https://wiki.fysik.dtu.dk/gpaw/tutorialsexercises/structureoptimization/surface/surface.html
    One surface property is the surface tension sigma defined implicitly via: 
    E_N = 2*A*sigma + E_atom # E_atom 是 total energy per bulk atom.
    """
    # 1. 计算钨原子能
    atoms_bulk = AseGpawTutorials().bulk_Al(fname_db=fname_db)
    # 2. 计算 slab 的能量
    atoms_slab = AseGpawTutorials().surface_Al(fname_db=fname_db)

    # 3. 计算
    db = ase.db.connect(fname_db)
    pe_atom = db.get(system='Al_bulk').energy
    pe_slab = db.get(system='Al_slab').energy
    surface_area = db.get(system='Al_slab').surface_area
    natoms = db.get(system='Al_slab').natoms
    surface_energy = (pe_slab - natoms*pe_atom)/(2*surface_area)
    return surface_energy

  def work_function(self,):
    # Read in the 5-layer slab:
    calc = gpaw.calculator.GPAW('slab-5.gpw')
    slab = calc.get_atoms()
    # Get the height of the unit cell:
    L = slab.get_cell()[2, 2]

    # Get the effective potential on a 3D grid:
    v: np.ndarray = calc.get_effective_potential()
    nx, ny, nz = v.shape
    z = np.linspace(0, L, nz, endpoint=False)

    efermi = calc.get_fermi_level()

    # Calculate xy averaged potential:
    vz: np.ndarray = v.mean(axis=0).mean(axis=0)
    print(f'Work function: {vz.max() - efermi:.2f} eV')

    plt.plot(z, vz, label='xy averaged effective potential')
    plt.plot([0, L], [efermi, efermi], label='Fermi level')
    plt.ylabel('Potential / V')
    plt.xlabel('z / Angstrom')
    plt.legend(loc=0)
    # plt.savefig('workfunction.png', format='png')
    plt.show()


class TutorialEnergies():
  def __init__(self) -> None:
    pass

  def atomization_energies(self,):
    """The following script will calculate the atomization energy of a hydrogen molecule:
    spinpol=True,  对于磁性物质设置为True
    hund=True, 对于原子设置为 True 
    """
    # web-page: atomization.txt
    a = 10.  # Size of unit cell (Angstrom)
    c = a / 2

    # Hydrogen atom:
    atom = ase.Atoms('H',
                     positions=[(c, c, c)],
                     magmoms=[0],
                     cell=(a, a + 0.0001, a + 0.0002))  # Break cell symmetry

    # gpaw calculator:
    calc = gpaw.calculator.GPAW(mode=gpaw.PW(),
                                xc='PBE',
                                hund=True,
                                eigensolver='rmm-diis',  # This solver can parallelize over bands
                                occupations=gpaw.FermiDirac(0.0,
                                                            fixmagmom=True),
                                txt='H.out',
                                )
    atom.calc = calc

    e1 = atom.get_potential_energy()
    calc.write('H.gpw')

    # Hydrogen molecule:
    d = 0.74  # Experimental bond length
    molecule = ase.Atoms('H2',
                         positions=([c - d / 2, c, c],
                                    [c + d / 2, c, c]),
                         cell=(a, a, a))

    calc = calc.new(hund=False,  # No hund rule for molecules
                    txt='H2.out')

    molecule.calc = calc
    e2 = molecule.get_potential_energy()
    calc.write('H2.gpw')

    with open('atomization.txt', 'w') as fd:
      print(f'  hydrogen atom energy:     {e1:5.2f} eV', file=fd)
      print(f'  hydrogen molecule energy: {e2:5.2f} eV', file=fd)
      print(f'  atomization energy:       {2 * e1 - e2:5.2f} eV', file=fd)
    pass

  def dft_plus_U(self,):
    """https://wiki.fysik.dtu.dk/gpaw/tutorialsexercises/energetics/hubbardu/hubbardu.html
    """
    from ase import Atoms
    n = Atoms('N', magmoms=[3])
    n.center(vacuum=3.5)

    # Calculation with no +U correction:
    n.calc = gpaw.calculator.GPAW(mode='lcao',
                                  basis='dzp',
                                  txt='no_u.txt',
                                  xc='PBE')
    e1 = n.get_potential_energy()

    # It is also possible to set multiple U corrections to a single element as follows:
    # setups={'Ni':':d,4.0,0;p,2.0,0'}

    # Calculation with a correction U=6 eV normalized:
    n.calc = n.calc.new(setups={'N': ':p,6.0'}, txt='normalized_u.txt')
    e2 = n.get_potential_energy()

    # Calculation with a correction U=6 eV not normalized:
    n.calc = n.calc.new(setups={'N': ':p,6.0,0'}, txt='not_normalized_u.txt')
    e3 = n.get_potential_energy()

    # check
    self.dft_plus_U_check()

  @staticmethod
  def dft_plus_U_check():
    # web-page: gaps.csv
    from ase.io import read
    with open('gaps.csv', 'w') as fd:
      gaps = []
      for name in ['no_u', 'normalized_u', 'not_normalized_u']:
        n = read(name + '.txt')
        calc: gpaw.calculator.GPAW = n.calc
        gap = calc.get_eigenvalues(spin=1)[1] - \
            calc.get_eigenvalues(spin=0)[1]
        gaps.append(gap)
        print(f"{name.replace('_', ' ').replace('u', 'U')}, {gap:.3f}",
              file=fd)

    assert abs(gaps[1] - gaps[0] - 6.0) < 0.8
    with open('gaps.csv') as f:
      content = f.read()
      print(content)

  def formation_energies_of_charged_defects(self,):
    """https://wiki.fysik.dtu.dk/gpaw/tutorialsexercises/energetics/defects/defects.html
    没看懂, 以后再说
    """
    import sys
    from ase import Atoms
    from gpaw import GPAW, FermiDirac

    # Script to get the total energies of a supercell
    # of GaAs with and without a Ga vacancy

    a = 5.628  # Lattice parameter
    # N = int(sys.argv[1])  # NxNxN supercell
    N = 2
    q = -3  # Defect charge

    formula = 'Ga4As4'

    lattice = [[a, 0.0, 0.0],  # work with cubic cell
               [0.0, a, 0.0],
               [0.0, 0.0, a]]

    basis = [[0.0, 0.0, 0.0],
             [0.5, 0.5, 0.0],
             [0.0, 0.5, 0.5],
             [0.5, 0.0, 0.5],
             [0.25, 0.25, 0.25],
             [0.75, 0.75, 0.25],
             [0.25, 0.75, 0.75],
             [0.75, 0.25, 0.75]]

    GaAs = Atoms(symbols=formula,
                 scaled_positions=basis,
                 cell=lattice,
                 pbc=(1, 1, 1))

    GaAsdef = GaAs.repeat((N, N, N))

    GaAsdef.pop(0)  # Make the supercell and a Ga vacancy

    calc = GPAW(mode='fd',
                kpts={'size': (2, 2, 2), 'gamma': False},
                xc='LDA',
                charge=q,
                occupations=FermiDirac(0.01),
                txt='GaAs{0}{0}{0}.Ga_vac.txt'.format(N))

    GaAsdef.calc = calc
    Edef = GaAsdef.get_potential_energy()

    calc.write('GaAs{0}{0}{0}.Ga_vac_charged.gpw'.format(N))

    # Now for the pristine case

    GaAspris = GaAs.repeat((N, N, N))
    parameters = calc.todict()
    parameters['txt'] = 'GaAs{0}{0}{0}.pristine.txt'.format(N)
    parameters['charge'] = 0
    calc = GPAW(**parameters)

    GaAspris.calc = calc
    Epris = GaAspris.get_potential_energy()

    calc.write('GaAs{0}{0}{0}.pristine.gpw'.format(N))
    pass

  def RPA_correlation_energies(self,):
    """https://wiki.fysik.dtu.dk/gpaw/tutorialsexercises/energetics/rpa_tut/rpa_tut.html
    """
    pass

  def cohesive_energy_Si(self):
    """https://wiki.fysik.dtu.dk/gpaw/tutorialsexercises/energetics/rpa_ex/rpa.html
    聚合能= 孤立原子的能量 - 体块中的单原子能量
    The purpose of this exercise is to explore different approximations for the exchange-correlation energy, E_xc
    """
    from ase.build import bulk
    from gpaw import GPAW, FermiDirac
    from gpaw import PW
    import ase.build

    # 计算Si原子能量
    atom_Si = ase.Atoms('Si', pbc=True,)
    atom_Si.center(vacuum=6)
    atom_Si.calc = gpaw.calculator.GPAW(mode=gpaw.PW(350), kpts=(4, 4, 4),
                                        hund=True,
                                        xc='PBE',
                                        # 下面这个参数不懂什么意思, 对结果有影响
                                        # occupations=gpaw.FermiDirac(0.01, fixmagmom=True),
                                        )
    e_atom_Si = atom_Si.get_potential_energy()

    # Do the bulk calculation
    k = 6  # NxNxN k-point sampling, gamma-centred grid
    alat = 5.421  # Si lattice constant
    pwcutoff = 400
    bulk_crystal = ase.build.bulk(
        name='Si', crystalstructure='diamond', a=alat)
    bulk_calc = gpaw.calculator.GPAW(mode=PW(pwcutoff),
                                     # gamma-centred grid
                                     kpts={'size': (k, k, k), 'gamma': True},
                                     xc='PBE',
                                     txt='si.pbe_output.txt',
                                     parallel={'band': 1},
                                     occupations=FermiDirac(0.01)
                                     )

    bulk_crystal.calc = bulk_calc
    e0_bulk_pbe = bulk_crystal.get_potential_energy()

    # 计算聚合能
    e_cohensive = e_atom_Si - 0.5*e0_bulk_pbe
    return e_cohensive

  def extract_exx(self):
    from ase.parallel import paropen
    resultfile = paropen('si.pbe+exx.results.txt', 'a')
    # 抽取交换关联能 Now the exact exchange
    from gpaw.hybrids.energy import non_self_consistent_energy as nsc_energy
    e0_bulk_exx = nsc_energy(calc='bulk.gpw', xcname='EXX')

    s = str(e0_bulk_exx)
    resultfile.write(s)

  def isolate_atom_exx(self,):
    from gpaw.hybrids.energy import non_self_consistent_energy as nsc_energy
    # This calculation is too heavy to run as an exercise!!
    myresults = ase.parallel.paropen('si_atom_exx.txt', 'a')

    # Plane wave cutoff
    pwcutoff = 400.0

    # Do the isolated calculation
    for L in [6.0, 7.0, 8.0]:
      isolated_silicon = ase.Atoms(
          symbols=['Si'],
          positions=[[0.5 * L, 0.5 * L, 0.5 * L]],
          cell=([L, 0, 0], [0, L, 0], [0, 0, L]),
          pbc=(1, 1, 1))

      isolated_calc = gpaw.calculator.GPAW(
          mode=gpaw.PW(pwcutoff, force_complex_dtype=True),
          xc='PBE',
          txt='si_isolated_pbe.txt',
          occupations=gpaw.FermiDirac(0.01, fixmagmom=True),
          spinpol=True,
          hund=True,
          convergence={'density': 1.e-6},
          mixer=gpaw.Mixer(beta=0.05, nmaxold=5, weight=50.0))

      isolated_silicon.calc = isolated_calc

      e0_isolated_pbe = isolated_silicon.get_potential_energy()
      isolated_calc.write('si.pbe+exx.isolated.gpw', mode='all')

      # Now the exact exchange
      si_isolated_exx = nsc_energy('si.pbe+exx.isolated.gpw', 'EXX')

      s = str(L)
      s += ' '
      s += str(e0_isolated_pbe)
      s += ' '
      s += str(si_isolated_exx)
      s += '\n'
      myresults.write(s)
    pass

  def correlation_energies(self):
    from ase import Atoms
    from ase.parallel import paropen
    from gpaw import GPAW
    from gpaw import PW

    resultfile = paropen('H.ralda.DFT_corr_energies.txt', 'w')
    resultfile.write('DFT Correlation energies for H atom\n')

    H = Atoms('H', [(0, 0, 0)])
    H.center(vacuum=2.0)
    calc = GPAW(mode=PW(400, force_complex_dtype=True),
                parallel={'domain': 1},
                hund=True,
                txt='H.ralda_01_lda.output.txt',
                xc='LDA')

    H.calc = calc
    E_lda = H.get_potential_energy()
    E_c_lda = -calc.get_xc_difference('LDA_X')

    resultfile.write(f'LDA correlation: {E_c_lda} eV')
    resultfile.write('\n')

    calc.diagonalize_full_hamiltonian()
    calc.write('H.ralda.lda_wfcs.gpw', mode='all')

    # followed by an RPA calculation:
    from gpaw.xc.rpa import RPACorrelation
    rpa = RPACorrelation('H.ralda.lda_wfcs.gpw',
                         ecut=300,
                         txt='H.ralda_02_rpa_at_lda.output.txt')
    rpa.calculate()

    # and finally one using the rALDA kernel:
    from gpaw.xc.fxc import FXCCorrelation
    fxc = FXCCorrelation('H.ralda.lda_wfcs.gpw',
                         xc='rALDA', txt='H.ralda_03_ralda.output.txt',
                         ecut=300)
    fxc.calculate()
    pass

  def corr_CO(self,):
    """https://wiki.fysik.dtu.dk/gpaw/tutorialsexercises/energetics/fxc_correlation/rapbe_tut.html
    """

    # CO
    CO = ase.Atoms('CO', [(0, 0, 0), (0, 0, 1.1283)])
    CO.center(vacuum=2.7)
    calc = gpaw.calculator.GPAW(mode=gpaw.PW(600, force_complex_dtype=True),
                                symmetry='off',
                                parallel={'domain': 1},
                                xc='PBE',
                                txt='CO.ralda_01_CO_pbe.txt',
                                convergence={'density': 1.e-6})

    CO.calc = calc
    E0_pbe = CO.get_potential_energy()

    E0_hf = nsc_energy(calc, 'EXX').sum()

    calc.diagonalize_full_hamiltonian()
    calc.write('CO.ralda.pbe_wfcs_CO.gpw', mode='all')

    # C

    C = ase.Atoms('C')
    C.set_cell(CO.cell)
    C.center()
    calc = gpaw.calculator.GPAW(mode=gpaw.PW(600, force_complex_dtype=True),
                                symmetry='off',
                                parallel={'domain': 1},
                                xc='PBE',
                                mixer=gpaw.MixerSum(
        beta=0.1, nmaxold=5, weight=50.0),
        hund=True,
        occupations=gpaw.FermiDirac(
        0.01),  # , fixmagmom=True),
        txt='CO.ralda_01_C_pbe.txt',
        convergence={'density': 1.e-6})

    C.calc = calc
    E1_pbe = C.get_potential_energy()

    E1_hf = nsc_energy(calc, 'EXX').sum()

    f = ase.parallel.paropen('CO.ralda.PBE_HF_C.dat', 'w')
    print(E1_pbe, E1_hf, file=f)
    f.close()

    calc.diagonalize_full_hamiltonian()
    calc.write('CO.ralda.pbe_wfcs_C.gpw', mode='all')

    # O

    O = ase.Atoms('O')
    O.set_cell(CO.cell)
    O.center()
    calc = gpaw.calculator.GPAW(mode=gpaw.PW(600, force_complex_dtype=True),
                                symmetry='off',
                                parallel={'domain': 1},
                                xc='PBE',
                                mixer=gpaw.MixerSum(
        beta=0.1, nmaxold=5, weight=50.0),
        hund=True,
        txt='CO.ralda_01_O_pbe.txt',
        convergence={'density': 1.e-6})

    O.calc = calc
    E2_pbe = O.get_potential_energy()

    E2_hf = nsc_energy(calc, 'EXX').sum()

    calc.diagonalize_full_hamiltonian()
    calc.write('CO.ralda.pbe_wfcs_O.gpw', mode='all')

    f = ase.parallel.paropen('CO.ralda.PBE_HF_CO.dat', 'w')
    print('PBE: ', E0_pbe - E1_pbe - E2_pbe, file=f)
    print('HF: ', E0_hf - E1_hf - E2_hf, file=f)
    f.close()

    # Next we calculate the RPA and rAPBE energies for CO with the script
    from ase.parallel import paropen
    from ase.units import Hartree
    from gpaw.xc.rpa import RPACorrelation
    from gpaw.xc.fxc import FXCCorrelation

    fxc0 = FXCCorrelation('CO.ralda.pbe_wfcs_CO.gpw',
                          xc='rAPBE',
                          ecut=400,
                          nblocks=8,
                          txt='CO.ralda_02_CO_rapbe.txt')

    E0_i = fxc0.calculate()

    f = paropen('CO.ralda_rapbe_CO.dat', 'w')
    for ecut, E0 in zip(fxc0.rpa.ecut_i, E0_i):
      print(ecut * Hartree, E0, file=f)
    f.close()

    rpa0 = RPACorrelation('CO.ralda.pbe_wfcs_CO.gpw',
                          ecut=400,
                          nblocks=8,
                          txt='CO.ralda_02_CO_rpa.txt')

    E0_i = rpa0.calculate()

    f = paropen('CO.ralda_rpa_CO.dat', 'w')
    for ecut, E0 in zip(rpa0.ecut_i, E0_i):
      print(ecut * Hartree, E0, file=f)
    f.close()


class TutorialElectronicStructure():
  def __init__(self) -> None:
    """A GPAW calculator gives access to four different kinds of projected density of states:
    Total density of states.
    Molecular orbital projected density of states.
    Atomic orbital projected density of states.
    Wigner-Seitz local density of states.

    gpaw.dos.DOSCalculator(wfs, setups=None, cell=None, shift_fermi_level=True)
    """
    pass

  def dos_calc(self,):
    from ase.build import fcc111, add_adsorbate
    from gpaw import GPAW, PW

    #  Slab with CO:
    slab: ase.Atoms = fcc111('Pt', size=(1, 1, 3))
    add_adsorbate(slab, 'C', 2.0, 'ontop')
    add_adsorbate(slab, 'O', 3.15, 'ontop')
    slab.center(axis=2, vacuum=4.0)
    slab.calc = gpaw.calculator.GPAW(mode=PW(400),
                                     xc='RPBE',
                                     kpts=(12, 12, 1),
                                     convergence={'bands': -10},
                                     txt='top.txt')
    slab.get_potential_energy()
    slab.calc.write('top.gpw', mode='all')

    #  Molecule
    molecule: ase.Atoms = slab[-2:]
    molecule.calc = gpaw.calculator.GPAW(mode=PW(400),
                                         xc='RPBE',
                                         kpts=(12, 12, 1),
                                         txt='CO.txt')
    molecule.get_potential_energy()
    molecule.calc.write('CO.gpw', mode='all')
    pass

  def total_dos(self,):
    # The total density of states can be obtained by the GPAW calculator method get_dos(spin=0, npts=201, width=None).
    # Density of States
    plt.subplot(211)
    slab, calc = gpaw.restart('top.gpw')
    calc: gpaw.calculator.GPAW
    e, dos = calc.get_dos(spin=0, npts=2001, width=0.2)
    e_f = calc.get_fermi_level()
    plt.plot(e - e_f, dos)
    plt.axis([-15, 10, None, 4])
    plt.ylabel('DOS')
    pass

  def pdos_molecular_orbital(self):
    # web-page: pdos.png
    from gpaw import GPAW, restart

    # Density of States
    self.total_dos()
    slab, calc = restart('top.gpw')
    e_f = calc.get_fermi_level()
    calc: gpaw.calculator.GPAW

    # molecule
    molecule = range(len(slab))[-2:]
    plt.subplot(212)
    c_mol = gpaw.calculator.GPAW('CO.gpw')
    for n in range(2, 7):
      print('Band', n)
      # PDOS on the band n
      wf_k = [kpt.psit_nG[n] for kpt in c_mol.wfs.kpt_u]
      P_aui = [[kpt.P_ani[a][n] for kpt in c_mol.wfs.kpt_u]
               for a in range(len(molecule))]
      e, dos = calc.get_all_electron_ldos(mol=molecule, spin=0, npts=2001,
                                          width=0.2, wf_k=wf_k, P_aui=P_aui)
      plt.plot(e - e_f, dos, label='Band: ' + str(n))
    plt.legend()
    plt.axis([-15, 10, None, None])
    plt.xlabel('Energy [eV]')
    plt.ylabel('All-Electron PDOS')
    plt.savefig('pdos.png')
    plt.show()
    pass

  def pdos_molecular_orbital_mod(self):
    """保存 pickle 文件, 由于gpw 通常较大
    """

    slab, calc = gpaw.restart('top.gpw')
    calc: gpaw.calculator.GPAW
    c_mol = gpaw.calculator.GPAW('CO.gpw')
    molecule = range(len(slab))[-2:]
    e_n = []
    P_n = []
    for n in range(c_mol.get_number_of_bands()):
      print('Band: ', n)
      wf_k = [kpt.psit_nG[n] for kpt in c_mol.wfs.kpt_u]
      P_aui = [[kpt.P_ani[a][n] for kpt in c_mol.wfs.kpt_u]
               for a in range(len(molecule))]
      e, P = calc.get_all_electron_ldos(mol=molecule, wf_k=wf_k, spin=0,
                                        P_aui=P_aui, raw=True)
      e_n.append(e)
      P_n.append(P)
    pickle.dump((e_n, P_n), open('top.pickle', 'wb'))

    # 读取 pickle 文件
    e_f = gpaw.calculator.GPAW('top.gpw').get_fermi_level()

    e_n, P_n = pickle.load(open('top.pickle', 'rb'))
    for n in range(2, 7):
      e, ldos = gpaw.utilities.dos.fold(
          e_n[n] * ase.units.Hartree, P_n[n], npts=2001, width=0.2)
      plt.plot(e - e_f, ldos, label='Band: ' + str(n))
    plt.legend()
    plt.axis([-15, 10, None, None])
    plt.xlabel('Energy [eV]')
    plt.ylabel('PDOS')
    plt.show()
    pass

  def pdos_atomic_orbital(self,):
    """available from a GPAW calculator from the method get_orbital_ldos(a, spin=0, angular='spdf', npts=201, width=None).

    参数 angular 的设置可以通过 gpaw.utilities.dos.print_projectors('Au') 查看
    A specific projector function for the given atom can be specified by an integer value for the keyword angular. Specifying a string value for angular, being one or several of the letters s, p, d, and f, will cause the code to sum over all bound state projectors with the specified angular momentum.
    """
    # 计算
    atoms = ase.build.bulk('Au')
    k = 8
    atoms.calc = gpaw.calculator.GPAW(mode='pw',
                                      kpts=(k, k, k))
    atoms.get_potential_energy()
    atoms.calc.write('au.gpw')

    # 画图
    calc = gpaw.calculator.GPAW('au.gpw', txt=None)
    energy, pdos = calc.get_orbital_ldos(a=0, angular='d')
    energy -= calc.get_fermi_level()
    I = np.trapz(pdos, energy)
    center = np.trapz(pdos * energy, energy) / I
    width = np.sqrt(np.trapz(pdos * (energy - center)**2, energy) / I)
    plt.plot(energy, pdos)
    plt.xlabel('Energy (eV)')
    plt.ylabel('d-projected DOS on atom 0')
    plt.title(
        f'd-band center = {center:.1f} eV, d-band width = {width:.1f} eV')
    plt.show()
    # plt.savefig('ag-ddos.png')
    pass

  def ldos_Wigner_Seitz(self, calc, a):
    """(Note: this is currently only implemented for Gamma point calculations, ie. with no k-points.)
    """
    # calc = gpaw.calculator.GPAW('top.gpw')
    # atoms = calc.get_atoms()
    calc.get_wigner_seitz_ldos(a=0, spin=0, npts=201, width=None)  # a=?
    # Integrating over energy gives the number of electrons contained in the region ascribed to atom
    # 获得每个原子的电子数
    calc.get_wigner_seitz_densities(spin=0)
    #  使用bader 方法更先进
    # ChargeAnalysis().method_bader()
    pass

  def pdos_lcao(self):
    name = 'HfS2'
    atoms = ase.build.mx2(formula=name, kind='1T', a=3.648, thickness=2.895,
                          size=(1, 1, 1), vacuum=12.0)
    atoms.center(vacuum=6.0, axis=2)

    h = 0.18
    kx = 9
    ky = 9
    kz = 1

    calc = gpaw.calculator.GPAW(mode='lcao',
                                h=h,
                                kpts={'size': (kx, ky, kz), 'gamma': True},
                                xc='PBE',
                                basis='dzp',
                                parallel={'band': 1},
                                symmetry='off',
                                convergence={'bands': -2},
                                maxiter=600,
                                txt=None,
                                occupations=gpaw.FermiDirac(width=0.01))

    atoms.calc = calc
    atoms.get_potential_energy()
    calc.write(name + '.gpw')

    # plot
    # web-page: lcaodos.png

    name = 'HfS2'
    calc = gpaw.calculator.GPAW(name + '.gpw', txt=None)
    atoms = ase.io.read(name + '.gpw')
    ef = calc.get_fermi_level()

    dos = gpaw.utilities.dos.RestartLCAODOS(calc)
    energies, weights = dos.get_subspace_pdos(range(51))
    e, w = gpaw.utilities.dos.fold(
        energies * ase.units.Hartree, weights, 2000, 0.1)

    e, m_s_pdos = dos.get_subspace_pdos([0, 1])
    e, m_s_pdos = gpaw.utilities.dos.fold(
        e * ase.units.Hartree, m_s_pdos, 2000, 0.1)
    e, m_p_pdos = dos.get_subspace_pdos([2, 3, 4])
    e, m_p_pdos = gpaw.utilities.dos.fold(
        e * ase.units.Hartree, m_p_pdos, 2000, 0.1)
    e, m_d_pdos = dos.get_subspace_pdos([5, 6, 7, 8, 9])
    e, m_d_pdos = gpaw.utilities.dos.fold(
        e * ase.units.Hartree, m_d_pdos, 2000, 0.1)

    e, x_s_pdos = dos.get_subspace_pdos([25])
    e, x_s_pdos = gpaw.utilities.dos.fold(
        e * ase.units.Hartree, x_s_pdos, 2000, 0.1)
    e, x_p_pdos = dos.get_subspace_pdos([26, 27, 28])
    e, x_p_pdos = gpaw.utilities.dos.fold(
        e * ase.units.Hartree, x_p_pdos, 2000, 0.1)

    w_max = []
    for i in range(len(e)):
      if (-4.5 <= e[i] - ef <= 4.5):
        w_max.append(w[i])

    w_max = np.asarray(w_max)

    # Plot things:
    plt.plot(e - ef, w, label='Total', c='k', lw=2, alpha=0.7)
    plt.plot(e - ef, x_s_pdos, label='X-s', c='g', lw=2, alpha=0.7)
    plt.plot(e - ef, x_p_pdos, label='X-p', c='b', lw=2, alpha=0.7)
    plt.plot(e - ef, m_s_pdos, label='M-s', c='y', lw=2, alpha=0.7)
    plt.plot(e - ef, m_p_pdos, label='M-p', c='c', lw=2, alpha=0.7)
    plt.plot(e - ef, m_d_pdos, label='M-d', c='r', lw=2, alpha=0.7)

    plt.axis(ymin=0., ymax=np.max(w_max), xmin=-4.5, xmax=4.5, )
    plt.xlabel(r'$\epsilon - \epsilon_F \ \rm{(eV)}$')
    plt.ylabel('DOS')
    plt.legend(loc=1)
    plt.savefig('lcaodos.png')
    plt.show()

    pass

  def magnetic_structure(self):
    a = 2.87
    m = 2.2

    fe = ase.Atoms('Fe2',
                   scaled_positions=[(0, 0, 0),
                                     (0.5, 0.5, 0.5)],
                   magmoms=[m, m],
                   cell=(a, a, a),
                   pbc=True)

    calc = gpaw.calculator.GPAW(mode=gpaw.PW(350),
                                kpts=(6, 6, 6),
                                txt='ferro.txt',)

    fe.calc = calc
    e = fe.get_potential_energy()
    calc.write('ferro.gpw')

    # 2. dos
    filename = 'ferro.gpw'
    width = 0.2
    calc = gpaw.calculator.GPAW(filename, txt=None)
    ef = calc.get_fermi_level()
    energy, dos = calc.get_dos(spin=0, width=width)
    plt.plot(energy - ef, dos)
    if calc.get_number_of_spins() == 2:
      energy, dos = calc.get_dos(spin=1, width=width)
      plt.plot(energy - ef, dos)
      plt.legend(('up', 'down'), loc='upper left')
    plt.xlabel(r'$\epsilon - \epsilon_F \ \rm{(eV)}$')
    plt.ylabel('Density of States (1/eV)')
    plt.show()

    # 3. pdos
    calc = gpaw.calculator.GPAW('ferro.gpw', txt=None)
    ef = calc.get_fermi_level()

    # Plot s, p, d projected LDOS:
    for c in 'spd':
      energies, ldos = calc.get_orbital_ldos(a=0, spin=0, angular=c, width=0.4)
      plt.plot(energies - ef, ldos, label=c + '-up')

      energies, ldos = calc.get_orbital_ldos(a=0, spin=1, angular=c, width=0.4)
      plt.plot(energies - ef, ldos, label=c + '-down')

    plt.legend()
    plt.show()
    return

  def band_structure(self):
    from ase.build import bulk
    from gpaw import GPAW, PW, FermiDirac

    # Perform standard ground state calculation (with plane wave basis)
    si = bulk('Si', 'diamond', 5.43)
    calc = GPAW(mode=PW(200),
                xc='PBE',
                kpts=(8, 8, 8),
                # random guess (needed if many empty bands required)
                random=True,
                occupations=FermiDirac(0.01),
                txt='Si_gs.txt')
    si.calc = calc
    si.get_potential_energy()
    ef = calc.get_fermi_level()
    calc.write('Si_gs.gpw')

    # Restart from ground state and fix potential:
    calc = gpaw.calculator.GPAW('Si_gs.gpw').fixed_density(
        nbands=16,
        symmetry='off',
        kpts={'path': 'GXWKL', 'npoints': 60},
        convergence={'bands': 8})

    # Finally, the bandstructure can be plotted (using ASE’s band-structure tool ase.spectrum.band_structure.BandStructure):
    bs = calc.band_structure()
    bs.plot(filename='bandstructure.png', show=True, emax=10.0)
    pass

  def band_structure_effect_of_spin_orbit_coupling(self,):
    from ase.build import bulk
    from gpaw import GPAW, PW, FermiDirac
    import numpy as np

    # Non-collinear ground state calculation:
    si: ase.Atoms = ase.build.bulk('Si', 'diamond', 5.43)
    si.calc = gpaw.calculator.GPAW(mode=PW(400),
                                   xc='LDA',
                                   experimental={'magmoms': np.zeros((2, 3)),
                                                 'soc': True},
                                   kpts=(8, 8, 8),
                                   symmetry='off',
                                   occupations=FermiDirac(0.01))
    si.get_potential_energy()

    bp = si.cell.bandpath('LGX', npoints=100)
    bp.plot()

    # Restart from ground state and fix density:
    calc2 = si.calc.fixed_density(
        nbands=16,
        basis='dzp',
        symmetry='off',
        kpts=bp,
        convergence={'bands': 8})

    bs = calc2.band_structure()
    bs = bs.subtract_reference()

    # Zoom in on VBM:
    bs.plot(filename='si-soc-bs.png', show=True, emin=-1.0, emax=0.5)


class Plotting_iso_surfaces_with_Mayavi():
  def __init__(self):
    """从一个立方体文件或从一个波函数或从一个计算器重新启动文件的电子密度中绘制数据：
    * ase.visualization.mlab.plot() 函数可以在命令行中使用：
    - $ python -m ase.visualize.mlab abc.cube
    - $ python -m ase.visualize.mlab -C gpaw abc.gpw
    """
    pass

  def electrostatic_potential(self):
    """
    识别最大值的一种方法是使用等值面（或3d轮廓面），其值略低于最大值。这可以通过外部可视化程序来完成，例如。（参见用Mayavi绘制等值面）：
    # -c后面的参数是两个轮廓面的电位值（最大值为13.4 eV）。
    $ python3 -m ase.visualize.mlab -c 11.1,13.3 mnsi.cube


    Returns:
        _type_: _description_
    """

    ed = Electrostatics_and_dynamics()
    calc = ed.Muon_Site()
    data = calc.get_electrostatic_potential()
    # data.max() 为 13.4
    atoms = calc.get_atoms()
    ase.visualize.mlab.plot(atoms=atoms, data=data,
                            contours=[11.1, 13.3])
    return None


class Electrostatics_and_dynamics():
  def __init__(self) -> None:
    """https://gpaw.readthedocs.io/tutorialsexercises/electrostatics/dipole_correction/dipole.html
    ---
    凝胶是一种具有弹性的半固体物质，由高分子溶液或溶胶在某种条件下粘度增大形成。
    溶剂化凝胶是通过溶剂化过程形成的凝胶。溶剂化过程涉及到溶剂分子与溶质分子之间的相互作用，这种相互作用可以改变溶质分子的性质和行为，从而形成凝胶。
    溶剂化凝胶法是一种制备材料的方法，它涉及将含有高化学活性组分的化合物在溶液中进行均匀混合，并进行水解、缩合化学反应，形成稳定的透明溶胶体系。随后，溶胶经过陈化，胶粒间缓慢聚合，形成三维空间网络结构的凝胶。凝胶网络间充满了失去流动性的溶剂，形成凝胶。最后，通过干燥、烧结固化等步骤，制备出分子乃至纳米亚结构的材料。
    """

    # self.gpawFeatures = gpawLearn.Features()
    pass

  # dipole 偶极修正
  def plot_dipole_example(self, calc: gpaw.calculator.GPAW,
                          name='zero'):
    """用于参考画偶极修正图"""
    # for name in ['zero', 'periodic', 'corrected', 'pwcorrected']:
    # calc = GPAW(name + '.gpw', txt=None)
    efermi = calc.get_fermi_level()
    # Average over y and x:
    v = calc.get_electrostatic_potential().mean(1).mean(0)
    z = np.linspace(0, calc.atoms.cell[2, 2], len(v), endpoint=False)

    plt.figure(figsize=(6.5, 4.5))
    plt.plot(z, v, label='xy-averaged potential')
    plt.plot([0, z[-1]], [efermi, efermi], label='Fermi level')

    if name.endswith('corrected'):
      n = 6  # get the vacuum level 6 grid-points from the boundary
      plt.plot([0.2, 0.2], [efermi, v[n]], 'r:')
      plt.text(0.23, (efermi + v[n]) / 2,
               r'$\phi$ = %.2f eV' % (v[n] - efermi), va='center')
      plt.plot([z[-1] - 0.2, z[-1] - 0.2], [efermi, v[-n]], 'r:')
      plt.text(z[-1] - 0.23, (efermi + v[-n]) / 2,
               r'$\phi$ = %.2f eV' % (v[-n] - efermi),
               va='center', ha='right')

    plt.xlabel(r'$z$, r$\AA$')
    plt.ylabel('(Pseudo) electrostatic potential, V')
    plt.xlim([0., z[-1]])
    if name == 'pwcorrected':
      title = 'PW-mode corrected'
    else:
      title = name.title()
    plt.title(title + ' boundary conditions')
    # plt.savefig(name + '.png')
    return None

  def plot_dipole(self, calc: gpaw.calculator.GPAW,
                  is_save=False,
                  fname_pdf='xxx/electrostatic_potential.pdf'):
    """ * 获得 xy-averaged potential
    """
    efermi = calc.get_fermi_level()
    # Average over y and x:
    v = calc.get_electrostatic_potential().mean(1).mean(0)
    z = np.linspace(0, calc.atoms.cell[2, 2], len(v), endpoint=False)

    plt.figure(figsize=(6.5, 4.5))
    plt.plot(z, v, label='xy-averaged potential')
    plt.plot([0, z[-1]], [efermi, efermi], label='Fermi level')

    plt.xlabel(r'$z$, r$\AA$')
    plt.ylabel('(Pseudo) electrostatic potential, V')
    plt.xlim([0., z[-1]])
    plt.legend()

    # -- 增加文本标记
    n = 6  # get the vacuum level 6 grid-points from the boundary
    plt.plot([0.2, 0.2], [efermi, v[n]], 'r:')
    plt.text(0.23, (efermi + v[n]) / 2,
             r'$\phi$ = %.2f eV' % (v[n] - efermi), va='center')
    plt.plot([z[-1] - 0.2, z[-1] - 0.2], [efermi, v[-n]], 'r:')
    plt.text(z[-1] - 0.23, (efermi + v[-n]) / 2,
             r'$\phi$ = %.2f eV' % (v[-n] - efermi),
             va='center', ha='right')
    # plt.title(' boundary conditions')
    if is_save:
      plt.savefig(fname_pdf)
      print(f'文件保存在-> {fname_pdf}')
    return None

  def Dipole_layer_corrections_example(self,
                                       directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/Dipole_layer_corrections',
                                       name='zero|periodic|corrected|pwcorrected'):
    """Dipole-layer corrections in GPAW
    偶记修正: calc.set(poissonsolver={'dipolelayer': 'xy'})  # z方向为真空层方向
    有了偶记修正, slab的两侧 的功函数才会显著不同, 且可以获得稳定的功函数也就是趋于稳定的值
    """

    def get_atoms():
      slab: ase.Atoms = ase.build.fcc100('Al', (2, 2, 2), a=4.05, vacuum=7.5)
      ase.build.add_adsorbate(slab, 'Na', 4.0)
      slab.center(axis=2)  # slab.pbc : array([ True,  True, False])
      return slab
    slab = get_atoms()

    # 对比偶记修正前后
    # 使用 setups={'Na': '1'} 明确指定 PAW 数据集，可以确保结果的可重复性，因为在不同的 GPAW 版本中，默认 PAW 数据集可能会发生变化。如果你不指定 setups 参数，GPAW 会自动为所有元素选择默认的 PAW 数据集。默认设置通常是一个平衡了计算精度和性能的数据集。
    directory = os.path.join(directory, name)
    calc = gpawLearn.Features().get_calc(directory=directory,
                                         calc_pars_dict={'mode': 'fd',
                                                         'xc': 'PBE',
                                                         'setups': {'Na': '1'},
                                                         'kpts': (4, 4, 1),
                                                         },)
    if name == 'zero':
      pass
    elif name == 'periodic':  # use periodic boundary conditions in all directions:
      slab.pbc = True
    elif name == 'corrected':  # dipole correction:
      slab.pbc = (True, True, False)
      calc.set(poissonsolver={'dipolelayer': 'xy'},)
    elif name == 'pwcorrected':  # 在pw模式下，势必须是周期性的
      calc.set(poissonsolver={'dipolelayer': 'xy'},
               mode='pw',)
    else:
      print(f'name 应该是: zero|periodic|corrected|pwcorrected')
      return
    calc = gpawLearn.Features().calc_single_point_wrapper(atoms=slab,
                                                          calc=calc,)
    return calc

  def Dipole_layer_corrections_example_wrapper(self,
                                               directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/Dipole_layer_corrections',
                                               name='zero|periodic|corrected|pwcorrected'):
    calc = self.Dipole_layer_corrections_example(directory=directory,
                                                 name=name,)
    self.plot_dipole(calc=calc, is_save=True,
                     fname_pdf=os.path.join(directory, name, 'electrostatic_potential.pdf'))
    return calc

  def dipole_layer_corrections(self,
                               slab: ase.Atoms,
                               baisc_calc: gpaw.calculator.GPAW,):
    """Dipole-layer corrections in GPAW
    偶记修正: calc.set(poissonsolver={'dipolelayer': 'xy'})  # z方向为真空层方向
    有了偶记修正, slab的两侧 的功函数才会显著不同, 且可以获得稳定的功函数也就是趋于稳定的值
    """

    # 对比偶记修正前后
    baisc_calc.set(poissonsolver={'dipolelayer': 'xy'},)
    calc = gpawLearn.Features().calc_single_point_wrapper(atoms=slab,
                                                          calc=baisc_calc,)
    self.plot_dipole(calc=calc,
                     is_save=True,
                     fname_pdf=os.path.join(calc.directory,
                                            'electrostatic_potential.pdf'))
    return calc

  # Jellium
  def Jellium_bulk(self,
                   directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/jellium_bulk'):
    """https://gpaw.readthedocs.io/tutorialsexercises/electrostatics/jellium/jellium.html
    - 在计算输出的文本中，可以看到单元格包含0.0527907个电子。
    """

    rs = 5.0 * ase.units.Bohr  # Wigner-Seitz radius
    h = 0.2          # grid-spacing
    a = 8 * h        # lattice constant
    k = 12           # number of k-points (k*k*k)

    ne = a**3 / (4 * np.pi / 3 * rs**3)
    jellium = gpaw.jellium.Jellium(ne)
    bulk = ase.Atoms(pbc=True, cell=(a, a, a))
    calc = gpawLearn.Features().get_calc(directory=directory,
                                         calc_pars_dict={'mode': gpaw.wavefunctions.pw.PW(400.0),
                                                         'background_charge': jellium,
                                                         'xc': 'LDA_X+LDA_C_WIGNER',
                                                         'nbands': 5,
                                                         'kpts': [k, k, k],
                                                         'h': h,
                                                         },
                                         )
    calc = gpawLearn.Features().calc_single_point(atoms=bulk,
                                                  calc=calc,)

    return calc

  def Jellium_surface(self, directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/jellium_surface'):
    """_summary_
    """

    rs = 5.0 * ase.units.Bohr  # Wigner-Seitz radius
    h = 0.2          # grid-spacing
    a = 8 * h        # lattice constant
    v = 3 * a        # vacuum
    L = 10 * a       # thickness
    k = 12           # number of k-points (k*k*1)

    ne = a**2 * L / (4 * np.pi / 3 * rs**3)
    eps = 0.001  # displace surfaces away from grid-points

    jellium = gpaw.jellium.JelliumSlab(ne, z1=v - eps, z2=v + L + eps)

    surf = ase.Atoms(pbc=(True, True, False),
                     cell=(a, a, v + L + v))
    calc = gpawLearn.Features().get_calc(directory=directory,
                                         mode=gpaw.wavefunctions.pw.PW(400.0),
                                         background_charge=jellium,
                                         xc='LDA_X+LDA_C_WIGNER',
                                         eigensolver='dav',
                                         kpts=[k, k, 1],
                                         h=h,
                                         convergence={'density': 0.001},
                                         nbands=int(ne / 2) + 15,
                                         )
    calc = gpawLearn.Features().calc_single_point(atoms=surf,
                                                  calc=calc)
    return calc

  def Jelium_surface_energy(self):
    """这与Lang和Kohn得出的100尔格/厘米的数值相当接近
    """
    # The surface energy is:
    calc1 = self.Jellium_bulk()
    calc2 = self.Jellium_surface()
    e0 = calc1.get_potential_energy()
    e = calc2.get_potential_energy()
    a = 1.6
    L = 10 * a
    sigma = (e - L / a * e0) / 2 / a**2
    print('%.2f mev/Ang^2' % (1000 * sigma))
    print('%.1f erg/cm^2' % (sigma / 6.24150974e-5))
    return None

  def Jelium_electron_density_profile(self):
    """这是电子密度分布图：
    """
    rs = 5.0 * ase.units.Bohr
    calc = gpawLearn.Features().get_calc(
        directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/jellium_surface')
    density = calc.get_pseudo_density()[0, 0]
    h = 0.2
    a = 8 * h
    v = 3 * a
    L = 10 * a
    z = np.linspace(0, v + L + v, len(density), endpoint=False)
    # Position of surface is between two grid points:
    z0 = (v + L - h / 2)
    n = 1 / (4 * np.pi / 3 * rs**3)  # electron density
    kF = (3 * np.pi**2 * n)**(1.0 / 3)
    lambdaF = 2 * np.pi / kF  # Fermi wavelength
    plt.figure(figsize=(6, 6 / 2**0.5))
    plt.plot([-L / lambdaF, -L / lambdaF, 0, 0], [0, 1, 1, 0], 'k')
    plt.plot((z - z0) / lambdaF, density / n)
    # plt.xlim(xmin=-1.2, xmax=1)
    plt.ylim(ymin=0)
    plt.title(r'$r_s=%.1f\ \mathrm{Bohr},\ \lambda_F=%.1f\ \mathrm{Bohr}$' %
              (rs / ase.units.Bohr, lambdaF / ase.units.Bohr))
    plt.xlabel('DISTANCE (FERMI WAVELENGTHS)')
    plt.ylabel('ELECTRON DENSITY')
    # plt.savefig('fig2.png')
    return calc

  #  Bare Coulomb potential for hydrogen
  def Bare_Coulomb_potential_for_hydrogen(self,
                                          directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/Coulomb_potential',
                                          name='ae|paw'):

    h = ase.Atoms('H', cell=(5, 5, 5))
    h.center()

    ecut_list = list(range(200, 1001, 100))
    energy_list = []
    directory = os.path.join(directory, name)
    for ecut in ecut_list:
      fname_gpw = f'H-{ecut}-{name}.gpw'
      fname_txt = f'H-{ecut}-{name}.txt'
      if name == 'ae':
        calc = gpawLearn.Features().get_calc(directory=directory,
                                             setups='ae',
                                             mode=gpaw.wavefunctions.pw.PW(
                                                 ecut),
                                             fname_gpw=fname_gpw,
                                             fname_txt=fname_txt)
      elif name == 'paw':
        calc = gpawLearn.Features().get_calc(directory=directory,
                                             mode=gpaw.wavefunctions.pw.PW(
                                                 ecut),
                                             fname_txt=fname_txt,
                                             fname_gpw=fname_gpw,
                                             )
      else:
        print('name 参数错误')
        return
      calc = gpawLearn.Features().calc_single_point(atoms=h,
                                                    calc=calc,
                                                    fname_gpw=fname_gpw)

      energy_list.append(calc.get_potential_energy())

    energy_array = np.array(energy_list)
    energy_array -= energy_array[-1]
    data = {'ecut_list': ecut_list,
            'energy_array': energy_array,
            'label': name}
    return data

  def Bare_Coulomb_potential_for_hydrogen_plot(self,
                                               data,
                                               fig=None,
                                               ax=None):

    ecut_list = data['ecut_list']
    energy_array = data['energy_array']
    label = data['label']
    if fig is None:
      fig = plt.figure()
      ax = fig.add_subplot()
    ax.plot(ecut_list, energy_array, label=label)
    ax.legend()
    ax.set_xlabel('ecut [eV]')
    ax.set_ylabel('Energy(ecut)- Energy(1000) [eV]')
    return fig, ax

  def Bare_Coulomb_potential_for_hydrogen_wrapper(self):
    data1 = self.Bare_Coulomb_potential_for_hydrogen(name='ae')
    data2 = self.Bare_Coulomb_potential_for_hydrogen(name='paw')
    fig, ax = self.Bare_Coulomb_potential_for_hydrogen_plot(data=data1,)
    fig, ax = self.Bare_Coulomb_potential_for_hydrogen_plot(
        data=data2, fig=fig,
        ax=ax)
    return None
  # Muon Site

  def Muon_Site(self,
                directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/Muon_Site'):
    """ https://gpaw.readthedocs.io/tutorialsexercises/electrostatics/muonsites/mnsi.html
    """

    a = 4.55643
    mnsi = ase.spacegroup.crystal(['Mn', 'Si'],
                                  [(0.1380, 0.1380, 0.1380),
                                   (0.84620, 0.84620, 0.84620)],
                                  spacegroup=198,
                                  cellpar=[a, a, a, 90, 90, 90])

    for atom in mnsi:
      if atom.symbol == 'Mn':
        atom.magmom = 0.5
    from py_package_learn.gpaw_learn import gpawLearn
    gf = gpawLearn.GpawLearn()
    calc = gf.get_calc(directory=directory,
                       xc='PBE',
                       kpts=(2, 2, 2),
                       mode=gpaw.wavefunctions.pw.PW(800),
                       occupations=gpaw.occupations.MethfesselPaxton(
                           width=0.005),
                       )
    calc = gf.calc_single_point(atoms=mnsi,
                                calc=calc,)
    #
    v = calc.get_electrostatic_potential()
    fname_cube = os.path.join(directory, 'gpaw.cube')
    # ASE代码输出一个高斯cube 文件, 具有可以可视化的电势（以eV为单位）的体积数据。
    ase.io.write(fname_cube, images=mnsi, data=v)
    return calc

  def Muon_Site_wrapper(self):
    calc = self.Muon_Site()
    # 使用 mayavi
    # pm = Plotting_iso_surfaces_with_Mayavi()
    # pm.electrostatic_potential()
    # 或者 matplotlib

    mnsi = calc.get_atoms()
    v = calc.get_electrostatic_potential()
    a = mnsi.cell[0, 0]
    n = v.shape[0]
    x = y = np.linspace(0, a, n, endpoint=False)

    f = plt.figure()
    ax = f.add_subplot(111)
    cax = ax.contour(x, y, v[:, :, n // 2], 100)  # 选择中间的值? n=60, n//2 =30
    cbar = f.colorbar(cax)
    ax.set_xlabel('x (Angstrom)')
    ax.set_ylabel('y (Angstrom)')
    ax.set_title('Pseudo-electrostatic Potential')
    # f.savefig('pot_contour.png')
    return None

  # Continuum Solvent Model (CSM)
  def get_calc_water_Continuum_Solvent_Model_complete(
      self,
      directory,
      calc_pars_dict={'mode': 'fd', 'xc':
                      'PBE', 'h': 0.2, },
      fname_gpw='gpaw.gpw',
      fname_txt='gpaw.txt',
      **kwargs,
  ):
    """ 
    from gpaw.solvation import (
        SolvationGPAW,             # the solvation calculator
        EffectivePotentialCavity,  # cavity using an effective potential
        Power12Potential,          # a specific effective potential
        LinearDielectric,  # rule to construct permittivity func from the cavity
        GradientSurface,  # rule to calculate the surface area from the cavity
        SurfaceInteraction  # rule to calculate non-electrostatic interactions
    )

    # all parameters on the user side of the solvation API follow the ASE unit conventions (eV, Angstrom, ...)
    获得水中的溶剂化效应能量 calc 
    """
    # solvent parameters for water from J. Chem. Phys. 141, 174108 (2014)
    u0 = 0.180  # eV
    epsinf = 78.36  # dimensionless
    # convert from dyne / cm to eV / Angstrom**2
    gamma = 18.4 * 1e-3 * ase.units.Pascal * ase.units.m
    T = 298.15  # Kelvin
    vdw_radii = ase.data.vdw.vdw_radii.copy()
    vdw_radii[1] = 1.09

    # atomic_radii expected by gpaw.solvation.Power12Potential have to be a callable mapping an Atoms object to an iterable of floats representing the atomic radii of the atoms in the same order as in the Atoms object (in Angstrom)
    def atomic_radii(atoms):
      return [vdw_radii[n] for n in atoms.numbers]

    cavity = gpaw.solvation.EffectivePotentialCavity(
        effective_potential=gpaw.solvation.Power12Potential(
            atomic_radii, u0),  temperature=T,
        surface_calculator=gpaw.solvation.GradientSurface())
    dielectric = gpaw.solvation.LinearDielectric(epsinf=epsinf)
    interactions = [gpaw.solvation.SurfaceInteraction(surface_tension=gamma)]

    fname_gpw = os.path.join(directory, fname_gpw)
    if os.path.exists(fname_gpw):
      calc = gpaw.solvation.SolvationGPAW(restart=fname_gpw,
                                          directory=directory,)
    else:
      calc = gpaw.solvation.SolvationGPAW(
          **calc_pars_dict,
          directory=directory,
          restart=None,
          txt=os.path.join(directory, fname_txt),
          cavity=cavity,
          dielectric=dielectric,
          interactions=interactions,
      )
      calc.set(**kwargs)

    return calc

  def get_calc_water_Continuum_Solvent_Model(self,
                                             directory,
                                             calc_pars_dict={
                                                 'mode': 'fd',
                                                 'xc': 'PBE',
                                                 'h': 0.2, },
                                             fname_txt='gpaw.txt',
                                             **kwargs,):
    """ 是 get_calc_water_Continuum_Solvent_Model_complete 方法的简化版 
    考虑溶剂化效应
    """

    # fname_gpw = os.path.join(directory, fname_gpw)
    # if os.path.exists(fname_gpw):
    #   calc = gpaw.solvation.SolvationGPAW(restart=fname_gpw,
    #                                       directory=directory,)
    # else:
    #   if not os.path.exists(directory):
    #     os.makedirs(directory, exist_ok=True)
    calc = gpaw.solvation.SolvationGPAW(
        directory=directory,
        txt=os.path.join(directory, fname_txt),
        **calc_pars_dict,  # non-solvent DFT parameters
        # convenient way to use HW14 water parameters:
        **gpaw.solvation.get_HW14_water_kwargs(),
    )
    calc.set(**kwargs)
    return calc

  def continuum_solvent_model_ethanol_in_water(self,
                                               directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/Continuum_Solvent_Model_Ethanol_in_Water',
                                               ):
    """https://gpaw.readthedocs.io/tutorialsexercises/electrostatics/continuum_solvent_model/continuum_solvent_model.html

    """

    # create Atoms object for ethanol and add vacuum
    atoms = ase.build.molecule('CH3CH2OH')
    atoms.center(vacuum=5)
    # non-solvent related DFT parameters
    calc_pars_dict = {'mode': 'fd',
                      'xc': 'PBE',
                      'h': 0.2}
    # 1. perform gas phase calculation
    fname_gpw = 'gas_phase.gpw'
    fname_txt = 'gas_phase.txt'
    calc = gpawLearn.Features().get_calc(
        directory=directory,
        calc_pars_dict=calc_pars_dict,
        fname_gpw=fname_gpw,
        fname_txt=fname_txt,
    )
    calc = gpawLearn.Features().calc_single_point(
        atoms=atoms, calc=calc,
        fname_gpw=fname_gpw)
    Egasphase = calc.get_potential_energy()

    # 2. perform calculation with continuum solvent model from J. Chem. Phys. 141, 174108 (2014)
    fname_gpw = 'inWater.gpw'
    fname_txt = 'inWater.txt'
    calc = self.get_calc_water_Continuum_Solvent_Model(
        directory=directory,
        calc_pars_dict=calc_pars_dict,
        fname_gpw=fname_gpw,
        fname_txt=fname_txt)
    calc = gpawLearn.Features().calc_single_point(
        atoms=atoms, calc=calc,
        fname_gpw=fname_gpw)
    Ewater = calc.get_potential_energy()

    # 3. calculate solvation Gibbs energy in various units
    DGSol_eV = Ewater - Egasphase
    DGSol_kJ_per_mol = DGSol_eV / (ase.units.kJ / ase.units.mol)
    DGSol_kcal_per_mol = DGSol_eV / (ase.units.kcal / ase.units.mol)

    ase.parallel.parprint('calculated Delta Gsol = %.0f meV = %.1f kJ / mol = %.1f kcal / mol' %
                          (DGSol_eV * 1000., DGSol_kJ_per_mol, DGSol_kcal_per_mol))
    return calc

  # Solvated Jellium Method (SJM)
  def get_calc_Solvated_Jellium_Method(self,
                                       directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/Solvated_Jellium_Method/',
                                       sj={'target_potential': 4.2},
                                       fname_txt='gpaw.txt',
                                       fname_gpw='gpaw.gpw',
                                       calc_par_dict={'mode': 'fd',
                                                      'xc': 'PBE',
                                                      'maxiter': 1000,
                                                      'gpts': (16, 16, 136),
                                                      # (9,9,1)
                                                      'kpts': (3, 3, 1),
                                                      },
                                       **kwargs,
                                       ):
    """ https://gpaw.readthedocs.io/tutorialsexercises/electrostatics/sjm/solvated_jellium_method.html
    ---
    恒定电势 
    Perhaps the most-desired use of constant-potential calculations is to find barriers at a specified potential. This avoids a well-known problem in canonical electronic structure calculations, where the work function (that is, the electrical potential) can change by 1–2 V over the course of an elementary step. Such a potential change is obviously much greater than the experimental situation, where potentiostats hold the potential to a tolerance many orders of magnitude smaller. The SJM method allows one to calculate a reaction barrier in a manner where all images in the trajectory have identical work functions, down to a user-specified tolerance.
    也许恒势计算最理想的用途是在特定势下找到势垒。这避免了典型电子结构计算中一个众所周知的问题，即功函数（即电势）在一个基本步骤的过程中可能改变1-2 V。这种电位变化显然比实验情况大得多，在实验情况下，电位器将电位保持在一个小许多数量级的容差范围内。SJM方法允许人们以一种方式计算反应势垒，其中所有的图像在轨迹上具有相同的
    --- 
    - 请记住，必须提供绝对电位，其中SHE电位在绝对标度上的值约为4.4 V。
    - As a simple example, we’ll examine the calculation of a Au slab with a water overlayer calculated at a potential of -0.2 V versus SHE. 我们将研究在-0.2 V与SHE的电位下计算水覆盖层的Au板的计算。
    - sj={'target_potential': 4.2},
    --- 
    Constant-charge mode
    SJM代码还可以在恒荷模式下运行，其中用户指定模拟中的电子总数。这是一种计算系统多个电位的快速方法——也就是说，如果一个人不关心具体的电位，而只想张成一个范围的电位。要使用恒定电荷模式，只需在sj字典中指定过量电子的数量并按正常方式计算: 
    sj = {'excess_electrons': 0.5}
    calc = SJM(sj=sj, ...)
    如果你的意图是在恒定电荷的集合中运行——就像在使用电荷外推方案时一样——你可能想要输出规范能量，而不是大势能。正则能与恒荷模式下的力一致。设置sj['grand_output'] = False，如下所示：
    sj = {'excess_electrons': ...,
      'grand_output': False} :

    """
    fname_gpw = os.path.join(directory, fname_gpw)
    if os.path.exists(fname_gpw):
      calc = gpaw.solvation.sjm.SJM(restart=fname_gpw,
                                    directory=directory,)
    else:
      if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

      # Implicit solvent parameters (to SolvationGPAW).
      epsinf = 78.36  # dielectric constant of water at 298 K
      gamma = 18.4 * 1e-3 * ase.units.Pascal * ase.units.m
      cavity = gpaw.solvation.EffectivePotentialCavity(
          effective_potential=gpaw.solvation.sjm.SJMPower12Potential(
              H2O_layer=True),
          temperature=298.15,  # K
          surface_calculator=gpaw.solvation.GradientSurface())
      dielectric = gpaw.solvation.LinearDielectric(epsinf=epsinf)
      interactions = [gpaw.solvation.SurfaceInteraction(surface_tension=gamma)]

      # The calculator
      calc = gpaw.solvation.sjm.SJM(
          directory=directory,
          # General GPAW parameters.
          txt=os.path.join(directory, fname_txt),
          **calc_par_dict,
          # Solvated jellium parameters.
          sj=sj,  # Desired potential
          # Implicit solvent parameters.
          cavity=cavity,
          dielectric=dielectric,
          interactions=interactions,
          **kwargs,)

    return calc

  def Solvated_Jellium_Method_trace_plot(self,
                                         calc: gpaw.solvation.sjm.SJM):
    fname_cavity = os.path.join(calc.directory,
                                'sjm_traces.out',
                                'cavity.txt')
    fname_background_charge = os.path.join(calc.directory,
                                           'sjm_traces.out',
                                           'background_charge.txt')
    fig, ax = plt.subplots(figsize=(4.6, 2.0))
    fig.subplots_adjust(bottom=0.2, top=0.99, left=0.15, right=0.97)

    data = np.loadtxt(fname=fname_cavity, delimiter=' ')
    ax.plot(data[:, 0], data[:, 1], label='solvent')

    data = np.loadtxt(fname=fname_background_charge,
                      delimiter=' ')
    ax.plot(data[:, 0], data[:, 1], ':', label='jellium')

    # Also add atom dots.
    atoms = calc.get_atoms()
    for atom in atoms:
      ax.plot(atom.z, 0.5, 'k.')

    ax.set_xlabel('$z$')
    ax.set_ylabel('$xy$-averaged value')
    ax.legend()
    # fig.savefig('traces-Au111.png')
    return None

  def Solvated_Jellium_Method_Au111_surface(self,
                                            directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/Solvated_Jellium_Method/'):
    """ https://gpaw.readthedocs.io/tutorialsexercises/electrostatics/sjm/solvated_jellium_method.html
    研究在-0.2 V与SHE的电位下计算水覆盖层的Au板的单点计算。
    ---
    在实践中，由于隐式溶剂的目的只是筛选场，因此净结果（如结合能和势垒高度）对隐式溶剂参数的选择相对不敏感，只要它们保持一致。试着运行下面的脚本来找到平衡功函数到4.2 eV所需的电子数：

    你会注意到 gpaw.txt 中的输出包含额外的信息，与电荷中性的模拟相比：
    Legendre-transformed energies (Omega = E - N mu)
      (grand-potential energies)
      N (excess electrons):   +0.006663
      mu (workfunction, eV):   +4.194593
    --------------------------
    Free energy:    -23.630651
    Extrapolated:   -23.608083
    """

    # Build a tiny gold slab with a single water molecule above.
    atoms: ase.Atoms = ase.build.fcc111('Au', size=(1, 1, 3))
    atoms.center(axis=2, vacuum=12.)
    atoms.translate([0., 0., -4.])
    water = ase.build.molecule('H2O')
    water.rotate('y', 90.)
    water.positions += atoms[2].position + (0., 0., 4.4) - water[0].position
    atoms.extend(water)

    # --

    calc = self.get_calc_Solvated_Jellium_Method(directory=directory,
                                                 )
    # Run the calculation.
    calc: gpaw.solvation.sjm.SJM = gpawLearn.Features().calc_single_point(
        atoms=atoms,
        calc=calc,)
    # 下面这步包含在 calc_single_point 中了
    # if isinstance(calc, gpaw.solvation.sjm.SJM):
    #   fname_sjm_traces = os.path.join(calc.directory, 'sjm_traces.out')
    #   calc.write_sjm_traces(path=fname_sjm_traces)
    #   print(f'文件保存-> {fname_sjm_traces}')
    #   fname_traj = os.path.join(calc.directory, 'gpaw.traj')
    #   atoms.write(fname_traj)
    #   print(f'文件保存-> {fname_traj}')
    self.Solvated_Jellium_Method_trace_plot(calc=calc)
    return calc

  def Solvated_Jellium_Method_Relaxing_the_slab_and_adsorbate(
          self,
          directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/Solvated_Jellium_Method_Relaxing_the_slab_and_adsorbate'):
    """接下来，让我们在恒定电位下进行结构优化。使用与前一个例子相同的系统，但在表面添加一个H原子作为吸附物。
    """

    # Add an H adsorbate.
    atoms = ase.io.read(
        '/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/Solvated_Jellium_Method/gpaw.traj')
    atoms.append(ase.Atom('H', atoms[2].position + (0., 0., 1.5)))
    # Fix some atoms.
    atoms.set_constraint(ase.constraints.FixAtoms(indices=[0, 1]))

    calc = self.get_calc_Solvated_Jellium_Method(
        directory=directory,
        sj={'target_potential': 4.2})
    # Run the calculation.
    calc = gpawLearn.Features().calc_relaxation_general(
        atoms=atoms,
        calc=calc,)

    return calc

  def Solvated_Jellium_Method_Relaxing_the_slab_and_adsorbate_fast_route(
          self,
          directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/Solvated_Jellium_Method_Relaxing_the_slab_and_adsorbate_fast_route'):
    """ 虽然更快但代码更麻烦一些
    - 接下来，让我们在恒定电位下进行结构优化。使用与前一个例子相同的系统，但在表面添加一个H原子作为吸附物。
    - 同时优化结构和潜力往往更快。也就是说，不用等到电势完全平衡后再进行离子步骤，你可以在进行离子步骤的同时调整电子的数量。为此，设置一个宽松的潜在容忍度，并将always_adjust关键字设置为True。下面是一个例子。

    """

    # Add an H adsorbate.
    atoms = ase.io.read(
        '/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/Solvated_Jellium_Method/gpaw.traj')
    atoms.append(ase.Atom('H', atoms[2].position + (0., 0., 1.5)))
    # Fix some atoms.
    atoms.set_constraint(ase.constraints.FixAtoms(indices=[0, 1]))

    # get calc
    sj = {'target_potential': 4.2,
          'tol': 0.2,
          'always_adjust': True}
    calc = self.get_calc_Solvated_Jellium_Method(
        directory=directory,
        sj=sj
    )
    # Run the calculation.

    calc = self.gpawFeatures.calc_relaxation_general(
        atoms=atoms,
        calc=calc,)

    # Tighten the tolerances again.
    sj['tol'] = 0.01
    sj['always_adjust'] = False
    sj['slope'] = None
    calc.set(sj=sj)
    calc = self.gpawFeatures.calc_relaxation_general(
        atoms=atoms,
        calc=calc,)
    return calc

  def Solvated_Jellium_Method_seq_sim_plot(self):
    from matplotlib import pyplot, gridspec

    def makefig():
      fig = pyplot.figure(figsize=(6.5, 6.5))
      grid = gridspec.GridSpec(2, 1, fig, right=0.95, top=0.95)
      smallgrid = gridspec.GridSpecFromSubplotSpec(2, 1, grid[0], hspace=0.)
      ax0 = fig.add_subplot(smallgrid[0])
      ax1 = fig.add_subplot(smallgrid[1], sharex=ax0)
      smallgrid = gridspec.GridSpecFromSubplotSpec(2, 1, grid[1], hspace=0.)
      ax2 = fig.add_subplot(smallgrid[0], sharex=ax0)
      ax3 = fig.add_subplot(smallgrid[1], sharex=ax0)
      return fig, ax0, ax1, ax2, ax3

    def get_data(mode):
      if mode == 'seq':
        directory = '/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/Solvated_Jellium_Method_Relaxing_the_slab_and_adsorbate'

      elif mode == 'sim':
        directory = '/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/Solvated_Jellium_Method_Relaxing_the_slab_and_adsorbate_fast_route/'
      fname_txt = os.path.join(directory, 'gpaw.txt')
      fname_log = os.path.join(directory, 'gpaw.log')

      with open(fname_txt, 'r') as f:
        lines = f.read().splitlines()
      potentials = []
      equilibrateds = []
      fmaxs = []
      for line in lines:
        if 'Potential found to be' in line:
          potentials += [float(line.split('to be')[-1].split('V (with')[0])]
        if 'Potential is within tolerance. Equilibrated.' in line:
          diff = [False] * (len(potentials) - len(equilibrateds))
          diff[-1] = True
          equilibrateds.extend(diff)
      with open(fname_log, 'r') as f:
        lines = f.read().splitlines()
      for line in lines:
        if 'BFGS:' in line:
          fmaxs += [float(line.split()[-1])]
      return potentials, equilibrateds, fmaxs

    def plot_data(potentials, equilibrateds, fmaxs, axes):
      fmax_indices = []
      axes[0].plot(potentials, 'o-', color='k', markerfacecolor='w')
      for index, (potential, equilibrated) in enumerate(zip(potentials,
                                                            equilibrateds)):
        if equilibrated:
          axes[0].plot(index, potential, 'og', markeredgecolor='k')
          fmax_indices += [index]
      axes[1].plot(fmax_indices, fmaxs, 'ko-')

    def prune_duplicate(potentials, equilibrateds):
      """Due to logging, there's a duplicate potential reading when
      we switched from simultaneous to sequential. Remove it, and also
      return the image number of the switch."""
      for index, potential in enumerate(potentials):
        if index > 0 and potential == potentials[index - 1]:
          duplicate = index
      del potentials[duplicate]
      del equilibrateds[duplicate]
      return duplicate

    def shade_plot(ax, xstart):
      xlim = ax.get_xlim()
      ylim = ax.get_ylim()
      ax.fill_between(x=[xstart, xlim[-1]], y1=[ylim[0]] * 2, y2=[ylim[1]] * 2,
                      color='0.8')
      ax.set_xlim(xlim)
      ax.set_ylim(ylim)

    fig, ax0, ax1, ax2, ax3 = makefig()
    potentials, equilibrateds, fmaxs = get_data('seq')
    plot_data(potentials, equilibrateds, fmaxs, [ax0, ax1])
    potentials, equilibrateds, fmaxs = get_data('sim')
    # duplicate = prune_duplicate(potentials, equilibrateds)
    plot_data(potentials, equilibrateds, fmaxs, [ax2, ax3])
    ax3.set_xlabel('DFT calculation')
    ax0.text(0.20, 0.75, 'sequential', transform=ax0.transAxes)
    ax2.text(0.20, 0.75, 'simultaneous', transform=ax2.transAxes)
    ax2.text(0.75, 0.75, '(sequential)', transform=ax2.transAxes)
    duplicate = 13
    shade_plot(ax2, duplicate - 0.5)
    shade_plot(ax3, duplicate - 0.5)
    for ax in [ax0, ax2]:
      ax.set_ylabel(r'$\phi$, V')
    for ax in [ax1, ax3]:
      ax.set_ylabel(r'max force, eV/$\mathrm{\AA}$')

    # fig.savefig('simultaneous.png')

    pass

  def Solvated_Jellium_Method_Finding_a_barrier_get_final_state(
      self,
      directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/Solvated_Jellium_Method_Finding_a_barrier_get_final_state',
  ):
    """创建最终状态, H 由 top 跑到 hollow
    """

    if os.path.exists(os.path.join(directory, 'gpaw-1.gpw')):
      # atoms = ase.io.read(fname_traj)
      calc = gpawLearn.Features().get_calc_from_gpw_file(
          directory=directory,
          fname_gpw='gpaw-1.gpw')
      return calc

    # Open the previous simulation and move the H to a hollow site.
    calc = self.Solvated_Jellium_Method_Relaxing_the_slab_and_adsorbate_fast_route()
    atoms = calc.get_atoms()
    atoms[6].x = atoms[0].x
    atoms[6].y = atoms[0].y

    # ---
    # Solvated jellium parameters.
    sj = {'target_potential': 4.2,
          'tol': 0.2,
          'always_adjust': True,
          'excess_electrons': -0.01232,  # guess from previous
          'slope': -50.}  # guess from previous
    calc = self.get_calc_Solvated_Jellium_Method(directory=directory,
                                                 sj=sj,)
    calc = self.gpawFeatures.calc_relaxation_general(atoms=atoms,
                                                     calc=calc,)

    # Tighten the tolerances again.
    sj['tol'] = 0.01
    sj['always_adjust'] = False
    sj['slope'] = None
    calc.set(sj=sj)
    calc = self.gpawFeatures.calc_relaxation_general(atoms=atoms,
                                                     calc=calc,
                                                     fname_gpw='gpaw-1.gpw',
                                                     fname_log='gpaw-1.log')

    return calc

  def solvated_Jellium_Method_Finding_a_barrier(
          self,
          directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/Solvated_Jellium_Method_Finding_a_barrier',
          n_images=5,
  ):
    """https://gpaw.readthedocs.io/tutorialsexercises/electrostatics/sjm/solvated_jellium_method.html
    也许恒势计算最理想的用途是在特定势下找到势垒。这避免了典型电子结构计算中一个众所周知的问题，即功函数（即电势）在一个基本步骤的过程中可能改变1-2 V。这种电位变化显然比实验情况大得多，在实验情况下，电位器将电位保持在一个小许多数量级的容差范围内。SJM方法允许人们以一种方式计算反应势垒，其中所有的图像在轨迹上具有相同的功函数，直至用户指定的公差。
    """

    def make_calculator(index,
                        directory,):
      # Solvated jellium parameters.
      sj = {'target_potential': 4.2,
            'tol': 0.01,
            'excess_electrons': -0.01232,  # guess from previous
            'slope': -50.}  # guess from previous
      # Implicit solvent parameters (to SolvationGPAW).
      calc = self.get_calc_Solvated_Jellium_Method(
          directory=directory,
          sj=sj,
          fname_txt=f'gpaw-{index:d}.txt')
      return calc

    # Create the band of images, attaching a calc to each.
    calc_initial = self.Solvated_Jellium_Method_Relaxing_the_slab_and_adsorbate_fast_route()
    calc_final = self.Solvated_Jellium_Method_Finding_a_barrier_get_final_state()
    initial = calc_initial.get_atoms()
    final = calc_final.get_atoms()

    # neb
    images = [initial]
    for index in range(n_images):
      images += [initial.copy()]
      images[-1].calc = make_calculator(index + 1, directory=directory)
    images += [final]
    ase.mep.interpolate(images)
    # Create and relax the DyNEB.
    neb = ase.mep.DyNEB(images)

    gpawLearn.Features().AseFeatures.TSTcalc.run_neb(
        neb_instance=neb,
        directory=directory,
        opt_name='bfgs',
    )
    gpawLearn.Features().AseFeatures.TSTcalc.analysis_neb(
        fname_traj=os.path.join(directory, 'neb.traj'), nimages=n_images)
    return None

  # ---
  def static_polarizabilty_in_finite_systems(self,
                                             directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/static_polarizabilty_in_finite_systems',
                                             ):
    """https://gpaw.readthedocs.io/tutorialsexercises/electrostatics/polarizabilty/polarizabilty.html
    Let us calculate the static polarizability of the water molecule.
    """

    atoms = ase.build.molecule('H2O')
    gpaw.utilities.adjust_cell.adjust_cell(atoms, border=3)
    calc = gpawLearn.Features().get_calc(directory=directory,
                                         mode='fd',)
    alpha_cc = gpawLearn.Features().calc_polarizability_tensor(
        atoms=atoms,
        calc=calc,
        fname_polarizability_tensor=os.path.join(
            directory, 'polarizability_tensor')
    )

    return alpha_cc


class MagneticProperties():
  def __init__(self):
    pass

  def Zero_field_splitting(self):
    """https://gpaw.readthedocs.io/tutorialsexercises/magnetic/zfs/zfs.html
    """
    pass

  def electron_spin_and_magnetic_structure(self,
                                           directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/electron_spin_and_magnetic_structure'):
    """https://gpaw.readthedocs.io/tutorialsexercises/magnetic/iron/iron.html
    没有详细的指导
    """
    a = 2.87
    m = 2.2

    fe = ase.Atoms('Fe2',
                   scaled_positions=[(0, 0, 0),
                                     (0.5, 0.5, 0.5)],
                   magmoms=[m, m],
                   cell=(a, a, a),
                   pbc=True)
    gf = gpawLearn.Features()
    calc = gf.get_calc(directory=directory,
                       mode=gpaw.wavefunctions.pw.PW(350),
                       kpts=(6, 6, 6),
                       )
    calc = gf.calc_single_point(atoms=fe,
                                calc=calc,)

    # calc = gpaw.calculator.GPAW(mode=gpaw.wavefunctions.pw.PW(350),
    #                             kpts=(6, 6, 6),
    #                             txt='ferro.txt')
    # fe.calc = calc
    # e = fe.get_potential_energy()
    # calc.write('ferro.gpw')
    return calc

  def electron_spin_and_magnetic_structure_compare(self):
    print('state    LDA        PBE')
    for name in ['ferro', 'anti', 'non']:
      calc = gpaw.calculator.GPAW(name + '.gpw', txt=None)
      atoms = calc.get_atoms()
      eLDA = atoms.get_potential_energy()
      deltaxc = calc.get_xc_difference('PBE')
      ePBE = eLDA + deltaxc

      if name == 'ferro':
        eLDA0 = eLDA
        ePBE0 = ePBE

      eLDA -= eLDA0
      ePBE -= ePBE0
      print(('%-5s: %7.3f eV %7.3f eV' % (name, eLDA, ePBE)))

    pass


class MolecularDynamics():
  def __init__(self) -> None:
    """https://wiki.fysik.dtu.dk/ase/tutorials/neb/diffusion.html#diffusion-tutorial
    """
    pass

  def get_neb_instance_gpaw_serial(self,
                                   initial: ase.Atoms,
                                   final: ase.Atoms,
                                   directory='xxx/neb',
                                   nimages=3,
                                   neb_method='string',
                                   calc_pars_dict={},
                                   **kwargs,
                                   ):
    """ 推荐使用 dyneb 
    """

    if not os.path.exists(directory):
      os.makedirs(directory, exist_ok=True)

    images = [initial]
    for i in range(nimages):
      image = initial.copy()
      calc = gpaw.calculator.GPAW(txt=os.path.join(directory,
                                                   f'neb{i+1:d}.txt'),
                                  parallel=False,
                                  **initial.calc.parameters,
                                  )
      calc.set(**calc_pars_dict)
      calc.set(**kwargs)
      image.calc = calc

      images.append(image)
    images.append(final)
    # ---
    neb_instance = ase.mep.DyNEB(images=images,
                                 parallel=False,
                                 climb=True,
                                 method=neb_method)
    neb_instance.interpolate(method='idpp',)
    return neb_instance

  def get_neb_instance_gpaw_parallel(self,
                                     initial: ase.Atoms,
                                     final: ase.Atoms,
                                     directory='xxx/neb',
                                     nimages=3,
                                     neb_method='string',
                                     climb=True,
                                     calc_pars_dict={},
                                     **kwargs,
                                     ):
    """并行不能使用 dyneb 

    Args:
        initial (ase.Atoms): _description_
        final (ase.Atoms): _description_
        directory (str, optional): _description_. Defaults to 'xxx/neb'.
        nimages (int, optional): _description_. Defaults to 3.
        neb_method (str, optional): _description_. Defaults to 'string'.
        climb (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    if not os.path.exists(directory):
      os.makedirs(directory, exist_ok=True)

    n = gpaw.mpi.size // nimages      # number of cpu's per image
    j = 1 + gpaw.mpi.rank // n  # my image number
    assert nimages * n == gpaw.mpi.size

    images = [initial]
    for i in range(nimages):
      ranks = list(range(i * n, (i + 1) * n))  # range(i * n, (i + 1) * n)
      image = initial.copy()
      if gpaw.mpi.rank in ranks:
        calc = gpaw.calculator.GPAW(txt=os.path.join(directory, f'neb{j}.txt'),
                                    communicator=ranks,
                                    **initial.calc.parameters,
                                    )
        calc.set(**calc_pars_dict)
        calc.set(**kwargs)
        image.calc = calc

      image.set_constraint(initial.constraints)
      images.append(image)
    images.append(final)
    # ---
    neb_instance = ase.mep.NEB(images=images,
                               parallel=True,
                               climb=climb,
                               method=neb_method)
    neb_instance.interpolate(method='idpp',)
    return neb_instance

  def NEB_calculations_parallelized_over_images_get_IF(
      self,
      directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/NEB_calculations_parallelized_over_images'
  ):

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
    gf = gpawLearn.GpawLearn()
    calc = gf.get_calc(directory=directory,
                       mode='fd',
                       fname_gpw='initial.gpw',
                       fname_txt='initial.log')
    calc = gf.calc_relaxation_general(atoms=slab,
                                      calc=calc,
                                      fname_gpw='initial.gpw',
                                      fname_traj='initial.traj',
                                      fname_log='initial_relax.log')

    # Final state:
    slab[-1].x += slab.get_cell()[0, 0] / 2
    calc = gf.get_calc(directory=directory,
                       mode='fd',
                       fname_gpw='final.gpw',
                       fname_txt='final.log')
    calc = gf.calc_relaxation_general(atoms=slab,
                                      calc=calc,
                                      fname_gpw='final.gpw',
                                      fname_traj='final.traj',
                                      fname_log='final_relax.log')
    return None

  def NEB_calculations_parallelized_over_images_parallel(
          self,
          directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/NEB_calculations_parallelized_over_images'):
    ase.parallel.parprint(
        '不能直接单核运行, 需要写入到脚本, 并行计算. 参见-> self.NEB_calculations_parallelized_over_images_parallel_wrapper')
    initial = ase.io.read(os.path.join(directory, 'initial.traj'))
    final = ase.io.read(os.path.join(directory, 'final.traj'))

    directory = os.path.join(directory, 'neb')
    neb = self.get_neb_instance_gpaw_parallel(initial=initial,
                                              final=final,
                                              directory=directory,
                                              nimages=3,
                                              )
    # calc
    gf = gpawLearn.GpawLearn()
    gf.TSTcalc.run_neb(neb_instance=neb,
                       directory=directory,
                       opt_name='bfgs')

    return None

  def NEB_calculations_parallelized_over_images_parallel_wrapper(
          self,
          fname_py='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/NEB_calculations_parallelized_over_images/neb/run.py'):
    def run():
      from py_package_learn.gpaw_learn import gpawLearn
      md = gpawLearn.GpawLearn().gpawTutorial.MolecularDynamics()
      md.NEB_calculations_parallelized_over_images_parallel()

    gpawLearn.GpawLearn().write_py_from_code(func=run,
                                             fname_py=fname_py)
    print(f'在终端运行: mpirun -np 6 gpaw python {fname_py}')
    return None

  def NEB_calculations_parallelized_over_images_serial(
          self,
          directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/NEB_calculations_parallelized_over_images/neb_serial',
          nimages=3):
    if_dir = '/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/NEB_calculations_parallelized_over_images'
    initial = ase.io.read(os.path.join(if_dir, 'initial.traj'))
    final = ase.io.read(os.path.join(if_dir, 'final.traj'))

    # neb
    neb = self.get_neb_instance_gpaw_serial(initial=initial,
                                            final=final,
                                            directory=directory,
                                            nimages=nimages,
                                            )

    # calc
    gf = gpawLearn.Features()
    gf.AseFeatures.TSTcalc.run_neb(neb_instance=neb,
                                   directory=directory,
                                   opt_name='bfgs')
    # analysis
    images = gf.AseFeatures.TSTcalc.analysis_neb(fname_traj=os.path.join(directory, 'neb.traj'),
                                                 nimages=nimages)

    return images

  def NEB_calculations_parallelized_over_images_serial_wrapper(
          self,
          fname_py='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/NEB_calculations_parallelized_over_images/test/run.py'):
    directory = os.path.dirname(fname_py)

    def run():
      from py_package_learn.gpaw_learn import gpawLearn
      md = gpawLearn.Features().gpawTutorial.MolecularDynamics()
      md.NEB_calculations_parallelized_over_images_serial(
          directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/NEB_calculations_parallelized_over_images/test')

    gpawLearn.Features().AseFeatures.write_py_from_code(func=run,
                                                        fname_py=fname_py)
    return None

  def NEB_calculations_parallelized_over_images_analysis(
          self,
          directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/NEB_calculations_parallelized_over_images/neb'):
    gf = gpawLearn.Features()
    # analysis
    images = gf.get_atoms_list(directory=directory,
                               fname='neb.traj')[-5:]
    images = gf.AseFeatures.TSTcalc.analysis_neb(images=images,)
    return images

  def get_density_differences(self):
    import numpy as np
    from gpaw import restart

    slab, calc = restart('ontop.gpw', txt=None)
    AuAl_density = calc.get_pseudo_density()

    # Remove gold atom and do a clean slab calculation:
    del slab[-1]
    slab.get_potential_energy()
    Al_density = calc.get_pseudo_density()

    # Remove Al atoms and do a calculation for Au only:
    slab, calc = restart('ontop.gpw', txt=None)
    del slab[:-1]
    slab.calc = calc.new(kpts=None)
    slab.get_potential_energy()
    Au_density = slab.calc.get_pseudo_density()

    diff = AuAl_density - Au_density - Al_density
    np.save('densitydiff.npy', diff)

  def plot_density_differences(self):
    from mayavi import mlab
    d = np.load('densitydiff.npy')
    d2 = np.tile(d, (2, 2, 1))  # repeat 2x2 times in x,y-plane
    mlab.contour3d(d2)
    mlab.show()

  def ab_initio_molecular_dynamics(self,
                                   atoms: ase.Atoms,
                                   calc: gpaw.calculator.GPAW,
                                   timestep=3,  # fs
                                   steps=80,
                                   fname_traj='abmd.traj',
                                   directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/test',
                                   ):

    calc = gpaw.calculator.GPAW(
        mode='fd',
        gpts=gpaw.utilities.h2gpts(0.2,
                                   atoms.get_cell(), idiv=8),
        nbands=110,
        xc='LDA',
        txt=os.path.join(directory, f'abmd.txt'))

    atoms.calc = calc
    # Filename for saving trajectory
    traj_file = os.path.join(directory, fname_traj)
    # Integrator for the equations of motion, timestep depends on system
    dyn = ase.md.verlet.VelocityVerlet(atoms, timestep * ase.units.fs)

    # Saving the positions of all atoms after every time step
    with ase.io.Trajectory(traj_file, 'w', atoms) as traj:
      dyn.attach(traj.write, interval=1)
      # Running the simulation for 80 timesteps
      dyn.run(steps=steps)

    return None

  def ab_initio_molecular_dynamics_example(self,
                                           directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/ab_initio_molecular_dynamics_example'):
    """ https://gpaw.readthedocs.io/tutorialsexercises/moleculardynamics/abinitiomd/abinitiomd.html#transmission-of-hydrogen-through-graphene
    下面的脚本模拟了氢原子的撞击，初始速度对应于40 keV的动能，通过石墨烯靶中的六边形中心传输。Transmission of hydrogen through graphene

    Args:
        directory (str, optional): _description_. Defaults to '/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/ab_initio_molecular_dynamics_example'.

    Returns:
        _type_: _description_
    """

    name = 'graphene_h'

    # 5 x 5 supercell of graphene
    a = 2.45
    gra: ase.Atoms = ase.build.graphene(a=a, size=(5, 5, 1), vacuum=10)
    gra.center()

    # Starting position of the projectile with an impact point at the
    # center of a hexagon.
    # Set mass to one atomic mass unit to avoid isotope average.
    atoms: ase.Atoms = gra + ase.Atoms('H', masses=[1.0])
    d = a / 3**0.5
    atoms.positions[-1] = atoms.positions[22] + (0, d, 5)
    atoms.pbc = (True, True, True)

    if not os.path.exists(directory):
      os.makedirs(directory, exist_ok=True)
    calc = gpaw.calculator.GPAW(mode='fd',
                                gpts=gpaw.utilities.h2gpts(0.2,
                                                           gra.get_cell(), idiv=8),
                                nbands=110,
                                xc='LDA',
                                txt=os.path.join(directory, f'{name}_gs.txt'))

    atoms.calc = calc
    atoms.get_potential_energy()

    # Moving to the MD part
    ekin = 100  # kinetic energy of the ion (in eV)
    timestep = 0.1  # timestep in fs

    # Filename for saving trajectory
    ekin_str = '_ek' + str(int(ekin / 1000)) + 'keV'
    strbody = name + ekin_str
    traj_file = os.path.join(directory, f'{name}_ek_{ekin}.traj')

    # Integrator for the equations of motion, timestep depends on system
    dyn = ase.md.verlet.VelocityVerlet(atoms, timestep * ase.units.fs,
                                       )

    # Saving the positions of all atoms after every time step
    with ase.io.Trajectory(traj_file, 'w', atoms) as traj:
      dyn.attach(traj.write, interval=1)

      # Running one timestep before impact
      dyn.run(1)

      # Giving the target atom a kinetic energy of ene in the -z direction
      atoms[-1].momentum[2] = -(2 * ekin * atoms[-1].mass)**0.5

      # Running the simulation for 80 timesteps
      dyn.run(80)

    atoms = ase.io.read(
        '/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/ab_initio_molecular_dynamics_example/graphene_h_ek_100.traj', index=':')
    # view(atoms)
    return None

  def ehrenfest_dynamics(self):
    """https://gpaw.readthedocs.io/tutorialsexercises/moleculardynamics/ehrenfest/ehrenfest.html
    """
    pass


class Tutorial_STM_images():
  def __init__(self) -> None:
    """https://wiki.fysik.dtu.dk/gpaw/tutorialsexercises/electronic/stm/stm.html
    """
    pass

  def Al111_STM_image(self):
    # Let’s make a 2 layer Al(111) fcc surface using the ase.build.fcc111() function:
    from ase.build import fcc111
    atoms = fcc111('Al', size=(1, 1, 2))
    atoms.center(vacuum=4.0, axis=2)

    # Now we calculate the wave functions and write them to a file:
    from gpaw import GPAW
    calc = GPAW(mode='pw',
                kpts=(4, 4, 1),
                symmetry='off',
                txt='al111.txt')
    atoms.calc = calc
    energy = atoms.get_potential_energy()
    calc.write('al111.gpw', 'all')

    # 2-d scans
    # web-page: 2d.png, 2d_I.png, line.png, dIdV.png
    from ase.dft.stm import STM
    from gpaw import GPAW
    calc = GPAW('al111.gpw')
    atoms = calc.get_atoms()
    stm = STM(atoms)
    z = 8.0
    bias = 1.0
    c = stm.get_averaged_current(bias, z)
    x, y, h = stm.scan(bias, c, repeat=(3, 5))

    # From the current we make a scan to get a 2-d array of constant current height and make a contour plot:
    import matplotlib.pyplot as plt
    plt.gca().axis('equal')
    plt.contourf(x, y, h, 40)
    plt.colorbar()
    # plt.savefig('2d.png')
    plt.show()

    # Similarly, we can make a constant height scan (at 8 Å) and plot it:
    plt.figure()
    plt.gca().axis('equal')
    x, y, I = stm.scan2(bias, z, repeat=(3, 5))
    plt.contourf(x, y, I, 40)
    plt.colorbar()
    # plt.savefig('2d_I.png')
    plt.show()

    # Here is how to make a line-scan:
    plt.figure()
    a = atoms.cell[0, 0]
    x, y = stm.linescan(bias, c, [0, 0], [2 * a, 0])
    plt.plot(x, y)
    plt.savefig('line.png')

    # Scanning tunneling spectroscopy
    plt.figure()
    biasstart = -2.0
    biasend = 2.0
    biasstep = 0.05
    bias, I, dIdV = stm.sts(0, 0, z, biasstart, biasend, biasstep)
    plt.plot(bias, I, label='I')
    plt.plot(bias, dIdV, label='dIdV')
    plt.xlim(biasstart, biasend)
    plt.legend()
    plt.savefig('dIdV.png')
    pass

  def H_on_Al111_STM(self):
    # 建立模型
    from gpaw import GPAW
    a = 4.0
    b = a / 2**0.5
    L = 11.0

    # Set up 2-layer 2x2 (100) Al-slab:
    slab = ase.Atoms('Al2',
                     positions=[(0, 0, 0),
                                (b / 2, b / 2, -a / 2)],
                     cell=(b, b, L),
                     pbc=True)
    slab *= (2, 2, 1)

    if True:
      # Add adsorbate:
      slab += ase.Atoms('H', [(b, b, 1.55)])

    slab.center(axis=2)

    calc = GPAW(mode='pw', kpts=(4, 4, 1))
    slab.calc = calc
    slab.get_potential_energy()
    calc.write('HAl100.gpw', 'all')

    # STM 图
    from sys import argv
    from ase.dft.stm import STM
    from gpaw import restart

    # filename = argv[1]
    filename = 'HAl100.gpw'
    z0 = 8
    bias = 1.0

    atoms, calc = restart(filename, txt=None)

    stm = STM(atoms, symmetries=[0, 1, 2])
    c = stm.get_averaged_current(bias, z0)

    print(f'Average current at z={z0:f}: {c:f}')

    # Get 2d array of constant current heights:
    x, y, h = stm.scan(bias, c)

    print(f'Min: {h.min():.2f} Ang, Max: {h.max():.2f} Ang')

    plt.contourf(x, y, h, 40)
    plt.hot()
    plt.colorbar()
    plt.show()

    pass


class TutorialChargeAnalysis():
  def __init__(self) -> None:
    """两种方法: Bader and Hirshfeld
    https://wiki.fysik.dtu.dk/gpaw/tutorialsexercises/wavefunctions/charge/charge.html#bader-analysis
    """
    # bader 的安装方法
    # from bader_learn import baderLearn
    # baderLearn.BaderLearn().install()
    pass

  def get_electronic_density(self,
                             calc: gpaw.calculator.GPAW,
                             spin=None,
                             gridrefinement=4,
                             is_save=False,
                             fname_cube='density.cube',
                             is_pseudo=False,):
    """对于自旋极化计算, spin=None 给出的是总电子密度, 否则给出的是 spin=0,1 为自旋向上和下的电子密度

    Args:
        calc (gpaw.calculator.GPAW): _description_
        spin (_type_, optional): _description_. Defaults to None.
        gridrefinement (int, optional): _description_. Defaults to 4.
        is_save (bool, optional): _description_. Defaults to False.
        is_pseudo (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    # 伪电子密度
    rho_pseudo = calc.get_pseudo_density()
    # 全电子密度
    rho_all = calc.get_all_electron_density(spin=spin,
                                            gridrefinement=gridrefinement,)

    rho = rho_pseudo if is_pseudo else rho_all
    if is_save:
      fname = os.path.join(calc.directory, fname_cube)
      ase.io.write(filename=fname,
                   images=calc.atoms,
                   data=rho * ase.units.Bohr**3)
    return rho

  def show_electronic_density(self, calc=gpaw.calculator.GPAW):
    # density = self.get_electronic_density(calc=calc)
    # from mayavi import mlab
    # mlab.contour3d(density)
    # # <mayavi.modules.iso_surface.IsoSurface object at 0x7f1194491110>
    # mlab.show()
    return None

  def method_Hirshfeld_example(self):
    # First do a ground state calculation, and save the density as a cube file:
    atoms = ase.build.molecule('H2O')
    atoms.center(vacuum=3.5)
    atoms.calc = gpaw.GPAW(mode='fd', h=0.17, txt='h2o.txt')
    atoms.get_potential_energy()

    # write Hirshfeld charges out
    hf = gpaw.analyse.hirshfeld.HirshfeldPartitioning(atoms.calc)
    for atom, charge in zip(atoms, hf.get_charges()):
      atom.charge = charge
    # atoms.write('Hirshfeld.traj') # XXX Trajectory writer needs a fix
    atoms.copy().write('Hirshfeld.traj')

    # 分析
    # import ase.io.bader
    hirsh = ase.io.read('Hirshfeld.traj')
    bader = hirsh.copy()
    ase.io.bader.attach_charges(bader, fileobj='ACF.dat')  # 这只是用于对比bader 分析的结果

    print('atom Hirshfeld Bader')
    for ah, ab in zip(hirsh, bader):
      assert ah.symbol == ab.symbol
      print(f'{ah.symbol:4s} {ah.charge:9.2f} {ab.charge:5.2f}')

  def method_bader_example(self):
    from ase.units import Bohr

    atoms = ase.build.molecule('H2O')
    atoms.center(vacuum=3.5)
    atoms.calc = gpaw.calculator.GPAW(mode='fd', h=0.17, txt='h2o.txt')
    atoms.get_potential_energy()

    # create electron density cube file ready for bader
    rho = atoms.calc.get_all_electron_density(gridrefinement=4)
    ase.io.write('density.cube', atoms, data=rho * Bohr**3)  # ？

    # 分析 analyse the density cube file
    # web-page: ACF.dat
    # This will produce a number of files. The ACF.dat file, contains a summary of the Bader analysis:  Revealing that 0.58 electrons have been transferred from each Hydrogen atom to the Oxygen atom.
    import subprocess
    subprocess.call('bader -p all_atom -p atom_index density.cube'.split())
    charges = gpaw.utilities.bader.read_bader_charges()
    assert abs(sum(charges) - 10) < 0.0001
    assert abs(charges[1] - 0.42) < 0.005
    assert abs(charges[2] - 0.42) < 0.005
    ...

  def method_Hirshfeld(self, calc: gpaw.calculator.GPAW):
    """Hirshfeld charges out
    - from gpaw.analyse.hirshfeld import HirshfeldPartitioning  
    - 只能用于gpaw计算器 (fd mode) 才能这么分析

    Args:
        calc (gpaw.calculator.GPAW): _description_

    Returns:
        _type_: _description_
    """

    atoms: ase.Atoms = calc.atoms
    hf = gpaw.analyse.hirshfeld.HirshfeldPartitioning(calc)
    atoms.set_initial_charges(hf.get_charges())
    # 或者下面这种方法
    # for atom, charge in zip(atoms, hf.get_charges()):
    #   atom.charge = charge
    # 保存
    # atoms.write(filename=os.path.join(calc.directory, 'Hirshfeld.traj'))
    return atoms

  def method_bader(self, calc: gpaw.calculator.GPAW,
                   gridrefinement=2,
                   fname_cube='density.cube',
                   recalc=False,):
    """_summary_

    Args:
        calc (gpaw.calculator.GPAW): _description_
        gridrefinement (int, optional): _description_. Defaults to 4.

    Returns:
        _type_: _description_
    """

    atoms: ase.Atoms = calc.atoms
    fname_ACF = os.path.join(calc.directory, 'ACF.dat')
    if os.path.exists(fname_ACF) and (not recalc):
      pass
    else:
      # create electron density cube file ready for bader
      self.get_electronic_density(calc=calc,
                                  spin=None,
                                  gridrefinement=gridrefinement,
                                  is_save=True,
                                  fname_cube=fname_cube,
                                  is_pseudo=False,)
      # 分析 analyse the density cube file
      cwd = os.getcwd()
      os.chdir(calc.directory)
      f = os.popen(cmd=f'bader -p all_atom -p atom_index {fname_cube}')
      read = f.read()
      print('bader 分析完成.')
      os.chdir(cwd)

    # charges = gpaw.utilities.bader.read_bader_charges(filename=)
    atoms.set_initial_magnetic_moments(magmoms=calc.get_magnetic_moments())
    ase.io.bader.attach_charges(atoms=atoms, fileobj=fname_ACF)
    # 保存
    # atoms.write(filename=os.path.join(calc.directory, 'bader.traj'))
    # 删除多余文件
    for fname_dat in os.listdir(calc.directory):
      if fname_dat.startswith('BvAt'):
        fname_dat = os.path.join(calc.directory, fname_dat)
        if os.path.isfile(fname_dat):
          os.remove(fname_dat)

    return atoms

  def plot_bader(self, calc: gpaw.calculator.GPAW,
                 is_save=False,
                 fname_png='gpaw.png'):
    """画图 web-page: h2o-bader.png

    Args:
        calc (gpaw.calculator.GPAW): _description_
        is_save (bool, optional): _description_. Defaults to False.
        fname_png (str, optional): _description_. Defaults to 'gpaw.png'.

    Returns:
        _type_: _description_
    """

    directory = calc.directory

    fname_pkl = os.path.join(directory, 'gpaw.pckl')
    if os.path.isfile(fname_pkl):
      with open(fname_pkl, 'rb') as fd:
        dens, bader, atoms = pickle.load(fd)
    else:
      dens, atoms = ase.io.cube.read_cube_data(
          os.path.join(directory, 'density.cube'))
      bader, atoms = ase.io.cube.read_cube_data(
          os.path.join(directory, 'AtIndex.cube'))
      x = len(dens) // 2
      dens = dens[x]
      bader = bader[x]
      with open(fname_pkl, 'wb') as fd:
        pickle.dump((dens, bader, atoms), fd)

    x0, y0, z0 = atoms.positions[0]
    y = np.linspace(0, atoms.cell[1, 1], len(dens), endpoint=False) - y0
    z = np.linspace(0, atoms.cell[2, 2], len(dens[0]), endpoint=False) - z0
    print(y.shape, z.shape, dens.shape, bader.shape)
    print(atoms.positions)
    print(dens.min(), dens.mean(), dens.max())
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot()
    ax.contourf(z, y, dens, np.linspace(0.01, 0.9, 15))
    ax.contour(z, y, bader, [1.5], colors='k')
    ax.axis(xmin=-2, xmax=2, ymin=-2, ymax=2)
    if is_save:
      fig.savefig(fname_png)
    return fig


class TutorialRamanSpectra():
  def __init__(self) -> None:
    """https://wiki.fysik.dtu.dk/gpaw/tutorialsexercises/vibrational/rraman/resonant_raman_water.html
    """
    pass


class Wave_functions_and_charge_transfer():
  def __init__(self) -> None:
    pass

  def create_wave_function(self):
    # Creating a wave function file
    d = 1.1   # bondlength of hydrogen molecule
    a = 5.0   # sidelength of unit cell
    c = a / 2
    atoms = ase.Atoms('CO',
                      positions=[(c - d / 2, c, c),
                                 (c + d / 2, c, c)],
                      cell=(a, a, a))

    calc = gpaw.calculator.GPAW(mode='fd', nbands=5, h=0.2, txt=None)
    atoms.calc = calc

    # Start a calculation:
    energy = atoms.get_potential_energy()

    # Save wave functions:
    calc.write('CO.gpw', mode='all')
    pass

  def create_wave_function_cube(self):
    """用 VESTA 能直接打开 *.cube 文件
    """
    if not os.path.exists('CO.gpw'):
      self.create_wave_function()
    # Creating wave function cube files
    # You can get separate cube files (the format used by Gaussian) for each wavefunction with the script:
    from ase.io import write
    from ase.units import Bohr
    from gpaw import restart

    basename = 'CO'
    # load binary file and get calculator
    atoms, calc = restart(basename + '.gpw')

    # loop over all wfs and write their cube files
    nbands = calc.get_number_of_bands()
    for band in range(nbands):
      wf = calc.get_pseudo_wave_function(band=band)
      fname = f'{basename}_{band}.cube'
      print('writing wf', band, 'to file', fname)
      write(fname, atoms, data=wf * Bohr**1.5)  # 需要乘 Bohr**1.5？

  def plot_wave_function(self):
    # vmd CO_*.cube
    # 用 VESTA 能直接打开 *.cube 文件
    pass

  def Kohn_Sham_wavefunctions(self):
    # Oxygen atom:
    atom = ase.Atoms('O', cell=[6, 6, 6], pbc=False)
    atom.center()

    calc = gpaw.calculator.GPAW(mode='fd',
                                h=0.2,
                                hund=True,  # assigns the atom its correct magnetic moment
                                txt='O.txt')

    atom.calc = calc
    atom.get_potential_energy()

    # Write wave functions to gpw file:
    calc.write('O.gpw', mode='all')

    # Generate cube-files of the orbitals:
    for spin in [0, 1]:
      for n in range(calc.get_number_of_bands()):
        wf = calc.get_pseudo_wave_function(band=n, spin=spin)
        ase.io.write(f'O.{spin}.{n}.cube', images=atom, data=wf)
    pass

  def Kohn_Sham_wavefunctions_visulize(self):
    """用 VESTA 能直接打开 *.cube 文件
    """
    from gpaw import GPAW
    # from mayavi import mlab
    # calc = GPAW('O.gpw', txt=None)
    # lumo = calc.get_pseudo_wave_function(band=2, spin=1)
    # mlab.contour3d(lumo)
    # mlab.show()

    pass

  def electrostatic_potential(self):
    """https://wiki.fysik.dtu.dk/gpaw/tutorialsexercises/wavefunctions/ps2ae/ps2ae.html
    """
    pass

  def electron_density_and_pseudo_electron_density(self):
    """
    from gpaw import GPAW
    from ase.build import molecule

    calc = GPAW(mode='fd')
    mol = molecule('C6H6', calculator=calc)
    mol.center(vacuum=5)
    E = mol.get_potential_energy()
    nt = calc.get_pseudo_density()
    # As the all-electron density has more structure than the pseudo-density, it is necessary to refine the density grid used to represent the pseudo-density.
    n_ae = calc.get_all_electron_density(gridrefinement=2)
    """
    # web-page: all_electron.csv
    unitcell = np.array([6.5, 6.6, 9.])
    gridrefinement = 2

    f = ase.parallel.paropen('all_electron.csv', 'w')

    for formula in ('Na', 'Cl', 'NaCl',):
      if formula in ['Na', 'Cl']:
        hund = True
      else:
        hund = False
      calc = gpaw.calculator.GPAW(mode='fd',
                                  xc='PBE',
                                  h=0.18,
                                  hund=hund,
                                  convergence={'eigenstates': 1e-8},
                                  txt=formula + '.txt')

      sys = ase.build.molecule(formula, cell=unitcell, calculator=calc)
      sys.center()
      sys.get_potential_energy()

      # Get densities
      nt = calc.get_pseudo_density()
      n = calc.get_all_electron_density(gridrefinement=gridrefinement)

      # Get integrated values
      dv = sys.get_volume() / calc.get_number_of_grid_points().prod()
      It = nt.sum() * dv
      I = n.sum() * dv / gridrefinement**3
      print('%-4s,%4.2f,%5.2f' % (formula, It, I), file=f)
      print('%-4s,%4.2f,%5.2f' % (formula, It, I))
    f.close()

  def interface_to_Wannier90(self):
    """
    https://wiki.fysik.dtu.dk/gpaw/tutorialsexercises/wavefunctions/wannier90/wannier90_tutorial.html

    conda install -c conda-forge wannier90
    which wannier90.x

    GaAs*.xsf 可以通过VEASTA 看图, 或者can be plotted with xcrysden. 

    """
    from xcrysden_learn import xcrysdenLearn
    xcrysdenLearn.XcrysdenLearn().install()

    # 基态计算
    from ase import Atoms
    from ase.build import bulk
    from gpaw import GPAW, FermiDirac, PW

    cell = bulk('Ga', 'fcc', a=5.68).cell
    a = Atoms('GaAs', cell=cell, pbc=True,
              scaled_positions=((0, 0, 0), (0.25, 0.25, 0.25)))

    calc = GPAW(mode=PW(600),
                xc='LDA',
                occupations=FermiDirac(width=0.01),
                convergence={'density': 1.e-6},
                kpts={'size': (2, 2, 2), 'gamma': True},
                txt='gs_GaAs.txt')

    a.calc = calc
    a.get_potential_energy()
    calc.write('GaAs.gpw', mode='all')

    # Wannier90
    import os
    from gpaw.wannier90 import Wannier90
    from gpaw import GPAW

    seed = 'GaAs'

    calc = GPAW(seed + '.gpw', txt=None)

    w90 = Wannier90(calc,
                    seed=seed,
                    bands=range(4),
                    orbitals_ai=[[], [0, 1, 2, 3]])

    w90.write_input(num_iter=1000,
                    # The plot keyword writes the four Wannier functions in .xsf format, which can be plotted with xcrysden. An example is shown below.
                    plot=True,
                    )
    w90.write_wavefunctions()
    os.system('wannier90.x -pp ' + seed)

    w90.write_projections()
    w90.write_eigenvalues()
    w90.write_overlaps()

    os.system('wannier90.x ' + seed)
    # 获得 GaAs.out 和 GaAs*.xsf 文件
    # GaAs*.xsf 可以通过VEASTA 看图
    pass

  def interface_to_Wannier90_fermi_surface_Cu_basic(self):
    # 基本计算
    from ase.build import bulk
    from gpaw import GPAW, FermiDirac, PW

    a = bulk('Cu', 'fcc')

    calc = GPAW(mode=PW(600),
                xc='PBE',
                occupations=FermiDirac(width=0.1),
                kpts=(12, 12, 12),
                txt='Cu_scf.txt')
    a.calc = calc
    a.get_potential_energy()

    calc.fixed_density(
        kpts={'size': (4, 4, 4), 'gamma': True},
        nbands=30,
        txt='Cu_nscf.txt',
        convergence={'bands': 20}).write('Cu.gpw', mode='all')

  def interface_to_Wannier90_fermi_surface_Cu(self):
    if not os.path.exists('Cu.gpw'):
      self.interface_to_Wannier90_fermi_surface_Cu_basic()

    # Wannier90 计算
    seed = 'Cu'
    calc = gpaw.calculator.GPAW(seed + '.gpw', txt=None)
    w90 = Wannier90(calc,
                    seed=seed,
                    bands=range(20),
                    orbitals_ai=[[0, 1, 4, 5, 6, 7, 8]])

    w90.write_input(num_iter=1000,
                    dis_num_iter=500,
                    # plot=True
                    )

    os.system('wannier90.x -pp ' + seed)

    w90.write_projections()
    w90.write_eigenvalues()
    w90.write_overlaps()

    os.system('wannier90.x ' + seed)

    # After running the script, add the following lines to Cu.win:
    'restart = plot'
    'fermi_surface_plot = True'
    # We emphasize that the write_input_file function is just for generating the basic stuff that should be in the Cu.win input file. In general this file should be modified according to need before running wannier90.x.

    # and do:
    'wannier90.x Cu'
    # conda install -c conda-forge xcrysden


class TutorialLocalOrbitals():
  def __init__(self) -> None:
    pass

  def benzene_molecule(self):
    """Local Orbitals in benzene molecule
    """
    # creates: C6H6_minimal.png, C6H6_extended.png, C6H6_pzLOs.png
    from gpaw.lcao.local_orbitals import LocalOrbitals
    from gpaw.lcao.pwf2 import LCAOwrap
    from matplotlib import pyplot as plt
    from scipy.linalg import eigvalsh

    plt.style.use('bmh')
    plt.rcParams['font.size'] = 13
    plt.rcParams['lines.linewidth'] = 2

    def get_eigvals(model, erng=[-10, 10]):
      """Helper function to get the eigenvalues.

      Parameters
      ----------
      model : Object
          Must have a `get_hamiltonian` and `get_overlap` methods.
      erng : (float,float), optional
          Energy range of min and max eigenvalues.
      """
      # Compute eigenvalues from H and S.
      H = model.get_hamiltonian()
      S = model.get_overlap()
      if np.allclose(S, np.eye(S.shape[0]), atol=1e-4):
        eigs = np.linalg.eigvalsh(H)
      else:
        eigs = eigvalsh(H, S)
      eigs = eigs[(eigs > erng[0]) & (eigs < erng[1])]
      return eigs

    def compare_eigvals(lcao, los, figname, figtitle):
      """Compare eigenvalues between LCAO and LO model.

      Parameters
      ----------
      lcao : LCAOWrap
          An LCAO wrapper around an LCAO calculation.
      los : LocalOrbitals
          A LO wrapper around an LCAO calculation
      figname : str
          Save the figure using `figname`.
      figtitle : str
          Title of the figure
      """
      # Get eigenvalues
      fermi = lcao.calc.get_fermi_level()
      erng = [fermi + elim for elim in [-10, 10]]
      lcao_eigs = get_eigvals(lcao, erng)
      los_eigs = get_eigvals(los, erng)
      # Plot eigenvalues
      plt.figure()
      plt.hlines(lcao_eigs, -1, -0.01, color='tab:blue')
      plt.hlines(los_eigs, 0.01,
                 1, linestyles='-.', color='tab:orange')
      plt.hlines(0., -1., 1., linestyle='--', color='black')
      plt.grid(axis='x')
      _ = plt.xticks(labels=['LCAO', 'LOs'], ticks=[-0.5, 0.5])
      plt.title(figtitle)
      plt.ylabel('Energy (eV)')
      plt.savefig(figname, bbox_inches='tight')

    # Atoms
    benzene = ase.build.molecule('C6H6', vacuum=5)

    # LCAO calculation
    calc = gpaw.calculator.GPAW(
        mode='lcao', xc='LDA', basis='szp(dzp)', txt=None)
    calc.atoms = benzene
    calc.get_potential_energy()

    # LCAO wrapper
    lcao = LCAOwrap(calc)

    # Construct a LocalOrbital Object
    los = LocalOrbitals(calc)

    # Subdiagonalize carbon atoms and group by energy.
    los.subdiagonalize('C', groupby='energy')
    # Groups of LOs are stored in a dictionary >>> los.groups

    # Dump pz-type LOs in cube format
    fig = los.plot_group(-6.9)
    fig.savefig('C6H6_pzLOs.png', dpi=300, bbox_inches='tight')

    # Take minimal model
    los.take_model(minimal=True)
    # Get the size of the model >>> len(los.model)
    # Assert that the Hamiltonian has the same
    # dimensions >> los.get_hamiltonian().shape

    # Assert model indeed conicides with pz-type LOs
    assert los.indices == los.groups[-6.9]

    # Compare eigenvalues with LCAO
    compare_eigvals(lcao, los, "C6H6_minimal.png", "minimal=True")

    # Extend with groups of LOs that overlap with the minimal model
    los.take_model(minimal=False)
    # Get the size of the model >>> len(los.model)

    # Assert model is extended with other groups.
    assert los.indices == (
        los.groups[-6.9] + los.groups[20.2] + los.groups[21.6])

    # Compare eigenvalues with LCAO
    compare_eigvals(lcao, los, "C6H6_extended.png", "minimal=False")
    pass


class N2_gpaw():
  def __init__(self) -> None:
    pass

  def explain(self, fname_out='gpaw.txt'):
    from ase.visualize import view
    from ase import Atoms
    atoms = Atoms('N2', positions=[[0, 0, -1], [0, 0, 1]])
    '''
    # 以防出错, 进行可视化
    from ase.visualize import view
    view(atoms)
    # 或者
    from ase.io import write
    write('myatoms.traj', atoms)
    import os
    os.system('ase gui myatoms.traj')
    '''
    from gpaw import GPAW
    # Normally, calculators work by calling an external electronic structure code or force field code.
    # 创建一个计算器实例, 然后附加给 atoms 对象
    calc = GPAW(mode='lcao', basis='dzp', txt=fname_out,
                xc='LDA')  # fname_out 给出计算的结果
    atoms.calc = calc
    # Different electronic structure codes have different input parameters. GPAW can use real-space grids (mode='fd'), planewaves (mode='pw'), or localized atomic orbitals (mode='lcao') to represent the wavefunctions. Here we have asked for the faster but less accurate LCAO mode, together with the standard double-zeta polarized basis set ('dzp'). GPAW and many other codes require a unit cell (or simulation box) as well. Hence we center the atoms within a box, leaving 3 Å of empty space around each atom:
    atoms.center(vacuum=3.0)
    # print(atoms) # The printout will show the simulation box (or cell) coordinates, and the box can also be seen in the GUI.

    # 计算 Once the Atoms have a calculator with appropriate parameters, we can do things like calculating energies and forces:
    # atoms.get_kinetic_energy() # 对于MD 还能给出 referring to the kinetic energy of the nuclei if they are moving. In DFT calculations, we normally just want the Kohn–Sham ground state energy which is the “potential” energy as provided by the calculator.)
    # Calling get_potential_energy() or get_forces() triggers a selfconsistent calculation and gives us a lot of output text. Inspect the gpaw.txt file. You can review the text file to see what computational parameters were chosen.
    e = atoms.get_potential_energy()  # in eV
    print('Energy', e)
    f = atoms.get_forces()  # in eV/A
    print('Forces')
    print(f)
    pass

  def get_traj(self,
               fname_traj='binding_curve.traj',
               ):
    from gpaw import GPAW
    from ase import Atoms
    from ase.io import Trajectory

    atoms = Atoms('N2', positions=[[0, 0, -1], [0, 0, 1]])
    atoms.center(vacuum=3.0)

    calc = GPAW(mode='lcao', basis='dzp', txt='gpaw.txt')
    atoms.calc = calc

    traj = Trajectory(fname_traj, 'w')

    step = 0.05
    nsteps = int(3 / step)

    for i in range(nsteps):
      d = 0.5 + i * step
      atoms.positions[1, 2] = atoms.positions[0, 2] + d
      atoms.center(vacuum=3.0)
      e = atoms.get_potential_energy()
      f = atoms.get_forces()
      print(e, f)
      traj.write(atoms)

  def get_fig(self, fname_traj='binding_curve.traj',
              is_save_fig=False,
              fname_fig='tmp.pdf'):
    import matplotlib.pyplot as plt
    from ase import io

    energies = []
    distances = []
    for atoms in io.iread(fname_traj):  # 这里是 io.iread()
      energies.append(atoms.get_potential_energy())
      distances.append(atoms.positions[1, 2] - atoms.positions[0, 2])

    ax = plt.gca()
    ax.plot(distances, energies)
    ax.set_xlabel('Distance [Å]')
    ax.set_ylabel('Total energy [eV]')
    if is_save_fig:
      plt.savefig(fname_fig)
    plt.show()
    return

  def get_energy_N(self,):
    """计算单个N原子的能量, 注意原子的自旋极化

    Returns:
        _type_: _description_
    """
    from gpaw import GPAW
    from ase import Atoms

    atoms = Atoms('N')
    atoms.center(vacuum=3.0)
    # before triggering the calculation to tell GPAW that your atom is spin polarized.
    atoms.set_initial_magnetic_moments([3])

    calc = GPAW(mode='lcao', basis='dzp')
    atoms.calc = calc
    energy_N = atoms.get_potential_energy()
    return energy_N

  def binding_enrgy_mod(self,):
    from gpaw import GPAW
    from ase import Atoms
    from ase.io import Trajectory
    from ase import io

    atoms = Atoms('N2', positions=[[0, 0, -1], [0, 0, 1]])
    atoms.center(vacuum=3.0)

    calc = GPAW(mode='lcao', basis='dzp', txt='gpaw.txt')
    atoms.calc = calc

    step = 0.1
    nsteps = int(3 / step)

    distance_list = []
    energy_list = []
    for i in range(nsteps):
      d = 0.5 + i * step
      atoms.positions[1, 2] = atoms.positions[0, 2] + d
      atoms.center(vacuum=3.0)
      e = atoms.get_potential_energy()
      f = atoms.get_forces()
      distance_list.append(d)
      energy_list.append(e)
      io.write('config.xyz', images=atoms, append=True)
    return distance_list, energy_list


class SummerSchool():
  def __init__(self):
    pass

  def catalysis(self,
                directory='/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/catalysis'):
    """https://gpaw.readthedocs.io/summerschools/summerschool24/catalysis/catalysis.html"""
    gf = gpawLearn.Features()

    def relax_slab(directory):
      a_Ru = 2.704  # PBE value from OQMD.org; expt value is 2.706
      slab = ase.build.hcp0001('Ru', a=a_Ru, size=(2, 2, 2), vacuum=5.0)

      # Other metals are possible, for example Rhodium
      # Rhodium is FCC so you should use fcc111(...) to set up the system
      # (same arguments).
      # Remember to set the FCC lattice constant, get it from OQMD.org.

      # a_Rh = 3.793
      # slab = fcc111('Rh', a=a_Rh, size=(2, 2, 2), vacuum=5.0)

      # view(slab)
      z = slab.positions[:, 2]
      constraint = ase.constraints.FixAtoms(mask=(z < z.min() + 1.0))
      slab.set_constraint(constraint)

      # calc = gpaw.calculator.GPAW(xc='PBE',
      #                             mode=gpaw.wavefunctions.pw.PW(350),
      #                             kpts={'size': (4, 4, 1), 'gamma': True},
      #                             convergence={'eigenstates': 1e-6})
      # slab.calc = calc
      calc = gf.get_calc(directory=directory,
                         xc='PBE',
                         mode=gpaw.wavefunctions.pw.PW(350),
                         kpts={'size': (4, 4, 1), 'gamma': True},
                         convergence={'eigenstates': 1e-6},
                         )
      calc = gf.calc_relaxation_general(atoms=slab,
                                        calc=calc,
                                        fname_traj='Ru.traj',)
      return calc

    def N2(directory):
      molecule = ase.Atoms('2N', positions=[(0., 0., 0.), (0., 0., 1.1)],)
      molecule.center(vacuum=5)

      calc = gf.get_calc(directory=directory,
                         xc='PBE',
                         mode=gpaw.wavefunctions.pw.PW(350),)
      calc = gf.calc_relaxation_general(atoms=molecule, calc=calc,
                                        opt_name='quasinewton')
      return calc

    def N2_on_slab(directory):
      calc = relax_slab(os.path.join(
          '/Users/wangjinlong/job/soft_learn/py_package_learn/gpaw_learn/my_example/learn_example/catalysis', 'slab'))
      atoms_slab = calc.atoms
      atoms = gf.aseFeatures.GetModel.get_adsorbate_on_slab_model_wrapper(
          atoms_slab=atoms_slab,
          adsorbate_name='N2',
          adsorbate_postion_index_list=[4],
          height=1.9
      )
      calc = gf.get_calc(directory=directory,
                         #  xc='PBE',
                         #  mode=gpaw.wavefunctions.pw.PW(350),
                         #  kpts={'size': (4, 4, 1), 'gamma': True},
                         #  convergence={'eigenstates': 1e-6},
                         **calc.parameters,
                         )
      calc = gf.calc_relaxation_general(atoms=atoms,
                                        calc=calc,
                                        fname_traj='N2_on_Ru.traj',)
      return calc

    directory_slab = os.path.join(directory, 'slab')
    calc1 = relax_slab(directory=directory_slab)
    directory_N2 = os.path.join(directory, 'N2')
    calc2 = N2(directory=directory_N2)
    directory_N2_on_slab = os.path.join(directory, 'N2_on_slab')
    calc3 = N2_on_slab(directory=directory_N2_on_slab)
    return calc3
