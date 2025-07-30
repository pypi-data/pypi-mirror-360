#----------------------------------------------------------------
# Generated CMake target import file for configuration "RELEASE".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "HYPRE::HYPRE" for configuration "RELEASE"
set_property(TARGET HYPRE::HYPRE APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(HYPRE::HYPRE PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libHYPRE.so.2.33.0"
  IMPORTED_SONAME_RELEASE "libHYPRE.so.233"
  )

list(APPEND _cmake_import_check_targets HYPRE::HYPRE )
list(APPEND _cmake_import_check_files_for_HYPRE::HYPRE "${_IMPORT_PREFIX}/lib/libHYPRE.so.2.33.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
