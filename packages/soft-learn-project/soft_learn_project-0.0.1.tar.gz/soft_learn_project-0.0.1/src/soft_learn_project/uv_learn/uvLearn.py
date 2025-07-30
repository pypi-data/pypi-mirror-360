class UvLearn():
  def __init__(self) -> None:
    """https://realpython.com/python-uv/?utm_source=realpython&utm_medium=web&utm_campaign=related-post&utm_content=python-pyproject-toml
    https://realpython.com/python-uv/?utm_source=realpython&utm_medium=web&utm_campaign=related-post&utm_content=dependency-management-python-poetry

    uv doc: https://docs.astral.sh/uv/#python-versions

    uv是一个Python包和项目管理器，它将多个功能集成到一个工具中，为管理Python项目提供了一个全面的解决方案。
    uv用于快速安装依赖项、虚拟环境管理、Python版本管理和项目初始化，提高生产力和效率。
    uv可以构建Python包并将其发布到包存储库（如PyPI），从而支持从开发到发布的简化过程。
    Uv自动处理虚拟环境，根据需要创建和管理它们，以确保干净和隔离的项目依赖关系。
    ---
    最近，在Python工具生态系统中出现了一些使用Rust编程语言构建的令人兴奋的工具。ruff是一个python的检查器和代码格式化器，是这些工具中一个众所周知的流行示例。
    这些工具背后的主要思想是通过加快项目管理操作来加快Python工作流程。例如，Ruff的速度比Flake8和Black这样的代码格式化器快10到100倍。同样，对于包安装，uv比pip快10到100倍。
    此外，uv将pip、pip-tools、pipx、poetry、pyenv、twine、virtualenv等工具提供的大部分功能集成到一个工具中。因此，uv是一个一体化的解决方案。
    """
    pass

  def install(self):
    """_summary_
      brew install uv
      pipx install uv 
      curl -LsSf https://astral.sh/uv/install.sh | sh
    """
    pass

  def config(self):
    """
      1. 配置 uv pip 的源
        # 在 ~/.config/uv/uv.toml 中写入
        index-url = "https://pypi.tuna.tsinghua.edu.cn/simple"
      2. 配置 python 版本
        # 在~/.zshrc 中写入
        export UV_PYTHON=$(which python3)
        # 或者在运行时指定使用哪个 python
        uv run --python $(which python3) main.py 
    """
    pass

  def venv(self):
    """
      uv 的决策规则如下（截至 2025）：
      查找项目根目录（project root）：
      从当前目录向上查找 pyproject.toml、requirements.txt、uv.lock 等文件；
      第一个匹配的目录就被视为项目根；
      使用项目根目录下的 .venv：
      忽略子目录中其他 .venv；
      如果你显示指定 --python 或设置 UV_PYTHON，则使用指定解释器构建 .venv；
      如果找不到这些文件，则以当前目录为根创建 .venv。

      uv venv .venv  # 当前目录手动创建虚拟环境
      source .venv/bin/activate # 激活虚拟环境
      python3 -m ensurepip --upgrade # 安装pip 
      python3 -m pip install -e . # 安装包
      uv run main.py # 在虚拟环境中运行脚本 
    """
    pass

  def steps1_初始化(self):
    """
      1. 要使用uv创建和初始化Python项目，请导航到要存储项目的目录。在那里，你可以运行以下命令来创建和初始化项目：
        uv init rpcats
        注意：如果你想用uv开始管理一个现有的项目，然后导航到项目目录并运行以下命令：
        uv init
        这个命令将为您创建uv项目结构。它不会覆盖main.py文件（如果有的话），但是如果缺少该文件，它将创建该文件。它既不修改Git存储库，也不修改README。md文件。
      2. 测试运行项目的入口点脚本
        一旦创建了项目，就可以使用uv运行入口点脚本，默认情况下它是main.py文件。要运行该脚本，请执行以下命令：
        uv run main.py 
    """
    pass

  def steps2_依赖(self):
    """
      1. 添加和安装依赖项
        # 此命令会将 Requests 库添加到项目的依赖项中，并在项目的虚拟环境中安装该库。运行完成后，请检查 pyproject.toml 文件的内容： uv add 也会更新 uv.lock 文件中的版本信息，包括直接以来和传递依赖
        uv add requests 
        # 或者将现有 requirements.txt 文件中声明的依赖项导入到 uv 基础架构中。
        uv add -r requirements.txt 
        尽管 uv 有一个类似 pip 的替代接口，但你不应该使用它来安装依赖项，因为这些命令不会像 uv.lock 那样自动更新 pyproject.toml 文件或 uv add 。
      2. 升级和删除依赖项
        uv add --upgrade requests # 升级
        uv remove <package_name> # 删除依赖项
      3. 管理开发依赖
        uv add --dev pytest # 安装开发依赖 pytest 
      4. 锁定和同步环境 uv 使用 uv.lock 文件锁定项目的依赖项。
        锁定过程是将项目特定的依赖项捕获到锁文件中。这一过程使得在所有可能的配置中（包括 Python 版本和发行版、操作系统和架构）都能重现你的工作环境成为可能。
        相应地，同步是指将锁文件中所需的包安装到项目的开发环境中的过程。
        当你执行 uv run 时，项目会先被锁定和同步，然后再运行该命令。这种行为确保了你的项目环境始终是最新的。
        现在，假设你从 GitHub 仓库中拉取了 cat 应用，并想尝试运行它。在这种情况下，你将只有源代码和 uv 配置文件。你没有包含运行应用所需依赖的完整 Python 虚拟环境。
        要重现这种情况，你可以在项目根目录中删除 .venv/ 文件夹，然后让 uv 来完成这项工作：
        uv run main.py "Scottish Fold"
        uv pip list # 查看.venv 中安装的包 
        您可以使用以下命令显式地锁定并同步项目：
        uv lock
        uv sync
    """
    pass

  def steps3_配置项目(self):
    """
      1. Configuring the Project配置项目
        你的猫应用有一个命令行界面（CLI），因此你需要显式设置项目的入口脚本，以便构建系统能够正确设置应用的可执行文件。进入 pyproject.toml 文件并添加以下内容：
        [project.scripts]
        rpcats = "main:main"
        在这两行代码的帮助下，当有人安装你的应用时，他们可以从终端运行 rpcats 命令来执行 main.py 中的main() 函数。
    """
    pass

  def steps4_打包和发布包(self):
    """
      1. 配置
        接下来，你需要定义一个构建系统。在这个教程中，你将使用 Setuptools 作为构建系统。现在在你的 pyproject.toml 文件末尾添加以下几行：
        [build-system]
        requires = ["setuptools>=78.1.0", "wheel>=0.45.1"]
        build-backend = "setuptools.build_meta"
        第一行高亮的代码指定了构建系统需要的依赖项 setuptools 和 wheel 。第二行高亮的代码定义了构建后端。在 project.toml 文件中添加这两项后，你就可以为你的应用构建分发包了。
      2. 构建分发包
        uv build
        您还可以选择以下构建选项：
        uv build --sdist
        uv build --wheel
        第一个命令仅构建源分发包，而第二个命令构建二进制分发包。请注意，使用 uv build 且不带任何标志时，将同时构建源分发包和二进制分发包。
      3. 发布项目
        你可以手动编辑你的 pyproject.toml 文件，如下所示：
        [[tool.uv.index]]
        name = "testpypi"
        url = "https://test.pypi.org/simple/"
        publish-url = "https://test.pypi.org/legacy/"
        explicit = true
        上传到 TestPyPI： --index
        uv publish --index testpypi --token pypi-AgENdGVzdC5weXBpLm9yZwIkZGY2NTRmN2QtNWI5Zi00NTVmLTk4OGYtN2ZjNDkzMmRkNGM0AAIqWzMsIjNhZjI2M2I5LWI1ODctNDRmZS05NzdlLWRmNWNhZGYxZjZjYiJdAAAGIM7Gg_88Uohqsb2i5eoH5Ls18oZgWjwOy1Hq0Gq1jHn2

    """

  def steps5_测试(self):
    """
      要尝试这个应用，你需要在不同的目录中创建一个新的虚拟环境。因此，请在硬盘上的其他目录中打开一个终端窗口，然后运行以下命令：
      mkdir ~/tmp/abc_test
      cd ~/tmp/abc_test
      uv venv 
      source .venv/bin/activate
      python3 -m ensurepip --upgrade # 安装pip 
      uv pip install requests
      uv pip install -i https://test.pypi.org/simple/ abc_wjl
      uv run abc_wjl Persian
    """
    pass

  def exercise(self):
    """
      # 最好是在~/tmp 中测试, 否则父目录可能有 pyproject.toml 
      1. mkdir t1_rpcats
      2. cd t1_rpcats; uv init
      3. uv run main.py
      4. uv add requests 
      5. uv build
      6. uv publish --index testpypi --token pypi-AgENdGVzdC5weXBpLm9yZwIkZGY2NTRmN2QtNWI5Zi00NTVmLTk4OGYtN2ZjNDkzMmRkNGM0AAIqWzMsIjNhZjI2M2I5LWI1ODctNDRmZS05NzdlLWRmNWNhZGYxZjZjYiJdAAAGIM7Gg_88Uohqsb2i5eoH5Ls18oZgWjwOy1Hq0Gq1jHn2
    """
    pass
