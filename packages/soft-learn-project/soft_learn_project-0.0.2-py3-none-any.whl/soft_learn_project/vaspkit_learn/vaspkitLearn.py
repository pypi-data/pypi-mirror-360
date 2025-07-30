
class VaspkitLearn():
  def __init__(self) -> None:
    pass

  def install(self):
    s = """(1) cd vaspkit/
    (2) bash setup.sh
    (3) modify ~/.vaspkit file based on your machine environment 
    (4) source ~/.bashrc"""
    print(s)
    pass

  def get_gibbs_H2O(self):
    """G(H20)是液态水分子的能量，等于饱和蒸气压不的水蒸氵量(常温下 ~0.035 bar)。

    Returns:
        _type_: _description_
    """
    print('注意vaspkit 目前只支持x86 而不支持mac m1 芯片故不能使用: vaspkit-502-298.15-0.035-1')
    return None
