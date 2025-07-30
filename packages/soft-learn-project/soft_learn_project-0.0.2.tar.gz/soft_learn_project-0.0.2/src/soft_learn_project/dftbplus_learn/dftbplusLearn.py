import os


class DftbplusLearn():
  def __init__(self,) -> None:
    """https://wiki.fysik.dtu.dk/ase/ase/calculators/dftb.html
    https://www.dftbplus.org/
    https://www.dftb.org/
    https://dftbplus-recipes.readthedocs.io/en/latest/introduction.html
    https://dftb.org/parameters/download.html#sec-parameters-download scf 文件
    """
    super().__init__()
    self.env_set()
    pass

  def env_set(self):
    with os.popen('which dftb+') as f:
      dftb_bin = f.read().strip()
    os.environ['ASE_DFTB_COMMAND'] = f"{dftb_bin} > PREFIX.out"
    os.environ['DFTB_PREFIX'] = '/Users/wangjinlong/job/soft_learn/py_package_learn/dftbplus_learn/ParameterSets/ptbp_complete_set'
    # '/Users/wangjinlong/job/soft_learn/py_package_learn/dftbplus_learn/pbc-0.3.0/skfiles'
    pass

  def install(self):
    """conda install -c conda-forge dftbplus
    conda install -c conda-forge "dftbplus=24.1=nompi*"
    conda install -c conda-forge "dftbplus=24.1=mpi_openmpi*"
    conda install dftbplus-tools=24.1
    conda install dftbplus-python=24.1
    """
    return None

  def get_calc(self, directory='.',
               kpts=[1]*3,
               Hamiltonian_SCC='Yes',
               **kwargs):
    """ Hamiltonian_MaxAngularMomentum_Si='d',  # 关键！需指定角动量,
    ---
    周期性结构需要设置 kpts, 否则会报错
    ---
    # Hamiltonian_SCC='Yes', 自洽计算 
    """
    import ase.calculators.dftb
    if not os.path.exists(directory):
      os.makedirs(directory)
    calc = ase.calculators.dftb.Dftb(
        kpts=kpts,
        directory=directory,
        Hamiltonian_SCC=Hamiltonian_SCC,
        **kwargs,
    )
    self.calc = calc
    return calc

  def example_relax_by_ase(self):
    """Geometry optimization by ASE
    """
    atoms = ase.build.molecule('H2O')
    calc = ase.calculators.dftb.Dftb(
        label='h2o',
        Hamiltonian_MaxAngularMomentum_='',
        Hamiltonian_MaxAngularMomentum_O='p',
        Hamiltonian_MaxAngularMomentum_H='s',
    )
    atoms.calc = calc

    dyn = ase.optimize.QuasiNewton(atoms, trajectory='test.traj')
    dyn.run(fmax=0.01)
    # ase.io.write('final.xyz', atoms)
    return atoms

  def example_relax_by_dftb(self):
    """Geometry optimization by DFTB+
    """
    atoms = ase.build.molecule('H2O')
    calc = ase.calculators.dftb.Dftb(label='h2o',
                                     Driver_='ConjugateGradient',
                                     Driver_MaxForceComponent=1e-4,
                                     Driver_MaxSteps=1000,
                                     Hamiltonian_MaxAngularMomentum_='',
                                     Hamiltonian_MaxAngularMomentum_O='p',
                                     Hamiltonian_MaxAngularMomentum_H='s')

    atoms.calc = calc
    calc.calculate(atoms)

    # The 'geo_end.gen' file written by the ASE calculator
    # (containing the initial geometry), has been overwritten
    # by DFTB+ and now contains the final, optimized geometry.
    # final = ase.io.read('geo_end.gen')
    # ase.io.write('final.xyz', final)
    return atoms
