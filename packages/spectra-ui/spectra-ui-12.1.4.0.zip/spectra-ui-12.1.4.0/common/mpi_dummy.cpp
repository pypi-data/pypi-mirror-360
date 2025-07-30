#ifdef __NOMPI__

#include <algorithm>
#include "mpi_dummy.h"
#include <stdio.h>
#include <stdlib.h>

using namespace std;

int MPI_Init(int *argc, char ***argv)
{
	return 0;
}

int MPI_Abort(MPI_Comm comm, int errorcode)
{
	return 0;
}

int MPI_Finalize(void)
{
	return 0;
}

int MPI_Comm_size(MPI_Comm comm, int *size)
{
	*size = 1;
	return 0;
}

int MPI_Comm_rank(MPI_Comm comm, int *rank)
{
	*rank = 0;
	return 0;
}

int MPI_Barrier(MPI_Comm comm)
{
	return 0;
}

int MPI_Send(void *buf, int count, MPI_Datatype datatype,
             int  dest, int   tag, MPI_Comm         comm)
{
	return 0;
}

int MPI_Recv(void *buf, int count, MPI_Datatype datatype, int source, int tag,
             MPI_Comm comm, MPI_Status *status)
{
	return 0;
}

int MPI_Bcast(void *buf, int count, MPI_Datatype datatype, 
              int  root, MPI_Comm comm)
{
	return 0;
}

void MPI_Dummy_Send_Recv(const void *sendbuf, int sendcount, MPI_Datatype sendtype, void *recvbuf, int recvcount)
{
	for(int n = 0; n < min(sendcount, recvcount); n++){
		if(sendtype == MPI_CHAR){
			((char *)recvbuf)[n] = ((char *)sendbuf)[n];
		}
		else if(sendtype == MPI_INT){
			((int *)recvbuf)[n] = ((int *)sendbuf)[n];
		}
		else if(sendtype == MPI_FLOAT){
			((float *)recvbuf)[n] = ((float *)sendbuf)[n];
		}
		else if(sendtype == MPI_DOUBLE){
			((double *)recvbuf)[n] = ((double *)sendbuf)[n];
		}
		else if(sendtype == MPI_LONG){
			((long *)recvbuf)[n] = ((long *)sendbuf)[n];
		}
	}
}

int MPI_Gather(const void *sendbuf, int sendcount, MPI_Datatype sendtype,
               void *recvbuf, int recvcount, MPI_Datatype recvtype,
               int root, MPI_Comm comm)
{
	MPI_Dummy_Send_Recv(sendbuf, sendcount, sendtype, recvbuf, recvcount);
	return 0;
}

int MPI_Scatter(const void *sendbuf, int sendcount, MPI_Datatype sendtype,
               void *recvbuf, int recvcount, MPI_Datatype recvtype, int root,
               MPI_Comm comm)
{
	MPI_Dummy_Send_Recv(sendbuf, sendcount, sendtype, recvbuf, recvcount);
	return 0;
}

int MPI_Reduce(const void *sendbuf, void *recvbuf, int count, MPI_Datatype datatype,
               MPI_Op op, int root, MPI_Comm comm)
{
	MPI_Dummy_Send_Recv(sendbuf, count, datatype, recvbuf, count);
	return 0;
}

int MPI_Allreduce(const void *sendbuf, void *recvbuf, int count, MPI_Datatype datatype,
	MPI_Op op, MPI_Comm comm)
{
	MPI_Dummy_Send_Recv(sendbuf, count, datatype, recvbuf, count);
	return 0;
}

int MPI_Get_processor_name(char *name, int *resultlen)
{
#ifdef WIN32
	sprintf_s(name, sizeof(name), "No MPI Process Available");
#else
	sprintf(name, "No MPI Process Available");
#endif
	return 0;
}

#endif