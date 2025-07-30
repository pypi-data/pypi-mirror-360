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

#[=======================================================================[

Provide targets for Legate, the Foundation for All Legate Libraries.

Imported Targets:
  - legate::legate



Result Variables
^^^^^^^^^^^^^^^^

This module will set the following variables::

  LEGATE_FOUND
  LEGATE_VERSION
  LEGATE_VERSION_MAJOR
  LEGATE_VERSION_MINOR

#]=======================================================================]


####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was config.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

cmake_minimum_required(VERSION 3.26.4)

set(rapids_global_languages )
foreach(lang IN LISTS rapids_global_languages)
  include("${CMAKE_CURRENT_LIST_DIR}/legate-${lang}-language.cmake")
endforeach()
unset(rapids_global_languages)

include("${CMAKE_CURRENT_LIST_DIR}/legate-dependencies.cmake" OPTIONAL)
include("${CMAKE_CURRENT_LIST_DIR}/legate-targets.cmake" OPTIONAL)

if()
  set(legate_comp_names )
  # find dependencies before creating targets that use them
  # this way if a dependency can't be found we fail
  foreach(comp IN LISTS legate_FIND_COMPONENTS)
    if(${comp} IN_LIST legate_comp_names)
      file(GLOB legate_component_dep_files LIST_DIRECTORIES FALSE
           "${CMAKE_CURRENT_LIST_DIR}/legate-${comp}*-dependencies.cmake")
      foreach(f IN LISTS  legate_component_dep_files)
        include("${f}")
      endforeach()
    endif()
  endforeach()

  foreach(comp IN LISTS legate_FIND_COMPONENTS)
    if(${comp} IN_LIST legate_comp_names)
      file(GLOB legate_component_target_files LIST_DIRECTORIES FALSE
           "${CMAKE_CURRENT_LIST_DIR}/legate-${comp}*-targets.cmake")
      foreach(f IN LISTS  legate_component_target_files)
        include("${f}")
      endforeach()
      set(legate_${comp}_FOUND TRUE)
    endif()
  endforeach()
endif()

include("${CMAKE_CURRENT_LIST_DIR}/legate-config-version.cmake" OPTIONAL)

# Set our version variables
set(LEGATE_VERSION_MAJOR 25)
set(LEGATE_VERSION_MINOR 07)
set(LEGATE_VERSION_PATCH 00)
set(LEGATE_VERSION 25.07.00)


set(rapids_global_targets legate)
set(rapids_namespaced_global_targets legate)
if((NOT "legate::" STREQUAL "") AND rapids_namespaced_global_targets)
  list(TRANSFORM rapids_namespaced_global_targets PREPEND "legate::")
endif()

foreach(target IN LISTS rapids_namespaced_global_targets)
  if(TARGET ${target})
    get_target_property(_is_imported ${target} IMPORTED)
    get_target_property(_already_global ${target} IMPORTED_GLOBAL)
    if(_is_imported AND NOT _already_global)
      set_target_properties(${target} PROPERTIES IMPORTED_GLOBAL TRUE)
    endif()
  endif()
endforeach()

# For backwards compat
if("rapids_config_install" STREQUAL "rapids_config_build")
  foreach(target IN LISTS rapids_global_targets)
    if(TARGET ${target})
      get_target_property(_is_imported ${target} IMPORTED)
      get_target_property(_already_global ${target} IMPORTED_GLOBAL)
      if(_is_imported AND NOT _already_global)
        set_target_properties(${target} PROPERTIES IMPORTED_GLOBAL TRUE)
      endif()
      if(NOT TARGET legate::${target})
        add_library(legate::${target} ALIAS ${target})
      endif()
    endif()
  endforeach()
endif()

unset(rapids_comp_names)
unset(rapids_comp_unique_ids)
unset(rapids_global_targets)
unset(rapids_namespaced_global_targets)

check_required_components(legate)

set(${CMAKE_FIND_PACKAGE_NAME}_CONFIG "${CMAKE_CURRENT_LIST_FILE}")

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(${CMAKE_FIND_PACKAGE_NAME} CONFIG_MODE)

if(NOT TARGET CCCL::Thrust)
  thrust_create_target(CCCL::Thrust FROM_OPTIONS)
endif()

set(Legion_USE_CUDA OFF)
set(Legion_USE_OpenMP OFF)
set(Legion_USE_Python ON)
set(Legion_CUDA_ARCH )
set(Legion_NETWORKS )
set(Legion_BOUNDS_CHECKS OFF)
set(Legion_MAX_DIM 6)
set(Legion_MAX_FIELDS 256)
include("${CMAKE_CURRENT_LIST_DIR}/Modules/legate_configure_target.cmake")

