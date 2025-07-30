import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize
import sklearn
import sklearn.cluster
import sklearn.datasets
import sklearn.decomposition
import sklearn.ensemble
import sklearn.feature_extraction
import sklearn.feature_selection
import sklearn.linear_model
import sklearn.metrics
import sklearn.model_selection
import sklearn.naive_bayes
import sklearn.neighbors
import sklearn.preprocessing
import sklearn.tree
import sklearn.utils
import jieba
import scipy.stats
import os
import joblib
from py_package_learn.functools_learn import functoolsLearn


class SklearnLearn():
  def __init__(self) -> None:
    """Scikit-learn简介  https://blog.csdn.net/asdfghjop/article/details/120978059
    # 第三方模块，对机器学习的算法进行了封装，包括回归、降维、分类和聚类四大机器学习方法。是Scipy模块的扩展，建立在Numpy和Matplotlib基础上，是简单高效的数据挖掘和数据分析工具。

    #  学习流程
    1. 入门
    2. 实战类书籍
    3. 书籍
      * 机器学习--周志华 西瓜书
      * 统计学习方法  李航
      * 深度学习 -- 花书

    # 机器学习库与框架
    * tensenflow
    * torch <-- 前身 chainner

    主要学习网址
    [1](https://blog.csdn.net/qq_39236499/article/details/115723947?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522163897332216780271547819%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fall.%2522%257D&request_id=163897332216780271547819&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_ecpm_v1~rank_v31_ecpm-3-115723947.first_rank_v2_pc_rank_v29&utm_term=%E9%BB%91%E9%A9%AC%E7%A8%8B%E5%BA%8F%E5%91%98---%E4%B8%89%E5%A4%A9%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8Python%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%EF%BC%88%E7%AC%AC%E4%B8%80%E5%A4%A9%EF%BC%89&spm=1018.2226.3001.4187)
    [2](https://blog.csdn.net/qq_39236499/article/details/115950283?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522163897332216780271912944%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=163897332216780271912944&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-2-115950283.first_rank_v2_pc_rank_v29&utm_term=%E9%BB%91%E9%A9%AC%E7%A8%8B%E5%BA%8F%E5%91%98---%E4%B8%89%E5%A4%A9%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8Python%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%EF%BC%88%E7%AC%AC%E4%B8%80%E5%A4%A9%EF%BC%89&spm=1018.2226.3001.4187)
    [3](https://blog.csdn.net/qq_39236499/article/details/115960087?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522163897332216780271912944%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=163897332216780271912944&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-1-115960087.first_rank_v2_pc_rank_v29&utm_term=%E9%BB%91%E9%A9%AC%E7%A8%8B%E5%BA%8F%E5%91%98---%E4%B8%89%E5%A4%A9%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8Python%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%EF%BC%88%E7%AC%AC%E4%B8%80%E5%A4%A9%EF%BC%89&spm=1018.2226.3001.4187)

    # 视频网址
    [bilibili](https://www.bilibili.com/video/BV1nt411r7tj?p=14&spm_id_from=pageDriver)

    # 其他参考
    [3天入门Python机器学习（黑马程序员）](https://blog.csdn.net/weixin_44517301/article/details/88405939)

    [第二天](https://blog.csdn.net/qq_39236499/article/details/115950283?spm=1001.2101.3001.6650.12&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7Edefault-12.nonecase&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7Edefault-12.nonecase)

    [网址1](https://blog.csdn.net/xiaotian127/article/details/86756402?spm=1001.2101.3001.6650.14&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromBaidu%7Edefault-14.nonecase&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromBaidu%7Edefault-14.nonecase)

    """
    pass

  def install(self):
    """
    conda install scikit-learn
    """
    pass


class FeatureExtraction():
  def __init__(self) -> None:
    """特征抽取

    将字典, 文本 等抽取为特征
    """
    pass

  def DictVectorizer(self):
    # 字典特征抽取 转换成one-hot 编码  应用场景: 特征当中存在的类别信息都需要转换成one-hot编码
    data = [{'city': '北京', 'temperature': 100}, {'city': '上海',
                                                 'temperature': 60}, {'city': '深圳', 'temperature': 30}]

    # 1、实例化一个转换器类
    transfer = sklearn.feature_extraction.DictVectorizer(sparse=True)
    # 2、调用fit_transform()
    data_new = transfer.fit_transform(data)
    print("data_new:\n", data_new.toarray(), type(data_new))
    # 获取特征名，transfer的一个方法
    print("特征名字：\n", transfer.get_feature_names_out())

  def CountVecotrizer(self):
    # 文本特征抽取
    data = ["life is short,i like like python",
            "life is too long,i dislike python"]
    # 1、实例化一个转换器类
    transfer = sklearn.feature_extraction.text.CountVectorizer(stop_words=[
                                                               "is", "too"])
    # 2、调用fit_transform
    data_new = transfer.fit_transform(data)
    # print(type(data_new))  # 通过查看数据类型然后标记类型，之后可以使用类型对象的方法，也就是csr_matrix的toarray()方法
    print(data_new)
    print("data_new:\n", data_new.toarray())  # 将稀疏矩阵转化为一般矩阵
    print("特征名字：\n", transfer.get_feature_names_out())

  def cut_word(self, text):
    """
    jieba.cut() # 可以将字符串分词为带空格的字符串，返回的是迭代器
    作用就是将字符串进行分词
    进行中文分词："我爱北京天安门" --> "我 爱 北京 天安门"
    :param text:
    :return:
    """
    return " ".join(list(jieba.cut(text)))

  def CountVecotrizer_chinese_example(self):
    # 将中文文本进行分词
    data = ["一种还是一种今天很残酷，明天更残酷，后天很美好，但绝对大部分是死在明天晚上，所以每个人不要放弃今天。",
            "我们看到的从很远星系来的光是在几百万年之前发出的，这样当我们看到宇宙时，我们是在看它的过去。",
            "如果只用一种方式了解某样事物，你就不会真正了解它。了解事物真正含义的秘密取决于如何将其与我们所了解的事物相联系。"]
    data_new = []
    for sent in data:
      data_new.append(self.cut_word(sent))

    # 1、实例化一个转换器类， CountVectorizer:计算样本特征词出现的个数
    transfer = sklearn.feature_extraction.text.CountVectorizer(stop_words=[
                                                               "一种", "所以"])
    # 2、调用fit_transform
    data_final = transfer.fit_transform(data_new)
    # print("data_new:\n", data_final.toarray())
    # print("特征名字：\n", transfer.get_feature_names_out())
    return transfer, data_final

  def CountVecotrizer_chinese(self, str_list=['xx']):
    # 将中文文本进行分词
    data_new = []
    for sent in str_list:
      data_new.append(self.cut_word(sent))
    # 1、实例化一个转换器类， CountVectorizer:计算样本特征词出现的个数
    transfer = sklearn.feature_extraction.text.CountVectorizer(stop_words=[
                                                               "一种", "所以"])
    # 2、调用fit_transform
    data_final = transfer.fit_transform(data_new)
    df = pd.DataFrame(data={'frequency': data_final.toarray().flatten()},
                      index=transfer.get_feature_names_out())
    # print("data_new:\n", data_final.toarray())
    # print("特征名字：\n", transfer.get_feature_names_out())
    df = df.sort_values(by='frequency',ascending=False).head(10)
    return df

  def TfidfVectorizer(self):
    """
    用TF-IDF的方法进行文本特征抽取
    tf: term frequency 词频  count(A词)/count(all词)
    idf: 逆向文档词频  log10 (总文章数/除以出现词语的文章数)
    tfidf: tf * idf
    例子：
    1000篇文章
    100篇文章含有"非常"
    10篇文章含有"经济"
    文章A和B都含有总共200个词，其中文章A含有20个"非常"， 文章B含有20个"经济"
    文章A的"非常"： tf = 20/200=0.1   idf = lg(1000/100) = 1  tfidf =0.1*1=0.1
    文章B的"经济"： tf = 20/200=0.1   idf = log(1000/10) = 2  tfidf =0.1*2=0.2
    文章B中的"经济"tfidf更大


    Returns: transfer, data_final
        _type_: _description_
    """

    # 将中文文本进行分词
    data = ["一种还是一种今天很残酷，明天更残酷，后天很美好，但绝对大部分是死在明天晚上，所以每个人不要放弃今天。",
            "我们看到的从很远星系来的光是在几百万年之前发出的，这样当我们看到宇宙时，我们是在看它的过去。",
            "如果只用一种方式了解某样事物，你就不会真正了解它。了解事物真正含义的秘密取决于如何将其与我们所了解的事物相联系。"]

    data_new = []
    for sent in data:
      data_new.append(self.cut_word(sent))

    # 1、实例化一个转换器类
    transfer = sklearn.feature_extraction.text.TfidfVectorizer(stop_words=[
                                                               "一种", "所以"])

    # 2、调用fit_transform
    data_final = transfer.fit_transform(data_new)  # 返回sparse矩阵
    # print("data_new:\n", data_final.toarray())  # 给出的是每个词语的tfidf值
    # print("特征名字：\n", transfer.get_feature_names_out())

    return transfer, data_final


