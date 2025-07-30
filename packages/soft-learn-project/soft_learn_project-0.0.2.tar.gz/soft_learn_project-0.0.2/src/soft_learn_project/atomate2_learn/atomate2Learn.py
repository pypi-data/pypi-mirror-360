import emmet.core
import emmet.core.utils
import emmet.core.vasp
import emmet.core.vasp.calculation
import jobflow.core
import jobflow
import jobflow.core.flow
import jobflow.core.job
import jobflow.core.job
import jobflow.core.maker
import jobflow.managers.fireworks
import pymatgen.electronic_structure.plotter
import pymatgen.electronic_structure.dos
import pymatgen.electronic_structure.bandstructure
import pymatgen.electronic_structure
import pymatgen.core.structure
import pymatgen.core
import pymatgen
import atomate2.vasp.jobs.core
import atomate2.vasp.jobs.base
import atomate2.vasp.jobs
import atomate2.vasp.flows.core
import atomate2.vasp.flows
import atomate2.vasp.files
import atomate2.vasp
import atomate2
import monty.serialization
import atomate2.vasp.sets.core
import atomate2.vasp.flows.elastic
import atomate2.vasp.powerups
import ase.build
import ase
import os
import atomate2.settings
import atomate2.vasp.flows.lobster
import pymatgen.electronic_structure.cohp
import fireworks


