/* 
 * File:   hellowidget.c
 * Author: pankaj
 *
 * Created on November 19, 2013, 2:41 PM
 */


#include <stdio.h>
#include <string.h>

#include "smokec.h"
#include "bindings.h"



unsigned int BUFLEN=1024;

int adds(char * buf, const char * to_add) {
    unsigned int s = strlen(buf);
    unsigned int ret = snprintf(&buf[s], BUFLEN-s, "%s", to_add);
    return ret;
}

int addsp(char * buf, const void * to_add) {
    unsigned int s = strlen(buf);
    unsigned int ret = snprintf(&buf[s], BUFLEN-s, "%p", to_add);
    return ret;
}

int addsm(char * buf, const CModuleIndex to_add) {
    unsigned int s = strlen(buf);
    unsigned int ret = snprintf(&buf[s], BUFLEN-s, "[%s, %i]", Smoke_moduleName(to_add.smoke), to_add.index);
    return ret;
}


void deleted(CSmokeBinding binding, Index classId, void *obj) {
    printf("~%s (%p)\n", SmokeBinding_className(binding, classId), obj);
}


cbool callMethod(CSmokeBinding binding, Index method, void *obj,
    Stack args, cbool isAbstract)
{
    CSmoke smoke = CSmoke_FromBinding(binding);
    Method meth = Smoke_methods(smoke)[method];
    char name[BUFLEN];
    memset(name, '\0', BUFLEN);

    // check for method flags
    if (meth.flags & mf_protected) adds(name, "protected ");
    if (meth.flags & mf_const) adds(name, "const ");

    // add the name
    adds(name, Smoke_methodNames(smoke)[meth.name]);
    adds(name, "(");

    // iterate over the argument list and build up the
    // parameter names
    Index * idx = Smoke_argumentList(smoke) + meth.args;
    while (*idx) {
        adds(name, Smoke_types(smoke)[*idx].name);
        idx++;
        if (*idx) adds(name, ", ");
    }
    adds(name, ")");

    printf("%s(%p)::%s\n", SmokeBinding_className(binding, meth.classId), obj, name);
    return 0;
}

/*
 * In a bindings runtime, this should return the classname as used
 * in the bindings language, e.g. Qt::Widget in Ruby or
 * Qyoto.QWidget in C# or QtGui.QWidget in python
 */
char *className(CSmokeBinding binding, Index classId) {
    return (char*) Smoke_classes(CSmoke_FromBinding(binding))[classId].className;
}


int main(int argc, char **argv)
{
    char buf[BUFLEN];
    memset(buf, '\0', BUFLEN);

    // init the Qt SMOKE runtime
    init_qtcore_CSmoke();
    init_qtgui_CSmoke();

    CSmoke qtcore_smoke = qtcore_CSmoke();
    CSmoke qtgui_smoke = qtgui_CSmoke();

    // create a SmokeBinding for the Qt SMOKE runtime
    CSmokeBinding qtcoreBinding = SmokeBinding_new(qtcore_smoke,
            deleted, callMethod, className);
    CSmokeBinding qtguiBinding = SmokeBinding_new(qtgui_smoke,
            deleted, callMethod, className);

    // find the 'QApplication' class
    CModuleIndex classId = findClass("QApplication");
    /* find the methodId. we use a munged method signature, where
     * $ is a plain scalar
     * # is an object
     * ? is a non-scalar (reference to array or hash, undef) */
    CModuleIndex methId = Smoke_findMethod(classId.smoke, "QApplication", "QApplication$?");  // find the constructor
    strcpy(buf, "QApplication classId: ");
    addsm(buf, classId);
    adds(buf, ", QApplication($?) methId: ");
    addsm(buf, methId);
    printf("%s\n", buf);

    // get the Smoke::Class
    Class klass = Smoke_classes(classId.smoke)[classId.index];

    // findMethod() returns an index into methodMaps, which has
    // information about the classId, methodNameId and methodId. we
    // are interested in the methodId to get a Smoke::Method
    Method meth = Smoke_methods(methId.smoke)[Smoke_methodMaps(methId.smoke)[methId.index].method];

    StackItem stack[3];
    // QApplication expects a reference to argc, so we pass it as a pointer
    stack[1].s_voidp = &argc;
    stack[2].s_voidp = argv;
    // call the constructor, Smoke::Method::method is the methodId
    // specifically for this class.
    (*klass.classFn)(meth.method, 0, stack);

    // the zeroth element contains the return value, in this case the
    // QApplication instance
    void *qapp = stack[0].s_voidp;

    // method index 0 is always "set smoke binding" - needed for
    // virtual method callbacks etc.
    stack[1].s_voidp = qtguiBinding.binding;
    (*klass.classFn)(0, qapp, stack);

    // create a widget
    classId = findClass("QWidget");
    methId = Smoke_findMethod(classId.smoke, "QWidget", "QWidget");
    memset(buf, '\0', BUFLEN);
    strcpy(buf, "QWidget classId: ");
    addsm(buf, classId);
    adds(buf, ", QWidget() methId: ");
    addsm(buf, methId);
    printf("%s\n", buf);

    klass = Smoke_classes(classId.smoke)[classId.index];
    meth = Smoke_methods(methId.smoke)[Smoke_methodMaps(methId.smoke)[methId.index].method];

    (*klass.classFn)(meth.method, 0, stack);
    void *widget = stack[0].s_voidp;
    // set the smoke binding
    stack[1].s_voidp = qtguiBinding.binding;
    (*klass.classFn)(0, widget, stack);

    // show the widget
    methId = Smoke_findMethod(classId.smoke, "QWidget", "show");
    memset(buf, '\0', BUFLEN);
    strcpy(buf, "QWidget classId: ");
    addsm(buf, classId);
    adds(buf, ", QWidget() methId: ");
    addsm(buf, methId);
    printf("%s\n", buf);
    meth = Smoke_methods(methId.smoke)[Smoke_methodMaps(methId.smoke)[methId.index].method];
    (*klass.classFn)(meth.method, widget, 0);

    // we don't even need findClass() when we use the classId provided
    // by the MethodMap
    methId = Smoke_findMethod(qtgui_smoke, "QApplication", "exec");
    memset(buf, '\0', BUFLEN);
    snprintf(buf, BUFLEN, "QApplication classId: %i, exec() methId: ",
             Smoke_methodMaps(qtgui_smoke)[methId.index].classId);
    addsm(buf, methId);
    printf("%s\n", buf);

    klass = Smoke_classes(methId.smoke)[Smoke_methodMaps(methId.smoke)[methId.index].classId];
    meth = Smoke_methods(methId.smoke)[Smoke_methodMaps(methId.smoke)[methId.index].method];

    // call QApplication::exec()
    (*klass.classFn)(meth.method, 0, stack);

    // store the return value of QApplication::exec()
    int retval = stack[0].s_int;

    // destroy the QApplication instance
    methId = Smoke_findMethod(qtgui_smoke, "QApplication", "~QApplication");
    memset(buf, '\0', BUFLEN);
    snprintf(buf, BUFLEN, "QApplication classId: %i, ~QApplication() methId: ",
             Smoke_methodMaps(qtgui_smoke)[methId.index].classId);
    addsm(buf, methId);
    printf("%s\n", buf);
    meth = Smoke_methods(methId.smoke)[Smoke_methodMaps(methId.smoke)[methId.index].method];
    (*klass.classFn)(meth.method, qapp, 0);

    // destroy the smoke instance
    CSmoke_delete(qtgui_smoke);
    CSmoke_delete(qtcore_smoke);

    // return the previously stored value
    return retval;
}

