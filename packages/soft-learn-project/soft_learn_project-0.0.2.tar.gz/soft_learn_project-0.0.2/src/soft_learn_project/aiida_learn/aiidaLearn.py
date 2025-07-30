
import aiida
import aiida.engine
import aiida.orm
import aiida.plugins
import ase.build
import ase
import aiida_vasp
import aiida_vasp.workchains.v2
import aiida_vasp.workchains.v2.bands
import os
import aiida_vasp.data.potcar


class AiidaLearn():
  def __init__(self) -> None:
    pass

  def install_and_configuration(self):
    r"""
    1. 建立环境
    conda create -n aiida python
    # Install Python Package
    git clone https://github.com/aiidateam/aiida-core
    cd aiida-core
    pip install -e .
    # Optional requirements
    conda install PyCifRW notebook
    pip install "aiida-core[atomic_tools,docs]"
    # RabbitMQ
    conda install aiida-core.services
    rabbitmq-server -detached  # 这必须在每次机器重新启动后执行。
    2. Create a profile
    conda install sqlite 
    conda install postgresql
    verdi profile setup core.sqlite_dos -n --profile-name myprofile --email 396292346@qq.com --use-rabbitmq  
    - 删除:  verdi profile delete myprofile
    2.1 psql
    # 建立空目录
    mkdir /Users/wangjinlong/job/soft_learn/aiida_learn/aiida_psql_db
    # 运行 initdb
    initdb -D /Users/wangjinlong/job/soft_learn/aiida_learn/aiida_psql_db
    # 启动 PostgreSQ
    # 可能需要: pg_ctl -D /Users/wangjinlong/opt/x86_64_anaconda/envs/aiida/var/postgresql stop
    pg_ctl -D /Users/wangjinlong/job/soft_learn/aiida_learn/aiida_psql_db -l logfile start
    # 连接到数据库：启动后，尝试连接到 PostgreSQL：
    psql -h localhost -d postgres # psql -h localhost -U wangjl -d postgres 
    CREATE USER aiida_user WITH PASSWORD '123456';
    CREATE DATABASE aiida_database OWNER aiida_user ENCODING 'UTF8';
    GRANT ALL PRIVILEGES ON DATABASE aiida_database to aiida_user;
    \l \q 
    # test 
    psql -h localhost -d aiida_database -U aiida_user # -W

    ---
    verdi profile setup core.psql_dos \
    --profile-name myprofile \
    --email 396292346@qq.com \
    --first-name jinlong \
    --last-name wang \
    --institution "tongling university" \
    --use-rabbitmq \
    --database-username aiida_user \
    --database-password 123456 \
    --database-name aiida_database \
    --repository-uri file:////Users/wangjinlong/job/soft_learn/aiida_learn/aiida_repository  # 
    # 验证
    verdi status 

    verdi daemon start
    3. Computer setup
    verdi computer setup -L local -H localhost -T core.local -S core.direct -w /Users/wangjinlong/job/soft_learn/aiida_learn/computer_node_tmp -n 
    # before the computer can be used, it has to be configured with the command
    verdi -p myprofile computer configure core.local local
    # check computer
    verdi computer test local
    #-
    verdi computer setup -L tutor -H localhost -T core.local -S core.direct -w `echo $PWD/work` -n
    verdi computer configure core.local tutor --safe-interval 1 -n
    verdi -p myprofile computer configure core.local local

    # 3.3 配置远程 
    verdi computer setup
    Report: enter ? for help.
    Report: enter ! to ignore the default and set no value.
    Computer label: hfeshell            
    Hostname: hfeshell
    Description []: my server hfeshell
    Transport plugin: core.ssh
    Scheduler plugin: core.slurm
    Shebang line (first line of each script, starting with #!) [#!/bin/bash]: 
    Work directory on the computer [/scratch/{username}/aiida/]: /public/home/wangjl/job/soft_learn/aiida_learn/aiida_learn/computer_node_tmp
    Mpirun command [mpirun -np {tot_num_mpiprocs}]: 
    Default number of CPUs per machine: 2
    Default amount of memory per machine (kB).: 
    Default amount of memory per machine (kB).: 
    Default amount of memory per machine (kB).: 4096000
    Escape CLI arguments in double quotes [y/N]: 
    Success: Computer<3> hfeshell created
    Report: Note: before the computer can be used, it has to be configured with the command:
    """
    pass

  def x(self, **kwds):
    pass


