import urllib.request 

encode_url = urllib.request.quote("https://www.runoob.com/")  # 编码
print(encode_url)

unencode_url = urllib.request.unquote(encode_url)    # 解码
print(unencode_url)
