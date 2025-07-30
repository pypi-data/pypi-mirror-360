# 要压缩 zip 文件，可以使用 Python 内置的 zipfile 模块。以下是一个简单的示例：


import zipfile

# 创建一个 ZipFile 对象，指定压缩后的文件名和打开模式
with zipfile.ZipFile('my_archive.zip', 'w') as myzip:
  # 添加要压缩的文件到 zip 文件中，可以一次添加多个文件
  myzip.write('file1.txt')
  myzip.write('file2.txt')
  myzip.write('file3.txt')


# 压缩完成后，可以在当前目录下找到 my_archive.zip 文件

# 在上面的示例中，我们首先创建了一个 ZipFile 对象，并指定了要创建的压缩文件的名称和打开模式。接下来，我们使用 write 方法将要压缩的文件添加到压缩文件中。最后，我们在 with 语句块结束时自动关闭了 ZipFile 对象，这样压缩文件就完成了。

# 请注意，如果要添加整个目录中的文件到压缩文件中，可以使用 write 方法的第二个参数指定目录前缀，如 myzip.write('my_dir/file1.txt', 'my_dir/')。这将在压缩文件中创建一个 my_dir 目录，并将文件 file1.txt 添加到该目录中。


import glob
import zipfile
fname_list = glob.glob('**/**成绩*表*.doc', recursive=True)
with zipfile.ZipFile(file='zip.zip', mode='w') as f:
  for fname in fname_list:
    f.write(fname, arcname=fname.rsplit('/')[-1])


# 解压缩 ZipFile 对象中的文件

# 打开一个已经存在的压缩文件
myzip = zipfile.ZipFile('my_archive.zip', 'r')

# 解压缩指定的文件到指定的目录
myzip.extract('file1.txt', '/path/to/extract')

# 解压缩压缩文件中的所有文件到指定的目录
myzip.extractall('/path/to/extract')


# 打开 ZipFile 对象

# 打开一个已经存在的压缩文件
myzip = zipfile.ZipFile('my_archive.zip', 'r')

# 获取压缩文件中所有的文件名列表
file_names = myzip.namelist()

# 读取压缩文件中指定的文件内容
file_content = myzip.read('file1.txt')

# 关闭 ZipFile 对象
myzip.close()
