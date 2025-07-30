#=============================================================================
# Copyright (c) 2025, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#=============================================================================

#[=======================================================================[.rst:
Findtblis
--------

Find tblis

Imported targets
^^^^^^^^^^^^^^^^

This module defines the following :prop_tgt:`IMPORTED` target(s):

``tblis::tblis``
  The tblis library, if found.

Result variables
^^^^^^^^^^^^^^^^

This module will set the following variables in your project:

``tblis_FOUND``
  True if tblis is found.
``tblis_INCLUDE_DIRS``
  The include directories needed to use tblis.
``tblis_LIBRARIES``
  The libraries needed to usetblis.
``tblis_VERSION_STRING``
  The version of the tblis library found. [OPTIONAL]

#]=======================================================================]

# Prefer using a Config module if it exists for this project



set(tblis_NO_CONFIG TRUE)
if(NOT tblis_NO_CONFIG)
  find_package(tblis CONFIG QUIET)
  if(tblis_FOUND)
    find_package_handle_standard_args(tblis DEFAULT_MSG tblis_CONFIG)
    return()
  endif()
endif()

find_path(tblis_INCLUDE_DIR NAMES tblis/tblis.h )

set(tblis_IS_HEADER_ONLY FALSE)
if(NOT tblis_LIBRARY AND NOT tblis_IS_HEADER_ONLY)
  find_library(tblis_LIBRARY_RELEASE NAMES libtblis.so NAMES_PER_DIR )
  find_library(tblis_LIBRARY_DEBUG   NAMES libtblis.sod   NAMES_PER_DIR )

  include(${CMAKE_ROOT}/Modules/SelectLibraryConfigurations.cmake)
  select_library_configurations(tblis)
  unset(tblis_FOUND) #incorrectly set by select_library_configurations
endif()

include(${CMAKE_ROOT}/Modules/FindPackageHandleStandardArgs.cmake)

if(tblis_IS_HEADER_ONLY)
  find_package_handle_standard_args(tblis
                                    FOUND_VAR tblis_FOUND
                                    REQUIRED_VARS tblis_INCLUDE_DIR
                                    VERSION_VAR )
else()
  find_package_handle_standard_args(tblis
                                    FOUND_VAR tblis_FOUND
                                    REQUIRED_VARS tblis_LIBRARY tblis_INCLUDE_DIR
                                    VERSION_VAR )
endif()

if(tblis_FOUND)
  set(tblis_INCLUDE_DIRS ${tblis_INCLUDE_DIR})

  if(NOT tblis_LIBRARIES)
    set(tblis_LIBRARIES ${tblis_LIBRARY})
  endif()

  if(NOT TARGET tblis::tblis)
    add_library(tblis::tblis UNKNOWN IMPORTED GLOBAL)
    set_target_properties(tblis::tblis PROPERTIES
      INTERFACE_INCLUDE_DIRECTORIES "${tblis_INCLUDE_DIRS}")

    if(tblis_LIBRARY_RELEASE)
      set_property(TARGET tblis::tblis APPEND PROPERTY
        IMPORTED_CONFIGURATIONS RELEASE)
      set_target_properties(tblis::tblis PROPERTIES
        IMPORTED_LOCATION_RELEASE "${tblis_LIBRARY_RELEASE}")
    endif()

    if(tblis_LIBRARY_DEBUG)
      set_property(TARGET tblis::tblis APPEND PROPERTY
        IMPORTED_CONFIGURATIONS DEBUG)
      set_target_properties(tblis::tblis PROPERTIES
        IMPORTED_LOCATION_DEBUG "${tblis_LIBRARY_DEBUG}")
    endif()

    if(NOT tblis_LIBRARY_RELEASE AND NOT tblis_LIBRARY_DEBUG)
      set_property(TARGET tblis::tblis APPEND PROPERTY
        IMPORTED_LOCATION "${tblis_LIBRARY}")
    endif()
  endif()
endif()



unset(tblis_NO_CONFIG)
unset(tblis_IS_HEADER_ONLY)
