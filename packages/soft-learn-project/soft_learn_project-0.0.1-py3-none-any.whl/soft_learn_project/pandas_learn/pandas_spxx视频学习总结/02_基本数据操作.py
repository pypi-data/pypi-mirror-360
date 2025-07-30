import pandas as pd

"""
4.2 基本数据操作
    4.2.1 索引操作
        1）直接索引
            先列后行
        2）按名字索引
            loc
        3）按数字索引
            iloc
        4）组合索引
            数字、名字
    4.2.3 排序
        对内容排序
            dataframe
            series
        对索引排序
            dataframe
            series
"""

# ### 4.2 基本数据操作
# 索引操作,
"""
data = pd.read_csv("../../stock_day/stock_day.csv")
# print(data)

data = data.drop(["ma5", "ma10", "ma20", "v_ma5", "v_ma10", "v_ma20"], axis=1)  # 去掉[]中的一些字段
# print(data)

# stock_change = np.random.normal(0, 1, (10, 5))
# print(stock_change[1, 1]) # 这里是ndarray类型的索引方式，可以与Dataframe类型索引方式对比

# data[1, 0] 不能直接进行数字索引
print(data.head())
print(data["open"]["2018-02-26"])  # 必须先列后行 # data["2018-02-26"]["open"] 就会发生错误
print(data.loc["2018-02-26"]["open"])
print(data.loc["2018-02-26", "open"])  # 这是先行后列
print(data.iloc[1, 0])
# 获取行第1天到第4天，['open', 'close', 'high', 'low']这个四个指标的结果
# data.ix[:4, ['open', 'close', 'high', 'low']]  # 这种方法已经被弃用了
# """

# ### 4.2.2 赋值操作
"""
data = pd.read_csv("../../stock_day/stock_day.csv")
data.open = 100
data.iloc[1, 0] = 222
data.head()
# """

# ### 4.2.3 排序
# """
# 对dataframe排序
data = pd.read_csv("../../stock_day/stock_day.csv")
print(data.sort_values(by=["high", "p_change"],
      ascending=False).head())  # by: 对多列的值进行排序
print(data.sort_index().head())  # 对索引排序

# 对serias 排序
sr = data["price_change"]
# print(sr.sort_values(ascending=False).head())  # 对值排序
# print(sr.sort_index().head())  # 对索引排序
# """
