class MembaLearn():
  def __init__(self):
    """# 我发现装上后 出问题， 谨慎安装，不要再base中安装
    * Mamba 是一个快速的 conda 包管理器替代工具，旨在提供比 conda 更快速的包解析和安装体验。它是用 C++ 编写的，利用了更高效的算法来解决依赖关系，因此能够大幅度提高包安装和环境创建的速度。
    - Mamba 的核心功能与 conda 相同，因此你可以几乎以相同的方式使用它，只是在性能上表现更好，尤其是在需要解决大量依赖的复杂环境时，Mamba 的速度优势非常明显。

    为什么使用 Mamba？
    1. 更快的包解析和依赖解决： Mamba 使用一个 C++ 实现的依赖解决器，这比 Python 实现的 conda 解决器要快得多。Mamba 在解决环境和包依赖时的速度比 conda 快 3 到 5 倍，甚至更多，特别是在处理大型环境和复杂依赖时。
    2. 兼容性： Mamba 完全兼容 conda，你可以用 Mamba 运行大多数 conda 命令，且不需要改变任何环境配置。Mamba 直接调用 conda 的频道和包，因此它可以无缝替代 conda，并使用相同的环境和包。
    3. 命令行界面一致： Mamba 保持与 conda 一致的命令行界面，只需要将 conda 替换为 mamba 即可。例如，conda install 变成 mamba install，conda create 变成 mamba create。

    """
    pass

  def install(self):
    """brew install micromamba
    # conda install mamba -c conda-forge
    """
    pass

  def config(self):
    """
      Please run the following to setup your shell:
      /opt/homebrew/opt/micromamba/bin/mamba shell init --shell <your-shell> --root-prefix ~/mamba
      and restart your terminal
    """
    pass

  def create_env(self):
    """
    1. mamba env create -n env_name --file jobflow_env.yaml
    2. mamba create -n myenv python=3.9 numpy pandas
    3. 删除环境: mamba env remove -n myenv
    4. 更新包: mamba update numpy

    """
    pass
