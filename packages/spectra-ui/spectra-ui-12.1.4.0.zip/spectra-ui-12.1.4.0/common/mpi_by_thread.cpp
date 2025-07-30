#include <iostream>
#include <algorithm>
#include <stdexcept>
#include <stdio.h>
#include <stdlib.h>
#include "mpi_by_thread.h"

MPIbyThread::MPIbyThread(int nthreads)
{
	m_nthreads = nthreads;
	m_gets[0] = m_gets[1] = 0;
	m_ready[0] = m_ready[1] = false;
	m_nreset[0] = m_nreset[1] = 0;
}

void MPIbyThread::Wait(int iab)
{
	unique_lock<mutex> lock(m_mtx);
	m_gets[iab]++;
	if(m_gets[iab] < m_nthreads){
		m_ready[iab] = false;
		while(!m_ready[iab]){
			m_cv.wait(lock);
		}
	}
	else{
		m_nreset[iab]++;
		m_gets[iab] = 0;
		m_ready[iab] = true;
		m_cv.notify_all();
	}
}

void MPIbyThread::Bcast(
	void *buf, int count, MPI_Datatype datatype, int root, int thid)
{
	if(thid == root){
		ArrangeWS(count, datatype);
		Set(buf, count, datatype);
	}
	Wait(0);
	if(thid != root){
		Get(buf, count, datatype);
	}
	Wait(1);
}

void MPIbyThread::SendRecv(
	void *buf, int count, MPI_Datatype datatype, int source, int dest, int thid)
{
	/*
	if(thid == source){
		ArrangeWS(count, datatype);
		Set(buf, count, datatype);
	}
	Wait(0);
	if(thid == dest){
		Get(buf, count, datatype);
	}
	Wait(1);
	*/
	SendRecv(buf, buf, count, datatype, source, dest, thid);
}

void MPIbyThread::SendRecv(void *sendbuf, void *recvdbuf, 
	int count, MPI_Datatype datatype, int source, int dest, int thid)
{
	if(thid == source){
		ArrangeWS(count, datatype);
		Set(sendbuf, count, datatype);
	}
	Wait(0);
	if(thid == dest){
		Get(recvdbuf, count, datatype);
	}
	Wait(1);
}

void MPIbyThread::Allreduce(
	void *sendbuf, void *recvbuf, int count, MPI_Datatype datatype, MPI_Op op, int thid)
{
	for(int th = 0; th < m_nthreads; th++){
		Wait(0);
		if(th == thid){
			if(th == 0){
				ArrangeWS(count, datatype);
				Set(sendbuf, count, datatype);
			}
			else{
				Reduce(sendbuf, count, datatype, op);
			}
		}
		Wait(1);
	}
	Wait(0);
	Get(recvbuf, count, datatype);
	Wait(1);
}

void MPIbyThread::Gather(void *sendbuf, int sendcount, MPI_Datatype sendtype,
	void *recvbuf, int recvcount, MPI_Datatype recvtype, int root, int thid)
{
	if(thid == root){
		ArrangeWS(recvcount*m_nthreads, recvtype);
	}
	for(int n = 0; n < m_nthreads; n++){
		Wait(0);
		if(thid == n){
			Set(sendbuf, sendcount, sendtype, sendcount*n);
		}
		Wait(1);
	}
	Wait(0);
	if(thid == root){
		Get(recvbuf, recvcount*m_nthreads, recvtype);
	}
	Wait(1);
}

void MPIbyThread::Allgather(void *sendbuf, int sendcount, MPI_Datatype sendtype, void *recvbuf, int recvcount, MPI_Datatype recvtype, int thid)
{
	if(thid == 0){
		ArrangeWS(recvcount*m_nthreads, recvtype);
	}
	for(int n = 0; n < m_nthreads; n++){
		Wait(0);
		if(thid == n){
			Set(sendbuf, sendcount, sendtype, sendcount*n);
		}
		Wait(1);
	}
	for(int n = 0; n < m_nthreads; n++){
		Wait(0);
		if(thid == n){
			Get(recvbuf, recvcount*m_nthreads, recvtype);
		}
		Wait(1);
	}
}

