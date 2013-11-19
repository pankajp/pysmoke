#set(LIB_TYPE SHARED)
add_library(smokec SHARED smokec.cpp)

#find_package(Qt4 REQUIRED)

find_library(SMOKE_BASE_LIB_NAMES
    NAMES smokebase
    PATHS "${SMOKE_INSTALL_PREFIX}/lib"
)


target_link_libraries(smokec
    ${SMOKE_BASE_LIB_NAMES}
)
