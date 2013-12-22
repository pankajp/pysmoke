/*
 * marshal.h
 *
 *  Created on: Dec 22, 2013
 *      Author: pankaj
 */

#ifndef MARSHAL_H
#define MARSHAL_H

#ifdef __cplusplus
extern "C" {
#endif

// BEGIN API

char* QString_to_utf8(void * qstr);
void * QString_from_utf8(char * charp);


// END API

#ifdef __cplusplus
}
#endif

#endif // MARSHAL_H