class Preprocessing():
  def __init__(self) -> None:
    """特征预处理
    特征预处理概念：通过一些转换函数将特征数据转换成更加适合算法模型的特征数据的过程。包含归一化和标准化两种转换函数
    为什么要做特征预处理？特征的单位不同数值也不同会导致算法模型不能很好的学习数值较小的特征
    归一化： 会受到异常值的影响，通用性不强，最好使用通用的标准化方法
    """
    pass

  def MinMaxScaler(self):
    # 1、获取数据
    fname = "/Users/wangjinlong/my_linux/soft_learn/py_package_learn/sklearn_learn/data/dating.txt"
    data: pd.DataFrame = pd.read_csv(fname)
    data = data.iloc[:, :3]
    # print("data:\n", data.head())
    # 2、实例化一个转换器类
    transfer = sklearn.preprocessing.MinMaxScaler(feature_range=(0, 1))
    # 3、调用fit_transform
    data_new: np.ndarray = transfer.fit_transform(data)
    # print("data_new:\n", data_new, type(data_new))

    return transfer, data_new

  def StandardScaler(self):
    # 1、获取数据
    fname = "/Users/wangjinlong/my_linux/soft_learn/py_package_learn/sklearn_learn/data/dating.txt"
    data: pd.DataFrame = pd.read_csv(fname)
    data = data.iloc[:, :3]
    # 2、实例化一个转换器类
    transfer = sklearn.preprocessing.StandardScaler()
    # 3、调用fit_transform
    data_new: np.ndarray = transfer.fit_transform(data)
    # print("data_new:\n", data_new, type(data_new))
    return transfer, data_new

  def PolynomialFeatures(self, features,
                         degree=2):
    """
    可以用于线性模型,非线性函数的拟合
    假设我们有一个简单的数据集，包含两个特征，我们想要生成到二次方的多项式特征。
    degree=1 表示线性特征（实际上是原始特征），degree=2 会添加二次特征（如平方和乘积），以此类推
    X = np.array([[1, 2], [3, 4], [5, 6]]) 
    X_poly:
    [[ 1.  1.  2.  1.  2.  4.]
    [ 1.  3.  4.  9. 12. 16.]
    [ 1.  5.  6. 25. 30. 36.]]
    每一行代表一个样本，列依次是 1（截距项）、x1、x2、x1^2、x1*x2、x2^2。
    注意事项
    使用多项式特征时要小心过拟合，因为增加特征的数量通常会增加模型的复杂度。
    可以使用 include_bias=False 参数来排除常数项（即截距项）。
    如果数据已经标准化（即特征缩放到相同的尺度），那么在使用多项式特征之前进行标准化通常是一个好主意，因为多项式特征会放大数据的尺度差异。
    PolynomialFeatures 生成的特征矩阵可能包含大量特征，特别是当特征的数量和多项式的度数较高时。这可能会导致计算成本显著增加。

    Args:
        features (_type_): _description_
        degree (int, optional): _description_. Defaults to 2.

    Returns: features_poly
        _type_: _description_
    """
    # 创建 PolynomialFeatures 实例，指定多项式的度数为 2
    poly = sklearn.preprocessing.PolynomialFeatures(degree=degree)
    # 拟合和转换数据
    features_poly = poly.fit_transform(features)

    return features_poly

  def PolynomialFeatures_example(self):
    # 示例数据
    X = np.array([[1, 2], [3, 4], [5, 6]])

    # 创建 PolynomialFeatures 实例，指定多项式的度数为 2
    poly = sklearn.preprocessing.PolynomialFeatures(degree=2)
    # 拟合和转换数据
    X_poly = poly.fit_transform(X)

    print(X_poly)
    pass


class FeatureSelection():
  def __init__(self) -> None:
    """低方差过滤和相关系数
    """
    pass

  def VarianceThreshold():
    """
    过滤低方差特征和相关系数法
    :return:
    """
    # 1、获取数据
    data = pd.read_csv(
        "/Users/wangjinlong/my_linux/soft_learn/py_package_learn/sklearn_learn/data/factor_returns.csv")
    data: pd.DataFrame = data.iloc[:, 1:-2]
    # 2、实例化一个转换器类
    transfer = sklearn.feature_selection.VarianceThreshold(
        threshold=10)  # 去除方差小于10的特征
    # 3、调用fit_transform # 获得的data_new 就是过滤低方差特征之后的特征数据
    data_new: np.ndarray = transfer.fit_transform(data)
    # print("data_new:\n", data_new)
    # print("data_new形状", data_new.shape)
    # print(data.columns)
    return transfer, data_new

  def CorrelationCoeffcient(self):
    """
    当确定两个特征相关性比较高，对特征如何处理？
    1) 舍去一个
    2) 加权求和获得一个新的特征
    3) 主成分分析，自动去掉相关性比较强的特征
    """
    # 1、获取数据
    data = pd.read_csv(
        "/Users/wangjinlong/my_linux/soft_learn/py_package_learn/sklearn_learn/data/factor_returns.csv")
    data: pd.DataFrame = data.iloc[:, 1:-2]
    # scipy.stats 中的函数来计算某两个变量之间的相关系数  -1 < r<1  正相关，负相关
    # 一般可按三级划分：|r|<0.4 低相关，0.4<=|r|<0.7 为显著性相关，0.7<=|r| <1 为高度线性相关
    # 返回的是个数组，第一个为相关系数， 第二个为p-value表示显著水平,越小越好
    r1 = scipy.stats.pearsonr(data["pe_ratio"], data["pb_ratio"])
    print("相关系数：\n", r1)
    r2 = scipy.stats.pearsonr(data['revenue'], data['total_expense'])
    print("revenue与total_expense之间的相关性：\n", r2)

    # 画图显示两列数据的相关性
    plt.figure(figsize=(8, 6), dpi=100)
    plt.scatter(data["revenue"], data["total_expense"])
    plt.show()
    pass


