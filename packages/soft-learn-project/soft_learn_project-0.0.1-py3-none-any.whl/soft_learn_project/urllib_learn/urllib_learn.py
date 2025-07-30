# urllib 是一个收集了多个涉及 URL 的模块的包：
# urllib.request 打开和读取 URL
# urllib.error 包含 urllib.request 抛出的异常
# urllib.parse 用于解析 URL
# urllib.robotparser 用于解析 robots.txt 文件

#出现错误ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:833)
'''
url = "https://www.baidu.com" 
context = ssl._create_unverified_context() #出现错误ssl.SSLError:,关闭ssl校验即可
get = urllib.request.urlopen(url, context = context ).read()
print(get)
#或者
import ssl
ssl._create_default_https_context = ssl._create_unverified_context #取消全局验证,然后使用urllib.urlopen('url')
'''

import urllib.request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context #取消全局验证,然后使用urllib.urlopen('url')

# urllib.request 最简单的使用方式如下所示：
# import urllib.request
# url="http://www.baidu.com"
# url="https://blog.csdn.net/moonhillcity/article/details/52767999"  
# url="https://www.12306.cn/index/"
# url="https://movie.douban.com"
url = 'https://movie.douban.com/top250?start=%s&filter='
# url="https://www.runoob.com/python3/python3-stdlib.html"
headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'} ##模拟浏览器访问
# ret=urllib.request.Request(url, headers=headers)  #模拟浏览器访问,否则可能会出现'urllib.error.HTTPError: HTTP Error 418: '
# with urllib.request.urlopen(ret) as response:
#    html = response.read().decode('utf=8') #
#    print(html)

# ret=urllib.request.Request(url, headers=headers)  #模拟浏览器访问,否则可能会出现'urllib.error.HTTPError: HTTP Error 418: '
# res=urllib.request.urlopen(ret) # 返回服务器响应的类文件对象
# aa=res.read().decode('utf-8')
# print(aa)

# ----设置代理服务器
# 当一直使用一个ip去爬取同一个网站上的网页时，容易被服务器屏蔽，这个时候可以使用代理服务器
# 登录网页http://www.xicidaili.com/，可以看到很多的免费代理ip https://zhimahttp.com/?utm-source=bdtg&utm-keyword=?http083&have_open_ok=1
# 举例：使用ip地址222.185.23.130，端口6666
'''
def use_proxy(proxy_addr,url):
    import urllib.request
    proxy=urllib.request.ProxyHandler({"http":proxy_addr})
    opener=urllib.request.build_opener(proxy,urrlib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    data=urllib.request.urlopen(url).decode("utf-8")
    return data

proxy_addr="222.185.23.130:6666"
data=use_proxy(proxy_addr,"http://www.baidu.com")
'''