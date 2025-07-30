
class FHI_aims():
  def __init__(self) -> None:
    # 设置环境变量
    s1 = 'export ASE_AIMS_COMMAND=aims.x'
    s2 = 'export AIMS_SPECIES_DIR=/home/alumne/software/FHIaims/species_defaults/light'
    # 如果不想
    import os
    os.environ['ASE_AIMS_COMMAND'] = 'aims.x'
    os.environ['AIMS_SPECIES_DIR'] = '/home/alumne/software/FHIaims/species_defaults/light'
    pass

  def optimisation(self,):
    import os
    from ase import Atoms
    from ase.calculators.aims import Aims
    from ase.optimize import BFGS

    os.environ['ASE_AIMS_COMMAND'] = 'aims.x'
    os.environ['AIMS_SPECIES_DIR'] = '/home/myname/FHIaims/species_defaults/light'

    atoms = Atoms('HOH',
                  positions=[[0, 0, -1], [0, 1, 0], [0, 0, 1]])

    # 自洽计算 单点能
    calc = Aims(xc='LDA', compute_forces=True)
    atoms.calc = calc
    energy = atoms.get_total_energy()

    # 常规结构优化
    opt = BFGS(atoms, trajectory='opt-aims.traj')
    opt.run(fmax=0.05)

    # socket结构优化, 可以加速计算
    aims = Aims(xc='LDA',
                compute_forces=True,
                use_pimd_wrapper=('UNIX:mysocket', 31415))

    from ase.calculators.socketio import SocketIOCalculator
    with SocketIOCalculator(aims, unixsocket='mysocket') as calc:
      atoms.calc = calc
      opt.run(fmax=0.05)