class Decomposition():
  def __init__(self) -> None:
    """特征工程 中的降维
    """
    pass

  def pca(self):
    """PCA降维: 在此过程可能会舍去原有的一些特征，创造新的特征，尽可能降低原有数据的维数，
    """
    data = [[2, 8, 4, 5], [6, 3, 0, 8], [5, 4, 9, 1]]
    # 1、实例化一个转换器类
    # n_components= 小数：表示保留多少信息，整数：减少到多少个特征
    transfer = sklearn.decomposition.PCA(n_components=0.95)
    # 2、调用fit_transform
    data_new = transfer.fit_transform(data)  # 返回降维后的数组
    # print(type(data_new))
    # print("data_new:\n", data_new)
    return transfer, data_new

  def pca_instacart(self):
    data = GetData().get_data_instacart()
    # 实例化一个转换器
    transfer = sklearn.decomposition.PCA(n_components=0.8)
    data_new = transfer.fit_transform(data)
    return transfer, data_new


class ModelSelection():
  def __init__(self) -> None:
    """模型选择与调优
    数据集的划分 和 网格搜索 CV 

    什么是交叉验证(cross validation)
    超参数搜索-网格搜索(Grid Search)
    """
    pass

  def train_test_split(self, features, target):
    """划分数据集

    Args:
        features (_type_): _description_
        target (_type_): _description_

    Returns: x_train, x_test, y_train, y_test
        _type_: _description_
    """
    # 划分数据集
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
        features, target, random_state=22)
    return x_train, x_test, y_train, y_test

  def train_test_split_iris(self):
    """划分数据集
    """

    # 1）获取数据
    iris = sklearn.datasets.load_iris()

    # 2）划分数据集
    # 特征 和 目标
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
        iris.data, iris.target, random_state=22)
    return x_train, x_test, y_train, y_test

  def GridSearchCV(self,
                   x_train, x_test, y_train, y_test,
                   estimator,
                   param_dict={"n_neighbors": [1, 3, 5, 7, 9, 11]},
                   cv=10,
                   ):
    # 加入网格搜索与交叉验证
    # 参数准备
    # n_neighbors 这个参数必须与KNeighborsClassifier()中的参数一致

    estimator = sklearn.model_selection.GridSearchCV(estimator,
                                                     param_grid=param_dict,
                                                     cv=cv)
    estimator.fit(x_train, y_train)

    # 5）模型评估
    # 方法1：直接比对真实值和预测值
    # y_predict = estimator.predict(x_test)
    # print("y_predict:\n", y_predict)
    # print("直接比对真实值和预测值:\n", y_test == y_predict)

    # 方法2：计算准确率
    score = estimator.score(x_test, y_test)
    print("准确率为：\n", score)

    # 最佳参数：best_params_
    print("最佳参数：\n", estimator.best_params_)
    # 最佳结果：best_score_
    # print("最佳结果：\n", estimator.best_score_)
    # # 最佳估计器：best_estimator_
    # print("最佳估计器:\n", estimator.best_estimator_)
    # # 交叉验证结果：cv_results_
    # print("交叉验证结果:\n", estimator.cv_results_)

    return estimator

  def knn_iris_gscv(self):
    """
    用KNN算法对鸢尾花进行分类，添加网格搜索和交叉验证
    :return:
    """
    # 1）获取数据
    iris = sklearn.datasets.load_iris()

    # 2）划分数据集
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
        iris.data, iris.target, random_state=22)

    # 3）特征工程：标准化
    transfer = sklearn.preprocessing.StandardScaler()
    x_train = transfer.fit_transform(x_train)
    x_test = transfer.transform(x_test)

    # 4）KNN算法预估器
    estimator = sklearn.neighbors.KNeighborsClassifier()

    # 加入网格搜索与交叉验证
    # 参数准备
    # n_neighbors 这个参数必须与KNeighborsClassifier()中的参数一致
    param_dict = {"n_neighbors": [1, 3, 5, 7, 9, 11]}
    estimator = sklearn.model_selection.GridSearchCV(estimator,
                                                     param_grid=param_dict,
                                                     cv=10)
    estimator.fit(x_train, y_train)

    # 5）模型评估
    # 方法1：直接比对真实值和预测值
    y_predict = estimator.predict(x_test)
    print("y_predict:\n", y_predict)
    print("直接比对真实值和预测值:\n", y_test == y_predict)

    # 方法2：计算准确率
    score = estimator.score(x_test, y_test)
    print("准确率为：\n", score)

    # 最佳参数：best_params_
    print("最佳参数：\n", estimator.best_params_)
    # 最佳结果：best_score_
    print("最佳结果：\n", estimator.best_score_)
    # 最佳估计器：best_estimator_
    print("最佳估计器:\n", estimator.best_estimator_)
    # 交叉验证结果：cv_results_
    print("交叉验证结果:\n", estimator.cv_results_)

    return None

  def gscv_example_FBlocation(self):
    # 1、获取数据
    data = pd.read_csv(
        "/Users/wangjinlong/my_linux/soft_learn/py_package_learn/sklearn_learn/data/FBlocation/train.csv")
    # 2、基本的数据处理
    # 1）缩小数据范围
    data = data.query("x < 2.5 & x > 2 & y < 1.5 & y > 1.0")
    # 2）处理时间特征
    time_value = pd.to_datetime(data["time"], unit="s")
    date = pd.DatetimeIndex(time_value)
    data["day"] = date.day
    data["weekday"] = date.weekday
    data["hour"] = date.hour
    # 3）过滤签到次数少的地点
    place_count = data.groupby("place_id").count()["row_id"]
    data_final = data[data["place_id"].isin(
        place_count[place_count > 3].index.values)]
    # 筛选特征值和目标值
    x = data_final[["x", "y", "accuracy", "day", "weekday", "hour"]]
    y = data_final["place_id"]
    # 数据集划分
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
        x, y)

    # 3）特征工程：标准化
    transfer = sklearn.preprocessing.StandardScaler()
    x_train = transfer.fit_transform(x_train)
    x_test = transfer.transform(x_test)

    # 4）KNN算法预估器
    estimator = sklearn.neighbors.KNeighborsClassifier()

    # 加入网格搜索与交叉验证
    param_dict = {"n_neighbors": [3, 5, 7, 9]}
    estimator = sklearn.model_selection.GridSearchCV(
        estimator, param_grid=param_dict, cv=3)
    estimator.fit(x_train, y_train)

    # 5）模型评估
    # 方法1：直接比对真实值和预测值
    y_predict = estimator.predict(x_test)
    print("y_predict:\n", y_predict)
    print("直接比对真实值和预测值:\n", y_test == y_predict)

    # 方法2：计算准确率
    score = estimator.score(x_test, y_test)
    print("准确率为：\n", score)

    # 最佳参数：best_params_
    print("最佳参数：\n", estimator.best_params_)
    # 最佳结果：best_score_
    # print("最佳结果：\n", estimator.best_score_)
    # 最佳估计器：best_estimator_
    # print("最佳估计器:\n", estimator.best_estimator_)
    # 交叉验证结果：cv_results_
    # print("交叉验证结果:\n", estimator.cv_results_)

    pass


