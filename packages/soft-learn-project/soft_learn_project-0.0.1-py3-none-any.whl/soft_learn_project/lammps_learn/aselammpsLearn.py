
import os
import ase
import ase.build
import ase.calculators
import ase.calculators.lammpsrun


class AseLammps():
  def __init__(self) -> None:
    """推荐用 AseLammpslib
    """
    self.env_sets()
    pass

  def env_sets(self, mpirun_path='/opt/homebrew/bin/mpirun',
               ncores=4,
               # '/opt/homebrew/bin/lmp_mpi',
               lmp_mpi_path='/Users/wangjinlong/job/science_research/sci_scripts/bin/lmp_mac_mpi',
               ):
    """shell ~/.bashrc 中添加:
    export ASE_LAMMPSRUN_COMMAND="/opt/homebrew/bin/mpirun -np 4 /opt/homebrew/bin/lmp_mpi"
    或者:
    os.environ['ASE_LAMMPSRUN_COMMAND'] = f'{mpirun_path} -np {ncores} {lmp_mpi_path}'
    终端执行:
    - /opt/homebrew/bin/mpirun -np 4 /opt/homebrew/bin/lmp_mpi -in in.melt

    """

    # 在python环境中执行
    if lmp_mpi_path is None:
      lmp_mpi_path = os.popen('which lmp_mpi').read().strip()
    os.environ['ASE_LAMMPSRUN_COMMAND'] = f'{mpirun_path} -np {ncores} {lmp_mpi_path}'

    os.environ['DYLD_LIBRARY_PATH'] = '/Users/wangjinlong/job/soft_learn/lammps_learn/package/mylammps/src:$DYLD_LIBRARY_PATH'
    return None

  def example(self,
              MD_pot_path='/Users/wangjinlong/job/soft_learn/lammps_learn/potential/MD_pot'):

    parameters = {'pair_style': 'eam/alloy',
                  'pair_coeff': [f'* * {MD_pot_path}/NiAlH_jea.eam.alloy Ni H']}

    files = ['NiAlH_jea.eam.alloy']

    Ni = ase.build.bulk('Ni', cubic=True)
    H = ase.Atom('H', position=Ni.cell.diagonal()/2)
    NiH: ase.Atoms = Ni + H

    # lammps = LAMMPS(parameters=parameters, files=files)
    lammps = ase.calculators.lammpsrun.LAMMPS(parameters=parameters,
                                              # tmp_dir='tmp',
                                              keep_alive=False,
                                              files=files,
                                              )

    NiH.calc = lammps
    print("Energy ", NiH.get_potential_energy())