class AiidaVasp():
  def __init__(self) -> None:
    """conda create -n x86_aiida python=3.9
    https://github.com/aiida-vasp/aiida-vasp/blob/develop/README.md
    # learn
    https://aiida-vasp-plugin.readthedocs.io/en/latest/getting_started/configuration.html 
    https://aiida-vasp-plugin.readthedocs.io/en/latest/tutorials/silicon_sp.html
    """
    pass

  def install(self):
    """conda install aiida-vasp # 这个版本比较老 
    # https://aiida-vasp-plugin.readthedocs.io/en/latest/getting_started/installation.html
    git clone https://github.com/aiida-vasp/aiida-vasp.git
    cd aiida-vasp
    pip install -e ".[pre-commit]"
    * 验证 To verify the installation, you can run the following command:
    verdi plugin list aiida.calculations
    """
    pass

  def configrations(self):
    """
    To utilize AiiDA-VASP you will need to make sure that:
    - You have a working AiiDA version >= 2 installation (see note).
    - You have setup a profile in AiiDA.
    - That you hold a valid VASP license and that VASP is installed on some computer, for instance a remote HPC cluster.
    - VASP >= 5.4.4 is used. The plugin has been tested with both VASP 5.4.4 and VASP 6 versions.
    - You have defined a computer where VASP is installed and that you can SSH to that computer without using a password.

    1. Setting up a InstalledCode for your VASP executable
    verdi code create core.code.installed
    # 1.1 local 
    verdi code create core.code.installed
    Report: enter ? for help.
    Report: enter ! to ignore the default and set no value.
    Computer: local
    Filepath executable: /Users/wangjinlong/job/soft_learn/vasp_learn/package/vasp.6.4.0_on_mac_vaspsol_neb/bin/vasp_std
    Label: vasp
    Description []: vasp 6.4.0 std
    Default `CalcJob` plugin: vasp.vasp
    Escape using double quotes [y/N]: 
    Success: Created InstalledCode<1>
    # 1.2 ssh 
    verdi code create core.code.installed
    Report: enter ? for help.
    Report: enter ! to ignore the default and set no value.
    Computer: hfeshell
    Filepath executable: /public/home/wangjl/apprepo/vasp/6.4.0-optcell_intelmpi2017_hdf5_libxc/app/bin/vasp_std
    Label: vasp
    Description []: vasp 6.4.0 std
    Default `CalcJob` plugin: vasp.vasp
    Escape using double quotes [y/N]: 
    Success: Created InstalledCode<2>
    * check 
    verdi code show vasp@hfeshell
    2. Configure pseduopotentials (POTCARs)
    - verdi data vasp.potcar uploadfamily --path=/Users/wangjinlong/job/soft_learn/vasp_learn/vasp_pot/potpaw_PBE --name=PBE --description="PBE potentials version 54"

    """

    pass

  def setup_Computer(self, profile='myprofile'):

    profile_instance = aiida.load_profile(profile=profile,)
    # Uncomment the below line to create a localhost Computer if you have not done so
    comp = aiida.orm.Computer(label='localhost',
                              hostname='localhost',
                              transport_type='core.local',
                              scheduler_type='core.direct')
    comp.store()

    # Some configuration may be needed for first-time user
    comp.set_workdir('/tmp/aiida_run/')
    comp.configure()

    return comp

  def setup_Installedcode(self, comp):
    from pathlib import Path
    vasp_path = os.popen(cmd='which vasp_std').read().strip()
    vasp_code = aiida.orm.InstalledCode(computer=comp,
                                        filepath_executable=vasp_path,
                                        default_calc_job_plugin='vasp.vasp',
                                        label='vasp_test')
    # vasp_code.label = 'vasp_test'
    vasp_code.store()
    os.environ['MOCK_VASP_REG_BASE'] = str(
        (Path() / 'mock_registry').absolute())
    os.environ['MOCK_VASP_UPLOAD_PREFIX'] = 'singlepoint'
    print(os.environ['MOCK_VASP_REG_BASE'])
    pass

  def upload_potcar(self):
    # 这些似乎是命令行对应的python 命令
    # from aiida_vasp.data.potcar import PotcarData, PotcarFileData
    aiida_vasp.data.potcar.PotcarData.upload_potcar_family(source='/Users/wangjinlong/job/soft_learn/vasp_learn/vasp_pot/potpaw_PBE',
                                                           group_name="PBE", group_description="PBE 54")
    pass

  def query(self):
    # The advantage of using a database like AiiDA is that we can easily query for the results of our calculations. For example, to get all calculations that used the PBE.EXAMPLE family:

    q = aiida.orm.QueryBuilder()
    q.append(aiida.orm.WorkChainNode, tag='workchain', project=['*'])
    q.append(aiida.orm.Str, with_outgoing='workchain', edge_filters={'label': 'potential_family'},
             filters={'attributes.value': 'PBE'})
    query_result = q.all()
    return query_result

  def getting_started_example(self):
    """https://aiida-vasp-plugin.readthedocs.io/en/latest/getting_started/simple_calculation.html
    """

    aiida.load_profile(profile='myprofile')
    # First, we create the sample structure using the ase package (assuming the ase package is installed):
    si = ase.build.bulk('Si', 'diamond', 5.4)
    si_structure = aiida.orm.StructureData(ase=si)
    # Next, we create necessary input node and set the required parameters:
    builder = aiida.plugins.WorkflowFactory('vasp.v2.vasp').get_builder()

    builder.parameters = aiida.orm.Dict(
        dict={'incar':
              {
                  'encut': 300,
                  'ismear': 0,
                  'ispin': 1,
              }
              }
    )
    builder.options = aiida.orm.Dict(dict={
        'resources': {'num_machines': 1,
                      'tot_num_mpiprocs': 1}}
    )
    builder.structure = si_structure
    # Assuming VASP is installed locally and the code is configured
    builder.code = aiida.orm.load_code('vasp@localhost')
    # Note that we can use python type - they are converted into AiiDA types automatically
    builder.potential_family = 'PBE'
    builder.potential_mapping = {'Si': 'Si'}
    builder.kpoints_spacing = 0.05
    builder.metadata.label = 'test-calculation'
    # Finally, the calculation can be run with the run_get_node method:
    from aiida.engine import run_get_node
    out_dict, process_node = run_get_node(builder)
    # The out_dict is dictionary containing the output nodes of the VaspWorkChain and the process_node is a WorkChainNode representing the work chain that has been executed.
    # The total energy, forces and stress can be found in the misc output node:
    out_dict, process_node
    out_dict['misc']['total_energies']
    out_dict['misc']['forces']
    out_dict['misc']['stress']
    process_node.outputs.misc['total_energies']
    pass

  def load_node(self, pk):
    # Note that our workchain_node has a pk as well as a uuid. Both of them are identifiers for the node. You can load the node using the load_node method:
    # at a later time to access the results.
    node = aiida.orm.load_node(pk=pk)
    return node

  def get_upd(self,):
    # https://aiida-vasp-plugin.readthedocs.io/en/latest/tutorials/silicon_sp.html
    aiida.load_profile(profile='myprofile')
    si = ase.build.bulk('Si', 'diamond', 5.4)
    si_node = aiida.orm.StructureData(ase=si)

    # You can place your own preset at ~/.aiida-vasp/ and use them for production calculations.
    upd = aiida_vasp.workchains.v2.VaspBuilderUpdater().apply_preset(si_node,
                                                                     code='vasp@local',)
    upd.builder.potential_family = 'PBE'
    return upd

  def get_si_structure(self):
    # 获得结构节点 structure_node
    si = ase.build.bulk('Si', 'diamond', 5.4)
    si_structure = aiida.orm.StructureData(ase=si)
    return si_structure

  def single_point_example(self, pk=886,
                           code='vasp@local',):
    """_summary_

    Args:
        pk (int, optional): _description_. Defaults to 886.

    Returns:
        _type_: _description_
    """
    # https://aiida-vasp-plugin.readthedocs.io/en/latest/tutorials/silicon_sp.html
    aiida.load_profile(profile='myprofile')
    si_node = self.get_si_structure()

    # You can place your own preset at ~/.aiida-vasp/ and use them for production calculations.
    # /Users/wangjinlong/job/soft_learn/aiida_learn/package/aiida-vasp-develop/src/aiida_vasp/workchains/v2/common/VaspPreset.yaml
    upd = aiida_vasp.workchains.v2.VaspBuilderUpdater().apply_preset(
        initial_structure=si_node,
        code=code,)
    upd.builder.potential_family = 'PBE'
    # run the calculation using the run_get_node method:
    if pk:
      results_node = self.load_node(pk=pk)
    else:
      results_node = upd.run_get_node().node
    # Accessing the results
    # Useful information such as the total energy, forces and stresses are stored in the misc output node:
    results_dict = results_node.outputs.misc.get_dict()
    return results_node

  def geo_opt_example(self, pk=None, code='vasp@local',):
    profile = aiida.load_profile(profile='myprofile')
    # Setting up the silicon structure
    si_node = self.get_si_structure()

    # Similar to the single point calculation tutorial, we will use a BuilderUpdater to setup the inputs for the VaspRelaxWorkChain.
    upd = aiida_vasp.workchains.v2.VaspRelaxUpdater().apply_preset(
        si_node,
        code=code,)
    upd.builder.vasp.potential_family = 'PBE'
    upd.builder
    # We can now run the relaxation using the same run_get_node method as in the single point example.
    if pk:
      results_node = self.load_node(pk=pk)
    else:
      results = upd.run_get_node()
      results_node = results.node

    print(results_node.outputs.misc.get_dict())
    relaxed_node = results_node.outputs.relax.structure
    print(f"Volume before relaxations: {si_node.get_cell_volume():3f} A^3")
    print(f"Volume after relaxations: {relaxed_node.get_cell_volume():3f} A^3")
    atoms = relaxed_node.get_ase()
    return results_node

  def band_and_dos_example(self, pk=848):
    profile = aiida.load_profile(profile='myprofile')
    # Setting up the silicon structure
    si_node = self.get_si_structure()
    # Setting up the band structure and DOS calculation
    upd = aiida_vasp.workchains.v2.VaspBandUpdater().apply_preset(
        structure=si_node,
        code='vasp@local')
    upd.builder.scf.potential_family = 'PBE'

    opt = aiida_vasp.workchains.v2.bands.BandOptions()
    print(opt.aiida_description())
    # Run and inspect the results, We can now run the workchain and get the returned WorkChainNode object.
    if pk:
      band_out = self.load_node(pk=pk)
    else:
      band_out = upd.run_get_node().node

    band_out.outputs.band_structure.show_mpl()
    return band_out

  def workflow_pars(self):

    # 1. 通用方式
    workflow = aiida.plugins.WorkflowFactory('core.arithmetic.multiply_add')
    node = aiida.engine.run_get_node(workflow, x=aiida.orm.Int(
        1), y=aiida.orm.Int(2), z=aiida.orm.Int(3)).node
    print(node.outputs.result)  # 9
    # 2. The ProcessBuilder class 方式
    builder = aiida.plugins.WorkflowFactory('vasp.v2.vasp').get_builder()
    builder.parameters = aiida.orm.Dict(
        dict={'incar': {'encut': 500, 'ismear': 0}})
    builder.kpoints_spacing = 0.05
    builder
    # 3. 工作流构造输入的另一种方便方法: The BuilderUpdater class
    si_node = self.get_si_structure()
    upd = aiida_vasp.workchains.v2.VaspBuilderUpdater().apply_preset(
        initial_structure=si_node,
        code='vasp@local')
    # 获取现有的字典
    pars_dict: aiida.orm.Dict = upd.builder.parameters
    # 将 Dict 转换为普通的 Python 字典
    pars_data = pars_dict.get_dict()
    # 更新字典内容
    pars_data['incar']['encut'] = 400
    upd.builder.parameters = aiida.orm.Dict(dict=pars_data)

    # 3.2 或者 还可以使用附加到工作链类的方法创建BuilderUpdater对象。
    wc = aiida.plugins.WorkflowFactory('vasp.v2.vasp')
    upd = wc.get_builder_updater()
    upd.builder

    # 1
    builder = aiida.plugins.WorkflowFactory('vasp.v2.relax').get_builder()
    builder.vasp.parameters = aiida.orm.Dict(
        dict={'incar': {'encut': 500, 'isif': 2, 'nsw': 5, 'potim': 0.01}})
    # 2.
    builder = aiida.plugins.WorkflowFactory('vasp.v2.vasp').get_builder()
    # This gets converted to a Dict automatically
    builder.parameters = {
        'incar': {'encut': 500, 'isif': 2, 'nsw': 5, 'potim': 0.01}}

    # To see the available settings, one can use:
    opt = aiida.plugins.WorkflowFactory('vasp.v2.relax').option_class
    # opt.<tab> to see all available options
    print(opt.aiida_description())
