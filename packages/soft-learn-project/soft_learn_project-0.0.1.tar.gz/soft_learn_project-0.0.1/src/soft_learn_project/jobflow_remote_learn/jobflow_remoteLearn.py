import jobflow.core
import jobflow.core.flow
import jobflow_remote.config
import jobflow_remote.config.settings
from jobflow_remote.utils.examples import add
from jobflow import Flow
import jobflow
from jobflow_remote import get_jobstore
import os
import jobflow_remote.utils.examples
import jobflow_remote.config.base
import jobflow_remote.config.manager


class JobflowRemoteLearn():
  def __init__(self):
    """https://matgenix.github.io/jobflow-remote/user/introduction.html
    jobflow -remote是一个免费的开源库，用作执行工作流的管理器。虽然jobflow并不一定要由特定的管理器执行，并且已经开发了一些适配器（例如Fireworks），但jobflow-remote的设计是为了充分利用和适应jobflow的功能，并与研究人员可以访问的典型高性能计算中心进行交互。
    Jobflow的Jobs函数直接在计算资源上执行，但是，与Fireworks不同的是，与输出store的所有交互都由一个称为runner的守护进程处理。这样可以绕过计算中心不能直接访问用户数据库的问题。考虑到相对较小的需求，这就可以自由地运行jobflow-remote的守护进程
    ---
    以下是jobflow-remote主要特性的简短列表
    与jobflow完全兼容
    基于蒙古式岩浆存储的数据存储。
    简单的单文件配置作为起点。是否可以扩展以处理不同配置的不同项目
    完全可配置的提交选项
    通过python API和命令行接口进行管理
    并行守护进程执行
    限制每个工人提交的作业数量
    批量提交（实验）
    """
    # os.environ['jfremote_project'] = 'std'  # 配置默认的项目
    print('服务器上需要运行: nohup mongod --dbpath /public/home/wangjl/my_server/my/mongoDB &')
    pass

  def install(self):
    string = """pip install jobflow-remote
    or, for the development version:
    pip install git+https://github.com/Matgenix/jobflow-remote.git
    # conda install jobflow-remote  # 不行
    """
    print(string)
    return None

  def config(self):
    """https://matgenix.github.io/jobflow-remote/user/install.html#userworkstation-config
    https://matgenix.github.io/jobflow-remote/user/projectconf.html # /Users/wangjinlong/.jfremote/std.yaml 配置文件内容的解释
    * 标准的jobflow执行需要在JOBFLOW_CONFIG_FILE中定义输出JobStore。这里，所有与jobflow相关的配置都在jobflow-remote配置文件中给出，JOBFLOW_CONFIG_FILE的内容将被忽略。
    # worker 中 有个设置可以限制提交作业的数量
    max_jobs: 20 
    为了定义批处理工作者，应该在配置文件中填充该工作者的批处理部分。特别是应该定义jobs_handle_dir和work_dir。这些应该表示将用于管理远程作业的工作者文件系统中的路径。此外，应该设置worker的max_jobs选项。这将定义同时提交到队列的批处理作业的最大数量。因此，批处理工作者的最小配置是：
    # ----
    # 你可以通过运行命令获得初始设置配置：
    $ jf project generate std # std 是 YOUR_PROJECT_NAME
    $ jf project generate --full YOUR_PROJECT_NAME  # 给出完整配置文件, 项目规格部分给出了项目文件的所有类型和密钥的描述
    1. worker
    工人是实际执行作业流作业的计算单元。如果您使用All-in-one配置，则工作器类型可以是本地的，并且不需要提供主机。否则，应该提供SSH连接的所有信息。在本例中，假设可以基于~/的内容建立无密码连接。ssh / config文件。远程连接基于Fabric，因此可以使用它的所有功能。指定work_dir也很重要，在这里将创建用于Jobs执行的所有文件夹。
    2. Queue
    - 数据库的连接详细信息，该数据库将包含有关作业和流状态的所有信息。可以用类似于jobflow配置文件中使用的方式来定义它。为此将使用三个集合。
    3. jobstore 
    用于作业流的作业存储。它的定义等同于jobflow配置文件中使用的定义。有关详细信息，请参阅Jobflow的文档。它可以与Queue中的相同，也可以是不同的。
    * 检查
    $jf project check --errors # 在所有配置设置完成后，您可以通过运行命令来验证是否可以建立所有连接：
    $jf -p std  project check --errors # 如果有多个项目需要加个参数 
    $jf admin reset # 重置数据库, 这也将删除数据库的内容。如果重用现有数据库并且不想擦除数据，请跳过此步骤。
    """
    jfrs = jobflow_remote.config.settings.JobflowRemoteSettings(
        # config_file='/Users/wangjinlong/.jfremote/std.yaml',
        projects_folder='/Users/wangjinlong/.jfremote/std',
        project='std',
    )
    jfrs.config_file

    pass

  def config_check(self):
    os.sysmtem('jf project check --errors')
    return None

  def get_project_data(self):
    """有了projext 可以获得 queue store jobstore 等 
    ds = project.get_jobstore().docs_store
    ds.connect()
    ds.count()

    """
    project = jobflow_remote.config.manager.ConfigManager().get_project(project_name='std')
    project_data = jobflow_remote.config.manager.ConfigManager(
    ).get_project_data(project_name='std')
    return project_data

  def get_queue_store(self):
    project_data = self.get_project_data()
    queue_store = project_data.project.get_queue_store()
    queue_store.connect()
    return queue_store

  def get_jobstore(self):
    """
    与标准作业流执行一样，当作业完成时，其输出存储在定义的JobStore中。对于像本例中使用的简单情况，可以使用CLI直接获取输出：
    jf job output 2
    对于接受单个Job id的CLI命令，可以传递uuid或db_id。代码将自动确定

    对于更高级的工作流，获得结果的最佳方法是使用JobStore，就像使用通常的工作流输出一样。对于jobflow-remote，在python中访问JobStore的一种方便方法是使用get_jobstore辅助函数。

    # ---
    可以通过以下命令获取Job的详细信息：
    jf job info 2

    Returns:
        _type_: _description_
    """

    # 或者通过这种方法
    # store = jobflow_remote.get_jobstore(project_name=project_name)
    # store.connect()

    project_data = self.get_project_data()
    jobstore = project_data.project.get_jobstore()
    jobstore.connect()
    # 通过 $jf job info 2 查到 job 2 的 uuid
    # store.get_output('c096b1de-3d8b-4657-b6f3-014d0fab88c3')
    # 或者通过 flow 对象 获取
    # store.get_output(flow.job_uuids[0])
    # store.get_output(flow.job_uuids[1])
    return jobstore

  def remove_docs(self):
    queue_store = self.get_queue_store()
    queue_store.remove_docs()
    return None

  def flow_learn(self):
    """
    # 查看 flow 的状态
    与作业列表类似，可以使用以下命令获取流程列表及其状态：
    jf flow list
    # 删除流
    如果你需要删除一些流，而不需要重置整个数据库，你可以使用命令：
    jf flow delete -did 1
    # ---
    # 与作业的状态相比，流程状态列表得到了简化，因为多个作业状态将被分组在单个流程状态下。
    jobflow_remote.jobs.state.FlowState 
    """
    pass

  def get_flow_example(self, a=1, b=2,):
    job1 = jobflow_remote.utils.examples.add(a=a, b=b)
    job2 = jobflow_remote.utils.examples.add(job1.output, 2)
    flow = jobflow.Flow([job1, job2])
    # flow = jobflow.Flow([job1])
    return flow

  def get_exec_config(self,
                      modules=['compiler/intel/2017.5.239',
                               'load mpi/intelmpi/2017.4.239'],
                      export={'PATH': '/public/home/wangjl/apprepo/vasp/6.4.0-optcell_intelmpi2017_hdf5_libxc/app/bin:$PATH',
                              'LD_LIBRARY_PATH': '$SCRIPTDIR/app/lib:$LD_LIBRARY_PATH',
                              'PROGLIST': '/public/home/wangjl/apprepo/vasp/6.4.0-optcell_intelmpi2017_hdf5_libxc/app/bin/vasp_std'},
                      pre_run='conda activate atomate2',
                      ):
    exec_config = jobflow_remote.config.base.ExecutionConfig(
        modules=modules,
        export=export,
        pre_run=pre_run)
    return exec_config

  def get_resorces(self, queue_name='hfacnormal01',
                   job_name='vasp',
                   nodes=1,
                   process_placement=32,
                   processes_per_node=128,
                   time_limit=30000,
                   output_filepath='pbs.log',
                   error_filepath='pbs.err',):
    from py_package_learn.qtoolkit_learn import qtoolkitLearn
    ql = qtoolkitLearn.QtoolkitLearn()
    resources = ql.get_resources(queue_name=queue_name,
                                 job_name=job_name,
                                 nodes=nodes,
                                 process_placement=process_placement,
                                 processes_per_node=processes_per_node,
                                 time_limit=time_limit,
                                 output_filepath=output_filepath,
                                 error_filepath=error_filepath,)
    return resources

  def submit_flow(self, flow,
                  project='std',
                  worker="local_shell",
                  exec_config=None,
                  resources={}):
    """* e.g. : flow = self.get_flow_example()
    ---
    向选定的Worker提交一个计算流。
    这不会启动计算，而只是将要执行的计算添加到数据库中
    关于工人的选择：
    工作者应该与项目中定义的一个工作者的名称相匹配。
    这样，所有的工作将被分配给同一个工人。
    如果省略该参数，则使用项目配置中的第一个worker。
    在任何情况下，工作线程都是在将Job插入数据库时确定的。

    resources = {"nodes": 1, "ntasks": 4, "partition": "batch"}
    """

    # 这段代码将打印一个与提交的作业相关联的整数唯一id。
    result = jobflow_remote.submit_flow(flow=flow, worker=worker,
                                        project=project,
                                        exec_config=exec_config,
                                        resources=resources,)

    # $jf job list # 显示数据库中的Job列表, 查看任务
    print(result)
    return flow

  def runner_cmd(self, check_job=False,
                 runner_start=False,
                 runner_stop=False,
                 runner_check=False,
                 reset=False,
                 check_flow=False,
                 delete_flows=False,
                 flows_id=1,
                 ):
    """
    - check_job = 'jf job list -v '
    - runner_start = 'jf runner start'
    - runner_check = 'jf runner status'
    - runner_stop = 'jf runner stop'
    - check_flow = 'jf flow list'
    - delete_flows='jf flow delete -did 1'
    - jf flow delete -jid 5

    Args:
        check_job (bool, optional): _description_. Defaults to False.
        runner_start (bool, optional): _description_. Defaults to False.
        runner_stop (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """

    from py_package_learn.os_learn import osLearn
    ol = osLearn.OsLearn()
    if check_job:
      cmd = 'jf job list -v'
    elif runner_start:
      cmd = 'jf runner start'
    elif runner_stop:
      cmd = 'jf runner stop'
    elif runner_check:
      cmd = 'jf runner status'
    elif reset:
      cmd = 'jf admin reset'
    elif check_flow:
      cmd = 'jf flow list'
    elif delete_flows:
      cmd = f'jf flow delete -did {flows_id}'
    result = ol.run_cmd_popen(cmd=cmd)
    check_job = 'jf job list'
    print(result)
    return result

  # ---
  def runner_learn(self):
    """Jobflow-remote的Runner是一个对象，负责处理提交的Job。它执行几个操作来推进工作流的状态。对于每个工作：
    在WORKER中复制文件（即作业的输入和输出）。
    与WORKER的队列管理器（例如SLURM、PBS等）交互，提交作业并检查其状态
    更新数据库的内容
    执行Runner的标准方法是通过一个守护进程，它可以用jf CLI启动：
    $ jf runner start
    因为这个进程是在后台启动的，你可以用下面的命令检查它是否正确启动了：
    $jf runner status
    在作业执行期间，可以像以前一样检查它们的状态：
    # $jf job list # 查看任务
    Runner将继续检查数据库中是否有新作业提交，并在前一个操作完成后立即更新每个作业的状态。如果你打算继续提交工作流，你可以保持守护进程运行，否则你可以使用以下命令停止进程：
    $jf runner stop 
    stop命令将向Runner进程发送一个SIGTERM命令，该命令将在实际停止之前终止当前正在执行的操作。这样可以防止数据库中出现不一致的状态。但是，如果您认为运行程序卡住或需要立即停止运行程序，您可以使用以下命令终止进程：
    $jf runner kill
    # 查询是否有锁定的作业 
    $jf job list -v
    或者，可以使用 $jf job list -l 命令获取锁定的作业列表。
    # 如果作业不需要被锁定，可以使用命令解锁：
    $jf admin remove-lock -jid 5
    $jf job rerun --break-lock 5 # 或者这个
    # 每个项目都有自己的文件夹（默认情况下是~/.jfremote的子文件夹），日志可以在~/中找到。jfremote / PROJECT_NAME /日志目录。log文件包含由python Runner对象产生的日志消息。这更有可能包含与代码相关的错误信息。log是由管理守护进程的superord生成的日志。
    """

    pass

  def tuning_job_execution(self, flow):
    """具有耗时计算的作业需要正确配置用于执行它们的环境和资源。本节重点介绍哪些选项可以调优，以及jobflow-remote中可用于更改这些选项的方法。
    在 jobflow_remote.submit_flow() 中参数设置
    1. worker 
    worker是一个计算单元，它将实际执行Job中的功能。worker的列表在workers项目配置中给出。工作者是通过在项目中定义它们时使用的名称来设置的，在向数据库添加Flow时，应该始终为每个Job定义一个工作者。
    2. ExecutionConfig, 其中包含在执行作业之前和之后运行其他命令的信息。
      - 这些通常可用于定义要在HPC中心上加载的模块、要加载的特定python环境或为作业所需的某些可执行文件设置PATH。
      - 它们通常可以作为引用项目配置文件中定义的设置的字符串给出，也可以作为ExecutionConfig的实例给出。
    3. Resources, 如果执行作业的工作线程在排队系统（例如SLURM、PBS）的控制下运行，那么指定在运行作业时需要分配哪些资源也很重要。
    由于所有涉及排队系统的操作都是用qtoolkit处理的，所以jobflow-remote支持相同的功能。特别是，可以传递一个包含特定于所选队列系统的关键字的字典，也可以传递一个QResources的实例，QResources是一个为标准用例定义资源的通用对象。这些将用于填写模板并生成合适的提交脚本。

    """
    # Submission
    # 这将为之前未在作业中设置的所有作业设置传递的值。一旦将流提交给数据库，将不会考虑对flow对象的任何进一步更改。
    resources = {"nodes": 1, "ntasks": 4, "partition": "batch"}
    jobflow_remote.submit_flow(flow=flow,
                               worker="local_shell",
                               exec_config="somecode_v.x.y",
                               resources=resources
                               )

    # ---
    from jobflow_remote.utils.examples import add, value
    from jobflow_remote import submit_flow, set_run_config
    from jobflow import Flow

    job1 = value(5)
    job2 = add(job1.output, 2)

    flow = jobflow.Flow([job1, job2])
    # 每个作业流的Job都有一个 JobConfig 属性。这可以用于存储具有特定于该作业的配置的manager_config字典。
    # flow.config 就是 JobConfig 属性
    # 这可以通过 set_run_config 函数来完成，该函数根据job的名称或它们正在包装的可调用对象来定位job。考虑下面的例子,
    flow = jobflow_remote.set_run_config(flow_or_job=flow, name_filter="add",
                                         worker="secondw",
                                         exec_config="anotherconfig",)
    # 设置后, name 为 add 的 job 将在 'secondw' worker 上执行, 而 'value' job 将在 ‘firstw' worker 上执行
    # name_filter匹配包含传入字符串的任何名称。因此，使用name_filter=add将匹配名为add的作业和名为add more的作业。
    resources = {"nodes": 1, "ntasks": 4, "partition": "batch"}
    jobflow_remote.submit_flow(flow, worker="firstw",
                               exec_config="somecode_v.x.y", resources=resources)
    # ---
    # 将Job添加到数据库后，仍然可以更改其设置。这可以通过jf job set CLI命令来实现。例如：
    # $jf job set worker -did 8 example_worker  # 将DB id为8的Job的worker设置为example_worker。
    # 类似地，jf job set resources 和 jf job set exec-config 可用于设置资源和执行配置的值。
    pass

  def dealing_with_errors(self):
    """* 考虑到执行作业所需的几个操作，出现错误是正常的。特别是，错误可能发生在运行程序管理作业期间，或者在作业本身内部
    * 当Job无法完成时，第一个任务是了解错误的来源。在jobflow-remote中，错误主要分为两类：
    - 远程错误：运行程序处理作业时发生的错误。例如，这些错误包括将文件复制到工作线程或从工作线程复制文件的错误，或者与队列管理器交互的错误。
      - $jf job list # 运行后它的状态将以橙色突出显示。
      - $jf job info 1 # 显示一条错误消息或远程错误的堆栈跟踪。
      - 解决后, $jf job retry 1 
      - 如果出于任何原因，作业需要从头开始重新启动，即恢复到READY状态，可以通过运行： jf job rerun 1
    - Job errors：在worker上执行Job时发生的错误。例如，执行的代码失败或用户提供的错误输入。
      - $jf job list 
      - $jf job info 5  # 查看错误的详细信息, (5表示作业 db_id)
      - 最好的选择是研究 run_dir 文件夹中作业生成的输出文件, queue.out, 或者通过 $jf job queue-out 5 直接查看 queue.out
      - $jf job rerun 5  # 重新运行 job 
    # 如果错误是由于缺乏资源或错误的配置选项，这些可以使用特定的命令更新：
    - $jf job set resources
    - $jf job set exec-config
    - $jf job set worker
    # 在大多数情况下，这种错误需要删除旧的Flow（例如jf Flow delete -jid 5），并使用正确的输入重新提交它。
    """
    pass

  def runer_states(self):
    """* 描述 https://matgenix.github.io/jobflow-remote/user/states.html
    - Waiting states: 描述尚未开始的工作。
    - Running states: 运行程序已开始处理作业的状态
    - Completed state: 作业已成功完成的状态
    - Error states: 与作业中的某些错误相关联的状态，无论是编程错误还是执行过程中的错误。

    * 作业状态列表在jobflow_remote.jobs.state中定义。JobState对象。在这里，我们给出了每个状态的列表和简短的描述。
    """

    pass
