import pandas as pd
import numpy as np
"""
1Pandas介绍
    4.1.1 Pandas介绍 - 数据处理工具
        panel + data + analysis
        panel面板数据 - 计量经济学 三维数据
    4.1.2 为什么使用Pandas
        便捷的数据处理能力
        读取文件方便: numpy 没办法读取字符串
        封装了Matplotlib、Numpy的画图和计算
    4.1.3 DataFrame
        结构：既有行索引，又有列索引的二维数组
        属性：
            shape
            index
            columns
            values: 就是获得ndarray
            T
        方法：
            head()
            tail()
        3 DataFrame索引的设置
            1）修改行列索引值
            2）重设索引
            3）设置新索引
    2 Panel
        DataFrame的容器: 已经被弃用了
    3 Series
        带索引的一维数组
        属性
            index
            values
    总结：
        DataFrame是Series的容器
        Panel是DataFrame的容器
"""

# 创建一个符合正态分布的10个股票5天的涨跌幅数据
stock_change = np.random.normal(0, 1, (10, 5))
# print(stock_change)
stock = ["股票{}".format(i) for i in range(10)]
date = pd.date_range(start="20180101", periods=5, freq="B")  # periods 添加几天，freq="B"工作日
# print(date)
# quit()
data = pd.DataFrame(stock_change, index=stock, columns=date)  # index=添加行索引，columns=添加列索引
# print(data)

# ###  DataFrame的属性
"""
data # shape (10, 5)
data.shape
data.index
data.columns
data.values
data.T
data.head(3)
data.tail(2)
# """

# ### 修改行列索引值
"""
data.head()
# data.index[2] = "股票88"   # 不能单独修改索引
stock_ = ["股票_{}".format(i) for i in range(10)]
data.index = stock_
print(data.index)
print(data)
# """

# ### 重设索引
"""
print(data.head())
print(data.reset_index(drop=False))  # 新加入一列索引
exit()
# """

# ### 设置新索引
"""
df = pd.DataFrame({'month': [1, 4, 7, 10],
                   'year': [2012, 2014, 2013, 2014],
                   'sale':[55, 40, 84, 31]})
print(df)
# 以月份设置新的索引
print(df.set_index("month", drop=True))
df["mon"] = df["month"]
print(df)
print(df.drop(columns="month"))

# 设置多个索引，以年和月份
new_df = df.set_index(["year", "month"])
print(new_df)
print(new_df.index)
print(new_df.index.names)
print(new_df.index.levels)
# """

# ### Panel  已经被弃用了
""" 
p = pd.Panel(np.arange(24).reshape(4,3,2),
                items=list('ABCD'),
                major_axis=pd.date_range('20130101', periods=3),
                minor_axis=['first', 'second'])
p
p["A"]
p["D"]
p.major_xs("2013-01-01")
p.minor_xs("first")
data
# """

# ### Series: 带索引的一维数组
"""
# print(data.head())
sr = data.iloc[1, :]
# print(sr)
# print(sr.index)
print(sr.values)
print(type(sr.values))
df1 = pd.Series(np.arange(3, 9, 2), index=["a", "b", "c"])
print(df1)
df2 = pd.Series({'red':100, 'blue':200, 'green': 500, 'yellow':1000})
print(df2)
# """