class GetData():
  def __init__(self) -> None:
    pass

  def get_data_iris(self, is_stand_scaler=False):
    # 1）获取数据
    iris = sklearn.datasets.load_iris()

    # 2）划分数据集
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
        iris.data, iris.target, random_state=22)

    # 3）特征工程：标准化
    if is_stand_scaler:
      transfer = sklearn.preprocessing.StandardScaler()
      x_train = transfer.fit_transform(x_train)
      # 这里要非常注意，要使用训练集的标准化参数(mean, sigma)来确定测试集的特征值
      x_test = transfer.transform(x_test)

    return x_train, x_test, y_train, y_test

  def get_data_tatanic(self):
    """_summary_

    Returns: x_train, x_test, y_train, y_test
        _type_: _description_
    """
    # 1.获取数据
    path = "/Users/wangjinlong/my_linux/soft_learn/py_package_learn/sklearn_learn/data/titanic.csv"
    titanic = pd.read_csv(path)

    # 筛选特征值和目标值
    y = titanic.loc[:, "survived"]
    x: pd.DataFrame = titanic.loc[:, ["age", "pclass", "sex"]]

    # 2. 数据处理
    # 2.1 缺失值处理
    x['age'] = x["age"].fillna(int(x["age"].mean()))

    # 2.2 转化成字典
    # x_dict = x.to_dict(orient="index")
    x_dict = x.to_dict(orient="records")

    # 划分数据集
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
        x_dict, y, random_state=22)

    return x_train, x_test, y_train, y_test

  def get_data_20newsgroups(self):
    # 1）获取数据
    news = sklearn.datasets.fetch_20newsgroups(data_home='/Users/wangjinlong/my_linux/soft_learn/py_package_learn/sklearn_learn/data',
                                               subset="all")  # 默认下载到当前目录，all表示获取所有数据包括训练集和测试集

    # 2）划分数据集
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
        news.data, news.target)

    # 3）特征工程：文本特征抽取-tfidf
    transfer = sklearn.feature_extraction.text.TfidfVectorizer()
    x_train = transfer.fit_transform(x_train)
    x_test = transfer.transform(x_test)
    return x_train, x_test, y_train, y_test

  def get_data_breast_cancer(self):
    # breast_cancer = sklearn.datasets.load_breast_cancer()
    # return breast_cancer

    # 1 读取数据 ,加上names
    # path = "https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/breast-cancer-wisconsin.data"
    column_name = ['Sample code number', 'Clump Thickness', 'Uniformity of Cell Size', 'Uniformity of Cell Shape',
                   'Marginal Adhesion', 'Single Epithelial Cell Size', 'Bare Nuclei', 'Bland Chromatin',
                   'Normal Nucleoli', 'Mitoses', 'Class']
    # data = pd.read_csv(path, names=column_name)

    data = pd.read_csv(
        "/Users/wangjinlong/my_linux/soft_learn/py_package_learn/sklearn_learn/data/breast_cancer/breast-cancer-wisconsin.data", names=column_name)
    # 2. 缺失值处理
    data = data.replace(to_replace="?", value=np.nan)  # 取代?为NaN
    # print(data.loc[data["Sample code number"] == 1057067])
    data.dropna(inplace=True)  # 剔除行包含NaN值的行
    # print(data.isnull().any())  # 可以看到不存在缺失值了
    return data

  def get_data_boston(self):
    """_summary_

    Returns: features, target
        _type_: _description_
    """
    # 1. 获取数据
    # boston = datasets.load_boston()
    raw_df = pd.read_csv(
        "/Users/wangjinlong/my_linux/soft_learn/py_package_learn/sklearn_learn/data/boston.csv", sep="\s+", skiprows=22, header=None)
    features = np.hstack([raw_df.values[::2, :], raw_df.values[1::2, :2]])
    target = raw_df.values[1::2, 2]
    return features, target

  def get_data_instacart(self, fname='/Users/wangjinlong/my_linux/soft_learn/py_package_learn/sklearn_learn/data/instacart/data_small.csv'):
    if os.path.exists(fname):
      df = pd.read_csv(fname, index_col=0)
      return df
    else:
      aisles = pd.read_csv(
          "/Users/wangjinlong/my_linux/soft_learn/py_package_learn/sklearn_learn/data/instacart/aisles.csv")
      order_products = pd.read_csv(
          "/Users/wangjinlong/my_linux/soft_learn/py_package_learn/sklearn_learn/data/instacart/order_products__prior.csv")
      orders = pd.read_csv(
          "/Users/wangjinlong/my_linux/soft_learn/py_package_learn/sklearn_learn/data/instacart/orders.csv")
      products = pd.read_csv(
          "/Users/wangjinlong/my_linux/soft_learn/py_package_learn/sklearn_learn/data/instacart/products.csv")
      tab1 = pd.merge(aisles, products, on='aisle_id')
      tab2 = pd.merge(tab1, order_products, on="product_id")
      tab3 = pd.merge(tab2, orders, on="order_id")
      table = pd.crosstab(tab3["user_id"], tab3["aisle"])
      table_test = pd.pivot_table(
          tab3, index="user_id", columns="aisle", aggfunc="count")
      df = table[:20000]
      df.to_csv(
          '/Users/wangjinlong/my_linux/soft_learn/py_package_learn/sklearn_learn/data/instacart/data_small.csv')
    return df


class Neighbors():
  def __init__(self) -> None:
    """

    """
    pass

  def knn(self, x_train, x_test, y_train, y_test):
    """
    用KNN算法
    """

    # 4）KNN算法预估器
    estimator = sklearn.neighbors.KNeighborsClassifier(n_neighbors=3)
    estimator.fit(x_train, y_train)

    # 5）模型评估
    # 方法1：直接比对真实值和预测值
    y_predict = estimator.predict(x_test)
    print("y_predict:\n", y_predict)
    print("直接比对真实值和预测值:\n", y_test == y_predict)

    # 方法2：计算准确率
    score = estimator.score(x_test, y_test)
    print("准确率为：\n", score)

    return None

  def get_data(self,):
    """
    用KNN算法对鸢尾花进行分类
    """
    # 1）获取数据
    iris = sklearn.datasets.load_iris()

    # 2）划分数据集
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
        iris.data, iris.target, random_state=22)

    # 3）特征工程：标准化
    transfer = sklearn.preprocessing.StandardScaler()
    x_train = transfer.fit_transform(x_train)
    # 这里要非常注意，要使用训练集的标准化参数(mean, sigma)来确定测试集的特征值
    x_test = transfer.transform(x_test)

    return x_train, x_test, y_train, y_test

  def knn_iris(self,):
    """
    用KNN算法对鸢尾花进行分类
    :return:
    """
    # 1）获取数据
    iris = sklearn.datasets.load_iris()

    # 2）划分数据集
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
        iris.data, iris.target, random_state=22)

    # 3）特征工程：标准化
    transfer = sklearn.preprocessing.StandardScaler()
    x_train = transfer.fit_transform(x_train)
    # 这里要非常注意，要使用训练集的标准化参数(mean, sigma)来确定测试集的特征值
    x_test = transfer.transform(x_test)

    # 4）KNN算法预估器
    estimator = sklearn.neighbors.KNeighborsClassifier(n_neighbors=3)
    estimator.fit(x_train, y_train)

    # 5）模型评估
    # 方法1：直接比对真实值和预测值
    y_predict = estimator.predict(x_test)
    print("y_predict:\n", y_predict)
    print("直接比对真实值和预测值:\n", y_test == y_predict)

    # 方法2：计算准确率
    score = estimator.score(x_test, y_test)
    print("准确率为：\n", score)

    return None


