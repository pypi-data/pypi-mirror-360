from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()   
 
numDataPerRank = 10  
sendbuf = np.linspace(rank*numDataPerRank+1,(rank+1)*numDataPerRank,numDataPerRank) # np.linspace(1, 10, 10) ,np.linspace(11, 20, 10) ...
print('Rank: ',rank, ', sendbuf: ',sendbuf)

if rank == 0:
    recvbuf = np.empty(numDataPerRank*size, dtype='d')   # 产生随机的，未初始化的数组
else:
    recvbuf = None

comm.Gather(sendbuf, recvbuf, root=0)

if rank == 0:
    print('Rank: ',rank, ', recvbuf received: ',recvbuf)
