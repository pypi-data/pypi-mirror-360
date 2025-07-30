import fireworks
import fireworks.core.fworker
import fireworks.core.launchpad
import fireworks.core.rocket_launcher
import fireworks.examples
import fireworks.examples.tutorial_examples
import fireworks.examples.tutorial_examples.dynamic_wf2
import fireworks.features
from fireworks.flask_site.app import wf_details
import fireworks.fw_config
import fireworks.queue.queue_adapter
import fireworks.tests
import fireworks.tests.mongo_tests
import fireworks.core.firework
import fireworks.queue.queue_launcher
import os

import fireworks.user_objects
import fireworks.user_objects.firetasks
import fireworks.user_objects.firetasks.dataflow_tasks
import fireworks.utilities
import fireworks.utilities.filepad
from fireworks.user_objects.dupefinders.dupefinder_exact import DupeFinderExact
import fireworks.user_objects.dupefinders.dupefinder_exact
import fireworks.features.background_task
import fireworks.user_objects.queue_adapters.common_adapter
import fw_tutorials.dynamic_wf.printjob_task
import fw_tutorials.dynamic_wf.addmod_task
import fw_tutorials.dynamic_wf.fibadd_task


class LearnNotes():
  def __init__(self):
    pass

  def flask(self):
    from fireworks.flask_site.app import app
    app.lp = fireworks.LaunchPad()  # change the LaunchPad info if needed
    # optional basic password-protection
    # app.config["WEBGUI_USERNAME"] = ""
    # # optional basic password-protection
    # app.config["WEBGUI_PASSWORD"] = ""
    app.run(debug=False, port=5000)

  def lauchpad_learn(self):
    """https://materialsproject.github.io/fireworks/performance_tutorial.html
    """
    launchpad = fireworks.LaunchPad(
        user_indices=["spec.parameter1", "spec.parameter2"],  # 用来给FW spec 增加索引
        # 给Workflow metadata 增加索引
        wf_user_indices=["metadata.parameter1", "metadata.parameter2"],
    )
    return launchpad

  def firework_learn(self):
    """FW规范中的保留关键字: https://materialsproject.github.io/fireworks/reference.html
    例如: _tasks, _pass_job_info
    _tasks: 用于在规范中指定firetask列表。
    _pass_job_info: 设置为True将自动将有关当前作业的信息传递给子作业
    _files_in 和 files_out ——作为指定Firework的预期输入和输出文件的方法。请参阅参考资料了解更多详细信息。
    # 加入这个参数后可以避免重复计算, 相同的spec认为是同一个任务 或者 {'_fw_name': 'DupeFinderExact'}
    '_dupefinder': fireworks.user_objects.dupefinders.dupefinder_exact.DupeFinderExact()
    _background_tasks: 后台任务, 参见 self.firetask_background_task() 例子
    ---
    Write out the Workflow to a flat file, or load a Firework object from a file:
    fw_json = firework.to_file("my_firework.json")
    firework = firework.from_file("my_firework.json")

    Returns:
        _type_: _description_
    """
    # 要设置作业优先级，只需在Firework规范中设置一个名为_priority的键为所需的优先级。FireWorks将根据该键的值自动确定作业的优先级。
    fw = fireworks.Firework(spec={'_priority': 1,  # 数字越大先执行
                                  '_launch_dir': 'xx',  # 设置Firework执行的目录。
                                  # 这个名字要和 my_fworker.yaml 中的name 一致, 设置了_fworker变量的FireWorks只会在具有完全匹配的name变量的 FireWorker 上运行。
                                  '_fworker': 'mymac',
                                  # my_fworker.yaml 中的 category 一致, 也是设置  FireWorker 和 _fworker的作用一样
                                  '_category': 'mymac_local',
                                  # 如果你想让子Firework和父FireWorker运行在同一个FireWorker上，把父Firework的Firework规范中的 _preserve_fworker 键设置为True。这将自动将子进程的_fworker传递给父进程的FWorker。请参阅参考资料了解更多详细信息。
                                  '_preserve_fworker': True,
                                  # 加入这个参数后可以避免重复计算, 相同的spec认为是同一个任务
                                  '_dupefinder': {'_fw_name': 'DupeFinderExact'},
                                  # 或者
                                  '_dupefinder': fireworks.user_objects.dupefinders.dupefinder_exact.DupeFinderExact(),

                                  },
                            )
    return fw

  def workflow_learn(self):
    """

    Returns:
        _type_: _description_
    """
    wf = fireworks.Workflow()["metadata.parameter1", "metadata.parameter2"]
    return wf

  def scripttask_learn(self):
    """参数解释: https://materialsproject.github.io/fireworks/scripttask.html
    ScriptTask是FireWorks内置的Firetask，用于帮助通过命令行运行非python程序。例如，您可以使用ScriptTask来执行Java“JAR”文件或C代码。在内部，ScriptTask通过一个瘦Python包装器运行脚本（ScriptTask实际上只是另一个Firetask，没有任何特殊权限）。
    一些参数例如:
    store_stdout（默认值：False） -将整个标准输出存储在fireworklaunch对象的stored_data中
    stdout_file -（默认值：None） -将整个标准输出存储在此文件路径中。如果None，标准输出将被流式传输到sys.stdout
    store_stderr -（默认值：False） -将整个标准错误存储在fireworklaunch对象的stored_data中
    stderr_file -（默认值：None） -将整个标准错误存储在此文件路径中。如果None，标准错误将被流式传输到sys.stderr
    ---
    - 内置的ScriptTask选项可能不够灵活，无法满足您的所有需求。例如，您可能希望返回一个复杂的FWAction，该FWAction存储来自作业的自定义数据，并以复杂的方式（例如在Java或C代码中）修改Workflow。要实现这一点，您的脚本可以编写一个名为FWAction的文件。json或FWAction。该文件包含FWAction对象的序列化。FireWorks将读取该文件，并将ScriptTask返回的简单FWAction替换为您在该文件中指定的FWAction。
    - 默认情况下，ScriptTask的参数应该在与ScriptTask对应的规范的_task部分中定义，而不是作为规范的根键。如果您想在规范的根部分中指定参数，可以在_task部分中将_use_global_spec设置为True。请注意，_use_global_spec可以简化FireWorks之间参数的查询和通信，但如果在同一个Firework中有多个scripttask，则可能会导致问题。
    """
    ftask = fireworks.ScriptTask(script=['echo ok'])
    return ftask

  def templatewritertask_learn(self):
    """https://materialsproject.github.io/fireworks/templatewritertask.html
    option1 = {{opt1}}
    option2 = {{opt2}}

    {% if optparam %}OPTIONAL PARAMETER
    {{ optparam }}{% endif %}

    LOOP PARAMETERS
    {% for param in param_list %}{{ param }}
    {% endfor %}
    """
    ftask = fireworks.TemplateWriterTask(append='',  # 追加-追加到输出文件，而不是覆盖它
                                         template_dir='',  # Template_dir——这实际上是设置模板目录的第三个选项
                                         )
    return ftask

  def firetask_fileIO_learn(self,
                            filename='words.txt',
                            dest='/Users/wangjinlong/job/soft_learn/py_package_learn/jobflow_learn',
                            ):
    """https://materialsproject.github.io/fireworks/fileiotasks.html

    Args:
        filename (str, optional): _description_. Defaults to 'words.txt'.
        dest (str, optional): _description_. Defaults to '/Users/wangjinlong/job/soft_learn/py_package_learn/jobflow_learn'.

    Returns:
        _type_: _description_
    """
    ftask1 = fireworks.FileWriteTask({'files_to_write': [{'filename': filename,
                                                          'contents': 'abc de\n eee', }],
                                      'dest': dest, })
    ftask2 = fireworks.FileDeleteTask({'files_to_delete': [filename],
                                      'dest': dest})
    # 本地传输
    ftask3 = fireworks.FileTransferTask({'files': [{'src': f'{dest}/words.txt',
                                                    'dest': f'~/tmp/{filename}'}],
                                         'mode': 'copy'})
    # 远程传输
    ftask4_remote = fireworks.FileTransferTask({'mode': 'rtransfer',
                                                'server': 'hfeshell.nscc-hf.cn',
                                                'port': 65062,
                                                'key_filename': None,  # '/Users/wangjinlong/.ssh/id_rsa.pub',
                                                'files': [{'src': f'/Users/wangjinlong/job/soft_learn/py_package_learn/jobflow_learn/{filename}', 'dest': f'/public/home/wangjl/tmp/{filename}'}], }
                                               )
    ftask5 = fireworks.CompressDirTask(
        {'dest': '/Users/wangjinlong/job/soft_learn/py_package_learn/jobflow_learn/test'})
    ftask6 = fireworks.ArchiveDirTask(
        {'base_name': 'words', 'format': 'gztar'})
    return [ftask1, ftask2, ftask3, ftask4_remote, ftask5, ftask6]

  def pytask_learn(self):
    """https://materialsproject.github.io/fireworks/pytask.html
    """
    from fireworks.user_objects.firetasks.script_task import PyTask
    # 下面是一个定义PyTask休眠5秒的例子:
    fw_timer = fireworks.Firework(
        fireworks.PyTask(func='time.sleep', args=[5]))
    # PyTask()
    pass

  def queue_adapter_learn(self):
    """https://materialsproject.github.io/fireworks/qadapter_programming.html
    """
    import fireworks.user_objects.queue_adapters.common_adapter
    fireworks.user_objects.queue_adapters.common_adapter.CommonAdapter()
    return None

  def Updating_values_learn(self):
    """https://materialsproject.github.io/fireworks/update_text.html
    """
    import fireworks.utilities.update_collection
    fireworks.utilities.update_collection.update_launchpad_data()

    return None

  def filepad_learn(self):
    """ https://materialsproject.github.io/fireworks/filepad_tutorial.html
    FilePad实用程序提供api添加和删除任意大小的任意文件到MongoDB（FilePad）。这是通过将整个文件内容插入GridFS并将GridFS插入返回的id、用户提供的标识符和元数据存储在文件pad中的文档中来实现的。在下面的文档中，file contents指的是存储在GridFS中的文件内容，document指的是存储file_id、标识符和其他与文件相关的杂项信息的相关mongodb文档。

    Returns:
        _type_: _description_
    """
    fp = fireworks.utilities.filepad.FilePad()
    return None

  def firetask_dataflow_learn(self):
    """https://materialsproject.github.io/fireworks/dataflow_tasks.html
    """
    # CommandLineTask提供了在shell中使用命令行选项处理命令的方法，管理命令的输入和输出，从父烟花接收文件元数据并将文件元数据传递给子烟花。
    fireworks.user_objects.firetasks.dataflow_tasks.CommandLineTask()
    # ForeachTask的目的是通过插入子烟花的并行部分，在这个烟花和它的子烟花之间动态地分支工作流。生成的并行烟花的数量由split参数或可选的chunks参数指定的列表长度决定。每个子Firework包含一个Firetask（类PyTask， CommandLineTask或任何Firetask与输入参数），从这个列表中处理一个元素（或一个块）。在绕道之后，使用推送方法（即输出）将输出传递给Firework的规范
    fireworks.user_objects.firetasks.dataflow_tasks.ForeachTask()
    # 这个Firetask将spec中的指定项组合到spec中新的或现有的字典中。
    fireworks.user_objects.firetasks.dataflow_tasks.JoinDictTask()

    pass

  def get_wf_from_yaml(self):
    """如果只是在python 中运行 则可以跳过 这部分

    Returns:
        _type_: _description_
    """
    import yaml
    with open('/Users/wangjinlong/job/soft_learn/py_package_learn/fireworks_learn/fireworks/fw_tutorials/dynamic_wf/addmod_wf.yaml', mode='r') as yf:
      dct = yaml.safe_load(yf)
    wf = fireworks.Workflow.from_dict(dct)
    return wf

  def FWAction_learn(self):
    """ * FWAction 对象参数: https://materialsproject.github.io/fireworks/guide_to_writing_firetasks.html
    * 例如: stored_data, mod_spec, additions, detours
    - stored_data: Stored_data: 运行时要存储的数据。数据与FWAction的其余部分一起放在Launch数据库中。不影响FireWorks的运行。
    - update_spec:(dict)一个数据字典, 它将更新任何剩余的firetask和以下Firework的规范。因此, 该参数可用于在firetask之间或FireWorks之间传递数据。注意, 如果原始的fw_spec和update_spec包含相同的键, 原始的将被覆盖。
    - mod_spec:([dict])这与update_spec有相同的目的-在firetask /FireWorks之间传递数据。然而, update_spec选项是有限的, 因为它不能增加变量或追加到列表。该参数允许使用DictMod语言更新子FW的规范, 这是一种类似蒙古的语法, 允许对fw_spec进行更细粒度的更改。
    - ([工作流])将wf / fw添加到此烟花的子列表。
    - detours:([工作流])要添加的wf /FW的子列表(它们将继承当前FW的子)
    ---
    - Dynamic Workflow 的动态性只来自于FWAction对象；接下来, 我们将更详细地介绍这个对象。
    - Firetask(或PyTask调用的函数)可以返回一个FWAction对象, 该对象可以执行许多功能强大的操作。注意, FWAction在执行后存储在FW数据库中, 因此您可以随时返回并查看不同的firetask返回的操作。下面是不同的FWActions的示意图:
    """
    # 参见
    # 注册
    self.firetask_example_custom_MyArchiveDirTask()
    # _pass_job_info
    self.firetask_example_custom_addtask()
    # 动态性
    self.launch_workflow_example_fabnaci()
    pass


