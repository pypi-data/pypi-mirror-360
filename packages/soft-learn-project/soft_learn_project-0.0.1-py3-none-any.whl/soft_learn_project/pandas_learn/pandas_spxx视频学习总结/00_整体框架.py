
# Pandas
"""
    基础处理
        Pandas是什么？为什么用？
        三大核心数据结构
            DataFrame
            Panel
            Series
        基本操作
        运算
        画图
        文件的读取与存储
    高级处理

4.1Pandas介绍
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
4.4 Pandas画图
    sr.plot()
4.5 文件读取与存储
    4.5.1 CSV
        pd.read_csv(path)
            usecols=
            names=
        dataframe.to_csv(path)
            columns=[]
            index=False
            header=False
    4.5.2 HDF5
        hdf5 存储 3维数据的文件
            key1 dataframe1二维数据
            key2 dataframe2二维数据
        pd.read_hdf(path, key=)
        df.to_hdf(path, key=)
    4.5.3 JSON
        pd.read_json(path)
            orient="records"
            lines=True
        df.to_json(patn)
            orient="records"
            lines=True
"""

# Pandas高级处理
"""
    缺失值处理
    数据离散化
    合并
    交叉表与透视表
    分组与聚合
    综合案例

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
4.7 高级处理-数据离散化
    性别 年龄
A    1   23
B    2   30
C    1   18
    物种 毛发
A    1
B    2
C    3
    男 女 年龄
A   1  0  23
B   0  1  30
C   1  0  18

    狗  猪  老鼠 毛发
A   1   0   0   2
B   0   1   0   1
C   0   0   1   1
one-hot编码&哑变量
4.7.1 什么是数据的离散化
    原始的身高数据：165，174，160，180，159，163，192，184
4.7.2 为什么要离散化
4.7.3 如何实现数据的离散化
    1）分组
        自动分组sr=pd.qcut(data, bins)
        自定义分组sr=pd.cut(data, [])
    2）将分组好的结果转换成one-hot编码
        pd.get_dummies(sr, prefix=)
4.8 高级处理-合并
    numpy
        np.concatnate((a, b), axis=)
        水平拼接
            np.hstack()
        竖直拼接
            np.vstack()
    1）按方向拼接
        pd.concat([data1, data2], axis=1)
    2）按索引拼接
        pd.merge实现合并
        pd.merge(left, right, how="inner", on=[索引])
4.9 高级处理-交叉表与透视表
    找到、探索两个变量之间的关系
    4.9.1 交叉表与透视表什么作用
    4.9.2 使用crosstab(交叉表)实现
        pd.crosstab(value1, value2)
    4.9.3 pivot_table
4.10 高级处理-分组与聚合
    4.10.1 什么是分组与聚合
    4.10.2 分组与聚合API
        dataframe
        sr
# """