class NaiveBayes():
  def __init__(self) -> None:
    """朴素贝叶斯算法
    通常用于文档分类
    假定特征之间独立, 利用贝叶斯公式计算概率
    """
    pass

  def MultinomialNB(self, x_train, x_test, y_train, y_test):
    """
    用朴素贝叶斯算法对新闻进行分类
    """

    # 4）朴素贝叶斯算法预估器流程
    # alpha=1 拉普拉斯平滑系数
    estimator = sklearn.naive_bayes.MultinomialNB(alpha=1)
    estimator.fit(x_train, y_train)

    # 5）模型评估
    # 方法1：直接比对真实值和预测值
    y_predict = estimator.predict(x_test)
    print("y_predict:\n", y_predict)
    print("直接比对真实值和预测值:\n", y_test == y_predict)

    # 方法2：计算准确率
    score = estimator.score(x_test, y_test)
    print("准确率为：\n", score)

    return None

  def MultinomialNB_example_news_classify(self,):
    """
    用朴素贝叶斯算法对新闻进行分类
    :return:
    """

    x_train, x_test, y_train, y_test = GetData().get_data_20newsgroups()

    # 4）朴素贝叶斯算法预估器流程
    estimator = sklearn.naive_bayes.MultinomialNB()
    estimator.fit(x_train, y_train)

    # 5）模型评估
    # 方法1：直接比对真实值和预测值
    y_predict = estimator.predict(x_test)
    print("y_predict:\n", y_predict)
    print("直接比对真实值和预测值:\n", y_test == y_predict)

    # 方法2：计算准确率
    score = estimator.score(x_test, y_test)
    print("准确率为：\n", score)

    return None


class Tree():
  def __init__(self) -> None:
    """决策树
    3.5.1 认识决策树
        如何高效的进行决策？
            特征的先后顺序
    3.5.2 决策树分类原理详解
        已知 四个特征值 预测 是否贷款给某个人
        先看房子，再工作 -> 是否贷款 只看了两个特征
        年龄，信贷情况，工作 看了三个特征
    信息论基础
        1）信息
            香农：消除随机不定性的东西
            小明 年龄 “我今年18岁” - 信息
            小华 ”小明明年19岁” - 不是信息
        2）信息的衡量 - 信息量 - 信息熵
            bit
            g(D,A) = H(D) - 条件熵H(D|A)
    4 决策树的划分依据之一------信息增益
    """
    pass

  def DecisionTreeClassifier(self, x_train, x_test, y_train, y_test,
                             max_depth,
                             feature_names):
    """决策树

    Args:
        x_train (_type_): _description_
        x_test (_type_): _description_
        y_train (_type_): _description_
        y_test (_type_): _description_
        max_depth (_type_): _description_
        feature_names (_type_): _description_

    Returns: estimator
        _type_: _description_
    """

    # 3）决策树预估器
    estimator = sklearn.tree.DecisionTreeClassifier(criterion="entropy",
                                                    max_depth=max_depth)
    estimator.fit(x_train, y_train)

    # 4）模型评估
    # 方法1：直接比对真实值和预测值
    y_predict = estimator.predict(x_test)
    print("y_predict:\n", y_predict)
    print("直接比对真实值和预测值:\n", y_test == y_predict)

    # 方法2：计算准确率
    score = estimator.score(x_test, y_test)
    print("准确率为：\n", score)

    # 可视化决策树
    # sklearn.tree.export_graphviz(estimator, out_file="iris_tree.dot", feature_names=feature_names,)
    self.plot_tree(estimator=estimator, feature_names=feature_names)
    return estimator

  def plot_tree(self, estimator, feature_names):
    """
    tree.export_graphviz(estimator, out_file="tree.dot", feature_names=iris.feature_names)  # 生成dot文件
    #  dot -Tpng tree.dot -o tree.png  # 我已经安装了grphviz软件，也可以在终端执行这条命令
    # print(iris.feature_names)
    os.system("dot -Tpng tree.dot -o tree.png")

    Args:
        estimator (_type_): _description_
        feature_names (_type_): _description_
    """
    # 绘制决策树
    plt.figure(figsize=(8, 6))  # 设置绘图尺寸
    # 使用plot_tree()函数绘制决策树
    # feature_names = iris.feature_names
    sklearn.tree.plot_tree(estimator, filled=True, feature_names=feature_names)
    plt.show()  # 显示图形
    pass

  def plot_tree2(self, estimator,
                 feature_names):
    # import graphviz
    # # 导出决策树为DOT格式
    # dot_data = sklearn.tree.export_graphviz(
    #     estimator, out_file=None, feature_names=feature_names)

    # # 使用Source类加载DOT格式数据
    # graph = graphviz.Source(dot_data)
    # # 渲染为PDF或图像文件
    # # graph.render("decision_tree")

    # # 显示决策树图形
    # # graph.view()
    # return graph
    pass

  def decision_tree_iris(self,):
    """
    用决策树对鸢尾花进行分类
    """
    iris = sklearn.datasets.load_iris()
    x_train, x_test, y_train, y_test = GetData().get_data_iris(
        is_stand_scaler=False)

    estimator = self.DecisionTreeClassifier(x_train=x_train,
                                            x_test=x_test,
                                            y_train=y_train,
                                            y_test=y_test,
                                            max_depth=None,
                                            feature_names=iris.feature_names)
    return estimator

  def decision_tree_titanic(self, max_depth=8,):
    """
    决策树-泰坦尼克
    """
    x_train, x_test, y_train, y_test = GetData().get_data_tatanic()

    # 字典特征抽取
    transfer = sklearn.feature_extraction.DictVectorizer()
    x_train = transfer.fit_transform(x_train)
    x_test = transfer.transform(x_test)

    # 决策树预估器
    estimator = self.DecisionTreeClassifier(x_train, x_test, y_train, y_test,
                                            max_depth=max_depth,
                                            feature_names=transfer.get_feature_names_out())
    return estimator


