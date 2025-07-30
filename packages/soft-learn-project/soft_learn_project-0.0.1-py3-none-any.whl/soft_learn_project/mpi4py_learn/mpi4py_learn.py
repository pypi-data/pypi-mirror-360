from mpi4py import MPI
import mpi4py


class Mpi4pyLearn():
  def __init__(self) -> None:
    pass

  def install(self):
    # `conda install mpi4py`
    pass

  def myfunc(self, a=3):
    print(f'{a} is OK')

  def rank_0(self, func, func_args_dict):
    comm = mpi4py.MPI.COMM_WORLD
    rank = comm.Get_rank()
    if rank == 0:
      func(**func_args_dict)
    return None

  def e1(self):
    # % % writefile mpi_test1.py
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    print('My rank is ', rank)

    # 执行效果如下：
    # !mpirun - n 4 python3 mpi_test1.py
    pass

  def e2(self):
    import numpy as np
    pass
