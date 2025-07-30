#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "CASM::casm_configuration" for configuration "Release"
set_property(TARGET CASM::casm_configuration APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(CASM::casm_configuration PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcasm_configuration.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libcasm_configuration.dylib"
  )

list(APPEND _cmake_import_check_targets CASM::casm_configuration )
list(APPEND _cmake_import_check_files_for_CASM::casm_configuration "${_IMPORT_PREFIX}/lib/libcasm_configuration.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
