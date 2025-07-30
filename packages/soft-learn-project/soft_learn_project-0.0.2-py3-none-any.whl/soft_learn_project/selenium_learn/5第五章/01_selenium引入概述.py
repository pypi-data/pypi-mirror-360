# 能不能让我的程序连接到浏览器 . 让浏览器来完成各种复杂的操作, 我们只接受最终的结果
# selenium: 自动化测试工具
# 可以: 打开浏览器. 然后像人一样去操作浏览器
# 程序员可以从selenium中直接提取网页上的各种信息
# 环境搭建:
#     pip install selenium -i 清华源
#     下载浏览器驱动:https://npm.taobao.org/mirrors/chromedriver
# (http://chromedriver.storage.googleapis.com/index.html)
#         把解压缩的浏览器驱动 chromedriver 放在python解释器所在的文件夹
#   cp chromedriver /usr/local/bin

# 让selenium启动谷歌浏览器  用于复杂加密的网页，让浏览器去解密
from selenium.webdriver import Chrome

# 1.创建浏览器对象
web = Chrome()  # executable_path="/usr/local/bin/chromedriver"
# 2.打开一个网址
web.get("http://www.baidu.com")

print(web.title)
print(web.page_source)  # 直接拿到页面代码Elements(经过数据加载以及js执行之后的结果的html内容)
