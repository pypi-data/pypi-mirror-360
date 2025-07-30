class PoetryLearn():
  def __init__(self) -> None:
    """
    https://realpython.com/dependency-management-python-poetry/?utm_source=realpython&utm_medium=web&utm_campaign=related-post&utm_content=python-pyproject-toml

    https://python-poetry.org/docs/pyproject#packages  # 官方文档
    ---
    诗歌指挥部	解释
      $ poetry --version	显示您的 Poetry 安装的版本。
      $ poetry new	创建一个新的诗歌项目。
      $ poetry init	将诗歌添加到现有项目中。
      $ poetry run	在 Poetry 管理的虚拟环境中执行命令。
      $ poetry add	添加一个包pyproject.toml并安装它。
      $ poetry update	更新项目的依赖项。
      $ poetry install	安装依赖项。
      $ poetry show	列出已安装的软件包。
      $ poetry lock	将依赖项的最新版本固定到poetry.lock。
      $ poetry lock --no-update	刷新poetry.lock文件而不更新任何依赖版本。
      $ poetry check	证实pyproject.toml。
      $ poetry config --list	显示诗歌配置。
      $ poetry env list	列出项目的虚拟环境。
      $ poetry export	导出poetry.lock为其他格式。
      您可以查看Poetry CLI 文档，了解有关上述命令以及 Poetry 提供的许多其他命令的更多信息。您也可以运行它，poetry --help直接在终端中查看信息！
    """
    pass

  def install(self):
    """
      安装
        python3 -m pip install poetry  
        pipx install poetry # 将把Poetry安装到一个专用的虚拟环境中，该环境不会与其他Python包共享。
    """
    pass

  def venv(self):
    """_summary_
    1. 先停用之前的虚拟环境
      deactivate
    2. 创建虚拟环境
      poetry env use python3 # 指定路径
    3. 查看
      poetry env info
      poetry env list
      Poetry指示当前选择连接到项目的哪个虚拟环境作为默认环境。虽然它说激活了，但在传统意义上，相应的虚拟环境实际上并没有在您的shell中激活。相反，当您运行其中一个Poetry命令时，Poetry将在子进程中临时激活该虚拟环境。 
      poetry env use <python> # 在现有环境之间切换，您可以再次发出
      poetry env remove --all  # 要快速删除与项目相关的所有环境，请运行
    """
    pass

  def dependency(self):
    """
      声明运行时依赖项
      而且它实际上不会在项目的虚拟环境中安装任何东西。这就是诗的命令行再次发挥作用的地方。
      运行poetry add命令将自动更新您的pyproject。使用新的依赖项导入Toml文件，并同时安装包。事实上，你甚至可以一次指定多个包：
      在添加前先安装, 之后 poetry add numpy 会变快
      poetry run python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple numpy  
      poetry add requests beautifulsoup4 # 这将找到PyPI上这两个依赖项的最新版本，将它们安装到相应的虚拟环境中，并在pyproject.toml 中插入两个声明。
      dependencies = [
      "requests (>=2.32.4,<3.0.0)",
      "beautifulsoup4 (>=4.13.4,<5.0.0)"
      ]
      请注意版本说明符前的插入符号（^），它表示Poetry可以自由安装与版本字符串最左边的非零数字匹配的任何版本。例如，如果Requests库发布了一个新版本2.99.99，那么Poetry将认为它是您项目的可接受候选。然而，3.0版本是不允许的。
      poetry remove requests # 删除包

      将一些依赖项添加到一个名为dev的组，并将一些依赖项添加到另一个名为test的组：
        poetry add --group dev black flake8 isort mypy pylint
        poetry add --group test pytest faker
      除此之外，您还可以将单个软件包添加为可选的，以让用户选择是否安装它们
        poetry add --optional mysqlclient
      更新
        poetry update requests beautifulsoup4 # 或者 poetry add requests@latest

      将项目的依赖项显示为树时，您将确切地知道哪些是您的项目直接使用的，哪些是它们的传递依赖项：
        poetry show --tree # 
      从 Poetry 导出依赖项
      poetry run python -m pip freeze > requirements.txt
    """
    pass

  def steps(self):
    r"""
      Poetry
      诗歌是另一个可以用来构建和上传软件包的工具。与Flit相比，Poetry有更多的特性可以在包的开发过程中提供帮助，包括强大的依赖项管理。注意：您不能同时使用Setuptools和Poetry配置您的包。为了测试本节中的工作流，您应该将Setuptools配置安全地存储在版本控制系统中，然后删除pyproject.toml中的build-system和project部分。
      Setuptools 通过 setup.py/setup.cfg + pyproject.toml 中的 [build-system] 工作
      Poetry 通过 pyproject.toml 中的 [tool.poetry] 工作, 当两者同时在项目中存在时，会产生配置冲突（如构建系统不知道该使用哪种方式打包）
      也可以一步到位： 

      2. 初始化
        poetry new reader_wjl_test
        poetry new poetryLearn-project --name poetryLearn # 你可以选择传递——name参数，它允许你为Python包指定一个不同于你的项目文件夹的名字：  默认为 src 布局 也可以指定平面  --flat 
        poetry init # 这将创建一个pyproject.tmol 基于您对有关包的问题的回答。
      3. 用诗歌安装你的软件包
        想象一下，您刚刚从GitHub克隆了一个带有rp-poetry项目的Git存储库，并且在没有虚拟环境的情况下重新开始。为了模拟这一点，你可以删除一些Poetry的元数据和与项目相关的任何虚拟环境：
        rm poetry.lock
        poetry env remove --all
        如果你是一个想要为这个项目做出贡献的开发者，那么你可以在rp-poetry/文件夹中执行诗歌安装命令来开始：
        poetry install
        poetry run python -c "import requests" # 测试虚拟环境安装的包
        现在，您可以使用 Poetry 提供的所有命令了。有了pyproject.toml文件，您就可以从隔离的虚拟环境运行脚本了：
        poetry run python hello.py
      4. 构建
        poetry build
      5. 发布
        1. 首先添加PyPI仓库配置：
        poetry config repositories.pypi https://upload.pypi.org/legacy/
        2. 然后设置PyPI的API令牌（从.pypirc文件中可以看到您已有令牌）
        poetry config pypi-token.pypi pypi-AgEIcHlwaS5vcmcCJDM5Zjc1YmIxLTFiZmEtNDdlMS05YzA2LWI0MTljNzAwOGU1OAACKlszLCJmMDAzYjBkNC1kZTcwLTQ1ODktOGM5ZS1lOThmYTcwOTVlMDgiXQAABiBEu9GNyjz2Y9kUw_nz2n7EejV1_dReUQzTYQgAl149bw
        3. 发布
        poetry publish --repository pypi
        ---
        或者使用twine上传您的软件包：
        twine upload -r pypi dist/* --verbose
        ----对于 testpypi 
        1. poetry config repositories.testpypi https://test.pypi.org/legacy/
        2. poetry config pypi-token.testpypi pypi-AgENdGVzdC5weXBpLm9yZwIkZGY2NTRmN2QtNWI5Zi00NTVmLTk4OGYtN2ZjNDkzMmRkNGM0AAIqWzMsIjNhZjI2M2I5LWI1ODctNDRmZS05NzdlLWRmNWNhZGYxZjZjYiJdAAAGIM7Gg_88Uohqsb2i5eoH5Ls18oZgWjwOy1Hq0Gq1jHn2
        3. poetry publish --repository testpypi --verbose
      6. 测试
        pip install -i https://pypi.org/simple/ ase-util # 不用这个网址可能镜像源更新不及时
        pip install -i https://test.pypi.org/simple/ ase-util 
    """
    print('xok')
    return None

  def example(self):
    """_summary_
    # 创建项目
    poetry new abc_test
    # 进入目录
    cd abc_test 
    # 创建虚拟环境, 查看
    poetry env use python3 
    poetry env info
    poetry env list
    # 在虚拟环境中安装依赖
    poetry run python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple numpy
    # 安装依赖并在 pyproject.tmol 中修改依赖
    poetry add numpy 
    # 安装到虚拟环境
    poetry install
    poetry run pip list |grep abc_test
    poetry run python -c "import abc_test"
    # 安装
    python3 -m pip install -e .
    pip list |grep abc_test
    import abc_test # 测试
    # 测试
    poetry check
    # 构建包
    poetry build
    # 发布
    poetry publish --repository testpypi
    """
    pass
