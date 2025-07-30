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

include(CMakeFindDependencyMacro)

set(CCCL_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../rapids/cmake/cccl")
set(span_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../legate/deps/cmake")
set(mdspan_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../legate/deps/cmake")
find_package(CCCL 2.5.0 QUIET)
find_dependency(CCCL)

if(CCCL_FOUND)
    target_compile_definitions(CCCL::CCCL INTERFACE THRUST_DISABLE_ABI_NAMESPACE)
    target_compile_definitions(CCCL::CCCL INTERFACE THRUST_IGNORE_ABI_NAMESPACE_ERROR)
    

endif()
find_package(Legion 25.7.0 QUIET)
find_dependency(Legion)

find_package(span 1.0 QUIET)
find_dependency(span)

find_package(mdspan 0.6 QUIET)
find_dependency(mdspan)


set(rapids_global_targets CCCL;CCCL::CCCL;CCCL::CUB;CCCL::libcudacxx;Legion::Realm;Legion::Regent;Legion::Legion;Legion::RealmRuntime;Legion::LegionRuntime)


foreach(target IN LISTS rapids_global_targets)
  if(TARGET ${target})
    get_target_property(_is_imported ${target} IMPORTED)
    get_target_property(_already_global ${target} IMPORTED_GLOBAL)
    if(_is_imported AND NOT _already_global)
        set_target_properties(${target} PROPERTIES IMPORTED_GLOBAL TRUE)
    endif()
  endif()
endforeach()

unset(rapids_global_targets)
unset(rapids_clear_cpm_cache)
