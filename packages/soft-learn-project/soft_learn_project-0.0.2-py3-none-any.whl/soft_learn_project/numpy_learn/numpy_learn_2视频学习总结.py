# numpy
"""
1. ndarray属性
2. 基本操作
    ndarray.方法()
    numpy.函数名()
3. ndarray运算
    逻辑运算
    统计运算
    数组间运算
4. 合并、分割、IO操作、数据处理， 对数据的合并分割主要还是用pandas

1.1 ndarray的属性
    shape
        ndim
        size
    dtype
        itemsize
    在创建ndarray的时候，如果没有指定类型
    默认
        整数 int64
        浮点数 float64
# """
import numpy as np
c = np.array([[[1,2,3],[4,5,6]],[[1,2,3],[4,5,6]]])
# 形状和类型属性最重要
print(c.shape)
print(c.dtype)

# 创建数组的时候指定类型
a = np.array([1.1, 2.2, 3.3], dtype="float32")
b = np.array([1.1, 2.2, 3.3], dtype=np.float32)
print(a.dtype)
print(b)


