project(smokec)
cmake_minimum_required(VERSION 2.8)
aux_source_directory(. SRC_LIST)

find_package(Smoke REQUIRED)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${SMOKE_CMAKE_MODULE_DIR}")
include_directories(${SMOKE_INCLUDE_DIR} include)

add_subdirectory(smokec)
add_subdirectory(examples)
add_subdirectory(bindings)
add_subdirectory(include)
add_subdirectory(pysmoke)

add_subdirectory(marshal)