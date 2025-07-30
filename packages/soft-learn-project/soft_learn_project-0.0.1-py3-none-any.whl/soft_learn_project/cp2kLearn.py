import os
import ase.build.bulk
import ase.calculators
import ase.calculators.cp2k
import ase.build
import ase.constraints
import ase.lattice.cubic
import pandas as pd


class Tools():
  def __init__(self) -> None:
    pass

  def aml(self):
    """https://www.cp2k.org/tools:aml
    AML Python Package
    The AML is a Python package to automatically build the reference set for the training of Neural Network Potentials (FORCE_EVAL/NNP) in an automated and data-driven fashion.

    The code is freely available under the GNU GPL license at: https://github.com/MarsalekGroup/aml.

    Appetizing Example
    Among other things, one can use it to convert CP2K output to the RuNNer/n2p2 format:
    """

    import numpy as np
    # import aml

    # fn_positions = 'cp2k-pos-1.xyz'
    # fn_forces = 'cp2k-frc-1.xyz'
    # A = 3
    # B = 4
    # C = 5
    # cell = np.array([[A, 0, 0], [0, B, 0], [0, 0, C]])
    # frames = aml.read_frames_cp2k(fn_positions=fn_positions,
    #                               fn_forces=fn_forces,
    #                               cell=cell)
    # structures = aml.Structures.from_frames(frames)
    # structures.to_file('input.data', label_prop='reference')
    pass

  def ase_tool(self):
    # https://www.cp2k.org/tools:ase
    pass


