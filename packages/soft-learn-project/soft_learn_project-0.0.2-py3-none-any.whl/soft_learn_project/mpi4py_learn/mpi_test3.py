from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()


if rank == 0:
    numData = 10
    comm.send(numData, dest=1)  # python 内部数据类型用小写
    data = np.linspace(0.0, 3.14, numData)
    comm.Send(data, dest=1)  # numpy 数组发送用大写Send
    print('This is process {}'.format(rank),
          '\nData send to process 1 successfully!')

elif rank == 1:
    numData = comm.recv(source=0)
    print('Number of data to receive: ', numData)
 
    data = np.empty(numData, ) # 接收前定义个空数组，大小要一致
    comm.Recv(data, source=0)  # 请注意用于发送和接收 numpy 数组的comm.Send和如何comm.Recv使用大写S和R.
    print('This is process {}, data is '.format(rank), data)
