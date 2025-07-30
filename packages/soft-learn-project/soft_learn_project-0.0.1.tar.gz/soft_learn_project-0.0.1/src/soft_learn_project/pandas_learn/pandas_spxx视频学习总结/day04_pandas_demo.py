#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


movie = pd.read_csv("./IMDB/IMDB-Movie-Data.csv")


# In[4]:


# 1）判断是否存在NaN类型的缺失值
movie.head()


# In[6]:


import numpy as np


# In[7]:


np.any(pd.isnull(movie)) # 返回True，说明数据中存在缺失值


# In[9]:


np.all(pd.notnull(movie)) # 返回False，说明数据中存在缺失值


# In[11]:


pd.isnull(movie).any()


# In[13]:


pd.notnull(movie).all()


# In[16]:


# 2）缺失值处理
# 方法1：删除含有缺失值的样本
data1 = movie.dropna()


# In[17]:


pd.notnull(movie).all()


# In[18]:


pd.notnull(data1).all()


# In[19]:


# 方法2：替换
movie.head()


# In[20]:


# 含有缺失值的字段
# Revenue (Millions)    
# Metascore
movie["Revenue (Millions)"].fillna(movie["Revenue (Millions)"].mean(), inplace=True)
movie["Metascore"].fillna(movie["Metascore"].mean(), inplace=True)


# In[22]:


movie.head()


# In[23]:


pd.notnull(movie).all() # 缺失值已经处理完毕，不存在缺失值


# ### 不是缺失值nan，有默认标记的

# In[25]:


# 读取数据
path = "https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/breast-cancer-wisconsin.data"
name = ["Sample code number", "Clump Thickness", "Uniformity of Cell Size", "Uniformity of Cell Shape", "Marginal Adhesion", "Single Epithelial Cell Size", "Bare Nuclei", "Bland Chromatin", "Normal Nucleoli", "Mitoses", "Class"]


data = pd.read_csv(path, names=name)


# In[27]:


data.head()


# In[28]:


# 1）替换
data_new = data.replace(to_replace="?", value=np.nan)


# In[30]:


data_new.head()


# In[31]:


# 2）删除缺失值
data_new.dropna(inplace=True)


# In[33]:


data_new.isnull().any() # 全部返回False说明不存在缺失值了


# In[34]:


type(np.nan)


# ### 4.7.3 如何实现数据的离散化

# In[35]:


# 1）准备数据
data = pd.Series([165,174,160,180,159,163,192,184], index=['No1:165', 'No2:174','No3:160', 'No4:180', 'No5:159', 'No6:163', 'No7:192', 'No8:184']) 


# In[36]:


data


# In[37]:


# 2）分组
# 自动分组
sr = pd.qcut(data, 3)


# In[39]:


type(sr)


# In[40]:


sr


# In[42]:


sr.value_counts()


# In[41]:


# 3）转换成one-hot编码
pd.get_dummies(sr, prefix="height")


# In[43]:


# 自定义分组
bins = [150, 165, 180, 195]
sr = pd.cut(data, bins)


# In[44]:


sr


# In[45]:


sr.value_counts()


# In[46]:


# get_dummies
pd.get_dummies(sr, prefix="身高")


# ### 案例：股票的涨跌幅离散化

# In[47]:


# 1）读取数据
stock = pd.read_csv("./stock_day/stock_day.csv")


# In[49]:


p_change = stock["p_change"]


# In[51]:


p_change.head()


# In[52]:


# 2）分组
sr = pd.qcut(p_change, 10)


# In[54]:


sr.value_counts()


# In[55]:


# 3）离散化
pd.get_dummies(sr, prefix="涨跌幅")


# In[56]:


# 自定义分组
bins = [-100, -7, -5, -3, 0, 3, 5, 7, 100]
sr = pd.cut(p_change, bins)


# In[58]:


sr.value_counts()


# In[60]:


# one-hot
pd.get_dummies(sr, prefix="rise").head()


# In[61]:


stock_change = pd.get_dummies(sr, prefix="rise")


# In[62]:


stock_change


# ### 4.8.1 pd.concat实现合并

# In[64]:


# 处理好的one-hot编码与原数据合并
stock.head()


# In[66]:


stock_change.head()


# In[67]:


pd.concat([stock, stock_change], axis=1)


# In[69]:


pd.concat([stock, stock_change], axis=0).head()


# ### pd.merge合并

# In[70]:


