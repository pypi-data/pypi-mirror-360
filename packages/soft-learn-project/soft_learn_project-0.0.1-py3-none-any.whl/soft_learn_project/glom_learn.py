# glom 模块来处理数据套嵌，glom 模块允许我们使用 . 来访问内嵌对象的属性。
# 安装: pip3 install glom
import pandas as pd
from glom import glom

df = pd.read_json('data/nested_deep.json')
print(df)
data = df['students'].apply(lambda row: glom(row, 'grade.math'))
print(data)
