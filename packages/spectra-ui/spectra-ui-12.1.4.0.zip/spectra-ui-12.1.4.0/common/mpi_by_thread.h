#ifndef mpi_by_thread_h
#define mpi_by_thread_h

#include <vector>
#include <mutex>
#include <shared_mutex>
#include <condition_variable>

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

using namespace std;

class MPIbyThread
{
public:
    MPIbyThread(int nthreads);
    void Wait(int iab);
    void Bcast(void *buf,int count, MPI_Datatype datatype,int root, int thid);
    void SendRecv(void *buf,int count, MPI_Datatype datatype, int source, int dest, int thid);
    void SendRecv(void *sendbuf, void *recvdbuf,int count, MPI_Datatype datatype, int source, int dest, int thid);
    void Allreduce(void *sendbuf, void *recvbuf, int count,
        MPI_Datatype datatype, MPI_Op op, int thid);
    void Gather(void *sendbuf, int sendcount, MPI_Datatype sendtype,
        void *recvbuf, int recvcount, MPI_Datatype recvtype, int root, int thid);
    void Allgather(void *sendbuf, int sendcount, MPI_Datatype sendtype,
        void *recvbuf, int recvcount, MPI_Datatype recvtype, int thid);
    void Scatter(void *sendbuf, int sendcount, MPI_Datatype sendtype,
        void *recvbuf, int recvcount, MPI_Datatype recvtype, int root, int thid);
    void ArrangeWS(int count, MPI_Datatype datatype);
    void Set(void *buf, int count, MPI_Datatype datatype, int offset = 0);
    void Get(void *buf, int count, MPI_Datatype datatype, int offset = 0);
    void Reduce(void *buf,int count, MPI_Datatype datatype, MPI_Op op);
    int GetThreads(){ return m_nthreads; }
    int GetNReset(int iab){ return m_nreset[iab]; }

private:
    mutex m_mtx;
    condition_variable m_cv;
    int m_gets[2];
    int m_nreset[2];
    int m_nthreads;
    bool m_ready[2];
    vector<double> m_wsd;
    vector<float> m_wsf;
    vector<int> m_wsi;
};

#endif
