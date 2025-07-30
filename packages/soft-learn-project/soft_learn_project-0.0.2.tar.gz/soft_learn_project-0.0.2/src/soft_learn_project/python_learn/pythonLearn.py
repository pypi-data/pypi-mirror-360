
class YieldOrder():
  def __init__(self) -> None:
    """
    # 在函数中，yield 返回值后还能继续执行 return 返回一次后函数调用就结束了
    # 如果yield在函数中的for循环中，调用函数后，执行到yield 返回值，进行下一个循环继续返回值，而return 返回一次就结束了
    # 带有 yield 的函数不再是一个普通函数，而是一个生成器generator，可用于迭代
    # 带有 yield 的函数不再是一个普通函数，而是一个生成器generator，可用于迭代，工作原理同上。
    # yield 是一个类似 return的关键字，迭代一次遇到yield时就返回yield后面的值。重点是：下一次迭代时，从上一次迭代遇到的yield后面的代码开始执行。
    # 简要理解：yield就是 return 返回一个值，并且记住这个返回的位置，下次迭代就从这个位置后开始。
    """
    pass

  def fun1(self):
    yield 'ok'
    # return 'ok'

  def yield_test(self, n):
    for ii in range(n):
      # yield call(ii)
      yield ii * 10  # 返回的是迭代器
      print("ii=", ii)
      # return ii

  def call(self, k):
    return k * 2

  def mytest(self):
    # 使用for循环
    for i in self.yield_test(5):
      print('i=', i)


class ImportPackage():
  def __init__(self) -> None:
    """import sys
    print(sys.path)   # 查看路径, 输出是一个列表

    # 添加路径 方法1
    sys.path.append('/Users/wangjinlong/.')  

    # 添加路径 方法2
    # 编辑.zshrc 
    export PYTHONPATH=$PYTHONPATH:/Users/wangjinlong/my_linux/soft_learn/python3_learn/myModule  

    # 添加路径 方法3 
    # 在 /Users/wangjinlong/Library/Python/3.9/lib/python/site-packages 或者 /Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages
    # 目录下 (.pth 必须放在Python的某个site-packages目录里) 编辑.pth 文件,内容如下：
    /Users/wangjinlong/my_linux/soft_learn/python3_learn/mylearn/mk-模块/exercise  # 所添加的搜索路径
    /Users/wangjinlong
    #---- 当解释器启动时，.pth文件里列举出来的存在于文件系统的目录将被添加到sys.path。 # 注意.pth 是隐藏文件一开始可能不存在
    """
    pass

  def method(self):
    from scipy import stats
    import scipy.stats  # 还可以有这种导入方式, 这样就能获取stats的提示了


