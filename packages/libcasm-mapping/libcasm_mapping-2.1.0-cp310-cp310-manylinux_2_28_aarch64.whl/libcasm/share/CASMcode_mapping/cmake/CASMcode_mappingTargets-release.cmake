#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "CASM::casm_mapping" for configuration "Release"
set_property(TARGET CASM::casm_mapping APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(CASM::casm_mapping PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcasm_mapping.so"
  IMPORTED_SONAME_RELEASE "libcasm_mapping.so"
  )

list(APPEND _cmake_import_check_targets CASM::casm_mapping )
list(APPEND _cmake_import_check_files_for_CASM::casm_mapping "${_IMPORT_PREFIX}/lib/libcasm_mapping.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
