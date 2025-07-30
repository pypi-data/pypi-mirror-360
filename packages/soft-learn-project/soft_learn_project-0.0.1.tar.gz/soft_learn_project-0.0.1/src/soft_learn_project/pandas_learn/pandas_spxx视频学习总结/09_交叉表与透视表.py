import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

"""
4.9 高级处理-交叉表与透视表  目的: 是从一张表里面的数据中， 找到、探索两个变量之间的关系。
    4.9.1 交叉表与透视表什么作用
    4.9.2 使用crosstab(交叉表)实现:  计算一列数据对于另外一列数据的分组个数
        pd.crosstab(value1, value2)
    4.9.3 pivot_table
# """

# ### 4.9.2 使用crosstab(交叉表)实现 星期数据以及涨跌幅是好是坏数据
# """
# pd.crosstab(星期数据列, 涨跌幅数据列)
# 准备星期数据列
stock = pd.read_csv("../../../../data/stock_day/stock_day.csv")
# print(stock.head())
# quit()

# pandas日期类型
# print(stock.index)
date = pd.to_datetime(stock.index)
# print(type(date),date)
# quit()
date: pd.DatetimeIndex
# print(date.day)
stock["week"] = date.weekday
# print(date.weekday)
# print(stock)

# 准备涨跌幅数据列
stock["pona"] = np.where(stock["p_change"] > 0, 1, 0)
print(stock.head())
# 交叉表
data = pd.crosstab(stock["week"], stock["pona"])
print(data)

# print(data.sum(axis=1))
# data.div(data.sum(axis=1), axis=0).plot(kind="bar", stacked=True)
# plt.show()
# 透视表操作
print(stock.pivot_table(["pona"], index=["week"], aggfunc="count"))
print(stock.pivot_table(values="close", index="week", columns="pona",aggfunc="count"))
# print(stock.groupby(by=["week"])["pona"].value_counts())
# """

# pivot_table透视表
"""
np.random.seed(22)
t_dict = {
    "A": ["one", "one", "two", "three"] * 3,
    "B": ["A", "B", "C"] * 4,
    "C": ["foo", "foo", "foo", "bar", "bar", "bar"] * 2,
    "D": np.round(np.random.randn(12), 2),
    "E": np.round(np.random.randn(12), 2),
}
df = pd.DataFrame(t_dict)
print(df)
print(pd.pivot_table(df, values="D", index=["A", "B"], columns=["C"]))  # 从 df 生成数据透视表
# """

# Crosstab 交叉列表取值 https://www.cnblogs.com/rachelross/p/10468589.html
# 透视表(pivot table)是各种电子表格程序和其他数据分析软件中一种常见的数据汇总工具。它根据一个或多个键对数据进行聚合，
# DataFrame有一个pivot_table方法，此外还有一个顶级的pandas.pivot_table函数。除了能为groupby提供便利之外，pivot_table还可以添加分项小计（也叫margins）。
# 原文链接： https://blog.csdn.net/hustqb/article/details/78086394
# 总结
# 透视表pivot_table()是一种进行分组统计的函数，参数aggfunc决定统计类型；
# 交叉表crosstab()是一种特殊的pivot_table()，专用于计算分组频率。
"""
data = pd.DataFrame({'Sample': range(1, 11),
                     'Gender': ['Female', 'Male', 'Female', 'Male', 'Male', 'Male', 'Female', 'Female', 'Male',
                                'Female'],
                     'Handedness': ['Right-handed', 'Left-handed', 'Right-handed', 'Right-handed', 'Left-handed',
                                    'Right-handed', 'Right-handed', 'Left-handed', 'Right-handed', 'Right-handed']})
print(data)

# 假设我们想要根据性别和用手习惯对这段数据进行统计汇总。
# 方法一：用pivot_table
# tab1 = data.pivot_table(index='Gender', columns='Handedness', aggfunc="count", margins=True)  # 或者aggfunc=len
tab1 = pd.pivot_table(data, index="Gender", columns="Handedness", aggfunc="count")  # , margins=是否添加汇总
print(tab1)
print("*" * 50)
print(pd.pivot_table(data=data, index="Gender", columns="Handedness", aggfunc="count"))
# print(data.pivot_table(index="Gender", columns="Handedness", aggfunc="count"))
quit()
# 方法二：用crosstab
tab2 = pd.crosstab(data.Gender, data.Handedness, margins=True)
print(tab2)
# """
