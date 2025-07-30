# base64模块 :这是一种编码和解码的方式的模块
# https://www.cnblogs.com/longwhite/p/10397707.html
# Base64就是一种基于64个可打印字符来表示二进制数据的方法。共包括a-z、A-Z、0-9、/、+共64个字符，这种编码模式用6个位表示一个字节。
# 原数据字符串字节的总位数如果数据字节数不是3的倍数，就会在原数据后添加1个或2个零值然后在编码后的字符串后添加1个或2个‘=’。故事实上总共由65个字符组成。

# base64模块真正用的上的方法只有8个，他们8个可以两两分为4组：
# encode,decode一组，专门用来编码和解码文件的,也可以StringIO里的数据做编解码；
# encodestring,decodestring一组，专门用来编码和解码字符串；
# b64encode和b64decode一组，用来编码和解码字符串，并且有一个替换符号字符的功能；
# urlsafe_b64encode和urlsafe_b64decode一组，这个就是用来专门对url进行base64编解码的。

# 对字符串操作
# """
import base64

# 编码与解码的处理对象是byte，故对原数据要先编码，使原本的str类型变成byte，解码后直接输出来的是byte对象，故要解码成str对象。
s = 'hello world!'
st = s.encode()  # 默认以utf8编码, 编码成字节
print(st)
print(st.decode())  # 把utf-8编码的字节，解码成字符串

res = base64.b64encode(st)  # 把字节st通过b64进行编码，得到的是编码后字节，该方法的对象必须是字节  #base64.encodebytes(st) 效果一样
# print(res)
# print(res.decode())  # 默认以utf8解码编码字节生成字符串
# print(base64.b64decode(res))  # 把编码的结果进行解码，解码成字节
# print(base64.b64decode(res).decode())  # 把b64解码后的字节，再以utf-8解码成字符串


# 将url编码成base64
url = "https://www.cnblogs.com/songzhixue/?wd=周杰伦"
bytes_url = url.encode("utf-8")  # 想将字符串转编码成base64,要先将字符串转换成二进制数据
str_url = base64.b64encode(bytes_url)  # 被编码的参数必须是二进制数据
print(str_url)
# 将base64解码成字符串
str_url = base64.b64decode(str_url).decode("utf-8")
print(str_url)
# """


# encode和code：对文件操作，有两个参数，一个是input，一个是output。
"""
# 我还没测试成功，以后再说
import base64
import io

st = "hello world!"
f = io.StringIO()  # 创建文件
out1 = io.StringIO()
out2 = io.StringIO()
f.write(st)
f.seek(0)
base64.encode(f, out1)
# base64.encode(f, out1)
# print(out1.getvalue())
# out1.seek(0)
# base64.decode(out1, out2)
# print(out2.getvalue())
"""

"""
# 位 bit
# 一个位就代表一个0或1（即二进制），数据传输大多是以“位”（bit，又名“比特”）为单位

# 字节 Byte
# 一个字节存储8位无符号数，储存的数值范围为0-255。字节（Byte）是计算机信息技术用于计量存储容量的一种计量单位，
# 数据存储是以“字节”（Byte）为单位，每8个位组成一个字节（Byte，简写为B），是最小一级的信息单位。
# 一个字节相当于一个字符 ASCII？

# 字（Word）
# 字通常分为若干个字节。在存储器中，通常每个单元存储一个字。因此每个字都是可以寻址的。
# 在计算机中，一串数码作为一个整体来处理或运算的，称为一个计算机字，简称字。

# 字长
# 计算机的每个字所包含的位数称为字长，计算的字长是指它一次可处理的二进制数字的数目。
# 一般地，大型计算机的字长为32-64位，小型计算机为12-32位，而微型计算机为4-16位。字长是衡量计算机性能的一个重要因素 [5]  。
"""