class Ensemble():
  def __init__(self) -> None:
    """集成学习方法, 随机深林是其中一种
    适合多特征大数据
    3.6.1 什么是集成学习方法
    3.6.2 什么是随机森林
        随机
        森林：包含多个决策树的分类器
    3.6.3 随机森林原理过程
        训练集：
        N个样本
        特征值 目标值
        M个特征
        随机
            两个随机
                训练集随机 - N个样本中随机有放回的抽样N个
                    bootstrap 随机有放回抽样
                    [1, 2, 3, 4, 5]
                    新的树的训练集
                    [2, 2, 3, 1, 5]
                特征随机 - 从M个特征中随机抽取m个特征
                    M >> m
                    降维
    """
    pass

  def RandomForestClassifier(self, x_train, x_test, y_train, y_test,
                             n_estimators=10,
                             max_depth=3,):
    estimator = sklearn.ensemble.RandomForestClassifier(
        criterion="entropy", n_estimators=n_estimators,
        max_depth=max_depth, random_state=22)
    estimator.fit(x_train, y_train)
    score = estimator.score(x_test, y_test)
    print("准确率为：", score)
    return estimator

  def RandomForestClassifier_titanic(self, n_estimators=10,
                                     max_depth=3,):
    x_train, x_test, y_train, y_test = GetData().get_data_tatanic()

    # 字典特征抽取
    transfer = sklearn.feature_extraction.DictVectorizer()
    x_train = transfer.fit_transform(x_train)
    x_test = transfer.transform(x_test)

    estimater = self.RandomForestClassifier(x_train, x_test, y_train, y_test,
                                            n_estimators=n_estimators,
                                            max_depth=max_depth)
    return estimater

  def RandomForestClassifier_titanic_with_gscv(self,
                                               param_dict={"n_estimators": [10, 100, 200, 300],
                                                           "max_depth": [3, 5, 7]},
                                               cv=3,):
    x_train, x_test, y_train, y_test = GetData().get_data_tatanic()

    # 字典特征抽取
    transfer = sklearn.feature_extraction.DictVectorizer()
    x_train = transfer.fit_transform(x_train)
    x_test = transfer.transform(x_test)

    # 随机森林预测生存  预估器
    estimator = sklearn.ensemble.RandomForestClassifier()
    # 加入网格搜索和交叉验证

    ModelSelection().GridSearchCV(x_train, x_test, y_train, y_test,
                                  estimator=estimator,
                                  param_dict=param_dict,
                                  cv=cv)

    return None


