# 原文链接：https://blog.csdn.net/destiny1507/article/details/100185331
# binascii模块主要用于二进制数据（byte类型数据）和ASCII的转换，通常情况不会直接使用这些功能，而是使用像UU，base64编码，或BinHex封装模块。
# 在16进制和字符串的转换过程中，主要用到了以下几个函数：
# b2a_hex(),hexlify()：返回二进制数据的16进制表现形式
# a2b_hex(),unhexlify()：返回16进制的二进制数据表现形式

"""
ASCII码就是被普遍采用的一个英文字符信息编码方案，它用8位二进制数表示各种字母和符号。
ASCII码使用7位二进制数组合来表示所有的大写和小写字母，数字0到9、标点符号，以及在美式英语中使用的特殊控制字符。
"""
# 用法
from binascii import b2a_hex, a2b_hex, hexlify, unhexlify

s = 'hello老大哥'.encode()  # 将字符串变成二进制比特流形式
b = b2a_hex(s)  # 同hexlify(s)  #二进制形式转换成16进制比特流形式
print(b)
a = a2b_hex(b)  # 同unhexlify(b) #16进制解码成字节流
print(a)
print(a.decode())  # 字节流转换成字符串