class PackageBuildPublish():
  def __init__(self):
    """
    https://packaging.python.org/en/latest/tutorials/packaging-projects/
    从 PEP 621 开始，Python 社区选择了 pyproject.toml 作为指定项目元数据的标准方式。
      build 和 Twine。这两个都是 PyPA 项目，是构建和上传包至 PyPI 的推荐工具。
      build 项目提供了一个构建前端，使构建您的包变得简单，同时生成源代码分发包和 wheel 分发包。作为一个前端，它实际上并不直接构建您的包，而是为 Setuptools 等构建后端提供了一个一致的接口。
    ---
    考虑为项目管理和打包提供单个命令行接口的打包工具，例如hatch、flit、pdm和poetry。 
      本例子使用了 build  和 twine 
      配置好 pyproject.toml 后可以
      pip install -e . # 本地安装

    如果需要与旧版构建或不支持某些打包标准的工具（例如 PEP 517 或 PEP 660）兼容，可以使用简单的`setup.py`文件。 可以在项目中添加 script 1 (在 pyproject.toml 中保持配置):
      from setuptools import setup
      setup()
    """
    pass

  def step0_准备工作(self):
    """
      0. https://test.pypi.org/account/register/ 你需要做的第一件事是在TestPyPI上注册一个帐户 并验证邮箱
        testpy
        PyPI recovery codes
        当前目录下的 cat _data.txt 
      1. python3 -m pip install --upgrade pip # 升级pip
      2. pip install hatchling
      3. pip show hatchling # 查看版本
      4. python3 -m pip install --upgrade build # 使用最新的build
      5. 安装 twine
      python3 -m pip install --upgrade twine
    """
    pass

  def step1_准备包(self):
    """
      准备分发项目的文件。
      packaging_tutorial/
        ├── LICENSE
        ├── pyproject.toml
        ├── README.md
        ├── src/
        │   └── example_package_YOUR_USERNAME_HERE/
        │       ├── __init__.py
        │       └── example.py
        └── tests/
    """

  def step2_config_pyproject(self):
    """pyproject.toml 文件中输入
    1.  选择打包后端: 例如
      [build-system]
      requires = ["setuptools >= 77.0.3"]
      build-backend = "setuptools.build_meta"
      ---
      [build-system]
      requires = ["hatchling >= 1.26"]
      build-backend = "hatchling.build"
    2. 配置元数据 Configuring metadata
      [project]
      name = "example_package_YOUR_USERNAME_HERE"
      version = "0.0.1"
      authors = [
        { name="Example Author", email="author@example.com" },
      ]
      description = "A small example package"
      readme = "README.md"
      requires-python = ">=3.9"
      classifiers = [
          "Programming Language :: Python :: 3",
          "Operating System :: OS Independent",
      ]
      license = "MIT"
      license-files = ["LICEN[CS]E*"]

      [project.urls]
      Homepage = "https://github.com/pypa/sampleproject"
      Issues = "https://github.com/pypa/sampleproject/issues"

    """
    pass

  def step3_readme(self):
    """
    Creating README.md
    # Example Package
      This is a simple example package. You can use
      [GitHub-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
      to write your content.
    """
    pass

  def step4_build(self):
    """生成发行版存档
    python3 -m pip install --upgrade build
    python3 -m build
    会生成
      dist/
      ├── example_package_YOUR_USERNAME_HERE-0.0.1-py3-none-any.whl
      └── example_package_YOUR_USERNAME_HERE-0.0.1.tar.gz

    """
    pass

  def setp5_upload(self):
    """上传发行版存档
    1. 需要注册
      https://test.pypi.org/account/register/ 
    2. 上传 
    python3 -m pip install --upgrade twine
    python3 -m twine upload --repository testpypi dist/*
    3. 测试后正式上传
      在 https://pypi.org 上注册一个帐户-注意，这是两个独立的服务器，并且来自测试服务器的登录详细信息不与主服务器共享。
      在生产环境中上传包，就不需要指定——repository；默认情况下，包将上传到https://pypi.org/。
    4. 免秘钥
      将该内容写入到 ~/.pypirc
      cat __file__  _data.txt 
      ---
      配置完成后，您可以直接运行, 而无需手动输入密码。
      python3 -m twine upload --repository testpypi dist/*
    """
    pass

  def step6_install(self):
    """
    安装新上传的包, 建议创建一个虚拟环境并从TestPyPI安装你的包。
      python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps example-package-YOUR-USERNAME-HERE
      这个例子使用——index-url标志来指定TestPyPI而不是live PyPI。另外，它指定了——no-deps。由于TestPyPI没有与活动的PyPI相同的包，因此尝试安装依赖项可能会失败或安装一些意外的东西。虽然我们的示例包没有任何依赖项，但在使用TestPyPI时避免安装依赖项是一个很好的做法。

      1. 安装新上传的包
        1. python3 -m venv env_test # 建立虚拟环境
        2. source env_test/bin/activate # 激活
        3. python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps example-package-wjl  # 安装包
      2. 测试
        from example_package_wjl import example
        example.add_one(2)
        deactivate
    """
    pass

  def other_method(self):
    """
    1. 准备
      my_package/                # 项目根目录
      ├── my_package/            # 包主目录（与项目同名）
      │   ├── __init__.py        # 标识为Python包（可为空文件）
      │   ├── module1.py         # 你的代码模块
      │   └── module2.py
      ├── setup.py               # 打包配置文件（关键！）
      ├── README.md              # 项目说明（可选）
      └── requirements.txt       # 依赖列表（可选）
    2. 安装
      python setup.py  # sdist bdist_wheel
      pip install dist/my_package-0.1.0-py3-none-any.whl
      pip install dist/mytest1-0.1.0.tar.gz # 或者这个
      pip install -e .
    3. 上传
    python3 -m twine upload dist/* 
    python3 -m twine upload --repository testpypi dist/* # 上传
    pip install my_package # 从PyPi安装
    python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps example-package-wjl  # testpypi 
    # 从GitHub安装
    pip install git+https://gitee.com/wangjl580/packaging_tutorial.git
    pip install git+https://gitee.com/wangjl580/ase_ext.git
      测试： from mytest2 import example
      example.hello().say_hello()
      from ase_ext import aseLearn
      aseLearn.AseFeatures().Model.get_atoms_bulk_bcc110()
    # 从本地压缩包安装
    pip install my_package-0.1.0.tar.gz
    """
    pass


