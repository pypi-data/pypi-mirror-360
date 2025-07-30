#处理get请求，不传data，则为get请求

import urllib
from urllib.request import urlopen
from urllib.parse import urlencode

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# url='https://www.baidu.com/login'
url="https://www.runoob.com/try/py3/py3_urllib_test.php"
# data={"username":"admin","password":123456}
data={"name":"admin","tag":123456}
req_data=urlencode(data)#将字典类型的请求数据转变为url编码
res=urlopen(url+'?'+req_data)#通过urlopen方法访问拼接好的url
# print(res)
res=res.read().decode()#read()方法是读取返回数据内容，decode是转换返回数据的bytes格式为str
print(res)
#处理post请求,如果传了data，则为post请求
