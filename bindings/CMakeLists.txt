add_library(smokebindings SHARED bindings.cpp)


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

target_link_libraries(smokebindings
    ${SMOKE_BASE_LIB_NAMES}
    ${SMOKE_QTCORE_LIB_NAMES}
    ${SMOKE_QTGUI_LIB_NAMES}
)