class PackageBuildPublish_RealPython():
  def __init__(self) -> None:
    """这些工具旨在简化管理Python项目的过程，并提供更统一的体验。它们甚至提供了自己的构建后端。这些工具包括：
    Hatch (PyPA project)
    PDM
    Poetry
    uv"""
    pass

  def realpython(self):
    """
    https://realpython.com/pypi-publish-python-package/
    https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html # 用于参考
    """
    pass

  def about_dependents(self):
    """
    关于依赖项, 依赖项列表如何写? 利用pip-tools 查看 requirements.txt 
      pip-tools项目是管理固定依赖项的好方法。它附带一个pip-compile命令，可以创建或更新完整的依赖项列表。
      1. 安装pip-tools
      pip install pip-tools
      2. 列出依赖项
      pip-compile pyproject.toml # 或者 pip-compile --output-file requirements.txt pyproject.toml
      3. 安装依赖项
      pip-sync  # 或者 pip install -r requirements.txt 
      # 4. 更新依赖项
      # pip-compile --upgrade --output-file requirements.txt pyproject.toml
      从 requirements.txt 迁移
      ---
      # 使用pip-chill检查实际使用的依赖（而非全部安装的）
      pip install pip-chill
      pip-chill --no-version > minimal_requirements.txt
      ---
      pip install pipreqs pigar
      # 生成依赖列表
      pipreqs . --force    # 生成requirements.txt
      pigar                 # 生成Pigar的依赖分析报告
      pigar generate src/reader_wjl_test # ?
      ---
      使用 poetry add 命令迁移依赖：
      # 导出所有依赖
      poetry add $(cat requirements.txt)

    """
    pass

  def about_Scriv(self):
    """
    Scriv 是一个用于**管理项目变更记录（changelog）**的工具。
      它的核心用途是：
      🧠 自动生成结构清晰的 CHANGELOG 文件，适用于 Python 项目，尤其结合 Git 提交、版本发布一起使用。
      安装：
      pip install scriv
      初始化配置：
      在 pyproject.toml 中添加：
      [tool.scriv]
      format = "md"
      version = "literal"
      创建变更片段（fragment）：
      scriv create 
      这会生成一个小文件，例如：changelog.d/20250620.fix-login-bug.md，你可以写入：
      - Fix login bug when user has no email set
      发布时合并：
      scriv collect
      会把所有 fragment 自动拼到 CHANGELOG.md，然后 fragment 文件会被删除。

      🔧 示例配置（pyproject.toml）
      [tool.scriv]
      format = "md"
      fragment_directory = "changelog.d"
      output_file = "CHANGELOG.md"
      version = "literal"
      categories = ["Added", "Changed", "Fixed", "Removed"]
    """
    pass

  def about_test(self):
    """
    tests 
      您可以在《Effective Python testing With Pytest》中了解更多关于测试的知识，并在《使用TDD在Python中构建哈希表》和《Python实践问题：解析CSV文件》中获得一些测试驱动开发（TDD）的实践经验。 https://realpython.com/pytest-python-testing/ 
      它们通常只对开发人员感兴趣，所以它们不应该包含在通过PyPI分发的包中。
    """
    pass

  def about_version_bumpver(self):
    """
    Version Your Package
      PyPI将只允许您上传一次特定版本的软件包。换句话说，如果您想在PyPI上更新您的包，那么您需要首先增加版本号。
      您将版本指定为三个数字组件，例如1.2.3。这些组件分别被称为MAJOR、MINOR和PATCH。
      1. 当您进行不兼容的API更改时，增加MAJOR版本。
      2. 当您以向后兼容的方式添加功能时，增加MINOR版本。
      3. 当您进行向后兼容的错误修复时，增加PATCH版本。(源)
      您希望在项目中的不同文件中指定版本号。例如，版本号在pyproject.toml 和reader/__init__.py 为了确保版本号保持一致，您可以使用BumpVer之类的工具。
      BumpVer允许你直接将版本号写入文件中，然后根据需要进行更新。作为一个例子，你可以安装和集成BumpVer到你的项目如下：
      python -m pip install bumpver
      bumpver init # 在pyproject.toml 中创建一个节。它允许您为您的项目配置工具。根据您的需要，您可能需要更改许多默认设置。要使BumpVer正常工作，您必须在file_patterns子句中指定包含您的版本号的所有文件。注意，BumpVer与Git配合得很好，可以在更新版本号时自动提交、标记和推送。
      bumpver init --file-patterns pyproject.toml --file-patterns reader/__init__.py --tag-pattern "{version}" 
      ```shell
        [tool.bumpver]
        current_version = "1.2.19"
        version_pattern = "MAJOR.MINOR.PATCH"
        commit_message = "bump version {old_version} -> {new_version}"
        tag_message = "{new_version}"
        tag_scope = "default"
        pre_commit_hook = ""
        post_commit_hook = ""
        commit = false
        tag = false
        push = false 

        [tool.bumpver.file_patterns]
        "pyproject.toml" = [
            'current_version = "{version}"',
        ]
        "src/reader/__init__.py" = ["{version}"]
        "src/reader/__main__.py" = ["{version}"]
      ```

      git init; git add .; git commit -m "init"; git tag -a 0.1.0 -m "0.1.0"
      bumpver show 
      bumpver update --patch |--minor |--major  设置好配置后，可以使用一个命令在所有文件中更改版本。例如，要增加reader的MINOR版本，
    """
    pass

  def about_readme(self):
    """
    readme.md 
      在向世界发布包之前，您应该添加一些文档。根据您的项目，您的文档可以小到单个README文件，也可以像包含教程，示例库和API参考的完整网页一样全面。
      至少，您应该在项目中包含一个README文件。一个好的自述文件应该快速描述你的项目，以及解释如何安装和使用你的包。通常，您希望在pyproject.toml的README键中引用您的README。这也将显示PyPI项目页面上的信息。
      对于较大的项目，您可能希望提供比单个文件更大的文档。在这种情况下，您可以将文档托管在GitHub或Read the Docs等网站上，并从PyPI项目页面链接到它。
      [project.urls]
      Homepage = "https://github.com/realpython/reader" # 您可以通过在项目中指定其他url链接到它们。pyproject.toml中的url表。在本例中，url部分用于链接到阅读器GitHub存储库。
    """
    pass

  def about_license(self):
    """
    _summary9. 授权您的软件包
      您应该在您的项目中添加一个名为LICENSE的文件，其中包含您选择的许可证的文本。然后可以在pyproject.toml 中引用该文件, 使许可证在PyPI上可见。 
    """
    pass

  def realpython_step_method_1_realpython_reader(self):
    """
    1. 给包起个PyPI 名字也是安装时的名字 python -m pip install realpython-reader, PyPI名称不需要与包名称匹配。这里，包的名称仍然是reader，这是你在导入包时需要使用的名称：  有时您需要为您的包使用不同的名称。但是，如果包名称和PyPI名称相同，则可以使用户的操作更简单
    2. 配置包
      1. 构建系统的配置
      2. 包的配置
      本教程将重点介绍如何使用setuptools作为构建系统。不过，稍后您将学习如何使用Flit和Poetry等替代品。
      简化构建: https://realpython.com/python-pyproject-toml/

    3. 必须包含在 pyproject.toml 中的最小信息是这样的：
      [project]
      name = "realpython-reader" # PyPI 的名字
      version = "1.0.0"
      --- 下面是可选的, 最好加上 
      description = "Read the latest Real Python tutorials"
      readme = "README.md"
      authors = [{ name = "Real Python", email = "info@realpython.com" }]
      license = { file = "LICENSE" } 
      # 分类器使用分类器列表描述项目。您应该使用这些，因为它们使您的项目更易于搜索。
      classifiers = [
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
      ]
      # Dependencies列出了你的包对第三方库的依赖。Reader依赖于feedparser、html2text和tomli，所以在这里列出了它们。 不要使用 == 固定某个特定版本
      dependencies = [
          "feedparser >= 5.2.0", # 必须是5.2.0或更高版本。
          "html2text",  # 可以是任何版本。
          'tomli; python_version < "3.11"', # tomli可以是任何版本，但仅在Python 3.10或更早的版本上必需。
          # 依赖 Git 仓库（如你的 Gitee 项目）
          "soft-learn-project @ git+https://gitee.com/wangjl580/soft_learn_project.git@main",
          本地路径依赖（开发时调试用）
          "soft-learn-project @ file:///本地路径/to/soft_learn_project",
      ]
      requires-python = ">=3.9"
      # 添加了一些链接，您可以使用这些链接向用户显示有关包的其他信息。您可以在这里包含几个链接。
      [project.urls]
      Homepage = "https://github.com/realpython/reader"
      # 创建调用包内函数的命令行脚本。这里，新的realpython命令在读取器中调用main().__main__模块。 构建后端读取来创建命令行的可执行命令: realpython  值为"reader.__main__:main"。你的构建后端将创建一个可执行命令来运行你刚刚安装的 reader 的__main__子模块中的main（）函数。 这些值可以自定义为您想要的任何值，并且您可以添加任意数量的值，只要它们指向Python可调用对象，例如函数。您只需要确保目标可调用对象是一个过程—它不应该接受参数。
      [project.scripts]
      realpython = "reader.__main__:main"  # reader/__main__.py:main() 是个函数
      # 关于PyPI的所有信息都来自pyproject.toml和README.md. 例如，版本号基于project中的version = "1.0.0"行。而Read最新的Real Python教程是从description中复制的。 

    5. [project.optional-dependencies] 的解释
      [project.optional-dependencies]
      dev = ["black", "bumpver", "isort", "pip-tools", "pytest"] # 这些都是包名
      例如，你可以通过以下方式安装reader的额外dev依赖项：
      python -m pip install "realpython-reader[dev]"
      python -m pip install -e ".[dev]"
      当绑定pip-compile的依赖项时，你也可以使用——extra命令行选项包括可选的依赖项：
      pip-compile --extra dev pyproject.toml  # 这会创建一个固定的requirements.txt文件，其中包括您的常规依赖项和开发依赖项。

    8. 向包中添加资源文件

    10. 在本地安装软件包
      1. 注意：通常，pip会进行常规安装，将一个包放入site-packages/文件夹中。如果您安装本地项目，那么源代码将被复制到site-packages/。这样做的结果是，您稍后所做的更改将不会生效。你需要先重新安装你的软件包。
      在开发过程中，这可能既无效又令人沮丧。Editable通过直接链接到您的源代码来安装解决这个问题的工作。 
      python -m pip install -e . # 注意命令末尾的“.”。它是命令的必要部分，并告诉pip您希望安装位于当前工作目录中的包。通常，这应该是包含pyproject.toml 文件的目录的路径。
      2. 注意：您可能会得到一个错误消息，说“项目文件有一个' pyproject.toml及其构建后端缺少‘ build_editable ’钩子。” 这是由于Setuptools对PEP 660的支持存在限制。你可以通过添加一个名为setup.py的文件来解决这个问题，其中包含以下内容：
      # setup.py
      from setuptools import setup
      setup()
      3. 安装好后的测试
        from reader import feed
        feed.get_titles()
        ---
        python3 -m reader

    11. 将包发布到PyPI
      1. 要构建并将包上传到PyPI，您将使用build和Twine两个工具。你可以像往常一样使用pip安装它们：
        python -m pip install build twine
      2. 构建您的包
        PyPI上的包不是作为纯源代码分发的。相反，它们被打包到分发包中。发行包最常见的格式是源代码存档和Python轮。
      3. 要为你的包创建一个源存档和一个轮子，你可以使用Build：
        python -m build
        wheel文件实际上是一个具有不同扩展名的ZIP文件。您可以解压缩它，并检查其内容如下：
        cd dist/
        unzip realpython_reader-1.0.0-py3-none-any.whl -d reader-whl
        tree reader-whl/
      4. Twine还可以检查您的包描述是否会在PyPI上正确渲染。你可以对dist中创建的文件执行twine check：
        twine check dist/*
      5. Upload Your Package
        # twine upload dist/* # 上传到pypi 
        twine upload -r testpypi dist/*
      6. 安装 
        python -m pip install -i https://test.pypi.org/simple realpython-reader-wjl

    """
    pass

  def realpython_step_method_flit(self):
    """
    Flit是一个很棒的小项目，当涉及到包装时，它的目标是“让简单的事情变得简单”。Flit不支持像创建C扩展那样的高级包，通常，在设置包时它不会给您提供很多选择。相反，Flit赞同这样一种理念，即应该有一个明显的工作流来发布包。 注意：您不能同时使用Setuptools和Flit配置包。为了测试本节中的工作流，您应该将Setuptools配置安全地存储在版本控制系统中，然后删除pyproject.toml中的build-system和project部分。
    1. 安装 
      python -m pip install flit
    2. 配置 
      flit init
    3. 构建
      flit build # 这将创建一个源代码归档文件和一个wheel，类似于前面使用python -m build所做的操作。如果您愿意，也可以使用Build。
    4. 发布 
      要将包上传到PyPI，可以像前面一样使用Twine。但是，你也可以直接使用Flit：
      flit publish --repository testpypi 
      flit publish

    """
    pass

  def realpython_step_method_Poetry(self):
    from soft_learn_project import poetryLearn
    import importlib
    importlib.reload(poetryLearn)
    poetryLearn.PoetryLearn().realpython_step_method_Poetry()
    pass


