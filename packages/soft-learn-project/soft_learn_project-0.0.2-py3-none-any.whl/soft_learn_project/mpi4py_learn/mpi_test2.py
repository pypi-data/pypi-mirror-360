# 在这个案例中，我们从rank id为0的进程向rank id为1的进程发送了一个整数变量的数据。因为我们并不知道这个脚本什么时候会被分配到rank 0什么时候会被分配到rank 1，因此在同一个脚本内我们就需要分别对这两种可能发生的情况进行针对性的处理。
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    idata = 1
    comm.send(idata, dest=1)
    print('This is process {}'.format(rank),
          '\nData send to process 1 successfully!')
elif rank == 1:
    idata = comm.recv(source=0)
    print('This is process {}, data is '.format(rank), idata)
