"""Helper functions for wasserstein distance."""

cimport cython
cimport numpy as cnp
from libc.stdlib cimport free, malloc

import numpy as np

cnp.import_array()

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef cnp.ndarray[cnp.float64_t, ndim=1] optimize_q(double[:] g):
    # M = number of probability-space grid, N = number of distance-space grid
    cdef Py_ssize_t i, j, idx
    cdef double[:] y_vals = np.unique(g)
    cdef Py_ssize_t M = g.shape[0], N = y_vals.shape[0]
    # Should memory error occurs, may need to make ca 1d and overwrite during loop.
    cdef double *ca = <double *> malloc(M * N * sizeof(double))
    if not ca:
        raise MemoryError()
    cdef int *predecessor = <int *> malloc((M - 1) * N * sizeof(int))
    if not predecessor:
        raise MemoryError()

    # Compute costs
    for i in range(M):  # TODO: parallize this i-loop
        for j in range(N):
            ca[i * N + j] = (g[i] - y_vals[j]) ** 2

    # Accumulate costs
    cdef Py_ssize_t prev_min_j
    cdef double prev_min
    for i in range(1, M):
        prev_min_j = 0
        prev_min = ca[(i - 1) * N + prev_min_j]
        for j in range(N):
            if ca[(i - 1) * N + j] < prev_min:
                prev_min_j = j
                prev_min = ca[(i - 1) * N + j]
            ca[i * N + j] += prev_min
            predecessor[(i - 1) * N + j] = prev_min_j

    # Backtrack
    cdef cnp.ndarray[cnp.float64_t, ndim=1] q = np.empty(M, dtype=np.float64)
    idx = 0
    # Last column
    for j in range(1, N):
        if ca[(M - 1) * N + j] < ca[(M - 1) * N + idx]:
            idx = j
    q[M - 1] = y_vals[idx]
    free(ca)
    # Other columns
    for i in range(1, M):
        idx = predecessor[(M - 1 - i) * N + idx]
        q[M - 1 - i] = y_vals[idx]

    free(predecessor)
    return q