class PyCp2k():
  def __init__(self) -> None:
    """
    - 学习例子, 以后有空学学
    https://www.cp2k.org/exercises
    https://www.cp2k.org/exercises:common:index
    https://www.cp2k.org/events:2018_summer_school:index

    # https://www.cp2k.org/howto:static_calculation
    # https://manual.cp2k.org/trunk/methods/optimization/geometry.html
    # /Users/wangjinlong/job/soft_learn/cp2k_learn/cp2k-examples/geometry_optimisation/my
    # https://www.cp2k.org/exercises:common:geo_opt

    * 继续一个计算
    - Should the job die for some reason, you can continue the job using the latest atomic coordinates by using command:
    - $cp2k.sopt -o H2O.out H2O-1.restart &
    """
    pass

  def install(self):
    """https://github.com/SINGROUP/pycp2k
    """
    # conda install pycp2k
    pass

  def parse_inp(self, fname='xxx/yy.inp'):
    from pycp2k import CP2K
    import pycp2k
    # An existing input file can be parsed
    calc = CP2K()
    calc.parse(filepath=fname)
    return calc

  def get_df_basis_set_and_potential(self):
    """https://cp2k-basis.pierrebeaujean.net/

    Returns:
        _type_: _description_
    """
    data_list = [{'kind': 'H',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q1',
                  'potential': 'GTH-PBE-q1'},
                 {'kind': 'He',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q2',
                  'potential': 'GTH-PBE-q2'},
                 {'kind': 'Li',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q3',  # ! or DZVP-MOLOPT-PBE-GTH-q1',
                  'potential': 'GTH-PBE-q3',  # ! or GTH-PBE-q1
                  },
                 {'kind': 'Be',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q4',  # ! or DZVP-MOLOPT-PBE-GTH-q2,
                  'potential': 'GTH-PBE-q4',  # ! or GTH-PBE-q2
                  },
                 {'kind': 'B',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q3',
                  'potential': 'GTH-PBE-q3'},
                 {'kind': 'C',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q4',
                  'potential': 'GTH-PBE-q4'},
                 {'kind': 'N',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q5',
                  'potential': 'GTH-PBE-q5'},
                 {'kind': 'O',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q6',
                  'potential': 'GTH-PBE-q6'},
                 {'kind': 'F',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q7',
                  'potential': 'GTH-PBE-q7'},
                 {'kind': 'Ne',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q8',
                  'potential': 'GTH-PBE-q8'},
                 {'kind': 'Na',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q9',  # ! or DZVP-MOLOPT-PBE-GTH-q1',
                  'potential': 'GTH-PBE-q9 ! or GTH-PBE-q1'},
                 {'kind': 'Mg',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q10',
                  'potential': 'GTH-PBE-q10'},
                 {'kind': 'Al',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q3',
                  'potential': 'GTH-PBE-q3'},
                 {'kind': 'Si',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q4',
                  'potential': 'GTH-PBE-q4'},
                 {'kind': 'P',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q5',
                  'potential': 'GTH-PBE-q5'},
                 {'kind': 'S',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q6',
                  'potential': 'GTH-PBE-q6'},
                 {'kind': 'Cl',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q7',
                  'potential': 'GTH-PBE-q7'},
                 {'kind': 'Ar',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q8',
                  'potential': 'GTH-PBE-q8'},
                 {'kind': 'K',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q9',
                  'potential': 'GTH-PBE-q9'},
                 {'kind': 'Ca',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q10',
                  'potential': 'GTH-PBE-q10'},
                 {'kind': 'Sc',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q11',
                  'potential': 'GTH-PBE-q11'},
                 {'kind': 'Ti',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q12',
                  'potential': 'GTH-PBE-q12'},
                 {'kind': 'V',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q13',
                  'potential': 'GTH-PBE-q13'},
                 {'kind': 'Cr',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q14',
                  'potential': 'GTH-PBE-q14'},
                 {'kind': 'Mn',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q15',
                  'potential': 'GTH-PBE-q15'},
                 {'kind': 'Fe',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q16',
                  'potential': 'GTH-PBE-q16'},
                 {'kind': 'Co',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q17',
                  'potential': 'GTH-PBE-q17'},
                 {'kind': 'Ni',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q18',
                  'potential': 'GTH-PBE-q18'},
                 {'kind': 'Cu',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q11',
                  'potential': 'GTH-PBE-q11'},
                 {'kind': 'Zn',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q12',
                  'potential': 'GTH-PBE-q12'},
                 {'kind': 'Ga',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q13',
                  'potential': 'GTH-PBE-q13'},
                 {'kind': 'Ge',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q4',
                  'potential': 'GTH-PBE-q4'},
                 {'kind': 'As',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q5',
                  'potential': 'GTH-PBE-q5'},
                 {'kind': 'Se',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q6',
                  'potential': 'GTH-PBE-q6'},
                 {'kind': 'Br',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q7',
                  'potential': 'GTH-PBE-q7'},
                 {'kind': 'Kr',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q8',
                  'potential': 'GTH-PBE-q8'},
                 {'kind': 'Rb',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q9',
                  'potential': 'GTH-PBE-q9'},
                 {'kind': 'Sr',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q10',
                  'potential': 'GTH-PBE-q10'},
                 {'kind': 'Y',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q11',
                  'potential': 'GTH-PBE-q11'},
                 {'kind': 'Zr',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q12',
                  'potential': 'GTH-PBE-q12'},
                 {'kind': 'Nb',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q13',
                  'potential': 'GTH-PBE-q13'},
                 {'kind': 'Mo',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q14',
                  'potential': 'GTH-PBE-q14'},
                 {'kind': 'Tc',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q15',
                  'potential': 'GTH-PBE-q15'},
                 {'kind': 'Ru',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q16',
                  'potential': 'GTH-PBE-q16'},
                 {'kind': 'Rh',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q17',
                  'potential': 'GTH-PBE-q17'},
                 {'kind': 'Pd',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q18',
                  'potential': 'GTH-PBE-q18'},
                 {'kind': 'Ag',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q11',
                  'potential': 'GTH-PBE-q11'},
                 {'kind': 'Cd',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q12',
                  'potential': 'GTH-PBE-q12'},
                 {'kind': 'In',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q13',
                  'potential': 'GTH-PBE-q13'},
                 {'kind': 'Sn',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q14',  # ! or DZVP-MOLOPT-PBE-GTH-q4',
                  'potential': 'GTH-PBE-q14 ! or GTH-PBE-q4'},
                 {'kind': 'Sb',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q5',
                  'potential': 'GTH-PBE-q5'},
                 {'kind': 'Te',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q6',
                  'potential': 'GTH-PBE-q6'},
                 {'kind': 'I',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q7',
                  'potential': 'GTH-PBE-q7'},
                 {'kind': 'Xe',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q8',
                  'potential': 'GTH-PBE-q8'},
                 {'kind': 'Cs',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q9',
                  'potential': 'GTH-PBE-q9'},
                 {'kind': 'Ba',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q10',
                  'potential': 'GTH-PBE-q10'},
                 {'kind': 'Hf',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q12',
                  'potential': 'GTH-PBE-q12'},
                 {'kind': 'Ta',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q13',
                  'potential': 'GTH-PBE-q13'},
                 {'kind': 'W',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q14',
                  'potential': 'GTH-PBE-q14'},
                 {'kind': 'Re',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q15',
                  'potential': 'GTH-PBE-q15'},
                 {'kind': 'Os',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q16',
                  'potential': 'GTH-PBE-q16'},
                 {'kind': 'Ir',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q17',
                  'potential': 'GTH-PBE-q17'},
                 {'kind': 'Pt',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q18',
                  'potential': 'GTH-PBE-q18'},
                 {'kind': 'Au',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q19',  # ! or DZVP-MOLOPT-PBE-GTH-q11',
                  'potential': 'GTH-PBE-q19 ! or GTH-PBE-q11'},
                 {'kind': 'Hg',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q12',
                  'potential': 'GTH-PBE-q12'},
                 {'kind': 'Tl',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q13',
                  'potential': 'GTH-PBE-q13'},
                 {'kind': 'Pb',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q4',
                  'potential': 'GTH-PBE-q4'},
                 {'kind': 'Bi',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q5',
                  'potential': 'GTH-PBE-q5'},
                 {'kind': 'Po',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q6',
                  'potential': 'GTH-PBE-q6'},
                 {'kind': 'At',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q7',
                  'potential': 'GTH-PBE-q7'},
                 {'kind': 'Rn',
                  'basis_set': 'ORB DZVP-MOLOPT-PBE-GTH-q8',
                  'potential': 'GTH-PBE-q8'}]
    df = pd.DataFrame(data=data_list)
    df = df.set_index(keys='kind')
    return df

  def get_atoms(self):
    atoms = ase.build.molecule('H2O', vacuum=4,)
    constraint = ase.constraints.FixAtoms(
        mask=[atom.symbol == 'O' for atom in atoms])
    atoms.set_constraint(constraint=constraint)
    return atoms

  def get_calc(self,
               directory='my_examples/geo_opt/h2o',
               project_name='h2o',):

    if not os.path.exists(directory):
      os.makedirs(name=directory)
    calc = CP2K(working_directory=directory,
                project_name=project_name,)
    return calc

  def set_global(self, calc,
                 run_type="GEO_OPT",):
    """run_type: ---
    ENERGY Computes energy
    ENERGY_FORCE Computes energy and forces
    MD Molecular Dynamics
    GEO_OPT Geometry Optimization
    MC Monte Carlo
    SPECTRA Computes absorption Spectra
    DEBUG Performs a Debug analysis
    BSSE Basis set superposition error
    LR Linear Response
    PINT Path integral
    VIBRATIONAL_ANALYSIS Vibrational analysis
    BAND Band methods # 计算过渡态, 如 neb 方法
    CELL_OPT Cell optimization.

    Args:
        calc (pycp2k.CP2K): _description_
        run_type (str, optional): _description_. Defaults to "GEO_OPT".

    Returns:
        _type_: _description_
    """
    GLOBAL = calc.CP2K_INPUT.GLOBAL
    GLOBAL.Run_type = run_type
    GLOBAL.Project_name = os.path.join(calc.working_directory,
                                       calc.project_name)
    return calc

  def set_force_eval(self, atoms: ase.Atoms,
                     calc,
                     force_eval_method="QUICKSTEP",
                     Basis_set_file_name='BASIS_MOLOPT_UZH',  # 'BASIS_MOLOPT'
                     Potential_file_name='GTH_POTENTIALS',
                     xc_functional='PBE',
                     dft_multiplicity=None,
                     dft_uks=True,  # 是否考虑自旋极化计算
                     dft_cutoff=200,  # 单位Ry 1Ry=13.6 eV
                     dft_rel_cutoff=200*0.1,  # 通常为 dft_cutoff的 10%
                     CP2K_DATA_DIR='/usr/local/Cellar/cp2k/2024.2/share/cp2k/data',):
    """* force_eval_method:
    QS|QUICKSTEP Electronic structure methods (DFT, …),
    SIRIUS PW DFT using the SIRIUS library,
    FIST Molecular Mechanics,
    QMMM Hybrid quantum classical,
    EIP Empirical Interatomic Potential,
    NNP Neural Network Potentials,
    -----
    * xc_functional
    B3LYP B3LYP,
    PBE0 PBE0 (see note in section XC/XC_FUNCTIONAL/PBE),
    BLYP BLYP,
    BP BP,
    PADE PADE,
    LDA Alias for PADE,
    PBE PBE (see note in section XC/XC_FUNCTIONAL/PBE),
    OLYP OLYP,
    ---
    dft_uks: 是否考虑自旋极化计算

    Args:
        atoms (ase.Atoms): _description_
        calc (pycp2k.CP2K): _description_
        force_eval_method (str, optional): _description_. Defaults to "QS".
        Basis_set_file_name (str, optional): _description_. Defaults to 'BASIS_SET'.
        Potential_file_name (str, optional): _description_. Defaults to 'POTENTIAL'.
        xc_functional (str, optional): _description_. Defaults to 'PADE'.
        kind_list (list, optional): _description_. Defaults to ['H', 'O'].
        Basis_set_list (list, optional): _description_. Defaults to ['DZVP-GTH-PADE', 'DZVP-GTH-PADE'].
        Potential_list (list, optional): _description_. Defaults to ["GTH-PADE-q1", 'GTH-PADE-q6'].
        CP2K_DATA_DIR (str, optional): _description_. Defaults to '/usr/local/Cellar/cp2k/2024.2/share/cp2k/data'.

    Returns:
        _type_: _description_
    """

    # 力的评估
    FORCE_EVAL = calc.CP2K_INPUT.FORCE_EVAL_add()
    FORCE_EVAL.Method = force_eval_method
    FORCE_EVAL.PRINT.FORCES.Section_parameters = "ON"
    calc.create_cell(FORCE_EVAL.SUBSYS, atoms=atoms,)
    calc.create_coord(FORCE_EVAL.SUBSYS, atoms=atoms)
    # 选取基集和势
    # kind_list=['H', 'O']
    # Basis_set_list=['DZVP-GTH-PADE', 'DZVP-GTH-PADE']
    # Potential_list=["GTH-PBE", 'GTH-PBE']
    # for kind, Basis_set, Potential in zip(kind_list, Basis_set_list, Potential_list):
    #   KIND = FORCE_EVAL.SUBSYS.KIND_add(kind)
    #   KIND.Basis_set = Basis_set
    #   KIND.Potential = Potential
    # 选取基集和势
    df = self.get_df_basis_set_and_potential()
    for kind in set(atoms.get_chemical_symbols()):
      KIND = FORCE_EVAL.SUBSYS.KIND_add(kind)
      KIND.Basis_set = df.loc[kind].basis_set
      KIND.Potential = df.loc[kind].potential

    # DFT 参数
    DFT = FORCE_EVAL.DFT
    DFT.Basis_set_file_name = os.path.join(CP2K_DATA_DIR, Basis_set_file_name)
    DFT.Potential_file_name = os.path.join(CP2K_DATA_DIR, Potential_file_name)
    DFT.Multiplicity = dft_multiplicity
    DFT.Uks = dft_uks
    DFT.QS.Eps_default = 1.0E-5
    DFT.MGRID.Ngrids = 4
    DFT.MGRID.Cutoff = dft_cutoff
    DFT.MGRID.Rel_cutoff = dft_rel_cutoff
    # DFT.SCF.OT.Minimizer  = 'CG' # 默认就很好了
    # DFT.SCF.OT.PRECONDITIONER = 'FULL_ALL' # 默认就很好了
    DFT.PRINT.MULLIKEN.Filename = 'mulliken'  # 是否写入mulliken 电荷
    # DFT.PRINT.MULLIKEN.Common_iteration_levels = 1 #
    DFT.XC.XC_FUNCTIONAL.Section_parameters = xc_functional
    DFT.SCF.Scf_guess = "ATOMIC"
    DFT.SCF.Eps_scf = 1.0E-3
    DFT.SCF.Max_scf = 200
    DFT.SCF.DIAGONALIZATION.Section_parameters = "ON"
    DFT.SCF.DIAGONALIZATION.Algorithm = "STANDARD"
    DFT.SCF.MIXING.Section_parameters = "T"
    DFT.SCF.MIXING.Method = "BROYDEN_MIXING"
    DFT.SCF.MIXING.Alpha = 0.4
    DFT.SCF.MIXING.Nbroyden = 8
    # 加上这个出错不知道为什么
    # DFT.SCF.SMEAR.Section_parameters = 'ON'
    # DFT.SCF.SMEAR.Method =  'FERMI_DIRAC'
    # DFT.SCF.SMEAR.Electronic_temperature= '[K] 300'

    return calc

  def set_motion(self, atoms: ase.Atoms,
                 calc,
                 geo_opt_type='MINIMIZATION',
                 optimizer='BFGS',
                 is_neb=False):
    """ MOTION 分两块: GEO_OPT 和 CONSTRAINT
    * geo_opt_type: 
    MINIMIZATION Performs a geometry minimization. TRANSITION_STATE Performs a transition state optimization.
    * OPTIMIZER: {BFGS|LBFGS|CG}
    Args:
        atoms (ase.Atoms): _description_
        calc (pycp2k.CP2K): _description_
        optimizer (str, optional): _description_. Defaults to 'CG'.

    Returns:
        _type_: _description_
    """
    # GEO_OPT 参数
    MOTION = calc.CP2K_INPUT.MOTION
    if is_neb:
      MOTION.BAND.Band_type = 'CI-NEB'
      MOTION.BAND.Number_of_replica = 8
      MOTION.BAND.K_spring = 0.05
      MOTION.BAND.CI_NEB.Nsteps_it = 2
      MOTION.BAND.CONVERGENCE_CONTROL.Max_force = 0.001
      MOTION.BAND.CONVERGENCE_CONTROL.Rms_force = 0.005
      ob = MOTION.BAND.OPTIMIZE_BAND_add()
      ob.Opt_type = 'DIIS'
      ob.Optimize_end_points = False
      ob.DIIS.Max_steps = 400
      # ? 以后看 pycp2k 中的例子
      # MOTION.BAND.PROGRAM_RUN_INFO
      # MOTION.BAND.CONVERGENCE_INFO
      replica = MOTION.BAND.REPLICA_add()

    MOTION.GEO_OPT.Type = geo_opt_type
    MOTION.GEO_OPT.Max_iter = 200
    MOTION.GEO_OPT.Max_force = 1e-3
    MOTION.GEO_OPT.Max_dr = 5e-3
    MOTION.GEO_OPT.Rms_dr = 1e-2
    MOTION.GEO_OPT.Rms_force = 1e-2
    MOTION.GEO_OPT.Optimizer = optimizer
    MOTION.GEO_OPT.CG.Max_steep_steps = 0   # 都有默认值
    MOTION.GEO_OPT.CG.Restart_limit = 9e-1  # 都有默认值

    # 固定原子
    try:
      fix_list = atoms.constraints[0].get_indices()
      fix_list += 1
      fix1 = MOTION.CONSTRAINT.FIXED_ATOMS_add()
      fix1.Components_to_fix = "XYZ"
      fix1.List = ' '.join(map(str, fix_list))
    except:
      pass
    return calc

  def set_restart(self, calc,
                  Restart_file_name,
                  Restart_default=True,
                  ):
    calc.CP2K_INPUT.EXT_RESTART.Restart_file_name = Restart_file_name
    calc.CP2K_INPUT.EXT_RESTART.Restart_default = Restart_default
    return calc

  def write_input_file(self, calc,):
    calc.write_input_file()
    print(f"产生文件-> {calc.CP2K_INPUT.GLOBAL.Project_name}.inp")
    return None

  def set_dft_plus_U(self, calc,):
    force_eval = calc.CP2K_INPUT.FORCE_EVAL_add()
    DFT = force_eval.DFT
    DFT.Plus_u_method = 'MULLIKEN'
    ...
    # DFT.Plus_u_method.
    # &KIND Co2uBASIS SET DZVP-GTH-MOLOPT-SR-GTHPOTENTIAL GTH-PBE-q17&DFT PLUS U
    # EPS_U_RAMPING 1.0E-3
    pass

  def vib_analysis(self, calc,):
    VIBRATIONAL_ANALYSIS = calc.CP2K_INPUT.VIBRATIONAL_ANALYSIS
    VIBRATIONAL_ANALYSIS.Intensities
    VIBRATIONAL_ANALYSIS.Nproc_rep = 1
    VIBRATIONAL_ANALYSIS.Dx = 0.001  # 用于分析是否有虚频？
    vib_print = VIBRATIONAL_ANALYSIS.PRINT
    vib_print.PROGRAM_RUN_INFO = 'MEDIUM'
    return calc

  def run(self, calc,):
    """
    * 自带的方法: 
    - calc.mpi_n_processes =2 
    - calc.run()
    --- 
    自带的run 出问题, 以后考虑解决

    Args:
        directory (_type_): _description_
        project_name (_type_): _description_
    """

    fin = calc.CP2K_INPUT.GLOBAL.Project_name + '.inp'
    fout = calc.CP2K_INPUT.GLOBAL.Project_name + '.out'
    os.system(command=f'cp2k.ssmp -i {fin} -o {fout}')
    print('计算完成')
    return None

  def cp2k_calc_wrapper(self, directory='my_examples/h2o',
                        project_name='h2o',
                        run_type='ENERGY_FORCE|GEO_OPT',
                        geo_opt_type='MINIMIZATION',
                        optimizer='BFGS',
                        ):
    """calc_energy_add_smearing(self):
    # To add smearing, we need to add the subsection ''SMEAR'' inside subsection SCF:
    # &SMEAR ON
    #   METHOD FERMI_DIRAC
    #   ELECTRONIC_TEMPERATURE [K] 300
    # &END SMEAR

    Args:
        directory (str, optional): _description_. Defaults to 'my_examples/h2o'.
        project_name (str, optional): _description_. Defaults to 'h2o'.
        run_type (str, optional): _description_. Defaults to 'ENERGY_FORCE|GEO_OPT'.
        geo_opt_type (str, optional): _description_. Defaults to 'MINIMIZATION'.
        optimizer (str, optional): _description_. Defaults to 'BFGS'.
    """

    atoms = self.get_atoms()
    calc = self.get_calc(directory=directory,
                         project_name=project_name)
    calc = self.set_global(calc=calc, run_type=run_type)
    calc = self.set_force_eval(atoms=atoms, calc=calc,)
    if 'ENERGY' not in run_type:
      calc = self.set_motion(atoms=atoms, calc=calc,
                             geo_opt_type=geo_opt_type,
                             optimizer=optimizer,)
    self.write_input_file(calc=calc)
    self.run(calc=calc)

    pass

  def energy_force_example(self, atoms=ase.build.bulk('Si'),
                           directory='xxx',
                           project_name='Si',
                           run_type="ENERGY_FORCE",
                           force_eval_method="Quickstep",
                           Basis_set_file_name='BASIS_SET',
                           Potential_file_name='GTH_POTENTIALS',
                           xc_functional='PADE',
                           kind_list=['Si'],
                           Basis_set_list=['DZVP-GTH-PADE'],
                           Potential_list=["GTH-PADE-q4"],
                           CP2K_DATA_DIR='/usr/local/Cellar/cp2k/2024.2/share/cp2k/data',):
    # 获取输入文件
    if not os.path.exists(directory):
      os.makedirs(name=directory)

    calc = CP2K(working_directory=directory,
                project_name=project_name,)
    # calc.mpi_n_processes = 2

    # ==================== Define shortcuts for easy access =========================
    CP2K_INPUT = calc.CP2K_INPUT
    GLOBAL = CP2K_INPUT.GLOBAL
    # Repeatable items have to be first created
    FORCE_EVAL = CP2K_INPUT.FORCE_EVAL_add()
    SUBSYS = FORCE_EVAL.SUBSYS
    DFT = FORCE_EVAL.DFT
    SCF = DFT.SCF

    # ======================= Write the simulation input ============================
    GLOBAL.Run_type = run_type
    FORCE_EVAL.Method = force_eval_method
    FORCE_EVAL.PRINT.FORCES.Section_parameters = "ON"
    DFT.Basis_set_file_name = os.path.join(CP2K_DATA_DIR, Basis_set_file_name)
    DFT.Potential_file_name = os.path.join(CP2K_DATA_DIR, Potential_file_name)
    DFT.QS.Eps_default = 1.0E-7
    DFT.MGRID.Ngrids = 4
    DFT.MGRID.Cutoff = 200
    DFT.MGRID.Rel_cutoff = 60
    DFT.XC.XC_FUNCTIONAL.Section_parameters = xc_functional
    SCF.Scf_guess = "ATOMIC"
    SCF.Eps_scf = 1.0E-7
    SCF.Max_scf = 300
    SCF.DIAGONALIZATION.Section_parameters = "ON"
    SCF.DIAGONALIZATION.Algorithm = "STANDARD"
    SCF.MIXING.Section_parameters = "T"
    SCF.MIXING.Method = "BROYDEN_MIXING"
    SCF.MIXING.Alpha = 0.4
    SCF.MIXING.Nbroyden = 8
    # Section_parameters can be provided as argument.
    for kind, Basis_set, Potential in zip(kind_list, Basis_set_list, Potential_list):
      KIND = SUBSYS.KIND_add(kind)
      KIND.Basis_set = Basis_set
      KIND.Potential = Potential
    calc.create_cell(SUBSYS, atoms=atoms,)
    calc.create_coord(SUBSYS, atoms=atoms)

    # ============ Run the simulation or just write the input file ================
    calc.write_input_file()
    print(f"产生文件-> {os.path.join(directory, project_name+'.inp')}")
    # calc.run()
    pass

  def geo_opt_example(self,
                      directory='my_examples/geo_opt/h2o',
                      project_name='h2o',
                      run_type="GEO_OPT",
                      force_eval_method="QS",
                      Basis_set_file_name='BASIS_SET',
                      Potential_file_name='POTENTIAL',
                      xc_functional='PADE',
                      kind_list=['H', 'O'],
                      Basis_set_list=['DZVP-GTH-PADE', 'DZVP-GTH-PADE'],
                      Potential_list=["GTH-PADE-q1", 'GTH-PADE-q6'],
                      CP2K_DATA_DIR='/usr/local/Cellar/cp2k/2024.2/share/cp2k/data',):

    atoms = ase.build.molecule('H2O', vacuum=4,)
    constraint = ase.constraints.FixAtoms(
        mask=[atom.symbol == 'O' for atom in atoms])
    atoms.set_constraint(constraint=constraint)

    # ================= Define and setup the calculator object ======================
    if not os.path.exists(directory):
      os.makedirs(name=directory)

    calc = CP2K(working_directory=directory,
                project_name=project_name,)
    # calc.mpi_n_processes = 2

    # ==================== Define shortcuts for easy access =========================
    CP2K_INPUT = calc.CP2K_INPUT
    GLOBAL = CP2K_INPUT.GLOBAL
    GLOBAL.Run_type = run_type
    CP2K_INPUT.GLOBAL.Project_name = os.path.join(directory, project_name)

    # 力的评估
    FORCE_EVAL = CP2K_INPUT.FORCE_EVAL_add()
    FORCE_EVAL.Method = force_eval_method
    FORCE_EVAL.PRINT.FORCES.Section_parameters = "ON"
    # Section_parameters can be provided as argument.
    for kind, Basis_set, Potential in zip(kind_list, Basis_set_list, Potential_list):
      KIND = FORCE_EVAL.SUBSYS.KIND_add(kind)
      KIND.Basis_set = Basis_set
      KIND.Potential = Potential
    calc.create_cell(FORCE_EVAL.SUBSYS, atoms=atoms,)
    calc.create_coord(FORCE_EVAL.SUBSYS, atoms=atoms)

    # GEO_OPT 参数
    MOTION = CP2K_INPUT.MOTION
    MOTION.GEO_OPT.Type = 'MINIMIZATION'
    MOTION.GEO_OPT.Optimizer = 'CG'  # "BFGS"
    MOTION.GEO_OPT.Max_iter = 20
    MOTION.GEO_OPT.Max_dr = 5e-3
    MOTION.GEO_OPT.Max_force = 1e-2
    MOTION.GEO_OPT.Rms_dr = 1e-2
    MOTION.GEO_OPT.Rms_force = 1e-2
    MOTION.GEO_OPT.CG.Max_steep_steps = 0
    MOTION.GEO_OPT.CG.Restart_limit = 9e-1
    # 固定原子
    fix_list = atoms.constraints[0].get_indices()
    fix_list += 1
    fix1 = MOTION.CONSTRAINT.FIXED_ATOMS_add()
    fix1.Components_to_fix = "XYZ"
    fix1.List = ' '.join(map(str, fix_list))

    # DFT 参数
    DFT = FORCE_EVAL.DFT
    DFT.Basis_set_file_name = os.path.join(CP2K_DATA_DIR, Basis_set_file_name)
    DFT.Potential_file_name = os.path.join(CP2K_DATA_DIR, Potential_file_name)
    DFT.QS.Eps_default = 1.0E-5
    DFT.MGRID.Ngrids = 4
    DFT.MGRID.Cutoff = 200
    DFT.MGRID.Rel_cutoff = 30
    DFT.XC.XC_FUNCTIONAL.Section_parameters = xc_functional
    DFT.SCF.Scf_guess = "ATOMIC"
    DFT.SCF.Eps_scf = 1.0E-3
    DFT.SCF.Max_scf = 200
    DFT.SCF.DIAGONALIZATION.Section_parameters = "ON"
    DFT.SCF.DIAGONALIZATION.Algorithm = "STANDARD"
    DFT.SCF.MIXING.Section_parameters = "T"
    DFT.SCF.MIXING.Method = "BROYDEN_MIXING"
    DFT.SCF.MIXING.Alpha = 0.4
    DFT.SCF.MIXING.Nbroyden = 8

    # ============ Run the simulation or just write the input file ================
    calc.write_input_file()
    print(f"产生文件-> {os.path.join(directory, project_name+'.inp')}")
    # calc.run()
    return calc


