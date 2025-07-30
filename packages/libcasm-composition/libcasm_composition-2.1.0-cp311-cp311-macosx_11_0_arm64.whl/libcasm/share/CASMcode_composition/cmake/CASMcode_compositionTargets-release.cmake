#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "CASM::casm_composition" for configuration "Release"
set_property(TARGET CASM::casm_composition APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(CASM::casm_composition PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcasm_composition.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libcasm_composition.dylib"
  )

list(APPEND _cmake_import_check_targets CASM::casm_composition )
list(APPEND _cmake_import_check_files_for_CASM::casm_composition "${_IMPORT_PREFIX}/lib/libcasm_composition.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
