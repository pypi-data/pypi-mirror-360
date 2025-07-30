import copy
import os
import numpy as np
import ase
import ase.build
import ase.lattice
import ase.io
from py_package_learn.ase_learn import aseLearn
from vasp_learn import dataBase, base


class GetModel(aseLearn.Model):
  def __init__(self) -> None:
    # 构建模型
    self.DataBase = dataBase.DataBase()
    self.Base = base.Base()
    pass
