import mace.calculators
import rdkit.Chem
import rdkit.Chem.Draw
import ase.io
import numpy as np
import aseMolec.anaAtoms
import aseMolec.extAtoms
import os
import collections
from matplotlib import pyplot as plt
import tqdm
import aseMolec.pltProps
import ase.md.velocitydistribution
import random
import ase.units
import ase.md.langevin
import ase.md.velocitydistribution
import IPython.display
import time
import ase.db


class MaceLearn:
  def __init__(self):
    r"""
    MACE提供了快速准确的机器学习原子间势和高阶等变消息传递。要使用cuEquivariance库进行更快的训练和推理，请阅读使用cuEquivariance库的CUDA加速部分。

    mace文档: https://mace-docs.readthedocs.io/en/latest/guide/installation.html#installations

    安装torch-> https://pytorch.org/get-started/locally/

    github: https://github.com/ACEsuit/mace?tab=readme-ov-file

    ---
    @article{batatia2023foundation,
      title={A foundation model for atomistic materials chemistry},
      author={Ilyes Batatia and Philipp Benner and Yuan Chiang and Alin M. Elena and Dávid P. Kovács and Janosh Riebesell and Xavier R. Advincula and Mark Asta and William J. Baldwin and Noam Bernstein and Arghya Bhowmik and Samuel M. Blau and Vlad Cărare and James P. Darby and Sandip De and Flaviano Della Pia and Volker L. Deringer and Rokas Elijošius and Zakariya El-Machachi and Edvin Fako and Andrea C. Ferrari and Annalena Genreith-Schriever and Janine George and Rhys E. A. Goodall and Clare P. Grey and Shuang Han and Will Handley and Hendrik H. Heenen and Kersti Hermansson and Christian Holm and Jad Jaafar and Stephan Hofmann and Konstantin S. Jakob and Hyunwook Jung and Venkat Kapil and Aaron D. Kaplan and Nima Karimitari and Namu Kroupa and Jolla Kullgren and Matthew C. Kuner and Domantas Kuryla and Guoda Liepuoniute and Johannes T. Margraf and Ioan-Bogdan Magdău and Angelos Michaelides and J. Harry Moore and Aakash A. Naik and Samuel P. Niblett and Sam Walton Norwood and Niamh O'Neill and Christoph Ortner and Kristin A. Persson and Karsten Reuter and Andrew S. Rosen and Lars L. Schaaf and Christoph Schran and Eric Sivonxay and Tamás K. Stenczel and Viktor Svahn and Christopher Sutton and Cas van der Oord and Eszter Varga-Umbrich and Tejs Vegge and Martin Vondrák and Yangshuai Wang and William C. Witt and Fabian Zills and Gábor Csányi},
      year={2023},
      eprint={2401.00096},
      archivePrefix={arXiv},
      primaryClass={physics.chem-ph}
    }

    MACE-Universal by Yuan Chiang, 2023, Hugging Face, Revision e5ebd9b, DOI: 10.57967/hf/1202, URL: https://huggingface.co/cyrusyc/mace-universal
    """
    self.model_mace_mp = '/Users/wangjinlong/job/soft_learn/soft_learn_project/mace_learn/mace-foundations/mace-mpa-0-medium.model'
    pass

  def install(self):
    """
    conda install -y pytorch torchvision torchaudio -c pytorch

    ---
    pip install --upgrade pip
    pip install mace-torch
    pip3 install cuequivariance cuequivariance_torch
    安装torch, 打开网址获得安装方法-> https://pytorch.org/get-started/locally/  # pip3 install torch torchvision torchaudio
    2. pip installation from source
    To install via pip, follow the steps below:
    git clone https://github.com/ACEsuit/mace.git
    pip install ./mace
    ---
    !git clone https://github.com/imagdau/Tutorials.git  # 安装教学代码
    !pip install mace-torch xtb nglview ipywidgets rdkit x3dase
    !pip install git+https://github.com/imagdau/aseMolec@main 
    # !pip install -U numpy==2.0
    %cd Tutorials
    ---
    conda install -c conda-forge xtb-python  # Python 接口（绑定 xtb 程序）	提供从 Python 脚本调用 xtb 的能力
    conda install -c conda-forge tqdm
    pip install mace-torch nglview ipywidgets rdkit
    !pip install git+https://github.com/imagdau/aseMolec@main
    --- 安装 aseMolec
    pip install git+https://github.com/imagdau/aseMolec.git
    """
    pass

  def get_calc(self,
               model_paths=[
                   '/Users/wangjinlong/job/soft_learn/soft_learn_project/mace_learn/mace-foundations/mace-mpa-0-medium.model'],
               device='cpu',
               default_dtype="float32"):
    # we can use MACE as a calculator in ASE!
    mace_calc = mace.calculators.MACECalculator(
        model_paths=model_paths,
        device=device,
        default_dtype=default_dtype)
    return mace_calc

  def get_calc_macemp(self,
                      directory='.',
                      model=None,
                      default_dtype='float64',
                      device='cpu'):
    """ 64 for 几何优化  32 for MD
    --- 
    基础模型 目录: /Users/wangjinlong/job/soft_learn/soft_learn_project/mace_learn/mace-foundations
    优先使用:
    MACE-matpes-pbe-omat-ft.model
    MACE-matpes-r2scan-omat-ft.model
    """
    if model is None:
      model = self.model_mace_mp
    macemp = mace.calculators.mace_mp(
        directory=directory,
        model=model,
        device=device,
        default_dtype=default_dtype,
    )  # 或者 model='small'
    return macemp

  def sel_by_info_val_example(self, db,
                              info_key='Nmols', info_val=1):
    db_sel = aseMolec.extAtoms.sel_by_info_val(
        db=db, info_key=info_key, info_val=info_val)
    return db_sel

  def get_prop_bind(self, db, type='bind',
                    prop='_xtb', peratom=True):
    prop = aseMolec.extAtoms.get_prop(
        db=db, type=type, prop=prop, peratom=peratom)
    return prop

  def get_prop_energy(self, db, type='info',
                      prop='energy_xtb', peratom=True):
    prop = aseMolec.extAtoms.get_prop(
        db=db, type=type, prop=prop, peratom=peratom)
    return prop

  def get_prop_forces(self, db, type='arrays',
                      prop='forces_xtb',):
    prop_arr = aseMolec.extAtoms.get_prop(
        db=db, type=type, prop=prop, peratom=False)
    prop_arr_flatten = np.concatenate(prop_arr).flatten()
    return prop_arr_flatten

  def plot_prop(self, prop1, prop2,
                title=r'Energy $(\rm eV/atom)$ ',
                labs=['XTB', 'MACE'],
                rel=False):
    aseMolec.pltProps.plot_prop(prop1=prop1, prop2=prop2,
                                title=title, labs=labs, rel=rel)
    return

  def extract_molecs(self, db,
                     old_energy_tag='energy_xtb',
                     old_forces_tag='forces_xtb',
                     intra_inter=True):
    """
    使得db 获得每个分子的力信息
    We can also extract the molecules from the configs and plot the translational and rotational vibrational modes.
    ---
    Note that the energy and forces are stored in the `atoms.info` and `atoms.arrays` respectively. For the sake of simplicity, we will rename the keys to `energy` and `forces` for consistency.
    at.arrays['forces_trans'] 
    at.arrays['forces_rot']
    at.arrays['forces_vib']
    """
    aseMolec.extAtoms.rename_prop_tag(
        db=db, oldtag=old_energy_tag, newtag='energy')  # Backward compatibility
    aseMolec.extAtoms.rename_prop_tag(
        db=db, oldtag=old_forces_tag, newtag='forces')  # Backward compatibility
    aseMolec.anaAtoms.extract_molecs(db=db, intra_inter=intra_inter)
    return

  def get_rdf(self, traj, rmax=5, nbins=50):
    for at in traj:
      at.pbc = True  # create a fake box for rdf compatibility
      at.cell = [100, 100, 100]
    # aseMolec provides functionality to compute RDFs
    rdf = aseMolec.anaAtoms.compute_rdfs_traj_avg(
        traj=traj, rmax=rmax, nbins=nbins)
    return rdf

  def rdf_plot(self, rdf, tag, label, alpha=0.7, linewidth=3):
    """tag: choose one of 'HH_intra', 'HC_intra', 'HO_intra', 'CC_intra', 'CO_intra', 'OO_intra'"""
    plt.plot(rdf[1], rdf[0][tag], '.-',
             label=label, alpha=alpha, linewidth=linewidth)
    return

  def conver_train_args_dict_to_args_list(self, args_dict):
    """
    --- 或者这样
    args_list = [k if v is None else f'{k}={v}' for k,
                    v in args_dict.items()]
    """

    args_list = []
    for k, v in args_dict.items():
      args_list.append(k)
      if v is None:
        continue
      args_list.append(str(v))  # 不要加额外的引号
    return args_list

  def run_mace_run_train(self, args_dict,
                         is_remove=False):
    args_list = self.conver_train_args_dict_to_args_list(
        args_dict)  # 转换为命令行参数列表
    from soft_learn_project import subprocessLearn
    subprocessLearn.SubprocessLearn().CLI_popen(
        directory='.',
        args=["mace_run_train",
              *args_list]
    )
    # remove checkpoints since they may cause errors on retraining a model with the same name but a different architecture
    if is_remove:
      import glob
      for file in glob.glob("MACE_models/*_run-*.model"):
        os.remove(file)
      for file in glob.glob("MACE_models/*.pt"):
        os.remove(file)
    return None

  def train_args_dict(self,
                      args_mod_dict={"--name": "mace02_com1",
                                     "--model_dir": 'MACE_models',
                                     "--log_dir": 'MACE_models',
                                     "--checkpoints_dir": 'MACE_models',
                                     "--results_dir": 'MACE_models',
                                     "--train_file": "/Users/wangjinlong/job/soft_learn/soft_learn_project/mace_learn/Tutorials/data/solvent_xtb_train_20.xyz",
                                     "--valid_file": "/Users/wangjinlong/job/soft_learn/soft_learn_project/mace_learn/Tutorials/data/solvent_xtb_train_50.xyz",
                                     "--test_file": "/Users/wangjinlong/job/soft_learn/soft_learn_project/mace_learn/Tutorials/data/solvent_xtb_test.xyz", },
                      ):
    args_dict = {"--model": "MACE",
                 "--num_interactions": 2,
                 "--num_channels": 16,
                 "--max_L": 0,
                 "--correlation": 2,
                 "--r_max": 4.0,
                 "--max_ell": 2,
                 "--name": 'xx',
                 "--model_dir": 'xx',
                 "--log_dir": 'xx',
                 "--checkpoints_dir": 'xx',
                 "--results_dir": 'xx',
                 "--train_file": 'xx',
                 "--valid_file": 'xx',
                 "--test_file": 'xx',
                 "--E0s": "average",
                 "--energy_key": "energy_xtb",
                 "--forces_key": "forces_xtb",
                 "--device": 'cpu',
                 "--batch_size": 10,
                 "--max_num_epochs": 300,
                 "--seed": 123,
                 "--swa": None,
                 }

    args_dict.update(args_mod_dict)
    return args_dict

  def fine_tune_MACE_MP_args_dict(self, args_mod_dict):
    args_dict = {"--name": "finetuned_MACE",
                 "--foundation_model": "/Users/wangjinlong/job/soft_learn/soft_learn_project/mace_learn/mace-foundations/mace-mp-0_small.model",
                 "--train_file": "/Users/wangjinlong/job/soft_learn/soft_learn_project/mace_learn/Tutorials/data/solvent_xtb_train_50.xyz",
                 "--valid_fraction": 0.60,
                 "--test_file": "/Users/wangjinlong/job/soft_learn/soft_learn_project/mace_learn/Tutorials/data/solvent_xtb_test.xyz",
                 "--energy_weight": 1.0,
                 "--forces_weight": 1.0,
                 "--energy_key": "energy_xtb",
                 "--forces_key": "forces_xtb",
                 "--lr": 0.01,
                 "--scaling": "rms_forces_scaling",
                 "--batch_size": 10,
                 "--max_num_epochs": 50,
                 "--ema": None,
                 "--ema_decay": 0.99,
                 "--amsgrad": None,
                 "--default_dtype": "float64",
                 "--device": 'cpu',
                 "--seed": 3,
                 }
    args_dict.update(args_mod_dict)
    return args_dict

  # --- 我自己的学习过程

  def geo_opt_example(self, atoms,):
    from soft_learn_project.gpaw_learn import gpawLearn
    gp = gpawLearn.GpawLearn()
    atoms = gp.Model.get_atoms_normal_crsytal(name='W')
    atoms.cell *= 1.1
    la = gp.Model.get_lc_a_from_atoms(atoms_relaxed=atoms)
    print(la)
    calc = self.get_calc_macemp(
        directory='/Users/wangjinlong/my_server/my/W_Re_potential/database_for_WReHe_gpaw/W_bulk',)
    atoms = gp.AseLearn.calc_lattice_constant(atoms=atoms,
                                              calc=calc,
                                              is_save_traj=False,
                                              fmax=0.01)
    la = gp.Model.get_lc_a_from_atoms(atoms_relaxed=atoms)
    print(la)
    pass

  def get_data_set(self,
                   fname='/Users/wangjinlong/my_server/my/W_Re_potential/database_for_WReHe_gpaw/data_set.xyz'):
    from soft_learn_project.gpaw_learn import gpawLearn
    gp = gpawLearn.GpawLearn()
    al = []
    gp.DataBase.db = ase.db.connect(
        '/Users/wangjinlong/my_server/my/W_Re_potential/database_for_WReHe_gpaw/W_Re_He.json')
    for row in gp.DataBase.db.select():
      atoms = row.toatoms()
      calc = gp.get_calc(directory=row.directory,)
      if atoms.__len__() == 1:
        atoms.info['config_type'] = 'IsolatedAtom'
      atoms.info['energy_gpaw'] = calc.get_potential_energy()
      atoms.arrays['forces_gpaw'] = calc.get_forces()
      al.append(atoms)

    ase.io.write(fname, al)
    return None


