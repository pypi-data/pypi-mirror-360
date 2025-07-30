# 可能需要先安装以下插件
# pip install --upgrade incremental
# pip install Twisted  #是scrapy低层的框架
# 先安装以上的模块
# pip install scrapy

# 步骤
"""
# 制作 Scrapy 爬虫 一共需要4步：
# 新建项目 (scrapy startproject xxx)：新建一个新的爬虫项目
# 明确目标 （编写items.py）：明确你想要抓取的目标
# 制作爬虫 （spiders/xxspider.py）：制作爬虫开始爬取网页
# 存储内容 （pipelines.py）：设计管道存储爬取内容
"""
# 具体操作步骤:
# -- 1. 创建了一个爬虫工程
"""
# $ scrapy startproject firstblood 
# 在当前目录下建立目录tutorial, 在./tutorial/ 里面有tutorial 目录和一个配置文件，
# 在./tutorial/tutorial/ 中有items.py       middlewares.py pipelines.py   settings.py  和./spiders/ (此时为空)
"""
# -- 2. 创建一个爬虫文件
"""
# $cd firstblood
# $scrapy genspider first "https://www.xxu.edu.cn/"  # scrapy genspider example example.com # 
# 之后会在 ./spiders/建立一个 first.py
# 通过这个命令去创建一个爬虫或者，可以省去每次都要写的一些命令，当然也可以不通过命令自己创建
"""
# -- 3. 编写爬虫，获取数据存入item
"""
# 3.1 编写items.py
    # 类似如下的方法
    title = scrapy.Field()  # 覆写类的属性
    link = scrapy.Field()
    desc = scrapy.Field()
# 3.2 编写first.py
# 先导入item.py 的包 from ..items import MyprojectTestItem
# 建立爬虫的子类(scrapy.Spider)，建立获取数据的方法等
#     content = response.body.decode('utf-8')  # 响应为字节，需要解码成字符串
# 写获取数据的方法时，可以Shell中尝试使用Selector选择器，这样可以避免每次都执行scrapy crawl xxu命令请求网页而浪费时间
# 您需要进入项目的根目录，执行下列命令来启动shell:
# $scrapy shell "https://www.xxu.edu.cn/"
"""
# -- 4. 存储数据
"""
# 4.1 基于终端指令存储数据   -->只可以将parse解析的返回值存储到本地文件中, 文件类型只能是'json', 'jsonlines', 'jl', 'csv', 'xml', 'marshal', 'pickle'
# 简洁高效，但只能是指定后缀的文本
scrapy crawl dmoz -o items.json #输出到json  
scrapy crawl dmoz -o items.jsonl #输出到jsonl
scrapy crawl dmoz -o items.xml #输出到xml
scrapy crawl dmoz -o items.csv #输出到csv

# 4.2 基于管道存储数据
# 流程：
    1. 数据解析
    2. 在items.py定义属性定义
    3. 将数据封装到item类型的对象
    4. 将item类型的对象提交给管道进行存储，在管道piplines.py文件中进行存储
    5. 在配置文件中settings.py 开启管道功能
# 好处：通用性比较强

# 通过编写管道文件piplines.py，别忘了在setings.py中开启pipline,存储数据，或者直接在爬虫文件中保存数据

"""
# --- 5. 最后通过以下命令启动爬虫
"""
# $ scrapy crawl xxu  # 项目中的任何目录下终端输入命令看结果
# scrapy crawl --nolog first  # --nolog 参数可以不显示日志信息  但是出错了也不会显示错误日志
# 可以在 setting.py 中任意位置加入如下代码
LOG_LEVEL = "ERROR"  # 而在执行时不要加入--nolog
这样如果出错了就可以只显示错误信息
"""

# 请求传参
# 使用场景，多页面抓取 例子

# 基于spider的全站数据爬取
"""
# 爬取优美图库美女写真板块里面的所有图片的名称
    # 实现方式
        - 将所有的url添加到列表中 不推荐 当页码较多时就不行了
        - 自行手动请求发送
"""

# ---反爬的处理，例如加user-agent
"""
# 在settings.py中大约18行设置如下
# USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
# 或者在如下位置打开设置并加入USER_AGENT
#DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en',
  "USER_AGENT" = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}
"""

# 在Shell中尝试Selector选择器
"""
# 您需要进入项目的根目录，执行下列命令来启动shell:
# $scrapy shell "https://www.xxu.edu.cn/"
# 当shell载入后，您将得到一个包含response数据的本地 response 变量。输入 response.body 将输出response的包体， 输出 response.headers 可以看到response的包头。
# 使用选择器的四个基本方法如下，eg: response.selector.xpath() 或者response.xpath()

# --- Selector有四个基本的方法(点击相应的方法可以看到详细的API文档): 都是返回列表
xpath(): 传入xpath表达式，返回该表达式所对应的所有节点的selector list列表 。
css(): 传入CSS表达式，返回该表达式所对应的所有节点的selector list列表.  # 语法同beautifulsoup
extract(): 序列化该节点为unicode字符串并返回list。
re(): 根据传入的正则表达式对数据进行提取，返回unicode字符串list列表。 #返回的字符串列表，与xpath和css不同的是不用extract()序列化
"""


# 在终端中操作
"""
scrapy  # 查看用法
scrapy <command> [options] [args]
例如：
scrapy bench # 查看机器的性能，查看每分钟能爬取的页面数目 Crawled 341 pages (at 900 pages/min),
scrapy fetch https://www.baidu.com  # Fetch a URL using the Scrapy downloader
scrapy shell https://www.baidu.com
Available commands:
  bench         Run quick benchmark test
  commands      
  fetch         Fetch a URL using the Scrapy downloader
  genspider     Generate new spider using pre-defined templates
  runspider     Run a self-contained spider (without creating a project)
  settings      Get settings values
  shell         Interactive scraping console
  startproject  Create new project
  version       Print Scrapy version
  view          Open URL in browser, as seen by Scrapy
Use "scrapy <command> -h" to see more info about a command
"""
