# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT license.

# Exports target APSI::apsi
#
# Creates variables:
#   APSI_FOUND : If APSI was found
#   APSI_VERSION : the full version number
#   APSI_VERSION_MAJOR : the major version number
#   APSI_VERSION_MINOR : the minor version number
#   APSI_VERSION_PATCH : the patch version number
#   APSI_BUILD_TYPE : The build type (e.g., "Release" or "Debug")
#   APSI_DEBUG : Set to non-zero value if library is compiled with extra debugging code (very slow!)
#   APSI_USE_CXX17 : Set to non-zero value if library is compiled as C++17 instead of C++14
#   APSI_USE_LOG4CPLUS : Set to non-zero value if library is compiled with log4cplus for logging
#   APSI_USE_ZMQ : Set to non-zero value if library is compiled with ZeroMQ and cppzmq for networking


####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was APSIConfig.cmake.in                            ########

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

include(CMakeFindDependencyMacro)

macro(apsi_find_dependency dep)
    find_dependency(${dep})
    if(NOT ${dep}_FOUND)
        if(NOT APSI_FIND_QUIETLY)
            message(WARNING "Could not find dependency `${dep}` required by this configuration")
        endif()
        set(APSI_FOUND FALSE)
        return()
    endif()
endmacro()

set(APSI_FOUND FALSE)

set(APSI_VERSION 0.8.2)
set(APSI_VERSION_MAJOR 0)
set(APSI_VERSION_MINOR 8)
set(APSI_VERSION_PATCH 2)

set(APSI_BUILD_TYPE Release)
set(APSI_DEBUG OFF)
set(APSI_USE_CXX17 ON)

apsi_find_dependency(SEAL 3.7 REQUIRED)
apsi_find_dependency(Kuku 2.1 REQUIRED)
apsi_find_dependency(Flatbuffers REQUIRED)
apsi_find_dependency(jsoncpp REQUIRED)

set(CMAKE_THREAD_PREFER_PTHREAD TRUE)
set(THREADS_PREFER_PTHREAD_FLAG TRUE)
apsi_find_dependency(Threads REQUIRED)

set(APSI_USE_LOG4CPLUS ON)
if(APSI_USE_LOG4CPLUS)
    apsi_find_dependency(log4cplus REQUIRED)
endif()

set(APSI_USE_ZMQ ON)
if(APSI_USE_ZMQ)
    apsi_find_dependency(ZeroMQ REQUIRED)
    apsi_find_dependency(cppzmq REQUIRED)
endif()

# Add the current directory to the module search path
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})

include(${CMAKE_CURRENT_LIST_DIR}/APSITargets.cmake)

if(TARGET APSI::apsi)
    set(APSI_FOUND TRUE)
endif()

if(APSI_FOUND)
    if(NOT APSI_FIND_QUIETLY)
        message(STATUS "APSI -> Version ${APSI_VERSION} detected")
    endif()
    if(APSI_DEBUG AND NOT APSI_FIND_QUIETLY)
        message(STATUS "Performance warning: APSI compiled in debug mode")
    endif()
    if(NOT APSI_FIND_QUIETLY)
        message(STATUS "APSI -> Targets available: APSI::apsi")
    endif()
else()
    if(NOT APSI_FIND_QUIETLY)
        message(STATUS "APSI -> NOT FOUND")
    endif()
endif()
