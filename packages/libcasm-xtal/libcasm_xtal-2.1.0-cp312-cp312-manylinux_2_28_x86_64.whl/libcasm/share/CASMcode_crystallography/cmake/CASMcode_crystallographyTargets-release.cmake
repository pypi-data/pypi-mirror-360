#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "CASM::casm_crystallography" for configuration "Release"
set_property(TARGET CASM::casm_crystallography APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(CASM::casm_crystallography PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcasm_crystallography.so"
  IMPORTED_SONAME_RELEASE "libcasm_crystallography.so"
  )

list(APPEND _cmake_import_check_targets CASM::casm_crystallography )
list(APPEND _cmake_import_check_files_for_CASM::casm_crystallography "${_IMPORT_PREFIX}/lib/libcasm_crystallography.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