left = pd.DataFrame({'key1': ['K0', 'K0', 'K1', 'K2'],
                        'key2': ['K0', 'K1', 'K0', 'K1'],
                        'A': ['A0', 'A1', 'A2', 'A3'],
                        'B': ['B0', 'B1', 'B2', 'B3']})

right = pd.DataFrame({'key1': ['K0', 'K1', 'K1', 'K2'],
                        'key2': ['K0', 'K0', 'K0', 'K0'],
                        'C': ['C0', 'C1', 'C2', 'C3'],
                        'D': ['D0', 'D1', 'D2', 'D3']})


# In[71]:


left


# In[72]:


right


# In[73]:


pd.merge(left, right, how="inner", on=["key1", "key2"])


# In[74]:


pd.merge(left, right, how="left", on=["key1", "key2"])


# In[75]:


pd.merge(left, right, how="outer", on=["key1", "key2"])


# ### 4.9.2 使用crosstab(交叉表)实现

# In[80]:


# 星期数据以及涨跌幅是好是坏数据
# pd.crosstab(星期数据列, 涨跌幅数据列)
# 准备星期数据列
stock.index


# In[81]:


# pandas日期类型
date = pd.to_datetime(stock.index)


# In[87]:


date


# In[89]:


stock["week"] = date.weekday


# In[86]:


date.weekday


# In[90]:


stock


# In[91]:


# 准备涨跌幅数据列
stock["pona"] = np.where(stock["p_change"] > 0, 1, 0)


# In[93]:


stock.head()


# In[95]:


# 交叉表
data = pd.crosstab(stock["week"], stock["pona"])


# In[96]:


data


# In[100]:


data.sum(axis=1)


# In[105]:


data.div(data.sum(axis=1), axis=0).plot(kind="bar", stacked=True)


# In[108]:


data.div(data.sum(axis=1), axis=0)


# In[107]:


# 透视表操作
stock.pivot_table(["pona"], index=["week"])


# ### 分组与聚合

# In[109]:


col =pd.DataFrame({'color': ['white','red','green','red','green'], 'object': ['pen','pencil','pencil','ashtray','pen'],'price1':[5.56,4.20,1.30,0.56,2.75],'price2':[4.75,4.12,1.60,0.75,3.15]})


# In[110]:


col


# In[113]:


# 进行分组，对颜色分组，price1进行聚合
# 用dataframe的方法进行分组
col.groupby(by="color")["price1"].max()


# In[116]:


col["price1"].groupby(col["color"]).max()


# ### 4.10.3 星巴克零售店铺数据案例

# In[117]:


# 1、准备数据
starbucks = pd.read_csv("directory.csv")


# In[119]:


starbucks.head()


# In[127]:


# 按照国家分组，求出每个国家的星巴克零售店数量
starbucks.groupby("Country").count()["Brand"].sort_values(ascending=False)[:10].plot(kind="bar", figsize=(20, 8), fontsize=40)


# In[129]:


# 假设我们加入省市一起进行分组
starbucks.groupby(by=["Country", "State/Province"]).count()


# ### 4.11 综合案例

# In[130]:


# 1、准备数据
movie = pd.read_csv("./IMDB/IMDB-Movie-Data.csv")


# In[131]:


movie


# In[133]:


# 问题1：我们想知道这些电影数据中评分的平均分，导演的人数等信息，我们应该怎么获取？
# 评分的平均分
movie["Rating"].mean()


# In[137]:


# 导演的人数
np.unique(movie["Director"]).size


# In[138]:


# 问题2：对于这一组电影数据，如果我们想rating，runtime的分布情况，应该如何呈现数据？


# In[141]:


movie["Rating"].plot(kind="hist", figsize=(20, 8))


# In[142]:


import matplotlib.pyplot as plt


# In[148]:


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

# In[149]:


movie


# In[151]:


# 先统计电影类别都有哪些
movie_genre = [i.split(",") for i in movie["Genre"]]


# In[152]:


movie_genre


# In[155]:


movie_class = np.unique([j for i in  movie_genre for j in i])


# In[157]:


len(movie_class)


# In[158]:


movie


# In[159]:


# 统计每个类别有几个电影
count = pd.DataFrame(np.zeros(shape=[1000, 20], dtype="int32"), columns=movie_class)


# In[161]:


count.head()


# In[162]:


# 计数填表
for i in range(1000):
    count.ix[i, movie_genre[i]] = 1


# In[164]:


count.head()


# In[173]:


count.sum(axis=0).sort_values(ascending=False).plot(kind="bar", figsize=(20, 9), fontsize=40, colormap="cool")


# In[ ]:




