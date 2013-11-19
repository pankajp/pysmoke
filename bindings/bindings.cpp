/*
 * bindings.cpp
 *
 *  Created on: Nov 18, 2013
 *      Author: pankaj
 */


#include <smoke.h>
#include <smoke/qtcore_smoke.h>
#include <smoke/qtgui_smoke.h>

#include "smokec.h"

extern "C" {

void init_qtcore_CSmoke() {
    init_qtcore_Smoke();
}

void init_qtgui_CSmoke() {
    init_qtgui_Smoke();
}


CSmoke qtcore_CSmoke() {
    CSmoke ret;
    ret.smoke = qtcore_Smoke;
    return ret;
}

CSmoke qtgui_CSmoke() {
    CSmoke ret;
    ret.smoke = qtgui_Smoke;
    return ret;
}

void CSmoke_delete(CSmoke csmoke) {
    delete (Smoke*)csmoke.smoke;
}

}

