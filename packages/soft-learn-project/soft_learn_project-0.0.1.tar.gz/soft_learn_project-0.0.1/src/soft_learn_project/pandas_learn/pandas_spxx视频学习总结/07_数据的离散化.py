"""
4.7 高级处理-数据离散化
    性别 年龄
A    1   23
B    2   30
C    1   18
    物种 毛发
A    1
B    2
C    3
    男 女 年龄
A   1  0  23
B   0  1  30
C   1  0  18

    狗  猪  老鼠 毛发
A   1   0   0   2
B   0   1   0   1
C   0   0   1   1
one-hot编码&哑变量
4.7.1 什么是数据的离散化  将数值连续的数据分成离散的几个组
    原始的身高数据：165，174，160，180，159，163，192，184
4.7.2 为什么要离散化
4.7.3 如何实现数据的离散化
    1）分组
        自动分组sr=pd.qcut(data, bins)
        自定义分组sr=pd.cut(data, [])
    2）将分组好的结果转换成one-hot编码
        pd.get_dummies(sr, prefix=)    
"""
import pandas as pd

# ### 4.7.3 如何实现数据的离散化 pd.qcut/cut pd.get_dumies()
"""
# 1）准备数据
data = pd.Series([165, 174, 160, 180, 159, 163, 192, 184],
                 index=['No1:165', 'No2:174', 'No3:160', 'No4:180', 'No5:159', 'No6:163', 'No7:192', 'No8:184'])
print(data)
# 2）分组
# 自动分组
sr = pd.qcut(data, 3)  # 分组后仍然是Series
# print(type(sr))
# print(sr)
print(sr.value_counts())

# 3）转换成one-hot编码
print(pd.get_dummies(sr, prefix="身高"))  # prefix="height"分组名前缀

# 自定义分组
bins = [150, 165, 180, 195]
sr = pd.cut(data, bins)
# print(sr)
# print(sr.value_counts())

# get_dummies
print(pd.get_dummies(sr, prefix="身高"))
# """

# ### 案例：股票的涨跌幅离散化
"""
# 1）读取数据
stock = pd.read_csv("../../../../data/stock_day/stock_day.csv")
p_change = stock["p_change"]
# print(p_change.head())
# 2）分组: 这几行是自动分组并进行离散化
# sr = pd.qcut(p_change, 10)
# print(sr.value_counts())
# 3）离散化
# print(pd.get_dummies(sr, prefix="涨跌幅"))

# 自定义分组
bins = [-100, -7, -5, -3, 0, 3, 5, 7, 100]
sr = pd.cut(p_change, bins)
print(sr.value_counts())  # 查看分组结果
# one-hot
print(pd.get_dummies(sr, prefix="rise").head())
stock_change = pd.get_dummies(sr, prefix="rise") # 将分组好的结果转换成one-hot编码
print(stock_change)
# """

