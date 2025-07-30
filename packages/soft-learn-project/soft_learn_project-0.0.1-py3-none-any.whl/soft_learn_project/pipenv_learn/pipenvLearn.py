pipenv - 给人用的Python开发管理工具
===================================

## 知识点

+ pipenv是更加便捷的Python项目管理工具

## 网站

http://pipenv.org/

## 在线体验

https://rootnroll.com/d/pipenv/

## 安装

```bash
$ pip install pipenv
$ pipenv --version
```

## 第一个工程项目

```bash
$ mkdir myweb
$ cd myweb
# 项目初始化-Python3
$ pipenv --python 3
$ pipenv install flask
$ cat Pipfile
$ pip list
$ pipenv shell
$ pip list
$ pipenv --venv
$ pipenv graph
$ exit
# 安装开发专用包
$ pipenv install --dev requests
$ cat Pipfile
```

## 团队内项目共享

### Pipfile

将建立好的Pipfile文件直接拷贝给项目组的其他成员，可迅速完成开发环境的搭建。

```bash
$ mkdir myweb1
$ cd myweb1
$ wget http://192.168.1.1/myweb/Pipfile
# 安装依赖库，包括开发用依赖库
$ pipenv install --dev
$ pipenv shell
$ pip list
$ exit
$ pipenv --venv
# 删除虚拟环境
$ pipenv --rm
$ pipenv --venv
```

## 代码运行

### main.py

```python
import requests
```

### 运行脚本

```bash
$ pipenv run python main.py
```

## 定义执行脚本

### Pipfile

```
[scripts]
start = "python main.py"
test = "pytest"
list = "pip list"
```

### 运行脚本

```bash
$ pipenv run python main.py
$ pipenv run start
$ pipenv run test
$ pipenv run list
```

## 课程文件

https://gitee.com/komavideo/LearnPipenv

## 小马视频频道

http://komavideo.com
