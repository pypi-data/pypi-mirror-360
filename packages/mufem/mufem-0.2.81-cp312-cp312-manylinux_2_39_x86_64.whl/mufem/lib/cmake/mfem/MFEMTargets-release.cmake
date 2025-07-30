#----------------------------------------------------------------
# Generated CMake target import file for configuration "RELEASE".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "mfem" for configuration "RELEASE"
set_property(TARGET mfem APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mfem PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libmfem.so.4.8.1"
  IMPORTED_SONAME_RELEASE "libmfem.so.4.8.1"
  )

list(APPEND _cmake_import_check_targets mfem )
list(APPEND _cmake_import_check_files_for_mfem "${_IMPORT_PREFIX}/lib/libmfem.so.4.8.1" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