class Turtorial(MaceLearn):
  def __init__(self):
    """https://github.com/imagdau/Tutorials?tab=readme-ov-file
    """
    super().__init__()
    pass

  def view_data(self):
    # SMILES strings for each molecule
    sm_dict = {
        'VC': 'c1coc(=O)o1',
        'EC': 'C1COC(=O)O1',
        'PC': 'CC1COC(=O)O1',
        'DMC': 'COC(=O)OC',
        'EMC': 'CCOC(=O)OC',
        'DEC': 'CCOC(=O)OCC'
    }

    rdkit.Chem.MolFromSmiles(sm_dict['VC'])
    # 绘制分子的3D结构
    image = rdkit.Chem.Draw.MolsToGridImage(
        [rdkit.Chem.MolFromSmiles(sm_dict[mol]) for mol in sm_dict],
        legends=list(sm_dict.keys()))
    return image

  def get_db_initial(self, fname='data/solvent_configs.xyz',):
    # read in list of configs
    db = ase.io.read(fname, ':')
    # print("Number of configs in database: ", len(db))
    # print("Number of atoms in each config: ", np.array([len(at) for at in db]))
    # print("Number of atoms in the smallest config: ", np.min(
    #     [len(at) for at in db]))  # test if database contains isolated atoms
    # print("Information stored in config.info: \n", db[10].info)  # check info
    # print("Information stored in config.arrays: \n", db[10].arrays)
    return db

  def get_db_identify_molecules(self, initial_db=None,
                                fname='data/solvent_molecs.xyz'):
    r"""此时，每个配置都是原子的集合：原子序数(Z)和位置(R)，没有其他信息。让我们来识别分子并标记分子簇。这将使它更容易检查数据集，并稍后测试描述分子间相互作用的潜力的准确性。分子识别是使用[aseMolec包]（https://github.com/imagdau/aseMolec）中的‘ wrap_molecules ’函数实现的，如图所示为前100帧‘ db[:100] ’。
    ---
    Note the additional information for each atomic config: number of molecules `Nmols`, molecular composition `Comp` (e.g `DEC(1):EC(1)` means the config comprises a dimer with 1 DEC molecule and 1 EC molecule) and molecular ID `molID`. Running the code for the full 5000 configurations can be slow, let's just load the final result (`data/solvent_molecs.xyz`) and inspect the distribution of configs by number of molecules:
    """
    if initial_db is None:
      initial_db = self.get_db_initial()
    if os.path.exists(fname):
      return ase.io.read(fname, ':')
    # identify molecules and label molecular clusters, showcase: first 100 frames
    aseMolec.anaAtoms.wrap_molecs(initial_db[:], prog=False)
    ase.io.write(fname, initial_db)  # save full result

    # print("Information stored in config.info: \n", db[10].info)
    # print("Information stored in config.arrays: \n", db[10].arrays)
    # view(db[10])
    return initial_db

  def dentify_molecules_view(self):

    db = ase.io.read('data/solvent_molecs.xyz', ':')
    # collect Nmols information across all data
    Nmols = np.array([at.info['Nmols'] for at in db])
    # db[0].info
    plt.hist(Nmols, align='left', bins=[1, 2, 3, 4, 5, 6, 7], rwidth=0.8)
    plt.xlabel('# Molecs')
    plt.ylabel('# Configs comprising that # Molecs')

  def get_comp_dict_identify_molecules_check_distribution_molecular(self,
                                                                    db=None):
    if db is None:
      db = self.get_db_identify_molecules()
    # check the distribution of molecular

    comp_dict = {}  # create a dictionary of compositions for each cluster size
    for Nmol in range(1, 7):
      comp_dict[Nmol] = dict(collections.Counter(
          [at.info['Comp'] for at in aseMolec.extAtoms.sel_by_info_val(
              db=db, info_key='Nmols', info_val=Nmol)]))

    Nmol = 6  # show distribution of compositions for cluster size 6
    # print(comp_dict[Nmol])
    x = plt.pie(comp_dict[Nmol].values(),
                labels=comp_dict[Nmol].keys(),
                explode=10/(25+np.array(list(comp_dict[Nmol].values()))),
                rotatelabels=True)
    return comp_dict

  def get_db_add_isolated_atoms(self,
                                db=None):
    r"""
    We convinced ourselves the training set is quite diverse, it samples many compositions and molecular cluster sizes. It is time to prepare the reference data (energies, forces) to train the model on. We will do this using the Semiempirical Tight Binding level of theory with [XTB](https://xtb-docs.readthedocs.io/en/latest/contents.html). This may be less accurate than other methods specialized for these systems, but it is fast and it will later allow us to test MLIP errors on-the-fly.

    Notice the data set contains isolated molecules but no isolated atoms. MACE (and other MLIPs) fit to atomization energies (eV) which is total energy minus the energy of each atom in vacuum $(E^{0})$:
    $$
    E^{\rm atm} = E^{\rm tot}-\sum_i^{N} E^{0}
    $$

    In our specific example, all molecules comprise of three chemical elements and we will need to compute $(E^{0})$ for each of them:

    $$
    E^{\rm atm} = E^{\rm tot}-\sum_i^{N_H} E^{H}_i-\sum_i^{N_C} E^{C}_i-\sum_i^{N_O} E^{O}_i
    $$

    Let us add three frames containing Hydrogen H, Carbon C and Oxygen O to the dataset and label them as `config_type=IsolatedAtom`
    """
    if db is None:
      db = self.get_db_identify_molecules()
    # add isolated atoms to the database
    db = [ase.Atoms('H'), ase.Atoms('C'), ase.Atoms('O')]+db

    for at in db[:3]:
      at.info['config_type'] = 'IsolatedAtom'
    # print("Number of configs in database: ", len(db))
    return db

  def get_db_labeling_Data_XTB_Values(self,
                                      db=None,
                                      fname='data/solvent_xtb.xyz'):
    if os.path.exists(fname):
      db = ase.io.read(fname, ':')
      return db
    else:
      if db is None:
        db = self.get_db_add_isolated_atoms()
      from soft_learn_project import xtbPythonLearn
      xl = xtbPythonLearn.XtbPythonLearn()
      xtb_calc = xl.get_calc(method="GFN2-xTB")

      for at in tqdm.tqdm(db[:15]):  # showcase: first 15 frames
        at.calc = xtb_calc
        at.info['energy_xtb'] = at.get_potential_energy()
        at.arrays['forces_xtb'] = at.get_forces()
      ase.io.write(fname, db)  # save full result

      # print("Information stored in config.info: \n", db[13].info)  # check info
      # print("Information stored in config.arrays: \n", db[13].arrays)
      # db[6].info['energy_xtb']
      return db

  def labeling_Data_XTB_Values_check_atomization_energies(self, db=None):
    r"""The updated data contains one energy value for each config `energy_xtb` and the `forces_xtb` on each atom. Latest version of [ASE](https://wiki.fysik.dtu.dk/ase/index.html) does not support simple names such as `energy` and `forces` so we append `_xtb`. The entire computation takes about `25 mins` for the 5003 configs. We have precomputed the data, so we can simply load the final result. Let's check the $E^0$ values and atomization energies:
    ---
    aseMolec.extAtoms.get_prop(db=db, type='info',
                               prop='energy_xtb',
                               peratom=False)[11]
    """
    if db is None:
      db = self.get_db_labeling_Data_XTB_Values()
    # print("E0s: \n", aseMolec.extAtoms.get_E0(db, tag='_xtb'))
    print("Total energy per config: \n", aseMolec.extAtoms.get_prop(
        db=db, type='info', prop='energy_xtb', peratom=False)[13])
    # print("Toal energy per atom: \n", ea.get_prop(
    #     db, 'info', 'energy_xtb', peratom=True)[13])
    # print("Atomization energy per config: \n", ea.get_prop(
    #     db, 'bind', prop='_xtb', peratom=False)[13])
    # print("Atomization energy per atom: \n", ea.get_prop(
    #     db, 'bind', prop='_xtb', peratom=True)[13])

    return db

  def Model_parameters(self):
    pass

  def data_set(self, db=None,
               fname_train_data='data/solvent_xtb_train_200.xyz',
               fname_test_data='data/solvent_xtb_test.xyz'):
    r"""
    划分训练集和测试集
    """
    if db is None:
      db = self.labeling_Data_XTB_Values()
    if not os.path.exists(fname_train_data):
      # first 200 configs plus the 3 E0s
      ase.io.write(fname_train_data, db[:203])
    elif not os.path.exists(fname_test_data):
      ase.io.write(fname_test_data, db[-1000:])  # last 1000 configs
    return None

  def Fitting_the_model_config_file(self,
                                    fneme='config/config-02.yml',
                                    data={'model': 'MACE',
                                          'num_interactions': 2,
                                          'num_channels': 32,
                                          'max_L': 0,
                                          'correlation': 2,
                                          'r_max': 4.0,
                                          'max_ell': 2,
                                          'name': 'mace01',
                                          'model_dir': 'MACE_models',
                                          'log_dir': 'MACE_models',
                                          'checkpoints_dir': 'MACE_models',
                                          'results_dir': 'MACE_models',
                                          'train_file': 'data/solvent_xtb_train_200.xyz',
                                          'valid_fraction': 0.10,
                                          'test_file': 'data/solvent_xtb_test.xyz',
                                          'E0s': 'average',
                                          'energy_key': 'energy_xtb',
                                          'forces_key': 'forces_xtb',
                                          'device': 'cpu',
                                          'batch_size': 10,
                                          'max_num_epochs': 50,
                                          'swa': True,
                                          'seed': 123
                                          }):
    """
    #region
    We'll give a high-level explanation of the important parameters in MACE. We will discuss these in detail during the third tutorial and associated lectures. Consult the [documentation](https://github.com/ACEsuit/mace) for additional parameters.

    - ##### <font color='red'>--num_interactions</font>: message-passing layers

    Controls the number of message-passing layers in the model.

    - ##### <font color='red'>--hidden_irreps</font>: number of message passing layers

    Determines the size of the model and its symmetry.
    For example: `hidden_irreps='128x0e'` means the model has `128` channels or paths, the output is invariant under rotation ($L_{\rm max}=0$) and even under inversion (`'e'`). For most applications, these settings will do well. `hidden_irreps='64x0e + 64x1o'` means the model has `64` channels and is equivariant under rotation ($L_{\rm max}=0$).

    Alternatively, the model size can be adjusted using a pair of more user-friendly arguments:

    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <font color='red'>--num_channels=32</font>

    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <font color='red'>--max_L=2</font>

    which, taken together achieve the same as <font color='red'>--hidden_irreps='32x0e + 32x1o + 32x2e'</font>

    <font color='blue'>**In general, the `accuracy` of the model can be improved by using more layers, more channels or higher equivariances. This will result in more parameters and `slower` models.**</font>

    - ##### <font color='red'>--correlation</font>: the order of the many-body expansion
    $$
    E_{i} = E^{(0)}_{i} + \sum_{j} E_{ij}^{(1)} + \sum_{jk} E_{ijk}^{(2)} + ...
    $$

    The energy-expansion order that MACE induces at each layer. Choosing `--correlation=3` will create basis functions of up to 4-body (ijkl) indices, for each layer. If the model has multiple layers, the effective correlation order is higher. For example, a two-layer MACE with `--correlation=3` has an effective body order of `13`.

    - ##### <font color='red'>--r_max</font>: the cutoff radius

    The cut-off applied to local environment in each layer. `r_max=3.0` means atoms separated by a distance of more than 3.0 A do not directly `communicate`. When the model has multiple message-passing layers, atoms further than 3.0 A can still `communicate` through later messages if intermediate proxy atoms exist. The effective `receptive field` of the model is `num_interactions x r_max`.

    - ##### <font color='red'>--max_ell</font>: angular resolution

    The angular resolution describes how well the model can describe angles. This is controlled by `l_max` of the spherical harmonics basis (not to be confused with `L_max`). Larger values will result in more accurate but slower models. The default is `l_max=3`, appropriate in most cases.

    Let's train our first model:
    ------

    - ##### <font color='red'>--name</font>: the name of the model
    This name will be used to form file names (model, log, checkpoints, results), so choose a distinct name for each experiment

    - ##### <font color='red'>--model_dir, --log_dir, --checkpoints_dir, --results_dir</font>: directory paths
    These are the directories where each type of file is saved. For simplicity, we will all files in the same directory.

    - ##### <font color='red'>--train_file</font>: name of training data

    These data configs are used to compute gradients and update model parameters.

    - ##### <font color='red'>--valid_file</font>: name of validation data
    An alternative way to choose the validation set is by using the `--valid_fraction` keyword. These data configs are used to estimate the model accuracy during training, but not for parameter optimization. The validation set also controls the stopping of the training. At each `--eval_interval` the model is tested on the validation set. The evaluation of these configs takes place in batches, which can be controlled by `--valid_batch_size`. If the accuracy of the model stops improving on the validation set for `--patience` number of epochs, the model will undergo **early stopping**. 

    - ##### <font color='red'>--test_file</font>: name of testing data

    This set is entirely independent and only gets evaluated at the end of the training process to estimate the model accuracy on an independent set.

    - ##### <font color='red'>--E0s</font>: isolated atom energies

    Controls how `E0s` should be determined. The strongly recommended approach is to add these values to the training set with `config_type=IsolatedAtom` in `atoms.info` and set `E0s="isolated"`. If these values are not available, MACE can estimate them by least square regression over the available data `E0s="average"` which can lead to unintended consequences depending on how representative the data is.

    - ##### <font color='red'>--energy_key, --forces_key</font> the key where these values are stores
    This key must coincide with the `ase.Atoms.info[key]/ase.Atoms.arrays[key]` where the energies and forces are stored in the ase.Atoms object.

    - ##### <font color='red'>--device</font> computing device to use
    Can be CPU (`cpu`), GPU (`cuda`) or Apple Silicon (`mps`). Here we will use `cuda` since the GPU will be significantly faster than the CPU.

    - ##### <font color='red'>--batch_size</font> number of configs evaluated in one batch
    Number of configs used to compute the gradients for each full update of the network parameters. This training strategy is called stochastic gradient descent because only a subset of the data (`batch_size`) is used to change the parameters at each update.

    - ##### <font color='red'>--max_num_epochs</font> number of passes through the data
    An `epoch` is completed when the entire training data has been used once in updating the weights `batch` by `batch`. A new epoch begins, and the process repeats.

    - ##### <font color='red'>--swa</font> protocol for loss weights
    During training you will notice energy errors are at first much higher than force errors, MACE implements a special protocol that increases the weight on the energy in the loss function (`--swa_energy_weight`) once the forces are sufficiently accurate. The starting epoch for this special protocol can be controlled by changing `--start_swa`.

    - ##### <font color='red'>--seed</font> random number generator seed
    Useful for preparing committee of models.

    Now we are ready to fit our first MACE model:
    #endregion
    """
    with open(fneme, 'w') as f:
      for k, v in data.items():
        print(k, ':', v, file=f)

    pass

  def Fitting_the_model(self, fname='config/config-02.yml',
                        is_remove=False):
    from soft_learn_project import subprocessLearn
    sl = subprocessLearn.SubprocessLearn()
    sl.CLI_popen(directory='.',
                 args=['mace_run_train', '--config', fname])

    # remove checkpoints since they may cause errors on retraining a model with the same name but a different architecture
    if is_remove:
      import glob
      for file in glob.glob("MACE_models/*_run-*.model"):
        os.remove(file)
      for file in glob.glob("MACE_models/*.pt"):
        os.remove(file)
    return None

  def evaluate_trained_model(self,
                             fname_train_data="data/solvent_xtb_train_200.xyz",
                             fname_train_evaluate='tests/mace01/solvent_train.xyz',
                             fname_test_data="data/solvent_xtb_test.xyz",
                             fname_test_evaluate='tests/mace01/solvent_test.xyz'):
    """We will now use the `mace_eval_configs` script to evaluate the trained model on both the train and test datasets. The script takes the arguments: `--configs` which specifies the file to evaluate, the path to the model in `--model` and the path to the output in `--output`.
    """
    from soft_learn_project import subprocessLearn
    import warnings
    warnings.filterwarnings("ignore")
    os.makedirs("tests/mace01/", exist_ok=True)
    # evaluate the train set
    subprocessLearn.SubprocessLearn().CLI_popen(
        directory='.',
        args=[
            "mace_eval_configs",
            "--configs",
            fname_train_data,
            "--model",
            "MACE_models/mace01.model",
            "--output",
            fname_train_evaluate,
        ],
    )
    # evaluate the test set
    subprocessLearn.SubprocessLearn().CLI_popen(
        directory='.',
        args=[
            "mace_eval_configs",
            "--configs",
            fname_test_data,
            "--model",
            "MACE_models/mace01.model",
            "--output",
            fname_test_evaluate,
        ],
    )
    pass

  def plot_RMSEs(self, db, labs):
    # Backward compatibility
    aseMolec.extAtoms.rename_prop_tag(db, 'MACE_energy', 'energy_mace')
    # Backward compatibility
    aseMolec.extAtoms.rename_prop_tag(db, 'MACE_forces', 'forces_mace')

    plt.figure(figsize=(9, 6), dpi=300)
    plt.subplot(1, 3, 1)
    self.plot_prop(prop1=self.get_prop_bind(db=db, prop='_xtb', peratom=True),
                   prop2=self.get_prop_bind(db=db, prop='_mace', peratom=True),
                   labs=labs, title=r'E$_b$ $(\rm eV/atom)$ ', rel=False)
    plt.subplot(1, 3, 2)
    self.plot_prop(prop1=self.get_prop_energy(db=db, prop='energy_xtb',
                                              peratom=True),
                   prop2=self.get_prop_energy(db=db, prop='energy_mace',
                                              peratom=True),
                   labs=labs,
                   title=r'E$_{totoal}$ $(\rm eV/atom)$ ', rel=False)
    plt.subplot(1, 3, 3)
    self.plot_prop(prop1=self.get_prop_forces(db=db, prop='forces_xtb'),
                   prop2=self.get_prop_forces(db=db, prop='forces_mace'),
                   labs=labs,
                   title=r'F $(\rm eV/\AA)$ ', rel=False)
    plt.tight_layout()
    return

  def compare_accuracy(self,
                       fname_train_evaluate='tests/mace01/solvent_train.xyz',
                       fname_test_evaluate='tests/mace01/solvent_test.xyz',):
    """
    We can compare MACE vs XTB accuracy on the train and test sets and for this we will use the [aseMolec](git@github.com:imagdau/aseMolec.git) which implements some handy utilities for manipulating ase.Atoms and testing potentials, especially for molecular systems.
    """
    train_data = ase.io.read(fname_train_evaluate, ':')
    # append the E0s for computing atomization energy errors
    test_data = train_data[:3] + \
        ase.io.read(fname_test_evaluate, ':')

    self.plot_RMSEs(train_data, labs=['XTB', 'MACE'])
    self.plot_RMSEs(test_data, labs=['XTB', 'MACE'])
    pass

  def check_forces(self, fname='tests/mace01/solvent_test.xyz',):
    """Indeed, the translation and rotational part of the forces (related to inter-molecular interactions) is significantly harder to capture as evidenced by the larger errors. While the absolute RMSEs are smaller, the relative RMSEs are signifincatly larger for the inter-molecular components. Nevertheless, MACE errors ar significantly lower than other models on these tests."""
    db1 = ase.io.read(fname, ':')
    self.extract_molecs(db=db1,
                        old_energy_tag='energy_xtb',
                        old_forces_tag='forces_xtb',
                        intra_inter=True)

    db2 = ase.io.read(fname, ':')
    self.extract_molecs(db=db2,
                        old_energy_tag='MACE_energy',
                        old_forces_tag='MACE_forces',
                        intra_inter=True)
    aseMolec.pltProps.plot_trans_rot_vib(db1, db2, labs=['XTB', 'MACE'])

  def simpleMD(self, fname, init_conf, calc,
               temp=1200, interval=10, steps=2000):
    """Accuracy on fixed test sets is great, but molecular dynamics (MD) is the ultimate test. First, we care about stability, then accuracy: let's check if MACE gives stable dynamics. We will start by implementing a simple function to run Langevin dynamics. We initialize the temperature at 300 K and remove all translations and rotations.
    """
    # remove previously stored trajectory with the same name
    os.system('rm -rfv '+fname)
    init_conf.set_calculator(calc)

    # initialize the temperature
    random.seed(701)  # just making sure the MD failure is reproducible
    # initialize temperature at 300
    ase.md.velocitydistribution.MaxwellBoltzmannDistribution(
        atoms=init_conf, temperature_K=temp)
    ase.md.velocitydistribution.Stationary(init_conf)
    ase.md.velocitydistribution.ZeroRotation(init_conf)

    dyn = ase.md.langevin.Langevin(atoms=init_conf,
                                   timestep=1.0*ase.units.fs,
                                   temperature_K=temp,
                                   friction=0.1)  # drive system to desired temperature

    # %matplotlib inline

    time_fs = []
    temperature = []
    energies = []

    fig, ax = plt.subplots(2, 1, figsize=(6, 6), sharex='all', gridspec_kw={
        'hspace': 0, 'wspace': 0})

    def write_frame():
      dyn.atoms.write(fname, append=True)
      time_fs.append(dyn.get_time()/ase.units.fs)
      temperature.append(dyn.atoms.get_temperature())
      energies.append(dyn.atoms.get_potential_energy()/len(dyn.atoms))

      ax[0].plot(np.array(time_fs), np.array(energies), color="b")
      ax[0].set_ylabel('E (eV/atom)')

      # plot the temperature of the system as subplots
      ax[1].plot(np.array(time_fs), temperature, color="r")
      ax[1].set_ylabel('T (K)')
      ax[1].set_xlabel('Time (fs)')

      IPython.display.clear_output(wait=True)
      IPython.display.display(plt.gcf())
      time.sleep(0.01)

    dyn.attach(write_frame, interval=interval)
    t0 = time.time()
    dyn.run(steps=steps)
    t1 = time.time()
    print("MD finished in {0:.2f} minutes!".format((t1-t0)/60))

  def simpleMD_example_mace(self, fname='moldyn/mace01_md.xyz',
                            model_paths=['MACE_models/mace01.model'],
                            temp=1200,
                            interval=10,
                            steps=2000):
    db = ase.io.read('data/solvent_molecs.xyz', ':')
    init_conf = self.sel_by_info_val_example(db=db, info_key='Nmols',
                                             info_val=1)[0].copy()
    # we can use MACE as a calculator in ASE!
    mace_calc = self.get_calc(model_paths=model_paths,
                              device='cpu', default_dtype="float32")
    self.simpleMD(fname=fname, init_conf=init_conf, temp=temp,
                  calc=mace_calc, interval=interval, steps=steps)

  def simpleMD_example_xtb(self, fname='moldyn/xtb_md.xyz',
                           temp=1200,
                           interval=10,
                           steps=2000):
    db = ase.io.read('data/solvent_molecs.xyz', ':')
    init_conf = self.sel_by_info_val_example(db=db, info_key='Nmols',
                                             info_val=1)[0].copy()
    from soft_learn_project import xtbPythonLearn
    xl = xtbPythonLearn.XtbPythonLearn()
    xtb_calc = xl.get_calc(method="GFN2-xTB")
    self.simpleMD(fname=fname, init_conf=init_conf, temp=temp,
                  calc=xtb_calc, interval=interval, steps=steps)
    pass

  def view_md(self, fname='moldyn/xtb_md.xyz'):
    # from ase.
    import ase.io 
    db = ase.io.read(fname, ':')
    pass

  def rdf_plot_example(self, tag='HO_intra',
                       rmax=5, nbins=50):
    """
    Are the different dynamics sampling the correct distributions? Let us check the radial distribution functions (RDF). The [aseMolec](https://github.com/imagdau/aseMolec) package provides functionality to do that:
    ---
    tag: choose one of 'HH_intra', 'HC_intra', 'HO_intra', 'CC_intra', 'CO_intra', 'OO_intra'
    """
    # choose one of 'HH_intra', 'HC_intra', 'HO_intra', 'CC_intra', 'CO_intra', 'OO_intra'
    for f in ['xtb_md', 'mace01_md']:
      traj = ase.io.read('moldyn/'+f+'.xyz', '50:')  # ignore first 50 frames
      rdf = self.get_rdf(traj=traj, rmax=rmax, nbins=nbins)
      plt.plot(rdf[1], rdf[0][tag], '.-', label=f, alpha=0.7, linewidth=3)

    plt.legend()
    plt.yticks([])
    plt.xlabel(r'R ($\rm \AA$)')
    plt.ylabel('RDF '+tag)

  def simpleMD_example_liquid(self, atoms=None,
                              fname='moldyn/mace01_md_liquid.xyz'):
    """
    read a liquid config with periodic boundary conditions
    ---
    Transferability from clusters to the condensed phase environment is still an [open research](https://doi.org/10.1021/acs.jpcb.2c03746) question. If this works, it implies that we might be able to learn highly accurate Quantum Chemistry PES on molecular clusters and make predictions (density, diffusivity) for the condensed phase! This is new science!
    """
    if atoms is None:
      atoms = ase.io.read('data/solvent_liquid.xyz')
      atoms.center()
    mace_calc = self.get_calc(model_paths=['MACE_models/mace01.model'],
                              device='cpu')
    self.simpleMD(init_conf=atoms, temp=500, calc=mace_calc,
                  fname=fname, interval=10, steps=2000)

  def mace_run_train(self,
                     args_mod_dict={"--name": "mace02_com1",
                                    "--model_dir": 'MACE_models',
                                    "--log_dir": 'MACE_models',
                                    "--checkpoints_dir": 'MACE_models',
                                    "--results_dir": 'MACE_models',
                                    "--train_file": "data/solvent_xtb_train_20.xyz",
                                    "--valid_file": "data/solvent_xtb_train_50.xyz",
                                    "--test_file": "data/solvent_xtb_test.xyz", },
                     ):

    args_dict = self.train_args_dict(args_mod_dict=args_mod_dict)
    self.run_mace_run_train(args_dict=args_dict)
    return None

  def Iterative_Training1(self,
                          name="mace02_com1",
                          model_dir='MACE_models',
                          fname_train="data/solvent_xtb_train_20.xyz",
                          fname_valid="data/solvent_xtb_train_50.xyz",
                          fname_test="data/solvent_xtb_test.xyz",
                          ):
    db = ase.io.read('data/solvent_xtb.xyz', ':')
    # first 50 configs plus the 3 E0s, we'll use only 20 of them for training!
    ase.io.write(fname_valid, db[:53])

    self.mace_run_train(args_mod_dict={'--name': name,
                                       '--model_dir': model_dir,
                                       "--log_dir": model_dir,
                                       "--checkpoints_dir": model_dir,
                                       "--results_dir": model_dir,
                                       "--train_file": fname_train,
                                       "--valid_file": fname_valid,
                                       "--test_file": fname_test,
                                       "--E0s": "isolated",
                                       "--energy_key": "energy_xtb", },)

  def Iterative_Training2(self,
                          name="mace02_com1_gen1",
                          model_dir='MACE_models',
                          fname_train="data/solvent_xtb_train_23_gen1.xyz",
                          fname_valid="data/solvent_xtb_train_50.xyz",
                          fname_test="data/solvent_xtb_test.xyz",
                          ):
    """尽管会产生错误的动态。让我们从这些失败的配置中选取三个，将它们添加回训练集并重新组装一个新模型。这被称为迭代训练："""

    traj = ase.io.read('data/mace02_md_100_xtb.xyz', ':')
    db = ase.io.read('data/solvent_xtb_train_20.xyz', ':')
    db += traj[40:100:20]  # add three failed configs to the training set
    ase.io.write(fname_train, db)

    self.mace_run_train(args_mod_dict={'--name': name,
                                       '--model_dir': model_dir,
                                       "--log_dir": model_dir,
                                       "--checkpoints_dir": model_dir,
                                       "--results_dir": model_dir,
                                       "--train_file": fname_train,
                                       "--valid_file": fname_valid,
                                       "--test_file": fname_test,
                                       })
    pass

  def active_learning_1(self,):
    """active learning
    如果我们有理由相信模型是错误的，我们可以继续迭代过程并逐步改进潜力。这是一个艰巨的过程，因为我们需要仔细研究轨迹，并决定将哪些配置添加回训练。我们可以通过动态预测错误和选择不能很好预测的配置来自动化这个协议：这被称为主动学习。
    """
    # Preparing a committee of models
    self.mace_run_train(args_mod_dict={'--name': 'mace02_com2',
                                       '--model_dir': 'MACE_models',
                                       "--log_dir": 'MACE_models',
                                       "--checkpoints_dir": 'MACE_models',
                                       "--results_dir": 'MACE_models',
                                       "--train_file": "data/solvent_xtb_train_20.xyz",
                                       "--valid_file": "data/solvent_xtb_train_50.xyz",
                                       "--test_file": "data/solvent_xtb_test.xyz",
                                       '--valid_fraction': 0.6,
                                       '--seed': 345
                                       })
    self.mace_run_train(args_mod_dict={'--name': 'mace02_com3',
                                       '--model_dir': 'MACE_models',
                                       "--log_dir": 'MACE_models',
                                       "--checkpoints_dir": 'MACE_models',
                                       "--results_dir": 'MACE_models',
                                       "--train_file": "data/solvent_xtb_train_20.xyz",
                                       "--valid_file": "data/solvent_xtb_train_50.xyz",
                                       "--test_file": "data/solvent_xtb_test.xyz",
                                       '--valid_fraction': 0.6,
                                       '--seed': 567
                                       })
    pass

  def active_learning_2_calc_the_commitee(self,):
    """
    Perfect, we have two new models. Let's start by testing the commitee on the first 100 frames of the first trajectory we generated. The `MACECalculator` can conveniently take a list of calculators as input and will compute separate energies from each calculator. 
    """
    from aseMolec import extAtoms as ea

    mace_calcs = self.get_calc(model_paths=['MACE_models/mace02_com1_compiled.model',
                                            'MACE_models/mace02_com2_compiled.model',
                                            'MACE_models/mace02_com3_compiled.model'],
                               device='cpu')

    traj = ase.io.read('data/mace02_md_100_xtb.xyz', ':')
    for at in traj:
      at.calc = mace_calcs
      engs = at.get_potential_energies()
      # rename value obtained with first member of the committee
      at.info['energy_mace_1'] = at.info.pop('energy_mace')
      at.info['energy_mace_2'] = engs[1]
      at.info['energy_mace_3'] = engs[2]
      at.info['variance'] = np.std(engs)
      at.info['average_mace_energy'] = np.average(engs)
      at.info['true_error'] = np.abs(
          at.info['average_mace_energy'] - at.info['energy_xtb'])
    return traj

  def active_learning_2_plot_the_commitee(self):
    """Notice how the variance (disagreement between models) increases around the same config where the true error with respect to XTB diverges. This is good news because it indicates the variance is a good proxy for true error.
    """
    traj = self.active_learning_2_calc_the_commitee()
    # Let's check the energies of the MACE committee vs XTB energy
    plt.plot(np.arange(len(traj)),
             aseMolec.extAtoms.get_prop(
        traj, 'info', 'energy_xtb', peratom=True),
        label='XTB')
    plt.plot(np.arange(len(traj)),
             aseMolec.extAtoms.get_prop(traj, 'info', 'energy_mace_1', peratom=True), label='MACE_1')
    plt.plot(np.arange(len(traj)),
             aseMolec.extAtoms.get_prop(
        traj, 'info', 'energy_mace_2', peratom=True),
        label='MACE_2')
    plt.plot(np.arange(len(traj)),
             aseMolec.extAtoms.get_prop(
        traj, 'info', 'energy_mace_3', peratom=True),
        label='MACE_3')
    plt.legend()
    plt.xlabel('Time (fs)')
    plt.ylabel('Energy per Atom (eV)')
    plt.show()

    # ---
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(np.arange(len(traj)),
             aseMolec.extAtoms.get_prop(traj, 'info',
                                        'variance', peratom=True),
             label='committee variance',
             color='tab:blue')
    ax2.plot(np.arange(len(traj)),
             aseMolec.extAtoms.get_prop(traj, 'info',
                                        'true_error', peratom=True),
             label='error w.r.t XTB',
             color='tab:orange')

    ax1.set_xlabel('time (fs)')
    ax1.set_ylabel('committee energy variance', color='tab:blue')
    ax2.set_ylabel('error w.r.t XTB', color='tab:orange')
    plt.legend()
    plt.show()
    pass

  def Running_MD_with_MACE_committee(self):
    """Now we can run dynamics with a commitee of models and monitor the variance in the energy prediction. Because XTB is cheap enough we can also compare that variance with the true error. Do they correlate?
    """

    import xtb.ase.calculator
    model_paths = ['MACE_models/mace02_com1_compiled.model',
                   'MACE_models/mace02_com2_compiled.model',
                   'MACE_models/mace02_com3_compiled.model']
    xtb_calc = xtb.ase.calculator.XTB(method="GFN2-xTB")
    mace_calc = self.get_calc(model_paths=model_paths, device='cpu')

    init_conf = aseMolec.extAtoms.sel_by_info_val(
        ase.io.read('data/solvent_molecs.xyz', ':'), 'Nmols', 1)[0].copy()
    init_conf.calc = mace_calc

    # initialize the temperature
    np.random.seed(701)
    ase.md.velocitydistribution.MaxwellBoltzmannDistribution(
        init_conf, temperature_K=300)
    ase.md.velocitydistribution.Stationary(init_conf)
    ase.md.velocitydistribution.ZeroRotation(init_conf)

    dyn = ase.md.langevin.Langevin(
        init_conf, 1*ase.units.fs, temperature_K=1200, friction=0.1)

    time_fs = []
    temperature = []
    energies_1 = []
    energies_2 = []
    energies_3 = []
    variances = []
    xtb_energies = []
    true_errors = []

    fig, ax = plt.subplots(4, 1, figsize=(8, 8), sharex='all',
                           gridspec_kw={'hspace': 0, 'wspace': 0})

    def write_frame():
      at = dyn.atoms.copy()
      at.calc = xtb_calc
      xtb_energy = at.get_potential_energy()

      dyn.atoms.write('moldyn/mace02_md_committee.xyz',
                      append=True, write_results=False)
      time_fs.append(dyn.get_time()/ase.units.fs)
      temperature.append(dyn.atoms.get_temperature())
      energies_1.append(dyn.atoms.calc.results["energies"][0]/len(dyn.atoms))
      energies_2.append(dyn.atoms.calc.results["energies"][1]/len(dyn.atoms))
      energies_3.append(dyn.atoms.calc.results["energies"][2]/len(dyn.atoms))
      variances.append(dyn.atoms.calc.results["energy_var"]/len(dyn.atoms))
      xtb_energies.append(xtb_energy/len(dyn.atoms))
      true_errors.append(
          np.var([dyn.atoms.calc.results["energy"], xtb_energy])/len(dyn.atoms))

      # plot the true error
      ax[0].plot(np.array(time_fs), np.array(true_errors), color="black")
      ax[0].set_ylabel(r'$\Delta$ E (eV$^2$/atom)')
      ax[0].legend(['Error w.r.t. XTB'], loc='upper left')

      # plot committee variance
      ax[1].plot(np.array(time_fs), np.array(variances), color="y")
      ax[1].set_ylabel(r'committee variance')
      ax[1].legend(['Estimated Error (committee variances)'], loc='upper left')

      # plot the temperature of the system as subplots
      ax[2].plot(np.array(time_fs), temperature,
                 color="r", label='Temperature')
      ax[2].set_ylabel("T (K)")

      ax[3].plot(np.array(time_fs), energies_1, color="g")
      ax[3].plot(np.array(time_fs), energies_2, color="y")
      ax[3].plot(np.array(time_fs), energies_3, color="olive")
      ax[3].plot(np.array(time_fs), xtb_energies, color="black")
      ax[3].set_ylabel("E (eV/atom)")
      ax[3].set_xlabel('Time (fs)')
      ax[3].legend(['E mace1', 'E mace2', 'E mace3',
                   'E xtb'], loc='upper left')

      IPython.display.clear_output(wait=True)
      IPython.display.display(fig)
      time.sleep(0.01)

    dyn.attach(write_frame, interval=10)
    dyn.run(2000)
    print("MD finished!")

    pass

  def Foundational_Models(self, steps=2000,
                          fname='moldyn/mace03_md.xyz',):
    """Foundation models changed everything. MACE-MP-0 is a model trained on >1 million DFT calcuations, and can run dynamics for the whole periodic table. 

    Mace provides a simple interface to load a foundational model, which we can use mow. Check the [documentation](https://mace-docs.readthedocs.io/en/latest/guide/foundation_models.html) for more details.
    """
    init_conf = aseMolec.extAtoms.sel_by_info_val(
        ase.io.read('data/solvent_molecs.xyz', ':'), 'Nmols', 1)[0].copy()
    macemp = mace.calculators.mace_mp(
        model="/Users/wangjinlong/job/soft_learn/soft_learn_project/mace_learn/mace-foundations/20231210mace128L0_energy_epoch249model")  # 或者 model='small'
    self.simpleMD(init_conf=init_conf, temp=1200, calc=macemp,
                  fname=fname, interval=10, steps=steps)

    pass

  def Foundational_Models_Compare_to_XTB(self,
                                         tag='OO_intra'):
    """
    Let's compute the radial distribution functions of this very stable trajectory and compare them to XTB. Remember MACE-MP was trained on PBE level of theory so we don't necessarily expect them to match:
    """
    # choose one of 'HH_intra', 'HC_intra', 'HO_intra', 'CC_intra', 'CO_intra', 'OO_intra'
    for f in ['xtb_md', 'mace03_md']:
      traj = ase.io.read('moldyn/'+f+'.xyz', '50:')  # ignore first 50 frames
      for at in traj:
        at.pbc = True  # create a fake box for rdf compatibility
        at.cell = [100, 100, 100]
      # aseMolec provides functionality to compute RDFs
      rdf = self.get_rdf(traj=traj, rmax=5, nbins=70)
      self.rdf_plot(rdf=rdf, tag=tag, label=f,)

    plt.legend()
    plt.yticks([])
    plt.xlabel(r'R ($\rm \AA$)')
    plt.ylabel('RDF '+tag)

  def Fine_tune_MACE_MP_to_XTB(self, args_mod_dict={}):
    args_dict = self.fine_tune_MACE_MP_args_dict(
        args_mod_dict=args_mod_dict)
    self.run_mace_run_train(args_dict=args_dict)
    pass
