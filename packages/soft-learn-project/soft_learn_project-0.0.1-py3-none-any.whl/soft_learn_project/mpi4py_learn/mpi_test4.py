from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    # data = {'key1' : [1,2, 3],
    #         'key2' : ( 'abc', 'xyz')}
    # data = np.linspace(1,10,10)
    data = [1,2,3,4,5.0]
    data  = np.array(data)
else:
    data =  None # {} 也可以
    pass 
 
data = comm.bcast(data, root=0)
print('Rank: ',rank, 'data: ' ,data)
