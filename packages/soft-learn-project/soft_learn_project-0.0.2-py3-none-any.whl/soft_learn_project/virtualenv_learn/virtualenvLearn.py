class viertu():
  def __init__(self) -> None:
    """
      简化版虚拟环境 virtualenv
      缺点是虚拟环境的文件分散在当当时创建的位置，每次使用时需要进入目录，找到激活的脚本，如果忘记了路径，不方便管理。
      ---
      场景	推荐工具
      Python 3 开发	venv（最简单） # Python 3.3 起内置，无需单独安装。
      需要 Python 2 支持	virtualenv # 第三方库（需要安装：pip install virtualenv）
      同时管理多个项目或环境	virtualenvwrapper  # 依赖：必须先安装 virtualenv
    """
    pass

  def install(self):
    """
     $pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple virtualenv
    """
    pass

  def step1_建立环境(self):
    """
      ```shell
      mkdir virtualenv
      cd virtualenv
      virtualenv mynumpy 
      # 或者
      python3 -m venv env_test
      python3 -m virtualenv env2_test 
      ```
    """
    pass

  def step2_使用环境(self):
    """
      1. 激活

      ```shell
      source mynumpy/bin/activate  # 激活版本
      pip list #可以看到已经进入虚拟环境
      pip install numpy #在虚拟环境中安装numpy
      ```
      2. 退出

      ```shell
      deactivate #退出虚拟环境
      pip list #可以确认确实退出了
      ```
    """
    pass

  def step3_包导出与安装(self):
    """
      1. 包导出与安装

      ```shell
      # 建立的第二个环境为mydev 与第一个方法相同
      pip freeze > requirement.txt #导出到安装目录
      virtualenv mydev #建立虚拟环境
      source mydev/bin/activate #激活
      pip list #查看
      pip install -r requirement.txt #安装
      pip list 
      deactivate 
      ```
    """
    pass

  def other_tips(self):
    """
      Python三神器之virtualenv、virtualenvwrapper
      virtualennv用于创建独立的Python环境， 多个python相互独立，互不影响，它能够：

      在没有权限的情况下安装新套件
      不同应用可以使用不同的套件版本
      套件升级不影响其他应用。
      # 启动环境
      cd env
      source .bin/activate

      ENV为虚拟环境名称，接下来所有模块都只会安装到该目录中去。

      默认情况下，虚拟环境会依赖系统环境中的site packages，如果不想依赖这些package，那么可以加上参数 --no-site-packages建立虚拟环境：

      virtualenv --no-site-packages [虚拟环境名称]

      # 退出
      deactivate
    """
    pass

  def Virtualenvwrapper(self):
    """
      Virtaulenvwrapper 是virtualenv的扩展包，用于更方便管理虚拟环境，它可以做：

      将所有虚拟环境整合在一个目录下
      管理（新增，删除，复制）虚拟环境
      快速切换虚拟环境

      ##  3. <a name='-1'></a>安装
      pip install virtualenvwrapper
      #pip3 install virtualenvwrapper -i https://pypi.tuna.tsinghua.edu.cn/simple

      ##  4. <a name='-1'></a>创建目录用来存放虚拟环境
      mkdir ~/.virtualenvs

      # 在.bashrc中添加 
      export WORKON_HOME=~/.virtualenvs
      source /usr/local/bin/virtualenvwrapper.sh
      source /Users/wangjinlong/opt/anaconda3/envs/py39/bin/virtualenvwrapper.sh

      之后就可以使用, 这样的好处是，所创建的所有虚拟环境都在~/.virtualenvs/目录下(便于管理)，只要记住环境名就可以轻松进入环境

      # 运行
      source ~/.bashrc
      workon:列出虚拟环境列表
      lsvirtualenv:同上
      ##  5. <a name='-1'></a>新建虚拟环境
      mkvirtualenv --python=版本文件路径 虚拟环境名  # 创建环境, 虚拟环境被创建在~/.virtualenvs/ 中
      #mkvirtualenv --python3=/Users/wangjinlong/opt/anaconda3/envs/py39/bin/python3 AI_learn
      workon [虚拟环境名称]:切换虚拟环境 # 进入虚拟环境：
      deactivate #离开虚拟环境
      rmvirtualenv deep_learn #删除虚拟环境
    """
    pass

  def other(self):
    """
      import venv
      venv.create('testevn')
    """
