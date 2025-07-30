#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "legate::legate" for configuration "Release"
set_property(TARGET legate::legate APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(legate::legate PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "hdf5_vfd_gds;cpptrace::cpptrace"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/liblegate.so.25.07.00"
  IMPORTED_SONAME_RELEASE "liblegate.so.25.07.00"
  )

list(APPEND _cmake_import_check_targets legate::legate )
list(APPEND _cmake_import_check_files_for_legate::legate "${_IMPORT_PREFIX}/lib64/liblegate.so.25.07.00" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
