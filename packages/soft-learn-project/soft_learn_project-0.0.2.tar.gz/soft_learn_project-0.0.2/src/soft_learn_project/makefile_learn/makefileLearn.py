class MakefileLearn():
  def __init__(self) -> None:
    pass

  def e1(self):
    """
    好的，让我们创建一个非常简单的 Python 项目，该项目将包含一个简单的 Python 脚本和一个 Makefile，Makefile 将用于运行该脚本。

    首先，我们创建一个名为 hello.py 的 Python 脚本，用于打印 "Hello, world!"：

    # hello.py

    def main():
        print("Hello, world!")


    if __name__ == "__main__":
        main()
    接下来，我们创建一个名为 Makefile 的 Makefile，用于定义运行该脚本的任务：

    makefile
    # Makefile for simple Python project

    # 默认目标
    .DEFAULT_GOAL := run

    # 运行目标
    run:
        python3 hello.py

    现在我们有了 hello.py 脚本和 Makefile 文件。现在我们可以使用 make 命令来运行脚本：

    bash
    make
    这将会执行 Makefile 中定义的默认目标，也就是 run 目标，它会运行 hello.py 脚本，然后在终端中打印 "Hello, world!"。

    这就是整个流程：通过 make 命令执行 Makefile 中定义的任务，这个任务会运行我们的 Python 脚本。

    Makefile:8: *** missing separator.  Stop.
    这个错误通常是由于 Makefile 中缩进不正确引起的。在 Makefile 中，命令行规则必须以 Tab 键开始，而不是空格。如果使用空格缩进，会导致 Makefile 解析错误。 请确保在 Makefile 中使用 Tab 键进行缩进，而不是空格。
    """
    pass
