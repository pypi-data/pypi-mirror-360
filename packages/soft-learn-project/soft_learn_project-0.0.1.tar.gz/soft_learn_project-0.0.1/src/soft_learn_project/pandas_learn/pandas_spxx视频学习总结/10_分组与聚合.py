import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

"""
4.10 高级处理-分组与聚合
    4.10.1 什么是分组与聚合 
    4.10.2 分组与聚合API
        dataframe
        sr
# """

# ### 分组与聚合: # 根据分组字段，将分析对象划分成不同的部分，以对比分析各组之间差异性的分析方法；
# """
col = pd.DataFrame(
    {'color': ['white', 'red', 'green', 'red', 'green'], 'object': ['pen', 'pencil', 'pencil', 'ashtray', 'pen'],
     'price1': [5.56, 4.20, 1.30, 0.56, 2.75], 'price2': [4.75, 4.12, 1.60, 0.75, 3.15]})
print(col)
# 进行分组，对颜色分组，price1进行聚合
# 用dataframe的方法进行分组
print(col.groupby(by="color")["price1"].max())  # by=按照哪一个列进行分组
# 用serias的方法进行分组
print(col["price1"].groupby(col["color"]).max())
# """

# ### 4.10.3 星巴克零售店铺数据案例
"""
# 1、准备数据
starbucks = pd.read_csv("../../../../data/directory.csv")
print(starbucks.head())
# 按照国家分组，求出每个国家的星巴克零售店数量
starbucks.groupby("Country").count()["Brand"].sort_values(ascending=False)[:10].plot(kind="bar", figsize=(10, 5),
                                                                                     fontsize=20)
plt.show()
# 假设我们加入省市一起进行分组
print(starbucks.groupby(by=["Country", "State/Province"]).count())
# print(starbucks.groupby(by=["Country", "State/Province"]).agg('count'))  # 和上面的结果一样
# """