class Atomate2Learn():
  def __init__(self) -> None:
    """官网: https://materialsproject.github.io/atomate2/index.html
    Atomate2是一个免费的开源软件，用于使用简单的Python函数执行复杂的材料科学工作流程。atomate2的特性包括
    它建立在开源库：pymatgen、custodian、jobflow和FireWorks之上。
    一个“标准”工作流库，用于计算各种所需的材料属性。
    能力范围从一种材料，到100种材料，或100,000种材料。
    修改和链接工作流的简单途径。
    它可以构建输出属性的大型数据库，您可以以系统的方式查询、分析和共享这些数据库。
    它会自动保存作业、作业目录、运行时参数等详细记录。
    """
    self.env_set()
    from py_package_learn.jobflow_learn import jobflowLearn
    self.JobflowLearn = jobflowLearn.JobflowLearn()  # 初始化, 即设置了环境变量
    # from py_package_learn.fireworks_learn import fireworksLearn
    # self.FireWorksLearn = fireworksLearn.FireWorksLearn()
    pass

  def install(self):
    string = """我当前尝试用conda 安装 atomate2 发现有问题, 有个ssl?模块不能正确加载
    1. 创建环境
    conda create -n atomate2 python=3.12
    2. To install the packages run:
    pip install atomate2 # conda install fireworks
    3. If you would like to use more specialized capabilities of atomate2 such as the phonon, Lobster or force field workflows, you would need to run one of
    pip install 'atomate2[phonons]'
    pip install 'atomate2[lobster]'  # 或者 conda install atomate2 lobsterpy
    pip install 'atomate2[forcefields]'

    # ---
    conda install atomate2 ijson lobsterpy
    pip install msgpack # conda 安装不上这个
    """
    print(string)
    return None

  def config_atomate2(self,
                      fname_atomat2_yaml='/Users/wangjinlong/job/soft_learn/py_package_learn/atomate2_learn/atomate2/config/atomate2.yaml'):
    # 写入:
    string_atomat2_yaml = """
    VASP_CMD: /opt/homebrew/bin/mpirun -np 4 /Users/wangjinlong/job/science_research/sci_scripts/bin/vasp_std
    VASP_GAMMA_CMD: /opt/homebrew/bin/mpirun -np 4 /Users/wangjinlong/job/soft_learn/vasp_learn/package/vasp.6.4.0_on_mac_vaspsol_neb/bin/vasp_gam
    VASP_NCL_CMD: /Users/wangjinlong/job/soft_learn/vasp_learn/package/vasp.6.4.0_on_mac_vaspsol_neb/bin/vasp_ncl
    # VASP_INCAR_UPDATES: Updates to apply to VASP INCAR files. This allows you to customise input sets on different machines, without having to change the submitted workflows. For example, you can set certain parallelization parameters, such as NCORE, KPAR etc.
    # VASP_VDW_KERNEL_DIR: The path to the VASP Van der Waals kernel.
    # LOBSTER
    LOBSTER_CMD: /Users/wangjinlong/job/soft_learn/lobster_learn/lobster-5.0.0/OSX/lobster-5.0.0-OSX

    # /Users/wangjinlong/.config/.pmgrc.yaml 的内容, 放在这里是不是也可以？
    # PMG_VASP_PSP_DIR: 
    #   /Users/wangjinlong/job/soft_learn/py_package_learn/pymatgen_learn/pmg_vasp_potcars
    # PMG_DEFAULT_FUNCTIONAL: PBE_52
    # PMG_MAPI_KEY: aKB0GGIGwkraQwvSLIkYLfvxOMtnjaKQ"""
    with open(file=fname_atomat2_yaml, mode='w') as f:
      string_list = string_atomat2_yaml.split('\n')
      for string in string_list:
        if string == '':
          continue
        string = string.strip()
        f.write(string+'\n')
    # Configure calculation output database
    # <<INSTALL_DIR>>/config/jobflow.yaml
    return None

  def configure_pymatgen(self):
    from py_package_learn.pymatgen_learn import pymatgenLearn
    pymatgenLearn.PymatgenLearn().env_set()
    pass

  def env_set(self,
              install_dir='/Users/wangjinlong/job/soft_learn/py_package_learn/atomate2_learn/atomate2'):
    """配置atomate2的最后一件事是将以下行添加到.bashrc / .bash_profile文件中，以设置一个环境变量，告诉atomate2和jobflow在哪里可以找到配置文件。
    """
    string1 = f"{install_dir}/config/atomate2.yaml"
    string2 = f"{install_dir}/config/jobflow.yaml"
    os.environ['ATOMATE2_CONFIG_FILE'] = string1
    os.environ['JOBFLOW_CONFIG_FILE'] = string2

    # export ATOMATE2_CONFIG_FILE="<<INSTALL_DIR>>/config/atomate2.yaml"
    # export JOBFLOW_CONFIG_FILE="<<INSTALL_DIR>>/config/jobflow.yaml"
    as_config = atomate2.settings.Atomate2Settings(
        CONFIG_FILE='/Users/wangjinlong/job/soft_learn/py_package_learn/atomate2_learn/atomate2/config/atomate2.yaml',)
    return None

  def get_structure_from_ase_atoms(self, atoms=ase.build.bulk(name='Si')):
    from py_package_learn.pymatgen_learn import pymatgenLearn
    structure = pymatgenLearn.PymatgenLearn().get_aseAtoms2pymagenStructure(atoms=atoms)
    return structure

  def modifying_input_sets(self, flow: atomate2.vasp.jobs.core.BaseVaspMaker,
                           incar_updates={"ENCUT": 200},
                           name_filter=None,
                           class_filter=None,
                           ):
    # update the ENCUT of all VASP jobs in the flow
    new_flow = atomate2.vasp.powerups.update_user_incar_settings(
        flow=flow,
        incar_updates=incar_updates,
        name_filter=name_filter,
        class_filter=class_filter,)
    return new_flow

  def run_flow_locally(self, flow: jobflow.core.flow.Flow,
                       root_dir='/Users/wangjinlong/job/soft_learn/py_package_learn/atomate2_learn/test/xx'):
    # run the job
    response = jobflow.run_locally(flow=flow,
                                   create_folders=True,
                                   root_dir=root_dir,
                                   store=self.get_jobstore())
    return response

  def get_jobstore(self):
    store: jobflow.core.store.JobStore = self.JobflowLearn.get_jobstore()
    return store

  def clean_store(self, store: jobflow.core.store.JobStore):
    store.docs_store.remove_docs({})
    store.additional_stores['data'].remove_docs({})
    return None

  def get_atoms(self, criteria={'name': 'static_W_bulk'}):
    store = self.get_jobstore()
    result = store.query_one(criteria=criteria)
    structure = result['output']['structure']
    atoms = pymatgen.core.Structure.from_dict(structure).to_ase_atoms()
    return atoms

  def get_dos(self, criteria={"output.task_label": "non-scf uniform"}):
    store = self.get_jobstore()

    # get the uniform bandstructure from the database
    result = store.query_one(criteria=criteria,
                             properties=["output.vasp_objects.dos"],
                             load=True,  # DOS stored in the data store, so we need to explicitly load it
                             )

    dos = pymatgen.electronic_structure.dos.CompleteDos.from_dict(
        result["output"]["vasp_objects"]["dos"])
    return dos

  def plot_dos(self, dos: pymatgen.electronic_structure.dos.CompleteDos,
               xlim=(-10, 10),
               ylim=None,
               fname="MgO-dos.pdf"):
    # plot the DOS
    dos_plotter = pymatgen.electronic_structure.plotter.DosPlotter()
    dos_plotter.add_dos_dict(dos.get_element_dos())
    dos_plotter.save_plot(filename=fname, xlim=xlim, ylim=ylim, )
    return None

  def plot_dos_wrapper(self, criteria={'name': 'W_bulk_static'},
                       fname='x.pdf'):
    dos = self.get_dos(criteria=criteria)
    self.plot_dos(dos=dos, fname=fname)
    pass

  def get_bandstructure(self,):
    store = self.get_jobstore()
    # get the line mode bandstructure from the database
    result = store.query_one(
        {"output.task_label": "non-scf line"},
        properties=["output.vasp_objects.bandstructure"],
        load=True,  # BS stored in the data store, so we need to explicitly load it
    )
    bandstructure = pymatgen.electronic_structure.bandstructure.BandStructureSymmLine.from_dict(
        result["output"]["vasp_objects"]["bandstructure"]
    )
    return bandstructure

  def plot_bandstructure(self, bandstructure: pymatgen.electronic_structure.bandstructure.BandStructureSymmLine,
                         fname="MgO-bandstructure.pdf"):
    # plot the line mode band structure
    bs_plotter = pymatgen.electronic_structure.plotter.BSPlotter(bandstructure)
    bs_plotter.save_plot(filename=fname)
    return None

  def get_taskDoc_from_calc_dir(self, dname="/Users/wangjinlong/my_server/my/myORR_B/adsorbate/O2_test"):
    # 您还可以从手动运行的VASP计算中生成TaskDoc。为此，使用from_directory类方法：
    from emmet.core.tasks import TaskDoc
    # import emmet.core.vasp.calculation
    doc = TaskDoc.from_directory(dir_name=dname,)
    return doc

  def example_installation_submit(self):
    string = """
    #!/bin/bash
    #SBATCH -J vasplobsterjob
    #SBATCH -o ./%x.%j.out
    #SBATCH -e ./%x.%j.err
    #SBATCH -D ./
    #SBATCH --mail-type=END
    #SBATCH --mail-user=you@you.de
    #SBATCH --time=24:00:00
    #SBATCH --nodes=1
    #This needs to be adapted if you run with different cores
    #SBATCH --ntasks=48

    # ensure you load the modules to run VASP, e.g., module load vasp
    module load my_vasp_module
    # please activate the required conda environment
    conda activate my_environment
    cd my_folder
    # the following script needs to contain the workflow
    python xyz.py
    """
    # LOBSTER_CMD: OMP_NUM_THREADS=48 <<LOBSTER_CMD>>
    print(string)

    return None

  def example_get_flow_Si(self):
    # construct an FCC silicon structure
    si_structure = pymatgen.core.Structure(
        lattice=[[0, 2.73, 2.73], [2.73, 0, 2.73], [2.73, 2.73, 0]],
        species=["Si", "Si"],
        coords=[[0, 0, 0], [0.25, 0.25, 0.25]],
    )

    # make a relax job to optimise the structure
    relax_job = atomate2.vasp.jobs.core.RelaxMaker().make(si_structure)
    return relax_job

  def example_run_locally_Si(self,
                             root_dir='/Users/wangjinlong/job/soft_learn/py_package_learn/atomate2_learn/test/Si'):
    flow = self.example_get_flow_Si()
    # run the job
    response = jobflow.run_locally(flow=flow,
                                   create_folders=True,
                                   root_dir=root_dir,)
    return response

  def example_analyzing_the_results_Si(self):
    """https://materialsproject.github.io/atomate2/user/docs_schemas_emmet.html
    了解了文档的构成就会理解下面的代码了 
    """
    from jobflow import SETTINGS
    store = SETTINGS.JOB_STORE
    # connect to the job store
    store.connect()
    # query the job store
    result = store.query_one({"output.formula_pretty": "Si"},
                             properties=["output.output.energy_per_atom"])
    print(result)
    return store

  def example_get_flow_MgO_BS(self,):
    # construct a rock salt MgO structure
    mgo_structure = pymatgen.core.Structure(
        lattice=[[0, 2.13, 2.13], [2.13, 0, 2.13], [2.13, 2.13, 0]],
        species=["Mg", "O"],
        coords=[[0, 0, 0], [0.5, 0.5, 0.5]],
    )

    # make a band structure flow to optimise the structure and obtain the band structure
    bandstructure_flow = atomate2.vasp.flows.core.RelaxBandStructureMaker().make(mgo_structure)
    return bandstructure_flow

  def example_run_completely_MgO_BS(self,
                                    root_dir='/Users/wangjinlong/job/soft_learn/py_package_learn/atomate2_learn/test/MgO',
                                    ):
    # construct a rock salt MgO structure
    mgo_structure = pymatgen.core.Structure(
        lattice=[[0, 2.13, 2.13], [2.13, 0, 2.13], [2.13, 2.13, 0]],
        species=["Mg", "O"],
        coords=[[0, 0, 0], [0.5, 0.5, 0.5]],
    )

    # make a band structure flow to optimise the structure and obtain the band structure
    bandstructure_flow = atomate2.vasp.flows.core.RelaxBandStructureMaker().make(mgo_structure)

    # run the job
    jobflow.run_locally(bandstructure_flow,
                        root_dir=root_dir,
                        create_folders=True)

  def example_analyzing_bandstructure(self):
    dos = self.get_dos()
    self.plot_dos(dos=dos)
    bandstructure = self.get_bandstructure()
    self.plot_bandstructure(bandstructure=bandstructure)

  def example_run_lobster(self, root_dir='/Users/wangjinlong/job/soft_learn/py_package_learn/atomate2_learn/test/lobster'):
    structure = pymatgen.core.structure.Structure(
        lattice=[[0, 2.13, 2.13], [2.13, 0, 2.13], [2.13, 2.13, 0]],
        species=["Mg", "O"],
        coords=[[0, 0, 0], [0.5, 0.5, 0.5]],
    )

    lobster = atomate2.vasp.flows.lobster.VaspLobsterMaker().make(structure)

    # update the incar
    lobster = atomate2.vasp.powerups.update_user_incar_settings(lobster, {
                                                                "NPAR": 4})
    # run the job
    jobflow.run_locally(lobster, create_folders=True,
                        store=jobflow.SETTINGS.JOB_STORE,
                        root_dir=root_dir,)
    # 或者
    # update the fireworker of the Lobster jobs
    # for job, _ in lobster.iterflow():
    #   config = {"manager_config": {"_fworker": "worker"}}
    #   if "get_lobster" in job.name:
    #     config["response_manager_config"] = {"_fworker": "lobster"}
    #   job.update_config(config)

    # # convert the flow to a fireworks WorkFlow object
    # wf = jobflow.managers.fireworks.flow_to_workflow(lobster)

    # # submit the workflow to the FireWorks launchpad
    # lpad = fireworks.LaunchPad.auto_load()
    # lpad.add_wf(wf)
    return None

  def example_plot_lobster(self):
    store = jobflow.SETTINGS.JOB_STORE
    store.connect()

    result = store.query_one(
        {"name": "lobster_run_0"},
        properties=[
            "output.lobsterpy_data.cohp_plot_data",
            "output.lobsterpy_data_cation_anion.cohp_plot_data",
        ],
        load=True,
    )

    for number, (key, cohp) in enumerate(
        result["output"]["lobsterpy_data"]["cohp_plot_data"]["data"].items()
    ):
      plotter = pymatgen.electronic_structure.plotter.CohpPlotter()
      cohp = pymatgen.electronic_structure.cohp.Cohp.from_dict(cohp)
      plotter.add_cohp(key, cohp)
      plotter.save_plot(f"plots_all_bonds{number}.pdf")

    for number, (key, cohp) in enumerate(
        result["output"]["lobsterpy_data_cation_anion"]["cohp_plot_data"]["data"].items()
    ):
      plotter = pymatgen.electronic_structure.plotter.CohpPlotter()
      cohp = pymatgen.electronic_structure.cohp.Cohp.from_dict(cohp)
      plotter.add_cohp(key, cohp)
      plotter.save_plot(f"plots_cation_anion_bonds{number}.pdf")

  def example_modifying_input_sets(self, structure):
    """https://materialsproject.github.io/atomate2/user/codes/vasp.html#modifying-input-sets
    """
    # 可以通过几种方式修改计算的输入。每个VASP作业都接受一个VaspInputGenerator作为参数（input_set_generator）。一种选择是指定另一个输入集生成器：
    # create a custom input generator set with a larger ENCUT
    my_custom_set = atomate2.vasp.jobs.core.StaticSetGenerator(
        user_incar_settings={"ENCUT": 800})
    # initialise the static maker to use the custom input set generator, create a job using the customised maker
    static_job: jobflow.core.job.Job = atomate2.vasp.jobs.core.StaticMaker(
        input_set_generator=my_custom_set).make(structure)
    # 第二种方法是在作业创建之后对其进行编辑。所有VASP作业都有一个maker属性，其中包含制造它们的maker的副本。更新input_set_generator属性生成器将更新被写入的输入集
    static_job.maker.input_set_generator.user_incar_settings["LOPTICS"] = True

    # ---
    # 单独更新每个作业的输入集可能会很繁琐, powerups 辅助函数，可以将设置更新应用于流中的所有VASP作业。这些升级还包含用于作业名称和生成它们的生成器的过滤器。
    # make a flow to calculate the elastic constants
    elastic_flow = atomate2.vasp.flows.elastic.ElasticMaker().make(structure)
    # update the ENCUT of all VASP jobs in the flow
    new_flow = atomate2.vasp.powerups.update_user_incar_settings(flow=elastic_flow,
                                                                 incar_updates={"ENCUT": 200})
    # only update VASP jobs which have "deformation" in the job name.
    new_flow = atomate2.vasp.powerups.update_user_incar_settings(flow=elastic_flow,
                                                                 incar_updates={
                                                                     "ENCUT": 200},
                                                                 name_filter="deformation")
    # only update VASP jobs which were generated by an ElasticRelaxMaker
    new_flow = atomate2.vasp.powerups.update_user_incar_settings(
        elastic_flow, {"ENCUT": 200},
        class_filter=atomate2.vasp.flows.elastic.ElasticRelaxMaker
    )
    # powerups can also be applied directly to a Maker. This can be useful for makers that produce flows, as it allows you to update all nested makers. E.g.
    relax_maker = atomate2.vasp.flows.core.DoubleRelaxMaker()
    new_maker = atomate2.vasp.powerups.update_user_incar_settings(flow=relax_maker,
                                                                  incar_updates={"ENCUT": 200})
    # this flow will reflect the updated ENCUT value
    flow = new_maker.make(structure)

    # --- 更灵活的方法:
    # 如果需要更大程度的灵活性，用户可以定义一组可以提供给VaspInputGenerator的默认输入参数（config_dict）。默认情况下，VaspInputGenerator使用BaseVaspSet中的VASP输入参数的基本集。yaml，每个Maker都建立在它的基础上。如果需要，用户可以定义一个自定义.yaml文件，其中包含要使用的VASP设置的不同基本集。下面是一个代表性静态计算的示例。
    from atomate2.vasp.jobs.base import VaspInputGenerator
    # read in a custom config file
    user_config_dict = monty.serialization.loadfn(
        "/Users/wangjinlong/job/soft_learn/py_package_learn/atomate2_learn/atomate2/CustomVaspSet.yaml")
    # create a custom static set generator with user-defined defaults. Also change the NELMIN parameter to 6 (for demonstration purposes)
    my_custom_set = atomate2.vasp.sets.core.StaticSetGenerator(
        user_incar_settings={"NELMIN": 6},
        config_dict=user_config_dict,)
    # initialise the static maker to use the custom input set generator
    static_maker = atomate2.vasp.jobs.core.StaticMaker(
        input_set_generator=my_custom_set)
    # create a job using the customised maker
    static_job = static_maker.make(structure)
    return static_job

  def example_chaining_workflows(self):
    """https://materialsproject.github.io/atomate2/user/codes/vasp.html#connecting-vasp-jobs
    * 下面的代码说明了这两个示例，其中我们链接了一个松弛计算和一个静态计算。
    """

    si_structure = self.example_get_flow_Si()
    # si_structure = pymatgen.core.structure.Structure.from_file("Si.cif")
    # create a relax job
    relax_job = atomate2.vasp.jobs.core.RelaxMaker().make(structure=si_structure)
    # 只使用放松后的结构
    static_job = atomate2.vasp.jobs.core.StaticMaker().make(
        structure=relax_job.output.structure)
    # 使用先前计算的结构和附加输出。默认情况下，这些输出包括INCAR设置、带隙（用于自动设置KSPACING）和磁矩。一些工作流还将使用其他输出。例如，Band Structure工作流将从之前的计算中复制CHGCAR文件（电荷密度）。这可以通过设置structure和prev_dir参数来实现。
    static_job = atomate2.vasp.jobs.core.StaticMaker().make(
        structure=relax_job.output.structure,
        prev_dir=relax_job.output.dir_name
    )
    # create a flow including the two jobs and set the output to be that of the static
    my_flow = jobflow.Flow([relax_job, static_job], output=static_job.output)
    return my_flow

  def setting_system_Atomate2_OpenMM(self):
    # Setting up the system
    from pymatgen.core.structure import Molecule
    import numpy as np
    from atomate2.openff.core import generate_interchange
    # 如果您想知道字典中允许哪些参数，请查看atomate2.openff中的create_mol_spec函数。
    mol_specs_dicts = [
        {"smiles": "O", "count": 200, "name": "water"},
        {"smiles": "CCO", "count": 10, "name": "ethanol"},
        {"smiles": "C1=C(C=C(C(=C1O)O)O)C(=O)O",
         "count": 1, "name": "gallic_acid"},
    ]

    gallic_interchange_job = generate_interchange(
        input_mol_specs=mol_specs_dicts,
        mass_density=1.3
    )

    # 或者这样
    """
    from atomate2.openff.utils import create_mol_spec
    mols_specs = [create_mol_spec(**mol_spec_dict)
                  for mol_spec_dict in mol_specs_dicts]
    generate_interchange(mols_specs, 1.3)
    """

    # 在更复杂的模拟中，我们可能想要缩放离子电荷并包含自定义的部分电荷。EC:EMC:LiPF6电解质的示例如下所示。这将产生elyte_interchange_job对象，我们可以将其传递到模拟的下一个阶段。

    pf6 = Molecule(
        ["P", "F", "F", "F", "F", "F", "F"],
        [
            [0.0, 0.0, 0.0],
            [1.6, 0.0, 0.0],
            [-1.6, 0.0, 0.0],
            [0.0, 1.6, 0.0],
            [0.0, -1.6, 0.0],
            [0.0, 0.0, 1.6],
            [0.0, 0.0, -1.6],
        ],
    )
    pf6_charges = np.array([1.34, -0.39, -0.39, -0.39, -0.39, -0.39, -0.39])

    mol_specs_dicts = [
        {"smiles": "C1COC(=O)O1", "count": 100, "name": "EC"},
        {"smiles": "CCOC(=O)OC", "count": 100, "name": "EMC"},
        {
            "smiles": "F[P-](F)(F)(F)(F)F",
            "count": 50,
            "name": "PF6",
            "partial_charges": pf6_charges,
            "geometry": pf6,
            "charge_scaling": 0.8,
            "charge_method": "RESP",
        },
        {"smiles": "[Li+]", "count": 50, "name": "Li", "charge_scaling": 0.8},
    ]

    elyte_interchange_job = generate_interchange(mol_specs_dicts, 1.3)
    return elyte_interchange_job

  def Running_simulation_Atomate2_OpenMM(self):
    # https://materialsproject.github.io/atomate2/user/codes/openmm.html
    # OpenMMFlowMaker将能量最小化、压力平衡、退火和nvt模拟的制造商联系在一起。退火步骤是一个子流程，它使我们不必手动实例化三个独立的作业。
    # 我们创建生产流程并链接到generate_interchange作业，从而生成一个生产就绪的分子动力学工作流。
    from atomate2.openmm.flows.core import OpenMMFlowMaker
    from atomate2.openmm.jobs.core import (
        EnergyMinimizationMaker,
        NPTMaker,
        NVTMaker,
    )
    from jobflow import Flow, run_locally

    production_maker = OpenMMFlowMaker(
        name="production_flow",
        makers=[
            EnergyMinimizationMaker(traj_interval=10, state_interval=10),
            NPTMaker(n_steps=100),
            OpenMMFlowMaker.anneal_flow(n_steps=150),
            NVTMaker(n_steps=100),
        ],
    )
    elyte_interchange_job = self.setting_system_Atomate2_OpenMM()
    production_flow = production_maker.make(
        elyte_interchange_job.output.interchange,
        prev_dir=elyte_interchange_job.output.dir_name,
        # output_dir="./tutorial_system",
    )

    run_locally(Flow([elyte_interchange_job, production_flow]),
                store=self.get_jobstore(),)
    return None

  def eample_run_with_FireWorks(self):
    """一旦使用atomate2构造了工作流，就可以使用flow_to_workflow函数将其转换为FireWorks工作流。然后可以按照通常的方式将工作流提交到启动台。例如，使用FireWorks提交MgO波段结构工作流：
    """
    bandstructure_flow = self.example_get_flow_Si()
    # （可选）向流程任务文档中添加元数据。可以用来从数据库中过滤特定的结果。例如，为化合物添加材料项目ID，使用以下行
    # bandstructure_flow = atomate2.vasp.powerups.add_metadata_to_flow(
    #     flow=bandstructure_flow,
    #     additional_fields={"mp_id": "mp-190"},
    # )

    # convert the flow to a fireworks WorkFlow object
    wf = jobflow.managers.fireworks.flow_to_workflow(bandstructure_flow)

    # submit the workflow to the FireWorks launchpad
    lpad = fireworks.LaunchPad.auto_load()
    lpad.add_wf(wf)
    # 本地发射任务
    # self.FireWorksLearn.run_rocket_launcher(launchpad=lpad,
    #                                         is_rapidfire=True,
    #                                         fworker=fireworks.FWorker(),
    #                                         )
    return lpad

  def my_example_get_flows(self):
    # 建立结构
    atoms = ase.build.bulk(name='W', cubic=True)
    structure = self.get_structure_from_ase_atoms(atoms=atoms)
    # 构建流
    relax_job = atomate2.vasp.flows.core.UniformBandStructureMaker().make(structure=structure)
    # 修改参数
    incar_updates = {"ENCUT": 400, 'ISMEAR': 0,
                     'SIGMA': 0.05, 'PREC': 'Normal'}
    incar_updates = {}
    relax_job = self.modifying_input_sets(
        flow=relax_job, incar_updates=incar_updates)
    # 注意 store 存储的单元信息(task_doc) 是 job 而不是 flow, 所以要设置 job 的 name 用于之后 store 的查询
    relax_job.jobs[0].name = 'W_bulk_static'
    relax_job.jobs[1].name = 'W_bulk_non_scf'
    # 为了防止重复加入这个？ fireworks 才用这个，对于 jobflow-remote 则不用
    # metadata = {
    #     '_dupefinder': fireworks.user_objects.dupefinders.dupefinder_exact.DupeFinderExact(), }
    # relax_job.jobs[0].metadata = metadata
    # relax_job.jobs[1].metadata = metadata
    return relax_job

  def my_example_run_local(self):
    flow = self.my_example_get_flows()
    # 运行
    self.run_flow_locally(flow=flow,
                          root_dir='test/W_bulk',)
    return None

  def my_example_run_with_firework(self,
                                   job_config={},  # {"manager_config": {"_fworker": "fworker1"}},
                                   ):
    flow = self.my_example_get_flows()
    store = self.get_jobstore()
    flow.update_config(config=job_config,)
    # Converting a Flow to a Workflow
    wf = jobflow.managers.fireworks.flow_to_workflow(flow=flow, store=store, )

    # 加入发射台
    # lpad = self.FireWorksLearn.get_launchpad(is_local_DB=True,
    #                                          is_uri_DB=False)
    # lpad.add_wf(wf=wf)
    # 发射
    # self.FireWorksLearn.run_rocket_launcher(launchpad=lpad, is_rapidfire=True,
    #                                         fworker=fireworks.FWorker(),
    #                                         )
    return None

  def my_example_check_result(self):
    flow = self.my_example_get_flows()
    # 获得结构 和 画图
    atoms = self.get_atoms(criteria={'name': flow.jobs[0].name})
    self.plot_dos_wrapper(criteria={'name': flow.jobs[1].name})
    # self.plot_dos_wrapper(criteria={'name': 'W_bulk_non_scf'})
