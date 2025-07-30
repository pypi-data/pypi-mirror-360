""" 学习网址：https://www.bilibili.com/video/BV1R7411i78Y?p=59&spm_id_from=pageDriver
4.3 DataFrame运算
    算术运算
    逻辑运算
        逻辑运算符
            布尔索引
        逻辑运算函数
            query()
            isin()
    统计运算
        min max mean median var std
        np.argmax()
        np.argmin()
    自定义运算
        apply(func, axis=0)True
            func:自定义函数

    我自己的记录:
        从pandas中搜索指定字符串
"""

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

# ### 4.3.1 算术运算
"""
data = pd.read_csv("../../stock_day/stock_day.csv")
data["open"].add(3).head()
data.sub(100).head()
data["close"].sub(data["open"]).head()
# """

# ###  逻辑运算, 符号<、 >、|、 &
""" 逻辑运算的目的是为了筛选需要的数据？
data = pd.read_csv("../../stock_day/stock_day.csv")
# 例如筛选p_change > 2的日期数据
data[data["p_change"] > 2].head()
# """

# 逻辑运算函数 df.query(), df.isin()
# """
data = pd.read_csv("../../stock_day/stock_day.csv")
# 完成一个多个逻辑判断， 筛选p_change > 2并且low > 15
# data[(data["p_change"] > 2) & (data["low"] > 15)].head()  # bool索引
print(data.query("p_change > 2 & low > 15").head())   # 或者直接使用query进行逻辑判断
# 判断'turnover'是否为4.19, 2.39
print(data[data["turnover"].isin([4.19, 2.39])])
# """

# ### 4.3.3 统计运算
"""
data = pd.read_csv("../../stock_day/stock_day.csv")
# print(data.describe())
# print(data.head())
# print(data.max(axis=0))
print(data.idxmax(axis=0))  # 最大值的索引，对应于np中的np.argmax

# ### 4.3.4 累计统计函数
# data["p_change"].sort_index().cumsum().plot()  # 绘图
# plt.show()
# """

# ### 4.3.5 自定义运算:  df.apply()
"""
data = pd.read_csv("../../stock_day/stock_day.csv")
print(data.head())
print(data.apply(lambda x: x.max() - x.min()))  # 对每一列应用lambda函数求最大值和最小值的差
# print(data["volume"].max() - data["volume"].min())  # 检查上面的结果对不对
data.plot(x="high", y="low", kind="scatter")  # kind: 表示使用那五种中的哪一种图形
# plt.show()
# """

# 查找指定字符串
# df1 = df[df['主监考'].str.contains("王金龙")==True] # 查找包含字符串"王金龙"的行, 由于某些行可能为空值, 故赋值True
# df_obj[df_obj["姓名"].str.find("倪孟熠") == 0]
# --
mydata = np.array(['ab', 'ac', 'ad', 'ae'])
myserie = pd.Series(mydata)
# 查找指定字符串
print(myserie.str.find('ac'))   # 找到的结果标记为0，否则-1
print(myserie.str.contains('ac'))  # 包含
print(myserie.eq('ac'))  # 精确匹配，使用 eq 或者 ==

# 还有这个方法
"""
keywords=['iPhone','iPad','Mac','Apple']
df['关键词'].isin(keywords)
"""
