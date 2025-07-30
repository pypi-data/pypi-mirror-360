#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "CASM::casm_clexmonte" for configuration "Release"
set_property(TARGET CASM::casm_clexmonte APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(CASM::casm_clexmonte PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcasm_clexmonte.so"
  IMPORTED_SONAME_RELEASE "libcasm_clexmonte.so"
  )

list(APPEND _cmake_import_check_targets CASM::casm_clexmonte )
list(APPEND _cmake_import_check_files_for_CASM::casm_clexmonte "${_IMPORT_PREFIX}/lib/libcasm_clexmonte.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