class LinearModel():
  def __init__(self) -> None:
    """目标值是连续的问题用回归算法

    以上两种方法都是线性回归，线性回归不常用，容易造成过拟合，实际常用为岭回归
    线性回归的损失和优化原理（理解记忆）
            目标：求模型参数
                模型参数能够使得预测准确
            真实关系：真实房子价格 = 0.02×中心区域的距离 + 0.04×城市一氧化氮浓度 + (-0.12×自住房平均房价) + 0.254×城镇犯罪率
            随意假定：预测房子价格 = 0.25×中心区域的距离 + 0.14×城市一氧化氮浓度 + 0.42×自住房平均房价 + 0.34×城镇犯罪率
            损失函数/cost/成本函数/目标函数：
                最小二乘法
            优化损失
                优化方法？
                正规方程
                梯度下降
                    勤奋努力的普通人
                        试错、改进
            4.1.4 波士顿房价预测
                流程：
                    1）获取数据集
                    2）划分数据集
                    3）特征工程：
                        无量纲化 - 标准化
                    4）预估器流程
                        fit() --> 模型
                        coef_ intercept_
                    5）模型评估
            回归的性能评估：
                均方误差
            4 正规方程和梯度下降对比

    """
    pass

  def estimator_evaluate(self,
                         estimator: sklearn.linear_model.Ridge,
                         x_test, y_test):
    """_summary_

    Args:
        estimator (sklearn.linear_model.Ridge): _description_
        x_test (_type_): _description_
        y_test (_type_): _description_

    Returns: predict
        _type_: _description_
    """
    predict = estimator.predict(x_test)
    mse = sklearn.metrics.mean_squared_error(y_test, predict)
    print(f'均方差误差为 {mse}')
    # 或者 score = estimator.score(x_test, y_test)
    score = sklearn.metrics.r2_score(y_test, predict)
    print(f'score: {score}')
    return predict

  def LinearRegression(self, features, target):
    """线性回归中的正规方程方法

    Args:
        x_train (_type_): _description_
        y_train (_type_): _description_

    Returns:
        _type_: _description_
    """
    estimator = sklearn.linear_model.LinearRegression()
    estimator.fit(features, target)
    print(f"权重系数为：", estimator.coef_)
    print(f"偏置为", estimator.intercept_)
    return estimator

  def LinearRegression_boston(self,):
    """
    正规方程方法
    :return:
    """
    # 1. 获得数据
    features, target = GetData().get_data_boston()
    # 2. 划分数据集
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
        features, target, random_state=22)
    # 3. 标准化
    transfer = sklearn.preprocessing.StandardScaler()
    x_train = transfer.fit_transform(x_train)
    x_test = transfer.transform(x_test)

    # 4. 预估器
    estimator = sklearn.linear_model.LinearRegression()
    estimator.fit(x_train, y_train)
    print("正规方程权重系数为：", estimator.coef_)
    print("正规方程偏置为", estimator.intercept_)

    # 6. 模型评估
    y_predict = estimator.predict(x_test)
    mse = sklearn.metrics.mean_squared_error(y_test, y_predict)
    print("正规方程的均方误差为：", mse)

    # 保存模型
    # Model().dump(estimator=estimator, fname="1_线性回归-正规方程法.pkl")
    # # 加载模型
    # estimator: sklearn.linear_model.LinearRegression = joblib.load(
    #     "1_线性回归-正规方程法.pkl")
    return estimator

  def SGDRegressor(self, features, target, penalty='l2'):
    """预估器: 梯度下降法
    设置学习率alpha, 和最大迭代次数max_iter:
    eta0=0.005, learning_rate="constant", max_iter=5000
    penalty='l1' 就是 LASSO

    Args:
        features (_type_): _description_
        target (_type_): _description_
        penalty (str, optional): _description_. Defaults to 'l2'.

    Returns: estimator
        _type_: _description_
    """

    estimator = sklearn.linear_model.SGDRegressor(
        penalty=penalty,
    )
    estimator.fit(features, target)
    print(f"权重系数为：", estimator.coef_)
    print(f"偏置为", estimator.intercept_)
    return estimator

  def SGDRegressor_bosten(self,):
    """
    线性回归中的梯度下降法
    :return:
    """
    # 1. 获取数据
    # boston = sklearn.datasets.load_boston()
    features, target = GetData().get_data_boston()
    # 2. 划分数据集
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
        features, target, random_state=22)
    # 3. 特征工程：标准化
    transfer = sklearn.preprocessing.StandardScaler()
    x_train = transfer.fit_transform(x_train)
    x_test = transfer.transform(x_test)

    # 4. 预估器 :梯度下降法
    # 设置学习率alpha, 和最大迭代次数max_iter:
    # eta0=0.005, learning_rate="constant", max_iter=5000
    # penalty='l1' 就是 LASSO
    estimator = sklearn.linear_model.SGDRegressor(max_iter=10000, eta0=0.002,
                                                  )

    estimator.fit(x_train, y_train)

    # 5. 得出模型
    print("梯度下降权重系数为：", estimator.coef_)
    print("梯度下降偏置为", estimator.intercept_)

    # 5. 模型评估
    y_predict = estimator.predict(x_test)
    mse = sklearn.metrics.mean_squared_error(y_test, y_predict)
    print("梯度下降的均方误差为：", mse)
    return None

  def Lasso(self, features, target):
    estimator = sklearn.linear_model.Lasso()
    estimator.fit(features, target)
    print(f'系数为: {estimator.coef_}\n偏置为: {estimator.intercept_}')
    return estimator

  def Ridge(self, features, target):
    """预估器 :岭回归

    查看模型
    name = "岭回归"
    print(f"{name}权重系数为：", estimator.coef_)
    print(f"{name}偏置为", estimator.intercept_)

    estimator = linear_model.SGDRegressor(penalty="l2") 等价于下面的Ridge， 因为penalty="l2" 区别在于使用的优化算法为一般的gd
    alpha 惩罚项系数
    estimator = sklearn.linear_model.Ridge(alpha=1, random_state=22,
                                   solver='auto',)  # 设置学习率alpha, 和最大迭代次数max_iter,solver=优化算法，gd, sdg(随机梯度下降)
    sklearn.linear_model.Lasso()
    带CV 的 ridge: estimator = sklearn.linear_model.RidgeCV(cv=3,)

    Returns: estimator
        _type_: _description_
    """

    # 设置学习率alpha, 和最大迭代次数max_iter,solver=优化算法 sdg(随机梯度下降)
    estimator = sklearn.linear_model.Ridge(alpha=1, random_state=22,
                                           solver='auto',)
    estimator.fit(features, target)
    print(f"权重系数为：", estimator.coef_)
    print(f"偏置为", estimator.intercept_)
    return estimator

  def Ridge_evaluate(self,
                     estimator: sklearn.linear_model.Ridge,
                     x_test, y_test):
    predict = self.estimator_evaluate(estimator=estimator,
                                      x_test=x_test,
                                      y_test=y_test)
    return predict

  def Ridge_wrapper(self, x_train, x_test, y_train, y_test):
    """_summary_

    Args:
        x_train (_type_): _description_
        x_test (_type_): _description_
        y_train (_type_): _description_
        y_test (_type_): _description_

    Returns: predict
        _type_: _description_
    """
    esitmator = self.Ridge(features=x_train, target=y_train)
    predict = self.Ridge_evaluate(
        estimator=esitmator, x_test=x_test, y_test=y_test)

    return predict

  def Ridge_boston(self):
    """
    岭回归计算房价
    :return:
    """
    # 获得数据
    features, target = GetData().get_data_boston()

    # 2. 划分数据集
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
        features, target, random_state=22)

    # 3. 标准化
    transfer = sklearn.preprocessing.StandardScaler()
    x_train = transfer.fit_transform(x_train)
    x_test = transfer.transform(x_test)

    # 4. 预估器 :岭回归
    # estimator = linear_model.SGDRegressor(penalty="l2") 等价于下面的Ridge， 因为penalty="l2" 区别在于使用的优化算法为一般的gd
    # alpha 惩罚项系数
    # estimator = sklearn.linear_model.Ridge(alpha=1, random_state=22,
    #                                solver='auto',)  # 设置学习率alpha, 和最大迭代次数max_iter,solver=优化算法，gd, sdg(随机梯度下降)
    # sklearn.linear_model.Lasso()
    # 带CV 的 ridge
    estimator = sklearn.linear_model.RidgeCV(cv=3,)
    estimator.fit(x_train, y_train)

    # 5. 得出模型
    name = "岭回归"
    print(f"{name}权重系数为：", estimator.coef_)
    print(f"{name}偏置为", estimator.intercept_)

    # 6. 模型评估
    y_predict = estimator.predict(x_test)
    mse = sklearn.metrics.mean_squared_error(y_test, y_predict)
    print(f"{name}的均方误差为：", mse)

    return estimator

  def BayesianRidge(self, features, target):
    estimator = sklearn.linear_model.BayesianRidge()
    estimator.fit(features, target)
    print(f"权重系数为：", estimator.coef_)
    print(f"偏置为", estimator.intercept_)
    return estimator

  def LogisticRegression_breast_cancer(self):
    """
    逻辑回归处理癌症分类, 既然是分类问题，我测试过，还可以使用knn，决策树和随机森林算法来处理
    4.4.2 逻辑回归的原理
        线型回归的输出 就是 逻辑回归 的 输入
        激活函数
            sigmoid函数 [0, 1]
            1/(1 + e^(-x))
        假设函数/线性模型
            1/(1 + e^(-(w1x1 + w2x2 + w3x3 + …… + wnxn + b)))
        损失函数
            (y_predict - y_true)平方和/总数
            逻辑回归的真实值/预测值 是否属于某个类别
            对数似然损失
            log 2 x
        优化损失
            梯度下降
    4.4.5 分类的评估方法
        1 精确率与召回率
            1 混淆矩阵
                TP = True Possitive
                FN = False Negative
            2 精确率(Precision)与召回率(Recall)
                精确率
                召回率 查得全不全
                工厂 质量检测 次品 召回率
            3 F1-score 模型的稳健型
       总共有100个人，如果99个样本癌症，1个样本非癌症 - 样本不均衡
       不管怎样我全都预测正例(默认癌症为正例) - 不负责任的模型
           准确率：99%
           召回率：99/99 = 100%
           精确率：99%
           F1-score: 2*99%/ 199% = 99.497%
           AUC:0.5
                TPR = 100%
                FPR = 1 / 1 = 100%
       2 ROC曲线与AUC指标
            1 知道TPR与FPR
                TPR = TP / (TP + FN) - 召回率
                    所有真实类别为1的样本中，预测类别为1的比例
                FPR = FP / (FP + TN)
                    所有真实类别为0的样本中，预测类别为1的比例
    """
    # 1 数据
    data = GetData().get_data_breast_cancer()

    # 3. 划分数据集
    # 筛选特征值和目标值
    x = data.iloc[:, 1:-1]
    y = data.loc[:, "Class"]
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
        x, y, random_state=22)

    # 4.特征工程 ：标准化
    transfer = sklearn.preprocessing.StandardScaler()
    x_train = transfer.fit_transform(x_train)
    x_test = transfer.transform(x_test)

    # 5. 逻辑回归 预估器
    # LogisticRegression方法相当于 SGDClassifier(loss="log"penalty=""),SGDClassifier实现了一个普通的随机梯度下降学习也支持平均随机梯度下降法(ASGD)，可以通过设置average=True。而使用LogisticRegression(实现了SAG)
    estimator = sklearn.linear_model.LogisticRegression()
    estimator.fit(x_train, y_train)

    # 6. 模型评估
    # 方法1 直接对比
    y_predict = estimator.predict(x_test)
    print("直接对比真实值和预测值：", y_predict == y_test)

    # 方法2 计算准确率
    score = estimator.score(x_test, y_test.values)
    print(score)

    # 7. 看模型参数 也是看权重和偏置
    print("回归系数：", estimator.coef_)
    print("偏置:", estimator.intercept_)

    # 8. 分类评估报告 API  以上查看的准确率并不能反映真正患癌症的能够被检测出来的几率，所以需要分类报告查看召回率
    # 精确率：查的对不对
    # 召回率：查的全不全 真正患癌症的能够被检测出来的几率->召回率
    # F1-score (反映了模型的稳健性)  F1 = 2* 准确率 /(准确率+召回率)
    # 测试目标值，预测目标值，标签，target_names 返回的是报告
    report = sklearn.metrics.classification_report(
        y_test, y_predict, labels=[2, 4], target_names=["良性", "恶性"])
    print(report)

    # 9. AUC 计算API  可以用于评价逻辑回归预估器(分类器)的性能 越接近1越好，越接近0.5越不好
    # 在样本均衡时，F1-score能够反映模型的稳健性，但如果样本不均衡(例如真实100个样本中，99个患病1个未患病)时，不能说分类器是稳健的，还需要考虑AUC指标
    # AUC 只能评价二分类，非常适合评价样本不均衡时分类器的性能
    # roc_auc_score API中的y_true(真实值)参数为样本的真实类别，必须用正例1和反例0标记
    y_true = np.where(y_test > 3, 1, 0)
    print(y_true)
    auc = sklearn.metrics.roc_auc_score(y_true, y_predict)
    print(auc)

  def nolinear_非线性回归拟合(self, features, target, degree=2,):
    """_summary_

    Returns: predict
        _type_: _description_
    """
    features_poly = Preprocessing().PolynomialFeatures(
        features=features, degree=degree)
    # self.BayesianRidge 也可以
    estimator = self.LinearRegression(features=features_poly, target=target)
    predict = self.estimator_evaluate(estimator=estimator,
                                      x_test=features_poly,
                                      y_test=target)
    return predict