class PythonLearn():
  def __init__(self) -> None:
    r"""注意注释中不能出现 \u 开头的  否则需要前面加上转义 r 
    https://packaging.python.org/en/latest/overview/# 
    https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-and-using-virtual-environments
    """
    from soft_learn_project import pipLearn
    self.pipLearn = pipLearn

    pass

  def install(self):
    """
      1. 安装
        brew install python@3.11  # 是核心 Python 解释器和标准库，但默认不包含 tkinter。
        brew install python-tk@3.11 #  是一个额外的包，为 Homebrew 安装的 Python 提供 GUI 支持（tkinter）
        这样安装的python 才有tkinter
      2. 测试
        python3 --version
        python3 -m tkinter # 弹出窗口就表明成功
    """
    pass

  def python_m_order(self):
    """ 
    知识点:
    # python3 -m 
    python3 hello.py 这样运行
    python3 -m hello # 或者 
    python3 -m 包名|模块名  # 只要包或者模块在python 使用-m的一个优点是，它允许您调用Python路径中的所有模块，包括那些内置在Python中的模块。 使用-m的另一个优点是它既适用于模块，也适用于包。 Python如何决定运行该目录中的哪些代码？它查找一个名为__main__.py的文件。如果存在这样的文件，则执行它。如果不存在，则打印错误消息： 
    如果你正在创建一个应该被执行的包，那么你应该包含一个__main__.py文件。您还可以按照Rich的示例使用python -m Rich来演示包的功能。 
    """
    pass

  def project_packaging_poetry(self):
    """使用 poetry打包
    """
    from soft_learn_project import poetryLearn
    poetryLearn()
    pass

  def project_packaging_uv(self):
    from soft_learn_project.uv_learn import uvLearn
    pass

  def package_构建和发行(self):
    from soft_learn_project.setuptools_learn import setuptoolsLearn

    pass
