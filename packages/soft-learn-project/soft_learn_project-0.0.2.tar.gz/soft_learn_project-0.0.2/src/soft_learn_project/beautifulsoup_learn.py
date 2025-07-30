# 拿到页面源代码
# 用bs4进行解析，拿到数据

# beatifulsoup 的用法
from bs4 import BeautifulSoup
import re

# bs4的用法，主要是以下两个命令：
# find(标签，属性=值)  #注意class是python 关键字，需要写成class_=""
# find_all(标签，属性=值,属性=值,...)  #返回的是列表

html_doc = "./baidunews.html"
html_file = open(html_doc, 'r', encoding='utf-8')  # encoding='gbk') 如果html文件的编码不是utf-8，看看是什么否则可能出错，
html_handle = html_file.read()

# 把页面源代码交给BeautifulStoneSoup处理生成Beautifulsoup对象
soup = BeautifulSoup(html_handle, 'html.parser')  # html.parser 指定html解析器
print(soup.div.find('a').get_text())  # 网页全部内容
print(soup.div.a.text)
print(soup.div.li.a.attrs['href'])  # 通过.div 或者find('div')获得的还是bs元素类对象，可以继续使用bs对象的方法
print(soup.find('div').find('li').find('a').get('href'))

lis = [i for i in range(10)]
print(lis[0:])

# 1 获取标签
"""
# print(soup.p)  # 找到第一个p标签
# print(soup.find('p'))  # 找到第一个p标签
# print(soup.find_all('p'))  # 找到所有的p标签,注意返回的是列表
# print(soup.find_all(id="headerwrapper"))  # 根据属性找标签，找到id="..."的所有标签
# print(soup.find("a", href="/auto"))  # 找到标签为a, 属性为href="/auto"的标签
# print(soup.find('div', class_="top-banner", id="topbanner"))  # class是python关键字，所以为了避免混淆加入_, 仍然表示class属性
# print(soup.find('div', attrs={"class": "top-banner","id":"topbanner"})) #属性可以改为字典形式
"""

# 2 找文本, 标签的文本内容
"""
# print(soup.find('a').get_text())  # 获得文本
# print(soup.find('a').string) 
# print(soup.find('a').text)
# soup.find_all('a') 返回的是列表，用法如下：
# for i in soup.find_all('a'):
#     print(i.get('href'))
"""

# 3 找属性值
"""
print(soup.find('a').get('href'))  # 获取a标签的href属性的属性值
# print(soup.find('a').attrs) #获取p标签的属性, 返回的是字典
"""

# 4 找属性名  #一般不用
# print(soup.find('a').name)


'''
# 正则表达式
# 如果传入正则表达式作为参数,Beautiful Soup会通过正则表达式的 search() 来匹配内容.
# 下面例子中找出所有以b开头的标签,这表示<body>和<b>标签都应该被找到:
import re
for tag in soup.find_all(re.compile("^b")):
    print(tag.name)
# body
# b
# 下面代码找出所有名字中包含”t”的标签:

for tag in soup.find_all(re.compile("t")):
    print(tag.name)
# html
# title'''

# bs学习参考网址：https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/
'''
快速开始
下面的一段HTML代码将作为例子被多次用到.这是 爱丽丝梦游仙境的 的一段内容(以后内容中简称为 爱丽丝 的文档):

html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""
使用BeautifulSoup解析这段代码,能够得到一个 BeautifulSoup 的对象,并能按照标准的缩进格式的结构输出:

from bs4 import BeautifulSoup
soup = BeautifulSoup(html_doc, 'html.parser')

print(soup.prettify())
# <html>
#  <head>
#   <title>
#    The Dormouse's story
#   </title>
#  </head>
#  <body>
#   <p class="title">
#    <b>
#     The Dormouse's story
#    </b>
#   </p>
#   <p class="story">
#    Once upon a time there were three little sisters; and their names were
#    <a class="sister" href="http://example.com/elsie" id="link1">
#     Elsie
#    </a>
#    ,
#    <a class="sister" href="http://example.com/lacie" id="link2">
#     Lacie
#    </a>
#    and
#    <a class="sister" href="http://example.com/tillie" id="link2">
#     Tillie
#    </a>
#    ; and they lived at the bottom of a well.
#   </p>
#   <p class="story">
#    ...
#   </p>
#  </body>
# </html>
几个简单的浏览结构化数据的方法:

soup.title
# <title>The Dormouse's story</title>

soup.title.name
# u'title'

soup.title.string
# u'The Dormouse's story'

soup.title.parent.name
# u'head'

soup.p
# <p class="title"><b>The Dormouse's story</b></p>

soup.p['class']
# u'title'

soup.a
# <a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>

soup.find_all('a')
# [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
#  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
#  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]

soup.find(id="link3")
# <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>
从文档中找到所有<a>标签的链接:

for link in soup.find_all('a'):
    print(link.get('href'))
    # http://example.com/elsie
    # http://example.com/lacie
    # http://example.com/tillie
从文档中获取所有文字内容:

print(soup.get_text())
# The Dormouse's story
#
# The Dormouse's story
#
# Once upon a time there were three little sisters; and their names were
# Elsie,
# Lacie and
# Tillie;
# and they lived at the bottom of a well.
#
# ...
这是你想要的吗?别着急,还有更好用的
'''
