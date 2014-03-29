/*
 * marshal.cpp
 *
 *  Created on: Dec 22, 2013
 *      Author: pankaj
 */

#include "marshal.h"

#include <QtCore/QString>
#include <cstdlib>


char * QString_to_utf8(void * qstr) {
    QString * qs = static_cast<QString*>(qstr);
    QByteArray text = qs->toUtf8();
    char *data = static_cast<char*>(malloc(text.size() + 1));
    strcpy(data, text.data());
    return data;
}

void * QString_from_utf8(char * charp) {
    return new QString(QString::fromUtf8(charp));
}


