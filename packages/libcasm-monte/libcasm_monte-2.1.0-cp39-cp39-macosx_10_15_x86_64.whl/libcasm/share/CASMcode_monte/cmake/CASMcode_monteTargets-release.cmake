#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "CASM::casm_monte" for configuration "Release"
set_property(TARGET CASM::casm_monte APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(CASM::casm_monte PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcasm_monte.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libcasm_monte.dylib"
  )

list(APPEND _cmake_import_check_targets CASM::casm_monte )
list(APPEND _cmake_import_check_files_for_CASM::casm_monte "${_IMPORT_PREFIX}/lib/libcasm_monte.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
