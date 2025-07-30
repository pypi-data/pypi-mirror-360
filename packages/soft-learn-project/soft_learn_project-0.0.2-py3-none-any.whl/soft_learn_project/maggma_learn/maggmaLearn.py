import maggma
import maggma.stores
import maggma.stores.gridfs


class MaggmaLearn():
  def __init__(self):
    """ https://materialsproject.github.io/maggma/
    Maggma 是一个框架，用于构建科学数据处理管道，从各种格式存储的数据——数据库、Azure blob、磁盘上的文件等，一直到REST API。本自述文件的其余部分包含了对岩浆功能的简要、高级概述。更多信息，请参考文档。
    magma 的核心类: Store 和 Builder——为模块化数据管道提供了构建块。
    store: 保存数据, builder: 提取 store 中的数据转存到另一个 store
    Store接口的好处是您只需要编写一次Builder。随着数据的移动或发展，您只需将其指向不同的Store，而无需更改处理代码。

    * 有用的 store : MemoryStore, JsonStore, MongoURIStore, FileStore
    ConcatStore: 将多个Store连接在一起，使它们看起来像一个Store
    JointStore: 将几个MongoDB集合连接在一起，合并具有相同键的文档，使它们看起来像一个集合

    """
    pass

  def install(self):
    """pip install --upgrade maggma
    conda install maggma
    """
    pass

  def example(self):
    """下面的示例演示了使用update将4个文档（python字典）插入到一个 Store中，然后使用count、query和distinct访问数据。
    """
    store = self.get_MemoryStore()
    store.update(docs=self.get_documents(), key='name')
    # 查询
    list(store.query())
    store.count()
    store.distinct(field='color')
    return store

  def get_documents(self):
    """除了作为字典列表结构外，每个文档（字典）必须有一个唯一标识它的键。默认情况下，这个键是task_id，但在实例化Store时，可以使用key参数将其设置为任何您喜欢的值。在上面的示例中，name可以用作键，因为所有文档都有它，并且值都是唯一的。

    Returns:
        _type_: _description_
    """
    # 将数据结构为dict对象列表，其中每个dict代表一条记录（称为“文档”）。下面，我们创建了一些数据来表示关于忍者神龟的信息。
    turtles = [{"name": "Leonardo",
                "color": "blue",
                "tool": "sword",
                "occupation": "ninja"
                },
               {"name": "Donatello",
                "color": "purple",
                "tool": "staff",
                "occupation": "ninja"
                },
               {"name": "Michelangelo",
                "color": "orange",
                "tool": "nunchuks",
                "occupation": "ninja"
                },
               {"name": "Raphael",
               "color": "red",
                "tool": "sai",
                "occupation": "ninja"
                },
               {"name": "Splinter",
               "occupation": "sensei"
                }
               ]
    return turtles

  def get_MemoryStore(self, key='name'):
    # 除了作为字典列表结构外，每个文档（字典）必须有一个唯一标识它的键。默认情况下，这个键是task_id，但在实例化Store时，可以使用key参数将其设置为任何您喜欢的值。
    # MemoryStore只是将数据加载到内存中，实例化时不需要参数。
    store = maggma.stores.MemoryStore()
    # Before you can interact with a store, you have to connect(). This is as simple as
    store.connect()
    # key=xx 字段名（用于确定文档的唯一性）可以是多个字段的列表、单个字段，如果要使用Store的关键字段，则可以是None
    # To add data to the store, use update().
    # store.update(docs=self.get_documents(), key=key)
    """
    with store as s: # 这将自动处理connect()，同时确保在存储任务完成后正确关闭连接。
      s.update(self.get_documents(), key='name')
    """

    return store

  def queries(self):
    """maggma查询语法遵循MongoDB查询语法。在本教程中，我们将介绍最常见的查询操作的语法。您可以参考MongoDB或pymongo （MongoDB的python接口）文档以获取更高级的用例示例。

    $in is an example of a "query operator". Others include:
    - store.query({"color": {"$in": ["red", "blue"]}})
    $nin: a value is NOT in a list (the inverse of the above example)
    $gt, $gte: greater than, greater than or equal to a value
    $lt, $lte: less than, less than or equal to a value
    $ne: not equal to a value
    $not: inverts the effect of a query expression, returning results that do NOT match.
    """
    store = self.get_MemoryStore()
    # Store.query() is the primary method you will use to search your data.
    # Turn into a list
    results = [d for d in store.query()]
    # Use in a for loop
    for doc in store.query():
      print(doc)
    # 查询也是字典。字典中的每个键对应于您想要查询的文档中的一个字段（例如名称、颜色等），值是您想要匹配的键的值。例如，选择职业为ninja的所有文档的查询如下所示
    store.count()
    store.query_one({})
    store.distinct('color')
    # 返回“职业”为“忍者”的所有记录
    with store as store:
      results = list(store.query({"occupation": "ninja"}))
      len(results)
    # 匹配列表中的任何值：$in¶
    with store as store:
      results = list(store.query({"color": {"$in": ["red", "blue"]}}))
    len(results)
    # query_one：与上面相同，但将返回的结果限制为与查询匹配的第一个文档。对于理解返回数据的结构非常有用。
    # remove_docs: Removes documents from the underlying data source.
    store.remove_docs({'color': 'red'})
    # 对于嵌套字段的查询方法
    # 假设我们的文档有一个嵌套结构，例如，通过为姓和名提供单独的字段：
    turtles = [{"name":
                {"first": "Leonardo",
                 "last": "turtle"
                 },
                "color": "blue",
                "tool": "sword",
                "occupation": "ninja"
                },
               ...]
    # 可以通过放置句号查询嵌套字段。在层次结构中的每个级别之间。例如:
    with store as store:
      results = list(store.query({"name.first": "Leonardo"}))
    len(results)
    pass

  def get_MongoStore(self,
                     database='MongoStore_local_DB',
                     collection_name='flows',
                     host='localhost',
                     port=27017,):
    """目前连不上
    - 如果您使用的是自托管的mongodb数据库，您可能希望使用MongoStore而不是 mongoristore，后者的参数略有不同。
    - 自托管的 mongodb 数据库: 在自己电脑上装的 mongodb
    Returns:
        _type_: _description_
    """
    store = maggma.stores.MongoStore(database=database,
                                     collection_name=collection_name,
                                     host=host,
                                     port=port,)
    store.connect()
    return store

  def get_MongoURIStore(self,
                        uri="mongodb+srv://396292346_wjl:1011320sr@cluster0.tgum0.mongodb.net",
                        database='myMongoDB',
                        collection_name="myMongoDB_Collection",
                        key=None,  # "name",
                        ):
    # 在下面的示例中，我们创建了一个连接到MongoDB数据库的MongoStore。要创建这个存储，我们必须向maggma提供到数据库的连接细节，如主机名、集合名称和身份验证信息。注意，我们设置了key='name'，因为我们想使用那个名称作为唯一标识符。
    store = maggma.stores.MongoURIStore(uri=uri,
                                        database=database,
                                        collection_name=collection_name,
                                        key=key,
                                        )

    store.connect()
    return store

  def get_GridFSURIStore(self,
                         uri="mongodb+srv://396292346_wjl:1011320sr@cluster0.tgum0.mongodb.net",
                         database='myMongoDB',  # 'myMongoDB',
                         collection_name="GridFSURIStore_Collection",  # 'myMongoDB_Collection'
                         key=None,  # "name",
                         ):
    # magm
    store = maggma.stores.gridfs.GridFSURIStore(uri=uri,
                                                database=database,
                                                collection_name=collection_name,
                                                key=key)
    store.connect()
    return store

  def get_S3Store(self):
    """x
    """
    store = maggma.stores.S3Store()
    store.connect()
    return store

  def get_JSONStore(self,
                    paths='/Users/wangjinlong/job/soft_learn/py_package_learn/maggma_learn/JSONStore.json',
                    key='name'):
    store = maggma.stores.JSONStore(paths=paths,
                                    read_only=False,
                                    encoding='utf8',
                                    key=key)
    store.connect()
    # store.update(docs=self.get_documents(), key='name')
    return store

  def get_FileStore(self,
                    path='/Users/wangjinlong/my_server/my/myORR_B/adsorbate/O2_test',
                    file_filters=["*.in", "test-[abcd].txt"],
                    max_depth=None,
                    ):
    """ * 为了限制由Store索引的文件（这可以提高性能），可以使用可选的关键字参数max_depth和file_filters。你可以传递多个file_filters，也可以使用类似regex的fnmatch模式。例如，索引所有以“。”结尾的文件。或命名为“test-X.txt”，其中X是a和d之间的任意一个字母，使用
    * 打印每个名为“input”的文件的路径。
    - result = [d["path"] for d in store.query({"name": "INCAR"})]
    - print("可以查看文件的内容: store.query_one({'name':'INCAR'})['contents']")

    Args:
        path (str, optional): _description_. Defaults to '/Users/wangjinlong/my_server/my/myORR_B/adsorbate/O2_test'.
        file_filters (list, optional): _description_. Defaults to ["*.in","test-[abcd].txt"].

    Returns:
        _type_: _description_
    """
    store = maggma.stores.FileStore(path=path,
                                    json_name="FileStore.json",  # 会在 path 下 创建该文件
                                    read_only=False,  # “添加元数据”
                                    encoding='utf8',
                                    file_filters=file_filters,
                                    max_depth=max_depth,  # 要索引的深度,
                                    include_orphans=True,
                                    )

    store.connect()
    return store

  def operation_of_FileStore(self,):
    fs = self.get_FileStore()

    # 请注意，当使用下面方法时，您不能修改默认填充的任何键（例如name， parent, file_id），因为它们直接从磁盘上的文件派生。
    # 您可以使用update（）向FileStore记录添加键。例如，要向名为“input”的文件添加一些标记。在“使用:
    docs = [d for d in fs.query({"name": "input.in"})]
    for d in docs:
      d["tags"] = ["preliminary"]
      d['test'] = '测试'
      d['another'] = ['另一个测试']

    fs.update(docs)
    # 上述步骤将导致将以下内容添加到.json文件中。下次连接到Store时，将自动回读此元数据。
    # 添加元数据的一种更方便的方法是通过add_metadata方法。要使用它，只需传递一个查询来标识要更新的文档，以及一个要添加到文档中的字典。下面是上面的示例使用add_metadata的样子
    fs.add_metadata({"name": "input.in"}, {
                    "tags": ["preliminary"], 'test': ['我的测试']})  # 我测试了好像不行

    # 定义一个函数来根据文件或目录名自动创建元数据。例如，如果你用日期戳作为所有文件的前缀（例如，‘2022-05-07_experiment.csv’），你可以编写一个简单的字符串解析函数来从FileStore记录中的任何键中提取信息，并将该函数作为参数传递给add_metadata。
    # 例如，要从名为‘2022-05-07_experiment.csv’的文件中提取日期，并将其添加到‘date’字段中：
    # 这是我自己的
    def get_date_from_filename(d):
      """
      Args:
          d: An item returned from the `FileStore`
      """
      if '.' in d['name']:
        return {"date": d["name"].split(".")[0],
                "test_name": d["name"].split(".")[1]}
      else:
        return {}

    fs.add_metadata({}, auto_data=get_date_from_filename)

    # 为了与Store接口保持一致，当read_only=False时，FileStore提供remove_docs方法。此方法将删除磁盘上的文件，因为FileStore文档只是这些文件的表示。它有一个额外的保护参数confirm，该参数必须设置为非默认值True，以便该方法实际执行任何操作。
    fs.remove_docs({"name": "input.in2"}, confirm=True)
    return None

  def example_Writing_Builder(self):
    from maggma.core import Store
    from maggma.core import Builder
    from collections.abc import Iterable

    store = self.get_MemoryStore()
    docs = [{
        'name': 'test',
        "id": 1,
        "a": 3,
        "last_updated": "2019-11-3"
    }]
    store.update(docs=docs)
    store.count()

    class MultiplyBuilder(Builder):
      """
      Simple builder that multiplies the "a" sub-document by pre-set value
      """

      def __init__(self, source: Store, target: Store, multiplier: int = 2, query=None, **kwargs):
        """
        Arguments:
            source: the source store
            target: the target store
            multiplier: the multiplier to apply to "a" sub-document
        """
        self.source = source
        self.target = target
        self.multiplier = multiplier
        self.query = query
        self.kwargs = kwargs

        super().__init__(sources=source, targets=target, **kwargs)

      def get_items(self) -> Iterable:
        """
        Gets induvidual documents to multiply
        """
        for doc in self.source.query():
          yield doc

      def process_items(self, item: dict) -> dict:
        """
        Multiplies the "a" sub-document by self.multiplier
        """
        new_item = dict(**item)
        new_item["a"] *= self.multiplier
        return new_item

      def update_targets(self, items: list[dict]):
        """
        Adds the processed items into the target store
        """
        self.target.update(items)

      def prechunk(self, number_splits: int) -> Iterable[dict]:
        from maggma.utils import grouper
        keys = self.source.distinct(self.source.key)
        for split in grouper(keys, number_splits):
          yield {
              "query": {self.source.key: {"$in": list(split)}}
          }
    # run builder
    # my_builder = MultiplyBuilder(source_store,target_store,multiplier=3)
    # magma设计用于在生产环境中运行构建管道。构建器可以直接在python环境中运行，但这无法提供多处理等性能特性。基类Builder实现了一个简单的run方法，可用于运行该构建器：
    # my_builder.run()
    # Running Multiple Builders¶
    # mrun can run multiple builders. You can have multiple builders in a single file: json, python, or jupyter-notebook. Or you can chain multiple files in the order you want to run them:

    # $mrun -n 32 -vv my_first_builder.json builder_2_and_3.py last_builder.ipynb
    mybuilder = MultiplyBuilder()
    pass

  def example_MapBuilder(self):
    from maggma.builders import MapBuilder
    from maggma.core import Store

    class MultiplyBuilder(MapBuilder):
      """
      Simple builder that multiplies the "a" sub-document by pre-set value
      """

      def __init__(self, source: Store, target: Store, multiplier: int = 2, **kwargs):
        """
        Arguments:
            source: the source store
            target: the target store
            multiplier: the multiplier to apply to "a" sub-document
        """
        self.source = source
        self.target = target
        self.multiplier = multiplier
        self.kwargs = kwargs

        # kwargs = {k, v in kwargs.items() if k not in ["projection", "delete_orphans", "timeout", "store_process_time", "retry_failed"]}
        kwargs = {k: v for k, v in kwargs.items() if k not in [
            "projection", "delete_orphans", "timeout", "store_process_time", "retry_failed"]}

        super().__init__(source=source,
                         target=target,
                         projection=["a"],
                         delete_orphans=False,
                         timeout=10,
                         store_process_time=True,
                         retry_failed=True,
                         **kwargs)
      # Finally let's get to the hard part which is running our function. We do this by defining unary_function

      def unary_function(self, item):
        return {"a": item["a"] * self.multiplier}

  def example_GroupBuilder(self):
    from maggma.builders import GroupBuilder
    from maggma.core import Store

    class ResupplyBuilder(GroupBuilder):
      ...

  def example_SSHTunnel(self):
    """ 使用岩浆的典型场景之一是连接到防火墙后面的远程数据库，因此无法从本地计算机直接访问（如下所示，图片来源）。
    在这种情况下，可以使用SSHTunnel先连接到远程服务器，然后再从服务器连接到数据库。
    https://materialsproject.github.io/maggma/getting_started/using_ssh_tunnel/
    """

    import maggma.stores.ssh_tunnel
    tunnel = maggma.stores.ssh_tunnel.SSHTunnel(
        tunnel_server_address="<REMOTE_SERVER_ADDRESS>:22",
        username="<USERNAME>",
        password="<USER_CREDENTIAL>",
        remote_server_address="COMPUTE_NODE_1:9000",
        local_port=9000,
    )
    ...
    pass
