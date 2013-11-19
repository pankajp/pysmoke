#set(LIB_TYPE SHARED)
add_library(smokec SHARED smokec.cpp bindings.cpp)

#find_package(Qt4 REQUIRED)
find_package(Smoke REQUIRED)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${SMOKE_CMAKE_MODULE_DIR}")
include_directories(${SMOKE_INCLUDE_DIR})


find_library(SMOKE_BASE_LIB_NAMES
    NAMES smokebase
    PATHS "${SMOKE_INSTALL_PREFIX}/lib"
)

find_library(SMOKE_QTCORE_LIB_NAMES
    NAMES smokeqtcore
    PATHS "${SMOKE_INSTALL_PREFIX}/lib"
)

find_library(SMOKE_QTGUI_LIB_NAMES
    NAMES smokeqtgui
    PATHS "${SMOKE_INSTALL_PREFIX}/lib"
)

target_link_libraries(smokec
    ${SMOKE_BASE_LIB_NAMES}
    ${SMOKE_QTCORE_LIB_NAMES}
    ${SMOKE_QTGUI_LIB_NAMES}
)
