import pandas as pd

"""
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
            
# excel 的读写
"""

# ### 1 读取csv文件-read_csv()
"""
# 读取有标题行的csv
data1 = pd.read_csv("../../../../data/stock_day/stock_day.csv", usecols=["high", "low", "open", "close"])
# print(data1)

# 读取无标题行的csv, 加入names参数，指定列名
data = pd.read_csv("../../stock_day2.csv",
                   names=["open", "high", "close", "low", "volume", "price_change", "p_change", "ma5", "ma10", "ma20",
                          "v_ma5", "v_ma10", "v_ma20", "turnover"])
# print(data)

df = pd.read_csv("log.lammps",skiprows=83, nrows=21,sep="[\s]+", engine="python")  # python读取csv到dataframe需要解析多个分割符分列, 可以用正则表达式, 需要加参数engine="python" 以避免出现警告
# 保存'open'列的数据
# print(data)
# print(data["open"])
# data[:10].to_csv("test.csv", columns=["open"])
# print(pd.read_csv("test.csv"))
data[:10].to_csv("test.csv", columns=["open"], index=False, mode="w", header=False)  # header:是否带列名, mode=a表示追加
print("over")
# """

# ### 4.5.2 HDF5
"""
day_close: pd.DataFrame = pd.read_hdf("../../stock_data/day/day_close.h5")
# print(day_close)
day_close.to_hdf("test.h5", key="close")

pd.read_hdf("test.h5", key="close").head()
day_open = pd.read_hdf("../../stock_data/day/day_open.h5")
day_open.to_hdf("test.h5", key="open")
df = pd.read_hdf("test.h5", key="close").head()
print(df)
# """

# ### 4.5.3 JSON
"""
sa = pd.read_json("../../Sarcasm_Headlines_Dataset.json", orient="records", lines=True)
sa
sa.to_json("../../test.json", orient="records", lines=True)
# """

# ===============================================

# Pandas 处理 CSV 文件
"""
# 1. 读取csv文件
df = pd.read_csv('nba.csv')  # 直接变成dataframe对象，之后就可以使用dataframe对象的方法

# 2. 保存csv文件
df.to_csv('test.csv')
nme = ["Google", "Runoob", "Taobao", "Wiki"]
st = ["www.google.com", "www.runoob.com", "www.taobao.com", "www.wikipedia.org"]
ag = [90, 40, 80, 98]
dic = {'name': nme, 'site': st, 'age': ag}
df = pd.DataFrame(dic)
df.to_csv('site.csv')  # 使用 to_csv() 方法将 DataFrame 对象存储为 csv 文件
# """

# excel 的读写
"""# 写入excel
df = pd.read_csv("nba.csv")
df2: pd.DataFrame = df.loc[0:10:2, :]
print(df2)
df2.to_excel("nba.xlsx", sheet_name="SHEET1", index=False) # 数据写入时通常指定index=False,因为DataFrame对象是带有index属性的

#  写入excel不覆盖原有sheet的方法,建立写入器，写入器的模式为mode="a"
# 直接用df.to_excel(writer, sheet_name=sheet_name)会覆盖所有其他sheet
with pd.ExcelWriter(outfile, mode="a") as writer:  
    df.to_excel(writer, sheet_name=sheet_name)  

# 如果sheet_name 已经存在会报错所以使用下面的方式
with pd.ExcelWriter(outfile, mode="a") as writer:
    if sheet_name not in writer.sheets.keys():
        df.to_excel(writer, sheet_name=sheet_name)
        print(f"保存到{outfile}完毕！")
    else:
        print(f"已经存在sheet_name:\to{sheet_name}")

# 另一种方法, sheet_name 即使重复也会建立一个sheet_name[n]的sheet
wb = openpyxl.load_workbook('test.xlsx')
# 如果有多个模块可以读写excel文件，这里要指定engine，否则可能会报错
with pd.ExcelWriter('test.xlsx', engine='openpyxl') as writer:
    # 没有下面这个语句的话excel表将完全被覆盖
    writer.book = wb
    df.to_excel(writer, sheet_name='Sheet3', index=None)
    print(writer.book)
# """

# """# 读取excel
"""
# 默认读取到第一个表单, index_col=0,指定第0列为索引列，第0行为表头， # 因为是从0开始
df = pd.read_excel("nba.xlsx", sheet_name="SHEET1", index_col=0, header=0)
print(df)

#df1 = pd.read_excel('../codes/python_2020CUMCM/副本附件1：123家有信贷记录企业的相关数据.xlsx',
                    # sheet_name='Sheet2',usecols='H:L',header=15, nrows=5)
# use_cols指定要读取哪些列，我要读取的是H到L,所以指定use_cols='H:L'；如果我只想读取H和L这两列（不连续），那么指定use_cols='H,L'
# header指定我们要从哪一行开始读取
# nrows用来指定我要读取多少行数据（标题行不算），这边nrows=5

# """

# Pandas 处理JSON数据
# """
# 从 URL 中读取 JSON 数据
# URL = 'https://static.runoob.com/download/sites.json'
# df = pd.read_json(URL)   # 直接变成dataframe对象

# 1.读取简单的json文件, 和写入json
"""
df = pd.read_json('sites.json')  # 直接变成dataframe对象, 对于特别复杂的就不不能使用该方法了
print(df)
df.head(1).to_json('xx.json', force_ascii=False)  # 写入json
# """

# 2.读取复杂的嵌套json
"""
with open('nested_list.json', 'r') as f:
    data = json.loads(f.read())  # 把字符串变成json # 或者 data = json.load(f)

df_nested_list = pd.json_normalize(data, record_path=[
    'students'], meta=['school_name', 'class'])  # 展平数据 #使用了参数 record_path 并设置为 ['students'] 用于展开内嵌的 JSON 数据
print(df_nested_list)
# """

# 3.1 读取更复杂的混合嵌套json
""" 
with open('nested_mix.json', 'r') as f:
    data = json.loads(f.read())

# print(pd.DataFrame(data))  # 对于字典里面有字典，字典里面还有列表就不行了

# 可以读取字典中的student
dic = data['students']
# print(dic)
df = pd.DataFrame(dic)
print(df)
# """

"""
# 或者使用pd.json_normalize方法
with open('nested_mix.json', 'r') as f:
    data = json.loads(f.read())

df = pd.json_normalize(
    data,
    record_path=['students'],
    meta=['class', ['info', 'president'], ['info', 'contacts', 'tel']]
)
print(df)
# """

# 3.2 也很复杂
"""
df = pd.read_json('nested_deep.json')
print(df)
data = df['students'].apply(lambda row: glom(row, 'grade.math'))
print(data)
print(df['students'].apply(lambda row: glom(row, 'grade')).apply(lambda row: glom(row, 'chemistry')))
# """