class Cluster():
  def __init__(self) -> None:
    """聚类算法
    """
    pass

  def KMeans_instacart(self):
    # 获取数据
    data = GetData().get_data_instacart()
    #  PCA 降维 实例化一个转换器
    transfer = sklearn.decomposition.PCA(n_components=0.8)  # 保存90%的信息
    # 调用fit_transform
    data_new = transfer.fit_transform(data)
    # print("降维之前的维度", data.shape)
    # print("降维之后的维度", data_new.shape)

    # 降维之后的数据
    # 1. 进行预估器流程
    estimator = sklearn.cluster.KMeans(n_clusters=3)
    estimator.fit(data_new)

    # 2. 看聚类分类结果
    y_predict = estimator.predict(data_new)
    print(y_predict[:200])

    # 3. 模型评估  轮廓系数 sc_i = (b_i - a_i)/max(b_i, a_i) bi  # 说明文档里有详细说明，b_i: 可理解为外部距离，a_i:可理解为内部距离
    # 可以进行多次聚类，从而避免收敛到局部最优解
    sc = sklearn.metrics.silhouette_score(
        data_new, y_predict)  # 轮廓系数 :[-1,1] 越接近1，族群分得越开，聚类效果越好
    print(sc)
    return estimator


class Model():
  def __init__(self) -> None:
    """模型的保存与加载
    """
    pass

  def dump(self, estimator, fname="1_线性回归-正规方程法.pkl"):
    """保存模型

    Args:
        estimator (_type_): _description_
        fname (str, optional): _description_. Defaults to "1_线性回归-正规方程法.pkl".
    """

    joblib.dump(estimator, filename=fname)
    print(f'模型保存在{fname}')

  def load(self, fname="1_线性回归-正规方程法.pkl"):
    """加载模型

    Args:
        fname (str, optional): _description_. Defaults to "1_线性回归-正规方程法.pkl".

    Returns: estimator
        _type_: _description_
    """

    estimator: sklearn.linear_model.LinearRegression = joblib.load(
        filename=fname)
    return estimator

  def model_evaluation(self,
                       y_true,
                       y_pred,):
    """print(f"均方误差为：", mse)

    Args:
        y_true (_type_): _description_
        y_pred (_type_): _description_

    Returns:
        _type_: _description_
    """
    mse = sklearn.metrics.mean_squared_error(y_true=y_true,
                                             y_pred=y_pred)
    print(f"均方误差为：", mse)
    r2_score = sklearn.metrics.r2_score(y_true=y_true,
                                        y_pred=y_pred)
    print(f"r2_score", r2_score)
    return None

  def model_evaluation_ridge(self, estimator: sklearn.linear_model.Ridge,
                             x_test, y_test):
    """模型评估 岭回归

    Args:
        estimator (sklearn.linear_model.Ridge): _description_
        x_test (_type_): _description_
        y_test (_type_): _description_

    Returns: mse
        _type_: _description_
    """

    y_predict = estimator.predict(x_test)
    mse = sklearn.metrics.mean_squared_error(y_test, y_predict)
    # sklearn.metrics.r2_score()
    print(f"均方误差为：", mse)

    return mse


class Fit(metaclass=functoolsLearn.AutoDecorateMeta):
  def __init__(self) -> None:
    """当前能想到的数据拟合方法
    """
    pass

  def fit_plot(self, xdata, ydata, x_fit, y_fit):
    x_fit, y_fit = self.polyfit_1d_numpy(xdata, ydata,
                                         degree=3)
    plt.figure()
    plt.plot(xdata, ydata, x_fit, y_fit)
    plt.show()

  def polyfit_1d_numpy(self,
                       x_arr=np.array([1, 2, 3, 4, 5, 6, 7, 8, 9]),
                       y_arr=np.array([1, 4, 9, 16, 25, 36, 49, 64, 81]),
                       degree=2,
                       num=100):
    # 一元多项式拟合
    from py_package_learn.numpy_learn import numpyLearn
    x_fit, y_fit = numpyLearn.Features().polyfit(
        x_arr=x_arr,
        y_arr=y_arr,
        degree=degree,
        num=num,)
    return x_fit, y_fit

  def curve_fit_2D_scipy(self, feature_list,
                         target,
                         model=None):
    # 二元或者多元变量的非线性拟合
    from py_package_learn.scipy_learn import scipyLearn
    popt = scipyLearn.Features().Optimize.curve_fit_2D(
        features=feature_list,
        target=target,
        model=model,)
    model.popt = popt
    target_predict = model(feature_list, *popt)
    return target_predict

  def nolinear_非线性回归拟合_sklearn(self, features, target, degree=2,):
    """_summary_

    Returns: target_predict
        _type_: np.array
    """
    target_predict = Features().LinearModel.nolinear_非线性回归拟合(
        features=features,
        target=target,
        degree=degree)

    return target_predict

  def plot_fit_check(self, data):
    from py_package_learn.matplotlib_learn import matplotlibLearn
    mf = matplotlibLearn.Features()
    z = abs((data['target']-data['predict'])/data['target'])
    fig, ax = mf.TwoDimension.scatter(x=data['x'], y=data['y'], z=z,
                                      is_colorbar=True, s=50)

    bad_index_list = z[z > 0.4].index
    for index in bad_index_list:
      print(f'waring: 相对误差大于0.4-> {index}')
    badest_index = z.index[np.argmax(z)]
    print(f'最差的异常点: {badest_index}')
    return fig, ax


class Features():
  def __init__(self) -> None:
    """
    **Table of contents**<a id='toc0_'></a>    
    - 1. [获取数据集](#toc1_)    
    - 2. [划分数据集](#toc2_)    
    - 3. [特征工程: 标准化](#toc3_)    
    - 4. [KNN 算法预估器](#toc4_)    
    - 5. [模型评估](#toc5_)   
    """
    self.SklearnLearn = SklearnLearn()
    # 1.获取数据集
    self.GetData = GetData()
    # 2.模型选择与调优: 包括划分数据集
    self.ModelSelection = ModelSelection()
    # 3.特征工程
    self.FeatureExtraction = FeatureExtraction()
    self.Preprocessing = Preprocessing()
    # 特征工程: 特征降维
    self.FeatureSelection = FeatureSelection()
    self.Decomposition = Decomposition()
    # 算法部分
    self.Neighbors = Neighbors()
    self.NaiveBayes = NaiveBayes()
    self.Tree = Tree()
    self.Ensemble = Ensemble()
    self.LinearModel = LinearModel()
    self.Cluster = Cluster()
    # 模型的保存与加载
    self.Model = Model()

    # 关于拟合
    self.Fit = Fit()
    pass

  def x(self):
    pass
