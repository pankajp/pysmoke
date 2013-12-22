add_library(marshalqtpy SHARED marshal.cpp)

find_package(Qt4 REQUIRED)

include(${QT_USE_FILE})
add_definitions(${QT_DEFINITIONS})

target_link_libraries(marshalqtpy
    ${QT_LIBRARIES}
)
