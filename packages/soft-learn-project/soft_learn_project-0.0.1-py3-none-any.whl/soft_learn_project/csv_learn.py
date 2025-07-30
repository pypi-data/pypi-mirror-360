# 链接：https://www.jianshu.com/p/ab49aecd9db2
# python内置了csv模块用于读写csv文件，csv是一种逗号分隔符文件，是数据科学中最常见的数据存储格式之一
# 使用
import csv

# 1.写入列表数据
'''
header = ['class', 'name', 'sex', 'height', 'year']
rows = [
    [1, 'xiaoming', 'male', 168, 23],
    [1, 'xiaohong', 'female', 162, 22],
    [2, 'xiaozhang', 'female', 163, 21],
    [2, 'xiaoli', 'male', 158, 21],
]

with open('data1.csv', mode='w', newline='') as f:  # newline=" "是为了避免写入之后有空行 在windows这种使用'\r\n'的系统中，会自动在行尾加上\r
    fl = csv.writer(f)
    fl.writerow(header)  # 写入一行
    fl.writerows(rows)  # 写入多行
    # 或者用如下两行写入多行
    # for row in rows:
    #     fl.writerow(row)
print('over')
# '''

# 2. 写入字典数据 注意：列表和字典形式的数据写入是不一样的！
'''
# headers = ['class','name','sex','height','year']
rows = [
    {'class': 1, 'name': 'xiaoming', 'sex': 'male', 'height': 168, 'year': 23},
    {'class': 1, 'name': 'xiaohong', 'sex': 'female', 'height': 162, 'year': 22},
    {'class': 2, 'name': 'xiaozhang', 'sex': 'female', 'height': 163, 'year': 21},
    {'class': 2, 'name': 'xiaoli', 'sex': 'male', 'height': 158, 'year': 21},
]
headers = [k for k in rows[0]]  # 直接从字典中获取表头 或者 headers = list(rows[0].keys())

with open('data2.csv', mode='w', newline='') as f:
    fd = csv.DictWriter(f, headers)  # 写入字典需要两个参数，一个是文件对象：f，一个是字段名称：fieldnames 或(keys)
    fd.writeheader()  # 写入表头
    fd.writerows(rows)  # 写入一行字典系列数据调用writerrow方法，并传入相应字典参数，写入多行调用writerows

print('over')
# '''

# 3.csv的读取，和读取文件差不多：
"""
with open('data1.csv','r+') as f:
    f_csv = csv.reader(f)
    for row in f_csv:
        print(row)
# """

# 也可以通过pandas 读取csv， 参见pandas文档
"""
import pandas as pd
df = pd.read_csv("data1.csv")
print(df)

df.to_excel("data1.xlsx", sheet_name="mysheet1")
print("over")
"""