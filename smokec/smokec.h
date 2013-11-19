#ifndef libSmokeC_H
#define libSmokeC_H

#ifdef __cplusplus
extern "C" {
#endif


/*
 * C/C++ interop data structures.
 */

// We could just pass everything around using void* (pass-by-reference)
// I don't want to, though. -aw
typedef union StackItem {
    void* s_voidp;
    int s_bool;
    signed char s_char;
    unsigned char s_uchar;
    short s_short;
    unsigned short s_ushort;
    int s_int;
    unsigned int s_uint;
    long s_long;
    unsigned long s_ulong;
    float s_float;
    double s_double;
    long s_enum;
    void* s_class;
} StackItem;

typedef enum EnumOperation {
    EnumNew, EnumDelete, EnumFromLong, EnumToLong
} EnumOperation;

typedef StackItem* Stack;
typedef short Index;
typedef void (*ClassFn)(Index method, void* obj, Stack args);
typedef void* (*CastFn)(void* obj, Index from, Index to);
typedef void (*EnumFn)(EnumOperation, Index, void*, long);


typedef enum ClassFlags {
    cf_constructor = 0x01,  // has a constructor
    cf_deepcopy = 0x02,     // has copy constructor
    cf_virtual = 0x04,      // has virtual destructor
    cf_namespace = 0x08,    // is a namespace
    cf_undefined = 0x10     // defined elsewhere
} ClassFlags;
/**
 * Describe one class.
 */
typedef struct Class {
    const char *className;    // Name of the class
    int external;        // Whether the class is in another module
    Index parents;        // Index into inheritanceList
    ClassFn classFn;    // Calls any method in the class
    EnumFn enumFn;        // Handles enum pointers
    unsigned short flags;   // ClassFlags
    unsigned int size;
} Class;

typedef enum MethodFlags {
    mf_static = 0x01, mf_const = 0x02, mf_copyctor = 0x04,  // Copy constructor
    mf_internal = 0x08,   // For internal use only
    mf_enum = 0x10,   // An enum value
    mf_ctor = 0x20,
    mf_dtor = 0x40,
    mf_protected = 0x80,
    mf_attribute = 0x100,   // accessor method for a field
    mf_property = 0x200,    // accessor method of a property
    mf_virtual = 0x400,
    mf_purevirtual = 0x800,
    mf_signal = 0x1000, // method is a signal
    mf_slot = 0x2000,   // method is a slot
    mf_explicit = 0x4000    // method is an 'explicit' constructor
} MethodFlags;
/**
 * Describe one method of one class.
 */
typedef struct Method {
    Index classId;        // Index into classes
    Index name;        // Index into methodNames; real name
    Index args;        // Index into argumentList
    unsigned char numArgs;    // Number of arguments
    unsigned short flags;    // MethodFlags (const/static/etc...)
    Index ret;        // Index into types for the return type
    Index method;        // Passed to Class.classFn, to call method
} Method;

/**
 * One MethodMap entry maps the munged method prototype
 * to the Method entry.
 *
 * The munging works this way:
 * $ is a plain scalar
 * # is an object
 * ? is a non-scalar (reference to array or hash, undef)
 *
 * e.g. QApplication(int &, char **) becomes QApplication$?
 */
typedef struct MethodMap {
    Index classId;        // Index into classes
    Index name;        // Index into methodNames; munged name
    Index method;        // Index into methods
} MethodMap;

typedef enum TypeFlags {
    // The first 4 bits indicate the TypeId value, i.e. which field
    // of the StackItem union is used.
    tf_elem = 0x0F,

// Always only one of the next three flags should be set
    tf_stack = 0x10,     // Stored on the stack, 'type'
    tf_ptr = 0x20,       // Pointer, 'type*'
    tf_ref = 0x30,       // Reference, 'type&'
// Can | whatever ones of these apply
    tf_const = 0x40        // const argument
} TypeFlags;

/**
 * One Type entry is one argument type needed by a method.
 * Type entries are shared, there is only one entry for "int" etc.
 */
typedef struct Type {
    const char *name;    // Stringified type name
    Index classId;        // Index into classes. -1 for none
    unsigned short flags;   // TypeFlags
} Type;

typedef enum TypeId {
    t_voidp,
    t_bool,
    t_char,
    t_uchar,
    t_short,
    t_ushort,
    t_int,
    t_uint,
    t_long,
    t_ulong,
    t_float,
    t_double,
    t_enum,
    t_class,
    t_last        // number of pre-defined types
} TypeId;



/*
 * Opaque Smoke and SmokeBinding structs
 */

typedef struct CSmoke {
    void * smoke;
} CSmoke;

/**
 * Describe one index in a given module.
 */
typedef struct CModuleIndex {
    CSmoke smoke;
    Index index;
} CModuleIndex;


/*
 * CSmoke accessors
 */

Method * Smoke_methods(CSmoke smoke);
const char ** Smoke_methodNames(CSmoke smoke);
MethodMap * Smoke_methodMaps(CSmoke smoke);
Index Smoke_numMethodMaps(CSmoke smoke);
Index * Smoke_argumentList(CSmoke smoke);
Type * Smoke_types(CSmoke smoke);
Class *Smoke_classes(CSmoke smoke);
Index Smoke_numClasses(CSmoke smoke);

/*
 * Smoke Methods
 */

const char * Smoke_moduleName(CSmoke smoke);
void * Smoke_castM(CSmoke smoke, void *ptr, const CModuleIndex from, const CModuleIndex to);
void * Smoke_cast(CSmoke smoke, void *ptr, Index from, Index to);
const char * Smoke_className(CSmoke smoke, Index classId);
int Smoke_leg(CSmoke smoke, Index a, Index b);
Index Smoke_idType(CSmoke smoke, const char *t);
CModuleIndex Smoke_idClass(CSmoke smoke, const char *c, int external);
CModuleIndex Smoke_idMethodName(CSmoke smoke, const char *m);
CModuleIndex Smoke_findMethodName(CSmoke smoke, const char *c, const char *m);
CModuleIndex Smoke_idMethod(CSmoke smoke, Index c, Index name);
CModuleIndex Smoke_findMethodM(CSmoke smoke, CModuleIndex c, CModuleIndex name);
CModuleIndex Smoke_findMethod(CSmoke smoke, const char *c, const char *name);

/*
 * Static functions
 */
CModuleIndex findClass(const char *c);
int isDerivedFromM(const CModuleIndex classId, const CModuleIndex baseClassId);
int isDerivedFromI(CSmoke smoke, Index classId, CSmoke baseSmoke, Index baseId);
int isDerivedFrom(const char *className, const char *baseClassName);



/*
 * SmokeBinding
 */

typedef struct CSmokeBinding {
    void * binding;
} CSmokeBinding;

typedef void (*SmokeBinding_DeletedFn)(CSmokeBinding, Index, void *);
typedef int (*SmokeBinding_CallMethodFn)(CSmokeBinding, Index, void*, Stack, int);
typedef char* (*SmokeBinding_ClassNameFn)(CSmokeBinding, Index);

CSmokeBinding SmokeBinding_new(CSmoke smoke,
            SmokeBinding_DeletedFn deleteFn,
            SmokeBinding_CallMethodFn callMethodFn,
            SmokeBinding_ClassNameFn classNameFn);
void SmokeBinding_delete(CSmokeBinding binding);

char * SmokeBinding_className(CSmokeBinding, Index);

CSmoke CSmoke_FromBinding(CSmokeBinding binding);



#ifdef __cplusplus
}
#endif

#endif