class Cp2kLearn():
  def __init__(self) -> None:
    """文字教程:http://bbs.keinsci.com/thread-19009-1-1.html
    视频教程:https://www.bilibili.com/video/BV1Y54y1e7Yx/
    官网教程: https://manual.cp2k.org/trunk/
    https://manual.cp2k.org/trunk/index.html
    github: https://github.com/cp2k
    官网: https://www.cp2k.org/howto:compile_on_macos
    例子: https://github.com/cp2k/cp2k-examples
    # 学习例子
    https://www.cp2k.org/events:2018_summer_school:index 
    """
    self.initialization_cp2k_env()
    pass

  def install(self):
    """conda install cp2k
    brew install cp2k
    单机多核 → ssmp（例如16核工作站）
    集群计算 → psmp（例如超算平台）
    小体系测试 → ssmp（内存占用更优）
    大体系计算 → psmp（并行效率更高）
    """
    pass

  def initialization_cp2k_env(self,
                              CP2K_DATA_DIR='/opt/homebrew/Cellar/cp2k/2025.1/share/cp2k/data'):
    """初始化cp2k使用环境
    https://wiki.fysik.dtu.dk/ase/ase/calculators/cp2k.html#module-ase.calculators.cp2k
    # 在cp2k源版本附带的cp2k/data/中可以找到基集和伪势文件的列表。这些应该涵盖大多数常用元素。但是，用户需要为给定的计算生成自己的主输入文件。
    # /opt/homebrew/Cellar/cp2k/2025.1/share/cp2k/data
    # /Users/wangjinlong/job/soft_learn/cp2k_learn/package/cp2k-master/data
    """
    # 在python环境中执行
    cp2k_shell_path = os.popen('which cp2k.psmp').read().strip()
    os.environ['CP2K_DATA_DIR'] = CP2K_DATA_DIR
    # The command used by the calculator to launch the CP2K-shell is cp2k_shell. To run a parallelized simulation use something like this:
    # CP2K.command="env OMP_NUM_THREADS=2 mpiexec -np 4 cp2k_shell.psmp"
    os.environ['ASE_CP2K_COMMAND'] = f'{cp2k_shell_path}'

    self.CP2K_DATA_DIR = CP2K_DATA_DIR
    pass

  def get_atoms(self):
    atoms = ase.build.molecule('H2O', vacuum=4,)
    constraint = ase.constraints.FixAtoms(
        mask=[atom.symbol == 'O' for atom in atoms])
    atoms.set_constraint(constraint=constraint)
    return atoms

  def get_calc(self,
               directory='my_examples/h2o',
               label='h2o',
               basis_set_file='BASIS_MOLOPT',
               basis_set='DZVP-MOLOPT-SR-GTH',
               potential_file='POTENTIAL',
               pseudo_potential='auto',
               cutoff=400,
               xc='PBE',  # 'LDA'
               force_eval_method='Quickstep',
               print_level='LOW',
               charge=0,
               inp='',
               max_scf=50,
               multiplicity=None,
               stress_tensor=True,
               poisson_solver='auto',
               uks=True,
               set_pos_file=False,
               ):
    """uks: 是否考虑自旋极化计算
    """
    # 配置 CP2K 计算器
    basis_set_file = os.path.join(self.CP2K_DATA_DIR, basis_set_file)
    potential_file = os.path.join(self.CP2K_DATA_DIR, potential_file)
    calc = ase.calculators.cp2k.CP2K(directory=directory,
                                     label=label,
                                     multiplicity=multiplicity,
                                     uks=uks,
                                     basis_set=basis_set,
                                     basis_set_file=basis_set_file,
                                     pseudo_potential=pseudo_potential,
                                     potential_file=potential_file,
                                     cutoff=cutoff,
                                     xc=xc,
                                     force_eval_method=force_eval_method,
                                     print_level=print_level,
                                     charge=charge,
                                     inp=inp,
                                     max_scf=max_scf,
                                     stress_tensor=stress_tensor,
                                     poisson_solver=poisson_solver,
                                     set_pos_file=set_pos_file,
                                     )
    return calc

  def write_input_file(self, calc: ase.calculators.cp2k.CP2K,):
    if not os.path.exists(calc.directory):
      os.makedirs(name=calc.directory)

    inp = calc._generate_input()
    inp_fn = calc.label + '.inp'
    calc._write_file(inp_fn, inp)
    print(f'产生文件-> {inp_fn}')
    return

  def run(self, calc: ase.calculators.cp2k.CP2K):
    """自带的 atoms.get_potential_energy() 出问题, 以后考虑解决
    """

    fin = calc.label + '.inp'
    fout = calc.label + '.out'
    os.system(command=f'cp2k.ssmp -i {fin} -o {fout}')
    print('计算完成')
    pass

  def cp2k_calc_wrapper(self,
                        atoms: ase.Atoms,
                        directory='my_examples/h2o',
                        label='h2o',
                        basis_set_file='BASIS_MOLOPT',
                        potential_file='GTH_POTENTIALS',
                        xc='PBE',
                        force_eval_method='Quickstep',
                        uks=True,
                        only_write_file=True,
                        **keywords,):

    calc = self.get_calc(atoms=atoms,
                         directory=directory,
                         label=label,
                         basis_set_file=basis_set_file,
                         potential_file=potential_file,
                         xc=xc,
                         force_eval_method=force_eval_method,
                         uks=uks,
                         **keywords,
                         )
    self.write_input_file(calc=calc)
    if not only_write_file:
      self.run(calc=calc)
    return calc
