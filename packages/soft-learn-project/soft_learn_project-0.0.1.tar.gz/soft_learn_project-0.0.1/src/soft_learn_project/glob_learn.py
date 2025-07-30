import glob
import os

'''
    1.通配符'*'：零个或多个字符匹配
    2.通配符'？'：单个字符匹配
    3.通配符'[]'：范围通配符，获取一定范围的文件列表
    4.通配符'[!]':在3的基础上取非，即获取不在这个范围的文件列表
    5.通配符'**':匹配指定路径下的所有子目录和当前目录里的文件名；
'''

# 用通配符'*'获取指定目录(不包含子目录)下的所有'.txt'文件
fileLs = glob.glob(r'globMain/*.txt')
print(u"eg1:获取指定目录(不包含子目录)下的所有'.txt'文件")
for file in fileLs:
    print(file)

# 用通配符'**'，获取指定目录(包含子目录)下的所有'.txt'文件,recursive必须True
fileLs = glob.glob('globMain/**/*.txt', recursive=True)
print(os.linesep, u"eg2:获取指定目录(包含子目录)下的所有'.txt'文件")
for file in fileLs:
    print(file)

# 用通配符'*'代替子目录名
fileLs = glob.glob('globMain/*/*.txt')
print(os.linesep, u"eg3:用通配符'*'代替子目录名")
for file in fileLs:
    print(file)

# 用通配符'?'提取globMain下的globMain？.txt
fileLs = glob.glob('globMain/globMain?.txt')
print(os.linesep, u"eg4:通配符'?'提取globMain下的globMain?.txt")
for file in fileLs:
    print(file)

# 用通配符'[]'，选取文件名globMain[5-9].txt
fileLs = glob.glob('globMain/globMain[5-9].txt')
print(os.linesep, u"eg5:用通配符'[]'，选取文件名globMain[5-9].txt")
for file in fileLs:
    print(file)

# 用通配符'[!]'，选取文件名globMain[!5-9].txt
fileLs = glob.glob('globMain/globMain[!5-9].txt')
print(os.linesep, u"eg6:用通配符'[!]'，选取文件名globMain[!5-9].txt")
for file in fileLs:
    print(file)

# iglob()用迭代器逐个获取文件
files = glob.iglob('globMain/*.txt')
print(os.linesep, u"eg7:iglob()用迭代器逐个获取文件")
for file in files:
    print(file)
