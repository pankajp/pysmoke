project(pysmoke)
cmake_minimum_required(VERSION 2.8)
aux_source_directory(. SRC_LIST)

find_package(Smoke REQUIRED)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${SMOKE_CMAKE_MODULE_DIR}")
include_directories(${SMOKE_INCLUDE_DIR} include)

# set(CMAKE_CXX_FLAGS "-fsanitize=address")
# set(CMAKE_C_FLAGS "-fsanitize=address")
# set(CMAKE_EXE_LINKER_FLAGS "-fsanitize=address")
# set(CMAKE_MODULE_LINKER_FLAGS "-fsanitize=address")
# set(CMAKE_SHARED_LINKER_FLAGS "-fsanitize=address")

add_subdirectory(smokec)
add_subdirectory(examples)
add_subdirectory(bindings)
add_subdirectory(include)
add_subdirectory(pysmoke)

add_subdirectory(marshal)
