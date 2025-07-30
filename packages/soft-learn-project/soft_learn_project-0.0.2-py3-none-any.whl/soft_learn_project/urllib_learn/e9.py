import urllib.request
import urllib.parse
import ssl
ssl._create_default_https_context=ssl._create_unverified_context

url = 'https://www.runoob.com/try/py3/py3_urllib_test.php'  # 提交到表单页面
data = {'name':'RUNOOB', 'tag' : '菜鸟教程'}   # 提交数据
header = {
    'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}   #头部信息
data = urllib.parse.urlencode(data).encode('utf8')  # 对参数进行编码，解码使用 urllib.parse.urldecode
request=urllib.request.Request(url, data, header)   # 请求处理
reponse=urllib.request.urlopen(request).read()      # 读取结果
print(reponse)
# fh = open("./urllib_test_post_runoob.html","w+")    # 将文件写入到当前目录中
# fh.write(reponse)
# fh.close()
