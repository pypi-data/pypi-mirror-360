
import pandas as pd

"""
4.6 高级处理-缺失值处理
    1）如何进行缺失值处理
        两种思路：
            1）删除含有缺失值的样本
            2）替换/插补
        4.6.1 如何处理nan
            1）判断数据中是否存在NaN
                pd.isnull(df)
                pd.notnull(df)
            2）删除含有缺失值的样本
                df.dropna(inplace=False)
               替换/插补
                df.fillna(value, inplace=False)
         4.6.2 不是缺失值nan，有默认标记的
            1）替换 ？-> np.nan
                df.replace(to_replace="?", value=np.nan)
            2）处理np.nan缺失值的步骤
    2）缺失值处理实例
# """

movie = pd.read_csv("../../../../data/IMDB/IMDB-Movie-Data.csv")
# print(movie)

# 1）判断是否存在NaN类型的缺失值
"""
print(movie.head())
np.any(pd.isnull(movie))  # 返回True，说明数据中存在缺失值
np.all(pd.notnull(movie))  # 返回False，说明数据中存在缺失值
pd.isnull(movie).any()
pd.notnull(movie).all()
# """

# 2）缺失值处理
"""
# 方法1：删除含有缺失值的样本
data1 = movie.dropna()
pd.notnull(movie).all()
pd.notnull(data1).all()
# 方法2：替换
movie.head()
# 含有缺失值的字段
# Revenue (Millions)
# Metascore
movie["Revenue (Millions)"].fillna(movie["Revenue (Millions)"].mean(), inplace=True)
movie["Metascore"].fillna(movie["Metascore"].mean(), inplace=True)
movie.head()
pd.notnull(movie).all()  # 缺失值已经处理完毕，不存在缺失值
# """

# ### 不是缺失值nan，有默认标记的
"""
# 读取数据
path = "https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/breast-cancer-wisconsin.data"
name = ["Sample code number", "Clump Thickness", "Uniformity of Cell Size", "Uniformity of Cell Shape",
        "Marginal Adhesion", "Single Epithelial Cell Size", "Bare Nuclei", "Bland Chromatin", "Normal Nucleoli",
        "Mitoses", "Class"]
data = pd.read_csv(path, names=name)
data.head()

# 1）替换
data_new = data.replace(to_replace="?", value=np.nan)
print(data_new.head())
# 2）删除缺失值
data_new.dropna(inplace=True)
print(data_new.isnull().any())  # 全部返回False说明不存在缺失值了
print(type(np.nan))
# """
