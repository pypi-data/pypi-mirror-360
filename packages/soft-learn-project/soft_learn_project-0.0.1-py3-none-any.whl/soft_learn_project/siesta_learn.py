import os


class SiestaLearn():
  def __init__(self) -> None:
    # Set both environment variables in your shell configuration file:
    s1 = '$ export ASE_SIESTA_COMMAND="siesta < PREFIX.fdf > PREFIX.out"'
    # 势文件数据库
    url = 'https://departments.icmab.es/leem/SIESTA_MATERIAL/Databases/Pseudopotentials/periodictable-gga-abinit.html'
    url = 'https://www.simuneatomistics.com/siesta-pro/siesta-pseudos-and-basis-database/'
    s2 = '$ export SIESTA_PP_PATH=$HOME/mypps'
    #

    # python env
    path_siesta = os.popen('which siesta').read().strip()
    num_cores = 4
    os.environ['ASE_SIESTA_COMMAND'] = f'mpirun -np {num_cores} {path_siesta} < PREFIX.fdf > PREFIX.out'
    # gpaw 的势文件 在安装目录中 envs/gpaw/share/gpaw 中, 而sista 中没有, 以后处理
    os.environ['SIESTA_PP_PATH'] = f''
    pass

  def set_pars(self):
    # Extra FDF parameters
    # The SIESTA code reads the input parameters for any calculation from a .fdf file. This means that you can set parameters by manually setting entries in this input .fdf file. This is done by the argument:

    Siesta(fdf_arguments={'variable_name': value, 'other_name': other_value})
    # For example, the DM.MixingWeight can be set using
    Siesta(fdf_arguments={'DM.MixingWeight': 0.01})

  def example(self,):
    from ase import Atoms
    from ase.calculators.siesta import Siesta
    from ase.units import Ry

    a0 = 5.43
    bulk = Atoms('Si2', [(0, 0, 0),
                         (0.25, 0.25, 0.25)],
                 pbc=True)
    b = a0 / 2
    bulk.set_cell([(0, b, b),
                  (b, 0, b),
                  (b, b, 0)], scale_atoms=True)

    calc = Siesta(label='Si',
                  xc='PBE',
                  mesh_cutoff=200 * Ry,
                  energy_shift=0.01 * Ry,
                  basis_set='DZ',
                  kpts=[10, 10, 10],
                  fdf_arguments={'DM.MixingWeight': 0.1,
                                 'MaxSCFIterations': 100},
                  )
    bulk.calc = calc
    e = bulk.get_potential_energy()
    pass
