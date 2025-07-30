
import pymongo
import pymongo.client_session
import pymongo.database
import pymongo.mongo_client
import pymongo.read_concern
from pymongo.server_api import ServerApi
import os
import datetime
import gridfs
import pymongo.write_concern
import pymongo.operations


class MongodbLearn():
  def __init__(self):
    """https://www.mongodb.com/zh-cn/docs/manual/core/document/
    docs: https://www.mongodb.com/zh-cn/docs/atlas/security/add-ip-address-to-list/
    """
    pass

  def install(self):
    string = """在 macOS 上安装 MongoDB：
    你可以使用 Homebrew 来安装 MongoDB：
    brew tap mongodb/brew
    brew install mongodb-community
    安装完成后，你可以通过以下命令启动 MongoDB：
    brew services start mongodb/brew/mongodb-community

    # 这将通过 Homebrew 安装最新的 MongoDB Compass 版本
    brew tap mongodb/brew
    brew install --cask mongodb-compass

    """
    print(string)
    return None

  def init(self):
    string = """配置数据库目录
    $nohup mongod --dbpath /public/home/wangjl/my_server/my/mongoDB & # 后台启动mongodb 服务
    """
    print(string)
    return None

  def useage(self):
    string = """使用 mongosh（MongoDB Shell）来连接到正在运行的 MongoDB 实例：
    mongosh
    # 在这里，你已连接到本地 MongoDB 实例（默认地址是 mongodb://127.0.0.1:27017/）。你可以开始执行 MongoDB 的操作命令。
    操作 MongoDB 数据库
    你可以使用 MongoDB Shell 执行一些基本操作，如：
    show databases # 列出所有数据库：
    use myDatabase # 切换到某个数据库：
    db.myCollection.insertOne({ name: "Alice", age: 30 }) # 创建一个集合并插入数据：
    db.myCollection.find() # 查询集合中的数据：
    show collections # 查看当前数据库的集合：
    """
    print(string)
    return None

  def MongoDB_Compass(self):
    string = """连接到 MongoDB
    启动 MongoDB Compass 后，你将看到一个界面，要求你输入连接信息。根据你的设置，选择适合的连接类型：

    本地连接（默认）：
    连接字符串：mongodb://127.0.0.1:27017
    如果你在本地安装了 MongoDB，并且默认配置没有修改，使用这个连接字符串即可。

    ---
    远程连接（例如 MongoDB Atlas）：
    输入 MongoDB Atlas 提供的连接字符串，通常格式类似：mongodb+srv://<username>:<password>@cluster0.mongodb.net/test
    在连接成功后，你可以开始通过 MongoDB Compass 管理和浏览数据库。

    4. 使用 MongoDB Compass
    MongoDB Compass 提供了一个可视化界面，让你能够轻松进行以下操作：

    查看和管理数据库和集合。
    执行查询：可以用图形化界面构建查询，不需要手动写 MongoDB 的查询语法。
    分析数据库：查看数据库的统计信息和性能数据。
    数据可视化：MongoDB Compass 可以帮助你快速查看集合中的数据，以图表的形式呈现。
    """
    print(string)
    return None


