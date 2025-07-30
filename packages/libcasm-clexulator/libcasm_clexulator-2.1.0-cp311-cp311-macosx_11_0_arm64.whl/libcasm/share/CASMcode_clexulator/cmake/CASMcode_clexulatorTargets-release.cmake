#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "CASM::casm_clexulator" for configuration "Release"
set_property(TARGET CASM::casm_clexulator APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(CASM::casm_clexulator PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcasm_clexulator.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libcasm_clexulator.dylib"
  )

list(APPEND _cmake_import_check_targets CASM::casm_clexulator )
list(APPEND _cmake_import_check_files_for_CASM::casm_clexulator "${_IMPORT_PREFIX}/lib/libcasm_clexulator.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
