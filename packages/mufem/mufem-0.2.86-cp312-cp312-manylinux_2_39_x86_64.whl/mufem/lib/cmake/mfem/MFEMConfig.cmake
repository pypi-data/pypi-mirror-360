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

include(${CMAKE_CURRENT_LIST_DIR}/MFEMConfigVersion.cmake)

set(MFEM_VERSION ${PACKAGE_VERSION})
set(MFEM_VERSION_INT 40801)
set(MFEM_GIT_STRING "tags/v4.8-53-g90a68678f4dd6b39e214f66836f05bb7a3aa124a-dirty")

set(MFEM_USE_MPI YES)
set(MFEM_USE_METIS ON)
set(MFEM_USE_METIS_5 1)
set(MFEM_USE_DOUBLE ON)
set(MFEM_USE_SINGLE OFF)
set(MFEM_DEBUG OFF)
set(MFEM_USE_EXCEPTIONS YES)
set(MFEM_USE_ZLIB YES)
set(MFEM_USE_LIBUNWIND OFF)
set(MFEM_USE_LAPACK OFF)
set(MFEM_THREAD_SAFE OFF)
set(MFEM_USE_OPENMP OFF)
set(MFEM_USE_LEGACY_OPENMP OFF)
set(MFEM_USE_MEMALLOC ON)
set(MFEM_TIMER_TYPE 2)
set(MFEM_USE_SUNDIALS OFF)
set(MFEM_USE_SUITESPARSE OFF)
set(MFEM_USE_SUPERLU OFF)
set(MFEM_USE_MUMPS YES)
set(MFEM_USE_STRUMPACK OFF)
set(MFEM_USE_GINKGO OFF)
set(MFEM_USE_AMGX OFF)
set(MFEM_USE_MAGMA OFF)
set(MFEM_USE_HIOP OFF)
set(MFEM_USE_GNUTLS OFF)
set(MFEM_USE_GSLIB YES)
set(MFEM_USE_HDF5 OFF)
set(MFEM_USE_NETCDF OFF)
set(MFEM_USE_PETSC OFF)
set(MFEM_USE_SLEPC OFF)
set(MFEM_USE_MPFR OFF)
set(MFEM_USE_SIDRE OFF)
set(MFEM_USE_FMS OFF)
set(MFEM_USE_CONDUIT OFF)
set(MFEM_USE_PUMI OFF)
set(MFEM_USE_CUDA OFF)
set(MFEM_USE_HIP OFF)
set(MFEM_USE_OCCA OFF)
set(MFEM_USE_RAJA OFF)
set(MFEM_USE_CEED OFF)
set(MFEM_USE_UMPIRE OFF)
set(MFEM_USE_SIMD OFF)
set(MFEM_USE_ADIOS2 OFF)
set(MFEM_USE_MOONOLITH )
set(MFEM_USE_CODIPACK OFF)
set(MFEM_USE_MKL_CPARDISO OFF)
set(MFEM_USE_MKL_PARDISO OFF)
set(MFEM_USE_ADFORWARD OFF)
set(MFEM_USE_CALIPER OFF)
set(MFEM_USE_ALGOIM OFF)
set(MFEM_USE_BENCHMARK OFF)
set(MFEM_USE_PARELAG OFF)
set(MFEM_USE_TRIBOL OFF)
set(MFEM_USE_ENZYME OFF)

set(MFEM_CXX_COMPILER "/usr/bin/clang++")
set(MFEM_CXX_FLAGS "-march=x86-64-v3 -mtune=generic -O3 -fomit-frame-pointer -pipe -fno-math-errno")


####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was MFEMConfig.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

set(MFEM_INCLUDE_DIRS "${PACKAGE_PREFIX_DIR}/include;/__w/mufem-mirror/mufem-mirror/mirror/include;/__w/mufem-mirror/mufem-mirror/mirror/lib")
foreach (dir ${MFEM_INCLUDE_DIRS})
  set_and_check(MFEM_INCLUDE_DIR "${dir}")
endforeach (dir "${MFEM_INCLUDE_DIRS}")

set_and_check(MFEM_LIBRARY_DIR "${PACKAGE_PREFIX_DIR}/lib")

check_required_components(MFEM)

if (NOT TARGET mfem)
  include(${CMAKE_CURRENT_LIST_DIR}/MFEMTargets.cmake)
endif (NOT TARGET mfem)

set(MFEM_LIBRARIES mfem)