class PymongoLearn():
  def __init__(self) -> None:
    """https://www.mongodb.com/zh-cn/docs/languages/python/pymongo-driver/current/write/replace/
    https://www.osgeo.cn/mongo-python-driver/tutorial.html
    https://learn.mongodb.com/learn/course/connecting-to-mongodb-in-python/lesson-2-connecting-to-an-atlas-cluster-in-python-applications/learn?client=customer
    """
    from soft_learn.MongoDB_learn import MongoDBLearn
    self.MongoDBLearn = MongoDBLearn.MongoDBLearn()
    self.pymongoDB_uri = "mongodb+srv://396292346_wjl:1011320sr@cluster0.tgum0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    self.mongoDB_atlas_URI = "mongodb+srv://396292346_wjl:1011320sr@cluster0.tgum0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    # 可以写入 .bashrc
    # export pymongoDB_uri="mongodb+srv://396292346_wjl:1011320sr@cluster0.tgum0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    # self.pymongoDB_uri = os.environ['pymongoDB_uri']
    # ---
    self.MongodbLearn = MongodbLearn()
    pass

  def install(self):
    string = """python -m pip uninstall "pymongo[srv]"
    或者: conda install pymongo dnspython
    """
    print(string)
    return None

  def get_client(self,
                 host='mongodb+srv://396292346_wjl:1011320sr@cluster0.tgum0.mongodb.net/',
                 compressors="zlib,zstd",  # snappy
                 ):
    """ client = pymongo.MongoClient(host="localhost", port=27017)
    或者使用MongoDB URI格式：
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    - db = mc.get_database(name='myMongoDB')
    - db_colection = db.get_collection(name='myMongoDB_Collection')
    - db_colection.find_one()
    """

    # 如果不指定压缩算法，PyMongo 不会压缩网络流量。 如果指定多种压缩算法，驱动程序会选择 MongoDB 实例支持的列表中的第一个算法。
    client = pymongo.MongoClient(host=host,
                                 compressors=compressors)

    return client

  def get_db(self, client: pymongo.MongoClient,
             name_DB='myMongoDB'):
    # client.list_database_names()
    # client[name_DB]
    # client.myMongoDB
    db = client.get_database(name=name_DB)
    return db

  def get_colection(self, db: pymongo.database.Database,
                    name_collection='myMongoDB_Collection'):
    db_colection = db.get_collection(name=name_collection)
    return db_colection

  def get_colection_atlas_URI_wrapper(self,
                                      host='mongodb+srv://396292346_wjl:1011320sr@cluster0.tgum0.mongodb.net/',
                                      name_DB='myMongoDB',
                                      name_collection='myMongoDB_Collection'
                                      ):
    mc = pymongo.MongoClient(host=host)
    db = mc.get_database(name=name_DB)
    db_colection = db.get_collection(name=name_collection)
    return db_colection

  def operations_database(self,):
    client = self.get_client(host='localhost')
    # ---
    # 列出当前所有数据库名称
    database_names = client.list_database_names()
    # 创建或者获得一个的数据库
    client.get_database(name='new_database')
    # # 删除现有数据库
    client.drop_database(name_or_database='new_database')
    pass

  def operations_collection(self,):
    client = self.get_client(host='localhost')
    db = client.get_database(name='test_database')
    # ---
    # 查看当前数据库中的所有集合
    db.list_collection_names()
    # 创建或者获得一个的集合
    col = db.get_collection(name='test_col')
    # 向集合中存放数据
    doc = {'test': 1}
    col.insert_one(document=doc)
    # 删除一个集合
    col.drop()
    pass

  def advance_query(self):
    client = self.get_client(host='localhost')
    db = client.get_database(name='test_database')
    col = db.get_collection(name='test_col')
    # ---
    # MongoDB支持多种不同类型的 advanced queries 。例如，让我们执行一个查询，其中我们将结果限制为某个日期之前的帖子，但也按作者对结果进行排序：
    d = datetime.datetime(2009, 11, 12, 12)
    col.find({"date": {"$gt": d}}).sort("author").to_list()
    return None

  def index_learn(self):
    client = self.get_client(host='localhost')
    client.list_database_names()
    db = client['test_database']
    # ---
    # 添加索引有助于加速某些查询，还可以为查询和存储文档添加附加功能。在此示例中，我们将演示如何创建 unique index 在拒绝其值已存在于索引中的文档的键上。
    # 首先，我们需要创建索引：
    result = db.profiles.create_index(
        [("user_id", pymongo.ASCENDING)], unique=True)
    sorted(list(db.profiles.index_information()))
    # 注意，我们现在有两个索引：一个是 _id MongoDB自动创建，另一个是 user_id 我们刚刚创造了。

    # 现在让我们设置一些用户配置文件：
    user_profiles = [{"user_id": 211, "name": "Luke"},
                     {"user_id": 212, "name": "Ziltoid"}]
    result = db.profiles.insert_many(user_profiles)

    # 索引阻止我们插入 user_id 已在集合中：
    new_profile = {"user_id": 213, "name": "Drew"}
    duplicate_profile = {"user_id": 212, "name": "Tommy"}
    result = db.profiles.insert_one(new_profile)  # This is fine.
    # result = db.profiles.insert_one(duplicate_profile) # 重复会出错

  def operations_doc(self):
    """更新操作中的修改器
    在实际中，更新文档往往是更新文档的一部分内容，在 MongoDB 中，我们可以使用更新修改器 (update modifier) 来对文档中某些字段进行更新，常用的修改器有以下几个：
    $set 用来指定一个字段的值，如果不存在，将创建一个新的字段
    $unset 删除一个字段
    $inc 用来增加(或减少)一个已有键的值，如果不存在将会创建一个
    $push 向已有的数组末尾添加一个元素
    $addToSet 避免插入重复数据
    $pull 删除元素，基于特定条件
    $each 遍历列表操作
    $pop 删除元素
    """
    client = self.get_client(host='localhost')
    db = client.get_database(name='test_database')
    col = db.get_collection(name='test_col')
    # ---
    # 向集合中存放数据
    doc = {'test': 1}
    post_doc = col.insert_one(doc)

    # insert_many() 用法
    col.insert_many([{'_id': 1}, {'_id': 2}])
    for data in col.find():
      print(data)
    # 删除集合中的文档
    col.delete_many({})
    # 查看
    col.count_documents({})
    # 或者只匹配特定查询的文档：
    # col.count_documents({"author": "Mike"})
    # 更新文档数据
    joe = {'name': 'joe', 'friends': 32, 'enemies': 2}
    col.insert_one(document=joe)
    joe_new = {'name': 'joe', 'friends': 32000, 'enemies': 200}
    col.replace_one(filter={'name': 'joe'}, replacement=joe_new)
    col.update_one({'name': 'joe'}, {'$set': {'favorite': 'War adn Peace'}})
    # 内嵌文档修改
    col.update_one({'name': 'joe'}, {'$set': {'enemies.name': 'bobo'}})
    # 删除 user 集合中 joe 的 favorite 字段
    col.update_one({'name': 'joe'}, {'$unset': {'favorite': 2}})
    # 添加数据
    col.update_one({'name': 'joe'}, {'$inc': {'score': 30}})
    # 在添加
    col.update_one({'name': 'joe'}, {
        '$push': {'abc': {'tuple': {'content': 'XXX'}}}})
    col.update_one({'name': 'joe'}, {
        '$push': {'abc': {'tuple': {'content': 'YYY'}}}})
    # 存在重复，数据不会被重复添加
    col.update_one({'name': 'joe'}, {
        '$addToSet': {'abc': {'tuple': {'content': 'YYYY'}}}})

    col.update_one({'name': 'joe'}, {'$push': {'emails': {
        '$each': ['joe@example.com', 'joe@outlook.com']}}})
    # 删除集合 user 中 joe 文档 emails 字段的第一个邮箱地址
    col.update_one({'name': 'joe'}, {'$pop': {'emails': -1}})
    col.find_one({'name': 'joe'})
    pass

  def operations_doc2(self):
    # 插入文档
    # 插入操作将一个或多个文档插入 MongoDB 集合。 您可以使用insert_one()或insert_many()方法执行插入操作。
    # 更新操作
    # update_one()，更新符合搜索条件的第一个文档, update_many()，更新符合搜索条件的所有文档
    # 替换文档
    # 您可以使用replace_one()方法在 MongoDB 中执行替换操作。 此方法会从匹配Atlas Search条件的第一个文档中删除除 _id 字段之外的所有字段。 然后，它将您指定的字段和值插入到文档中。
    # 删除操作
    # delete_one() ，删除符合搜索条件的第一个文档,delete_many()，删除所有符合Atlas Search条件的文档
    # ----
    pass

  def operations_doc_批量写入(self):
    # 批量写入操作
    # 定义写入操作
    # 对于要执行的每个写入操作，请创建以下操作类之一的实例：InsertOne, UpdateOne, UpdateMany, ReplaceOne, DeleteOne, DeleteMany, 然后，将这些实例的列表传递给bulk_write()方法。

    client = self.get_client()
    client.list_database_names()
    db = client.get_database(name='sample_restaurants')
    db.list_collection_names()
    restaurants = db["restaurants"]
    # 例创建了一个InsertOne实例：
    operation = pymongo.InsertOne(
        {
            "name": "Mongo's Deli",
            "cuisine": "Sandwiches",
            "borough": "Manhattan",
            "restaurant_id": "1234"
        }
    )
    # 调用bulk_write()方法, 为要执行的每个操作定义类实例后，将这些实例的列表传递给bulk_write()方法。 默认，该方法按照列表中定义的顺序运行操作。
    # 以下示例使用bulk_write()方法执行多个写入操作：
    operations = [pymongo.InsertOne({
        "name": "Mongo's Deli",
        "cuisine": "Sandwiches",
        "borough": "Manhattan",
        "restaurant_id": "1234"
    }
    ),
        pymongo.InsertOne(
            {
                "name": "Mongo's Deli",
                "cuisine": "Sandwiches",
                "borough": "Brooklyn",
                "restaurant_id": "5678"
            }
    ),
        pymongo.UpdateMany(
            {"name": "Mongo's Deli"},
            {"$set": {"cuisine": "Sandwiches and Salads"}},
    ),
        pymongo.DeleteOne(
            {"restaurant_id": "1234"}
    )
    ]
    results = restaurants.bulk_write(operations)
    print(results)
    pass

  def GridFSBucket_learn_存储大文件(self):
    """* https://www.mongodb.com/zh-cn/docs/languages/python/pymongo-driver/current/write/gridfs/
    gridfs.GridFSBucket 是 MongoDB 4.x 及更高版本推荐的 API，它提供了更灵活、更高效的文件上传和下载功能。GridFSBucket 使用了更底层的流操作，允许更细粒度的控制，适用于处理大文件或需要按块上传/下载的场景。
    ---
    * GridFSBucket 主要方法：
    open_upload_stream(): 创建一个上传流，你可以逐块写入文件数据。
    open_download_stream(): 创建一个下载流，允许按块读取文件内容。
    delete(): 删除文件。
    find(): 查找文件，根据条件返回文件。
    find_one(): 查找并返回第一个匹配的文件。
    ---
    * 总结
    GridFS: 较为简单的接口，适合小文件上传、下载操作，适合简单应用。
    GridFSBucket：更低级、更灵活，适合大文件和流式操作，推荐用于处理大型文件上传和下载。
    """
    client = self.get_client()
    # 创建 GridFS 存储桶
    # 要从 GridFS 存储或检索文件，请调用GridFSBucket()构造函数并传入Database实例，以创建 GridFS 存储桶。 您可以使用GridFSBucket实例对存储桶中的文件调用读取和写入操作。
    db = client.get_database(name='db')
    bucket = gridfs.GridFSBucket(db=db, bucket_name='myCustomBucket')
    # 上传文件
    # 使用GridFSBucket类中的open_upload_stream()方法为给定文件名创建上传流。 open_upload_stream()方法允许您指定配置信息，如文件数据段大小和其他要作为元数据存储的字段/值对。 将这些选项设置为open_upload_stream()的参数，如以下代码示例所示：
    with bucket.open_upload_stream(filename="my_file",
                                   chunk_size_bytes=1048576,
                                   # metadata 只是为了方便检索时方便查询
                                   metadata={
                                       "contentType": "text/plain", "author": "John Doe", "tags": ["example", "text file"]}
                                   ) as grid_in:
      grid_in.write(b"data to store", )
    # 查找所有 contentType 为 text/plain 且 author 为 John Doe 的文件
    files = bucket.find({
        "metadata.contentType": "text/plain",
        "metadata.author": "John Doe"
    })

    # 要上传的文件路径和文件名
    file_path = 'pymongoLearn.py'
    file_name = 'uploaded_file.txt'
    # 打开文件并上传到 GridFS, 这个方法更好
    with open(file_path, 'rb') as file_data:
      # 使用 bucket.upload_from_stream 上传文件
      file_id = bucket.upload_from_stream(filename=file_name, source=file_data)
      print(f"文件上传成功，文件 ID: {file_id}")
    # method 2. 使用 open_upload_stream() 创建上传流, 这种方法适合于内存不够的大文件如 100G大小的文件. 因为内存没有100G 无法一下子读取这个文件
    with open(file_path, 'rb') as file_data:
      # 打开上传流并逐块写入数据
      with bucket.open_upload_stream(file_name,) as upload_stream:
        # 逐块读取文件并写入上传流
        while chunk := file_data.read(1024 * 1024):  # 每次读取 1MB 数据
          upload_stream.write(chunk)
        print(f"文件上传成功，文件 ID: {upload_stream._id}")

    # 检索文件信息
    # 检索存储在 GridFS 存储桶的 files 集合的文件元数据。元数据包含所引用文件的相关信息，包括：文件的 _id,文件的名称,文件的长度/大小,上传日期和时间
    bf = bucket.find({}).to_list()[0]
    bf.filename
    # 下载文件
    # 您可以使用 GridFSBucket 中的 open_download_stream_by_name() 方法创建下载流，从 MongoDB 数据库下载文件。
    # 以下示例展示了如何下载文件名"my_file"引用的文件并读取其内容：
    file = bucket.open_download_stream_by_name(filename="my_file")
    contents = file.read()
    # 或者可以使用 open_download_stream() 方法将文件的 _id 字段作为参数：
    file = bucket.open_download_stream(grid_in._id)
    contents = file.read()
    # 下载文件
    with open('x.txt', 'wb') as file:
      bucket.download_to_stream_by_name(filename='uploaded_file.txt',
                                        destination=file)
    # 重命名文件
    # 使用 rename() 方法更新存储桶中 GridFS 文件的名称。您必须用文件的 _id 字段而不是文件名来指定要重命名的文件。
    bucket.rename(grid_in._id, new_filename="new_file_name")
    # 删除文件
    # 使用delete()方法从存储桶中删除文件的集合文档和关联的数据段。 这实际上删除了该文件。 您必须用文件的_id字段而不是文件名来指定文件。
    bucket.delete(file_id=bf._id)

    pass

  def grifs_learn(self):
    """较老的 API：GridFS 是较早版本 MongoDB 的接口，在 MongoDB 3.x 版本中使用更为广泛。自 MongoDB 4.x 版本开始，推荐使用 GridFSBucket。
    GridFS 主要方法：
    put(): 将文件上传到 GridFS，自动拆分文件并存储为多个块。
    get(): 根据文件 ID 获取文件并下载。
    delete(): 删除 GridFS 中的文件。
    find(): 查找文件，返回文件的元数据。

    # 总结
    GridFS: 较为简单的接口，适合小文件上传、下载操作，适合简单应用。
    GridFSBucket：更低级、更灵活，适合大文件和流式操作，推荐用于处理大型文件上传和下载。
    """
    # 我们从创建一个 GridFS 要使用的实例：
    db = pymongo.MongoClient().gridfs_example
    fs = gridfs.GridFS(db,)
    # 保存和检索数据
    fs.put(b"hello world", filename='abc.txt')

    fname = 'pymongoLearn.py'
    with open(fname, mode='rb') as file:
      b = fs.put(file, filename=fname)
    id = fs.find({'filename': 'pymongoLearn.py'}).to_list()[0]._id
    fs.get(id).read()
    # 检索
    id = fs.find({'filename': 'abc.txt'}).to_list()[0]._id
    # 要取回文件的内容
    fs.get(file_id=id).read()
    fs.delete(file_id=id)

  def transaction_learn(self):
    """( client.start_session() 的最大优势之一是它支持 多文档事务 (multi-document transactions)。在 MongoDB 中，事务是确保多个操作在多个文档或多个集合之间保持原子性的一种机制。通过会话，你可以确保一组操作要么全成功，要么全失败，从而避免部分成功的情况，这对于需要数据一致性的应用场景非常重要。
    * 通过会话，你可以确保多个操作（特别是在分布式环境中）能够在独立的事务或操作范围内执行。这对于 并发控制 至关重要。例如，多个应用程序或多个服务可能同时访问 MongoDB，通过会话，你可以为每个操作提供隔离性，确保并发操作之间互不干扰，保证数据的一致性。
    """
    # 下示例显示如何通过以下步骤创建会话、创建事务以及提交多文档插入操作：
    # 使用 start_session() 方法从客户端创建会话。
    # 使用 with_transaction() 方法启动事务。
    # 插入多个文档。 with_transaction()方法运行插入操作并提交ACID 事务。 如果任何操作导致错误， with_transaction()将取消该ACID 事务。 此方法可确保在区块退出时正确关闭会话。
    # 使用client.close()方法关闭与服务器的连接。
    # Establishes a connection to the MongoDB server
    client = self.get_client()
    # Defines the database and collection
    restaurants_db = client["sample_restaurants"]
    restaurants_collection = restaurants_db["restaurants"]
    # Function performs the transaction

    def insert_documents(session):
      restaurants_collection_with_session = restaurants_collection.with_options(
          write_concern=pymongo.write_concern.WriteConcern("majority"),
          read_concern=pymongo.read_concern.ReadConcern("local")
      )

      # Inserts documents within the transaction
      restaurants_collection_with_session.insert_one(
          {"name": "PyMongo Pizza", "cuisine": "Pizza"}, session=session
      )
      restaurants_collection_with_session.insert_one(
          {"name": "PyMongo Burger", "cuisine": "Burger"}, session=session
      )

    # Starts a client session
    # with_transaction() 是 pymongo 中 client_session 的一个方法，简化了事务的管理。使用 with_transaction，你不需要手动调用 start_transaction() 来开始事务，也不需要手动调用 commit_transaction() 来提交事务。with_transaction 会在你指定的回调函数（在这个例子中是 insert_documents）中自动管理事务，确保事务在操作成功时提交，并在发生错误时回滚。
    with client.start_session() as session:
      try:
        # Uses the with_transaction method to start a transaction, execute the callback, and commit (or abort on error).
        session.with_transaction(insert_documents)
        print("Transaction succeeded")
      except (pymongo.client_session.ConnectionFailure, pymongo.client_session.OperationFailure) as e:
        print(f"Transaction failed: {e}")

    # Closes the client connection
    client.close()
    pass

  def find_learn_查询(self):
    client = self.get_client()
    try:
      database = client["sample_fruit"]
      collection = database["fruits"]

      collection.insert_many([
          {"_id": 1, "name": "apples", "qty": 5, "rating": 3,
           "color": "red", "type": ["fuji", "honeycrisp"]},
          {"_id": 2, "name": "bananas", "qty": 7, "rating": 4,
           "color": "yellow", "type": ["cavendish"]},
          {"_id": 3, "name": "oranges", "qty": 6,
           "rating": 2, "type": ["naval", "mandarin"]},
          {"_id": 4, "name": "pineapple", "qty": 3, "rating": 5, "color": "yellow"},
      ])

      client.close()

    except Exception as e:
      raise Exception("Error inserting documents: ", e)

    client = self.get_client()
    database = client["sample_fruit"]
    collection = database["fruits"]
    collection.count_documents({})
    # 精确匹配
    results = collection.find({"color": "yellow"})
    # 查找所有文档
    results = collection.find({})
    collection.find({"rating": {"$gt": 2}}).to_list()
    # 比较操作符。
    # 比较运算符会根据查询筛选器中的指定值评估文档字段值。 以下是常见比较操作符的列表：$gt ：大于, $lte ：小于或等于, $ne ：不等于
    # 逻辑操作符
    # $and ，返回符合所有子句条件的所有文档,$or ，返回符合一个子句条件的所有文档,$nor ，返回所有不符合任何子句条件的文档, $not ，返回与表达式不匹配的所有文档
    collection.find(
        {"$or": [{"qty": {"$gt": 5}}, {"color": "yellow"}]}).to_list()
    # 数组操作符根据数组字段中元素的值或数量来匹配文档。 以下是可用数组操作符的列表：$all ，返回带有数组的文档，而该数组包含查询中的所有元素,$elemMatch ，如果大量字段中的元素与查询中的所有条件匹配，则返回文档,$size ，返回包含指定大小数组的所有文档
    collection.find({"type": {"$size": 2}}).to_list()
    # 元素操作符
    # 元素操作符根据字段的存在或类型查询数据。
    # 以下示例将查询筛选器中的元素操作符指定为find()方法的参数。 此代码将返回所有具有color字段的文档：
    collection.find({"color": {"$exists": "true"}}).to_list()
    # 评估操作符
    # 求值操作符根据对单个字段或整个文集文件的求值结果返回数据。
    # 以下是常见评估操作符的列表：$text ，对文档执行文本搜索, $regex,，返回与指定正则表达式匹配的文档,$mod ，对字段的值执行模运算并返回余数为指定值的文档
    # 以下示例将查询筛选器中的评估运算符指定为find()方法的参数。 此代码使用正则表达式返回name字段值至少有两个连续"p"字符的所有文档：
    collection.find({"name": {"$regex": "p{2,}"}}).to_list()
    pass

  def find_learn_指定字段(self):
    client = self.get_client()
    db = client.get_database(name='sample_restaurants')
    restaurants = db.get_collection(name='restaurants')
    # restaurants.find_one({"cuisine": "Bakery"})
    # 指定要返回的字段
    # 在本指南中，您可以了解如何使用投影指定从读取操作中返回哪些字段。 投影是指定 MongoDB 从查询中返回哪些字段的文档。
    # 以下示例使用find()方法查找name字段值为"Emerald Pub"的所有餐厅。 然后，它使用投影仅返回所返回文档中的name 、 cuisine和borough字段。
    restaurants.find({"name": "Emerald Pub"}, {"name": 1,
                                               "cuisine": 1, "borough": 1}).to_list()
    # 排除_id字段
    # 在指定要包含的字段时，您还可以从返回的文档中排除_id字段。
    # 以下示例执行与前面的示例相同的查询，但从投影中排除_id字段：
    restaurants.find({"name": "Emerald Pub"}, {
        "_id": 0, "name": 1, "cuisine": 1, "borough": 1}).to_list()
    # 以下示例使用find()方法查找name字段值为"Emerald Pub"的所有餐厅。 然后，它使用投影从返回的文档中排除grades和address字段：
    restaurants.find({"name": "Emerald Pub"}, {
        "grades": 0, "address": 0, }).to_list()

  def find_learn_指定要返回的文档(self):
    client = self.get_client()
    db = client.get_database(name='sample_restaurants')
    restaurants = db.get_collection(name='restaurants')
    # 在本指南中，您可以学习；了解如何使用以下方法指定从读取操作中返回哪些文档：
    # limit() ：指定查询返回的最大文档数。
    # sort() ：指定返回文档的排序顺序。
    # skip() ：指定在返回查询结果之前要跳过的文档数。
    # Limit
    # 要指定读取操作返回的最大文档数，请调用limit()方法。
    # 以下示例查找cuisine字段值为"Italian"的所有餐馆，并将结果限制为5文档：
    restaurants.find({"cuisine": "Italian"}).limit(5).to_list()
    # Sort
    # 要按指定顺序返回文档，请调用sort()方法。 sort()方法接受两个参数：对结果进行排序的字段和排序方向。 要指定排序方向，请指定pymongo.ASCENDING或pymongo.DESCENDING 。 ASCENDING将值从最低到最高排序， DESCENDING将值从最高到最低排序。 如果未指定任一方向，则该方法默认按升序排序。
    # 以下示例返回cuisine值为"Italian"的所有文档，并按升序排序：
    restaurants.find({"cuisine": "Italian"}).sort(
        "name", pymongo.ASCENDING).to_list()
    # 跳过
    # 要在返回查询结果之前跳过指定数量的文档，请调用skip()方法并传入要跳过的文档数。 skip()方法会忽略查询结果中指定数量的文档并返回其余文档。
    # 以下示例返回borough字段值为"Manhattan"的所有文档，并跳过前10文档：
    restaurants.find({"borough": "Manhattan"}).skip(10).to_list()
    # 组合限制、排序和跳过
    # 您可以在单个操作中组合使用limit() 、 sort()和skip()方法。 这允许您设置要返回的最大排序文档数，在返回之前跳过指定数量的文档。
    # 以下示例返回cuisine值为"Italian"的文档。 结果按字母顺序排序，跳过前10文档：
    restaurants.find({"cuisine": "Italian"}) .sort(
        "name", pymongo.ASCENDING) .limit(5) .skip(10).to_list()
    # 您还可以在find()方法中将结果指定为参数，从而对结果进行限制、排序和跳过。 以下示例指定与前面的示例相同的查询：
    restaurants.find({"cuisine": "Italian"}, limit=5, sort={
        "name": pymongo.ASCENDING}, skip=10).to_list()

    pass

  def doc_计算文档(self):
    client = self.get_client()
    db = client.get_database(name='sample_restaurants')
    collection = db.get_collection(name='restaurants')
    # 对所有文档进行计数
    # 要返回集合中所有文档的计数，请将空字典传递给count_documents()方法，如以下示例所示：
    collection.count_documents({})
    # 对特定文档进行计数
    # 要返回与特定Atlas Search条件匹配的文档计数，请在 count_documents() 方法中指定您的查询，如以下示例所示：
    collection.count_documents({"author": "Mike"})
    # 检索估计计数
    # 您可以通过调用estimated_document_count()方法来估计集合中的文档数量。 该方法根据集合元数据估计文档数量，这可能比执行精确计数更快。
    collection.estimated_document_count()
    pass

  def doc_检索不同字段值(self):
    client = self.get_client()
    db = client.get_database(name='sample_restaurants')
    restaurants = db.get_collection(name='restaurants')
    # distinct() 方法
    # 要检索指定字段的非重复值，请调用distinct()方法并传入要查找非重复值的字段的名称。
    # 以下示例检索restaurants集合中borough字段的非重复值：
    restaurants.distinct("borough")
    # 以下示例检索cuisine字段值为"Italian"的所有文档的borough字段的非重复值：
    restaurants.distinct("borough", {
        "cuisine": "Italian"})
    # 以下示例检索borough字段值为"Bronx"且cuisine字段值为"Pizza"的所有文档的name字段的非重复值。 它还使用comment选项为操作添加注释。
    restaurants.distinct("name",
                         {"borough": "Bronx",
                          "cuisine": "Pizza"},
                         comment="Bronx pizza restaurants"
                         )
    pass

  def doc_监控数据变化(self):
    client = self.get_client()
    db = client.get_database(name='sample_restaurants')
    collection = db.get_collection(name='restaurants')
    # 打开变更流
    # 要打开变更流，请调用watch()方法。 您调用watch()方法的实例决定了变更流侦听的事件范围。 您可以对以下类调用watch()方法：
    # 以下示例在restaurants集合上打开变更流，并在发生变更时输出变更：
    with collection.watch() as stream:
      for change in stream:
        with open('x.txt', mode='a+') as f:
          f.write(str(change) + '\n')

    # 以下示例使用pipeline参数打开仅记录更新操作的变更流：
    # change_pipeline = {"$match": {"operationType": "update"}},
    # with collection.watch(pipeline=change_pipeline) as stream:
    #   for change in stream:
    #     print(change)

    # 更新集合时，变更流应用程序会在发生变更时打印变更。
    # 要开始监视更改，请运行该应用程序。 然后，在单独的应用程序或 shell 中，修改restaurants集合。 以下示例更新name字段值为Blarney Castle的文档：
    query_filter = {"name": "Blarney Castle"}
    update_operation = {'$set':
                        {"cuisine": "Irish"}
                        }
    result = collection.update_one(query_filter, update_operation)

    pass

  def command_运行数据库命令(self):
    client = self.get_client()
    db = client.get_database(name='sample_restaurants')
    collection = db.get_collection(name='restaurants')
    # 执行命令
    # 您可以使用 command() 方法运行数据库命令。您必须指定命令和所有相关参数。 如果命令很简单，则可以将其作为字符串传递。 否则，它们可以作为 dict对象传递。该方法将返回所运行命令的结果。
    # 以下代码展示如何在 Database 上使用 command() 方法来运行hello 命令，该命令会返回有关服务器的信息：

    database = client.get_database("my_db")
    hello = database.command("hello")
    print(hello)
    # 命令游标
    # command() 方法返回所运行命令的结果。您还可以使用cursor_command() 方法，该方法发出MongoDB命令并将响应解析为 CommandCursor 。CommandCursor 可用于遍历命令结果。
    # 以下示例在 sample_mflix数据库上使用 cursor_command() 方法。它对 movies集合运行 find 命令，以按 runtime字段值为 11 的文档进行过滤。
    database = client.get_database("sample_mflix")
    database.cursor_command("find", "movies", filter={"runtime": 11}).to_list()
    # 以下示例使用command()方法运行dbStats命令，以检索sample_mflix数据库的存储统计信息：
    database = client.get_database("sample_mflix")
    database.command("dbStats")

  def index_使用索引优化查询(self):
    """MongoDB 默认会使用 全表扫描（扫描所有文档）来执行查询。如果数据量非常大，全表扫描会非常慢，尤其是当你进行复杂的查询时，速度会明显下降。通过为查询条件创建索引，MongoDB 可以跳过不相关的文档，直接定位到匹配的文档，从而加快查询速度。
    示例：
    如果你有一个包含百万条记录的数据库，且你经常根据字段 name 进行查询，创建索引就能使得这些查询比全表扫描更快速。

    3. 索引的作用
    加速查询：通过在查询条件字段上创建索引，可以显著提高查询速度，尤其是当查询条件涉及到多个字段时。
    优化排序操作：索引不仅加速查询，还能提高排序（sort）操作的效率。没有索引时，MongoDB 需要加载所有文档，然后进行排序，而有索引时，可以直接在索引上进行排序，节省了时间。
    提高聚合操作的效率：一些聚合操作（如 $group, $match 等）会显著受益于索引。合适的索引可以减少聚合时需要处理的数据量，提高性能。
    支持唯一性约束：你可以创建唯一索引来确保某个字段的值在集合中是唯一的，防止插入重复数据。
    # ---
    # 使用索引 操作注意事项
    # 若要提高查询性能，请对应用程序查询中经常出现的字段以及其他操作返回的排序结果中经常出现的字段建立索引。您添加的每个索引在活动状态下都会占用磁盘空间和内存，因此您应当跟踪索引内存和磁盘使用情况以进行容量规划。此外，当写入操作更新索引化字段时，MongoDB 还须更新相关索引。
    """
    client = self.get_client()
    db = client.get_database(name='sample_mflix')
    database = db
    movies = db.get_collection(name='movies')
    collection = movies

    movies.find_one({})
    # 创建单字段索引
    # 以下示例将对 title 字段按升序创建索引：
    movies.create_index("title")
    # 以下是前面代码示例中创建的索引涵盖的查询示例：
    query = {"title": "Batman"}
    # 等效 sort = [("title", pymongo.ASCENDING)], pymongo.ASCENDING 就等于1
    sort = [("title", 1)]
    movies.find(query).sort(sort).to_list()

    # 创建复合索引
    # 以下示例在 type 和 genre 字段上创建复合索引：
    movies.create_index([("type", pymongo.ASCENDING),
                        ("genre", pymongo.ASCENDING)])
    # 以下是使用前面代码示例中创建的索引的查询示例：
    query = {"type": "movie", "genre": "Drama"}
    sort = [("type", pymongo.ASCENDING), ("genre", pymongo.ASCENDING)]
    movies.find(query).sort(sort).to_list()
    # 创建多键索引
    # 以下示例在cast字段上创建多键索引：
    result = movies.create_index("cast")
    # 以下是使用前面代码示例中创建的索引的查询示例：

    query = {"cast": "Viola Davis"}
    cursor = movies.find(query)
    # 以下代码示例展示了如何创建 Atlas Search 索引和 Atlas Vector Search 索引：
    search_idx = pymongo.operations.SearchIndexModel(
        definition={
            "mappings": {
                "dynamic": True
            }
        },
        name="my_index",
    )
    vector_idx = pymongo.operations.SearchIndexModel(
        definition={
            "fields": [
                {
                    "type": "vector",
                    "numDimensions": '<number of dimensions>',
                    "path": "<field to index>",
                    "similarity": "<select from euclidean, cosine, dotProduct>"
                }
            ]
        },
        name="my_vector_index",
        type="vectorSearch",
    )
    indexes = [search_idx, vector_idx]
    collection.create_search_indexes(models=indexes)
    # 更新搜索索引
    # 您可以使用 update_search_index() 方法更新 Atlas Search 或 Vector Search 索引。

    # 以下代码示例展示如何更新 Atlas Search 索引：

    new_index_definition = {
        "mappings": {
            "dynamic": False
        }
    }
    collection.update_search_index("my_index", new_index_definition)
    # 以下代码示例展示如何更新 Atlas Vector Search 索引：

    new_index_definition = {
        "fields": [
            {
                "type": "vector",
                "numDimensions": 1536,
                "path": "<field to index>",
                "similarity": "euclidean"
            },
        ]
    }
    collection.update_search_index("my_vector_index", new_index_definition)
    # 删除搜索索引
    # 您可以使用 drop_search_index() 方法删除 Atlas Search 或 Vector Search 索引。

    # 以下代码展示了如何从集合中删除搜索索引：

    collection.drop_index("my_index")

    pass

  def index_使用索引优化查询_text索引(self):
    client = self.get_client()
    db = client.get_database(name='sample_mflix')
    movies = db.get_collection(name='movies')
    # Text Indexes
    # Overview
    # 文本索引支持对字符串内容进行文本搜索查询。这些索引可以包括任何值为字符串或字符串元素数组的字段。MongoDB 还支持各种语言的文本搜索。在创建索引时，可以指定默认语言作为选项。
    # 单个字段上的文本索引
    # 以下示例在 plot 字段上创建一个文本索引：
    movies.create_index([("plot", "text")])
    # 以下是使用前面代码示例中创建的索引的查询示例：
    query = {"$text": {"$search": "a time-traveling DeLorean"}}
    movies.find(query).to_list()

    # 多个字段上的文本索引
    # 一个集合只能包含一个文本索引。 如果要为多个文本字段创建文本索引，请创建复合索引。 对复合索引中的所有文本字段运行文本搜索。
    # 以下示例为title和genre字段创建复合文本索引：
    # result = movies.create_index(
    #     [("title", "text"), ("genre", "text")],
    #     default_language="english",
    #     weights={ "title": 10, "genre": 3 }
    # )
    pass

  def index_唯一索引(self):
    client = self.get_client()
    db = client.get_database(name='sample_mflix')
    database = db
    theaters = db.get_collection(name='theaters')
    # 创建唯一索引
    # 以下示例在theaterId字段上创建一个降序唯一索引：
    theaters.create_index("theaterId", unique=True)
    return None

  def index_通配符索引(self):
    # 通配符索引可对未知或任意字段进行查询。如果您使用的是动态模式，则这些索引可能很有用。
    # 创建通配符索引
    # 以下示例将对 location 字段的所有值（包括嵌套在子文档和数组中的值）创建升序通配符索引：
    client = self.get_client()
    sample_mflix = client.get_database(name='sample_mflix')
    movies = sample_mflix.get_collection(name='movies')
    movies.create_index({"location.$**": pymongo.ASCENDING})
    # 创建集群索引
    # 以下示例在新的movie_reviews集合中的_id字段上创建集群索引：
    sample_mflix.create_collection("movies", clusteredIndex={
        "key": {"_id": 1},
        "unique": True
    })

    pass

  def example(self, uri,
              name_db='sample_restaurants',
              name_collection='restaurants',
              ):
    try:
      client = pymongo.MongoClient(uri)
      client = self.get_client()
      database = client.get_database(name=name_db)
      collection = database.get_collection(name=name_collection)
      # start example code here

      # end example code here

      client.close()

    except Exception as e:
      raise Exception(
          "The following error occurred: ", e)
  # old

  def operations_find(self):
    client = self.get_client(host='localhost')
    db = client.get_database(name='test_database')
    col = db.get_collection(name='test_col')
    col.delete_many({})
    # ---
    joe = {'name': 'joe', 'age': 26}
    mike = {'name': 'mike', 'age': 28}
    jake = {'name': 'jake', 'age': 26}
    # 使用 insert_many() 可以一次添加多个文档记录
    col.insert_many([joe, mike, jake])
    # for data in col.find():
    #   print(data)
    # 指定返回字段, 我们在查询的时候，可能并不需要文档中的所有字段，这是我们可以在查询条件之后再传入一个参数来指定返回的字段。
    # 不要 _id 字段
    col.find_one({}, {'_id': 0})
    # 只输出 _id 字段
    col.find_one({}, {'_id': 1})

    # 在查询中，我们会经常用到比较字段值得大小来查询数据，实现这一功能我们会用到比较操作符，Pymongo 常用的比较操作符有以下几个：
    # $lt 小于
    # $let 小于等于
    # $ge 大于
    # $gte 大于等于
    # $ne 不等于
    # 查询大于 26 岁的用户
    # for data in col.find({'age': {'$gt': 26}}):
    #   print(data)

    # $in 和 $nin 的用法, 我们可以使用 $in 和 $nin 操作符来匹配一个键的多个值，具体用法示例如下：
    # 用户名为 joe 和 mike 的文档记录
    # for data in col.find({'name': {'$in': ['joe', 'mike']}}):
    #   print(data)
    # 匹配用户名不是 mike 的用户 注意： $in 和 $nin 条件必须是一个数组
    for data in col.find({'name': {'$nin': ['mike']}}):
      print(data)
    # $or 的用法, 如果需要查询两个条件中其中一个为真的查询结果，可以使用 $or 操作符。具体示例如下：
    for data in col.find({'$or': [{'name': 'mike'}, {'age': 80}]}):
      print(data)

    # 为方便演示，创建一个 c 集合，并向里面添加 3 条记录
    # col.insert_many([{'y': None}, {'y': 1}, {'y': 2}])
    # 查询 null 值
    for data in col.find({'z': {'$in': [None], '$exists': 1}}):
      print(data)

    # 为方便演示，创建一个 c 集合，并向里面添加 3 条记录
    # col.insert_many([{'y': None}, {'y': 1}, {'y': 2}])
    # 查询 null 值
    for data in col.find({'z': {'$in': [None], '$exists': 1}}):
      print(data)

    pass

  def operations_find_array(self):
    client = self.get_client(host='localhost')
    db = client.get_database(name='test_database')
    col = db.get_collection(name='test_col')
    col.delete_many({})
    # ---
    # 查询数组, 在实际使用当中，我们还可能会存在文档中有数组形式的字段值，因此我们需要一些特定的操作来查询匹配这些数组，同样的，MongoDb 提供了相关的操作符可以使用，常用的数组操作符有以下几个：
    # $all 匹配多个元素数组
    # $size 匹配特定长度的数组
    # $slice 返回匹配数组的一个子集
    # 下面将用代码演示以上三个操作符的用法。为方便演示，我们会先创建一个 food 的集合用来存放水果的文档记录。
    food = db.get_collection(name='test')
    food.drop()

    food.insert_one({'_id': 1, 'fruit': ['apple', 'peach', 'banana', ]})
    food.insert_one({'_id': 2, 'fruit': ['apple', 'kumquat', 'orange']})
    food.insert_one({'_id': 3, 'fruit': ['cherry', 'banana', 'apple']})

    # all
    result = food.find({'fruit': {'$all': ['apple', 'banana']}})
    result.to_list()
    # 也可以使用位置定位匹配
    result = food.find({'fruit.1': 'banana'})  # 位置在第二个的 banana
    result.to_list()

    food.update_one({'_id': 2}, {'$push': {'fruit': 'strawbreey'}})
    # 查找数组size为3的结果
    result = food.find({'fruit': {'$size': 4}})
    result.to_list()
    # $slice 可以返回某个键匹配的数组的一个子集，我们将会用 blog 集合来演示使用 $slice 操作符获取特定数量的评论记录。
    # 获取前两条评论记录
    food.find({}, {'fruit': {'$slice': 2}}).to_list()
    # 获取最后一条评论记录
    food.find({}, {'fruit': {'$slice': -1}}).to_list()
    # ----
    c = db.get_collection(name='test_col')
    # 我们先清空 c 集合，并加入新的文档记录
    c.delete_many({})
    c.insert_many([{'x':  5}, {'x': 15}, {'x': 25}, {'x': [5, 25]}])

    # 假设我们需要查询 [10, 20] 区间内的记录
    c.find({'x': {'$gt': 10, '$lt': 20}}).to_list()
    # 这里看到 [5, 25] 这一条记录其实是不符合我们的查询预期的
    # 我们可以使用 $elemMatch 来不匹配非数组元素
    c.find({'x': {'$elemMatch': {'$gt': 10, '$lt': 20}}}).to_list()
    # >> // 没有输出结果
    # 通过添加 $elemMatch 可以剔除 [5, 25] 这一记录，但正确的查询结果 {'x': 15} 却不能匹配
    # 我们将使用 min() 以及 max() 方法
    # 为使用者两个方法，我们需要先给 c 集合的 x 字段建立索引
    c.create_index('x')
    # c.find({'x': {'$gt': 10, '$lt': 20}}).min([('x', 10)]).to_list()
    # ---
    client = self.get_client(host='localhost')
    db = client.get_database(name='test_database')
    c = db.get_collection(name='test_col')
    c.delete_many({})
    # ---
    import pymongo
    import random
    type(c.find())  # pymongo.synchronous.cursor.Cursor
    c.drop()
    # 我们创建一系列文档
    for i in range(20):
      c.insert_one({'x': random.randint(0, 20)})
    # 我们在基于上面的集合数据之下，对 x 进行一个排序操作，可以使用 sort() 方法，具体操作如下：
    c.find().sort([('x', pymongo.ASCENDING)]).to_list()
    # 降序
    c.find().sort([('x', pymongo.DESCENDING)]).to_list()
    pass

  def get_colection_local_wrapper(self,
                                  host='localhost',
                                  name_DB='MongoStore_local_DB',
                                  name_collection='jobs'
                                  ):
    mc = pymongo.MongoClient(host=host)
    db = mc.get_database(name=name_DB)
    db_colection = db.get_collection(name=name_collection)
    return db_colection

  def example_aggregate(self):
    # aggregate
    from bson.son import SON
    from pymongo import MongoClient
    db = MongoClient().aggregation_example
    db.things.delete_many({})
    result = db.things.insert_many(
        [{"x": 1, "tags": ["dog", "cat"]},
            {"x": 2, "tags": ["cat"]},
            {"x": 2, "tags": ["mouse", "cat", "dog"]},
            {"x": 3, "tags": []},]
    )

    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": SON([("count", -1), ("_id", -1)])},
    ]
    db.things.aggregate(pipeline).to_list()

  def terminal_connect(self):
    string = """终端输入:
    mongosh "mongodb+srv://396292346_wjl:1011320sr@cluster0.tgum0.mongodb.net/" --apiVersion 1
    或者 mongosh "mongodb+srv://cluster0.tgum0.mongodb.net/myMongoDB" -u 396292346_wjl -p 1011320sr
    """
    print(string)
    return None

  def connect(self):
    client = self.get_client()
    # Send a ping to confirm a successful connection
    try:
      client.admin.command('ping')
      print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
      print(e)
    pass


class Features():
  def __init__(self):
    self.PymongoLearn = PymongoLearn()
    self.MongodbLearn = MongodbLearn()
    pass

  def add_asedb_to_mongodb(self, db_row, name='O_I_MVG',
                           name_collection='vasp_calc_DB'):
    from py_package_learn.ase_learn import aseLearn
    af = aseLearn.Features()
    atoms_dict = af.get_atoms_dict(atoms=db_row.toatoms())

    col = self.PymongoLearn.get_colection_local_wrapper(
        name_collection=name_collection)
    # col.delete_many({})
    # col.create_index([("name", pymongo.ASCENDING)], unique=True)
    a = {'name': name, 'atoms': atoms_dict,
         'magmoms': db_row.magmoms.tolist(), **db_row.key_value_pairs}
    col.update_one({'name': name}, {'$set': a}, upsert=True)
    return col
