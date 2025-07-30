import jobflow
import jobflow.core
import jobflow.core.flow
import jobflow.core.job
import jobflow.core.job
import jobflow.core.maker
import jobflow.core.store
import jobflow.managers.fireworks
import jobflow.managers.local
import dataclasses
import os
import jobflow.settings
from py_package_learn.maggma_learn import maggmaLearn


class JobflowLearn():
  def __init__(self) -> None:
    """* 官网: https://materialsproject.github.io/jobflow/index.html
    * Jobflow是一个免费的开源库，用于编写和执行工作流。复杂的工作流可以使用简单的python函数定义，并使用jobflow-remote或FireWorks工作流管理器在本地或任意计算资源上执行。 通过magma包集成多个数据库（MongoDB、S3、GridFS等）。
    * 工作流中的工作流由两个主要组件组成：
    - 作业是一个原子计算作业。基本上任何python函数都可以是Job，只要它的输入和返回值可以序列化为json。作业返回的任何内容都被视为“输出”，并存储在作业流数据库中。
    - Flow是Job对象或其他Flow对象的集合。作业之间的连通性由作业输入自动确定。作业的执行顺序根据它们的连通性自动确定。
    ---
    * 我的认识是: jobflow 和 fireworks 都是建立并执行工作流, 但 fireworks 学习起来很费劲很难理解, 用了很多命令行操作, 直接学习 jobflow 并应用 jobflow 就好了
    """
    # env
    self.env_sets()
    # 或者直接在 .zhsrc 中添加:
    # export JOBFLOW_CONFIG_FILE="/Users/wangjinlong/job/soft_learn/py_package_learn/jobflow_learn/jobflow.yaml"
    jobflow.SETTINGS.JOB_STORE = self.get_jobstore()
    # ---
    pass

  def install(self):
    string = """conda install jobflow
    conda install prettytable argcomplete # 可能还需要安装这个
    """
    print(string)
    return None

  def get_config_file_method2_nogood(self,
                                     fname='/Users/wangjinlong/job/soft_learn/py_package_learn/jobflow_learn/jobflow.yaml'):
    """ https://materialsproject.github.io/jobflow/stores.html
    Configuring a MongoStore
    in your ~/.bashrc file, add the following line:
    export JOBFLOW_CONFIG_FILE="/path/to/my/jobflow.yaml"
    """
    os.environ['JOBFLOW_CONFIG_FILE'] = fname
    # 如果您使用的是URI（这在MongoDB Atlas中很常见), job_store.yaml 内容如下
    string = '''
JOB_STORE:
  docs_store:
    uri: mongodb+srv://396292346_wjl:1011320sr@cluster0.tgum0.mongodb.net
    database: myMongoDB
    collection_name: myMongoDB_Collection
    ssh_tunnel:
    mongoclient_kwargs: {}
    default_sort:
    key:
    type: MongoURIStore
  additional_stores:
    data:
      uri: mongodb+srv://396292346_wjl:1011320sr@cluster0.tgum0.mongodb.net
      collection_name: GridFSURIStore_Collection
      database: myMongoDB
      compression: false
      ensure_metadata: false
      searchable_fields: []
      mongoclient_kwargs: {}
      key:
      type: GridFSURIStore
    '''
    if os.path.getsize(filename=fname) > 0:
      pass
    else:
      with open(file=fname, mode='w') as f:
        f.write(string)
    return None

  def get_config_file(self, fname='/Users/wangjinlong/job/soft_learn/py_package_learn/jobflow_learn/jobflow.yaml'):
    """获得 jobflow.yaml 文件
    """
    from py_package_learn.maggma_learn import maggmaLearn
    store1 = maggmaLearn.MaggmaLearn().get_MongoURIStore()
    store2 = maggmaLearn.MaggmaLearn().get_GridFSURIStore()
    d1 = store1.as_dict()
    d2 = store2.as_dict()
    d1 = {k: v for k, v in d1.items() if '@' not in k}
    d2 = {k: v for k, v in d2.items() if '@' not in k}
    d1.update({'type': 'MongoURIStore'})
    d2.update({'type': 'GridFSURIStore'})
    d = {'JOB_STORE': {'docs_store': d1, 'additional_stores': {'data': d2}}}
    from py_package_learn.monty_learn import montyLearn
    ml = montyLearn.MontyLearn()
    ml.dumpfn(data=d, fname_json=fname)
    return None

  def env_sets(self, config_file='/Users/wangjinlong/job/soft_learn/py_package_learn/jobflow_learn/jobflow.yaml'):
    if os.path.exists(config_file) and os.path.getsize(filename=config_file) > 0:
      pass
    else:
      self.get_config_file(fname=config_file)
    # 使用环境变量
    os.environ['JOBFLOW_CONFIG_FILE'] = config_file
    return None

  def get_jobstore(self):
    jobstore: jobflow.core.store.JobStore = self.get_jobstore_method1()
    return jobstore

  def get_jobstore_method1(self,
                           config_file='/Users/wangjinlong/job/soft_learn/py_package_learn/jobflow_learn/jobflow.yaml'):
    # 设置环境变量后 CONFIG_FILE 可以不设置
    jfs = jobflow.settings.JobflowSettings(
        CONFIG_FILE=config_file,)
    jobstore: jobflow.core.store.JobStore = jfs.JOB_STORE
    jobstore.connect()
    return jobstore

  def get_jobstore_method2(self,):
    """
    from maggma.stores import MemoryStore
    docs_store = MemoryStore()
    from jobflow import JobStore
    store = JobStore(docs_store)
    """
    ml = maggmaLearn.MaggmaLearn()
    docs_store = ml.get_MongoURIStore()
    additional_store = ml.get_GridFSURIStore()
    jobstore = jobflow.JobStore(docs_store=docs_store,
                                additional_stores={'data': additional_store})
    jobstore.connect()
    return jobstore

  def get_jobstore_from_json(self,
                             fname='/Users/wangjinlong/job/soft_learn/py_package_learn/jobflow_learn/jobstore.json'):
    if os.path.exists(fname):
      pass
    else:
      # 获得 jobstore.json 文件
      jobstore = self.get_jobstore_method1()
      from py_package_learn.json_learn import jsonLearn
      jsonLearn.JsonLearn().dump(data_dict=jobstore.as_dict(),
                                 fname=fname)

    jobstore = jobflow.JobStore.from_file(db_file=fname)
    jobstore.connect()
    return jobstore

  def get_jobstore_MemoryStore(slef):
    # JobStore是Maggma包提供的Store接口的实现。Maggma提供了许多常用数据库的实现，包括：
    # MongoDB (MongoStore)
    # GridFS (GridFSStore)
    # AWS S3 (S3Store)
    # 在本例中，我们将对所有文档使用单一存储类型。特别地，我们将使用一种称为MemoryStore的特殊类型的存储。这意味着任何输出只存储在内存中，而不是存储在外部数据库中。对于生产工作流程，我们建议使用上面列出的永久存储之一。

    # 首先，我们需要创建内存存储，它将作为所有输出的存储。
    ml = maggmaLearn.MaggmaLearn()
    docs_store = ml.get_MemoryStore()
    # ml.get_JSONStore()
    # 接下来，我们可以用内存存储初始化JobStore。
    jobstore = jobflow.JobStore(docs_store)
    # 如果没有设置自定义存储，这种类型的JobStore（对所有输出使用MemoryStore）是jobflow使用的默认存储。
    return jobstore

  def get_job_tutorial(self,):
    """https://materialsproject.github.io/jobflow/tutorials/3-defining-jobs.html

    Returns:
        _type_: _description_
    """
    # Creating job objects
    # 创建作业最简单的方法是使用@job装饰器。作业装饰器可以应用于任何函数，甚至是那些带有可选参数的函数。
    @jobflow.job
    def add(a, b):
      return a + b

    # 对add函数的任何调用都将返回一个Job对象。
    add_first = add(1, 5)

    # 作业具有可以使用output属性访问的输出。由于作业尚未执行，因此当前输出是对未来输出的引用。
    add_first.output
    # Each job is assigned a unique identifier (UUID).
    add_first.uuid
    # job 还有索引
    add_first.index
    # job 的输出可以作为另一个job的输入
    # The output of a job can be used as the input to another job.
    add_second = add(add_first.output, 3)

    # 输出本身不必是参数，它可以包含在列表或字典中。
    @jobflow.job
    def sum_numbers(numbers):
      return sum(numbers)

    sum_job = sum_numbers([add_first.output, 10])
    return add

  def get_flow_tutorial(self):
    # 要将这两个Job对象组合成一个工作流，我们可以利用Jobflow中的Flow构造函数。
    job = self.get_job_tutorial()
    job1 = job(1, 2)
    job2 = job(job1.output, 3)
    # 因为job2依赖于job1的输出，所以它只会在job1成功完成时运行。Jobflow将自动确定作业的连通性，并相应地运行它们。在这里，我们还为流提供了一个可选的名称，这对于跟踪目的可能很有用。
    flow = jobflow.Flow([job1, job2], name='my_jobflow_example')

    # 在作业和流运行之前将元数据附加到它们通常是有用的，特别是用于以后的查询目的。这可以通过update_metadata函数完成。这个名字也可以随时更新。
    job1.name = "test"
    job1.update_metadata(update={"tags": ["test"]})
    return flow

  def get_graph(self,
                flow: jobflow.Flow,
                figsize=(3, 3)):
    import matplotlib.pyplot as plt
    graph: plt.Figure = flow.draw_graph(figsize=figsize)
    graph.show()
    return graph

  def run_local(self,
                job_flow: jobflow.Flow | jobflow.Job,
                store=None,
                root_dir='xx',
                create_folders=True,):
    if store is None:
      store = jobflow.settings.JobflowSettings().JOB_STORE
    responses = jobflow.managers.local.run_locally(job_flow,
                                                   store=store,
                                                   create_folders=create_folders,
                                                   root_dir=root_dir)
    # for uuid, response in responses.items():
    #   print(f"{uuid} -> {response}")
    return responses

  def check_result(self,
                   flow: jobflow.Flow,
                   store: jobflow.JobStore,
                   responses):
    # 我们可以使用以下命令检查特定作业的输出：
    responses[flow.jobs[0].uuid][1].output

    # 通常，使用JobStore检查作业的输出更容易。get_output函数。这将查询数据库（在本例中是MemoryStore）并返回作业的输出。如果使用多个存储，将自动从适当的存储查询相关输出。
    store.get_output(flow.jobs[0].uuid)
    return None

  def example_set_SettingMetadata(self, job: jobflow.core.job.Job):
    # 在作业和流运行之前将元数据附加到它们通常是有用的，特别是用于以后的查询目的。这可以通过update_metadata函数完成。这个名字也可以随时更新。
    job.name = "test"
    job.update_metadata({"tags": ["test"]})
    pass

  def get_flow_instroduction(self):
    # 让我们创建一个修饰函数，计算加载网站所需的时间。
    @jobflow.job
    def time_website(website: str):
      import urllib.request
      from time import perf_counter

      with urllib.request.urlopen(website) as f:
        start_time = perf_counter()
        f.read()
        end_time = perf_counter()

      return end_time - start_time

    @jobflow.job
    def sum_numbers(numbers):
      return sum(numbers)

    # 创建流
    time_github = time_website("https://www.tlu.edu.cn/")
    time_google = time_website("https://www.baidu.com")
    time_nyt = time_website("https://www.xxu.edu.cn/")

    sum_times = sum_numbers(
        [time_github.output, time_google.output, time_nyt.output])

    flow = jobflow.Flow(
        jobs=[time_github, time_google, time_nyt, sum_times],
        # output=sum_times.output
        output={
            "times": [time_github.output, time_google.output, time_nyt.output],
            "sum": sum_times.output
        }
    )

    # flow.draw_graph(figsize=(3,3)).show()
    new_job = sum_numbers([flow.output["sum"], 10])

    '''
    # 在作业和流运行之前将元数据附加到它们通常是有用的，特别是用于以后的查询目的。这可以通过update_metadata函数完成。名字也可以随时更新。
    time_google.update_metadata({"tags": ["test_测试"]})
    time_google.name = '谷歌'
    '''
    return flow

  def example_quick_tutorial(self):
    """使用@job装饰器可以很容易地将Python函数转换为Job对象。在下面的示例中，我们定义了一个将两个数字相加的作业。

    Returns:
        _type_: _description_
    """
    flow = self.get_flow_tutorial()
    # 运行流程 Run the Flow
    # Jobflow支持在本地或远程集群上运行flow。下面我们使用run_local函数在本地运行流。
    # 可以使用FireWorks包在远程集群上运行流，这在使用FireWorks运行Jobflow教程中有介绍。
    responses = jobflow.managers.local.run_locally(flow)
    # 我们可以使用以下命令检查特定作业的输出：
    responses[flow.jobs[0].uuid][1].output
    return responses

  def example_introduction(self):
    """https://materialsproject.github.io/jobflow/tutorials/2-introduction.html

    Returns:
        _type_: _description_
    """

    flow = self.get_flow_instroduction()
    store = self.get_jobstore_MemoryStore()

    # Running the Flow
    # Jobflow支持在本地或远程集群上运行flow。下面我们使用run_local函数和自定义存储在本地运行Flow。
    # job_index和Response（）对象将在后面的教程中介绍。要知道的主要事情是，Response包含Job的输出和用于控制流执行的任何其他命令。
    Response = self.run_local(job_flow=flow,
                              store=store)
    # self.check_result()
    return store, Response

  def get_flow_dynamic_Response_option_replace(self):
    """https://materialsproject.github.io/jobflow/tutorials/5-dynamic-flows.html
    * 在Jobflow中创建动态作业的主要机制是通过Response对象。我们将在下面演示一个玩具示例，其中我们：

    Returns:
        _type_: _description_
    """

    @jobflow.job
    def make_list(a):
      return [a] * 5  # random.randint(2, 5)

    @jobflow.job
    def add(a, b):
      return a + b

    @jobflow.job
    def add_distributed(list_a):
      jobs = [add(val, 1) for val in list_a]
      flow = jobflow.Flow(jobs)
      return jobflow.Response(replace=flow)

    job1 = make_list(2)
    job2 = add_distributed(job1.output)
    flow = jobflow.Flow([job1, job2])

    '''run 
    responses = jobflow.managers.local.run_locally(flow)
    # 如上所示，运行了几个作业—当然比我们开始时的两个作业要多。第一个作业生成2的随机列表。流中的第二个作业是针对列表中的每个条目启动作业。它为每个条目替换为一个作业，因此它没有直接输出。然后运行每个新生成的作业。
    for uuid, response in responses.items():
      print(f"{uuid} -> {response}")'''
    return flow

  def get_flow_dynamic_Response_option_addtion(self):
    @jobflow.job
    def add(a, b):  # noqa: F811
      return a + b

    @jobflow.job
    def add_with_logic(a, b):
      if a < 10:
        return jobflow.Response(addition=add(a, b))
        # 响应（绕道）选项的行为类似于响应（添加）。不同之处在于Response（addition）将向当前流添加作业（或流），而Response（ detour ）将不再运行当前流并切换到并行作业或流。
        # return jobflow.Response(detour=add(a, b))
      return None

    job1 = add(1, 2)
    job2 = add_with_logic(job1.output, 2)
    flow = jobflow.Flow([job1, job2])
    '''
    responses = jobflow.managers.local.run_locally(flow)
    # 正如您在上面看到的，添加作业正确地运行了两次。现在让我们确认，如果第一个作业的输出大于10，则只运行一次添加作业。
    for uuid, response in responses.items():
      print(f"{uuid} -> {response}")
      pass'''
    return flow

  def get_flow_dynamic_Response_option_addtion_fabonacci(self):
    @jobflow.job
    def fibonacci(smaller, larger, stop_point=100):
      """A dynamic workflow that calculates the Fibonacci sequence.

      If the number is larger than stop_point, the job will stop the workflow
      execution, otherwise, a new job will be submitted to calculate the next number.
      """
      total = smaller + larger

      if total > stop_point:
        return total

      new_job = fibonacci(larger, total, stop_point=stop_point)
      return jobflow.Response(output=total, addition=new_job)

    fibonacci_job = fibonacci(1, 1, stop_point=100)

    # run the job; responses will contain the output from all jobs
    # responses = jobflow.run_locally(fibonacci_job)
    return fibonacci_job

  def get_flow_creating_dynamic_flows_Response_option_detour(self):
    # 响应（绕道）选项的行为类似于响应（添加）。不同之处在于Response（addition）将向当前流添加作业（或流），而Response（detour）将不再运行当前流并切换到并行作业或流。
    @jobflow.job
    def add(a, b):
      return a + b

    @jobflow.job
    def add_with_logic(a, b):
      if a < 10:
        return jobflow.Response(detour=add(a, b))
      return None

    job1 = add(1, 2)
    job2 = add_with_logic(job1.output, 2)
    flow = jobflow.Flow([job1, job2])
    return flow

  def get_flow_from_maker_example(self):
    """ Maker是一个类，它可以方便地在工作流中动态更新参数。 也是用来建立job的, 最好都通过maker 来建立 job
    继承一个 maker  类, 通过类用于建立 job
    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    @dataclasses.dataclass
    class AddMaker(jobflow.Maker):
      """让我们从定义一个简单的Maker开始，它可以将两个数字相加或相乘，我们将这样做两次来制作流。注意，所有从Maker基类继承的类都必须有一个名称变量和一个make方法。
      """
      name: str = "Add Maker"
      operation: str = "add"

      @jobflow.job
      def make(self, a, b):
        if self.operation == "add":
          return a + b
        if self.operation == "mult":
          return a * b
        raise ValueError(f"Unknown operation: {self.operation}")

    @dataclasses.dataclass
    class SubtractMaker(jobflow.Maker):
      name: str = "Subtract Maker"

      @jobflow.job
      def make(self, a, b):
        return b - a

    job1 = AddMaker().make(a=2, b=3)
    job2 = SubtractMaker().make(a=job1.output, b=4)
    flow = jobflow.Flow([job1, job2])
    # 现在，这里没有什么特别的事情发生。但是，如果您有一个包含许多步骤的复杂得多的工作流，并且您希望更改AddMaker关键字参数，但仅针对流程中的几个单独的作业，该怎么办？这就是制造者派上用场的地方。让我们看看它是如何工作的。
    # 在本例中，我们使用name_filter和update_maker_kwargs函数更新了流中作业的关键字参数（“kwargs”），update_maker_kwargs函数起作用是因为流中的类本身就是Maker对象。
    # name_filter="Add Maker":只有 flow 中的 AddMaker 才会被修改参数 而不是 SubtractMaker
    flow.update_maker_kwargs({"operation": "mult"},  # 修改 类的参数
                             name_filter="Add Maker")  # 通过这个方式更改流作业中的参数
    # responses = jobflow.managers.local.run_locally(flow)
    # 当然，我们可以简单地执行job1 = AddMaker（operation=“mult”）。首先使用make(a=2, b=3)，但在实践中，如果您要从某些外部Python包导入此流，则可能无法直接修改AddMaker类。在这种情况下，Maker类提供了一种方便的方法来更新流中作业的参数，而不必重新定义流本身。
    return flow

  def writing_generalized_Makers(self):
    """https://materialsproject.github.io/jobflow/tutorials/7-generalized-makers.html
    """
    # 分离依赖dft代码的部分和独立的部分可能是一件非常令人头痛的事情。
    # 因此，我们建议采用以下方法。
    # 定义一个基本的Maker对象，该对象在make函数中定义与dft代码无关的Flow。代码
    # 通用Maker调用的特定作业将为每个特定于代码的操作接受Callable参数。
    # 特定于代码的操作将被定义为基本Maker中的抽象函数。
    # 每个特定于代码的操作都应该在子Maker中实现，这将是基Maker的具体实现。
    '''以下是 BaseMaker 的内容'''
    @jobflow.job
    def job1(func, arg1):
      print("DO CODE INDEPENDENT STUFF")
      func(arg1)
    # jobflow.core.maker.Maker()

    class BaseMaker(jobflow.Maker):
      def code_specific_func(self, arg1):
        raise NotImplementedError

      def make(self):
        return jobflow.Flow(jobs=[job1(self.code_specific_func, "ARG1")])

    '''以下是 每个特定于代码的操作都应该在 BaseMaker 的 子Maker 中实现， '''
    class Code1Maker(BaseMaker):
      def code_specific_func(self, arg1):
        print("DO STUFF specific to CODE 1")

    class Code2Maker(BaseMaker):
      def code_specific_func(self, arg1):
        print("DO STUFF specific to CODE 2")
    # -----
    flow = Code1Maker().make()
    responses = jobflow.managers.local.run_locally(flow)
    flow = Code2Maker().make()
    responses = jobflow.managers.local.run_locally(flow)

  def Running_Jobflow_with_FireWorks(self,
                                     job: jobflow.Flow | jobflow.Job,
                                     flow: jobflow.Flow):
    """https://materialsproject.github.io/jobflow/tutorials/8-fireworks.html
    - 我的认识是: jobflow 和 fireworks 都是建立并执行工作流, 但 fireworks 学习起来很费劲很难理解, 用了很多命令行操作, 直接学习 jobflow 并应用 jobflow 就好了
    - https://materialsproject.github.io/jobflow/install_fireworks.html
    os.envrion[FW_CONFIG_FILE]="/Users/wangjinlong/job/soft_learn/py_package_learn/jobflow_learn/fw_config1/FW_config1.yaml"
    Args:
        job (_type_): _description_
        flow (_type_): _description_
    """
    from py_package_learn.fireworks_learn import fireworksLearn
    import fireworks
    # To convert a Job to a firework and add it to your launch pad:
    fw = jobflow.managers.fireworks.job_to_firework(job)
    lpad = fireworks.LaunchPad.auto_load()
    lpad.add_wf(fw)

    # To convert a Flow to a workflow and add it to your launch pad:
    wf = jobflow.managers.fireworks.flow_to_workflow(flow)
    lpad = fireworks.LaunchPad.auto_load()
    lpad.add_wf(wf)
    # 将工作流添加到启动台上后，您可以在所需的机器上运行qlaunch rapidfire——nlaunching <N>（其中<N>是要提交的作业数），在命令行中将工作流提交给作业调度器。
    '''
    实现此目标的最简单方法是为流中的每个作业定义唯一的fworker并设置job.config.manager_config["_fworker"]为您希望用于该作业的fworker的名称。

    /path/to/fw_config1
    ├── FW_config1.yaml
    ├── my_fworker1.yaml
    ├── my_launchpad1.yaml
    └── my_qadapter1.yaml
    /path/to/fw_config2
    ├── FW_config2.yaml
    ├── my_fworker2.yaml
    ├── my_launchpad2.yaml
    └── my_qadapter2.yaml
    # .bashrc 中
    export FW_CONFIG1=/path/to/fw_config1
    export FW_CONFIG2=/path/to/fw_config2
    1. my_fworker1.yaml和 my_fworker2.yaml文件应该具有不同的名称属性，例如fworker1和fworker2，这样它们就可以相互区分。
    2. my_qadapter1.yaml 文件应该有针对计划运行的两种作业类型定制的不同作业提交设置（例如，不同的节点或运行时间属性）。
    
    '''
    job.update_config({"manager_config": {"_fworker": "fworker1"}})
    # 使用上面或者下面的方式
    flow.update_config(config={"manager_config": {"_fworker": "fworker1"}},  # fworker1 即是my_fworker1.yaml中的name 属性值
                       name_filter="job1")
    flow.update_config(config={"manager_config": {"_fworker": "fworker2"}},
                       name_filter="job2")
    # 启动任务
    from py_package_learn.fireworks_learn import fireworksLearn
    fireworksLearn.FireWorksLearn().run_rocket_launcher(launchpad=lpad,
                                                        is_rapidfire=True)
    return lpad

  def get_workflow_from_jobflow_run_with_fireworks_1(self, jf: jobflow.core.flow.Flow,
                                                     job_config={"manager_config": {"_fworker": "fworker1"}}):
    store = self.get_jobstore()
    jf.update_config(config=job_config,)
    # Converting a Flow to a Workflow
    wf = jobflow.managers.fireworks.flow_to_workflow(flow=jf, store=store, )
    return wf

  def add_to_lauchupad_run_with_fireworks_2(self, wf):
    # 加入启动台: 方法1
    # lpad = fireworks.LaunchPad.auto_load()
    # lpad.add_wf(wf)
    # 加入启动台: 方法2
    from py_package_learn.fireworks_learn import fireworksLearn
    lpad = fireworksLearn.FireWorksLearn().get_launchpad(is_local_DB=True,
                                                         is_uri_DB=False)
    lpad.add_wf(wf=wf)
    return lpad

  def run_rocket_launcher_run_with_fireworks_3(self, lpad):
    # 发射
    from py_package_learn.fireworks_learn import fireworksLearn
    fireworksLearn.FireWorksLearn().run_rocket_launcher(
        launchpad=lpad, is_rapidfire=True)
    pass

  def my_example_run_local(self, root_dir='/Users/wangjinlong/job/soft_learn/py_package_learn/atomate2_learn/'):
    store = self.get_jobstore()
    flow = self.get_flow_from_maker_example()
    response = self.run_local(job_flow=flow, store=store, create_folders=True,
                              root_dir=root_dir)
    return response, store

  def my_run_with_fireworks(self):
    flow = self.get_flow_from_maker_example()
    wf = self.get_wf_from_jobflow_run_with_fireworks_1(jf=flow,)
    lpad = self.add_to_lauchupad_run_with_fireworks_2(wf=wf)
    self.run_rocket_launcher_run_with_fireworks_3(lpad=lpad,)
    pass
