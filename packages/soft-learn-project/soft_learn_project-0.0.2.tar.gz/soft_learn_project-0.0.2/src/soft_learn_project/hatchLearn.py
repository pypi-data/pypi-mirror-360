class HatchLearn:
  def __init__(self):
    pass

  def install(self):
    """
      建议使用 pipx 或 condax 
        允许在隔离环境中全局安装 Python 应用程序。
        pipx install hatch
        brew install hatch
        conda install -c conda-forge hatch
    """
    pass

  def config(self):
    """
      Hatch 能识别的所有项目特定配置可以在 `pyproject.toml` 文件中定义，或者在名为 `hatch.toml` 的文件中定义，其中选项不在 `tool.hatch` 表格内：
      toml example:
        option = "..."
        [table1]
        option = "..."
        [table2]
        option = "..."
      --- 或者
        option = "..."
        table1.option = "..."
        table2.option = "..."
    """
    pass

  def steps1_初始化(self):
    """
      新项目 ¶
        假设你想创建一个名为 Hatch Demo 的项目。你可以运行：
        hatch new "Hatch-Demo"
      现有项目 ¶
        要初始化现有项目，请进入包含项目的目录并运行以下命令：
        hatch new --init
    """
    pass

  def step2_env(self):
    """
      环境旨在提供隔离的工作空间，用于测试、构建文档或项目所需的任何其他工作。
      创建 ¶
        你可以使用 env create 命令创建环境。让我们进入我们在 设置阶段 创建的项目的目录：
        cd /Users/wangjinlong/job/tmp/hatch-demo # 在创建的项目中
        hatch env create # 可以创建默认环境 default
      进入环境
        你可以使用 shell 命令在环境中启动一个 shell。
        $ hatch shell
      现在确认项目已安装：
        (hatch-demo) $ pip show hatch-demo # 会发现刚创建的项目已经安装到环境中, 而且是可编辑模式
      查看你的环境中的 Python 安装位置：
        (hatch-demo) $ python -c "import sys;print(sys.executable)"
      离开该环境
        exit
      ---
      命令执行 ¶
        `run` 命令允许你在环境中执行命令，就好像你已经进入了该环境一样。例如，运行以下命令将输出与之前相同的结果：
        hatch run python -c "import sys;print(sys.executable)"
        hatch run test:pytest # 要访问 `test` 环境并运行 `pytest`，可以执行：
      配置环境 htach.toml 文件中 
        配置默认环境
          [envs.default]
          dependencies = [
            "pydantic",
            "numpy",
          ]
        创建自定义环境, 环境名: test 
          [envs.test]
          dependencies = [
            "pytest",
            "pytest-cov"
          ]
      当你第一次调用测试环境时，Hatch 将：
        创建该环境
        将你的项目及其依赖项（默认情况下）以 开发模式 安装到该环境中。
        安装环境的 依赖项
      查看当前环境 ¶
        hatch env show
        hatch env find test  # 要查看当前环境的位置
    """
    pass

  def steps3_依赖项(self):
    """
      Hatch 确保环境始终与当前定义的项目依赖项（如果已安装并在开发模式下）和环境依赖项兼容。
      要将 `cowsay` 作为依赖项添加，打开 `pyproject.toml` 并将其添加到 `dependencies` 数组中：
        dependencies = ["cowsay"]
      此依赖项将在下次启动终端或运行命令时被安装。例如：
        hatch run cowsay -t "Hello, world\!"
    """
    pass

  def steps4_版本控制(self):
    """
      ---
        [project]
        name = "hatch-demo"
        dynamic = ["version"]  # 这里已经给出了动态设置版本
      ---
      当版本未静态设置时，配置定义在 tool.hatch.version 表中, 默认模式查找名为 __version__ 或 VERSION 的变量，该变量被设置为包含版本的字符串，可选地以小写字母 v 开头。
        [tool.hatch.version]
        path = "src/hatch_demo/__about__.py"
      显示当前版本
        hatch version
      更新 
        hatch version "0.0.3"
        与其显式设置版本，你可以选择用于递增版本的 段 的名称：
        $ hatch version minor
        Old: 0.1.0
        New: 0.2.0
    """

    pass

  def steps5_build(self):
    """
      构建配置使用 tool.hatch.build 表进行。每个 目标 由 tool.hatch.build.targets 中的一个部分定义，例如：
        [tool.hatch.build.targets.sdist]
        exclude = [
          "/.github",
          "/docs",
        ]

        [tool.hatch.build.targets.wheel]
        packages = ["src/foo"]
      构建 
        不带任何参数调用 build 命令将构建 sdist 和 wheel 目标：
        $ hatch build
        要仅构建特定的目标，可以使用 -t/--target 选项：
        $ hatch build -t wheel
    """
    pass

  def steps6_publis(self):
    """
      查看发布文档：publishing。
        选项 ¶
        标志	配置名称	描述
        -r/--repo	repo	用于发布构建产物的仓库
        -u/--user	user	用于认证的用户
        -a/--auth	auth	用于认证的凭据
        --ca-cert	ca-cert	CA 证书路径
        --client-cert	client-cert	客户端证书路径，可选地包含私钥
        --client-key	client-key	客户端证书的私钥路径
      仓库 ¶
        所有顶级选项可以通过 repos 表进行覆盖，每个仓库需要一个必需的 url 属性。以下显示了默认配置：
        config.toml
        [publish.index.repos.main]
        url = "https://upload.pypi.org/legacy/"
        [publish.index.repos.test]
        url = "https://test.pypi.org/legacy/"
      构件选择
        默认情况下，项目根目录下的 `dist` 文件夹将被使用：
        hatch publish -r testpypi

    """
    pass

  def exercise(self):
    """
      hatch new "Hatch-Demo_wjl1"
      cd hatch-demo-wjl1 
      hatch build 
      hatch publish -r test
    """
    pass
