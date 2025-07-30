import pandas as pd

"""
4.8 高级处理-合并 :merge concat 两个函数, 目的: 是把两张以上的表的数据放在一张表.
    numpy
        np.concatnate((a, b), axis=)
        水平拼接
            np.hstack()
        竖直拼接
            np.vstack()
    1）按方向拼接
        pd.concat([data1, data2], axis=1)  # axis=0 按行合并，axis=1按列合并
    2）按索引拼接
        pd.merge实现合并 # 记住merge这个函数就行了，功能最强大
        pd.merge(left, right, how="inner", on=[索引]) # 参数很多，主要就是how=? 和on=[key1,key2]
        # how=进行内连接，外连接还是左右连接，例如：内连接就是拼接后的结果只保留两个表共同的索引(由on决定)，外连接表示全部保留两个表的索引    
"""

# ### pd.merge合并  ：按照索引合并
"""
left = pd.DataFrame({'key1': ['K0', 'K0', 'K1', 'K2'],
                     'key2': ['K0', 'K1', 'K0', 'K1'],
                     'A': ['A0', 'A1', 'A2', 'A3'],
                     'B': ['B0', 'B1', 'B2', 'B3']})

right = pd.DataFrame({'key1': ['K0', 'K1', 'K1', 'K2'],
                      'key2': ['K0', 'K0', 'K0', 'K0'],
                      'C': ['C0', 'C1', 'C2', 'C3'],
                      'D': ['D0', 'D1', 'D2', 'D3']})

print(left)
print(right)
print(pd.merge(left, right, how="inner", on=["key1", "key2"]))
print(pd.merge(left, right, how="left", on=["key1", "key2"]))
print(pd.merge(left, right, how="outer", on=["key1", "key2"]))
# print(pd.merge(left, right, on='key'))
# """

# ### 4.8.1 pd.concat实现合并 ：按照方向合并
"""
stock = pd.read_csv("../../../../data/stock_day/stock_day.csv")
# print(stock)
p_change = stock["p_change"]
# print(p_change)
# 自定义分组
bins = [-100, -7, -5, -3, 0, 3, 5, 7, 100]
sr = pd.cut(p_change, bins)
# print(sr)
# print(sr.value_counts())  # 查看分组结果
# one-hot
stock_change = pd.get_dummies(sr, prefix="rise")  # 将分组好的结果转换成one-hot编码
# print(stock_change)

# 处理好的one-hot编码与原数据合并
# print(stock.head())
# print(stock_change.head())
# quit()
# print(pd.concat([stock, stock_change], axis=0))
print(pd.concat([stock, stock_change], axis=1))  # 按照行？合并
# """
