# Copyright (c) 2010-2025, Lawrence Livermore National Security, LLC. Produced
# at the Lawrence Livermore National Laboratory. All Rights reserved. See files
# LICENSE and NOTICE for details. LLNL-CODE-806117.
#
# This file is part of the MFEM library. For more information and source code
# availability visit https://mfem.org.
#
# MFEM is free software; you can redistribute it and/or modify it under the
# terms of the BSD-3 license. We welcome feedback and contributions, see file
# CONTRIBUTING.md for details.

# Variables corresponding to defines in config.hpp (YES, NO, or value)
MFEM_VERSION           = 40801
MFEM_VERSION_STRING    = 4.8.1
MFEM_SOURCE_DIR        = /__w/mufem-mirror/mufem-mirror/build/mfem
MFEM_INSTALL_DIR       = /__w/mufem-mirror/mufem-mirror/scripts/../mirror
MFEM_GIT_STRING        = tags/v4.8-53-g90a68678f4dd6b39e214f66836f05bb7a3aa124a-dirty
MFEM_USE_MPI           = YES
MFEM_USE_METIS         = YES
MFEM_USE_METIS_5       = YES
MFEM_USE_DOUBLE        = YES
MFEM_USE_SINGLE        = NO
MFEM_DEBUG             = NO
MFEM_USE_EXCEPTIONS    = YES
MFEM_USE_ZLIB          = YES
MFEM_USE_LIBUNWIND     = NO
MFEM_USE_LAPACK        = NO
MFEM_THREAD_SAFE       = NO
MFEM_USE_LEGACY_OPENMP = NO
MFEM_USE_OPENMP        = NO
MFEM_USE_MEMALLOC      = YES
MFEM_TIMER_TYPE        = 2
MFEM_USE_SUNDIALS      = NO
MFEM_USE_SUITESPARSE   = NO
MFEM_USE_SUPERLU       = NO
MFEM_USE_SUPERLU5      = NO
MFEM_USE_MUMPS         = YES
MFEM_USE_STRUMPACK     = NO
MFEM_USE_GINKGO        = NO
MFEM_USE_AMGX          = NO
MFEM_USE_MAGMA         = NO
MFEM_USE_GNUTLS        = NO
MFEM_USE_HDF5          = NO
MFEM_USE_NETCDF        = NO
MFEM_USE_PETSC         = NO
MFEM_USE_SLEPC         = NO
MFEM_USE_MPFR          = NO
MFEM_USE_SIDRE         = NO
MFEM_USE_FMS           = NO
MFEM_USE_CONDUIT       = NO
MFEM_USE_PUMI          = NO
MFEM_USE_HIOP          = NO
MFEM_USE_GSLIB         = YES
MFEM_USE_CUDA          = NO
MFEM_USE_HIP           = NO
MFEM_USE_RAJA          = NO
MFEM_USE_OCCA          = NO
MFEM_USE_CEED          = NO
MFEM_USE_CALIPER       = NO
MFEM_USE_UMPIRE        = NO
MFEM_USE_SIMD          = NO
MFEM_USE_ADIOS2        = NO
MFEM_USE_MKL_CPARDISO  = NO
MFEM_USE_MKL_PARDISO   = NO
MFEM_USE_MOONOLITH     = NO
MFEM_USE_ADFORWARD     = NO
MFEM_USE_CODIPACK      = NO
MFEM_USE_BENCHMARK     = NO
MFEM_USE_PARELAG       = NO
MFEM_USE_TRIBOL        = NO
MFEM_USE_ENZYME        = NO

