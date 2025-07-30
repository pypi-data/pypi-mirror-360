#ifndef mpi_dummy_h
#define mpi_dummy_h

#define MPI_MAX_PROCESSOR_NAME 128
#define MPI_COMM_WORLD 0

typedef int MPI_Comm;
typedef int MPI_Datatype;
typedef int MPI_Comm;
typedef int MPI_Status;
typedef int MPI_Datatype;
typedef int MPI_Op;

#define MPI_CHAR ((MPI_Datatype)0)
#define MPI_INT ((MPI_Datatype)1)
#define MPI_FLOAT ((MPI_Datatype)2)
#define MPI_DOUBLE ((MPI_Datatype)4)
#define MPI_LONG ((MPI_Datatype)8)
#define MPI_SUM ((MPI_Op)16)
#define MPI_MAX ((MPI_Op)32)

int MPI_Allreduce(const void *sendbuf, void *recvbuf, int count, 
	MPI_Datatype datatype,	MPI_Op op, MPI_Comm comm);
int MPI_Init(int *argc, char ***argv);
int MPI_Abort(MPI_Comm comm, int errorcode);
int MPI_Finalize(void);
int MPI_Comm_size(MPI_Comm comm, int *size);
int MPI_Comm_rank(MPI_Comm comm, int *rank);
int MPI_Barrier(MPI_Comm comm);
int MPI_Send(void *buf, int count, MPI_Datatype datatype,
             int  dest, int   tag, MPI_Comm         comm);
int MPI_Recv(void *buf, int count, MPI_Datatype datatype, int source, int tag,
             MPI_Comm comm, MPI_Status *status);
int MPI_Bcast(void *buf, int count, MPI_Datatype datatype, 
              int  root, MPI_Comm comm);
int MPI_Gather(const void *sendbuf, int sendcount, MPI_Datatype sendtype,
               void *recvbuf, int recvcount, MPI_Datatype recvtype,
               int root, MPI_Comm comm);
int MPI_Scatter(const void *sendbuf, int sendcount, MPI_Datatype sendtype,
               void *recvbuf, int recvcount, MPI_Datatype recvtype, int root,
               MPI_Comm comm);
int MPI_Reduce(const void *sendbuf, void *recvbuf, int count, MPI_Datatype datatype,
               MPI_Op op, int root, MPI_Comm comm);
int MPI_Get_processor_name(char *name, int *resultlen);


#endif
