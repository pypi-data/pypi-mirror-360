
class OpenmmLearn():
  def __init__(self):
    """https://openmm.org/documentation
    github: https://github.com/openmm/openmm/tree/master
    * OpenMM是一个用于分子模拟的工具包。它既可以用作运行模拟的独立应用程序，也可以用作从自己的代码调用的库。它提供了极高的灵活性（通过自定义力和集成商），开放性和高性能（特别是在最近的gpu上）的组合，使其在仿真代码中真正独特。
    """
    pass

  def install(self):
    string = """conda install openmm
    conda install openff-toolkit
    conda install mdareporter 
    # 测试安装
    python -m openmm.testInstallation
    """
    print(string)
    return None

  def x(self):
    return None
