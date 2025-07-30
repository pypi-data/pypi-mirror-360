# https://www.cnblogs.com/niuu/p/10107212.html
# 密码学中的高级加密标准（Advanced Encryption Standard，AES） #AES加密方式有五种：ECB, CBC, CTR, CFB, OFB
# 从安全性角度推荐CBC加密方法，本文介绍了CBC,ECB两种加密方法的python实现
# python 在 Windows下使用AES时要安装的是pycryptodome 模块   pip install pycryptodome
# python 在 Linux下使用AES时要安装的是pycrypto模块   pip install pycrypto
# CBC加密需要一个十六位的key(密钥)和一个十六位iv(偏移量)
# ECB加密不需要iv, 即没有偏移量

# AES CBC 加密的python实现
from Crypto.Cipher import AES  # pip install pycryptodome
from binascii import b2a_hex, a2b_hex


# def add_to_16(par):
#     par = par.encode()  # 先将字符串类型数据，按照默认的'utf-8'转换成字节型数据
#     while len(par) % 16 != 0:  # 对字节型数据进行长度判断, 如果字节型数据长度不是16倍整数就进行补充
#         par += b'\x00'
#     return par

def add_to_16(data):
    pad = 16 - len(data) % 16
    data += b'\x00'.decode() * pad
    return str(data).encode()

text = 'abc加密的内容eof测试用'
# text = {
#     "csrf_token": "",
#     "cursor": "-1",
#     "offset": "0",
#     "orderType": "1",
#     "pageNo": "1",
#     "pageSize": "20",
#     "rid": "R_SO_4_1325905146",
#     "threadId": "R_SO_4_1325905146",
# }
# text=str(text)

# 加密
key = '9999999999999999'.encode('utf-8')
mode = AES.MODE_CBC
iv = b'qqqqqqqqqqqqqqqq'
text = add_to_16(text)
aes = AES.new(key, mode, iv)  # 可以理解为创建加密器
cipher_text = aes.encrypt(text)  # 进行加密
print(cipher_text)
# print(b2a_hex(cipher_text))  # 因为AES加密后的字符串不一定是ascii字符集的，输出保存可能存在问题，所以这里转为16进制字符串

# 解密
key = '9999999999999999'.encode('utf-8')
iv = b'qqqqqqqqqqqqqqqq'  # iv = ('q' * 16).encode()  # 偏移量
mode = AES.MODE_CBC
aes = AES.new(key, mode, iv)  # 加密器在在解密的时候需要重新建立，而不能使用加密时的加密器
# aes = AES.new(key=key, iv=iv, mode=mode) # 也可以通过这种方式
plain_text = aes.decrypt(cipher_text)
print(plain_text)  # 显示解密后的字节
print(plain_text.decode().rstrip('\x00'))  # 解密后，去掉补足的空格用strip() 去掉
# plain_text = aes.decrypt(a2b_hex(cipher_text))


# 下面是建立函数的方式
"""
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


# 如果text不足16位的倍数就用空格补足为16位
def add_to_16(text):
    if len(text.encode('utf-8')) % 16:
        add = 16 - (len(text.encode('utf-8')) % 16)
    else:
        add = 0
    text = text + ('\0' * add)
    return text.encode('utf-8')


# 加密函数
def encrypt(text):
    key = '9999999999999999'.encode('utf-8')
    mode = AES.MODE_CBC
    iv = b'qqqqqqqqqqqqqqqq'
    text = add_to_16(text)
    cryptos = AES.new(key, mode, iv)
    cipher_text = cryptos.encrypt(text)
    # 因为AES加密后的字符串不一定是ascii字符集的，输出保存可能存在问题，所以这里转为16进制字符串
    return b2a_hex(cipher_text)


# 解密后，去掉补足的空格用strip() 去掉
def decrypt(text):
    key = '9999999999999999'.encode('utf-8')
    iv = b'qqqqqqqqqqqqqqqq'
    mode = AES.MODE_CBC
    cryptos = AES.new(key, mode, iv)
    plain_text = cryptos.decrypt(a2b_hex(text))
    return bytes.decode(plain_text).rstrip('\0')


if __name__ == '__main__':
    e = encrypt("hello world张三")  # 加密
    d = decrypt(e)  # 解密
    print("加密:", e)
    print("解密:", d)
"""
