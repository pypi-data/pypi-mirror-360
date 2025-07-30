import pandas as pd

"""
4.4 Pandas画图
    sr.plot()
"""

"""
data = pd.read_csv("../../stock_day/stock_day.csv")
# print(data.head())
print(data.apply(lambda x: x.max() - x.min()))  # 对每一列应用lambda函数求最大值和最小值的差
data.plot(x="high", y="low", kind="scatter")  # kind: 表示使用那五种中的哪一种图形
# plt.show()
# """