# Compiler, compile options, and link options
MFEM_CXX       = /usr/bin/clang++
MFEM_HOST_CXX  = /usr/bin/clang++
MFEM_CPPFLAGS  = 
MFEM_CXXFLAGS  = -std=c++11 -O3 -DNDEBUG -march=x86-64-v3 -mtune=generic -O3 -fomit-frame-pointer -pipe -fno-math-errno
MFEM_TPLFLAGS  =  -I/__w/mufem-mirror/mufem-mirror/mirror/include -I/__w/mufem-mirror/mufem-mirror/mirror/lib
MFEM_INCFLAGS  = -I$(MFEM_INC_DIR) $(MFEM_TPLFLAGS)
MFEM_PICFLAG   = -fPIC
MFEM_FLAGS     = $(MFEM_CPPFLAGS) $(MFEM_CXXFLAGS) $(MFEM_INCFLAGS)
MFEM_EXT_LIBS  =  -Wl,-rpath,/__w/mufem-mirror/mufem-mirror/mirror/lib -L/__w/mufem-mirror/mufem-mirror/mirror/lib -lHYPRE -Wl,-rpath,/__w/mufem-mirror/mufem-mirror/mirror/lib -L/__w/mufem-mirror/mufem-mirror/mirror/lib -ldmumps -Wl,-rpath,/__w/mufem-mirror/mufem-mirror/mirror/lib -L/__w/mufem-mirror/mufem-mirror/mirror/lib -lmumps_common -Wl,-rpath,/__w/mufem-mirror/mufem-mirror/mirror/lib -L/__w/mufem-mirror/mufem-mirror/mirror/lib -lpord -Wl,-rpath,/__w/mufem-mirror/mufem-mirror/mirror/lib -L/__w/mufem-mirror/mufem-mirror/mirror/lib -lmpi_usempi -Wl,-rpath,/__w/mufem-mirror/mufem-mirror/mirror/lib -L/__w/mufem-mirror/mufem-mirror/mirror/lib -lmpi_mpifh -Wl,-rpath,/__w/mufem-mirror/mufem-mirror/mirror/lib -L/__w/mufem-mirror/mufem-mirror/mirror/lib -lparmetis -Wl,-rpath,/__w/mufem-mirror/mufem-mirror/mirror/lib -L/__w/mufem-mirror/mufem-mirror/mirror/lib -lmetis -Wl,-rpath,/__w/mufem-mirror/mufem-mirror/mirror/lib -L/__w/mufem-mirror/mufem-mirror/mirror/lib -lscalapack -Wl,-rpath,/__w/mufem-mirror/mufem-mirror/scripts/../mirror/lib -L/__w/mufem-mirror/mufem-mirror/scripts/../mirror/lib -lopenblas -Wl,-rpath,/__w/mufem-mirror/mufem-mirror/mirror/lib -L/__w/mufem-mirror/mufem-mirror/mirror/lib -lopenblas -lm -ldl -Wl,-rpath,/__w/mufem-mirror/mufem-mirror/mirror/lib -L/__w/mufem-mirror/mufem-mirror/mirror/lib -lgs -Wl,-rpath,/__w/mufem-mirror/mufem-mirror/mirror/lib -L/__w/mufem-mirror/mufem-mirror/mirror/lib -lz -Wl,-rpath,/__w/mufem-mirror/mufem-mirror/mirror/lib -L/__w/mufem-mirror/mufem-mirror/mirror/lib -lmpi
MFEM_LIBS      = -Wl,-rpath,$(MFEM_LIB_DIR) -L$(MFEM_LIB_DIR) -lmfem $(MFEM_EXT_LIBS)
MFEM_LIB_FILE  = $(MFEM_LIB_DIR)/libmfem.so.4.8.1
MFEM_STATIC    = NO
MFEM_SHARED    = YES
MFEM_BUILD_TAG = Linux-6.11.0-28-generic
MFEM_PREFIX    = /__w/mufem-mirror/mufem-mirror/scripts/../mirror
MFEM_INC_DIR   = /__w/mufem-mirror/mufem-mirror/scripts/../mirror/include
MFEM_LIB_DIR   = /__w/mufem-mirror/mufem-mirror/scripts/../mirror/lib

# Location of test.mk
MFEM_TEST_MK = /__w/mufem-mirror/mufem-mirror/scripts/../mirror/share/mfem/test.mk

# Command used to launch MPI jobs
MFEM_MPIEXEC    = /__w/mufem-mirror/mufem-mirror/mirror/bin/mpiexec
MFEM_MPIEXEC_NP = -n
MFEM_MPI_NP     = 4

# The NVCC compiler cannot link with -x=cu
MFEM_LINK_FLAGS := $(filter-out -x=cu -xhip, $(MFEM_FLAGS))

# Optional extra configuration

