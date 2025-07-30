class PyenvLearn():
  def __init__():
    """https://github.com/pyenv/pyenv?tab=readme-ov-file#a-getting-pyenv
    """
    pass

  def install(self):
    """
      brew update
      brew install pyenv
      升级
        如果你是通过 Homebrew 安装的 Pyenv，请使用以下命令升级：
        brew upgrade pyenv
      卸载 pyenv
        pyenv 的简洁性使其很容易临时禁用或从系统中卸载。
        要禁用 Pyenv 管理你的 Python 版本，只需从你的 shell 启动配置中移除 `pyenv init` 的调用。这将从 `PATH` 中移除 Pyenv 的 shim 目录，并且未来如 `python` 的调用将执行系统的 Python 版本，就像在使用 Pyenv 之前一样。
        `pyenv` 仍然可以在命令行中使用，但你的 Python 应用程序不会受到版本切换的影响。
        要完全卸载 Pyenv，请从你的 shell 启动配置中删除所有 Pyenv 配置行，然后删除其根目录。这将删除在 `$(pyenv root)/versions/` 目录下安装的所有 Python 版本：
        rm -rf $(pyenv root)
        如果你是通过包管理器安装了 Pyenv，在最终步骤中，请执行 Pyenv 包的卸载。例如，对于 Homebrew：
        brew uninstall pyenv
    """
    pass

  def config(self):
    """
      1. zsh 配置
      echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
      echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
      echo 'eval "$(pyenv init - zsh)"' >> ~/.zshrc
    """
    pass

  def steps1_python版本(self):
    """
      切换测试 
      pyenv global 3.13;python3 --version;which python3
      ---
      1. 安装额外的 Python 版本
        pyenv install 3.10.4  # 安装指定版本
        pyenv install 3.10   # 安装并切换到最新的3.10版本：
        ---或者 手动下载Python源码包 ：
        wget https://www.python.org/ftp/python/3.10.18/Python-3.10.18.tar.xz
        mv Python-3.10.18.tar.xz $(pyenv root)/cache/  # /Users/wangjinlong/.pyenv/cache/
        pyenv install 3.10.18

      2. 切换版本
        要选择一个由 Pyenv 安装的 Python 版本，请运行以下命令之一：
        pyenv shell %version% -- 仅对当前 shell 会话选择
        pyenv local <version> -- 在当前目录（及其子目录）中自动选择
        pyenv global <version> -- 为您的用户账户选择全局版本
        查看版本 
        pyenv global 3.13
        pyenv versions 
        python --version
        现在每当调用 `python`、`pip` 等命令时，将会运行 Pyenv 提供的版本的可执行文件，而不是系统中的 Python。
        pyenv which <command> 显示当你通过 shim 调用 <command> 时，将会运行哪个实际可执行文件
      3. 卸载 Python 版本
        要删除旧的 Python 版本，请使用 pyenv uninstall <versions>。
    """
    pass

  def steps2_other(self):
    """
      其他操作
        运行 `pyenv commands` 可以查看所有可用子命令。使用 `pyenv subcommand --help` 可以获取子命令的帮助信息，或者参见 命令参考 。
    """
    pass

  def notes(self):
    """
      pyenv: 推荐用法：用 pyenv 安装你需要的 Python 版本（如 3.10.14），然后用该版本创建虚拟环境（如用 venv、poetry）。
      uv: 推荐用法：你用 pyenv 安装好某个 Python 版本后，在项目中用 uv 管理环境和依赖（可取代 pip+venv 或 poetry）。
      conda: 推荐用法：需要 C/C++/Fortran 环境或非 Python 科学计算库时优先使用；否则日常开发可以选择更轻量的 uv

      总结：什么时候用哪个？
        目标	推荐工具	说明
        安装多个 Python 版本	pyenv	轻松管理多个版本，适配 uv/venv/poetry 等
        快速安装依赖，做纯 Python 项目	uv	现代、高效、适合 Python-only 项目
        搞科研/深度学习/系统级软件依赖	conda	对底层库友好，不用自己编译
    """
    pass