void MPIbyThread::Scatter(void *sendbuf, int sendcount, MPI_Datatype sendtype,
	void *recvbuf, int recvcount, MPI_Datatype recvtype, int root, int thid)
{
	if(thid == root){
		ArrangeWS(sendcount*m_nthreads, sendtype);
		Set(sendbuf, sendcount*m_nthreads, sendtype);
	}
	for(int n = 0; n < m_nthreads; n++){
		Wait(0);
		if(thid == n){
			Get(recvbuf, recvcount, recvtype, recvcount*n);
		}
		Wait(1);
	}
}

void MPIbyThread::ArrangeWS(int count, MPI_Datatype datatype)
{
	int extra_size = 100;

	if(datatype == MPI_DOUBLE){
		if(count > m_wsd.size()){
			m_wsd.resize(count+extra_size);
		}
	}
	else if(datatype == MPI_INT){
		if(count > m_wsi.size()){
			m_wsi.resize(count+extra_size);
		}
	}
	else if(datatype == MPI_FLOAT){
		if(count > m_wsf.size()){
			m_wsf.resize(count+extra_size);
		}
	}
	else{
		throw runtime_error("Invalid MPI data type");
	}
}

void MPIbyThread::Set(void *buf, int count, MPI_Datatype datatype, int offset)
{
	if(datatype == MPI_DOUBLE){
		for(int n = 0; n < count; n++){
			m_wsd[n+offset] = ((double *)buf)[n];
		}
	}
	else if(datatype == MPI_INT){
		for(int n = 0; n < count; n++){
			m_wsi[n+offset] = ((int *)buf)[n];
		}
	}
	else if(datatype == MPI_FLOAT){
		for(int n = 0; n < count; n++){
			m_wsf[n+offset] = ((float *)buf)[n];
		}
	}
	else{
		throw runtime_error("Invalid MPI data type");
	}
}

void MPIbyThread::Get(void *buf, int count, MPI_Datatype datatype, int offset)
{
	if(datatype == MPI_DOUBLE){
		for(int n = 0; n < count; n++){
			((double *)buf)[n] = m_wsd[n+offset];
		}
	}
	else if(datatype == MPI_INT){
		for(int n = 0; n < count; n++){
			((int *)buf)[n] = m_wsi[n+offset];
		}
	}
	else if(datatype == MPI_FLOAT){
		for(int n = 0; n < count; n++){
			((float *)buf)[n] = m_wsf[n+offset];
		}
	}
	else{
		throw runtime_error("Invalid MPI data type");
	}
}

void MPIbyThread::Reduce(void *buf, int count, MPI_Datatype datatype, MPI_Op op)
{
	if(datatype == MPI_DOUBLE){
		for(int n = 0; n < count; n++){
			if(op == MPI_SUM){
				m_wsd[n] += ((double *)buf)[n];
			}
			else if(op == MPI_MAX){
				m_wsd[n] = max(m_wsd[n],  ((double *)buf)[n]);
			}
		}
	}
	else if(datatype == MPI_INT){
		for(int n = 0; n < count; n++){
			if(op == MPI_SUM){
				m_wsi[n] += ((int *)buf)[n];
			}
			else if(op == MPI_MAX){
				m_wsi[n] = max(m_wsi[n], ((int *)buf)[n]);
			}
		}
	}
	else if(datatype == MPI_FLOAT){
		for(int n = 0; n < count; n++){
			if(op == MPI_SUM){
				m_wsf[n] += ((float *)buf)[n];
			}
			else if(op == MPI_MAX){
				m_wsf[n] = max(m_wsf[n], ((float *)buf)[n]);
			}
		}
	}
	else{
		throw runtime_error("Invalid MPI data type");
	}
}
