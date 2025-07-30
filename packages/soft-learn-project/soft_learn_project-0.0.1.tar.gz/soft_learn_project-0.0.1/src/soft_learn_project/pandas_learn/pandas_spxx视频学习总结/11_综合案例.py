import pandas as pd
import numpy as np

# ### 4.11 综合案例
# """
# 1、准备数据
movie = pd.read_csv("/Users/wangjinlong/my_linux/soft_learn/python3_learn/mylearn/Python_data_mining数据挖掘基础教程资料/data/IMDB/IMDB-Movie-Data.csv")
print(movie)
# 问题1：我们想知道这些电影数据中评分的平均分，导演的人数等信息，我们应该怎么获取？
# 评分的平均分
movie["Rating"].mean()
# 导演的人数
np.unique(movie["Director"]).size

# 问题2：对于这一组电影数据，如果我们想rating，runtime的分布情况，应该如何呈现数据？
movie["Rating"].plot(kind="hist", figsize=(20, 8))
import matplotlib.pyplot as plt

# 1、创建画布
plt.figure(figsize=(20, 8), dpi=80)
# 2、绘制直方图
plt.hist(movie["Rating"], 20)
# 修改刻度
plt.xticks(np.linspace(movie["Rating"].min(), movie["Rating"].max(), 21))
# 添加网格
plt.grid(linestyle="--", alpha=0.5)
# 3、显示图像
plt.show()
# ### 问题3：对于这一组电影数据，如果我们希望统计电影分类(genre)的情况，应该如何处理数据？
# movie
# 先统计电影类别都有哪些
movie_genre = [i.split(",") for i in movie["Genre"]]
movie_genre
movie_class = np.unique([j for i in movie_genre for j in i])
len(movie_class)
movie
# 统计每个类别有几个电影
count = pd.DataFrame(np.zeros(shape=[1000, 20], dtype="int32"), columns=movie_class)
count.head()
# 计数填表
for i in range(1000):
    count.head()
count.sum(axis=0).sort_values(ascending=False).plot(kind="bar", figsize=(20, 9), fontsize=40, colormap="cool")
# """

