# [学习网址](https://www.w3school.com.cn/xpath/xpath_operators.asp)
# 概述
# xpath是xml文档中搜索内容的一门语言
# html是xml的一个子集，xpath 也能处理html

# 概念
# 在xml中每一项都称为节点, 基本值是无父或无子的节点。 项目：节点和基本值都属于项目
# 基本值的例子：
# J K. Rowling
# "en"
# 节点关系:父子，同胞，先辈，子代

# 在python3中如何用xpah，
# 安装lxml
# pip install lxml
# Xpath 解析

# <?xml version="1.0" encoding="ISO-8859-1"?>  #这一行加进去就会出错，不知道为啥
xml = '''
<bookstore>
<book>
  <title lang="eng">Harry Potter</title>
  <price>29.99</price>
</book>
<book>
  <title lang="zh-CN">学习 XML</title>
  <price>39.95</price>
</book>
</bookstore>'''

from lxml import etree

# 装载文件
tree = etree.XML(xml)  # 返回？
# print(type(tree))
# tree=etree.HTML() 
# tree=etree.parse(source,parser=None, base_url=None) 

# 从文件装载
# html01 = etree.parse('demo01.html') #, etree.HTMLParser())  # demo01.html是和当前py文件同级的文件
# print(html01)      # <lxml.etree._ElementTree object at 0x014CE940>  返回一个节点树
# result = etree.tostring(html01)  # 结果是bytes类型
# print(result.decode('utf-8'))  # 利用decode()方法将其转成str类型 ==> 输出demo01.html中的内容

# 使用xpath
# 1, 找标签
# result=tree.xpath("/bookstore/book[1]/title/text()") #xpath返回的是列表,即使里面只有一个元素, 从1开始数而非0 []表示索引
result = tree.xpath("/bookstore/book/title[@lang='zh-CN']/text()")  # 提取属性lang为zh-CN的标签（元素，节点）
# result=tree.xpath("/bookstore/book/title[@lang]/text()") #找具有属性lang的title标签  @用来选取属性
# result=tree.xpath("/bookstore/*/title/text()") # 从根节点查找,* 表示通配符
# result=tree.xpath('/bookstore//title/text()')  # 结果同上
# result=tree.xpath('//book/title/text() | //book/price/text()') # 选取 book 元素的所有 title 和 price 元素
# result=tree.xpath('/bookstore/book[price < 35]/title/text()') #选取 bookstore 元素的所有 book 元素，且其中的 price 元素的值须大于 35
# result=xpath('//div[@class="NewPages"]/a[text()="下一页"]/@href')  # 选取a的文本内容为"下一页"的a标签的href属性值
print(result)
# -还有运算符 and or = != >  两个节点的或 |
# 函数：position()

# 2，找内容
result = tree.xpath("/bookstore/book[1]/title/text()")  # text()用来拿文本, book[1]里面第一个文本
print(result)
result = tree.xpath("/bookstore/book/title")
for it in result:
    print(it.text)
# print(result)
# print(result[0].tag)  # 输出标签名
# print(result[0].text)  # 输出文本内容

# 3，找属性值
result = tree.xpath('//book/title/@lang')  # 提取的是lang的属性值
print(result)
# result1=tree.xpath('/bookstore/book')
# for it in result1:
#   result2=it.xpath('./title/@lang') #相对路径进一步查找, 
#   print(result2)
