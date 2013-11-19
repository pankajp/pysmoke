/*
 * bindings.h
 *
 *  Created on: Nov 18, 2013
 *      Author: pankaj
 */

#ifndef BINDINGS_H_
#define BINDINGS_H_

#ifdef __cplusplus
extern "C" {
#endif

void init_qtcore_CSmoke();
void init_qtgui_CSmoke();

CSmoke qtcore_CSmoke();
CSmoke qtgui_CSmoke();

void CSmoke_delete(CSmoke);


#ifdef __cplusplus
}
#endif

#endif /* BINDINGS_H_ */