class FireWorksLearn():
  def __init__(self) -> None:
    """官网: https://materialsproject.github.io/fireworks/
    “给我六个小时砍倒一棵树, 我会用前四个小时来磨斧头。”
        ——亚伯拉罕·林肯
    - FireWorks是用于定义、管理和执行工作流的免费开源代码。复杂的工作流可以使用Python、JSON或YAML定义, 使用MongoDB存储, 并可以通过内置的web界面进行监控。工作流执行可以在任意计算资源上自动化, 包括那些具有排队系统的计算资源。FireWorks已被用于运行数百万个工作流, 这些工作流涵盖了跨越不同应用领域和多年的长期生产项目的数千万cpu小时。

    - 我的认识是: jobflow 和 fireworks 都是建立并执行工作流, 但 fireworks 学习起来很费劲很难理解, 用了很多命令行操作, 直接学习 jobflow 并应用 jobflow 就好了
    ---
    @article {CPE:CPE3505,
    author = {Jain, Anubhav and Ong, Shyue Ping and Chen, Wei and Medasani, Bharat and Qu, Xiaohui and Kocher, Michael and Brafman, Miriam and Petretto, Guido and Rignanese, Gian-Marco and Hautier, Geoffroy and Gunter, Daniel and Persson, Kristin A.},
    title = {FireWorks: a dynamic workflow system designed for high-throughput applications},
    journal = {Concurrency and Computation: Practice and Experience},
    volume = {27},
    number = {17},
    issn = {1532-0634},
    url = {http://dx.doi.org/10.1002/cpe.3505},
    doi = {10.1002/cpe.3505},
    pages = {5037--5059},
    keywords = {scientific workflows, high-throughput computing, fault-tolerant computing},
    year = {2015},
    note = {CPE-14-0307.R2},
    }

    ---
    fireworks 只有两个组成部分:
    LaunchPad: 管理工作流的服务器(“LaunchPad”)。您可以将工作流(“FireWorks”的DAG)添加到LaunchPad, 查询工作流的状态, 或者重新运行工作流。工作流可以是一系列简单的脚本, 也可以根据获得的结果动态调整。
    worker: 运行作业的一个或多个工人(“FireWorkers”)。FireWorkers从LaunchPad请求工作流, 执行它们, 然后发回信息。FireWorker可以简单到与承载LaunchPad的工作站一样, 也可以很复杂

    您可能会注意到, FireWorks代码库将“Firework”对象视为原子计算作业。作业在Firework级别启动、跟踪、重新启动和重复检查。firetask是一种便利, 它可以让您简化与拥有多个FireWorks相关的一些开销, 特别是当您希望在同一目录和同一台机器上运行多个任务时。然而, Firetask级别上可用的特性并不多。
    ---
    使用LaunchPad很容易启动web框架: $lpad webgui
    """
    self.LearnNotes = LearnNotes()
    self.firework_env()
    pass

  def install(self):
    string = """ https://github.com/materialsproject/fireworks
    conda install fireworks
    ---
    pip install FireWorks
    # (only needed for seeing visual report plots in web gui!)
    pip install matplotlib
    # (only needed if using built-in remote file transfer!)
    pip install paramiko
    pip install fabric  # (only needed if using daemon mode of qlaunch!)
    # (only needed if you want to use the NEWT queue adapter!)
    pip install requests
    # follow instructions to install argcomplete library if you want auto-complete of FWS commands
    """
    print(string)
    return None

  def firework_env(self):
    """https://materialsproject.github.io/fireworks/config_tutorial.html

    # 设置
    os.environ['FW_CONFIG_FILE'] = '/Users/wangjinlong/job/soft_learn/py_package_learn/fireworks_learn/fireworks/fw_tutorials/fw_config/FW_config.yaml'  # 以后再改
    # 在文件 FW_config.yaml 中写入
    LAUNCHPAD_LOC: fullpath/to/my_launchpad.yaml
    FWORKER_LOC: fullpath/to/my_fworker.yaml
    QUEUEADAPTER_LOC: fullpath/to/my_qadapter.yaml
    # 加上这个或者上面三个
    CONFIG_FILE_DIR: /Users/wangjinlong/job/soft_learn/py_package_learn/fireworks_learn/fireworks/fw_tutorials/worker
    # 还可以加入一些别的设置: https://materialsproject.github.io/fireworks/config_tutorial.html
    例如:
    PRINT_FW_JSON: True -是否打印FW。运行目录下的Json文件
    WEBSERVER_HOST: 127.0.0.1—运行web服务器的默认主机
    WEBSERVER_PORT: 5000—运行web服务器的默认端口
    TEMPLATE_DIR: 自定义模板的目录
    ---
    测试是否被激活 os.environ['FW_CONFIG_FILE'] = '' 时 和 '...' 是不一样的
    $lpad - -version
    """
    fireworks.fw_config.LAUNCHPAD_LOC = '/Users/wangjinlong/job/soft_learn/py_package_learn/fireworks_learn/fw_config1/my_launchpad1.yaml'
    fireworks.fw_config.FWORKER_LOC = '/Users/wangjinlong/job/soft_learn/py_package_learn/fireworks_learn/fw_config1/my_fworker1.yaml'
    fireworks.fw_config.QUEUEADAPTER_LOC = '/Users/wangjinlong/job/soft_learn/py_package_learn/fireworks_learn/fw_config1/my_qadapter1.yaml'
    # 直接设置这个就行了？
    os.environ['FW_CONFIG_FILE'] = '/Users/wangjinlong/job/soft_learn/py_package_learn/fireworks_learn/fw_config1/FW_config1.yaml'  # 以后再改

    # ---
    # 或者直接设置 CONFIG_FILE_DIR 目录下应该包含 my_launchpad.yaml, my_fworker.yaml, and my_qadapter.yaml
    # fireworks.fw_config.CONFIG_FILE_DIR = '/Users/wangjinlong/job/soft_learn/py_package_learn/fireworks_learn/fw_config1'
    #  my_launchpad.yaml 的修改

    # ---
    fireworks.fw_config.override_user_settings()
    pass

  def get_launchpad(self, is_local_DB=True,
                    is_uri_DB=False,
                    strm_lvl='WARNING'):
    """  *lpad 可以查看 db 和数据集*
    - mc = lpad.connection
    - db = mc.get_database(name='myMongoDB')
    - db.list_collection_names()
    - col = db.get_collection(name='myMongoDB_Collection')
    - col = db.get_collection(name='fireworks')
    - col.find_one()

    lpad.db.list_collection_names()
    col = lpad.db.get_collection('fireworks')
    col.count_documents({})
    col.find_one({'name': 'myadd'})
    lpad.db.list_collection_names()

    Args:
        is_local_DB (bool, optional): _description_. Defaults to False.
        is_uri_DB (bool, optional): _description_. Defaults to True.
    """

    if is_local_DB:
      lpad: fireworks.LaunchPad = fireworks.LaunchPad(host="localhost",
                                                      port=27017,
                                                      name="fireworks",
                                                      strm_lvl=strm_lvl,)
    elif is_uri_DB:
      lpad: fireworks.LaunchPad = fireworks.LaunchPad(host='mongodb+srv://396292346_wjl:1011320sr@cluster0.tgum0.mongodb.net/myMongoDB',
                                                      uri_mode=True,
                                                      strm_lvl=strm_lvl)
      # 这样也行
      # launchpad = fireworks.LaunchPad.from_dict(
      #     {'host': 'mongodb+srv://396292346_wjl:1011320sr@cluster0.tgum0.mongodb.net/myMongoDB',
      #      'uri_mode': True})
    # else:
    #   pass
    # 运行lpad reset将清除您的FireWorks启动板，所以只有当您是新用户时才使用此命令。
    # launchpad.reset('', require_password=False)  # ?
    # store workflow and launch it locally
    return lpad

  def get_launchpad_collection(self, lpad: fireworks.LaunchPad,
                               name_col=None):
    col_list = lpad.db.list_collection_names()
    print(col_list)
    if name_col is None:
      return
    else:
      return lpad.db.get_collection(name=name_col)

  def get_mongoDB(self):
    from py_package_learn.pymongo_learn import pymongoLearn
    pl = pymongoLearn.PymongoLearn()
    cli = pl.get_client(host='localhost')
    cli.list_database_names()
    db = cli.get_database(name='fireworks')
    db.list_collection_names()
    db.get_collection(name='fireworks').find_one({'name': 'myadd'})
    return db

  def run_rocket_launcher(self,
                          launchpad: fireworks.LaunchPad,
                          is_launch_rocket=False,
                          is_rapidfire=False,
                          fworker=fireworks.FWorker(),
                          ):
    """虽然大多数人会使用命令行向队列提交作业, 但您也可以通过Python提交作业。
    这个例子类似于前面的关于运行rapidfire命令的教程, 但是您想要替换 fireworks.core.rocket_launcher.quickfire 为
    fireworks.core.queue_launcher.rapidfire 并相应地调整参数。

    Args:
        launchpad (fireworks.LaunchPad): _description_
        firework (fireworks.Firework): _description_

    Returns:
        _type_: _description_
    """

    # launch_rocket  只能运行一个火箭,  rapidfire 才可以: Run in rapid-fire mode
    if is_launch_rocket:
      fireworks.core.rocket_launcher.launch_rocket(launchpad=launchpad,
                                                   fworker=fworker)
    if is_rapidfire:
      fireworks.core.rocket_launcher.rapidfire(launchpad=launchpad,
                                               fworker=fworker)
    # 提交任务
    # fireworks.queue.queue_launcher.rapidfire()
    # fireworks.queue.queue_adapter.
    return None

  def query(self):
    """
    查询FireWorks和工作流/生成报表¶
    FireWorks提供了两个函数来获取有关工作流的信息。lpad get_fws命令查询单个FireWorks(工作流中的步骤), 而lpad get_wflows命令查询整个工作流。报告特性允许您生成关于运行时统计信息的详细报告。
    !lpad get_fws -s COMPLETED -d count # 计算完成烟花的数量
    !lpad get_fws -s FIZZLED -d all -m 3 --rsort updated_on
    !lpad get_fws -n my_fw -d all
    !lpad get_fws -i 1 -d more
    !lpad get_wflows -s COMPLETED -d count # 统计已完成工作流的数量:
    !lpad get_wflows -i 1 -d more # 显示包含fw_id为1的Firework的工作流摘要:
    # 显示元数据包含my_parameter值等于3的所有工作流的摘要:
    !lpad get_wflows -q '{"metadata.my_parameter":3}' -d more
    !lpad report
    !lpad report -c wflows
    !lpad report -c launches
    """

    pass

  def example_quickstart(self):
    # set up the LaunchPad and reset it
    launchpad = fireworks.LaunchPad()
    launchpad.reset('', require_password=False)

    # create the individual FireWorks and Workflow
    fw1 = fireworks.Firework(
        fireworks.ScriptTask.from_str('echo "hello"'), name="hello")
    fw2 = fireworks.Firework(fireworks.ScriptTask.from_str(
        'echo "goodbye"'), name="goodbye")
    wf = fireworks.Workflow([fw1, fw2], {fw1: fw2}, name="test workflow")

    # store workflow and launch it locally
    launchpad.add_wf(wf)
    fireworks.core.rocket_launcher.rapidfire(launchpad)
    return None

  def example_intruduction(self):
    # set up the LaunchPad and reset it
    launchpad = fireworks.LaunchPad()
    launchpad.reset('', require_password=False)

    # create the Firework consisting of a single task
    firetask = fireworks.ScriptTask.from_str(
        'echo "howdy, your job launched successfully!"')
    firework = fireworks.Firework(firetask)

    # store workflow and launch it locally
    launchpad.add_wf(firework)
    fireworks.core.rocket_launcher.launch_rocket(launchpad)
    return None

  def example_custom_addtask(self,
                             name_fw='myadd',
                             launch_dir='/Users/wangjinlong/job/soft_learn/py_package_learn/jobflow_learn/test',
                             input_array=[1, 3]):
    """https://materialsproject.github.io/fireworks/guide_to_writing_firetasks.html
    我自己定义的 Firetask
    例子: 参见 -> from py_package_learn.fireworks_learn import MyArchiveDirTask
    1. 这个模块需要在Python的搜索路径内, 2. 必须注册您的Firetask, 通过添加 @fireworks.explicit_serialize 装饰器就可以
    """
    from fw_tutorials.firetask.addition_task import AdditionTask  # 可以从这里看源代码
    # 实际代码的理解和解释
    # @fireworks.explicit_serialize  # 添加@explicit_serialize装饰器可以省略 类属性 _fw_name

    class AdditionTask(fireworks.FiretaskBase):  # 继承 FiretaskBase 类
      # 特殊参数_fw_name设置为“添加任务”。该参数设置Firetask将被外部调用的内容, 并用于引导对象, 如前一节所述。如果我们没有自己设置, 默认值将是(根模块名加上用冒号分隔的类名)fireworks:AdditionTask
      _fw_name = "Addition Task"

      def run_task(self, fw_spec):
        input_array = fw_spec["input_array"]
        m_sum = sum(input_array)
        print(f"The sum of {input_array} is: {m_sum}")

        return fireworks.FWAction(stored_data={"sum": m_sum},
                                  mod_spec=[{"_push": {"input_array": m_sum}}])

    # create the Firework consisting of a custom "Addition" task
    firework = fireworks.Firework(tasks=AdditionTask(),
                                  name=name_fw,
                                  spec={"input_array": input_array,
                                        '_launch_dir': launch_dir,
                                        '_dupefinder': fireworks.user_objects.dupefinders.dupefinder_exact.DupeFinderExact(),
                                        },
                                  )
    # set up the LaunchPad and reset it
    lpad = fireworks.LaunchPad()
    # launchpad.reset('', require_password=False)
    # store workflow and launch it locally
    lpad.add_wf(firework)
    fireworks.core.rocket_launcher.launch_rocket(launchpad=lpad,
                                                 fworker=fireworks.FWorker())
    return None

  def example_Creating_Workflows(self):
    # set up the LaunchPad and reset it
    launchpad = fireworks. LaunchPad()
    # launchpad.reset('', require_password=False)

    # define four individual FireWorks used in the Workflow
    task1 = fireworks.ScriptTask.from_str('echo "Ingrid is the CEO."')
    task2 = fireworks.ScriptTask.from_str('echo "Jill is a manager."')
    task3 = fireworks.ScriptTask.from_str('echo "Jack is a manager."')
    task4 = fireworks.ScriptTask.from_str('echo "Kip is an intern."')

    fw1 = fireworks.Firework(task1)
    fw2 = fireworks.Firework(task2)
    fw3 = fireworks.Firework(task3)
    fw4 = fireworks.Firework(task4)

    # assemble Workflow from FireWorks and their connections by id
    workflow = fireworks.Workflow(
        [fw1, fw2, fw3, fw4], {fw1: [fw2, fw3], fw2: [fw4], fw3: [fw4]})

    # store workflow and launch it locally
    launchpad.add_wf(workflow)
    fireworks.core.rocket_launcher.rapidfire(launchpad, fireworks.FWorker())
    pass

  def example_Dynamic_Workflows_1_passjobinfo(self):
    """在工作流中的FireWorks之间传递信息
    定义根据任务输出自动创建更多FireWorks的firetask
    """
    # create the Workflow that passes job info
    fw1 = fireworks.Firework([fireworks.ScriptTask.from_str(
        'echo "This is the first FireWork"')], spec={"_pass_job_info": True}, fw_id=1)
    fw2 = fireworks.Firework(
        [fw_tutorials.dynamic_wf.printjob_task.PrintJobTask()], parents=[fw1], fw_id=2)
    wf = fireworks.Workflow([fw1, fw2])

    # set up the LaunchPad and reset it
    launchpad = fireworks.LaunchPad()
    # launchpad.reset('', require_password=False)
    # store workflow and launch it locally
    launchpad.add_wf(wf)
    fireworks.core.rocket_launcher.rapidfire(launchpad)
    pass

  def example_Dynamic_Workflows_2_add(self, ):
    firework1 = fireworks.Firework(tasks=fw_tutorials.dynamic_wf.addmod_task.AddModifyTask(),
                                   spec={"input_array": [1, 2],
                                         #  '_dupefinder': {'_fw_name': 'DupeFinderExact'},
                                         })
    firework2 = fireworks.Firework(tasks=fw_tutorials.dynamic_wf.addmod_task.AddModifyTask(),
                                   spec={"input_array": [10],
                                         #  '_dupefinder': {'_fw_name': 'DupeFinderExact'},
                                         })
    # workflow
    wf = fireworks.Workflow(fireworks=[firework1, firework2],
                            links_dict={firework1: [firework2]}
                            )
    # set up the LaunchPad and reset it
    launchpad = fireworks.LaunchPad()
    # launchpad.reset('', require_password=False)
    # store workflow and launch it locally
    launchpad.add_wf(wf)
    fireworks.core.rocket_launcher.rapidfire(launchpad)
    return None

  def example_Dynamic_Workflows_3_fabonacci(self):
    # create the Firework consisting of a custom "Fibonacci" task
    firework = fireworks.Firework(
        tasks=fw_tutorials.dynamic_wf.fibadd_task.FibonacciAdderTask(),
        spec={"smaller": 0, "larger": 1, "stop_point": 100})

    # set up the LaunchPad and reset it
    launchpad = fireworks.LaunchPad()
    # launchpad.reset('', require_password=False)
    # store workflow and launch it locally
    launchpad.add_wf(firework)
    fireworks.core.rocket_launcher.rapidfire(launchpad, fireworks.FWorker())
    return None

  def example_custom_firetask_ArchiveDirTask(self):
    from py_package_learn.fireworks_learn import myFireTask  # 查看里面的解释
    ftask = myFireTask.ArchiveDirTask()
    fw = fireworks.Firework(tasks=ftask,
                            spec={'base_name': 'words',
                                  'format': 'gztar'})
    return fw

  def example_File_passing_Workflows(self):
    """
    _files_in和_files_out都是{mapped_name: actual_file_name}的字典。如果子Firework的_files_in与父Firework的files_out相交，则这些文件将自动复制并重命名，并透明地处理gzip、bzip2压缩。在上面的示例中，fw1生成一个名为test1的文件，该文件位于_files_out中，名称为fwtest1。fw2的files_in包含fwtest1，这意味着将文件test1复制到fw2的启动目录，并将其重命名为hello。同样的概念也适用于fw2和fw3，不过在本例中，将fw2的gzip压缩文件移动到fw3的启动目录中，解压缩并以fwtest2的形式提供。请注意，映射的名称必须符合MongoDB的规则，即'.'和'$'不能是第一个字符。对实际文件名没有限制。

    Returns:
        _type_: _description_
    """
    fw1 = fireworks.Firework(
        [fireworks.ScriptTask.from_str(
            'echo "***** This is the first FireWork *****" > test1')],
        spec={"_files_out": {"fwtest1": "test1"}}, fw_id=1)
    fw2 = fireworks.Firework([fireworks.ScriptTask.from_str('gzip hello')], fw_id=2,
                             parents=[fw1],
                             spec={"_files_in": {"fwtest1": "hello"},
                                   "_files_out": {"fw2": "hello.gz"}})
    fw3 = fireworks.Firework([fireworks.ScriptTask.from_str('cat fwtest.2')], fw_id=3,
                             parents=[fw2],
                             spec={"_files_in": {"fw2": "fwtest.2"}})
    wf = fireworks.Workflow(fireworks=[fw1, fw2, fw3],
                            links_dict={fw1: [fw2], fw2: [fw3]})
    return wf

  def example_all(self):
    """进入对应的py文件看例子详细的写法
    """
    # 打印任务
    from fireworks.examples.custom_firetasks.hello_world.hello_world_task import HelloTask
    from fireworks.examples.custom_firetasks.hello_world import hello_world_run
    # ScriptTask 脚本任务, echo "howdy, your job
    from fireworks.examples.tutorial_examples import introduction
    # workflows 任务, Ingrid is the CEO
    from fireworks.examples.tutorial_examples import workflows
    # 合并任务 TaskA, TaskB,TaskC
    from fireworks.examples.custom_firetasks.merge_task import merge_task
    # 动态任务1 PrintJobTask
    from fw_tutorials.dynamic_wf.printjob_task import PrintJobTask
    from fireworks.examples.tutorial_examples import dynamic_wf1
    # addtion 任务
    from fw_tutorials.dynamic_wf.addmod_task import AddModifyTask
    from fireworks.examples.tutorial_examples import dynamic_wf2
    # 动态任务2 FibonacciAdderTask
    from fw_tutorials.dynamic_wf.fibadd_task import FibonacciAdderTask
    from fireworks.examples.tutorial_examples import dynamic_wf2
    # python_examples
    from fw_tutorials.python import python_examples
    pass

  def example_Handling_Duplicates_Automatically(self):
    fw = fireworks.Firework([fireworks.ScriptTask.from_str('echo "hello"')],
                            spec={"_dupefinder": fireworks.user_objects.dupefinders.dupefinder_exact.DupeFinderExact()})
    pass

  def example_background_task(self):
    firetask1 = fireworks.ScriptTask.from_str(
        'echo "starting"; sleep 30; echo "ending"')
    bg_task1 = fireworks.features.background_task.BackgroundTask(
        fireworks.ScriptTask.from_str('echo "hello from BACKGROUND thread #1"'), sleep_time=10)
    bg_task2 = fireworks.features.background_task.BackgroundTask(fireworks.ScriptTask.from_str(
        'echo "hello from BACKGROUND thread #2"'), num_launches=0, sleep_time=5, run_on_finish=True)

    # create the Firework consisting of a custom "Fibonacci" task
    fw = fireworks.Firework(
        firetask1, spec={'_background_tasks': [bg_task1, bg_task2]})

    lpad = self.get_launchpad()
    lpad.add_wf(wf=fw)

    self.run_rocket_launcher(launchpad=lpad,
                             is_rapidfire=True,)
    return None

  def example_templates(self):
    """FireWorks查找模板的默认位置是在FireWorks安装的user_objects/firetasks/templates目录中。实际上, 本教程中使用的simple_template.txt和advanced_template.txt文件就存储在这里(这就是为什么修改教程文件对结果没有影响)。您放入此目录(或其子目录)中的任何模板都将被FireWorks读取；只需将模板的相对路径作为template_file参数。

    - 模板文件存储的位置: /Users/wangjinlong/opt/anaconda3/envs/py312/lib/python3.12/site-packages/fireworks/user_objects/firetasks/templates
    """

    firetask1 = fireworks.TemplateWriterTask({'context': {'opt1': 5.0, 'opt2': 'fast method'},
                                              'template_file': 'simple_template.txt',
                                              'output_file': 'inputs.txt'})
    firetask2 = fireworks.ScriptTask.from_str('wc -w < inputs.txt > words.txt')
    firetask3 = fireworks.FileTransferTask({'files': [{'src': 'words.txt', 'dest': '~/tmp/words.txt'}],
                                            'mode': 'copy'})
    fw = fireworks.Firework(tasks=[firetask1, firetask2, firetask3])

    '''# store workflow and launch it locally, single shot
    launchpad = self.get_launchpad(wf=fw)
    # workflow 里面只有一个 firework, is_launch_rocket 就可以了, 尽管这个 firework 里面有多个 firetask
    self.run_rocket_launcher(launchpad=launchpad,
                             is_rapidfire=True)'''
    return fw

  def example_fileIO(self,
                     filename='abc.txt',
                     dest='/Users/wangjinlong/job/soft_learn/py_package_learn/jobflow_learn',
                     ):
    ftask1 = fireworks.FileWriteTask({'files_to_write': [{'filename': filename,
                                                          'contents': 'abc de\n eee', }],
                                      'dest': dest, })
    ftask2 = fireworks.FileDeleteTask({'files_to_delete': [filename],
                                      'dest': dest})
    # spec 不需要, FileWriteTask 中就没有用到 fw_spec 参数
    fw1 = fireworks.Firework(tasks=ftask1, spec=None)
    fw2 = fireworks.Firework(tasks=ftask2, spec=None)
    wf = fireworks.Workflow(fireworks=[fw1, fw2], links_dict={'fw1': ['fw2']})
    return wf

  def add_tracker(self):
    """您可以在Firework执行期间跟踪文件的最后几行。例如，您可以监视输出文件以确保运行按预期进行。设置一个或多个这样的跟踪器很简单。
    # 下面的代码示例用两个跟踪器创建了上面的Firework：
    """
    # create the Firework consisting of multiple tasks
    firetask1 = fireworks.TemplateWriterTask(
        {'context': {'opt1': 5.0, 'opt2': 'fast method'}, 'template_file': 'simple_template.txt', 'output_file': 'inputs.txt'})
    firetask2 = fireworks.ScriptTask.from_str('wc -w < inputs.txt > words.txt')
    # define the trackers
    tracker1 = fireworks.Tracker('words.txt', nlines=25)
    tracker2 = fireworks.Tracker('inputs.txt', nlines=25)
    fw = fireworks.Firework(tasks=[firetask1, firetask2],
                            spec={"_trackers": [tracker1, tracker2]})

    fw.to_file('fw_tracker.json')
    # 您可以使用以下命令查看所有FireWorks（在执行期间或之后）的跟踪文件：
    # lpad track_fws
    lpad = self.get_launchpad()
    lpad.add_wf(wf=fw)

    self.run_rocket_launcher(launchpad=lpad,
                             is_rapidfire=True)
    pass

  def get_qadapter(self):
    qadapter = fireworks.user_objects.queue_adapters.common_adapter.CommonAdapter(
        q_type='SLURM', q_name='hfacnormal01',
        template_file='/Users/wangjinlong/job/soft_learn/py_package_learn/fireworks_learn/fw_config1/SLURM_template_custom.sh',
    )
    return qadapter

  def mytest(self, input_array=[1, 2, 3],
             launch_dir='/Users/wangjinlong/job/soft_learn/py_package_learn/jobflow_learn/test',
             name_fw='mytest',
             strm_lvl='WARNING',
             name_fworker='fworker1',
             fworker=fireworks.FWorker(name='fworker1')):
    fw = fireworks.Firework(
        tasks=fw_tutorials.dynamic_wf.addmod_task.AddModifyTask(),
        spec={"input_array": input_array,
              '_launch_dir': launch_dir,
              '_fworker': name_fworker,
              # '_dupefinder': fireworks.user_objects.dupefinders.dupefinder_exact.DupeFinderExact(),
              },
        name=name_fw,)
    wf = fireworks.Workflow(fireworks=[fw])

    lpad = self.get_launchpad(is_local_DB=True,
                              is_uri_DB=False,
                              strm_lvl=strm_lvl)
    lpad.add_wf(wf=wf)
    # lauchpad.reset('', require_password=False)
    self.run_rocket_launcher(launchpad=lpad,
                             is_rapidfire=True,
                             fworker=fworker)
    return None
