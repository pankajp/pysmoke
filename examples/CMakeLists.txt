add_executable(hellowidget hellowidget.c)
include_directories(${CMAKE_SOURCE_DIR}/smokec)
target_link_libraries(hellowidget smokec)
