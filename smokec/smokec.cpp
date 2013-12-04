/*
 * smokec.cpp
 *
 *  Created on: Nov 18, 2013
 *      Author: pankaj
 */

#include <smoke.h>

#include "smokec.h"


Smoke * SMOKE(CSmoke csmoke) {
    return (Smoke*)(csmoke.smoke);
}
Smoke::ModuleIndex MODULEINDEX(CModuleIndex mindex) {
    return Smoke::ModuleIndex(SMOKE(mindex.smoke), mindex.index);
}

CModuleIndex CMODULEINDEX(Smoke::ModuleIndex mindex) {
    CModuleIndex ret;
    ret.smoke.smoke = mindex.smoke;
    ret.index = mindex.index;
    return ret;
}

CSmokeBinding CSMOKEBINDING(SmokeBinding * binding) {
    CSmokeBinding ret;
    ret.binding = binding;
    return ret;
}

extern "C" {

const char* Smoke_moduleName(CSmoke smoke) {
    return SMOKE(smoke)->moduleName();
}

void* Smoke_castM(CSmoke smoke, void* ptr, const CModuleIndex from,
        const CModuleIndex to) {
    return SMOKE(smoke)->cast(ptr, MODULEINDEX(from), MODULEINDEX(to));
}

void* Smoke_cast(CSmoke smoke, void* ptr, Index from, Index to) {
    return SMOKE(smoke)->cast(ptr, from, to);
}

const char* Smoke_className(CSmoke smoke, Index classId) {
    return SMOKE(smoke)->className(classId);
}

int Smoke_leg(CSmoke smoke, Index a, Index b) {
    return SMOKE(smoke)->leg(a, b);
}

Index Smoke_idType(CSmoke smoke, const char* t) {
    return SMOKE(smoke)->idType(t);
}

CModuleIndex Smoke_idClass(CSmoke smoke, const char* c, cbool external) {
    return CMODULEINDEX(SMOKE(smoke)->idClass(c, (bool)external));
}

CModuleIndex Smoke_idMethodName(CSmoke smoke, const char* m) {
    return CMODULEINDEX(SMOKE(smoke)->idMethodName(m));
}

CModuleIndex Smoke_findMethodName(CSmoke smoke, const char* c, const char* m) {
    return CMODULEINDEX(SMOKE(smoke)->findMethodName(c, m));
}

CModuleIndex Smoke_idMethod(CSmoke smoke, Index c, Index name) {
    return CMODULEINDEX(SMOKE(smoke)->idMethod(c, name));
}

CModuleIndex Smoke_findMethodM(CSmoke smoke, CModuleIndex c, CModuleIndex name) {
    return CMODULEINDEX(SMOKE(smoke)->findMethod(MODULEINDEX(c), MODULEINDEX(name)));
}

CModuleIndex Smoke_findMethod(CSmoke smoke, const char* c, const char* name) {
    return CMODULEINDEX(SMOKE(smoke)->findMethod(c, name));
}


CModuleIndex findClass(const char* c) {
    return CMODULEINDEX(Smoke::findClass(c));
}

cbool isDerivedFromM(const CModuleIndex classId, const CModuleIndex baseClassId) {
    return Smoke::isDerivedFrom(MODULEINDEX(classId), MODULEINDEX(baseClassId));
}

cbool isDerivedFromI(CSmoke smoke, Index classId, CSmoke baseSmoke, Index baseId) {
    return Smoke::isDerivedFrom(SMOKE(smoke), classId, SMOKE(baseSmoke), baseId);
}

cbool isDerivedFrom(const char* className, const char* baseClassName) {
    return Smoke::isDerivedFrom(className, baseClassName);
}



class CSmokeBindingImpl: public SmokeBinding {
protected:
    SmokeBinding_DeletedFn deleteFn;
    SmokeBinding_CallMethodFn callMethodFn;
    SmokeBinding_ClassNameFn classNameFn;
    CSmokeBinding csmokebinding;

public:
    CSmoke csmoke;
    CSmokeBindingImpl(CSmoke csmoke,
                      SmokeBinding_DeletedFn deletef,
                      SmokeBinding_CallMethodFn callMethodf,
                      SmokeBinding_ClassNameFn classNamef):
        SmokeBinding(SMOKE(csmoke)),
        csmoke(csmoke),
        deleteFn(deletef),
        callMethodFn(callMethodf),
        classNameFn(classNamef),
        csmokebinding(CSMOKEBINDING(this))
    {
    }

    virtual void deleted(Smoke::Index classId, void *obj) {
        this->deleteFn(this->csmokebinding, classId, obj);
    }

    virtual bool callMethod(Smoke::Index method, void *obj, Smoke::Stack args, bool isAbstract=false) {
        return (bool)this->callMethodFn(this->csmokebinding, method, obj, (Stack)args, isAbstract);
    }

    virtual char * className(Smoke::Index classId) {
        return this->classNameFn(this->csmokebinding, classId);
    }
};


CSmokeBinding SmokeBinding_new(CSmoke smoke,
        SmokeBinding_DeletedFn deleteFn,
        SmokeBinding_CallMethodFn callMethodFn,
        SmokeBinding_ClassNameFn classNameFn) {
    return CSMOKEBINDING(new CSmokeBindingImpl(smoke, deleteFn, callMethodFn, classNameFn));
}

void SmokeBinding_delete(CSmokeBinding binding) {
    delete (CSmokeBindingImpl*)binding.binding;
}

char * SmokeBinding_className(CSmokeBinding binding, Index index) {
    return ((CSmokeBindingImpl*)binding.binding)->className(index);
}

}

CSmoke CSmoke_FromBinding(CSmokeBinding binding) {
    return ((CSmokeBindingImpl*)binding.binding)->csmoke;
}


Method * Smoke_methods(CSmoke smoke) {
    return (Method*)SMOKE(smoke)->methods;
}

Index Smoke_numMethods(CSmoke smoke) {
    return (Index)SMOKE(smoke)->numMethods;
}

const char ** Smoke_methodNames(CSmoke smoke) {
    return SMOKE(smoke)->methodNames;
}

Index Smoke_numMethodNames(CSmoke smoke) {
    return (Index)SMOKE(smoke)->numMethodNames;
}

MethodMap * Smoke_methodMaps(CSmoke smoke) {
    return (MethodMap*)SMOKE(smoke)->methodMaps;
}

Index Smoke_numMethodMaps(CSmoke smoke) {
    return (Index)SMOKE(smoke)->numMethodMaps;
}

Index * Smoke_argumentList(CSmoke smoke) {
    return SMOKE(smoke)->argumentList;
}

Type * Smoke_types(CSmoke smoke) {
    return (Type *)SMOKE(smoke)->types;
}

Index Smoke_numTypes(CSmoke smoke) {
    return (Index)SMOKE(smoke)->numTypes;
}

Class * Smoke_classes(CSmoke smoke) {
    return (Class *)SMOKE(smoke)->classes;
}
Index Smoke_numClasses(CSmoke smoke) {
    return SMOKE(smoke)->numClasses;
}
Index * Smoke_inheritanceList(CSmoke smoke) {
    return SMOKE(smoke)->inheritanceList;
}
Index * Smoke_ambiguousMethodList(CSmoke smoke) {
    return SMOKE(smoke)->ambiguousMethodList;
}
CastFn Smoke_castFn(CSmoke smoke) {
    return SMOKE(smoke)->castFn;
}

